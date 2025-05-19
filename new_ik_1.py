import pybullet as p 
import numpy as np
import pandas as pd
import time
import os

# Initialize PyBullet
physicsClient = p.connect(p.GUI)
p.setGravity(0, 0, -9.81)

# Allow time for the simulation to initialize
time.sleep(2)  # 2-second delay for initialization

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
Z_LIFT = 0.06  # Lift height
DISTANCE_THRESHOLD = 0.011  # Threshold for lifting
NUM_INTERMEDIATE_STEPS = 10  # Intermediate steps between waypoints
SIM_STEPS_PER_MOVE = 5      # Simulation steps per move

# Get initial end-effector position and orientation
initial_state = p.getLinkState(robot_id, end_effector_link_index)
initial_position = np.array(initial_state[0])
fixed_orientation = initial_state[1]  # Use the initial orientation or set from first waypoint if needed

# Adjust fixed_orientation based on first waypoint's orientation (if provided in CSV)
if waypoints.size > 0:
    first_waypoint_euler = waypoints[0][3:6]
    fixed_orientation = p.getQuaternionFromEuler(first_waypoint_euler)

# Store IK solutions
ik_solutions_rad = []
ik_solutions_deg = []

def interpolate_positions(start, end, num_steps):
    """Generate intermediate positions between start and end, including the end position."""
    if num_steps <= 0:
        return []
    start_arr = np.array(start)
    end_arr = np.array(end)
    step = (end_arr - start_arr) / num_steps
    return [start_arr + step * i for i in range(1, num_steps + 1)]

def move_to_position(target_pos):
    """Move the robot to a target position using inverse kinematics with fixed orientation."""
    # Allow time for the solver to compute IK
    time.sleep(0.1)  # 100ms delay for solver stability

    joint_angles_rad = p.calculateInverseKinematics(
        robot_id, end_effector_link_index, target_pos, fixed_orientation)
    joint_angles_rad = joint_angles_rad[:num_joints]  # Ensure correct number of joints

    # Save IK solutions
    ik_solutions_rad.append(joint_angles_rad)
    ik_solutions_deg.append(np.degrees(joint_angles_rad))

    # Move the robot
    for i in range(num_joints):
        p.setJointMotorControl2(robot_id, i, p.POSITION_CONTROL,
                              targetPosition=joint_angles_rad[i])
    for _ in range(SIM_STEPS_PER_MOVE):
        p.stepSimulation()
        time.sleep(1./960)

# Initialize previous position to the robot's initial end-effector position
previous_position = initial_position.copy()

# Allow time for the robot to stabilize at the initial position
time.sleep(1)  # 1-second delay for stabilization

# Process each waypoint in order
for target_waypoint in waypoints:
    target_position = np.array(target_waypoint[:3])
    distance = np.linalg.norm(previous_position - target_position)

    if distance > DISTANCE_THRESHOLD:
        # Lift phase
        lifted_pos = np.array([previous_position[0], previous_position[1], Z_LIFT])
        for interp_pos in interpolate_positions(previous_position, lifted_pos, NUM_INTERMEDIATE_STEPS):
            move_to_position(interp_pos)
        previous_position = lifted_pos.copy()

        # Horizontal move phase
        end_horizontal = np.array([target_position[0], target_position[1], Z_LIFT])
        for interp_pos in interpolate_positions(lifted_pos, end_horizontal, NUM_INTERMEDIATE_STEPS):
            move_to_position(interp_pos)
        previous_position = end_horizontal.copy()

        # Lower phase
        for interp_pos in interpolate_positions(end_horizontal, target_position, NUM_INTERMEDIATE_STEPS):
            move_to_position(interp_pos)
        previous_position = target_position.copy()
    else:
        # Direct move with interpolation
        for interp_pos in interpolate_positions(previous_position, target_position, NUM_INTERMEDIATE_STEPS):
            move_to_position(interp_pos)
        previous_position = target_position.copy()

    # Draw a line to visualize the path
    p.addUserDebugLine(previous_position.tolist(), target_position.tolist(), [1,0,0], 2, 0)

# Save results
output_dir = r'D:\ras_sh\sav_vs'
os.makedirs(output_dir, exist_ok=True)

if ik_solutions_rad:
    pd.DataFrame(ik_solutions_rad, columns=[f'Joint_{i+1}' for i in range(num_joints)]
                ).to_csv(os.path.join(output_dir, 'ik_solved_rad.csv'), index=False)
if ik_solutions_deg:
    pd.DataFrame(ik_solutions_deg, columns=[f'Joint_{i+1}' for i in range(num_joints)]
                ).to_csv(os.path.join(output_dir, 'ik_solved_deg.csv'), index=False)

p.disconnect()