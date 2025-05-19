import pybullet as p
import numpy as np
import pandas as pd
import time
import os

# Initialize PyBullet
physicsClient = p.connect(p.GUI)
p.setGravity(0, 0, -9.81)

# Load URDF model
urdf_path = r"D:\Traiding model\project5\working\ciara5\urdf\ciara5.urdf"
robot_id = p.loadURDF(urdf_path, [0, 0, 0], useFixedBase=True)

# Load saved joint angles (Theta values in degrees)
ik_solutions_path = r"C:\Users\ACER\Documents\joint_angles.csv"
ik_solutions = np.radians(pd.read_csv(ik_solutions_path).values)  # Convert to radians

# Get the number of joints and define the motor 4 index
num_joints = p.getNumJoints(robot_id)
motor_4_index = 3  # Assuming motor 4 is at joint index 3, adjust if needed

# Simulation parameters
SIM_STEPS_PER_MOVE = 5  # Steps per movement for smooth animation
previous_motor_4_position = None  # Store previous position of motor 4

# Move the robot using the loaded joint angles
for joint_angles in ik_solutions:
    # Apply joint positions
    for i in range(num_joints):
        p.setJointMotorControl2(robot_id, i, p.POSITION_CONTROL, targetPosition=joint_angles[i])

    # Step simulation for smooth movement
    for _ in range(SIM_STEPS_PER_MOVE):
        p.stepSimulation()
        time.sleep(1.0 / 960)

    # Get **motor 4** position
    motor_4_state = p.getLinkState(robot_id, motor_4_index, computeForwardKinematics=True)
    current_motor_4_position = np.array(motor_4_state[0])  # Extract position

    # **Shift position by 4 cm in X and 2 cm in Y**
    current_motor_4_position_shifted = current_motor_4_position + np.array([0.03, 0.02, 0])  # X +4cm, Y +2cm

    # Draw movement debug line from shifted Joint 4 position
    if previous_motor_4_position is not None:
        p.addUserDebugLine(previous_motor_4_position, current_motor_4_position_shifted, [0, 0, 1], 2)  # Blue line

    # Update previous position
    previous_motor_4_position = current_motor_4_position_shifted

# Keep simulation running
while True:
    p.stepSimulation()
    time.sleep(1.0 / 240)
