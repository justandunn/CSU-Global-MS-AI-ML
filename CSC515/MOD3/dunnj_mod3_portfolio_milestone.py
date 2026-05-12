import os
from pathlib import Path
import cv2

print("Current Working Directory:", os.getcwd())

image_path = "me.jpg"
output_path = "me_annotated.jpg"

image = cv2.imread(image_path)

if image is None:
    raise FileNotFoundError(f"Could not load image at {image_path}")

annotated = image.copy()
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Build Haar cascade path
cv2_base = Path(cv2.__file__).resolve().parent
haar_dir = cv2_base / "data"

face_cascade_path = str(haar_dir / "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(face_cascade_path)

if face_cascade.empty():
    raise RuntimeError(f"Could not load face cascade classifier from {face_cascade_path}")

# Detect faces
faces = face_cascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(80, 80)
)

if len(faces) == 0:
    raise RuntimeError("No face detected.")

# Keep the largest detected face
x, y, w, h = max(faces, key=lambda f: f[2] * f[3])

# Draw green circle around face
center_x = x + w // 2
center_y = y + h // 2
radius = max(w, h) // 2

cv2.circle(annotated, (center_x, center_y), radius, (0, 255, 0), 3)

# Manual eye boxes based on detected face proportions
left_eye_x1 = x + int(w * 0.18)
left_eye_y1 = y + int(h * 0.35)
left_eye_x2 = x + int(w * 0.42)
left_eye_y2 = y + int(h * 0.52)

right_eye_x1 = x + int(w * 0.58)
right_eye_y1 = y + int(h * 0.30)
right_eye_x2 = x + int(w * 0.82)
right_eye_y2 = y + int(h * 0.48)

cv2.rectangle(
    annotated,
    (left_eye_x1, left_eye_y1),
    (left_eye_x2, left_eye_y2),
    (0, 0, 255),
    2
)

cv2.rectangle(
    annotated,
    (right_eye_x1, right_eye_y1),
    (right_eye_x2, right_eye_y2),
    (0, 0, 255),
    2
)

# Add text
text_x = max(20, x)
text_y = min(image.shape[0] - 20, y + h + 40)

cv2.putText(
    annotated,
    "this is me",
    (text_x, text_y),
    cv2.FONT_HERSHEY_SIMPLEX,
    1.0,
    (255, 255, 255),
    2,
    cv2.LINE_AA
)

cv2.imwrite(output_path, annotated)

cv2.imshow("Annotated Self Image", annotated)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(f"Detected face at: x={x}, y={y}, w={w}, h={h}")
print(f"Annotated image saved to: {output_path}")