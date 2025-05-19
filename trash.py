import numpy as np
import matplotlib.pyplot as plt

# Define DH parameters
# [theta (rad), d (m), a (m), alpha (rad)]
dh_params = [
    [0,      0.04,     0,          0],
    [0,      0,        0.083609,   np.pi/2],
    [0,      0,        0.16195,    np.pi],
    [0,      0,        0.0013557, -np.pi]
]

def dh_transform(theta, d, a, alpha):
    """Return the individual transformation matrix using DH parameters."""
    return np.array([
        [np.cos(theta), -np.sin(theta)*np.cos(alpha),  np.sin(theta)*np.sin(alpha), a*np.cos(theta)],
        [np.sin(theta),  np.cos(theta)*np.cos(alpha), -np.cos(theta)*np.sin(alpha), a*np.sin(theta)],
        [0,              np.sin(alpha),                np.cos(alpha),               d],
        [0,              0,                            0,                           1]
    ])

# Compute forward kinematics
origins = [np.array([0, 0, 0, 1])]
T = np.eye(4)

for i, (theta, d, a, alpha) in enumerate(dh_params):
    A = dh_transform(theta, d, a, alpha)
    T = T @ A
    origin = T @ np.array([0, 0, 0, 1])
    origins.append(origin)

# Convert to XYZ for plotting
x_vals = [o[0] for o in origins]
y_vals = [o[1] for o in origins]
z_vals = [o[2] for o in origins]

# Plotting the arm
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot(x_vals, y_vals, z_vals, '-o', linewidth=3, markersize=6, color='goldenrod')

for i, (x, y, z) in enumerate(zip(x_vals, y_vals, z_vals)):
    ax.text(x, y, z, f'Link {i}', fontsize=10)

# Set plot limits and labels
ax.set_xlabel('X axis (m)')
ax.set_ylabel('Y axis (m)')
ax.set_zlabel('Z axis (m)')
ax.set_title('4-DOF Robotic Arm Visualization')
ax.set_box_aspect([1,1,1])  # Equal aspect ratio

plt.show()
