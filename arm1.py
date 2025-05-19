import pybullet as p 
import numpy as np
import pandas as pd
import time
import os

# Initialize PyBullet
physicsClient = p.connect(p.GUI)
p.setGravity(0, 0, -9.81)

# Load URDF model
urdf_path = r'D:\Traiding model\project5\working\ciara4\urdf\ciara4.urdf'
robot_id = p.loadURDF(urdf_path, [0, 0, 0], useFixedBase=1)

# Load waypoints from CSV
waypoints_path = r'D:\ras_sh\waypoints_square.csv'
waypoints = pd.read_csv(waypoints_path).values

# Get the number of joints
num_joints = p.getNumJoints(robot_id)
end_effector_link_index = num_joints - 1

# Define parameters
Z_LIFT = 0.14  # Lift height
DISTANCE_THRESHOLD = 0.011  # Threshold for lifting
NUM_INTERMEDIATE_STEPS = 2  # Intermediate steps between waypoints
SIM_STEPS_PER_MOVE = 5      # Simulation steps per move

# Initialize variables with NumPy arrays
first_waypoint = np.array(waypoints[0])
previous_position = first_waypoint[:3].copy()
current_orientation = p.getQuaternionFromEuler(first_waypoint[3:6])
remaining_waypoints = waypoints.tolist()
ik_solutions_rad = []
ik_solutions_deg = []

def find_nearest_waypoint(current_pos, waypoints):
    current_pos = np.array(current_pos)
    distances = [np.linalg.norm(current_pos - np.array(wp[:3])) for wp in waypoints]
    return waypoints.pop(np.argmin(distances))

def interpolate_positions(start, end, num_steps):
    start_arr = np.array(start)
    end_arr = np.array(end)
    return [start_arr + (end_arr - start_arr) * i/(num_steps+1) for i in range(1, num_steps+1)]

def move_to_position(target_pos, target_orient, is_lift=False):
    joint_angles_rad = p.calculateInverseKinematics(
        robot_id, end_effector_link_index, target_pos, target_orient)
    
    # Save IK solutions
    ik_solutions_rad.append(joint_angles_rad[:num_joints])
    ik_solutions_deg.append(np.degrees(joint_angles_rad[:num_joints]))
    
    # Move the robot
    for i in range(num_joints):
        p.setJointMotorControl2(robot_id, i, p.POSITION_CONTROL,
                              targetPosition=joint_angles_rad[i])
    for _ in range(SIM_STEPS_PER_MOVE):
        p.stepSimulation()
        time.sleep(1./960)

while remaining_waypoints:
    target_waypoint = find_nearest_waypoint(previous_position, remaining_waypoints)
    target_position = np.array(target_waypoint[:3])
    target_orientation = p.getQuaternionFromEuler(target_waypoint[3:6])
    distance = np.linalg.norm(previous_position - target_position)
    
    if distance > DISTANCE_THRESHOLD:
        # Lift phase
        lifted_pos = np.array([previous_position[0], previous_position[1], Z_LIFT])
        for interp_pos in interpolate_positions(previous_position, lifted_pos, NUM_INTERMEDIATE_STEPS):
            move_to_position(interp_pos.tolist(), current_orientation, is_lift=True)

        # Horizontal move phase
        start_horizontal = lifted_pos
        end_horizontal = np.array([target_position[0], target_position[1], Z_LIFT])
        for interp_pos in interpolate_positions(start_horizontal, end_horizontal, NUM_INTERMEDIATE_STEPS):
            move_to_position(interp_pos.tolist(), target_orientation)

        # Lower phase
        start_lower = end_horizontal
        for interp_pos in interpolate_positions(start_lower, target_position, NUM_INTERMEDIATE_STEPS):
            move_to_position(interp_pos.tolist(), target_orientation)
                
        current_orientation = target_orientation
    else:
        # Direct move with interpolation
        for interp_pos in interpolate_positions(previous_position, target_position, NUM_INTERMEDIATE_STEPS):
            move_to_position(interp_pos.tolist(), target_orientation)
                
        current_orientation = target_orientation

    # Draw a line to visualize the path (skip if lifted)
    if distance <= DISTANCE_THRESHOLD:
        p.addUserDebugLine(previous_position.tolist(), target_position.tolist(), [1,0,0], 2, 0)
    previous_position = target_position.copy()

# Save results
output_dir = r'D:\ras_sh\sav_vs'
os.makedirs(output_dir, exist_ok=True)

pd.DataFrame(ik_solutions_rad, columns=[f'Joint_{i+1}' for i in range(num_joints)]
            ).to_csv(os.path.join(output_dir, 'ik_solved_rad.csv'), index=False)
pd.DataFrame(ik_solutions_deg, columns=[f'Joint_{i+1}' for i in range(num_joints)]
            ).to_csv(os.path.join(output_dir, 'ik_solved_deg.csv'), index=False)

p.disconnect()