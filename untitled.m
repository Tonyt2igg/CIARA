clc; clear; close all;

% Load URDF Robot Model
robot = importrobot('D:\Traiding model\project5\working\ciara7\urdf\ciara7.urdf');
robot.DataFormat = 'column';
robot.Gravity = [0 0 -9.81]; % Set gravity in Z-direction

% Define Joint Limits: [min, max] in degrees
jointLimits = deg2rad([ 
    -90,  90;  % Joint 1
    -90,  90;  % Joint 2
    -130, 130; % Joint 3
    -90,  90   % Joint 4
]);

% **Increase the Number of Samples for High Density**
numSamples = 2000000; % High-density plot
ee_positions = zeros(3, numSamples); % Store end-effector positions

% Generate Random Joint Configurations Within Limits
for i = 1:numSamples
    q_rand = jointLimits(:, 1) + (jointLimits(:, 2) - jointLimits(:, 1)) .* rand(4, 1);
    T = getTransform(robot, q_rand, 'end'); 
    ee_positions(:, i) = T(1:3, 4);
end

% **Filter Points where Y ≥ -0.05 and Z ≈ 0.06**
z_target = 0.06; % Desired Z-plane
z_tolerance = 0.002; % Small range to capture nearby points
valid_idx = (ee_positions(2, :) >= -0.05) & (abs(ee_positions(3, :) - z_target) <= z_tolerance);
filtered_positions = ee_positions(:, valid_idx);

% **Plot Only the Workspace at Z = 0.06**
figure('Position', [100, 100, 1600, 1000]); % Large figure
scatter(filtered_positions(1, :), filtered_positions(2, :), ...
    2, 'b', 'filled', 'MarkerEdgeColor', 'none'); % Blue dots for the plane

% Labels and Formatting
xlabel('X (m)', 'FontSize', 16); 
ylabel('Y (m)', 'FontSize', 16); 
title('Robot Workspace at Z = 0.06 (Filtered for Y ≥ -0.05)', 'FontSize', 18);

grid on; 
axis equal;
