import numpy as np
import csv
import time
from math import cos, sin, atan2, sqrt, acos, degrees, radians
from adafruit_servokit import ServoKit

class ArmController:
    def __init__(self):
        # DH Parameters (modify these based on your arm configuration)
        self.dh_params = [
            {'theta': 0, 'd': 0.04, 'a': 0, 'alpha': 0},
            {'theta': 0, 'd': 0, 'a': 0.083609, 'alpha': 1.5708},
            {'theta': 0, 'd': 0, 'a': 0.16195, 'alpha': 3.1416},
            {'theta': 0, 'd': 0, 'a': 0.0013557, 'alpha': -3.1416}
        ]
        
        # Servo control setup
        self.kit = ServoKit(channels=16, address=0x40)
        self.SERVO_CHANNELS = [0, 3, 6, 9]
        self.SERVO_SPEED = 100
        self.INTERPOLATION_STEPS = 200
        self.UPDATE_INTERVAL = 0.005
        self.INITIAL_MOVE_DURATION = 2.0

    def inverse_kinematics(self, target_pos):
        """Calculate joint angles for given target position (x, y, z)"""
        x, y, z = target_pos
        angles = [0.0] * 4
        
        # Joint 1 calculation (base rotation)
        angles[0] = atan2(y, x)
        
        # Project position to arm plane
        r = sqrt(x**2 + y**2)
        z_adj = z - self.dh_params[0]['d']
        
        # Joint 2 and 3 calculations (shoulder and elbow)
        a2 = self.dh_params[1]['a']
        a3 = self.dh_params[2]['a']
        
        # Law of cosines for planar arm
        D = (r**2 + z_adj**2 - a2**2 - a3**2) / (2 * a2 * a3)
        D = np.clip(D, -1.0, 1.0)
        
        angles[2] = atan2(sqrt(1 - D**2), D)
        angles[1] = atan2(z_adj, r) - atan2(a3 * sin(angles[2]), a2 + a3 * cos(angles[2]))
        
        # Calculate theta4 using geometric relationship
        theta2_deg = degrees(angles[1])
        theta3_deg = degrees(angles[2])
        theta5 = 180 - (90 + theta2_deg) - (180 - theta3_deg)
        angles[3] = radians(-(90 - theta5))
        
        return angles

    def move_servos_smoothly(self, target_angles, calibration_data):
        """Interpolate between current and target angles smoothly"""
        current_angles = [self.kit.servo[ch].angle for ch in self.SERVO_CHANNELS]
        
        for step in np.linspace(0, 1, self.INTERPOLATION_STEPS):
            interp_angles = [
                current + (target - current) * step
                for current, target in zip(current_angles, target_angles)
            ]
            
            for ch, angle in zip(self.SERVO_CHANNELS, interp_angles):
                pulse = self.angle_to_pulse_ticks(angle, calibration_data[ch])
                self.kit.servo[ch].angle = pulse
                
            time.sleep(self.UPDATE_INTERVAL)

    def execute_trajectory(self, csv_path, calibration_data):
        """Read waypoints from CSV and execute trajectory"""
        with open(csv_path, 'r') as file:
            reader = csv.reader(file)
            waypoints = [list(map(float, row)) for row in reader]

        previous_angles = None
        for wp in waypoints:
            target_pos = wp[:3]  # x, y, z
            target_angles = self.inverse_kinematics(target_pos)
            
            if previous_angles is None:
                # Initial move with slower speed
                self.move_servos_smoothly(target_angles, calibration_data)
            else:
                # Normal speed movement
                self.move_servos_smoothly(target_angles, calibration_data)
            
            previous_angles = target_angles

    @staticmethod
    def angle_to_pulse_ticks(angle, calibration):
        """Convert angle to PWM ticks using calibration data"""
        min_angle, max_angle = calibration[0][0], calibration[-1][0]
        angle = max(min(angle, max_angle), min_angle)
        
        for i in range(len(calibration) - 1):
            lower_angle, lower_ticks = calibration[i]
            upper_angle, upper_ticks = calibration[i + 1]
            if lower_angle <= angle <= upper_angle:
                ratio = (angle - lower_angle) / (upper_angle - lower_angle)
                return int(round(lower_ticks + ratio * (upper_ticks - lower_ticks)))
        
        return int(round(calibration[-1][1]))

# Usage example
if __name__ == "__main__":
    controller = ArmController()
    
    # Load calibration data (replace with your actual calibration)
    calibration_data = [
        # Format: [(-angle, pulse), ...] for each servo
        [],  # Servo 0 calibration
        [],  # Servo 1 calibration
        [],  # Servo 2 calibration
        []   # Servo 3 calibration
    ]
    
    # Execute trajectory
    controller.execute_trajectory("/home/ciara/New/square_1.csv", calibration_data)