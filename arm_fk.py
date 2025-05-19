import pybullet as p
import numpy as np
import pandas as pd
import time
import os

# Initialize PyBullet
physicsClient = p.connect(p.GUI)
p.setGravity(0, 0, -9.81)

# Load URDF model
urdf_path = r"D:\Traiding model\project5\working\CIARAFINAL\CIARAFINAL\urdf\CIARAFINAL.urdf"
robot_id = p.loadURDF(urdf_path, [0, 0, 0], useFixedBase=1)

# Load saved IK solutions (Theta values in radians)
ik_solutions_path = r'D:\ras_sh\sav_vs\ik_solved_rad.csv'
ik_solutions = pd.read_csv(ik_solutions_path).values

# Get the number of joints
num_joints = p.getNumJoints(robot_id)

# Parameters
SIM_STEPS_PER_MOVE = 5  # Steps per movement for smooth animation

# Initialize previous end-effector position for debug lines
previous_ee_position = None

# Move the robot using the loaded joint angles
for joint_angles in ik_solutions:
    # Apply joint positions
    for i in range(num_joints):
        p.setJointMotorControl2(robot_id, i, p.POSITION_CONTROL, targetPosition=joint_angles[i])

    # Step simulation for smooth movement
    for _ in range(SIM_STEPS_PER_MOVE):
        p.stepSimulation()
        time.sleep(1./960)

    # Get current end-effector position
    ee_state = p.getLinkState(robot_id, num_joints - 1)
    current_ee_position = ee_state[0]  # Position of the end-effector

    # Add debug line if we have a previous point
    if previous_ee_position is not None:
        p.addUserDebugLine(previous_ee_position, current_ee_position, [0, 1, 0], 2, 0)

    # Update previous position
    previous_ee_position = current_ee_position

# Keep simulation running
while True:
    p.stepSimulation()
    time.sleep(1./240)