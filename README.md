# AI-Powered Gesture-Controlled Computer System

A machine learning-based desktop application that enables users to control computer operations using hand gestures captured through a webcam.

The system uses **MediaPipe** for hand landmark detection, a **Random Forest classifier** for gesture recognition, and **PyAutoGUI** for computer interaction.

## Features

- **Real-Time Hand Tracking:** Detects hand landmarks using a webcam.
- **ML-Based Gesture Recognition:** Recognizes predefined gestures using a trained Random Forest model.
- **PowerPoint Navigation:** Move to the next or previous slide using hand gestures.
- **Media Control:** Play or pause media using an open-palm gesture.
- **Volume Control:** Adjust the system volume using the index finger.
- **Screenshot Capture:** Capture the active application window using a three-finger gesture.
- **Webcam Display Modes:** Choose between always-visible mode and application-focused visibility mode.

## Technologies Used

- Python
- OpenCV
- MediaPipe
- NumPy
- Pandas
- Scikit-learn
- PyAutoGUI
- PyGetWindow
- PyWin32
- PyCAW
- Joblib
- PyInstaller

## Gesture Controls

| Hand Gesture | Action |
|---|---|
| 👍 Thumbs Up | Next PowerPoint slide / Right Arrow |
| ✊ Fist | Previous PowerPoint slide / Left Arrow |
| 🖐️ Open Palm | Play / Pause media |
| ☝️ Index Finger | Volume adjustment |
| Three Fingers | Capture screenshot |

*Actions may depend on the active application and the configured gesture-control logic.*

## Project Structure

```text
AI-Gesture-Controlled-System/
│
├── control_computer.py
├── collect_data.py
├── train_model.py
├── predict_gesture.py
├── gesture_model.pkl
├── requirements.txt
├── AI Gesture Controller.spec
├── .gitignore
└── README.md
```

## Requirements

- Windows operating system
- Python 3.12.10 recommended
- Webcam
- Git
- Required Python packages listed in `requirements.txt`

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Tanushree140307/AI-Gesture-Controlled-System.git
cd AI-Gesture-Controlled-System
```


### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

For Windows Command Prompt:

```cmd
venv\Scripts\activate.bat
```

For PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run the application

```bash
python control_computer.py
```

Choose the webcam display mode when prompted and follow the instructions displayed by the application.

**Note:** Keep `gesture_model.pkl` in the expected project directory so the application can load the trained model.

## Machine Learning Workflow

1. Capture hand gesture samples using the data collection script.
2. Extract hand landmark coordinates from the collected samples.
3. Train a Random Forest classifier using the prepared gesture dataset.
4. Save the trained model as `gesture_model.pkl`.
5. Predict gestures in real time using webcam input.
6. Execute the corresponding computer action based on the recognized gesture.

The model can be retrained using the training script when suitable training data is available.

## Building a Windows Executable

The project includes a PyInstaller specification file for packaging the application as a Windows executable.

With the required dependencies installed, run:

```bash
python -m PyInstaller --clean "AI Gesture Controller.spec"
```

The generated application is typically available inside the `dist` directory. Test the packaged application before distributing it.

**Applications**

Hands-free computer interaction

Presentation slide navigation

Media playback control

Accessibility-oriented interaction experiments

Machine learning and computer vision demonstrations

**Future Enhancements**

Support for additional hand gestures

Improved gesture recognition accuracy

Customizable gesture-to-action mapping

Better gesture smoothing and response time

Expanded application integration

# Author

Tanushree D J

Computer Science and Engineering Student

# License

Choose an appropriate open-source license before distributing this project for reuse. Until a license is added, do not assume that others have permission to reuse or redistribute the code.
