import cv2
import numpy as np
from skimage.morphology import skeletonize
from sklearn.cluster import DBSCAN
from PIL import Image
import random
import matplotlib.pyplot as plt

# Load the sketch image
image = cv2.imread("C:\\Users\\tonyb\\OneDrive\\Pictures\\input_image_fake.png", cv2.IMREAD_GRAYSCALE)

# Resize the image to a width of 400 pixels (downsampling)
height, width = image.shape
new_width = 600
scale_ratio = new_width / width
new_height = int(height * scale_ratio)
resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

# Binarize the image using adaptive thresholding
_, binary = cv2.threshold(resized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# Apply skeletonization
binary_bool = binary // 255  # Convert to boolean for skeletonization
skeleton = skeletonize(binary_bool).astype(np.uint8) * 255  # Convert back to uint8

# Step 1: Pixel-to-Pixel Line Extraction
def extract_lines(skeleton):
    height, width = skeleton.shape
    visited = np.zeros_like(skeleton, dtype=bool)
    lines = []

    def dfs(x, y, current_line):
        # Depth-First Search (DFS) for connected pixels
        if x < 0 or y < 0 or x >= height or y >= width:
            return
        if skeleton[x, y] == 0 or visited[x, y]:
            return
        visited[x, y] = True
        current_line.append((x, y))
        # Explore neighbors
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            dfs(x + dx, y + dy, current_line)

    for i in range(height):
        for j in range(width):
            if skeleton[i, j] == 255 and not visited[i, j]:
                line = []
                dfs(i, j, line)
                if len(line) > 10:  # Filter out noise (e.g., small fragments)
                    lines.append(line)

    return lines

lines = extract_lines(skeleton)

# Step 2: Line Clustering
def cluster_lines(lines, eps=5, min_samples=5):
    # Flatten lines into points with labels for clustering
    points = []
    for idx, line in enumerate(lines):
        points.extend([(x, y, idx) for x, y in line])

    points = np.array(points)
    coords = points[:, :2]

    # DBSCAN clustering
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(coords)
    clustered_lines = {i: [] for i in set(clustering.labels_)}

    for point, label in zip(points, clustering.labels_):
        if label != -1:  # Exclude noise
            clustered_lines[label].append(point[:2])

    return clustered_lines

clustered_lines = cluster_lines(lines, eps=7, min_samples=10)

# Step 3: Waypoint Generation
def generate_waypoints(clustered_lines, max_waypoints=250):
    waypoints = []
    for cluster_id, cluster_points in clustered_lines.items():
        if len(cluster_points) > max_waypoints:
            sampled_points = cluster_points[::len(cluster_points) // max_waypoints]
        else:
            sampled_points = cluster_points
        waypoints.append(sampled_points)
    return waypoints

waypoints = generate_waypoints(clustered_lines)

# Step 4: Visualize Extracted Lines and Waypoints
def visualize_lines(image, clustered_lines):
    output_image = np.zeros_like(image)
    for cluster_id, cluster_points in clustered_lines.items():
        color = random.randint(100, 255)  # Random gray intensity for each cluster
        for x, y in cluster_points:
            output_image[x, y] = color
    return output_image

final_output = visualize_lines(binary, clustered_lines)

# Step 5: Plot clustered waypoints
def plot_waypoints(clustered_lines):
    plt.figure(figsize=(10, 10))
    for cluster_id, cluster_points in clustered_lines.items():
        cluster_points = np.array(cluster_points)
        plt.scatter(cluster_points[:, 1], -cluster_points[:, 0], label=f'Cluster {cluster_id}', s=5)  # Inverted y-axis
    plt.legend()
    plt.title("Clustered Waypoints")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.show()

# Additional Function: Find Contours
def find_contours(edges, nth=1):
    HEIGHT = len(edges)
    WIDTH = len(edges[0])

    viewed = set()
    starts = []

    def is_valid(x, y):
        return 0 <= x < WIDTH and 0 <= y < HEIGHT

    def get_neighbours(x, y):
        candidates = [
            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
            (x - 1, y), (x + 1, y),
            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)
        ]
        result = [
            point
            for point in candidates
            if is_valid(point[0], point[1]) and edges[point[1]][point[0]] == 255 and point not in viewed
        ]
        return result

    def search_iterative(x, y):
        stack = [(x, y)]
        path = []
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in viewed:
                continue
            viewed.add((cx, cy))
            path.append((cx, cy))
            for neighbor in get_neighbours(cx, cy):
                stack.append(neighbor)
        return path

    for i in range(HEIGHT):  # y
        for j in range(WIDTH):  # x
            if edges[i][j] == 255 and len(get_neighbours(j, i)) == 1:
                starts.append((j, i))

    final = []
    for start in starts:
        if start not in viewed:
            viewed.add(start)
            points = search_iterative(start[0], start[1])
            points = np.array(points[::nth])
            if len(points) >= 1:
                final.append(points)

    return final



# Convert binary image to PIL format for find_contours
pil_image = Image.fromarray(binary)
orig_array = np.array(pil_image)

# Find contours
contours = find_contours(orig_array)

# Visualize contours
plt.figure()
plt.title("Contours")
for contour in contours:
    plt.plot(contour[:, 0], -contour[:, 1], 'k-', linewidth=1)
plt.gca().invert_yaxis()
plt.show()

# Display the results
cv2.imshow("Original Sketch", resized)
cv2.imshow("Skeleton", skeleton)
cv2.imshow("Extracted Lines", final_output)
plot_waypoints(clustered_lines)

cv2.waitKey(0)
cv2.destroyAllWindows()
