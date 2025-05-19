import pybullet as p
import numpy as np
import pandas as pd
import time
import os
import cv2

# Initialize PyBullet
physicsClient = p.connect(p.GUI)
p.setGravity(0, 0, -9.81)

# Load URDF model
urdf_path = r"D:\Traiding model\project5\working\ciara5\urdf\ciara5.urdf"
robot_id = p.loadURDF(urdf_path, [0, 0, 0], useFixedBase=True)

# Load saved joint angles (Theta values in degrees)
ik_solutions_path = r"C:\Users\ACER\Documents\cat.csv"
ik_solutions = np.radians(pd.read_csv(ik_solutions_path).values)  # Convert to radians

# Get the number of joints and define the motor 4 index
num_joints = p.getNumJoints(robot_id)
motor_4_index = 3  # Assuming motor 4 is at joint index 3, adjust if needed

# Simulation parameters
SIM_STEPS_PER_MOVE = 5  # Steps per movement for smooth animation
previous_motor_4_position = None  # Store previous position of motor 4

# Create output folder if it doesn't exist
output_path = r"D:\ras_sh\temp"
os.makedirs(output_path, exist_ok=True)

# Camera setup parameters for capturing the view
camera_target_position = [0, 0, 0]  # Center the camera on the robot
camera_distance = 1.5  # Distance from the robot
camera_yaw, camera_pitch = 50, -30  # Angles for better view

# Function to save PyBullet's rendered image as a file
def save_simulation_image(file_path):
    width, height, _, _, _, _, rgb_img, _, _ = p.getCameraImage(
        width=640, height=480,
        viewMatrix=p.computeViewMatrixFromYawPitchRoll(camera_target_position, camera_distance, camera_yaw, camera_pitch, 0, 2),
        projectionMatrix=p.computeProjectionMatrixFOV(fov=60, aspect=1.0, nearVal=0.1, farVal=10.0)
    )
    # Convert image to save as PNG
    rgb_img = np.reshape(rgb_img, (height, width, 4))[:, :, :3]  # Keep RGB channels only
    rgb_img = cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR)  # Convert from RGB to BGR
    cv2.imwrite(file_path, rgb_img)

# Move the robot using the loaded joint angles (Waypoint Execution)
for joint_angles in ik_solutions:
    # Apply joint positions for each joint
    for i in range(num_joints):
        p.setJointMotorControl2(robot_id, i, p.POSITION_CONTROL, targetPosition=joint_angles[i])

    # Step simulation for smooth movement
    for _ in range(SIM_STEPS_PER_MOVE):
        p.stepSimulation()
        time.sleep(1.0 / 960)

    # Get motor 4 position and draw debug line
    motor_4_state = p.getLinkState(robot_id, motor_4_index)
    current_motor_4_position = motor_4_state[0]  # Extract position

    if previous_motor_4_position is not None:
        p.addUserDebugLine(previous_motor_4_position, current_motor_4_position, [0, 0, 1], 2, 0)  # Blue line

    previous_motor_4_position = current_motor_4_position

# Move to Home Position after finishing waypoints
home_position = [0] * num_joints  # Assuming home position is all joints set to 0 degrees (adjust if needed)
for i in range(num_joints):
    p.resetJointState(robot_id, i, targetValue=home_position[i])
    p.setJointMotorControl2(robot_id, i, p.POSITION_CONTROL, targetPosition=home_position[i])

# Step the simulation for home position move
for _ in range(240):
    p.stepSimulation()
    time.sleep(1.0 / 960)

# Save the final image with debug lines to the folder
image_save_path = os.path.join(output_path, "final_debug_line_image.png")
save_simulation_image(image_save_path)
print(f"Final image with debug lines saved at {image_save_path}")

# Keep simulation running and interactive after completion
while True:
    p.stepSimulation()
    time.sleep(1.0 / 240)
