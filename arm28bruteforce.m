%% ======================== SETUP & CONFIGURATION ========================
robot = importrobot('D:\Traiding model\project5\working\ciara7\urdf\ciara7.urdf');  
show(robot, 'Frames', 'off');  % Faster rendering (disable frames)

% Load waypoints from CSV
waypointsData = csvread("D:\CIARA\1csv_transfer\CSV\vscode_user\square_waypoints.csv");  
waypoints = waypointsData(:, 1:3);  % X, Y, Z
orientations = waypointsData(:, 4:6);  % Roll, Pitch, Yaw

% Simulation speed-up factor (higher = faster but less smooth)
speed_factor = 1;  % Reduce waypoints by this factor (try 2-5)

% Joint limits (degrees)
motor_limits_deg = [
    [-90, 90];    % Motor 1
    [-90, 90];    % Motor 2
    [-130, 130]   % Motor 3
];
theta4_limits_deg = [-180, 180];  

%% ======================== PRE-PROCESS WAYPOINTS ========================
% (1) Reduce waypoints for faster simulation
if speed_factor > 1
    waypoints = waypoints(1:speed_factor:end, :);
    orientations = orientations(1:speed_factor:end, :);
end

% (2) Add lifted waypoints for long movements
threshold = 0.05;  % Distance threshold to trigger lift
z_lift = 0.04;     % Lifted Z height
new_waypoints = [];
new_orientations = [];

for i = 1:size(waypoints,1)-1
    current = waypoints(i,:);
    next = waypoints(i+1,:);
    dist = norm(current - next);
    
    new_waypoints = [new_waypoints; current];
    new_orientations = [new_orientations; orientations(i,:)];
    
    if dist > threshold
        lifted_current = [current(1:2), current(3) + z_lift];
        lifted_next = [next(1:2), next(3) + z_lift];
        
        new_waypoints = [new_waypoints; lifted_current; lifted_next];
        new_orientations = [new_orientations; orientations(i,:); orientations(i+1,:)];
    end
end
new_waypoints = [new_waypoints; waypoints(end,:)];
new_orientations = [new_orientations; orientations(end,:)];

% (3) Lightweight interpolation (fewer points)
t = 1:size(new_waypoints, 1);
t_interp = linspace(1, size(new_waypoints, 1), round(size(new_waypoints, 1) / speed_factor));

x_interp = spline(t, new_waypoints(:, 1), t_interp);
y_interp = spline(t, new_waypoints(:, 2), t_interp);
z_interp = spline(t, new_waypoints(:, 3), t_interp);
interpolated_waypoints = [x_interp', y_interp', z_interp'];

roll_interp = spline(t, new_orientations(:, 1), t_interp);
pitch_interp = spline(t, new_orientations(:, 2), t_interp);
yaw_interp = spline(t, new_orientations(:, 3), t_interp);
interpolated_orientations = [roll_interp', pitch_interp', yaw_interp'];

%% ======================== BRUTE-FORCE IK SOLVER ========================
joint_angles = [];
drawn_path = [];
prev_theta_deg = [0, 0, 0];  % Start from home position
search_delta = 10;  % ±10° search range (adjust for speed/accuracy)

% Plot setup
figure;
hold on;
xlabel('X'); ylabel('Y'); zlabel('Z');
title('CIARA Robot Path (Brute-Force IK)');
grid on;
view(3);

% Start timer
tic;

for i = 1:size(interpolated_waypoints,1)
    targetPos = interpolated_waypoints(i,:);
    targetRPY = interpolated_orientations(i,:);
    targetRot = eul2rotm(targetRPY, 'XYZ');
    
    % Brute-force search (integer degrees)
    best_error = Inf;
    best_theta = zeros(1,4);
    
    theta1_range = max(motor_limits_deg(1,1), prev_theta_deg(1)-search_delta) : 1 : ...
                   min(motor_limits_deg(1,2), prev_theta_deg(1)+search_delta);
    theta2_range = max(motor_limits_deg(2,1), prev_theta_deg(2)-search_delta) : 1 : ...
                   min(motor_limits_deg(2,2), prev_theta_deg(2)+search_delta);
    theta3_range = max(motor_limits_deg(3,1), prev_theta_deg(3)-search_delta) : 1 : ...
                   min(motor_limits_deg(3,2), prev_theta_deg(3)+search_delta);
    
    for t1 = theta1_range
        for t2 = theta2_range
            for t3 = theta3_range
                theta4 = round(-(180 + t2 - t3));  % Geometric rule
                
                if theta4 < theta4_limits_deg(1) || theta4 > theta4_limits_deg(2)
                    continue;  % Skip invalid theta4
                end
                
                % Forward kinematics
                config = robot.homeConfiguration;
                config(1).JointPosition = deg2rad(t1);
                config(2).JointPosition = deg2rad(t2);
                config(3).JointPosition = deg2rad(t3);
                config(4).JointPosition = deg2rad(theta4);
                
                eeTransform = getTransform(robot, config, 'end');
                eePos = tform2trvec(eeTransform);
                eeRot = tform2rotm(eeTransform);
                
                % Error metric (weighted)
                pos_error = norm(eePos - targetPos);
                rot_error = acos((trace(targetRot' * eeRot) - 1)/2);
                total_error = pos_error + 0.3 * rot_error;  % Tune weight (0.3)
                
                if total_error < best_error
                    best_error = total_error;
                    best_theta = [t1, t2, t3, theta4];
                end
            end
        end
    end
    
    % Store solution
    joint_angles = [joint_angles; best_theta];
    prev_theta_deg = best_theta(1:3);
    
    % Update visualization (every N steps for speed)
    if mod(i, 3) == 0 || i == 1
        show(robot, config, 'PreservePlot', false, 'FastUpdate', true);
        eePos = tform2trvec(getTransform(robot, config, 'end'));
        drawn_path = [drawn_path; eePos];
        plot3(drawn_path(:,1), drawn_path(:,2), drawn_path(:,3), 'r-', 'LineWidth', 1.5);
        drawnow limitrate;  % Faster rendering
    end
end

% Display computation time
fprintf('IK solved in %.2f seconds\n', toc);

% Save results
csvwrite('D:\CIARA\1csv_transfer\CSV\matlab\arrow_angles.csv', joint_angles);