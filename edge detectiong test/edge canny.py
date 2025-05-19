import cv2

# Load the image in grayscale
image = cv2.imread(r"C:\projects\cyclegan\tech\Unpaired-Portrait-Drawing\results\pretrained\test_200\examples\temp_output\input_image_fake2.png", cv2.IMREAD_GRAYSCALE)

# Apply Gaussian blur to reduce noise
blurred = cv2.GaussianBlur(image, (5, 5), 0)

# Apply Canny edge detection
edges = cv2.Canny(blurred, 200, 150)  # Adjust thresholds (50 and 150)

# Display results
cv2.imshow("Original Image", image)
cv2.imshow("Sketch Lines (Canny)", edges)
cv2.waitKey(0)
cv2.destroyAllWindows()
