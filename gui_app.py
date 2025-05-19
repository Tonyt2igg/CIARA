import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox, 
    QComboBox, QHBoxLayout, QGroupBox, QGraphicsView, QGraphicsScene, QFileDialog
)
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage, QColor
from PyQt5.QtCore import Qt, QPoint
from PIL import Image
import cv2
import numpy as np
import os
import subprocess

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from testomg2 import fetch_image, process_image  # Adjust import based on your module's path


class DrawingCanvas(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Set up drawing attributes
        self.drawing = False
        self.last_point = QPoint()
        self.pen = QPen(Qt.black, 10, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        
        # Create a white pixmap as the drawing surface
        self.pixmap = QPixmap(800, 600)
        self.pixmap.fill(Qt.white)
        self.pixmap_item = self.scene.addPixmap(self.pixmap)
        self.setSceneRect(0, 0, 800, 600)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = self.mapToScene(event.pos()).toPoint()
            
    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) and self.drawing:
            painter = QPainter(self.pixmap)
            painter.setPen(self.pen)
            current_point = self.mapToScene(event.pos()).toPoint()
            painter.drawLine(self.last_point, current_point)
            painter.end()
            self.pixmap_item.setPixmap(self.pixmap)
            self.last_point = current_point
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            
    def clear(self):
        self.pixmap.fill(Qt.white)
        self.pixmap_item.setPixmap(self.pixmap)
        
    def get_image(self):
        return self.pixmap.toImage()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.custom_image_path = ""

    def initUI(self):
        # Main layout
        layout = QVBoxLayout()

        # Mode selection combo box
        self.mode_selector = QComboBox(self)
        self.mode_selector.addItems(["Select Mode", "Drawing Mode", "Pick and Place Mode", "Custom Mode"])
        self.mode_selector.currentIndexChanged.connect(self.switch_mode)
        layout.addWidget(self.mode_selector)

        # Drawing Mode Widgets
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Enter the object you want to draw")
        self.fetch_button = QPushButton("Fetch Image and Save CSV", self)
        self.fetch_button.clicked.connect(self.fetch_image_and_execute_pipeline)
        self.matlab_button = QPushButton("Run MATLAB to Generate Joint Angles CSV", self)
        self.matlab_button.clicked.connect(self.run_matlab_script)
        self.transfer_button = QPushButton("Transfer CSV to Raspberry Pi", self)
        self.transfer_button.clicked.connect(self.transfer_to_pi)
        self.image_label = QLabel(self)

        # Add Drawing Mode widgets to layout (initially hidden)
        layout.addWidget(self.input_field)
        layout.addWidget(self.fetch_button)
        layout.addWidget(self.matlab_button)
        layout.addWidget(self.transfer_button)
        layout.addWidget(self.image_label)

        # Pick and Place Mode Widgets
        self.pick_button = QPushButton("Start Pick and Place Task", self)
        self.pick_button.clicked.connect(self.run_pick_and_place)
        self.reset_button = QPushButton("Reset Robotic Arm", self)
        self.reset_button.clicked.connect(self.reset_arm)

        layout.addWidget(self.pick_button)
        layout.addWidget(self.reset_button)

        # Custom Mode Widgets
        self.canvas = DrawingCanvas(self)
        self.clear_button = QPushButton("Clear Canvas", self)
        self.clear_button.clicked.connect(self.canvas.clear)
        self.process_button = QPushButton("Process Drawing", self)
        self.process_button.clicked.connect(self.process_custom_drawing)
        self.skeleton_button = QPushButton("Generate Skeleton", self)
        self.skeleton_button.clicked.connect(self.generate_skeleton)
        self.waypoints_button = QPushButton("Generate Waypoints", self)
        self.waypoints_button.clicked.connect(self.generate_waypoints)
        self.custom_matlab_button = QPushButton("Upload to MATLAB", self)
        self.custom_matlab_button.clicked.connect(self.run_custom_matlab_script)
        self.custom_transfer_button = QPushButton("Transfer to Raspberry Pi", self)
        self.custom_transfer_button.clicked.connect(self.transfer_custom_to_pi)
        self.custom_image_label = QLabel(self)
        self.skeleton_image_label = QLabel(self)

        # Add Custom Mode widgets to layout (initially hidden)
        layout.addWidget(self.canvas)
        layout.addWidget(self.clear_button)
        layout.addWidget(self.process_button)
        layout.addWidget(self.skeleton_button)
        layout.addWidget(self.waypoints_button)
        layout.addWidget(self.custom_matlab_button)
        layout.addWidget(self.custom_transfer_button)
        layout.addWidget(QLabel("Original Drawing:"))
        layout.addWidget(self.custom_image_label)
        layout.addWidget(QLabel("Skeletonized Image:"))
        layout.addWidget(self.skeleton_image_label)

        # Image display group box
        self.image_group_box = QGroupBox("Processed Images")
        self.image_display_layout = QHBoxLayout()

        # Create individual vertical layouts for each image and caption
        self.pollinated_layout = QVBoxLayout()
        self.cyclegan_layout = QVBoxLayout()
        self.skeleton_layout = QVBoxLayout()
        self.stroked_layout = QVBoxLayout()

        # Add image labels and captions to their respective layouts
        self.pollinated_image_label = QLabel(self)
        self.pollinated_caption = QLabel("Pollinated Image", self)
        self.pollinated_layout.addWidget(self.pollinated_image_label)
        self.pollinated_layout.addWidget(self.pollinated_caption)

        self.cyclegan_image_label = QLabel(self)
        self.cyclegan_caption = QLabel("CycleGAN Output", self)
        self.cyclegan_layout.addWidget(self.cyclegan_image_label)
        self.cyclegan_layout.addWidget(self.cyclegan_caption)

        self.skeleton_image_label_main = QLabel(self)
        self.skeleton_caption_main = QLabel("Skeletonized Image", self)
        self.skeleton_layout.addWidget(self.skeleton_image_label_main)
        self.skeleton_layout.addWidget(self.skeleton_caption_main)

        self.stroked_image_label = QLabel(self)
        self.stroked_caption = QLabel("Stroked Image", self)
        self.stroked_layout.addWidget(self.stroked_image_label)
        self.stroked_layout.addWidget(self.stroked_caption)

        # Add the individual layouts to the main horizontal layout
        self.image_display_layout.addLayout(self.pollinated_layout)
        self.image_display_layout.addLayout(self.cyclegan_layout)
        self.image_display_layout.addLayout(self.skeleton_layout)
        self.image_display_layout.addLayout(self.stroked_layout)

        self.image_group_box.setLayout(self.image_display_layout)
        layout.addWidget(self.image_group_box)

        # Hide all mode-specific widgets initially
        self.hide_all_modes()

        # Setting the main layout
        self.setLayout(layout)
        self.setWindowTitle("Robotic Arm Control System")
        self.setMinimumSize(1000, 800)

        # Apply a neon-themed stylesheet
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #00FF00;
                font-size: 14px;
            }
            QPushButton {
                background-color: #00FF00;
                color: #000000;
                border: 2px solid #00FF00;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00CC00;
                border: 2px solid #00CC00;
            }
            QLineEdit {
                background-color: #111111;
                color: #00FF00;
                border: 2px solid #00FF00;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox {
                background-color: #111111;
                color: #00FF00;
                border: 2px solid #00FF00;
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #111111;
                color: #00FF00;
                selection-background-color: #00FF00;
                selection-color: #000000;
            }
            QLabel {
                color: #00FF00;
                font-weight: bold;
            }
            QGroupBox {
                border: 2px solid #00FF00;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                color: #00FF00;
                font-weight: bold;
            }
            QGraphicsView {
                background-color: white;
                border: 2px solid #00FF00;
                border-radius: 5px;
            }
        """)

    def hide_all_modes(self):
        """Hide all widgets for all modes."""
        self.input_field.hide()
        self.fetch_button.hide()
        self.matlab_button.hide()
        self.transfer_button.hide()  # This hides the Drawing Mode transfer button
        self.image_label.hide()
        self.pick_button.hide()
        self.reset_button.hide()
        self.canvas.hide()
        self.clear_button.hide()
        self.process_button.hide()
        self.skeleton_button.hide()
        self.waypoints_button.hide()
        self.custom_matlab_button.hide()
        # Don't hide custom_transfer_button here
        self.custom_image_label.hide()
        self.skeleton_image_label.hide()
        self.image_group_box.hide()

    def switch_mode(self):
        """Switch modes based on combo box selection."""
        self.hide_all_modes()
        selected_mode = self.mode_selector.currentText()

        if selected_mode == "Drawing Mode":
            self.input_field.show()
            self.fetch_button.show()
            self.matlab_button.show()
            self.transfer_button.show()
            self.image_label.show()

        elif selected_mode == "Pick and Place Mode":
            self.pick_button.show()
            self.reset_button.show()

        elif selected_mode == "Custom Mode":
            self.canvas.show()
            self.canvas.clear()
            self.clear_button.show()
            self.process_button.show()
            self.custom_image_label.show()
            self.skeleton_image_label.show()
            self.custom_transfer_button.show()  # Always show transfer button in Custom Mode

    def fetch_image_and_execute_pipeline(self):
        """Fetch image, process it, and save waypoints CSV."""
        object_to_draw = self.input_field.text()
        if not object_to_draw:
            QMessageBox.warning(self, "Input Error", "Please enter an object to draw.")
            return

        try:
            waypoints = fetch_image(object_to_draw)
            if waypoints is not None:
                # Display fetched image on the GUI
                img = Image.fromarray(np.array(waypoints))
                img.save("fetched_image.png")
                pixmap = QPixmap("fetched_image.png")
                self.image_label.setPixmap(pixmap)
                QMessageBox.information(self, "Success", "Image fetched and displayed!")

                # Process image and save CSV at the specified path
                processed_img = process_image(cv2.imread("fetched_image.png"))
                csv_file_path = "D:\\CIARA\\1csv_transfer\\CSV\\vs_code\\waypoints.csv"
                if os.path.exists(csv_file_path):
                    print(f"Waypoints CSV saved at: {csv_file_path}")
                    QMessageBox.information(self, "Success", "Waypoints CSV file saved!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save CSV.")

                # Display all images
                self.display_images()
            else:
                QMessageBox.warning(self, "Fetch Error", "Failed to fetch image. Try again.")
        except Exception as e:
            print(f"Error during image processing and CSV generation: {e}")
            QMessageBox.critical(self, "Error", f"Image processing failed: {e}")

    def display_images(self):
        """Display pollinated, CycleGAN, skeletonized, and stroked images."""
        pollinated_image_path = "D:\\CIARA\\1csv_transfer\\CSV\\vs_code\\polinated_image.png"
        cyclegan_image_path = "fetched_image.png"  # CycleGAN output
        skeleton_image_path = "D:\\CIARA\\final\\skeleton\\input_image_fake2.png"
        stroked_image_path = "D:\\CIARA\\1csv_transfer\\CSV\\vs_code\\reconstructed_drawing.jpg"

        # Display pollinated image
        if os.path.exists(pollinated_image_path):
            pollinated_pixmap = QPixmap(pollinated_image_path)
            self.pollinated_image_label.setPixmap(pollinated_pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            self.pollinated_image_label.show()
        else:
            print(f"Pollinated image not found at: {pollinated_image_path}")

        # Display CycleGAN output
        if os.path.exists(cyclegan_image_path):
            cyclegan_pixmap = QPixmap(cyclegan_image_path)
            self.cyclegan_image_label.setPixmap(cyclegan_pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            self.cyclegan_image_label.show()
        else:
            print(f"CycleGAN output not found at: {cyclegan_image_path}")

        # Display skeletonized image
        if os.path.exists(skeleton_image_path):
            skeleton_pixmap = QPixmap(skeleton_image_path)
            self.skeleton_image_label_main.setPixmap(skeleton_pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            self.skeleton_image_label_main.show()
        else:
            print(f"Skeleton image not found at: {skeleton_image_path}")

        # Display stroked image
        if os.path.exists(stroked_image_path):
            stroked_pixmap = QPixmap(stroked_image_path)
            self.stroked_image_label.setPixmap(stroked_pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            self.stroked_image_label.show()
        else:
            print(f"Stroked image not found at: {stroked_image_path}")

        # Show the image group box
        self.image_group_box.show()

    def run_matlab_script(self):
        """Run MATLAB script (matlab_auto.py) to generate joint_angles.csv."""
        try:
            print("Running MATLAB script to generate joint_angles.csv...")
            subprocess.run(["python", "D:\\CIARA\\matlab_auto.py"], check=True)
            joint_angles_path = "D:\\CIARA\\1csv_transfer\\CSV\\matlab\\joint_angles.csv"
            if os.path.exists(joint_angles_path):
                QMessageBox.information(self, "MATLAB Success", "joint_angles.csv generated successfully!")
            else:
                QMessageBox.warning(self, "MATLAB Error", "joint_angles.csv not found. MATLAB execution may have failed.")
        except subprocess.CalledProcessError as e:
            print(f"Error running MATLAB script: {e}")
            QMessageBox.critical(self, "MATLAB Error", "Failed to run MATLAB script.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            QMessageBox.critical(self, "MATLAB Error", f"An unexpected error occurred: {e}")

    def transfer_to_pi(self):
        """Transfer joint_angles.csv to Raspberry Pi using rasp_transfer.py."""
        try:
            print("Running rasp_transfer.py to transfer joint_angles.csv to Raspberry Pi...")
            subprocess.run(["python", "D:\\CIARA\\rasp_transfer.py"], check=True)
            QMessageBox.information(self, "Transfer Successful", "CSV file successfully transferred to Raspberry Pi!")
            self.close()  # Close the GUI after successful transfer
        except subprocess.CalledProcessError as e:
            print(f"Error transferring file to Raspberry Pi: {e}")
            QMessageBox.critical(self, "Transfer Error", "Failed to transfer CSV to Raspberry Pi.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def run_pick_and_place(self):
        QMessageBox.information(self, "Pick and Place Mode", "Pick and Place task executed!")

    def reset_arm(self):
        QMessageBox.information(self, "Pick and Place Mode", "Robotic Arm reset to initial position!")

    def process_custom_drawing(self):
        """Save the custom drawing to the specified directory."""
        try:
            # Create directory if it doesn't exist
            custom_dir = "D:\\CIARA\\1csv_transfer\\CSV\\vscode_custom"
            os.makedirs(custom_dir, exist_ok=True)
            
            # Save the drawing
            image = self.canvas.get_image()
            self.custom_image_path = os.path.join(custom_dir, "custom_drawing.png")
            image.save(self.custom_image_path)
            
            # Display the saved image
            pixmap = QPixmap(self.custom_image_path)
            self.custom_image_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))
            
            QMessageBox.information(self, "Success", f"Drawing saved to {self.custom_image_path}")
            
            # Enable the next step button
            self.skeleton_button.show()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save custom drawing: {e}")

    def generate_skeleton(self):
        """Generate skeleton image using new_wap1.py without verification"""
        if not self.custom_image_path:
            QMessageBox.warning(self, "Error", "Please process the drawing first.")
            return
            
        try:
            # Run the skeleton generation script
            subprocess.run(["python", "D:\\CIARA\\new_wap1.py", self.custom_image_path], check=True)
            
            # Assume success and proceed
            QMessageBox.information(self, "Success", "Skeleton generation completed!")
            self.waypoints_button.show()
            
            # Store the expected skeleton path for next step
            custom_dir = os.path.dirname(self.custom_image_path)
            self.skeleton_path = os.path.join(custom_dir, "skeleton.png")
                
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Failed to generate skeleton: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def generate_waypoints(self):
        """Generate waypoints using stroke_arm4.py without verification"""
        try:
            if not hasattr(self, 'skeleton_path'):
                QMessageBox.warning(self, "Error", "Please generate skeleton first.")
                return
                
            # Run the waypoint generation script  
            subprocess.run(["python", "D:\\CIARA\\stroke_arm4.py", self.skeleton_path], check=True)
            
            # Assume success and proceed
            QMessageBox.information(self, "Success", "Waypoints generation completed!")
            self.custom_matlab_button.show()
                
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Failed to generate waypoints: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    def run_custom_matlab_script(self):
        """Run custom MATLAB script for the custom drawing."""
        try:
            print("Running custom MATLAB script...")
            subprocess.run(["python", "D:\\CIARA\\matlab_auto1.py"], check=True)
            joint_angles_path = "D:\\CIARA\\1csv_transfer\\CSV\\vscode_custom\\joint_angles.csv"
            if os.path.exists(joint_angles_path):
                QMessageBox.information(self, "MATLAB Success", "Custom joint_angles.csv generated successfully!")
                self.custom_transfer_button.show()
            else:
                QMessageBox.warning(self, "MATLAB Error", "joint_angles.csv not found. MATLAB execution may have failed.")
        except subprocess.CalledProcessError as e:
            print(f"Error running MATLAB script: {e}")
            QMessageBox.critical(self, "MATLAB Error", "Failed to run MATLAB script.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            QMessageBox.critical(self, "MATLAB Error", f"An unexpected error occurred: {e}")

    def transfer_custom_to_pi(self):
        """Transfer custom joint_angles.csv to Raspberry Pi."""
        try:
            print("Transferring custom CSV to Raspberry Pi...")
            subprocess.run(["python", "D:\\CIARA\\rasp_transfer.py"], check=True)
            QMessageBox.information(self, "Transfer Successful", "Custom CSV file successfully transferred to Raspberry Pi!")
        except subprocess.CalledProcessError as e:
            print(f"Error transferring file to Raspberry Pi: {e}")
            QMessageBox.critical(self, "Transfer Error", "Failed to transfer CSV to Raspberry Pi.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())