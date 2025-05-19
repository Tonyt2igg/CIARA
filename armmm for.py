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
ik_solutions_path = r"D:\ras_sh\sav_vs\ik_solved_deg.csv"
ik_solutions = np.radians(pd.read_csv(ik_solutions_path).values)  # Convert to radians

# Get the number of joints and define the reference frame index
num_joints = p.getNumJoints(robot_id)
joint_3_index = 2  # Assuming joint_3 is at index 2, adjust if needed

# Simulation parameters
SIM_STEPS_PER_MOVE = 5  # Steps per movement for smooth animation
previous_joint_3_position = None  # Store previous position of joint_3

# Move the robot using the loaded joint angles
for joint_angles in ik_solutions:
    # Apply joint positions
    for i in range(num_joints):
        p.setJointMotorControl2(robot_id, i, p.POSITION_CONTROL, targetPosition=joint_angles[i])

    # Step simulation for smooth movement
    for _ in range(SIM_STEPS_PER_MOVE):
        p.stepSimulation()
        time.sleep(1.0 / 960)

    # Get **joint_3** position
    joint_3_state = p.getLinkState(robot_id, joint_3_index)
    current_joint_3_position = joint_3_state[0]  # Extract position

    # Draw debug line from joint_3's movement
    if previous_joint_3_position is not None:
        p.addUserDebugLine(previous_joint_3_position, current_joint_3_position, [1, 0, 0], 2, 0)  # Red line

    # Update previous position
    previous_joint_3_position = current_joint_3_position

# Keep simulation running
while True:
    p.stepSimulation()
    time.sleep(1.0 / 240)