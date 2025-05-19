from skimage.morphology import skeletonize
import cv2
import numpy as np

image = cv2.imread(r"C:\projects\cyclegan\tech\Unpaired-Portrait-Drawing\results\pretrained\test_200\examples\temp_output\input_image_fake2.png", cv2.IMREAD_GRAYSCALE)
_, binary = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY_INV)

skeleton = skeletonize(binary // 255) 
skeleton_image = (skeleton * 255).astype(np.uint8)

cv2.imshow('Original', image)
cv2.imshow('Skeletonized', skeleton_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
