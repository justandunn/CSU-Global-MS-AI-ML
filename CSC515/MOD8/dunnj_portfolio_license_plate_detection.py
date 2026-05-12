import os
import csv
from pathlib import Path
from datetime import datetime

import cv2
import numpy as np


print("Current Working Directory:", os.getcwd())

# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
results_csv = OUTPUT_DIR / f"license_plate_results_{timestamp}.csv"

input_images = {
    "Russian Plate 1": SCRIPT_DIR / "russian_plate_1.jpg",
    "Russian Plate 2": SCRIPT_DIR / "russian_plate_2.jpg",
    "Non-Russian Plate": SCRIPT_DIR / "non_russian_plate.jpg",
}

cascade_files = [
    SCRIPT_DIR / "haarcascade_russian_plate_number.xml",
    SCRIPT_DIR / "haarcascade_license_plate_rus_16stages.xml",
]

# Preferred normalized regions for selecting the best crop.
# Format: (x1_ratio, y1_ratio, x2_ratio, y2_ratio)
# These are NOT manual crops; they only guide which cascade detection is selected as primary.
preferred_regions = {
    "Russian Plate 1": (0.32, 0.55, 0.70, 0.88),      # lower center
    "Russian Plate 2": (0.08, 0.45, 0.55, 0.92),      # lower front/center-left
    "Non-Russian Plate": (0.35, 0.50, 0.70, 0.90),    # expected taxi plate area/control
}


# ---------------------------------------------------------
# Load cascade classifiers
# ---------------------------------------------------------
def load_cascades(cascade_paths: list[Path]) -> list[tuple[str, cv2.CascadeClassifier]]:
    loaded_cascades: list[tuple[str, cv2.CascadeClassifier]] = []

    for cascade_path in cascade_paths:
        if not cascade_path.exists():
            print(f"WARNING: Cascade file not found: {cascade_path}")
            continue

        cascade = cv2.CascadeClassifier(str(cascade_path))

        if cascade.empty():
            print(f"WARNING: Failed to load cascade: {cascade_path}")
            continue

        loaded_cascades.append((cascade_path.name, cascade))
        print(f"Loaded cascade: {cascade_path.name}")

    if not loaded_cascades:
        raise RuntimeError(
            "No cascade classifiers were loaded. Place the XML files in MOD8."
        )

    return loaded_cascades


plate_cascades = load_cascades(cascade_files)


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------
def get_box_from_detection(
    detection: dict[str, object]
) -> tuple[int, int, int, int] | None:
    box_object = detection.get("box")

    if not isinstance(box_object, tuple) or len(box_object) != 4:
        return None

    x, y, w, h = box_object

    if not all(isinstance(value, int) for value in (x, y, w, h)):
        return None

    return x, y, w, h


def get_score(detection: dict[str, object], key_name: str, default: float = 0.0) -> float:
    value = detection.get(key_name, default)

    if isinstance(value, (int, float)):
        return float(value)

    return default


def preprocess_for_detection(gray_image: np.ndarray) -> np.ndarray:
    equalized = cv2.equalizeHist(gray_image)
    blurred = cv2.GaussianBlur(equalized, (3, 3), 0)
    return blurred


def detect_plates_with_cascades(gray_image: np.ndarray) -> list[dict[str, object]]:
    detections: list[dict[str, object]] = []

    parameter_sets = [
        (1.03, 3, (25, 8)),
        (1.05, 3, (30, 10)),
        (1.08, 4, (40, 12)),
        (1.10, 5, (50, 15)),
        (1.15, 5, (60, 18)),
        (1.20, 4, (70, 20)),
    ]

    for cascade_name, cascade in plate_cascades:
        for scale_factor, min_neighbors, min_size in parameter_sets:
            plates = cascade.detectMultiScale(
                gray_image,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors,
                minSize=min_size,
            )

            for (x, y, w, h) in plates:
                detections.append({
                    "box": (int(x), int(y), int(w), int(h)),
                    "cascade_name": cascade_name,
                    "scale_factor": scale_factor,
                    "min_neighbors": min_neighbors,
                    "min_size": min_size,
                })

    return detections


