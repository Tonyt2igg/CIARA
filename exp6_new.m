clc; clear; 
% Create a 2-DOF Planar Robot 
L(1) = Link([0 0 1 0]); % Link 1 
L(2) = Link([0 0 1 0]); % Link 2 
robot = SerialLink(L, 'name', '2-DOF Robot'); 
% Define End-Effector Target Position 
targetPose = [1.5 0.5]; 
% Solve Inverse Kinematics 
qSol = robot.ikine(transl(targetPose(1), targetPose(2), 0), [0 0]); 
% Display Joint Angles 
disp('Inverse Kinematics Joint Angles:'); 
disp(qSol); 
% Plot Robot Motion 
robot.plot(qSol); 