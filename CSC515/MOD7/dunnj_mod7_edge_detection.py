import os
import cv2
import numpy as np


print("Current Working Directory:", os.getcwd())

# ---------------------------------------------------------
# Output folder
# ---------------------------------------------------------
output_dir = "MOD7"
os.makedirs(output_dir, exist_ok=True)


# ---------------------------------------------------------
# Evaluation Function
# ---------------------------------------------------------
def evaluate_edges(detected_edges, ground_truth_edges, tolerance=1):
    """
    Evaluate detected edges against ground truth using precision, recall, and F1-score.

    A tolerance is used so detected edges within a small neighborhood of the
    ground-truth boundary count as correct.
    """

    detected_binary = (detected_edges > 0).astype(np.uint8)
    ground_truth_binary = (ground_truth_edges > 0).astype(np.uint8)

    kernel_size = 2 * tolerance + 1
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)

    # Dilate ground truth for precision tolerance.
    ground_truth_dilated = cv2.dilate(ground_truth_binary, kernel, iterations=1)

    # Dilate detected edges for recall tolerance.
    detected_dilated = cv2.dilate(detected_binary, kernel, iterations=1)

    true_positive_precision = np.logical_and(
        detected_binary == 1,
        ground_truth_dilated == 1
    ).sum()

    total_detected = detected_binary.sum()

    true_positive_recall = np.logical_and(
        ground_truth_binary == 1,
        detected_dilated == 1
    ).sum()

    total_ground_truth = ground_truth_binary.sum()

    precision = true_positive_precision / total_detected if total_detected > 0 else 0.0
    recall = true_positive_recall / total_ground_truth if total_ground_truth > 0 else 0.0

    if precision + recall == 0:
        f1_score = 0.0
    else:
        f1_score = 2 * (precision * recall) / (precision + recall)

    return precision, recall, f1_score


# ---------------------------------------------------------
# Edge Detection Methods
# ---------------------------------------------------------
def apply_canny(gray_image, low_threshold, high_threshold):
    """Apply Canny edge detection."""
    return cv2.Canny(gray_image, low_threshold, high_threshold)


def apply_sobel(gray_image, threshold_value):
    """
    Apply Sobel edge detection.

    Sobel calculates horizontal and vertical gradients. The gradient magnitude
    is then converted into a binary edge image using NumPy thresholding.
    """

    sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)

    magnitude = np.sqrt((sobel_x ** 2) + (sobel_y ** 2))
    magnitude = np.clip(magnitude, 0, 255).astype(np.uint8)

    sobel_edges = np.where(magnitude >= threshold_value, 255, 0).astype(np.uint8)

    return sobel_edges


def apply_laplacian(gray_image, threshold_value):
    """
    Apply Laplacian edge detection.

    Laplacian calculates second-order intensity changes. The absolute result is
    converted into a binary edge image using NumPy thresholding.
    """

    laplacian = cv2.Laplacian(gray_image, cv2.CV_64F, ksize=3)
    laplacian_abs = np.clip(np.absolute(laplacian), 0, 255).astype(np.uint8)

    laplacian_edges = np.where(laplacian_abs >= threshold_value, 255, 0).astype(np.uint8)

    return laplacian_edges


# ---------------------------------------------------------
# Synthetic Image Generation
# ---------------------------------------------------------
height = 256
width = 256

# Clean image intensities
background_intensity = 40
square_intensity = 140
circle_intensity = 220

clean_image = np.full((height, width), background_intensity, dtype=np.uint8)

# Square coordinates
square_top_left = (40, 50)
square_bottom_right = (110, 120)

# Circle coordinates
circle_center = (180, 165)
circle_radius = 35

# Draw one filled square and one filled circle.
cv2.rectangle(clean_image, square_top_left, square_bottom_right, square_intensity, -1)
cv2.circle(clean_image, circle_center, circle_radius, circle_intensity, -1)

# Ground truth edge map.
ground_truth = np.zeros((height, width), dtype=np.uint8)
cv2.rectangle(ground_truth, square_top_left, square_bottom_right, 255, 1)
cv2.circle(ground_truth, circle_center, circle_radius, 255, 1)

# Save clean image and ground truth.
cv2.imwrite(os.path.join(output_dir, "synthetic_clean_image.jpg"), clean_image)
cv2.imwrite(os.path.join(output_dir, "synthetic_ground_truth_edges.jpg"), ground_truth)


# ---------------------------------------------------------
# Clean Image Edge Detection
# ---------------------------------------------------------
clean_canny = apply_canny(clean_image, 50, 150)
clean_sobel = apply_sobel(clean_image, 60)
clean_laplacian = apply_laplacian(clean_image, 40)