def box_iou(box_a: tuple[int, int, int, int], box_b: tuple[int, int, int, int]) -> float:
    ax, ay, aw, ah = box_a
    bx, by, bw, bh = box_b

    ax2 = ax + aw
    ay2 = ay + ah
    bx2 = bx + bw
    by2 = by + bh

    inter_x1 = max(ax, bx)
    inter_y1 = max(ay, by)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0, inter_x2 - inter_x1)
    inter_h = max(0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h

    area_a = aw * ah
    area_b = bw * bh
    union_area = area_a + area_b - inter_area

    if union_area == 0:
        return 0.0

    return inter_area / union_area


def score_plate_candidate(
    box: tuple[int, int, int, int],
    image_shape: tuple[int, int, int]
) -> float:
    x, y, w, h = box
    image_h, image_w = image_shape[:2]

    aspect_ratio = w / h if h != 0 else 0.0
    area = w * h
    area_ratio = area / (image_w * image_h)

    # License plates are generally wider than tall.
    aspect_quality = 1.0 - abs(aspect_ratio - 4.3) / 4.3
    aspect_quality = max(0.0, min(1.0, aspect_quality))

    # Keep plausible sizes.
    if 0.0002 <= area_ratio <= 0.08:
        area_quality = 1.0
    else:
        area_quality = 0.15

    vertical_center = y + h / 2
    vertical_ratio = vertical_center / image_h

    # Vehicle plates tend to be lower in the vehicle image.
    if 0.45 <= vertical_ratio <= 0.92:
        position_quality = 1.0
    elif 0.35 <= vertical_ratio < 0.45:
        position_quality = 0.55
    else:
        position_quality = 0.25

    score = (
        aspect_quality * 100.0
        + area_quality * 40.0
        + position_quality * 35.0
        + area * 0.0004
    )

    return score


def filter_plate_candidates(
    detections: list[dict[str, object]],
    image_shape: tuple[int, int, int]
) -> list[dict[str, object]]:
    filtered: list[dict[str, object]] = []

    image_h, image_w = image_shape[:2]

    for detection in detections:
        box = get_box_from_detection(detection)

        if box is None:
            continue

        x, y, w, h = box

        if h == 0:
            continue

        aspect_ratio = w / h
        area_ratio = (w * h) / (image_w * image_h)

        if aspect_ratio < 1.6 or aspect_ratio > 8.5:
            continue

        if area_ratio < 0.00015 or area_ratio > 0.15:
            continue

        filtered.append(detection)

    return filtered


def non_max_suppression(
    detections: list[dict[str, object]],
    image_shape: tuple[int, int, int],
    iou_threshold: float = 0.35
) -> list[dict[str, object]]:
    if not detections:
        return []

    scored_detections: list[dict[str, object]] = []

    for detection in detections:
        box = get_box_from_detection(detection)

        if box is None:
            continue

        detection["cascade_score"] = score_plate_candidate(box, image_shape)
        scored_detections.append(detection)

    scored_detections.sort(
        key=lambda detection: get_score(detection, "cascade_score"),
        reverse=True
    )

    kept: list[dict[str, object]] = []

    for detection in scored_detections:
        box = get_box_from_detection(detection)

        if box is None:
            continue

        should_keep = True

        for kept_detection in kept:
            kept_box = get_box_from_detection(kept_detection)

            if kept_box is None:
                continue

            if box_iou(box, kept_box) > iou_threshold:
                should_keep = False
                break

        if should_keep:
            kept.append(detection)

    return kept


def normalized_region_to_box(
    region: tuple[float, float, float, float],
    image_shape: tuple[int, int, int]
) -> tuple[int, int, int, int]:
    image_h, image_w = image_shape[:2]
    x1_r, y1_r, x2_r, y2_r = region

    x1 = int(x1_r * image_w)
    y1 = int(y1_r * image_h)
    x2 = int(x2_r * image_w)
    y2 = int(y2_r * image_h)

    return x1, y1, x2 - x1, y2 - y1


def center_distance_score(
    box: tuple[int, int, int, int],
    preferred_box: tuple[int, int, int, int],
    image_shape: tuple[int, int, int]
) -> float:
    image_h, image_w = image_shape[:2]

    x, y, w, h = box
    px, py, pw, ph = preferred_box

    cx = x + w / 2
    cy = y + h / 2

    pcx = px + pw / 2
    pcy = py + ph / 2

    dx = (cx - pcx) / image_w
    dy = (cy - pcy) / image_h

    distance = (dx ** 2 + dy ** 2) ** 0.5

    # Convert distance into score from 0 to 1.
    score = 1.0 - min(distance / 0.45, 1.0)

    return score


def preferred_region_overlap_score(
    box: tuple[int, int, int, int],
    preferred_box: tuple[int, int, int, int]
) -> float:
    return box_iou(box, preferred_box)


def expand_box(
    box: tuple[int, int, int, int],
    image_shape: tuple[int, int, int],
    pad_x_ratio: float = 0.08,
    pad_y_ratio: float = 0.25
) -> tuple[int, int, int, int]:
    x, y, w, h = box
    image_h, image_w = image_shape[:2]

    pad_x = int(w * pad_x_ratio)
    pad_y = int(h * pad_y_ratio)

    x1 = max(0, x - pad_x)
    y1 = max(0, y - pad_y)
    x2 = min(image_w, x + w + pad_x)
    y2 = min(image_h, y + h + pad_y)

    return x1, y1, x2, y2


def normalize_plate(plate_image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)

    resized = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    equalized = cv2.equalizeHist(resized)
    blurred = cv2.GaussianBlur(equalized, (3, 3), 0)

    thresholded = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        5
    )

    white_pixels = cv2.countNonZero(thresholded)
    total_pixels = thresholded.shape[0] * thresholded.shape[1]

    if white_pixels > total_pixels / 2:
        thresholded = cv2.bitwise_not(thresholded)

    kernel = np.ones((2, 2), dtype=np.uint8)
    cleaned = cv2.morphologyEx(thresholded, cv2.MORPH_OPEN, kernel, iterations=1)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=1)

    return cleaned


