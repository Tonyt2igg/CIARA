import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Use raw string for Windows paths
file_path = r"D:\Games\trash\waypoints.csv"

# Read CSV file
try:
    # Read the CSV file without assuming header
    df = pd.read_csv(file_path, header=None)
    
    # Assign column names explicitly
    df.columns = ['x', 'y']
    
    # Clean any potential whitespace in data
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    exit()
except Exception as e:
    print(f"Error reading file: {str(e)}")
    exit()

# Convert to numeric types in case of string data
df = df.apply(pd.to_numeric, errors='coerce')

# Check for missing or invalid data
if df.isnull().values.any():
    print("Warning: Missing or invalid data points detected. These will be dropped.")
    df = df.dropna()

# Calculate distances between consecutive points
dx = np.diff(df['x'])
dy = np.diff(df['y'])
distances = np.sqrt(dx**2 + dy**2)

# Calculate adaptive threshold using robust statistics
def calculate_threshold(distances):
    q75, q25 = np.percentile(distances, [75, 25])
    iqr = q75 - q25
    return q75 + 2 * iqr  # Increased multiplier for better separation

threshold = calculate_threshold(distances)

# Visualization
plt.figure(figsize=(12, 6))
plt.hist(distances, bins=100, color='skyblue', edgecolor='black')
plt.axvline(threshold, color='red', linestyle='--', label=f'Threshold: {threshold:.2f}')
plt.title('Distance Distribution Analysis\n(Pen Lift Threshold Detection)', pad=20)
plt.xlabel('Euclidean Distance Between Points', labelpad=15)
plt.ylabel('Frequency', labelpad=15)
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# Enhanced statistics
stats = {
    "Threshold": threshold,
    "Median": np.median(distances),
    "Mean": np.mean(distances),
    "Max": np.max(distances),
    "95th Percentile": np.percentile(distances, 95)
}

print("\nDrawing Quality Analysis Report:")
for k, v in stats.items():
    print(f"{k+':':<18} {v:.2f}")

print("\nRecommendation:")
if threshold < stats["95th Percentile"]:
    print("Threshold appears valid - use for pen lifting")
else:
    print("Warning: Threshold might be too high - consider manual adjustment")