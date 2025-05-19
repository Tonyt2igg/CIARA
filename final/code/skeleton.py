import os
import cv2
from skimage.morphology import skeletonize
import numpy as np

# Input and output paths
input_path = r"D:\Traiding model\project5\tech\tech\Unpaired-Portrait-Drawing\results\pretrained\test_200\examples\temp_output\input_image_fake2.png"  # Full path to the input image
output_dir = r"D:\Traiding model\project5\tech\tech\Unpaired-Portrait-Drawing\final\skeleton"  # Directory to save processed images

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Load the image in grayscale
image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)

if image is None:
    print(f"Failed to load image: {input_path}")
else:
    # Binarize the image using thresholding
    _, binary = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY_INV)

    # Perform skeletonization
    skeleton = skeletonize(binary // 255)
    skeleton_image = (skeleton * 255).astype(np.uint8)

    # Invert the skeletonized image to match the original white lines on black background
    final_image = cv2.bitwise_not(skeleton_image)

    # Display the original and final images for debugging
    cv2.imshow('Original', image)
    cv2.imshow('Skeletonized and Inverted', final_image)
    cv2.waitKey(0)  # Wait for key press to proceed

    # Save the final processed image
    output_path = os.path.join(output_dir, f"{os.path.basename(input_path)}")
    cv2.imwrite(output_path, final_image)
    print(f"Processed image saved at: {output_path}")

    # Close all OpenCV windows
    cv2.destroyAllWindows()

print("Processing complete.")