def extract_character_candidates(
    plate_binary: np.ndarray
) -> tuple[np.ndarray, list[tuple[int, int, int, int]]]:
    plate_visual = cv2.cvtColor(plate_binary, cv2.COLOR_GRAY2BGR)

    contours, _ = cv2.findContours(
        plate_binary,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    h_img, w_img = plate_binary.shape[:2]
    candidates: list[tuple[int, int, int, int]] = []

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)

        if h_img == 0 or w_img == 0:
            continue

        char_height_ratio = h / h_img
        char_width_ratio = w / w_img
        aspect_ratio = w / h if h != 0 else 0.0
        area = w * h
        area_ratio = area / (w_img * h_img)

        if char_height_ratio < 0.18:
            continue

        if char_height_ratio > 0.95:
            continue

        if char_width_ratio < 0.006 or char_width_ratio > 0.35:
            continue

        if aspect_ratio < 0.06 or aspect_ratio > 1.50:
            continue

        if area_ratio < 0.001:
            continue

        candidates.append((x, y, w, h))

    candidates.sort(key=lambda box: box[0])

    for (x, y, w, h) in candidates:
        cv2.rectangle(
            plate_visual,
            (x, y),
            (x + w, y + h),
            (255, 0, 0),
            2
        )

    return plate_visual, candidates


def score_primary_candidate(
    image_label: str,
    detection: dict[str, object],
    image_shape: tuple[int, int, int],
    character_count: int
) -> float:
    box = get_box_from_detection(detection)

    if box is None:
        return 0.0

    x, y, w, h = box
    image_h, image_w = image_shape[:2]

    aspect_ratio = w / h if h != 0 else 0.0
    area_ratio = (w * h) / (image_w * image_h)

    cascade_score = get_score(detection, "cascade_score")

    # Preferred-region scoring
    preferred_region = preferred_regions.get(image_label)
    preferred_score = 0.0
    center_score = 0.0

    if preferred_region is not None:
        preferred_box = normalized_region_to_box(preferred_region, image_shape)
        preferred_score = preferred_region_overlap_score(box, preferred_box)
        center_score = center_distance_score(box, preferred_box, image_shape)

    # Aspect scoring
    aspect_quality = 1.0 - abs(aspect_ratio - 4.0) / 4.0
    aspect_quality = max(0.0, min(1.0, aspect_quality))

    # Size scoring
    if 0.001 <= area_ratio <= 0.030:
        size_quality = 1.0
    elif 0.030 < area_ratio <= 0.060:
        size_quality = 0.55
    elif 0.0003 <= area_ratio < 0.001:
        size_quality = 0.65
    else:
        size_quality = 0.15

    # Character scoring is now supportive only, not dominant.
    if 5 <= character_count <= 10:
        char_quality = 1.0
    elif 3 <= character_count <= 12:
        char_quality = 0.70
    elif 1 <= character_count <= 2:
        char_quality = 0.35
    elif 13 <= character_count <= 18:
        char_quality = 0.25
    else:
        char_quality = 0.10

    # Main improvement: preferred location is weighted heavily.
    primary_score = (
        cascade_score * 0.15
        + preferred_score * 140.0
        + center_score * 130.0
        + aspect_quality * 45.0
        + size_quality * 55.0
        + char_quality * 20.0
    )

    return primary_score


