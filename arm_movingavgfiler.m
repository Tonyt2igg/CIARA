% Load joint angles data from CSV
filename = 'D:\CIARA\1csv_transfer\CSV\matlab\square_joint_angles.csv';
joint_angles = csvread(filename);

% Parameters for Savitzky-Golay filter
window_size = 11; % Must be odd, adjust for smoothness
poly_order = 3;   % Polynomial order, keeps natural shape

% Apply Savitzky-Golay filter to smooth the joint angles
smoothed_angles = sgolayfilt(joint_angles, poly_order, window_size);

% Save the smoothed joint angles
output_filename = 'D:\CIARA\1csv_transfer\CSV\matlab\square_joint_angles_smooth.csv';
csvwrite(output_filename, smoothed_angles);

% Plot comparison: Original vs Smoothed
figure;
for i = 1:size(joint_angles, 2)
    subplot(2,2,i);
    plot(joint_angles(:, i), 'r--', 'LineWidth', 1); % Original (dotted red)
    hold on;
    plot(smoothed_angles(:, i), 'b', 'LineWidth', 1.5); % Smoothed (blue)
    title(['Joint ', num2str(i)]);
    xlabel('Time Step');
    ylabel('Angle (degrees)');
    legend('Original', 'Smoothed');
    grid on;
end
