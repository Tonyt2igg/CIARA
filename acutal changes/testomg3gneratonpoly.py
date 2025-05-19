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

def fetch_images(object_to_draw):
    api_key = "D04D2174.15F6418685411D3E0F0C1FF4"
    prompt = object_to_draw
    width = 768
    height = 768
    seed = 42
    model = 'flux'

    base_url = "https://pollinations.ai/p/"
    images = []

    for i in range(3):  # Generate three images with different seeds
        image_url = f"{base_url}{prompt}?width={width}&height={height}&seed={seed + i}&model={model}&key={api_key}"
        print(f"Fetching image {i + 1} from Pollinations for prompt: {prompt}")

        try:
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                print(f"Image {i + 1} successfully fetched!")
                img = Image.open(BytesIO(response.content))
                images.append(img)
            else:
                print(f"Error fetching image {i + 1}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"An error occurred while fetching image {i + 1}: {e}")

    if not images:
        print(f"No images found for {object_to_draw}.")
        return None

    selected_image = display_images_and_select(images)
    return selected_image


def display_images_and_select(images):
    """
    Display multiple images in a single window and let the user select one by clicking on it.
    :param images: List of PIL.Image objects.
    :return: The selected PIL.Image object.
    """
    # Convert PIL images to OpenCV format for display
    opencv_images = [cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR) for img in images]

    # Combine images horizontally for display
    combined_image = np.hstack(opencv_images)

    # Display the combined image
    window_name = "Select an Image"
    cv2.imshow(window_name, combined_image)
    print("Click on the image you want to select (left, middle, or right).")
    
    selected_image_index = -1

    def mouse_callback(event, x, y, flags, param):
        nonlocal selected_image_index
        if event == cv2.EVENT_LBUTTONDOWN:
            width_per_image = combined_image.shape[1] // len(images)
            selected_image_index = x // width_per_image
            cv2.destroyAllWindows()

    cv2.setMouseCallback(window_name, mouse_callback)
    cv2.waitKey(0)

    if selected_image_index >= 0 and selected_image_index < len(images):
        print(f"Selected image {selected_image_index + 1}.")
        return images[selected_image_index]
    else:
        print("No image selected. Defaulting to the first image.")
        return images[0]

def run_cyclegan_script(input_image_path, output_image_path):
    script_path = r"C:\projects\cyclegan\tech\Unpaired-Portrait-Drawing\test_seq_style.py"
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
    # Convert PIL image to NumPy array
    try:
        img_np = np.array(img)
        if img_np is None:
            print("Failed to convert image to NumPy array.")
            return None

        # Check the shape of the image
        print(f"Image shape: {img_np.shape}")

        # Convert to OpenCV format (BGR)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Use OpenCV to select ROI
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


if os.path.exists('input_image_fake.png'):
    print("Output image generated successfully.")
else:
    print("No output image found. Check CycleGAN processing.")

def process_image(img):
    img_cropped = crop_image(img)
    input_image_path = "input_cropped.png"
    output_image_path = r"C:\projects\cyclegan\tech\Unpaired-Portrait-Drawing\results\pretrained\test_200\examples\temp_output\input_image_fake.png"

    cv2.imwrite(input_image_path, img_cropped)

    # Run the CycleGAN script to generate the sketch
    run_cyclegan_script(input_image_path, output_image_path)

    # Load the generated sketch
    sketch = cv2.imread(output_image_path, cv2.IMREAD_GRAYSCALE)

    img_blurred = cv2.GaussianBlur(sketch, (5, 5), 0)
    edges = cv2.Canny(img_blurred, 25, 100)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    simplified_contours = []
    for contour in contours:
        epsilon = 0.05 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        simplified_contours.append(approx)

    waypoints = []
    for contour in simplified_contours:
        for point in contour:
            x, y = point[0]
            waypoints.append((x, y))

    return waypoints


def normalize_path(waypoints, workspace_size=(0.4, 0.4)):
    x_vals, y_vals = zip(*waypoints)
    x_scaled = np.interp(x_vals, (min(x_vals), max(x_vals)), (-workspace_size[0]/2, workspace_size[0]/2))
    y_scaled = np.interp(y_vals, (min(y_vals), max(y_vals)), (-workspace_size[1]/2, workspace_size[1]/2))
    normalized_waypoints = list(zip(x_scaled, y_scaled))
    print(f"Normalized waypoints: {normalized_waypoints}")
    return normalized_waypoints

def move_to_waypoints_humanlike(kuka_id, waypoints, lift_pen_distance=0.02, z_draw=0.1, z_lift=0.2):
    """
    Move the robotic arm through waypoints with human-like drawing behavior.
    
    :param kuka_id: ID of the KUKA robot in PyBullet.
    :param waypoints: List of (x, y) coordinates.
    :param lift_pen_distance: Minimum distance change between points to lift the pen.
    :param z_draw: Z-axis position when drawing.
    :param z_lift: Z-axis position when moving without drawing.
    """
    previous_position = None
    for wp in waypoints:
        x, y = wp
        
        # Check if we need to lift the pen
        if previous_position is not None:
            px, py = previous_position[:2]
            if abs(x - px) > lift_pen_distance or abs(y - py) > lift_pen_distance:
                z = z_lift  # Lift the pen
            else:
                z = z_draw  # Keep drawing
        else:
            z = z_lift  # First point, lift the pen

        target_position = [x, y, z]

        # Add debug lines for visualization
        if previous_position is not None:
            p.addUserDebugLine(previous_position, target_position, lineColorRGB=[1, 0, 0], lineWidth=2)

        previous_position = target_position

        # Move the robot to the target position
        joint_positions = p.calculateInverseKinematics(kuka_id, 6, target_position)
        for joint_index in range(7):
            p.setJointMotorControl2(kuka_id, joint_index, p.POSITION_CONTROL, joint_positions[joint_index])

        for _ in range(20):  # Allow time for the robot to reach the position
            p.stepSimulation()
            time.sleep(1./480.)

        print(f"Moved to waypoint: {x}, {y}, {z}")


def main_workflow():
    object_to_draw = input("Enter the object to draw: ")
    normalized_waypoints = fetch_images(object_to_draw)
    if normalized_waypoints:
        print(f"Normalized waypoints: {normalized_waypoints}")
        move_to_waypoints_humanlike(kuka_id, normalized_waypoints)
    else:
        print("No image or edge detection results found for the object.")
    while True:
        time.sleep(1)

p.connect(p.GUI)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
p.setGravity(0, 0, -9.8)

kuka_id = p.loadURDF("kuka_iiwa/model.urdf", basePosition=[0, 0, 0.5])

if __name__ == "__main__":
    main_workflow()
    p.disconnect()