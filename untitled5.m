clear; clc; close all;

fig = figure('Name', '4-DOF Robotic Arm Control', 'NumberTitle', 'off');
ax = axes('Parent', fig, 'Position', [0.3 0.1 0.65 0.8]);
hold(ax, 'on'); grid(ax, 'on'); axis(ax, 'equal'); xlabel(ax, 'X'); ylabel(ax, 'Y'); zlabel(ax, 'Z'); view(ax, 3);

slider1 = uicontrol('Style', 'slider', 'Min', -180, 'Max', 180, 'Value', 30, 'Position', [20, 300, 200, 20], 'Callback', @(~, ~) updateArm(guidata(fig)));
slider2 = uicontrol('Style', 'slider', 'Min', -180, 'Max', 180, 'Value', -20, 'Position', [20, 250, 200, 20], 'Callback', @(~, ~) updateArm(guidata(fig)));
slider3 = uicontrol('Style', 'slider', 'Min', -180, 'Max', 180, 'Value', 15, 'Position', [20, 200, 200, 20], 'Callback', @(~, ~) updateArm(guidata(fig)));
slider4 = uicontrol('Style', 'slider', 'Min', -180, 'Max', 180, 'Value', -10, 'Position', [20, 150, 200, 20], 'Callback', @(~, ~) updateArm(guidata(fig)));

handles.ax = ax; handles.slider1 = slider1; handles.slider2 = slider2; handles.slider3 = slider3; handles.slider4 = slider4;
guidata(fig, handles);

function updateArm(handles)
    ax = handles.ax;
    cla(ax);
    Th = [get(handles.slider1, 'Value'), get(handles.slider2, 'Value'), get(handles.slider3, 'Value'), get(handles.slider4, 'Value')] * pi / 180;

    T = eye(4);
    positions = [0 0 0];
    link_lengths = [0.041 0.162 0.162 0.072];
    for i = 1:4
        R = [cos(Th(i)) -sin(Th(i)) 0; sin(Th(i)) cos(Th(i)) 0; 0 0 1];
        T = T * [R [link_lengths(i); 0; 0]; 0 0 0 1];
        positions = [positions; T(1:3, 4)'];
    end

    plot3(ax, positions(:, 1), positions(:, 2), positions(:, 3), '-o', 'LineWidth', 2, 'MarkerSize', 8, 'MarkerFaceColor', 'r');
    grid(ax, 'on'); axis(ax, 'equal'); view(ax, 3);
end

updateArm(handles);
