import os
import cv2
import numpy as np

print("Current Working Directory:", os.getcwd())

# ---------------------------------------------------------
# File paths
# ---------------------------------------------------------
input_images = {
    "Indoor Scene": "MOD6/indoor.jpg",
    "Outdoor Scenery": "MOD6/outdoor.jpg",
    "Close-Up Object": "MOD6/closeup.jpg",
}

output_dir = "MOD6"
comparison_output_path = os.path.join(output_dir, "mod6_adaptive_thresholding_results.jpg")

# ---------------------------------------------------------
# Helper function for labeled display panels
# ---------------------------------------------------------
def add_label(image, label):
    label_height = 35
    h, w = image.shape[:2]

    canvas = np.full((h + label_height, w, 3), 255, dtype=np.uint8)

    if len(image.shape) == 2:
        image_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        image_bgr = image

    canvas[label_height:label_height + h, 0:w] = image_bgr

    cv2.putText(
        canvas,
        label,
        (10, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 0, 0),
        2,
        cv2.LINE_AA
    )

    return canvas


# ---------------------------------------------------------
# Adaptive thresholding function
# ---------------------------------------------------------
def process_image(label, image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    # Resize for consistent visual comparison
    display_w = 320
    display_h = 240
    image_resized = cv2.resize(image, (display_w, display_h))

    # Convert to grayscale
    gray = cv2.cvtColor(image_resized, cv2.COLOR_BGR2GRAY)

    # Noise reduction preprocessing
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Global Otsu thresholding for comparison
    _, otsu = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    # Adaptive mean thresholding
    adaptive_mean = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        21,
        5
    )

    # Adaptive Gaussian thresholding
    adaptive_gaussian = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        21,
        5
    )

    # Morphological cleanup to reduce small artifacts
    kernel = np.ones((3, 3), np.uint8)
    adaptive_gaussian_cleaned = cv2.morphologyEx(
        adaptive_gaussian,
        cv2.MORPH_OPEN,
        kernel,
        iterations=1
    )

    adaptive_gaussian_cleaned = cv2.morphologyEx(
        adaptive_gaussian_cleaned,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=1
    )

    # Save individual outputs
    safe_label = label.lower().replace(" ", "_").replace("-", "")
    cv2.imwrite(os.path.join(output_dir, f"{safe_label}_original.jpg"), image_resized)
    cv2.imwrite(os.path.join(output_dir, f"{safe_label}_grayscale.jpg"), gray)
    cv2.imwrite(os.path.join(output_dir, f"{safe_label}_otsu.jpg"), otsu)
    cv2.imwrite(os.path.join(output_dir, f"{safe_label}_adaptive_mean.jpg"), adaptive_mean)
    cv2.imwrite(os.path.join(output_dir, f"{safe_label}_adaptive_gaussian.jpg"), adaptive_gaussian)
    cv2.imwrite(os.path.join(output_dir, f"{safe_label}_adaptive_gaussian_cleaned.jpg"), adaptive_gaussian_cleaned)

    # Return labeled panels for combined comparison image
    panels = [
        add_label(image_resized, f"{label}: Original"),
        add_label(gray, f"{label}: Gray"),
        add_label(otsu, f"{label}: Otsu"),
        add_label(adaptive_mean, f"{label}: Mean"),
        add_label(adaptive_gaussian, f"{label}: Gaussian"),
        add_label(adaptive_gaussian_cleaned, f"{label}: Cleaned"),
    ]

    return panels


# ---------------------------------------------------------
# Process all images
# ---------------------------------------------------------
all_rows = []

for label, path in input_images.items():
    panels = process_image(label, path)

    # Combine six panels horizontally for each image type
    row = np.hstack(panels)
    all_rows.append(row)

# Combine all rows vertically
comparison_canvas = np.vstack(all_rows)

cv2.imwrite(comparison_output_path, comparison_canvas)

cv2.imshow("Module 6 Adaptive Thresholding Results", comparison_canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(f"Saved combined comparison image to: {comparison_output_path}")
print("Saved individual outputs in MOD6 folder.")