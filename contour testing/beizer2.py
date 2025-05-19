from skimage.morphology import medial_axis
import cv2
import numpy as np

# Load and preprocess the image
image = cv2.imread(r"C:\projects\cyclegan\tech\Unpaired-Portrait-Drawing\results\pretrained\test_200\examples\temp_output\input_image_fake2.png", cv2.IMREAD_GRAYSCALE)
_, binary = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY_INV)

# Compute the medial axis
skeleton, distance = medial_axis(binary // 255, return_distance=True)
skeleton_image = (skeleton * 255).astype(np.uint8)

# Show the result
cv2.imshow('Original', image)
cv2.imshow('Medial Axis', skeleton_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