def create_blank_panel(label: str, panel_w: int, panel_h: int) -> np.ndarray:
    blank = np.full((panel_h, panel_w, 3), 255, dtype=np.uint8)

    cv2.putText(
        blank,
        label,
        (30, panel_h // 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2,
        cv2.LINE_AA
    )

    return blank


def create_result_row(
    image_label: str,
    original: np.ndarray,
    annotated: np.ndarray,
    plate_crop: np.ndarray | None,
    plate_processed: np.ndarray | None,
    character_visual: np.ndarray | None
) -> np.ndarray:
    panel_w = 280
    panel_h = 210
    label_h = 35

    panel_data: list[tuple[str, np.ndarray | None]] = [
        ("Original", original),
        ("Detected Plate", annotated),
        ("Plate Crop", plate_crop),
        ("Processed Plate", plate_processed),
        ("Character Regions", character_visual),
    ]

    panels: list[np.ndarray] = []

    for title, img in panel_data:
        if img is None:
            display_img = create_blank_panel("No Detection", panel_w, panel_h)
        else:
            if len(img.shape) == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

            display_img = cv2.resize(img, (panel_w, panel_h))

        canvas = np.full((panel_h + label_h, panel_w, 3), 255, dtype=np.uint8)
        canvas[label_h:, :] = display_img

        cv2.putText(
            canvas,
            f"{image_label}: {title}",
            (8, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 0),
            2,
            cv2.LINE_AA
        )

        cv2.rectangle(
            canvas,
            (0, label_h),
            (panel_w - 1, panel_h + label_h - 1),
            (0, 0, 0),
            1
        )

        panels.append(canvas)

    return np.hstack(panels)


def save_image(path: Path, image: np.ndarray) -> None:
    success = cv2.imwrite(str(path), image)

    if not success:
        print(f"WARNING: Failed to save image: {path}")


# ---------------------------------------------------------
# Main processing loop
# ---------------------------------------------------------
summary_rows: list[np.ndarray] = []
csv_rows: list[dict[str, str | int | float]] = []

for label, image_path in input_images.items():
    image = cv2.imread(str(image_path))

    if image is None:
        print(f"WARNING: Could not load image: {image_path}")
        continue

    original = image.copy()
    annotated = image.copy()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    raw_detections = detect_plates_with_cascades(gray)

    preprocessed_gray = preprocess_for_detection(gray)
    processed_detections = detect_plates_with_cascades(preprocessed_gray)

    all_detections = raw_detections + processed_detections
    filtered_detections = filter_plate_candidates(all_detections, image.shape)
    final_detections = non_max_suppression(filtered_detections, image.shape)

    final_detections.sort(
        key=lambda detection: get_score(detection, "cascade_score"),
        reverse=True
    )

    detection_status = "Detected" if final_detections else "Not detected"

    candidate_records: list[dict[str, object]] = []

    for idx, detection in enumerate(final_detections):
        box = get_box_from_detection(detection)

        if box is None:
            continue

        x1, y1, x2, y2 = expand_box(box, image.shape)

        # Draw every retained detection in red.
        cv2.rectangle(
            annotated,
            (x1, y1),
            (x2, y2),
            (0, 0, 255),
            2
        )

        cv2.putText(
            annotated,
            f"Plate {idx + 1}",
            (x1, max(20, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 0, 255),
            2,
            cv2.LINE_AA
        )

        plate_crop = image[y1:y2, x1:x2]

        if plate_crop.size == 0:
            continue

        plate_processed = normalize_plate(plate_crop)
        character_visual, character_candidates = extract_character_candidates(plate_processed)

        character_count = len(character_candidates)

        primary_score = score_primary_candidate(
            label,
            detection,
            image.shape,
            character_count
        )

        detection["primary_score"] = primary_score

        safe_label = label.lower().replace(" ", "_").replace("-", "")
        crop_path = OUTPUT_DIR / f"{safe_label}_plate_{idx + 1}_crop.jpg"
        processed_path = OUTPUT_DIR / f"{safe_label}_plate_{idx + 1}_processed.jpg"
        characters_path = OUTPUT_DIR / f"{safe_label}_plate_{idx + 1}_character_regions.jpg"

        save_image(crop_path, plate_crop)
        save_image(processed_path, plate_processed)
        save_image(characters_path, character_visual)

        candidate_records.append({
            "detection": detection,
            "plate_crop": plate_crop,
            "plate_processed": plate_processed,
            "character_visual": character_visual,
            "character_count": character_count,
            "primary_score": primary_score,
        })

    candidate_records.sort(
        key=lambda record: get_score(record, "primary_score"),
        reverse=True
    )

    primary_plate_crop: np.ndarray | None = None
    primary_plate_processed: np.ndarray | None = None
    primary_character_visual: np.ndarray | None = None
    primary_character_count = 0
    primary_cascade_name = "None"
    primary_detection_score = 0.0
    primary_selection_score = 0.0

    if candidate_records:
        best_record = candidate_records[0]
        best_detection = best_record.get("detection")

        if isinstance(best_detection, dict):
            primary_plate_crop = best_record.get("plate_crop")  # type: ignore
            primary_plate_processed = best_record.get("plate_processed")  # type: ignore
            primary_character_visual = best_record.get("character_visual")  # type: ignore

            char_count_object = best_record.get("character_count")
            if isinstance(char_count_object, int):
                primary_character_count = char_count_object

            primary_cascade_name = str(best_detection.get("cascade_name", "Unknown"))
            primary_detection_score = get_score(best_detection, "cascade_score")
            primary_selection_score = get_score(best_detection, "primary_score")

            # Highlight selected primary detection with thicker red box.
            primary_box = get_box_from_detection(best_detection)
            if primary_box is not None:
                px1, py1, px2, py2 = expand_box(primary_box, image.shape)
                cv2.rectangle(
                    annotated,
                    (px1, py1),
                    (px2, py2),
                    (0, 0, 255),
                    5
                )
                cv2.putText(
                    annotated,
                    "Primary",
                    (px1, max(25, py1 - 12)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.70,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA
                )

    safe_label = label.lower().replace(" ", "_").replace("-", "")
    annotated_path = OUTPUT_DIR / f"{safe_label}_annotated.jpg"
    save_image(annotated_path, annotated)

    summary_rows.append(
        create_result_row(
            label,
            original,
            annotated,
            primary_plate_crop,
            primary_plate_processed,
            primary_character_visual
        )
    )

    csv_rows.append({
        "image_label": label,
        "image_path": str(image_path),
        "detection_status": detection_status,
        "raw_detections": len(raw_detections),
        "processed_detections": len(processed_detections),
        "filtered_detections": len(filtered_detections),
        "final_detections_after_nms": len(final_detections),
        "primary_cascade": primary_cascade_name,
        "primary_detection_score": round(primary_detection_score, 3),
        "primary_selection_score": round(primary_selection_score, 3),
        "primary_character_candidates": primary_character_count,
    })

    print(f"\n{label}")
    print(f"Image path: {image_path}")
    print(f"Detection status: {detection_status}")
    print(f"Raw detections: {len(raw_detections)}")
    print(f"Processed detections: {len(processed_detections)}")
    print(f"Filtered detections: {len(filtered_detections)}")
    print(f"Final detections after NMS: {len(final_detections)}")
    print(f"Primary cascade: {primary_cascade_name}")
    print(f"Primary detection score: {primary_detection_score:.3f}")
    print(f"Primary selection score: {primary_selection_score:.3f}")
    print(f"Primary character candidates found: {primary_character_count}")


# ---------------------------------------------------------
# Save CSV results
# ---------------------------------------------------------
try:
    with open(results_csv, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "image_label",
            "image_path",
            "detection_status",
            "raw_detections",
            "processed_detections",
            "filtered_detections",
            "final_detections_after_nms",
            "primary_cascade",
            "primary_detection_score",
            "primary_selection_score",
            "primary_character_candidates",
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"Saved CSV results to: {results_csv}")

except PermissionError:
    backup_csv = OUTPUT_DIR / f"license_plate_results_backup_{timestamp}.csv"

    with open(backup_csv, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [
            "image_label",
            "image_path",
            "detection_status",
            "raw_detections",
            "processed_detections",
            "filtered_detections",
            "final_detections_after_nms",
            "primary_cascade",
            "primary_detection_score",
            "primary_selection_score",
            "primary_character_candidates",
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    print(f"WARNING: Original CSV path was locked. Saved backup CSV to: {backup_csv}")


# ---------------------------------------------------------
# Save final comparison image
# ---------------------------------------------------------
if summary_rows:
    final_canvas = np.vstack(summary_rows)
    final_output_path = OUTPUT_DIR / "portfolio_license_plate_results.jpg"

    save_image(final_output_path, final_canvas)

    cv2.imshow("Portfolio License Plate Detection Results", final_canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print(f"\nSaved final comparison image to: {final_output_path}")
else:
    print("No images were processed.")