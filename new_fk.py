import pybullet as p
import numpy as np
import pandas as pd
import time

# Initialize PyBullet
physicsClient = p.connect(p.GUI)
p.setGravity(0, 0, -9.81)
p.setTimeStep(1./240)  # Ensure simulation step consistency

# Load URDF model
urdf_path = r'D:\Traiding model\project5\working\ciara4\urdf\ciara4.urdf'
robot_id = p.loadURDF(urdf_path, [0, 0, 0], useFixedBase=1)

# Get end-effector link index (must match IK code)
num_joints = p.getNumJoints(robot_id)
end_effector_link_index = num_joints - 1  # Verify with URDF

# Load IK solutions in degrees
ik_solutions_path = r'D:\ras_sh\sav_vs\ik_solved_deg.csv'
ik_solutions_deg = pd.read_csv(ik_solutions_path).values

# Convert degrees to radians for PyBullet
ik_solutions_rad = np.radians(ik_solutions_deg)

# Simulation parameters
SIM_STEPS_PER_MOVE = 5
previous_ee_position = None

for joint_angles in ik_solutions_rad:
    for i in range(len(joint_angles)):
        p.setJointMotorControl2(robot_id, i, p.POSITION_CONTROL, targetPosition=joint_angles[i])
    
    for _ in range(SIM_STEPS_PER_MOVE):
        p.stepSimulation()
        time.sleep(1./960)
    
    ee_state = p.getLinkState(robot_id, end_effector_link_index)
    current_ee_position = ee_state[0]

    if previous_ee_position is not None:
        p.addUserDebugLine(previous_ee_position, current_ee_position, [0, 1, 0], 2, 0)
    
    previous_ee_position = current_ee_position

# Final validation: Check if FK matches last waypoint
waypoints_path = r'D:\ras_sh\waypointss.csv'
waypoints = pd.read_csv(waypoints_path).values

ee_final_state = p.getLinkState(robot_id, end_effector_link_index)
print(f"Final EE Position: {ee_final_state[0]}")
print(f"Expected Position: {waypoints[-1][:3]}")

# Keep simulation open
while True:
    p.stepSimulation()
    time.sleep(1./240)