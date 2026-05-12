import os
import cv2
import numpy as np

print("Current Working Directory:", os.getcwd())

image_path = "MOD5/latent_fingerprint.jpg"
output_path = "MOD5/fingerprint_morphology_results.jpg"

image = cv2.imread(image_path)

if image is None:
    raise FileNotFoundError(f"Could not load image at {image_path}")

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Threshold image to create binary structure for morphology
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# Invert if needed so ridges are white on black background
# This helps morphology operate on ridge structures as foreground.
white_pixels = cv2.countNonZero(binary)
total_pixels = binary.shape[0] * binary.shape[1]

if white_pixels > total_pixels / 2:
    binary = cv2.bitwise_not(binary)

kernel = np.ones((3, 3), np.uint8)

dilated = cv2.dilate(binary, kernel, iterations=1)
eroded = cv2.erode(binary, kernel, iterations=1)
opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

# Convert all outputs to BGR so labels can be added
images = [
    ("Original", image),
    ("Grayscale", cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)),
    ("Binary / Otsu", cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)),
    ("Dilation", cv2.cvtColor(dilated, cv2.COLOR_GRAY2BGR)),
    ("Erosion", cv2.cvtColor(eroded, cv2.COLOR_GRAY2BGR)),
    ("Opening", cv2.cvtColor(opened, cv2.COLOR_GRAY2BGR)),
    ("Closing", cv2.cvtColor(closed, cv2.COLOR_GRAY2BGR)),
]

panel_w = 260
panel_h = 220
cols = 3
rows = 3
label_h = 35

canvas = np.full(
    (rows * (panel_h + label_h), cols * panel_w, 3),
    255,
    dtype=np.uint8
)

for idx, (label, img) in enumerate(images):
    row = idx // cols
    col = idx % cols

    resized = cv2.resize(img, (panel_w, panel_h))
    x1 = col * panel_w
    y1 = row * (panel_h + label_h) + label_h
    x2 = x1 + panel_w
    y2 = y1 + panel_h

    cv2.putText(
        canvas,
        label,
        (x1 + 10, y1 - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2,
        cv2.LINE_AA
    )

    canvas[y1:y2, x1:x2] = resized
    cv2.rectangle(canvas, (x1, y1), (x2, y2), (0, 0, 0), 1)

cv2.imwrite(output_path, canvas)

cv2.imshow("Fingerprint Morphology Results", canvas)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(f"Saved morphology comparison image to: {output_path}")