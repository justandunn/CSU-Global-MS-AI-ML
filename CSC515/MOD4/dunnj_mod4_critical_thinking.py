import os
import cv2
import numpy as np

print("Current Working Directory:", os.getcwd())

# Since you are running from CSC515 root
image_path = "MOD4/Mod4CT1.jpg"
output_path = "MOD4/mod4_filter_comparison.jpg"

image = cv2.imread(image_path)

if image is None:
    raise FileNotFoundError(f"Could not load image at {image_path}")

# Convert to RGB not required since OpenCV displays in BGR
# Keep everything in OpenCV format

kernels = [3, 5, 7]
sigma1 = 0.5
sigma2 = 1.5

row_labels = ["3x3 Kernel", "5x5 Kernel", "7x7 Kernel"]
col_labels = ["Mean", "Median", "Gaussian s=0.5", "Gaussian s=1.5"]

results = []

for k in kernels:
    mean_img = cv2.blur(image, (k, k))
    median_img = cv2.medianBlur(image, k)
    gaussian1_img = cv2.GaussianBlur(image, (k, k), sigma1)
    gaussian2_img = cv2.GaussianBlur(image, (k, k), sigma2)

    results.append([mean_img, median_img, gaussian1_img, gaussian2_img])

# Standard display size for each panel
panel_w = 260
panel_h = 180

# Margins for labels
left_margin = 140
top_margin = 60
right_margin = 20
bottom_margin = 20

canvas_h = top_margin + 3 * panel_h + bottom_margin
canvas_w = left_margin + 4 * panel_w + right_margin

canvas = np.full((canvas_h, canvas_w, 3), 255, dtype=np.uint8)

# Draw column labels
for j, label in enumerate(col_labels):
    x = left_margin + j * panel_w + 20
    y = 35
    cv2.putText(
        canvas,
        label,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2,
        cv2.LINE_AA
    )

# Draw rows and row labels
for i in range(3):
    label_x = 15
    label_y = top_margin + i * panel_h + panel_h // 2
    cv2.putText(
        canvas,
        row_labels[i],
        (label_x, label_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2,
        cv2.LINE_AA
    )

    for j in range(4):
        resized = cv2.resize(results[i][j], (panel_w, panel_h))
        y1 = top_margin + i * panel_h
        y2 = y1 + panel_h
        x1 = left_margin + j * panel_w
        x2 = x1 + panel_w
        canvas[y1:y2, x1:x2] = resized

        # Optional border around each panel
        cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 0, 0), 1)

# Save output
cv2.imwrite(output_path, canvas)

# Display result
cv2.imshow("Mean, Median, and Gaussian Filter Comparison", canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(f"Comparison image saved to: {output_path}")