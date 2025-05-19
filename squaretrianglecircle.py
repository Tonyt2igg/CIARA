import numpy as np
import csv

def generate_square(x_offset, y_offset, size, total_waypoints, z, yaw):
    corners = [
        (x_offset, y_offset),
        (x_offset + size, y_offset),
        (x_offset + size, y_offset + size),
        (x_offset, y_offset + size),
        (x_offset, y_offset)  # Closing the loop
    ]
    return interpolate_waypoints(corners, total_waypoints, z, yaw)

def generate_rectangle(x_offset, y_offset, width, height, total_waypoints, z, yaw):
    corners = [
        (x_offset, y_offset),
        (x_offset + width, y_offset),
        (x_offset + width, y_offset + height),
        (x_offset, y_offset + height),
        (x_offset, y_offset)
    ]
    return interpolate_waypoints(corners, total_waypoints, z, yaw)

def generate_circle(x_offset, y_offset, radius, total_waypoints, z, yaw):
    angles = np.linspace(0, 2 * np.pi, total_waypoints)
    waypoints = [(x_offset + radius * np.cos(a), y_offset + radius * np.sin(a), z, 0, 0, yaw) for a in angles]
    return waypoints

def generate_triangle(x_offset, y_offset, size, total_waypoints, z, yaw):
    corners = [
        (x_offset, y_offset),
        (x_offset + size, y_offset),
        (x_offset + size / 2, y_offset + np.sqrt(3) / 2 * size),
        (x_offset, y_offset)  # Closing the loop
    ]
    return interpolate_waypoints(corners, total_waypoints, z, yaw)

def interpolate_waypoints(waypoints, total_waypoints, z, yaw):
    interpolated_points = []
    num_interpolated = total_waypoints // (len(waypoints) - 1)
    for i in range(len(waypoints) - 1):
        x_vals = np.linspace(waypoints[i][0], waypoints[i + 1][0], num_interpolated)
        y_vals = np.linspace(waypoints[i][1], waypoints[i + 1][1], num_interpolated)
        interpolated_points.extend((x, y, z, 0, 0, yaw) for x, y in zip(x_vals, y_vals))
    return interpolated_points

def save_to_csv(filename, waypoints):
    path = "D:/CIARA/1csv_transfer/CSV/vscode_user/" + filename
    with open(path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(waypoints)

# User input
shape = input("Enter shape (square, rectangle, circle, triangle): ").strip().lower()
x_offset = float(input("Enter X offset: "))
y_offset = float(input("Enter Y offset: "))
z = float(input("Enter Z value: "))
yaw = float(input("Enter Yaw value: "))
total_waypoints = 300

if shape == "square":
    size = float(input("Enter size of square: "))
    waypoints = generate_square(x_offset, y_offset, size, total_waypoints, z, yaw)
    save_to_csv("square_waypoints.csv", waypoints)

elif shape == "rectangle":
    width = float(input("Enter width of rectangle: "))
    height = float(input("Enter height of rectangle: "))
    waypoints = generate_rectangle(x_offset, y_offset, width, height, total_waypoints, z, yaw)
    save_to_csv("rectangle_waypoints.csv", waypoints)

elif shape == "circle":
    radius = float(input("Enter radius of circle: "))
    waypoints = generate_circle(x_offset, y_offset, radius, total_waypoints, z, yaw)
    save_to_csv("circle_waypoints.csv", waypoints)

elif shape == "triangle":
    size = float(input("Enter size of triangle: "))
    waypoints = generate_triangle(x_offset, y_offset, size, total_waypoints, z, yaw)
    save_to_csv("triangle_waypoints.csv", waypoints)

else:
    print("Invalid shape entered.")