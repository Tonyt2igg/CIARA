import pybullet as p
import pybullet_data
import time
import requests
from PIL import Image
from io import BytesIO
import cv2
import numpy as np
import subprocess
import os
import csv
import math

def fetch_image(object_to_draw):
    api_key = "D04D2174.15F6418685411D3E0F0C1FF4"
    prompt = object_to_draw
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
            waypoints = process_image(img)
            normalized_waypoints = normalize_path(waypoints, workspace_size=(0.25, 0.25))  # Adjusted for 25 cm x 25 cm workspace
            img.show()
            return normalized_waypoints
        else:
            print(f"Error fetching image: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

    print(f"No images found for {object_to_draw}.")
    return None

def run_cyclegan_script(input_image_path, output_image_path):
    script_path = r"D:\Traiding model\project5\tech\tech\Unpaired-Portrait-Drawing\test_seq_style.py"
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
    script1_path = r"D:\Traiding model\project5\tech\tech\Unpaired-Portrait-Drawing\new_wap.py"
    command1 = ["python", script1_path]
    print(f"Running additional script 1: {command1}")
    try:
        subprocess.run(command1, check=True)
        print("Successfully ran new_wap.py")
    except subprocess.CalledProcessError as e:
        print(f"Error running new_wap.py: {e}")
    
    script2_path = r"D:\Traiding model\project5\tech\tech\Unpaired-Portrait-Drawing\final.py"
    command2 = ["python", script2_path]
    print(f"Running additional script 2: {command2}")
    try:
        subprocess.run(command2, check=True)
        print("Successfully ran final.py")
    except subprocess.CalledProcessError as e:
        print(f"Error running final.py: {e}")

def display_generated_images_and_select():
    styled_image_paths = [
        r"D:\Traiding model\project5\tech\tech\Unpaired-Portrait-Drawing\results\pretrained\test_200\examples\temp_output\input_image_fake1.png",
        r"D:\Traiding model\project5\tech\tech\Unpaired-Portrait-Drawing\results\pretrained\test_200\examples\temp_output\input_image_fake2.png",
        r"D:\Traiding model\project5\tech\tech\Unpaired-Portrait-Drawing\results\pretrained\test_200\examples\temp_output\input_image_fake3.png"
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
        output_image_path = r"D:\Traiding model\project5\tech\tech\Unpaired-Portrait-Drawing\results\pretrained\test_200\examples\temp_output\input_image_fake1.png"

        cv2.imwrite(input_image_path, img_cropped)

        run_cyclegan_script(input_image_path, output_image_path)
        call_additional_scripts()

        output_image_path = r"D:\Traiding model\project5\tech\tech\Unpaired-Portrait-Drawing\results\pretrained\test_200\examples\temp_output\input_image_fake2.png"
        image_with_dots = cv2.imread(output_image_path)

        if image_with_dots is None:
            print(f"Failed to load image with red dots from {output_image_path}.")
            return None

        waypoints = extract_red_dots_coordinates(image_with_dots)

        return waypoints

    except Exception as e:
        print(f"Error in process_image: {e}")
        return None

def extract_red_dots_coordinates(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    waypoints = []
    for contour in contours:
        for point in contour:
            x, y = point[0]
            waypoints.append((x, y))

    return waypoints

import numpy as np

def normalize_path(waypoints, workspace_size=(0.18, 0.18), z_draw=0.01, x_offset=0, y_offset=0.22):
    x_vals, y_vals = zip(*waypoints)
    x_scaled = np.interp(x_vals, (min(x_vals), max(x_vals)), (-workspace_size[0]/2, workspace_size[0]/2))
    y_scaled = np.interp(y_vals, (min(y_vals), max(y_vals)), (-workspace_size[1]/2, workspace_size[1]/2))
    
    normalized_waypoints = []
    for x, y in zip(x_scaled, y_scaled):
        x_offseted = x + x_offset
        y_offseted = y + y_offset
        normalized_waypoints.append((x_offseted, y_offseted, z_draw))  # Fixed Z
    
    print(f"Normalized waypoints: {normalized_waypoints}")
    return normalized_waypoints

def save_waypoints_to_csv(waypoints, file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["X", "Y","Z"])
        for wp in waypoints:
            writer.writerow(wp)
    print(f"Waypoints saved to {file_path}")

def move_to_waypoints_humanlike(kuka_id, waypoints, distance_threshold=0.011, z_draw=0.01, z_lift=0.05):
    remaining_waypoints = waypoints[:]
    current_position = None
    drawing = False

    while remaining_waypoints:
        if current_position is None:
            next_wp = remaining_waypoints.pop(0)
        else:
            distances = [math.sqrt((wp[0] - current_position[0])**2 + (wp[1] - current_position[1])**2) 
                         for wp in remaining_waypoints]
            nearest_index = distances.index(min(distances))
            next_wp = remaining_waypoints.pop(nearest_index)

        x, y, z = next_wp

        if current_position is not None:
            distance = math.sqrt((x - current_position[0])**2 + (y - current_position[1])**2)
            if distance > distance_threshold:
                z = z_lift
                drawing = False
            else:
                z = z_draw
                drawing = True
        else:
            z = z_lift
            drawing = False

        target_position = [x, y, z]

        if drawing and current_position is not None and current_position[2] == z_draw:
            p.addUserDebugLine(current_position, target_position, lineColorRGB=[1, 0, 0], lineWidth=2)

        current_position = target_position

        joint_positions = p.calculateInverseKinematics(kuka_id, 6, target_position)
        for joint_index in range(7):
            p.setJointMotorControl2(kuka_id, joint_index, p.POSITION_CONTROL, joint_positions[joint_index])

        for _ in range(20):
            p.stepSimulation()
            time.sleep(1. / 480.)

        print(f"Moved to waypoint: {x}, {y}, {z} (Drawing: {drawing})")

def main_workflow():
    object_to_draw = input("Enter the object to draw: ")
    normalized_waypoints = fetch_image(object_to_draw)
    if normalized_waypoints:
        print(f"Normalized waypoints: {normalized_waypoints}")
        save_waypoints_to_csv(normalized_waypoints, r"D:\ras_sh\waypoints.csv")
        move_to_waypoints_humanlike(kuka_id, normalized_waypoints)
    else:
        print("No image or edge detection results found for the object.")
    while True:
        time.sleep(1)

p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)

kuka_id = p.loadURDF("kuka_iiwa/model.urdf", basePosition=[0, 0, 0])

if __name__ == "__main__":
    main_workflow()
    p.disconnect()