robot = importrobot('D:\Traiding model\project5\working\ciara5\urdf\ciara5.urdf');  
show(robot);  % Display the robot model

% Load waypoints from CSV
waypointsData = csvread("D:\CIARA\1csv_transfer\CSV\vscode_custom\waypoints.csv");  
waypoints = waypointsData(:, 1:3);  % X, Y, Z
orientations = waypointsData(:, 4:6);  % Roll, Pitch, Yaw

% Inverse kinematics setup
ik = inverseKinematics('RigidBodyTree', robot);  
ik.SolverAlgorithm = 'LevenbergMarquardt';  
weights = [1 1 1 1 1 1];  
initialguess = robot.homeConfiguration;  
endEffector = 'end';  % Confirm end-effector name

% Plot setup
figure;  
hold on;  
xlabel('X-axis'); ylabel('Y-axis'); zlabel('Z-axis');  
title('End Effector Drawing Path');  
grid on;  
view(3);  

drawn_path = [];  
joint_angles = [];  

% Joint limits (radians)
motor_limits = [
    deg2rad([-90, 90]);   % Motor 1
    deg2rad([-90, 90]);    % Motor 2
    deg2rad([-130, 130])  % Motor 3
];

% Use original waypoint and orientation order
orderedWaypoints = waypoints;
orderedOrientations = orientations;

% ========================================================================
% Insert lifted waypoints where distance exceeds threshold
% ========================================================================
threshold = 0.05;  % Distance threshold to trigger lift
z_lift = 0.04;      % Lifted Z height

new_waypoints = [];
new_orientations = [];
is_lifted = [];  % Track if a waypoint is part of a lifted move

for i = 1:size(orderedWaypoints,1)-1
    current = orderedWaypoints(i,:);
    next_wp = orderedWaypoints(i+1,:);
    dist = norm(current - next_wp);
    
    % Add current waypoint
    new_waypoints = [new_waypoints; current];
    new_orientations = [new_orientations; orderedOrientations(i,:)];
    is_lifted = [is_lifted; false];
    
    if dist > threshold
        % Insert lifted_current (current XY, Z + lift)
        lifted_current = [current(1:2), current(3) + z_lift];
        new_waypoints = [new_waypoints; lifted_current];
        new_orientations = [new_orientations; orderedOrientations(i,:)]; % Use current orientation
        is_lifted = [is_lifted; true];
        
        % Insert lifted_next (next XY, Z + lift)
        lifted_next = [next_wp(1:2), next_wp(3) + z_lift];
        new_waypoints = [new_waypoints; lifted_next];
        new_orientations = [new_orientations; orderedOrientations(i+1,:)]; % Use next orientation
        is_lifted = [is_lifted; true];
        
        % Add the original next waypoint (lowered)
        new_waypoints = [new_waypoints; next_wp];
        new_orientations = [new_orientations; orderedOrientations(i+1,:)];
        is_lifted = [is_lifted; false];
    end
end

% Add the last waypoint
new_waypoints = [new_waypoints; orderedWaypoints(end,:)];
new_orientations = [new_orientations; orderedOrientations(end,:)];
is_lifted = [is_lifted; false];

% ========================================================================
% Cubic Spline Interpolation
% ========================================================================
% Generate parameterized points for interpolation
t = 1:size(new_waypoints, 1);
t_interp = linspace(1, size(new_waypoints, 1), 2 * size(new_waypoints, 1)); % Limit to twice the number of waypoints

% Interpolate X, Y, Z coordinates
x_interp = spline(t, new_waypoints(:, 1), t_interp);
y_interp = spline(t, new_waypoints(:, 2), t_interp);
z_interp = spline(t, new_waypoints(:, 3), t_interp);

% Combine interpolated points
interpolated_waypoints = [x_interp', y_interp', z_interp'];

% Interpolate orientations (Roll, Pitch, Yaw)
roll_interp = spline(t, new_orientations(:, 1), t_interp);
pitch_interp = spline(t, new_orientations(:, 2), t_interp);
yaw_interp = spline(t, new_orientations(:, 3), t_interp);

% Combine interpolated orientations
interpolated_orientations = [roll_interp', pitch_interp', yaw_interp'];

% ========================================================================
% Main loop: Process interpolated_waypoints
% ========================================================================
for i = 1:size(interpolated_waypoints,1)
    targetPos = interpolated_waypoints(i,:);
    targetRPY = interpolated_orientations(i,:);
    
    % Convert orientation to rotation matrix
    rotm = eul2rotm(targetRPY, 'XYZ');
    targetPose = [rotm, targetPos'; 0 0 0 1];
    
    % Solve IK
    [config, solInfo] = ik(endEffector, targetPose, weights, initialguess);
    
    % Apply joint limits
    for j = 1:min(3, length(config))
        config(j).JointPosition = max(motor_limits(j,1), min(motor_limits(j,2), config(j).JointPosition));
    end
    
    % Compute theta4
    theta2_deg = rad2deg(config(2).JointPosition);
    theta3_deg = rad2deg(config(3).JointPosition);
    theta5 = 180 - (90 + theta2_deg) - (180 - theta3_deg);
    theta4_deg = -(90 - theta5);
    
    % Store joint angles (motors 1-4)
    theta = [rad2deg(config(1).JointPosition), theta2_deg, theta3_deg, theta4_deg];
    joint_angles = [joint_angles; theta];  % Directly store angles
    
    % Update robot visualization
    show(robot, config, 'PreservePlot', false);
    
    % Add to drawn_path
    eeTransform = getTransform(robot, config, endEffector);  
    eePos = tform2trvec(eeTransform);
    drawn_path = [drawn_path; eePos];  
    plot3(drawn_path(:,1), drawn_path(:,2), drawn_path(:,3), 'r-', 'LineWidth', 2);
    
    pause(0.000001);
    initialguess = config; % Update initial guess for next iteration
end

hold off;  
csvwrite('D:\CIARA\1csv_transfer\CSV\matlab\joint_angles.csv', joint_angles);
