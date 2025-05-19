import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox
from PyQt5.QtGui import QPixmap
from PIL import Image
import cv2
import numpy as np
import os
import subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Unpaired_Portrait_Drawing.testomg2 import fetch_image, process_image, display_generated_images_and_select, call_additional_scripts


# Importing your functions (assuming they are in a separate module)
from your_pipeline import fetch_image, process_image, display_generated_images_and_select, call_additional_scripts

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Main layout
        layout = QVBoxLayout()

        # Input for object name
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("Enter the object you want to draw")
        layout.addWidget(self.input_field)

        # Button to fetch image from Pollinations API
        self.fetch_button = QPushButton("Fetch Image", self)
        self.fetch_button.clicked.connect(self.fetch_image_from_api)
        layout.addWidget(self.fetch_button)

        # Label to show fetched image
        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        # Button to process the image using CycleGAN
        self.process_button = QPushButton("Process Image (Apply CycleGAN)", self)
        self.process_button.clicked.connect(self.process_image_and_apply_cyclegan)
        layout.addWidget(self.process_button)

        # Button to run additional drawing scripts
        self.run_arm_button = QPushButton("Run Robotic Arm Drawing", self)
        self.run_arm_button.clicked.connect(self.run_drawing_scripts)
        layout.addWidget(self.run_arm_button)

        # Setting the layout
        self.setLayout(layout)
        self.setWindowTitle("Image Processing and Robotic Drawing Pipeline")

    def fetch_image_from_api(self):
        """Fetch image from Pollinations AI based on user input."""
        object_to_draw = self.input_field.text()
        if not object_to_draw:
            QMessageBox.warning(self, "Input Error", "Please enter an object to draw.")
            return

        waypoints = fetch_image(object_to_draw)
        if waypoints:
            # Display fetched image on the GUI
            img = Image.fromarray(np.array(waypoints))
            img.save("fetched_image.png")
            pixmap = QPixmap("fetched_image.png")
            self.image_label.setPixmap(pixmap)
            QMessageBox.information(self, "Success", "Image fetched and displayed!")
        else:
            QMessageBox.warning(self, "Fetch Error", "Failed to fetch image. Try again.")

    def process_image_and_apply_cyclegan(self):
        """Process the image using CycleGAN and display styled options."""
        if not os.path.exists("fetched_image.png"):
            QMessageBox.warning(self, "Error", "Please fetch an image first.")
            return

        processed_img = process_image(cv2.imread("fetched_image.png"))
        if processed_img is None:
            QMessageBox.warning(self, "Error", "Image processing failed.")
        else:
            QMessageBox.information(self, "Processing Done", "CycleGAN has processed the image!")

    def run_drawing_scripts(self):
        """Run the final drawing scripts for the robotic arm."""
        try:
            call_additional_scripts()
            QMessageBox.information(self, "Drawing Done", "Robotic arm drawing completed!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run drawing scripts: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
