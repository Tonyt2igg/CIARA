import csv
import numpy as np
import os

# Define save path
save_path = r"D:\ras_sh\waypoints_square.csv"

# Define fixed Z value
fixed_z = 0.04

# Define perfect square properties
square_size = 0.1  # Side length of the square (10 cm)
start_x, start_y = -0.05, 0.15  # Bottom-left corner of the square

# Define perfect square corners
square_corners = [
    (start_x, start_y),  # A (Bottom-left)
    (start_x + square_size, start_y),  # B (Bottom-right)
    (start_x + square_size, start_y + square_size),  # C (Top-right)
    (start_x, start_y + square_size),  # D (Top-left)
    (start_x, start_y)  # Closing the loop back to A
]

# Step size for waypoints (0.5 cm = 0.005 m)
step_size = 0.005

# Function to generate waypoints along a line
def interpolate_waypoints(start, end, step):
    x_start, y_start = start
    x_end, y_end = end
    distance = np.hypot(x_end - x_start, y_end - y_start)
    num_steps = max(1, int(distance / step))  # Avoid zero division
    return [(round(x, 5), round(y, 5), fixed_z, 0, 0,-45) 
            for x, y in zip(np.linspace(x_start, x_end, num_steps + 1), np.linspace(y_start, y_end, num_steps + 1))]

# Generate waypoints for the square
waypoints = []
for i in range(len(square_corners) - 1):
    waypoints.extend(interpolate_waypoints(square_corners[i], square_corners[i+1], step_size))

# Ensure directory exists
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Save waypoints to CSV
with open(save_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(waypoints)

print(f"Perfect square CSV file saved successfully at: {save_path}")
