# CIARA - 4-DOF Articulated Drawing Arm

CIARA is a 4-DOF articulated robotic arm that converts text prompts into hand-drawn sketches. It combines AI-based image generation, skeletonization, inverse kinematics, and robotic control to create drawings on paper.

---

## What's Inside

This repository contains:

* **URDF Model**: Used in MATLAB for solving inverse kinematics.
* **CycleGAN Model**: Adapted from Ran Yi's Portrait Drawing GAN.
* **Custom Skeletonization & Line Stroke Algorithm**: Converts sketches into waypoints.
* **MATLAB Code**: Solves inverse kinematics using the URDF model.
* **Raspberry Pi Code**: Controls the robotic arm servos using joint angles.
* **Simple GUI**: One-click solution to process images and command the arm.

---

## How It Works

1. **Text Prompt Input**
   The user enters a text prompt (e.g., "cat").

2. **Image Generation**
   An image is fetched using Pollinations AI based on the prompt.

3. **Sketch Simplification**
   The image is passed through a CycleGAN model to create a sketch.

4. **Skeletonization**
   The sketch is converted into a thin skeleton outline.

5. **Line Stroke Planning**
   Waypoints are generated using a custom stroke algorithm and saved to a `.csv` file.

6. **Inverse Kinematics in MATLAB**
   The CSV file is used with the custom URDF model to compute joint angles.

7. **Drawing Execution**
   The joint angles are sent to a Raspberry Pi, which commands the robot to draw.

---

## Note on the GAN Model

The CycleGAN model used in this project is based on the *Unpaired-Portrait-Drawing* repository developed by Ran Yi et al. This model is not authored by the CIARA development team. It is included only to facilitate project replication and experimentation. Users are encouraged to obtain the original implementation from the authors' repository and provide appropriate credit when using it in derivative works.

Original repository: https://github.com/yiranran/Unpaired-Portrait-Drawing

---

## Installation

Clone the repository:

```bash
git clone https://github.com/ReXeeDD/CIARA.git
```

---

## Running the Project

Launch the GUI:

```bash
python 1gui_app.py
# or
python gui_app.py
```

**Note:** The GUI was tested during project development and may require minor adjustments depending on the execution environment.

---

## File Structure

| File / Folder                   | Description                                             |
| ------------------------------- | ------------------------------------------------------- |
| `gui_app.py` / `1gui_app.py`    | GUI to run the complete pipeline                        |
| `testomg2.py`                   | Main script for CycleGAN inference                      |
| `URDF AND MODEL/CIARAFINAL/...` | URDF model used in MATLAB inverse kinematics solver     |
| `arm27.m`, `arm26.m`, `arm24.m` | MATLAB scripts for inverse kinematics                   |
| `raspberrypi_code.py`           | Code for controlling the robotic arm using Raspberry Pi |

---

## Modifying the Project

* To modify CycleGAN integration, edit:

  * `testomg2.py`

* To understand how the modules interact, refer to:

  * `gui_app.py`

The codebase is modular and contains inline comments to aid understanding and customization.

---

## Authors

This project was developed by a team of students as part of an academic mini-project.

---

## Citation

If you use this work in your research, please cite:

```bibtex
@INPROCEEDINGS{11349080,
  author={Babu, Tony Basil and Thomas, Albin and Chacko, Alex and Shahsad, Muhammed and Abraham, Nelsa and C. D., Anil Kumar},
  booktitle={2025 International Conference on Robotics and Mechatronics (ICRM)},
  title={CIARA: Integrating AI in a Low-Cost Articulated Robotic Arm for Image-to-Sketch Reproduction},
  year={2025},
  pages={1--5},
  doi={10.1109/ICRM66809.2025.11349080}
}
```

### References

[1] T. B. Babu, A. Thomas, A. Chacko, M. Shahsad, N. Abraham, and A. K. C. D., “CIARA: Integrating AI in a Low-Cost Articulated Robotic Arm for Image-to-Sketch Reproduction,” in *Proceedings of the 2025 International Conference on Robotics and Mechatronics (ICRM)*, 2025, pp. 1–5, doi:10.1109/ICRM66809.2025.11349080.

[2] Ran Yi, Yong-Jin Liu, Yu-Kun Lai, and Paul L. Rosin, *Unpaired-Portrait-Drawing*, GitHub repository. Available: https://github.com/yiranran/Unpaired-Portrait-Drawing

---

## License

This project is intended for educational and research purposes. Please ensure that appropriate credit is given to the original authors of any third-party models, datasets, or software components used within this project.
