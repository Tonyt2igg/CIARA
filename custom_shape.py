import numpy as np
import csv

# Shape Generators
def generate_square(x_offset, y_offset, size, total_waypoints, z, yaw):
    corners = [
        (x_offset, y_offset),
        (x_offset + size, y_offset),
        (x_offset + size, y_offset + size),
        (x_offset, y_offset + size),
        (x_offset, y_offset)
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
    return [(x_offset + radius * np.cos(a), y_offset + radius * np.sin(a), z, 0, 0, yaw) for a in angles]

def generate_triangle(x_offset, y_offset, size, total_waypoints, z, yaw):
    corners = [
        (x_offset, y_offset),
        (x_offset + size, y_offset),
        (x_offset + size / 2, y_offset + np.sqrt(3) / 2 * size),
        (x_offset, y_offset)
    ]
    return interpolate_waypoints(corners, total_waypoints, z, yaw)

def generate_poland_flag(x_offset, y_offset, width, height, total_waypoints, z, yaw):
    flag_ratio = 0.8
    pole_ratio = 1 - flag_ratio
    flag_points = int(total_waypoints * flag_ratio)
    pole_points = total_waypoints - flag_points

    half = flag_points // 2
    white = generate_rectangle(x_offset, y_offset + height / 2, width, height / 2, half, z, yaw)
    red = generate_rectangle(x_offset, y_offset, width, height / 2, flag_points - half, z, yaw)

    pole_width = width * 0.05
    pole_height = height * 1.5
    pole_x = x_offset - pole_width
    pole_y = y_offset - (pole_height - height)

    pole = generate_rectangle(pole_x, pole_y, pole_width, pole_height, pole_points, z, yaw)

    return white + red + pole

def generate_3d_cube(x_offset, y_offset, size, total_waypoints, z, yaw):
    front = [
        (x_offset, y_offset),
        (x_offset + size, y_offset),
        (x_offset + size, y_offset + size),
        (x_offset, y_offset + size),
        (x_offset, y_offset)
    ]
    offset = size / 2
    back = [(x + offset, y + offset) for (x, y) in front]
    edges = []
    for i in range(4):
        edges += interpolate_waypoints([front[i], front[i+1]], total_waypoints // 12, z, yaw)
        edges += interpolate_waypoints([back[i], back[i+1]], total_waypoints // 12, z, yaw)
        edges += interpolate_waypoints([front[i], back[i]], total_waypoints // 12, z, yaw)
    return edges

def generate_heart(x_offset, y_offset, scale, total_waypoints, z, yaw):
    t = np.linspace(0, 2 * np.pi, total_waypoints)
    x = scale * 16 * np.sin(t)**3 + x_offset
    y = scale * (13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)) + y_offset
    return [(x[i], y[i], z, 0, 0, yaw) for i in range(total_waypoints)]

def generate_minecraft_creeper(x_offset, y_offset, size, total_waypoints, z, yaw):
    outer = generate_square(x_offset, y_offset, size, total_waypoints // 2, z, yaw)

    unit = size / 8
    black_blocks = [
        (1, 5), (2, 5), (5, 5), (6, 5),
        (3, 3), (4, 3),
        (2, 2), (3, 2), (4, 2), (5, 2),
        (2, 1), (5, 1)
    ]

    per = total_waypoints // (2 * len(black_blocks))
    inner = []
    for col, row in black_blocks:
        x = x_offset + col * unit
        y = y_offset + row * unit
        inner += generate_square(x, y, unit, per, z, yaw)

    return outer + inner

def generate_arrow(x_offset, y_offset, size, total_waypoints, z, yaw):
    shaft_thickness = size / 8     # thinner shaft
    head_length = size * 1.2       # longer head
    head_width = size * 0.8        # wider head base

    points = [
        (x_offset, y_offset + shaft_thickness / 2),
        (x_offset + size, y_offset + shaft_thickness / 2),
        (x_offset + size, y_offset + head_width / 2),
        (x_offset + size + head_length, y_offset),
        (x_offset + size, y_offset - head_width / 2),
        (x_offset + size, y_offset - shaft_thickness / 2),
        (x_offset, y_offset - shaft_thickness / 2),
        (x_offset, y_offset + shaft_thickness / 2)
    ]

    return interpolate_waypoints(points, total_waypoints, z, yaw)

def generate_letter(letter, x_offset, y_offset, size, total_waypoints, z, yaw):
    letters = {
        'A': [(0, 0), (0.5, 1), (1, 0), (0.25, 0.5), (0.75, 0.5)],
        'M': [(0, 0), (0, 1), (0.5, 0.5), (1, 1), (1, 0)],
        'N': [(0, 0), (0, 1), (1, 0), (1, 1)],
        'V': [(0, 1), (0.5, 0), (1, 1)],
        'W': [(0, 1), (0.25, 0), (0.5, 0.5), (0.75, 0), (1, 1)],
        'Z': [(0, 1), (1, 1), (0, 0), (1, 0)],
    }
    if letter.upper() not in letters:
        print("Unsupported letter.")
        return []
    scaled = [(x_offset + x * size, y_offset + y * size) for x, y in letters[letter.upper()]]
    return interpolate_waypoints(scaled, total_waypoints, z, yaw)

def generate_square_1(x_offset, y_offset, size, total_waypoints, z, yaw):
    # Main square
    main_square = [
        (x_offset, y_offset),
        (x_offset + size, y_offset),
        (x_offset + size, y_offset + size),
        (x_offset, y_offset + size),
        (x_offset, y_offset)
    ]
    
    # Second square connected at top-right vertex
    second_square = [
        (x_offset + size, y_offset + size),  # Connection point
        (x_offset + size * 2, y_offset + size),
        (x_offset + size * 2, y_offset + size * 2),
        (x_offset + size, y_offset + size * 2),
        (x_offset + size, y_offset + size)
    ]
    
    # Combine and interpolate
    combined = main_square + second_square
    return interpolate_waypoints(combined, total_waypoints, z, yaw)

def generate_square_2(x_offset, y_offset, size, total_waypoints, z, yaw):
    # First square
    square1 = [
        (x_offset, y_offset),
        (x_offset + size, y_offset),
        (x_offset + size, y_offset + size),
        (x_offset, y_offset + size),
        (x_offset, y_offset)
    ]
    
    # Second square connected at top-right vertex of first square
    square2 = [
        (x_offset + size, y_offset + size),  # Connection point
        (x_offset + size * 2, y_offset + size),
        (x_offset + size * 2, y_offset + size * 2),
        (x_offset + size, y_offset + size * 2),
        (x_offset + size, y_offset + size)
    ]
    
    # Third square connected at top-right vertex of second square
    square3 = [
        (x_offset + size * 2, y_offset + size * 2),  # Connection point
        (x_offset + size * 3, y_offset + size * 2),
        (x_offset + size * 3, y_offset + size * 3),
        (x_offset + size * 2, y_offset + size * 3),
        (x_offset + size * 2, y_offset + size * 2)
    ]
    
    # Combine and interpolate
    combined = square1 + square2 + square3
    return interpolate_waypoints(combined, total_waypoints, z, yaw)

# Utility
def interpolate_waypoints(points, total_waypoints, z, yaw):
    interpolated = []
    segments = len(points) - 1
    base = total_waypoints // segments
    rem = total_waypoints % segments
    for i in range(segments):
        count = base + (1 if i < rem else 0)
        xs = np.linspace(points[i][0], points[i+1][0], count, endpoint=False)
        ys = np.linspace(points[i][1], points[i+1][1], count, endpoint=False)
        interpolated += [(x, y, z, 0, 0, yaw) for x, y in zip(xs, ys)]
    interpolated.append((points[-1][0], points[-1][1], z, 0, 0, yaw))
    return interpolated

def save_to_csv(filename, waypoints):
    path = "D:/CIARA/1csv_transfer/CSV/vscode_user/" + filename
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(waypoints)

# ----------- USER INPUT -----------

shape = input("Enter shape (square, rectangle, circle, triangle, poland_flag, cube, heart, minecraft, arrow, letter, square_1, square_2): ").strip().lower()
x_offset = float(input("Enter X offset: "))
y_offset = float(input("Enter Y offset: "))
z = 0.06
yaw = -45
total_waypoints = 300

if shape == "square":
    size = float(input("Enter size: "))
    waypoints = generate_square(x_offset, y_offset, size, total_waypoints, z, yaw)
    save_to_csv("square_waypoints.csv", waypoints)

elif shape == "rectangle":
    width = float(input("Enter width: "))
    height = float(input("Enter height: "))
    waypoints = generate_rectangle(x_offset, y_offset, width, height, total_waypoints, z, yaw)
    save_to_csv("rectangle_waypoints.csv", waypoints)

elif shape == "circle":
    radius = float(input("Enter radius: "))
    waypoints = generate_circle(x_offset, y_offset, radius, total_waypoints, z, yaw)
    save_to_csv("circle_waypoints.csv", waypoints)

elif shape == "triangle":
    size = float(input("Enter size: "))
    waypoints = generate_triangle(x_offset, y_offset, size, total_waypoints, z, yaw)
    save_to_csv("triangle_waypoints.csv", waypoints)

elif shape == "poland_flag":
    width = float(input("Enter flag width: "))
    height = float(input("Enter flag height: "))
    waypoints = generate_poland_flag(x_offset, y_offset, width, height, total_waypoints, z, yaw)
    save_to_csv("poland_flag_waypoints.csv", waypoints)

elif shape == "cube":
    size = float(input("Enter cube size: "))
    waypoints = generate_3d_cube(x_offset, y_offset, size, total_waypoints, z, yaw)
    save_to_csv("cube_waypoints.csv", waypoints)

elif shape == "heart":
    scale = float(input("Enter heart scale: "))
    waypoints = generate_heart(x_offset, y_offset, scale, total_waypoints, z, yaw)
    save_to_csv("heart_waypoints.csv", waypoints)

elif shape == "minecraft":
    size = float(input("Enter size: "))
    waypoints = generate_minecraft_creeper(x_offset, y_offset, size, total_waypoints, z, yaw)
    save_to_csv("minecraft_creeper.csv", waypoints)

elif shape == "arrow":
    size = float(input("Enter size: "))
    waypoints = generate_arrow(x_offset, y_offset, size, total_waypoints, z, yaw)
    save_to_csv("arrow_waypoints.csv", waypoints)

elif shape == "letter":
    letter = input("Enter letter (A, M, N, V, W, Z): ").strip().upper()
    if letter not in ['A', 'M', 'N', 'V', 'W', 'Z']:
        print("Invalid letter entered.")
    else:
        size = float(input("Enter size: "))
        waypoints = generate_letter(letter, x_offset, y_offset, size, total_waypoints, z, yaw)
        save_to_csv(f"letter_{letter}_waypoints.csv", waypoints)

elif shape == "square_1":
    size = float(input("Enter size (for each square): "))
    waypoints = generate_square_1(x_offset, y_offset, size, total_waypoints, z, yaw)
    save_to_csv("square_1_waypoints.csv", waypoints)

elif shape == "square_2":
    size = float(input("Enter size (for each square): "))
    waypoints = generate_square_2(x_offset, y_offset, size, total_waypoints, z, yaw)
    save_to_csv("square_2_waypoints.csv", waypoints)

else:
    print("Invalid shape entered.")