import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev
from skimage.morphology import skeletonize
from skimage import img_as_ubyte

# Parameters
WAYPOINTS_PER_LINE = 250
CLUSTER_PROXIMITY = 60  # DBSCAN clustering proximity
APPROX_EPSILON = 5.0  # ApproxPolyDP simplification factor


def load_image(image_path):
    """Load the sketch image in grayscale."""
    return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)


def detect_edges(image):
    """Apply edge detection on the image."""
    return cv2.Canny(image, 100, 200)


def find_contours(edges):
    """Find contours in the edge-detected image."""
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [contour[:, 0, :] for contour in contours]  # Extract x, y points


def cluster_lines(lines):
    """Cluster lines based on proximity using DBSCAN."""
    from sklearn.cluster import DBSCAN

    all_points = np.vstack(lines)  # Combine all points into a single array
    clustering = DBSCAN(eps=CLUSTER_PROXIMITY, min_samples=1).fit(all_points)

    # Group points by cluster
    clustered_lines = {}
    for point, label in zip(all_points, clustering.labels_):
        if label not in clustered_lines:
            clustered_lines[label] = []
        clustered_lines[label].append(point)

    # Convert to numpy arrays
    clustered_lines = {label: np.array(points) for label, points in clustered_lines.items()}
    return clustered_lines


def smooth_waypoints(points, num_waypoints=250):
    """Fit a B-spline to the points and generate smooth waypoints."""
    if len(points) < 3:  # Need at least 3 points for spline fitting
        return points

    # Fit a B-spline to the points
    tck, _ = splprep([points[:, 0], points[:, 1]], s=5)  # `s` is the smoothing factor
    u = np.linspace(0, 1, num_waypoints)

    # Generate evenly spaced waypoints
    smooth_points = np.array(splev(u, tck)).T
    return smooth_points


def simplify_contour(contour, epsilon=8):
    """Simplify contour using Ramer-Douglas-Peucker."""
    return cv2.approxPolyDP(contour, epsilon, closed=False).reshape(-1, 2)


def adaptive_sampling(points, max_points=250):
    """Sample waypoints adaptively based on curvature."""
    if len(points) < 3:
        return points

    # Calculate differences (approximation of curvature)
    diffs = np.diff(points, axis=0)
    curvatures = np.linalg.norm(np.diff(diffs, axis=0), axis=1)

    # Normalize curvatures and calculate weights
    weights = np.interp(curvatures, (curvatures.min(), curvatures.max()), (1, 10))
    total_weight = weights.sum()

    # Determine the number of points to sample for each segment
    samples_per_segment = np.round(weights / total_weight * max_points).astype(int)
    sampled_points = [points[0]]

    for i, num_samples in enumerate(samples_per_segment):
        segment = np.linspace(points[i], points[i + 1], num_samples)
        sampled_points.extend(segment)

    return np.array(sampled_points)


def skeletonize_image(image):
    """Skeletonize a binary image."""
    binary = image > 128  # Convert to binary
    skeleton = skeletonize(binary)
    return img_as_ubyte(skeleton)


def visualize_results(image, contours, clustered_lines, smooth_lines, simplified_lines, skeleton):
    """Visualize all methods."""
    plt.figure(figsize=(20, 15))

    # Original Image
    plt.subplot(2, 3, 1)
    plt.imshow(image, cmap='gray')
    plt.title("Original Image")

    # Detected Contours
    plt.subplot(2, 3, 2)
    plt.imshow(image, cmap='gray')
    for contour in contours:
        plt.plot(contour[:, 0], contour[:, 1], linewidth=1)
    plt.title("Contours")

    # Clustered Lines
    plt.subplot(2, 3, 3)
    plt.imshow(image, cmap='gray')
    for points in clustered_lines.values():
        plt.plot(points[:, 0], points[:, 1], linewidth=2)
    plt.title("Clustered Lines")

    # Smoothed Lines
    plt.subplot(2, 3, 4)
    plt.imshow(image, cmap='gray')
    for points in smooth_lines:
        plt.plot(points[:, 0], points[:, 1], linewidth=2)
    plt.title("Smoothed Waypoints (B-spline)")

    # Simplified Lines
    plt.subplot(2, 3, 5)
    plt.imshow(image, cmap='gray')
    for points in simplified_lines:
        plt.plot(points[:, 0], points[:, 1], linewidth=2)
    plt.title("Simplified Contours (RDP)")

    # Skeleton
    plt.subplot(2, 3, 6)
    plt.imshow(skeleton, cmap='gray')
    plt.title("Skeletonized Image")

    plt.tight_layout()
    plt.show()


# Main Execution
if __name__ == "__main__":
    # Load and process the image
    image_path = r"C:\projects\cyclegan\tech\Unpaired-Portrait-Drawing\results\pretrained\test_200\examples\temp_output\input_image_fake2.png"  # Replace with your image path
    image = load_image(image_path)
    edges = detect_edges(image)
    contours = find_contours(edges)

    # Cluster lines
    clustered_lines = cluster_lines(contours)

    # Smooth lines
    smooth_lines = [smooth_waypoints(points) for points in contours]

    # Simplify contours
    simplified_lines = [simplify_contour(points, epsilon=APPROX_EPSILON) for points in contours]

    # Skeletonize the image
    skeleton = skeletonize_image(edges)

    # Visualize results
    visualize_results(image, contours, clustered_lines, smooth_lines, simplified_lines, skeleton)
