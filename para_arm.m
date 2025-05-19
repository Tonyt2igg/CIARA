clc; clear; close all;

%% Define 5-DOF Robotic Arm
robot = rigidBodyTree('DataFormat', 'row', 'MaxNumBodies', 5);
L = [0.3, 0.25, 0.2, 0.15, 0.1]; % Link lengths

prevBody = robot.BaseName;
for i = 1:5
    body = rigidBody(['link', num2str(i)]);
    joint = rigidBodyJoint(['joint', num2str(i)], 'revolute');
    joint.JointAxis = [0 0 1];
    tform = trvec2tform([L(i), 0, 0]);
    joint.HomePosition = 0;
    setFixedTransform(joint, tform);
    body.Joint = joint;
    addBody(robot, body, prevBody);
    prevBody = body.Name;
end

show(robot);
title('5-DOF Robotic Arm');
grid on;

%% Define Waypoints and Generate Trajectory
q_home = zeros(5,1);
waypoints = [q_home, q_home + deg2rad([30; -20; 15; -10; 5])];
timePoints = [0, 5];
timeSamples = linspace(0, 5, 100);

[q_traj, qd_traj, qdd_traj] = quinticpolytraj(waypoints, timePoints, timeSamples);

%% Compute Torque Required to Hold Pose
robot.Gravity = [0 0 -9.81];
dynamics = inverseDynamics(robot, q_traj', qd_traj', qdd_traj');

%% Plot Results
figure;
subplot(3,1,1);
plot(timeSamples, q_traj', 'LineWidth', 2);
xlabel('Time (s)'); ylabel('Position (rad)'); title('Joint Positions'); grid on;

subplot(3,1,2);
plot(timeSamples, qd_traj', 'LineWidth', 2);
xlabel('Time (s)'); ylabel('Velocity (rad/s)'); title('Joint Velocities'); grid on;

subplot(3,1,3);
plot(timeSamples, qdd_traj', 'LineWidth', 2);
xlabel('Time (s)'); ylabel('Acceleration (rad/s^2)'); title('Joint Accelerations'); grid on;

figure;
plot(timeSamples, dynamics', 'LineWidth', 2);
xlabel('Time (s)'); ylabel('Torque (Nm)'); title('Joint Torques Required to Hold Pose'); grid on;