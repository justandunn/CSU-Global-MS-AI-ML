import os
import cv2

print("Current Working Directory:", os.getcwd())

# Image path relative to the CSC515 root folder in VS Code
input_image_path = "MOD1/brain image.jpg"
output_image_path = "MOD1/brain_image_copy.jpg"

# Load the image
image = cv2.imread(input_image_path)

# Check if the image loaded correctly
if image is None:
    raise FileNotFoundError(f"Could not load image at {input_image_path}")

# Display the image
cv2.imshow("Brain Image", image)

# Save a copy of the image
cv2.imwrite(output_image_path, image)

# Wait for a key press before closing the window
cv2.waitKey(0)
cv2.destroyAllWindows()

print(f"Image successfully loaded from: {input_image_path}")
print(f"Copy successfully saved to: {output_image_path}")