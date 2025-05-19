import requests
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
import subprocess
import os

def fetch_image(object_to_draw):
    api_key = "D04D2174.15F6418685411D3E0F0C1FF4"
    
    # Enhanced prompt to guide Pollinations AI effectively
    prompt = f"Image of {object_to_draw} with plain background, dark edges, thick lines, easy to draw"
    
    width = 768
    height = 768
    seed = 42
    model = 'flux'

    base_url = "https://pollinations.ai/p/"
    image_url = f"{base_url}{prompt}?width={width}&height={height}&seed={seed}&model={model}&key={api_key}"
    print(f"Fetching image from Pollinations for prompt: {prompt}")

    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            print("Image successfully fetched!")
            img = Image.open(BytesIO(response.content))

            # Save the image to the specified path
            save_path = r"D:\CIARA\1csv_transfer\CSV\vs_code\polinated_image.png"
            img.save(save_path)
            print(f"Image saved to {save_path}")

            img.show()  # Display the fetched image (optional)
            waypoints = process_image(img)
            return waypoints
        else:
            print(f"Error fetching image: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

    print(f"No images found for {object_to_draw}.")
    return None

def run_cyclegan_script(input_image_path, output_image_path):
    script_path = r"D:\CIARA\test_seq_style.py"
    command = [
        "python",
        script_path,
        "--input_image", input_image_path,
        "--output_image", output_image_path
    ]
    print(f"Running CycleGAN script: {command}")
    try:
        subprocess.run(command, check=True)
        print("CycleGAN processing completed.")
    except subprocess.CalledProcessError as e:
        print(f"Error running CycleGAN script: {e}")
        raise

def crop_image(img):
    try:
        img_np = np.array(img)
        if img_np is None:
            print("Failed to convert image to NumPy array.")
            return None

        print(f"Image shape: {img_np.shape}")

        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        roi = cv2.selectROI("Select Region to Crop", img_bgr, showCrosshair=True)
        cv2.destroyAllWindows()

        if roi == (0, 0, 0, 0):
            print("No region selected. Using the full image.")
            return img_bgr

        x, y, w, h = roi
        cropped_img = img_bgr[int(y):int(y + h), int(x):int(x + w)]
        return cropped_img
    except Exception as e:
        print(f"An error occurred during cropping: {e}")
        return None

def save_image_to_folder(img, folder_path, filename="input_image_real.png"):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    file_path = os.path.join(folder_path, filename)
    cv2.imwrite(file_path, img)
    print(f"Image saved to {file_path}")
    return file_path

def call_additional_scripts():
    script1_path = r"D:\CIARA\new_wap.py"
    command1 = ["python", script1_path]
    print(f"Running additional script 1: {command1}")
    try:
        subprocess.run(command1, check=True)
        print("Successfully ran new_wap.py")
    except subprocess.CalledProcessError as e:
        print(f"Error running new_wap.py: {e}")
    
    script2_path = r"D:\CIARA\stroke_arm.py"
    command2 = ["python", script2_path]
    print(f"Running additional script 2: {command2}")
    try:
        subprocess.run(command2, check=True)
        print("Successfully ran final.py")
    except subprocess.CalledProcessError as e:
        print(f"Error running final.py: {e}")

def display_generated_images_and_select():
    styled_image_paths = [
        r"D:\CIARA\results\pretrained\test_200\examples\temp_output\input_image_fake1.png"
        r"D:\CIARA\results\pretrained\test_200\examples\temp_output\input_image_fake2.png",
        r"D:\CIARA\results\pretrained\test_200\examples\temp_output\input_image_fake3.png"
    ]

    opencv_images = [cv2.imread(img_path) for img_path in styled_image_paths]

    for i, img in enumerate(opencv_images):
        if img is None:
            print(f"Error: Could not load image {styled_image_paths[i]}")
            return None

    combined_image = np.hstack(opencv_images)

    window_name = "Select a Style"
    cv2.imshow(window_name, combined_image)
    print("Click on the style you want to select (left, middle, or right).")

    selected_index = -1

    def mouse_callback(event, x, y, flags, param):
        nonlocal selected_index
        if event == cv2.EVENT_LBUTTONDOWN:
            width_per_image = combined_image.shape[1] // len(opencv_images)
            selected_index = x // width_per_image
            cv2.destroyAllWindows()

    cv2.setMouseCallback(window_name, mouse_callback)
    cv2.waitKey(0)

    if selected_index >= 0 and selected_index < len(styled_image_paths):
        print(f"Selected style {selected_index + 1}.")
        return styled_image_paths[selected_index]
    else:
        print("No style selected. Defaulting to the first style.")
        return styled_image_paths[0]

def process_image(img):
    try:
        img_cropped = crop_image(img)
        if img_cropped is None:
            print("Cropping failed. Exiting process_image.")
            return None

        input_image_path = "input_cropped.png"
        output_image_path = r"D:\CIARA\results\pretrained\test_200\examples\temp_output\input_image_fake1.png"

        cv2.imwrite(input_image_path, img_cropped)

        run_cyclegan_script(input_image_path, output_image_path)
        call_additional_scripts()

        output_image_path = r"D:\CIARA\results\pretrained\test_200\examples\temp_output\input_image_fake2.png"
        image_with_dots = cv2.imread(output_image_path)

        if image_with_dots is None:
            print(f"Failed to load image with red dots from {output_image_path}.")
            return None

        return image_with_dots

    except Exception as e:
        print(f"Error in process_image: {e}")
        return None
def main():
    print("Welcome to the Image Processing and Drawing Pipeline!")
    object_to_draw = input("Enter the object you want to draw: ")

    # Step 1: Fetch the image using Pollinations AI API
    waypoints = fetch_image(object_to_draw)
    if waypoints is None:
        print("Failed to generate image and waypoints. Exiting.")
        return

    # Step 2: Process the image and apply CycleGAN
    img_path = "input_image_real.png"
    if not os.path.exists(img_path):
        print(f"Error: {img_path} does not exist.")
        return

    processed_img = process_image(waypoints)
    if processed_img is None:
        print("Image processing failed. Exiting.")
        return

    # Step 3: Display styled images and allow user selection
    selected_style_path = display_generated_images_and_select()
    if selected_style_path is None:
        print("No style selected. Exiting.")
        return

    print(f"You selected the styled image at: {selected_style_path}")
    
    # Step 4: Run additional scripts for drawing with the robotic arm
    call_additional_scripts()

if __name__ == "__main__":
    main()