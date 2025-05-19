clc; clear; close all;
N = 4;
robot = rigidBodyTree('MaxNumBodies', N);
robot.DataFormat = 'row';
robot.Gravity = [0 0 -9.81];
L = [0.4, 0.3, 0.2, 0.1];
m = [2, 1.5, 1, 0.5];
I = repmat([0.01, 0.01, 0.01, 0, 0, 0], N, 1);
for i = 1:N
    body = rigidBody(['link' num2str(i)]);
    joint = rigidBodyJoint(['joint' num2str(i)], 'revolute');
    setFixedTransform(joint, trvec2tform([L(i), 0, 0]));
    joint.JointAxis = [0 0 1];
    body.Joint = joint;
    body.Mass = m(i);
    body.CenterOfMass = [L(i)/2, 0, 0];
    body.Inertia = I(i, :);
    if i == 1
        addBody(robot, body, 'base');
    else
        addBody(robot, body, ['link' num2str(i-1)]);
    end
end
t_end = 20;
dt = 0.1;
time = 0:dt:t_end;
q_initial = [0, 0, 0, 0];
q_final = [0.5, -0.8, 0.6, 0.3];
q_trajectory = zeros(length(time), N);
qd_trajectory = zeros(length(time), N);
qdd_trajectory = zeros(length(time), N);
end_effector_position = zeros(length(time), 3);
torques = zeros(length(time), N);
for t = 1:length(time)
    q_trajectory(t, :) = q_initial + (q_final - q_initial) * (time(t) / t_end);
    if t > 1
        qd_trajectory(t, :) = (q_trajectory(t, :) - q_trajectory(t-1, :)) / dt;
    end
    if t > 2
        qdd_trajectory(t, :) = (qd_trajectory(t, :) - qd_trajectory(t-1, :)) / dt;
    end
    torques(t, :) = inverseDynamics(robot, q_trajectory(t, :), qd_trajectory(t, :), qdd_trajectory(t, :));
    fprintf('Time: %.2f s -> Joint Torques: [%.4f, %.4f, %.4f, %.4f] Nm\n', time(t), torques(t, :));
    T = getTransform(robot, q_trajectory(t, :), 'link4', 'base');
    end_effector_position(t, :) = T(1:3, 4);
end
figure;
subplot(3, 1, 1);
plot(time, end_effector_position(:, 1), 'r-', 'LineWidth', 1.5);
title('End-Effector X Position vs Time');
xlabel('Time (s)');
ylabel('X Position (m)');
grid on;
subplot(3, 1, 2);
plot(time, end_effector_position(:, 2), 'g-', 'LineWidth', 1.5);
title('End-Effector Y Position vs Time');
xlabel('Time (s)');
ylabel('Y Position (m)');
grid on;
subplot(3, 1, 3);
plot(time, end_effector_position(:, 3), 'b-', 'LineWidth', 1.5);
title('End-Effector Z Position vs Time');
xlabel('Time (s)');
ylabel('Z Position (m)');
grid on;
figure;
subplot(4, 1, 1);
plot(time, q_trajectory);
title('Joint Positions vs Time');
xlabel('Time (s)');
ylabel('Position (radians)');
legend('Joint 1', 'Joint 2', 'Joint 3', 'Joint 4');
grid on;
subplot(4, 1, 2);
plot(time, qd_trajectory);
title('Joint Velocities vs Time');
xlabel('Time (s)');
ylabel('Velocity (rad/s)');
legend('Joint 1', 'Joint 2', 'Joint 3', 'Joint 4');
grid on;
subplot(4, 1, 3);
plot(time, qdd_trajectory);
title('Joint Accelerations vs Time');
xlabel('Time (s)');
ylabel('Acceleration (rad/s²)');
legend('Joint 1', 'Joint 2', 'Joint 3', 'Joint 4');
grid on;
subplot(4, 1, 4);
plot(time, torques);
title('Joint Torques vs Time');
xlabel('Time (s)');
ylabel('Torque (Nm)');
legend('Joint 1', 'Joint 2', 'Joint 3', 'Joint 4');
grid on;
figure;
hold on;
grid on;
axis equal;
xlabel('X (m)');
ylabel('Y (m)');
zlabel('Z (m)');
title('End-Effector 3D Trajectory Animation');
xlim([min(end_effector_position(:, 1)) - 0.1, max(end_effector_position(:, 1)) + 0.1]);
ylim([min(end_effector_position(:, 2)) - 0.1, max(end_effector_position(:, 2)) + 0.1]);
zlim([min(end_effector_position(:, 3)) - 0.1, max(end_effector_position(:, 3)) + 0.1]);
h = plot3(end_effector_position(1, 1), end_effector_position(1, 2), end_effector_position(1, 3), 'ro', 'MarkerSize', 8, 'LineWidth', 2);
trajectory_line = plot3(NaN, NaN, NaN, 'b-', 'LineWidth', 1.5);
for t = 1:length(time)
    set(h, 'XData', end_effector_position(t, 1), 'YData', end_effector_position(t, 2), 'ZData', end_effector_position(t, 3));
    set(trajectory_line, 'XData', end_effector_position(1:t, 1), ...
                         'YData', end_effector_position(1:t, 2), ...
                         'ZData', end_effector_position(1:t, 3));
    pause(0.05);
end
