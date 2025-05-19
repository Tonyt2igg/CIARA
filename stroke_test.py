import cv2
import numpy as np

# 📂 Path to the CSV file containing waypoints
csv_path = r"D:\CIARA\1csv_transfer\CSV\vscode_user\square_1_waypoints.csv"

# 📥 Load waypoints from CSV
waypoints = np.loadtxt(csv_path, delimiter=",", skiprows=1, usecols=(0, 1))


# Create a blank white image
img_size = 500
img = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255

# Scale waypoints to fit in the image
min_x, min_y = waypoints.min(axis=0)
max_x, max_y = waypoints.max(axis=0)

scale_x = (img_size - 40) / (max_x - min_x)  # Add margin
scale_y = (img_size - 40) / (max_y - min_y)

waypoints[:, 0] = (waypoints[:, 0] - min_x) * scale_x + 20  # Centering
waypoints[:, 1] = (waypoints[:, 1] - min_y) * scale_y + 20

# Convert to integer
waypoints = waypoints.astype(int)

# 🎨 Draw only the stroke (connecting lines) without marking waypoints
for i in range(len(waypoints) - 1):
    cv2.line(img, tuple(waypoints[i]), tuple(waypoints[i + 1]), (0, 0, 0), 2)

# Show and save result
cv2.imshow("Stroke Path", img)
cv2.imwrite(r"D:\ras_sh\stroke\stroke_path.jpg", img)

cv2.waitKey(0)
cv2.destroyAllWindows()