cv2.imwrite(os.path.join(output_dir, "clean_canny_edges.jpg"), clean_canny)
cv2.imwrite(os.path.join(output_dir, "clean_sobel_edges.jpg"), clean_sobel)
cv2.imwrite(os.path.join(output_dir, "clean_laplacian_edges.jpg"), clean_laplacian)


# ---------------------------------------------------------
# Noisy / Lower-Contrast Image Generation
# ---------------------------------------------------------
noisy_background_intensity = 80
noisy_square_intensity = 130
noisy_circle_intensity = 180

noisy_image = np.full((height, width), noisy_background_intensity, dtype=np.uint8)

cv2.rectangle(
    noisy_image,
    square_top_left,
    square_bottom_right,
    noisy_square_intensity,
    -1
)

cv2.circle(
    noisy_image,
    circle_center,
    circle_radius,
    noisy_circle_intensity,
    -1
)

# Add random Gaussian noise.
np.random.seed(42)
noise = np.random.normal(0, 20, (height, width))
noisy_image_float = noisy_image.astype(np.float32) + noise
noisy_image = np.clip(noisy_image_float, 0, 255).astype(np.uint8)

cv2.imwrite(os.path.join(output_dir, "synthetic_noisy_low_contrast_image.jpg"), noisy_image)


# ---------------------------------------------------------
# Noisy Image Edge Detection
# ---------------------------------------------------------
# Thresholds tuned for the noisy and lower-contrast image.
noisy_canny = apply_canny(noisy_image, 75, 175)
noisy_sobel = apply_sobel(noisy_image, 85)
noisy_laplacian = apply_laplacian(noisy_image, 75)

cv2.imwrite(os.path.join(output_dir, "noisy_canny_edges.jpg"), noisy_canny)
cv2.imwrite(os.path.join(output_dir, "noisy_sobel_edges.jpg"), noisy_sobel)
cv2.imwrite(os.path.join(output_dir, "noisy_laplacian_edges.jpg"), noisy_laplacian)


# ---------------------------------------------------------
# Evaluation
# ---------------------------------------------------------
results = {
    "Clean Canny": evaluate_edges(clean_canny, ground_truth),
    "Clean Sobel": evaluate_edges(clean_sobel, ground_truth),
    "Clean Laplacian": evaluate_edges(clean_laplacian, ground_truth),
    "Noisy Canny": evaluate_edges(noisy_canny, ground_truth),
    "Noisy Sobel": evaluate_edges(noisy_sobel, ground_truth),
    "Noisy Laplacian": evaluate_edges(noisy_laplacian, ground_truth),
}

print("\nEdge Detection Evaluation Results")
print("--------------------------------")
print(f"{'Method':<20} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")

for method, (precision, recall, f1_score) in results.items():
    print(f"{method:<20} {precision:<12.3f} {recall:<12.3f} {f1_score:<12.3f}")


# ---------------------------------------------------------
# Build Comparison Image for Discussion Attachment
# ---------------------------------------------------------
def to_bgr(gray_image):
    """Convert a grayscale image to BGR for OpenCV canvas placement."""
    return cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)


panel_w = 220
panel_h = 220
label_h = 40

comparison_images = [
    ("Clean Synthetic", clean_image),
    ("Ground Truth", ground_truth),
    ("Clean Canny", clean_canny),
    ("Clean Sobel", clean_sobel),
    ("Clean Laplacian", clean_laplacian),
    ("Noisy/Low Contrast", noisy_image),
    ("Noisy Canny", noisy_canny),
    ("Noisy Sobel", noisy_sobel),
    ("Noisy Laplacian", noisy_laplacian),
]

cols = 3
rows = 3

canvas = np.full(
    (rows * (panel_h + label_h), cols * panel_w, 3),
    255,
    dtype=np.uint8
)

for idx, (label, img) in enumerate(comparison_images):
    row = idx // cols
    col = idx % cols

    resized = cv2.resize(img, (panel_w, panel_h))
    resized_bgr = to_bgr(resized)

    x1 = col * panel_w
    y1 = row * (panel_h + label_h) + label_h
    x2 = x1 + panel_w
    y2 = y1 + panel_h

    cv2.putText(
        canvas,
        label,
        (x1 + 8, y1 - 12),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 0, 0),
        2,
        cv2.LINE_AA
    )

    canvas[y1:y2, x1:x2] = resized_bgr
    cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 0, 0), 1)

comparison_path = os.path.join(output_dir, "mod7_edge_detection_comparison.jpg")
cv2.imwrite(comparison_path, canvas)

cv2.imshow("Module 7 Edge Detection Comparison", canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(f"\nSaved comparison image to: {comparison_path}")
print("Saved individual output images in MOD7 folder.")