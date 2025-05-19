import pybullet as p
import numpy as np
import pandas as pd
import time

# Initialize PyBullet
physicsClient = p.connect(p.GUI)  # or p.DIRECT for non-graphical version
p.setGravity(0, 0, -9.81)

# Load URDF model
urdf_path = r'D:\Traiding model\project5\working\ciara4\urdf\ciara4.urdf'
robot_id = p.loadURDF(urdf_path, [0, 0, 0], useFixedBase=1)

# Load waypoints from CSV
waypoints_path = r'D:\ras_sh\waypointss.csv'
waypoints = pd.read_csv(waypoints_path).values

# Get the number of joints
num_joints = p.getNumJoints(robot_id)

# Assuming the end effector is the last link
end_effector_link_index = num_joints - 1

# Set the initial position and orientation
initial_position = [0, 0, 0]
initial_orientation = p.getQuaternionFromEuler([0, 0, 0])

# Initialize variables for tracing
previous_position = None  # Stores the previous position of the end effector

# Main loop to move through waypoints
for waypoint in waypoints:
    target_position = waypoint[:3]
    target_orientation = p.getQuaternionFromEuler(waypoint[3:6])
    
    # Compute IK
    joint_angles = p.calculateInverseKinematics(
        robot_id, 
        end_effector_link_index, 
        target_position, 
        target_orientation
    )
    
    # Set joint positions
    for i in range(num_joints):
        p.setJointMotorControl2(
            robot_id, 
            i, 
            p.POSITION_CONTROL, 
            targetPosition=joint_angles[i]
        )
    
    # Step simulation
    for _ in range(100):
        p.stepSimulation()
        time.sleep(1./240.)
    
    # Get the current position of the end effector
    end_effector_state = p.getLinkState(robot_id, end_effector_link_index)
    current_position = end_effector_state[0]  # Position of the end effector
    
    # Draw a line from the previous position to the current position
    if previous_position is not None:
        # Draw a new line without removing the previous one
        p.addUserDebugLine(previous_position, current_position, lineColorRGB=[1, 0, 0], lineWidth=2)
    
    # Update the previous position
    previous_position = current_position
    
    # Optionally, add a delay to visualize the movement
    time.sleep(1)

# Disconnect from PyBullet
p.disconnect()