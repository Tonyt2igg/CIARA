import pybullet as p 
import numpy as np
import pandas as pd
import time
import os
from scipy.interpolate import CubicSpline

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

# Define parameters
Z_LIFT = 0.14  # Lift height
DISTANCE_THRESHOLD = 0.5  # Threshold for lifting
SIM_STEPS_PER_MOVE = 5    # Simulation steps per move

# Initialize variables
first_waypoint = np.array(waypoints[0])
previous_position = first_waypoint[:3].copy()
current_orientation = p.getQuaternionFromEuler(first_waypoint[3:6])
remaining_waypoints = waypoints.tolist()

# Store IK solutions
ik_solutions_rad = []
ik_solutions_deg = []

first_waypoint_reached = False

def find_nearest_waypoint(current_pos, waypoints):
    distances = [np.linalg.norm(np.array(current_pos) - np.array(wp[:3])) for wp in waypoints]
    return waypoints.pop(np.argmin(distances))

def generate_spline_trajectory(start, end, num_points=10):
    t = np.linspace(0, 1, num_points)
    cs = CubicSpline([0, 1], np.vstack([start, end]), axis=0)
    return cs(t)

def move_to_position(target_pos, target_orient):
    joint_angles_rad = p.calculateInverseKinematics(
        robot_id, end_effector_link_index, target_pos, target_orient)
    joint_angles_rad = joint_angles_rad[:num_joints]  # Ensure correct number of joints

    if first_waypoint_reached:
        ik_solutions_rad.append(joint_angles_rad)
        ik_solutions_deg.append(np.degrees(joint_angles_rad))

    for i in range(num_joints):
        p.setJointMotorControl2(robot_id, i, p.POSITION_CONTROL, targetPosition=joint_angles_rad[i])
    
    for _ in range(SIM_STEPS_PER_MOVE):
        p.stepSimulation()
        time.sleep(1./960)

while remaining_waypoints:
    target_waypoint = find_nearest_waypoint(previous_position, remaining_waypoints)
    target_position = np.array(target_waypoint[:3])
    target_orientation = p.getQuaternionFromEuler(target_waypoint[3:6])
    
    distance = np.linalg.norm(previous_position - target_position)
    
    if distance > DISTANCE_THRESHOLD:
        lifted_pos = np.array([previous_position[0], previous_position[1], Z_LIFT])
        trajectory = generate_spline_trajectory(previous_position, lifted_pos)
        for pos in trajectory:
            move_to_position(pos.tolist(), current_orientation)

        horizontal_pos = np.array([target_position[0], target_position[1], Z_LIFT])
        trajectory = generate_spline_trajectory(lifted_pos, horizontal_pos)
        for pos in trajectory:
            move_to_position(pos.tolist(), target_orientation)
        
        trajectory = generate_spline_trajectory(horizontal_pos, target_position)
        for pos in trajectory:
            move_to_position(pos.tolist(), target_orientation)
    else:
        trajectory = generate_spline_trajectory(previous_position, target_position)
        for pos in trajectory:
            move_to_position(pos.tolist(), target_orientation)
    
    if not first_waypoint_reached:
        first_waypoint_reached = True
        ik_solutions_rad = []
        ik_solutions_deg = []

    if distance <= DISTANCE_THRESHOLD:
        p.addUserDebugLine(previous_position.tolist(), target_position.tolist(), [1,0,0], 2, 0)
    
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