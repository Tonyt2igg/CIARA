import math

# All waypoints provided
waypoints = [
    (-0.0034782608695652084, 0.19841269841269837),
    (-0.004347826086956524, 0.19920634920634922),
    (-0.0034782608695652084, 0.2),
    (-0.00260869565217392, 0.19920634920634922),
    (-0.009565217391304365, 0.1968253968253968),
    (-0.010434782608695653, 0.19761904761904758),
    (-0.009565217391304365, 0.19841269841269837),
    (-0.008695652173913049, 0.19761904761904758),
    (-0.017391304347826098, 0.1968253968253968),
    (-0.018260869565217386, 0.19761904761904758),
    (-0.017391304347826098, 0.19841269841269837),
    (-0.01652173913043478, 0.19761904761904758),
    (-0.013913043478260861, 0.196031746031746),
    (-0.014782608695652177, 0.1968253968253968),
    (-0.013913043478260861, 0.19761904761904758),
    (-0.013043478260869573, 0.1968253968253968),
    (-0.04869565217391306, 0.19365079365079363),
    (-0.049565217391304345, 0.19444444444444442),
    (-0.04869565217391306, 0.1952380952380952),
    (-0.04782608695652174, 0.19444444444444442),
    (-0.032173913043478275, 0.17063492063492064),
]

# Calculate distances between consecutive waypoints
distances = []
for i in range(len(waypoints) - 1):
    x1, y1 = waypoints[i]
    x2, y2 = waypoints[i + 1]
    distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    distances.append(distance)

# Calculate statistics
average_distance = sum(distances) / len(distances)
max_distance = max(distances)
min_distance = min(distances)

# Print distances
print("Distances between consecutive waypoints:")
for i, d in enumerate(distances, 1):
    print(f"Distance {i}: {d:.5f}")

# Print statistics
print(f"\nAverage distance: {average_distance:.5f}")
print(f"Maximum distance: {max_distance:.5f}")
print(f"Minimum distance: {min_distance:.5f}")

