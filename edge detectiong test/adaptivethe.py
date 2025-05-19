import cv2

# Load the image in grayscale
image = cv2.imread(r"C:\Users\tonyb\Downloads\testing\pencil_sketches\images\New folder\input_image_fake2.png", cv2.IMREAD_GRAYSCALE)

# Apply adaptive thresholding
adaptive_thresh = cv2.adaptiveThreshold(
    image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
)

# Display results
cv2.imshow("Original Image", image)
cv2.imshow("Sketch Lines (Adaptive Thresholding)", adaptive_thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()
