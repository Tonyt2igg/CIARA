clear; clc;
syms theta1 theta2 theta3 theta4;
L1 = 1; L2 = 1; L3 = 1; L4 = 1;  % Set all link lengths to 1 meter
Rot1 = [cos(theta1) -sin(theta1) 0; sin(theta1) cos(theta1) 0; 0 0 1];
Rot2 = [cos(theta2) 0 sin(theta2); 0 1 0; -sin(theta2) 0 cos(theta2)];
Rot3 = [1 0 0; 0 cos(theta3) -sin(theta3); 0 sin(theta3) cos(theta3)];
Rot4 = [cos(theta4) -sin(theta4) 0; sin(theta4) cos(theta4) 0; 0 0 1];
T1 = [Rot1 [0; 0; L1]; 0 0 0 1];
T2 = [Rot2 [0; 0; L2]; 0 0 0 1];
T3 = [Rot3 [L3; 0; 0]; 0 0 0 1];
T4 = [Rot4 [L4; 0; 0]; 0 0 0 1];
FK = T1 * T2 * T3 * T4;
disp('Forward Kinematics Transformation Matrix:');
disp(FK);
theta1_val = input('Enter joint angle theta1 (in degrees): ');
theta2_val = input('Enter joint angle theta2 (in degrees): ');
theta3_val = input('Enter joint angle theta3 (in degrees): ');
theta4_val = input('Enter joint angle theta4 (in degrees): ');
theta1_val = deg2rad(theta1_val);
theta2_val = deg2rad(theta2_val);
theta3_val = deg2rad(theta3_val);
theta4_val = deg2rad(theta4_val);
EeP = double(subs(FK, {theta1, theta2, theta3, theta4}, ...
                  {theta1_val, theta2_val, theta3_val, theta4_val}));
disp('End-Effector Position and Orientation (Numerical Values):');
disp(EeP);
end_effector_position = EeP(1:3, 4);
disp('End-Effector Position (X, Y, Z):');
disp(end_effector_position);
