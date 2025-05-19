import cv2
import numpy as np

# Read the already skeletonized image
image_path = r"D:\CIARA\1csv_transfer\CSV\vscode_custom\custom_drawing.png"
img = cv2.imread(image_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Ensure image is binary (pure black & white)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# Invert if needed (if background is white)
if np.sum(binary == 255) > np.sum(binary == 0):
    binary = cv2.bitwise_not(binary)

# Apply Morphological Closing to Fill Small Gaps in Lines
kernel = np.ones((3, 3), np.uint8)
binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

# Extract contours using RETR_TREE for inner and outer contour hierarchy
contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Create blank canvases
reconstructed = np.ones_like(img) * 255
waypoint_image = np.ones_like(img) * 255

# Define HSV color transition settings
num_strokes = 30  # Estimated total strokes
hue_shift_per_stroke = 120 // num_strokes  # Fast transition from Red → Blue
hue_value = 0  # Start with Red (HSV = 0)

waypoints = []  # Store waypoint coordinates

first_stroke = True
last_point = None  # Track last point for final red dot

for contour in contours:
    if len(contour) < 2:
        continue  # Skip small contours

    # Approximate contour to reduce noise and simplify path
    contour = cv2.approxPolyDP(contour, epsilon=0.5, closed=False)

    # Compute mean distance between consecutive points
    distances = [
        np.linalg.norm(contour[i][0] - contour[i + 1][0])
        for i in range(len(contour) - 1)
    ]
    mean_dist = np.mean(distances) if distances else 0
    gap_threshold = mean_dist * 4  # Threshold for new stroke

    # Convert HSV to BGR
    hsv_color = np.array([hue_value, 255, 255])
    color = cv2.cvtColor(np.uint8([[hsv_color]]), cv2.COLOR_HSV2BGR)[0][0].tolist()

    prev_x, prev_y = contour[0][0]

    if first_stroke:
        # Mark the start of the FIRST stroke with a black dot
        cv2.circle(reconstructed, (prev_x, prev_y), 3, (0, 0, 0), -1)
        waypoints.append((prev_x, prev_y))  # Store first waypoint
        first_stroke = False

    for i in range(1, len(contour)):
        x, y = contour[i][0]
        dist = np.linalg.norm([x - prev_x, y - prev_y])

        # If distance exceeds threshold, start a new stroke
        if dist > gap_threshold:
            hue_value = min(hue_value + hue_shift_per_stroke, 120)  # Increase hue towards blue
            hsv_color = np.array([hue_value, 255, 255])
            color = cv2.cvtColor(np.uint8([[hsv_color]]), cv2.COLOR_HSV2BGR)[0][0].tolist()

        # Draw line segment
        cv2.line(reconstructed, (prev_x, prev_y), (x, y), color, 1)

        # Mark waypoints along the stroke path
        cv2.circle(waypoint_image, (x, y), 1, (0, 0, 255), -1)
        waypoints.append((x, y))  # Store waypoints

        prev_x, prev_y = x, y  # Update previous point
        last_point = (x, y)  # Track last point for final red dot

# Handle Remaining Gaps: Connect nearby contours based on proximity
for i, contour in enumerate(contours):
    for j, contour2 in enumerate(contours):
        if i != j:
            x1, y1 = contour[-1][0]
            x2, y2 = contour2[0][0]
            distance = np.linalg.norm([x2 - x1, y2 - y1])
            if distance < 20:  # Threshold for connecting contours
                cv2.line(reconstructed, (x1, y1), (x2, y2), (0, 255, 0), 1)
                waypoints.append((x1, y1))
                waypoints.append((x2, y2))

# Mark the END of the LAST stroke with a red dot
if last_point:
    cv2.circle(reconstructed, last_point, 3, (0, 0, 255), -1)
    waypoints.append(last_point)  # Store last waypoint

# Normalize and Resize Waypoints to 18cm x 18cm
waypoints = np.array(waypoints, dtype=np.float32)
min_x, min_y = waypoints.min(axis=0)
max_x, max_y = waypoints.max(axis=0)

scale_x = 0.15 / (max_x - min_x)  # Scaling factor to fit in 18cm
scale_y = 0.15 / (max_y - min_y)

waypoints[:, 0] = (waypoints[:, 0] - min_x) * scale_x
waypoints[:, 1] = (waypoints[:, 1] - min_y) * scale_y

# Apply X-offset of -0.08 and Y-offset of 0.13
waypoints[:, 0] += -0.08  # Shift X-coordinates left
waypoints[:, 1] += 0.14   # Shift Y-coordinates up

# Add fixed values for Z, Roll, Pitch, and Yaw
z_value = 0.06
roll, pitch, yaw = 0, 0, -45

waypoints_extended = np.column_stack((waypoints, np.full((waypoints.shape[0], 1), z_value),
                                      np.full((waypoints.shape[0], 1), roll),
                                      np.full((waypoints.shape[0], 1), pitch),
                                      np.full((waypoints.shape[0], 1), yaw)))

# Save waypoints as CSV at "D:\ras_sh\stroke"
csv_path = r"D:\CIARA\1csv_transfer\CSV\vscode_custom\waypoints.csv"
np.savetxt(csv_path, waypoints_extended, delimiter=",", comments="", fmt="%.6f")

# Show images
cv2.imshow('Waypoints Detected', waypoint_image)
cv2.imshow('Reconstructed Drawing', reconstructed)

# Save results
cv2.imwrite(r"D:\CIARA\1csv_transfer\CSV\vs_code\waypoints_detected.jpg", waypoint_image)
cv2.imwrite(r"D:\CIARA\1csv_transfer\CSV\vs_code\reconstructed_drawing.jpg", reconstructed)

cv2.waitKey(0)
cv2.destroyAllWindows()

print(f"Waypoints saved to {csv_path}")
