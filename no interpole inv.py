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
robot_id = p.loadURDF(urdf_path, [0, 0, 0], useFixedBase=1)

# Load waypoints from CSV
waypoints_path = r'D:\ras_sh\waypoints_square.csv'
waypoints = pd.read_csv(waypoints_path).values

# Get the number of joints
num_joints = p.getNumJoints(robot_id)
end_effector_link_index = num_joints - 1

# Initialize variables
previous_position = np.array(waypoints[0][:3])
current_orientation = p.getQuaternionFromEuler(waypoints[0][3:6])
remaining_waypoints = waypoints.tolist()

# Store IK solutions
ik_solutions_rad = []
ik_solutions_deg = []

first_waypoint_reached = False


def move_to_position(target_pos, target_orient):
    joint_angles_rad = p.calculateInverseKinematics(
        robot_id, end_effector_link_index, target_pos, target_orient)
    joint_angles_rad = joint_angles_rad[:num_joints]  # Ensure correct number of joints

    if first_waypoint_reached:
        ik_solutions_rad.append(joint_angles_rad)
        ik_solutions_deg.append(np.degrees(joint_angles_rad))

    for i in range(num_joints):
        p.setJointMotorControl2(robot_id, i, p.POSITION_CONTROL, targetPosition=joint_angles_rad[i])
    
    for _ in range(5):  # Small simulation steps to allow movement
        p.stepSimulation()
        time.sleep(1./960)

# Move through waypoints
for waypoint in remaining_waypoints:
    target_position = np.array(waypoint[:3])
    target_orientation = p.getQuaternionFromEuler(waypoint[3:6])
    
    move_to_position(target_position, target_orientation)
    
    if not first_waypoint_reached:
        first_waypoint_reached = True
        ik_solutions_rad = []
        ik_solutions_deg = []
    
    p.addUserDebugLine(previous_position.tolist(), target_position.tolist(), [1, 0, 0], 2, 0)
    previous_position = target_position.copy()

# Save results
output_dir = r'D:\ras_sh\sav_vs'
os.makedirs(output_dir, exist_ok=True)

if ik_solutions_rad:
    pd.DataFrame(np.array(ik_solutions_rad), columns=[f'Joint_{i+1}' for i in range(num_joints)]
                ).to_csv(os.path.join(output_dir, 'ik_solved_rad.csv'), index=False)
if ik_solutions_deg:
    pd.DataFrame(np.array(ik_solutions_deg), columns=[f'Joint_{i+1}' for i in range(num_joints)]
                ).to_csv(os.path.join(output_dir, 'ik_solved_deg.csv'), index=False)

p.disconnect()