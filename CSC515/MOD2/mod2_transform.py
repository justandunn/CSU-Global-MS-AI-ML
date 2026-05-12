import os
import cv2
import numpy as np

print("Current Working Directory:", os.getcwd())

image_path = "MOD2/banknotes.jpg"
image = cv2.imread(image_path)

if image is None:
    raise FileNotFoundError(f"Could not load image at {image_path}")

h, w = image.shape[:2]

# 1. Translation
tx, ty = 50, 30
translation_matrix = np.array(
    [
        [1, 0, tx],
        [0, 1, ty]
    ],
    dtype=np.float32
)

translated = cv2.warpAffine(image, translation_matrix, (w, h))

# 2. Rotation
center = (w // 2, h // 2)
angle = 8
scale = 1.0

rotation_matrix = cv2.getRotationMatrix2D(center, angle, scale)
rotated = cv2.warpAffine(image, rotation_matrix, (w, h))

# 3. Perspective transform
src_points = np.array(
    [
        [100, 50],        # top-left
        [w - 100, 40],    # top-right
        [120, h - 60],    # bottom-left
        [w - 80, h - 40]  # bottom-right
    ],
    dtype=np.float32
)

dst_points = np.array(
    [
        [0, 0],
        [w - 1, 0],
        [0, h - 1],
        [w - 1, h - 1]
    ],
    dtype=np.float32
)

perspective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
corrected = cv2.warpPerspective(image, perspective_matrix, (w, h))

# Save outputs
cv2.imwrite("MOD2/banknotes_translated.jpg", translated)
cv2.imwrite("MOD2/banknotes_rotated.jpg", rotated)
cv2.imwrite("MOD2/banknotes_corrected.jpg", corrected)

# Show outputs
cv2.imshow("Original", image)
cv2.imshow("Translated", translated)
cv2.imshow("Rotated", rotated)
cv2.imshow("Corrected", corrected)

cv2.waitKey(0)
cv2.destroyAllWindows()

print("\nTranslation Matrix:\n", translation_matrix)
print("\nRotation Matrix:\n", rotation_matrix)
print("\nPerspective Matrix:\n", perspective_matrix)