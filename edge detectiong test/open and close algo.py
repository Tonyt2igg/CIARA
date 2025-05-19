import cv2
import numpy as np

# Load the sketch image in grayscale
image = cv2.imread(r"C:\projects\cyclegan\tech\Unpaired-Portrait-Drawing\results\pretrained\test_200\examples\temp_output\input_image_fake2.png", cv2.IMREAD_GRAYSCALE)

# Define the kernel for morphological operations
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))  # Change size based on need

# Apply opening to remove small noise
opened = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

# Apply closing to fill small gaps in lines
closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel)

# Highlight sketch lines by subtracting the processed image from the original
sketch_lines = cv2.subtract(image, closed)

# Display the results
cv2.imshow("Original Image", image)
cv2.imshow("Opened Image", opened)
cv2.imshow("Closed Image", closed)
cv2.imshow("Sketch Lines", sketch_lines)

# Wait for a key press and close windows
cv2.waitKey(0)
cv2.destroyAllWindows()
