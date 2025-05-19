import pybullet as p
import pybullet_data
import numpy as np
import csv
import time
import math

# Configuration
URDF_PATH = r"D:\Traiding model\project5\CIARAFNL\CIARAFNL\urdf\CIARAFNL.urdf"
SAVE_PATH = r"D:\ras_sh\sav_vs\joint_angles.csv"
FIXED_ORIENTATION = [0, math.pi/2, 0]  # Pen points downward (adjust if needed)

def load_robot(urdf_path):
    p.connect(p.GUI)
    p.setGravity(0, 0, -9.8)
    robot = p.loadURDF(urdf_path, [0, 0, 0], useFixedBase=True)
    return robot

def get_joint_info(robot):
    joint_indices = []
    joint_names = []
    num_joints = p.getNumJoints(robot)
    
    for i in range(num_joints):
        info = p.getJointInfo(robot, i)
        joint_name = info[1].decode('utf-8')
        joint_type = info[2]
        
        if joint_name.startswith("joint_") and joint_type != p.JOINT_FIXED:
            joint_number = int(joint_name.split("_")[1])
            if joint_number <= 4:  # Use first 4 joints
                joint_indices.append(i)
                joint_names.append(joint_name)
    
    # Find end effector link (child of joint_4)
    ee_link_index = None
    for i in range(num_joints):
        info = p.getJointInfo(robot, i)
        if info[1].decode('utf-8') == "joint_4":
            ee_link_index = info[4]
            break
    
    return joint_indices[:4], ee_link_index

def read_waypoints(filename):
    waypoints = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 3:
                waypoints.append([float(row[0]), float(row[1]), float(row[2])])
    return waypoints

def main():
    # Initialize simulation
    robot = load_robot(URDF_PATH)
    joint_indices, ee_link_index = get_joint_info(robot)
    
    # Disable joint_5 if present
    for i in range(p.getNumJoints(robot)):
        info = p.getJointInfo(robot, i)
        if info[1].decode('utf-8') == "joint_5":
            p.resetJointState(robot, i, 0)
            p.setJointMotorControl2(robot, i, p.POSITION_CONTROL, targetPosition=0, force=500)
    
    # Read waypoints
    waypoints = read_waypoints("D:\ras_sh\waypoints_square.csv")  # Replace with your CSV path
    
    # Store solved joint angles
    saved_angles = []
    
    # IK parameters
    ll = [-math.pi]*4  # Lower joint limits
    ul = [math.pi]*4   # Upper joint limits
    jr = [math.pi]*4   # Joint ranges
    
    for wp in waypoints:
        # Convert orientation to quaternion
        target_orn = p.getQuaternionFromEuler(FIXED_ORIENTATION)
        
        # Solve IK
        joint_angles = p.calculateInverseKinematics(
            robot,
            ee_link_index,
            wp,
            target_orn,
            lowerLimits=ll,
            upperLimits=ul,
            jointRanges=jr,
            restPoses=[0]*4,
            maxNumIterations=100
        )
        
        # Take first 4 joints (ignore any extra joints)
        joint_angles = joint_angles[:4]
        saved_angles.append(joint_angles)
        
        # Move robot to calculated position
        for i, angle in enumerate(joint_angles):
            p.setJointMotorControl2(robot, joint_indices[i], p.POSITION_CONTROL, targetPosition=angle)
        
        # Step simulation
        for _ in range(100):
            p.stepSimulation()
            time.sleep(1/240)
    
    # Save joint angles to CSV
    with open(SAVE_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(saved_angles)
    
    p.disconnect()

if __name__ == "__main__":
    main()