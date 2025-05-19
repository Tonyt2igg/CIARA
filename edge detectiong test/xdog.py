import cv2
import numpy as np

# Load the image in grayscale
image = cv2.imread(r"C:\projects\cyclegan\tech\Unpaired-Portrait-Drawing\results\pretrained\test_200\examples\temp_output\input_image_fake2.png", cv2.IMREAD_GRAYSCALE)

# Apply Gaussian blur (twice with different sigmas)
blur1 = cv2.GaussianBlur(image, (5, 5), 0)
blur2 = cv2.GaussianBlur(image, (9, 9), 0)

# Compute Difference of Gaussians
dog = cv2.subtract(blur1, blur2)

# Normalize and threshold
dog = cv2.normalize(dog, None, 0, 255, cv2.NORM_MINMAX)
_, sketch = cv2.threshold(dog, 50, 255, cv2.THRESH_BINARY)

# Display results
cv2.imshow("Original Image", image)
cv2.imshow("Sketch Lines (DoG)", sketch)
cv2.waitKey(0)
cv2.destroyAllWindows()
