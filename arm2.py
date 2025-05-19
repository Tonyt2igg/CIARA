import pybullet as p
import numpy as np
import pandas as pd
import time

# Initialize PyBullet
physicsClient = p.connect(p.GUI)
p.setGravity(0, 0, -9.81)

# Load robot model
urdf_path = r'D:\Traiding model\project5\working\ciara4\urdf\ciara4.urdf'
robot_id = p.loadURDF(urdf_path, [0, 0, 0], useFixedBase=1)

# Load waypoints
waypoints_path = r'D:\ras_sh\waypointss.csv'
waypoints = pd.read_csv(waypoints_path).values.tolist()

# Robot parameters
num_joints = p.getNumJoints(robot_id)
end_effector_idx = num_joints - 1
lift_height = 0.13  # 13 cm lift
distance_threshold = 0.316  # 31.6 cm threshold

def move_to_target(target_pos, target_orn, draw_line=True):
    # Calculate IK and move
    joint_angles = p.calculateInverseKinematics(robot_id, end_effector_idx, target_pos, target_orn)
    for i in range(num_joints):
        p.setJointMotorControl2(robot_id, i, p.POSITION_CONTROL, targetPosition=joint_angles[i])
    
    # Simulate movement
    current_pos = None
    for _ in range(40):
        p.stepSimulation()
        time.sleep(1/500.)
        current_pos = p.getLinkState(robot_id, end_effector_idx)[0]
    
    return current_pos

# Initial setup
current_pos = p.getLinkState(robot_id, end_effector_idx)[0]
previous_pos = current_pos
remaining_waypoints = waypoints

while remaining_waypoints:
    # Find nearest waypoint using XY distance
    distances = [np.linalg.norm(np.array(current_pos[:2]) - np.array(w[:2])) for w in remaining_waypoints]
    nearest_idx = np.argmin(distances)
    target_waypoint = remaining_waypoints.pop(nearest_idx)
    
    target_pos = target_waypoint[:3]
    target_orn = p.getQuaternionFromEuler(target_waypoint[3:6])
    xy_distance = np.linalg.norm(np.array(current_pos[:2]) - target_pos[:2])

    if xy_distance > distance_threshold:
        # Lift pen and move
        lifted_pos = [current_pos[0], current_pos[1], current_pos[2] + lift_height]
        current_pos = move_to_target(lifted_pos, target_orn, False)
        
        # Move to lifted position above target
        lifted_target = [target_pos[0], target_pos[1], target_pos[2] + lift_height]
        current_pos = move_to_target(lifted_target, target_orn, False)
        
        # Lower pen
        current_pos = move_to_target(target_pos, target_orn, False)
        previous_pos = None  # Reset drawing history
    else:
        # Normal move with drawing
        current_pos = move_to_target(target_pos, target_orn)
        if previous_pos is not None:
            p.addUserDebugLine(previous_pos, current_pos, lineColorRGB=[1,0,0], lineWidth=2)
        previous_pos = current_pos

p.disconnect()