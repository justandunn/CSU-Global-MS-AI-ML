import os
import cv2

print("Current Working Directory:", os.getcwd())

# Image path relative to CSC515 root
image_path = "MOD2/puppy.jpg"

# Load the image in color
image = cv2.imread(image_path, cv2.IMREAD_COLOR)

if image is None:
    raise FileNotFoundError(f"Could not load image at {image_path}")

# Split into Blue, Green, Red channels
# OpenCV loads images in BGR order, not RGB
blue_channel, green_channel, red_channel = cv2.split(image)

# Merge channels back into original color image
merged_bgr = cv2.merge((blue_channel, green_channel, red_channel))

# Swap red and green channels to create GRB-style output
# Since OpenCV uses BGR, swapping red and green means:
# original: (B, G, R)
# swapped : (B, R, G)
merged_swapped = cv2.merge((blue_channel, red_channel, green_channel))

# Save output images
cv2.imwrite("MOD2/puppy_blue_channel.jpg", blue_channel)
cv2.imwrite("MOD2/puppy_green_channel.jpg", green_channel)
cv2.imwrite("MOD2/puppy_red_channel.jpg", red_channel)
cv2.imwrite("MOD2/puppy_merged_original.jpg", merged_bgr)
cv2.imwrite("MOD2/puppy_merged_swapped_grb.jpg", merged_swapped)

# Display original and channel images
cv2.imshow("Original Color Image", image)
cv2.imshow("Blue Channel (2D)", blue_channel)
cv2.imshow("Green Channel (2D)", green_channel)
cv2.imshow("Red Channel (2D)", red_channel)
cv2.imshow("Merged Original Color Image", merged_bgr)
cv2.imshow("Merged with Red and Green Swapped", merged_swapped)

cv2.waitKey(0)
cv2.destroyAllWindows()

print("Image loaded successfully.")
print("Blue channel shape:", blue_channel.shape)
print("Green channel shape:", green_channel.shape)
print("Red channel shape:", red_channel.shape)
print("Original image shape:", image.shape)
print("Merged original image saved as: MOD2/puppy_merged_original.jpg")
print("Swapped GRB image saved as: MOD2/puppy_merged_swapped_grb.jpg")