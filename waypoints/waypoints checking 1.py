from skimage.morphology import skeletonize
import cv2
import numpy as np
import os
from sklearn.cluster import DBSCAN

# Input directory
input_dir = r"C:\projects\cyclegan\tech\Unpaired-Portrait-Drawing\results\pretrained\test_200\examples\temp_output\input_image_fake2.png"  # Directory with skeleton images

# Waypoint generation function
def generate_waypoints(line_points, interval=13):  # Reduced interval to 13
    """
    Generate waypoints for the robotic arm at regular intervals.
    :param line_points: Points that represent a sorted line.
    :param interval: The interval between waypoints.
    :return: A list of waypoints for the line.
    """
    waypoints = []
    for i in range(0, len(line_points), interval):
        waypoint = line_points[i]
        waypoints.append((int(waypoint[0]), int(waypoint[1])))  # Ensure integer coordinates
    return waypoints

# Check if input_dir is a directory
if not os.path.isdir(input_dir):
    print(f"The path {input_dir} is not a valid directory.")
else:
    # Process each skeleton image in the input directory
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)

        # Ensure the file is an image
        if os.path.isfile(file_path) and file_name.lower().endswith(('.png', '.jpg', '.jpeg')):  # Process image files
            # Load the skeleton image
            skeleton_image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if skeleton_image is None:
                print(f"Failed to load image: {file_path}")
                continue

            # Ensure black lines are treated correctly (invert if necessary)
            skeleton_image = cv2.bitwise_not(skeleton_image)  # Make black lines white for processing

            # Detect non-zero points in the skeletonized image
            non_zero_points = np.column_stack(np.where(skeleton_image > 0))  # Coordinates of line pixels

            # Apply DBSCAN clustering algorithm based on proximity
            dbscan = DBSCAN(eps=5, min_samples=5)  # Adjusted min_samples for tighter clusters
            clusters = dbscan.fit_predict(non_zero_points)

            # Group points by cluster
            clustered_lines = {}
            for i, cluster_id in enumerate(clusters):
                if cluster_id == -1:  # Ignore noise points
                    continue
                if cluster_id not in clustered_lines:
                    clustered_lines[cluster_id] = []
                clustered_lines[cluster_id].append(non_zero_points[i])

            # Generate waypoints for each cluster and mark them on the image
            waypoint_image = cv2.cvtColor(cv2.bitwise_not(skeleton_image), cv2.COLOR_GRAY2BGR)  # Convert to BGR
            for cluster_id, line_points in clustered_lines.items():
                # Convert points to numpy array and sort them
                line_points = np.array(line_points)
                sorted_line_points = line_points[np.argsort(line_points[:, 1])]  # Sort by y-coordinate (or x if needed)

                # Generate waypoints along the sorted line
                waypoints = generate_waypoints(sorted_line_points, interval=13)  # Reduced interval for more waypoints
                for waypoint in waypoints:
                    # Draw the waypoint as a small red dot on the black line
                    cv2.circle(waypoint_image, (waypoint[1], waypoint[0]), 1, (0, 0, 255), -1)  # Red dot

            # The waypoint image is now processed, you can use or display it directly
            # For example, display the image
            cv2.imshow(f"Waypoints for {file_name}", waypoint_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    print("Waypoint marking complete.")
