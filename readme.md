# 🤖 CIARA - 4-DOF Articulated Drawing Arm

CIARA is a 4-DOF articulated robotic arm that converts text prompts into hand-drawn sketches. It combines AI-based image generation, skeletonization, inverse kinematics, and robotic control to create drawings on paper.

---

## 🛠️ What's Inside

This repository contains:

- 🤖 **URDF Model**: Used in MATLAB for solving inverse kinematics.
- 🎨 **CycleGAN Model**: Adapted from [Ran Yi's Portrait Drawing GAN](https://github.com/yiranran/Unpaired-Portrait-Drawing).
- 🧠 **Custom Skeletonization & Line Stroke Algorithm**: Converts sketches into waypoints.
- 🧮 **MATLAB Code**: Solves inverse kinematics using the URDF model.
- 🍓 **Raspberry Pi Code**: Controls the robotic arm servos using joint angles.
- 🖼️ **Simple GUI**: One-click solution to process images and command the arm.

---

## ⚙️ How It Works

1. **Text Prompt Input**  
   The user enters a text prompt (e.g., "cat").

2. **Image Generation**  
   An image is fetched using Polination AI based on the prompt.

3. **Sketch Simplification**  
   The image is passed through a CycleGAN model to create a sketch.

4. **Skeletonization**  
   The sketch is converted into a thin skeleton outline.

5. **Line Stroke Planning**  
   Waypoints are generated using a custom stroke algorithm and saved to a `.csv`.

6. **Inverse Kinematics in MATLAB**  
   The CSV is used with our custom URDF model to compute joint angles.

7. **Drawing Execution**  
   The joint angles are sent to a Raspberry Pi, which commands the robot to draw.

---

## ⚠️ Note on GAN Model

The CycleGAN model (`Unpaired-Portrait-Drawing`) by Ran Yi is **not authored** by us. We uploaded it temporarily due to storage constraints.  
👉 [Download the original model here](https://github.com/yiranran/Unpaired-Portrait-Drawing) for proper usage and credit.

---

## 🔧 Installation

Clone the repository:
```bash
git clone https://github.com/ReXeeDD/CIARA.git
```

---

## 🚀 Running the Project

Launch the GUI:
```bash
python 1gui_app.py
# or
python gui_app.py
```

> **Note:** The GUI was tested during our project development and may require minor adjustments at runtime.

---

## 📂 File Structure

| File / Folder                     | Description                                  |
|----------------------------------|----------------------------------------------|
| `gui_app.py` / `1gui_app.py`     | GUI to run full pipeline                     |
| `testomg2.py`                    | Main script for CycleGAN inference           |
| `URDF AND MODEL/CIARAFINAL/...`  | URDF model used in MATLAB IK solver          |
| `arm27.m`, `arm26.m`, `arm24.m` | MATLAB scripts for IK                        |
| `raspberrypi_code.py`           | Code for running the robotic arm on the Pi   |

---

## 📌 Modifying the Project

- To tweak CycleGAN integration, edit:  
  `testomg2.py`

- To understand how each module is linked, see:  
  `gui_app.py` – it’s well-commented and modular.

---

## 👨‍💻 Authors

This project was developed by a small team of students as part of a mini project.

---

## 📜 License

This project is intended for educational use.  
Please credit the original authors for third-party models.

