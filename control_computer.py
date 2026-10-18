
import cv2
import mediapipe as mp
import joblib
import pandas as pd
import pyautogui
import pygetwindow as gw
import win32com.client
import win32gui
import win32con
import time
from pathlib import Path
from datetime import datetime
from collections import deque, Counter
from pycaw.pycaw import AudioUtilities
import sys

if getattr(sys,"frozen",False):
    base_path=Path(sys._MEIPASS)
else:
    base_path=Path(__file__).resolve().parent

model_path=base_path/"gesture_model.pkl"
model=joblib.load(model_path)

pyautogui.PAUSE=0

window_name="Gesture Computer Control"

screen_width,screen_height=pyautogui.size()


# Select webcam mode BEFORE initializing audio
print("Choose webcam mode:")
print("1 - Always Visible")
print("2 - Visible When Using This App")

mode=input("Enter 1 or 2: ").strip()

while mode not in ["1","2"]:
    mode=input("Invalid choice. Enter 1 or 2: ").strip()

show_camera=(mode=="1")

# Mode 2: remember the top-level window from which this program was launched.
# In VS Code's integrated terminal this is normally the VS Code window;
# in Command Prompt it is the Command Prompt window.
launch_app_hwnd=win32gui.GetForegroundWindow()
launch_root_hwnd=(
    win32gui.GetAncestor(launch_app_hwnd,win32con.GA_ROOT)
    if launch_app_hwnd else 0
) or launch_app_hwnd


# Initialize Windows volume control
try:
    speakers=AudioUtilities.GetSpeakers()
    volume_control=speakers.EndpointVolume
except Exception as error:
    print("Volume initialization error:",error)
    print("Check that pycaw and comtypes are installed.")
    raise SystemExit


# Volume settings
volume_anchor_y=None
volume_threshold=0.025
volume_step=0.04


# Screenshot folder
screenshot_folder=Path.home()/"Pictures"/"GestureShots"
screenshot_folder.mkdir(parents=True,exist_ok=True)


# Window tracking
camera_hwnd=None
last_non_camera_hwnd=None


def perform_directional_action(direction):
    """Use PowerPoint slideshow controls when available; otherwise control the active app."""
    try:
        app=win32com.client.GetActiveObject("PowerPoint.Application")
        if app.SlideShowWindows.Count > 0:
            view=app.SlideShowWindows(1).View
            if direction == "next":
                view.Next()
            else:
                view.Previous()
            return True, "PowerPoint - Next slide" if direction == "next" else "PowerPoint - Previous slide"
    except Exception:
        pass

    # No running PowerPoint slideshow: send the key to the active application.
    # In YouTube/browser, Right/Left Arrow normally skips 5 seconds when the player is focused.
    key="right" if direction == "next" else "left"
    pyautogui.press(key)
    return True, "Active app - Forward" if direction == "next" else "Active app - Rewind"


def save_active_window_screenshot(hwnd):
    global camera_hwnd

    if hwnd is None or not win32gui.IsWindow(hwnd):
        print("No application window found.")
        return False

    if hwnd==camera_hwnd:
        print("Cannot capture webcam window.")
        return False

    try:
        client_rect=win32gui.GetClientRect(hwnd)

        top_left=win32gui.ClientToScreen(
            hwnd,
            (client_rect[0],client_rect[1])
        )

        bottom_right=win32gui.ClientToScreen(
            hwnd,
            (client_rect[2],client_rect[3])
        )

        left,top=top_left
        right,bottom=bottom_right

        left=max(0,left)
        top=max(0,top)
        right=min(screen_width,right)
        bottom=min(screen_height,bottom)

        width=right-left
        height=bottom-top

        if width<=0 or height<=0:
            print("Application window is not visible.")
            return False

        camera_visible=(
            camera_hwnd is not None
            and win32gui.IsWindow(camera_hwnd)
            and win32gui.IsWindowVisible(camera_hwnd)
        )

        if camera_visible:
            win32gui.ShowWindow(camera_hwnd,win32con.SW_HIDE)
            time.sleep(0.2)

        try:
            screenshot=pyautogui.screenshot(
                region=(left,top,width,height)
            )
        finally:
            if camera_visible:
                win32gui.ShowWindow(
                    camera_hwnd,
                    win32con.SW_SHOWNOACTIVATE
                )

        timestamp=datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        file_path=screenshot_folder/f"screenshot_{timestamp}.png"

        screenshot.save(file_path)

        print("Screenshot saved:",file_path)
        return True

    except Exception as error:
        print("Screenshot error:",error)
        return False


# Open webcam
camera=cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH,640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

if not camera.isOpened():
    print("Camera access failed.")
    raise SystemExit


# Initialize MediaPipe
mp_hands=mp.solutions.hands
mp_draw=mp.solutions.drawing_utils

hands=mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)


# Prepare model input columns
columns=[]

for i in range(21):
    columns.extend([f"x{i}",f"y{i}",f"z{i}"])


# Gesture tracking
gesture_history=deque(maxlen=5)

repeat_interval=1.5
last_action_time=0
active_gesture=None

open_palm_triggered=False
screenshot_triggered=False


# Create webcam window
cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)

print("Gesture control started. Press Q to quit in foreground mode.")

camera_hwnd=win32gui.FindWindow(None,window_name)

if show_camera and camera_hwnd:
    win32gui.SetWindowPos(
        camera_hwnd,
        win32con.HWND_TOPMOST,
        0,0,0,0,
        win32con.SWP_NOMOVE |
        win32con.SWP_NOSIZE |
        win32con.SWP_SHOWWINDOW
    )



if show_camera:
    pass
else:
    pass


try:
    while True:

        success,frame=camera.read()

        if not success:
            print("Camera access failed.")
            break

        frame=cv2.flip(frame,1)

        # Remember the last active non-webcam application
        active_hwnd=win32gui.GetForegroundWindow()

        if (
            active_hwnd
            and active_hwnd!=camera_hwnd
            and win32gui.IsWindow(active_hwnd)
        ):
            active_title=win32gui.GetWindowText(active_hwnd).strip()

            if active_title:
                last_non_camera_hwnd=active_hwnd

        rgb_frame=cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results=hands.process(rgb_frame)

        stable_gesture=None
        current_landmarks=None

        if results.multi_hand_landmarks:

            hand_landmarks=results.multi_hand_landmarks[0]
            current_landmarks=hand_landmarks.landmark

            if show_camera:
                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

            features=[]

            for landmark in current_landmarks:
                features.extend([
                    landmark.x,
                    landmark.y,
                    landmark.z
                ])

            input_data=pd.DataFrame(
                [features],
                columns=columns
            )

            prediction=model.predict(input_data)[0]
            gesture_history.append(prediction)

        else:
            gesture_history.clear()
            active_gesture=None
            open_palm_triggered=False
            screenshot_triggered=False
            volume_anchor_y=None


        # Stabilize predictions
        if len(gesture_history)>=3:

            counts=Counter(gesture_history)
            gesture,count=counts.most_common(1)[0]

            if count>=3:
                stable_gesture=gesture


        current_time=time.time()
        action_text=stable_gesture or "Detecting gesture..."


        # INDEX_FINGER: volume control
        if stable_gesture=="INDEX_FINGER" and current_landmarks:

            active_gesture=None
            open_palm_triggered=False
            screenshot_triggered=False

            current_y=current_landmarks[8].y

            if volume_anchor_y is None:
                volume_anchor_y=current_y

            vertical_movement=current_y-volume_anchor_y

            if abs(vertical_movement)>=volume_threshold:

                current_volume=volume_control.GetMasterVolumeLevelScalar()

                if vertical_movement<0:
                    new_volume=min(1.0,current_volume+volume_step)
                    action_text="INDEX_FINGER - Volume Up"
                else:
                    new_volume=max(0.0,current_volume-volume_step)
                    action_text="INDEX_FINGER - Volume Down"

                volume_control.SetMasterVolumeLevelScalar(
                    new_volume,
                    None
                )

                volume_anchor_y=current_y


            else:
                action_text="INDEX_FINGER - Volume Control"

        elif stable_gesture!="INDEX_FINGER":
            volume_anchor_y=None


        # Reset slide gesture when another gesture appears
        if stable_gesture not in ["THUMBS_UP","FIST"]:
            active_gesture=None


        # THUMBS_UP / FIST: PowerPoint if slideshow is running; otherwise active app
        if stable_gesture in ["THUMBS_UP","FIST"]:

            gesture_changed=(stable_gesture!=active_gesture)
            repeat_due=(current_time-last_action_time>=repeat_interval)

            if gesture_changed or repeat_due:
                if stable_gesture=="THUMBS_UP":
                    success, message=perform_directional_action("next")
                else:
                    success, message=perform_directional_action("previous")

                action_text=message
                last_action_time=time.time()
                active_gesture=stable_gesture


        # OPEN_PALM: media Play/Pause once per hold
        if stable_gesture=="OPEN_PALM":

            active_gesture=None
            screenshot_triggered=False
            action_text="OPEN_PALM - Play/Pause"

            if not open_palm_triggered:
                pyautogui.press("playpause")
                open_palm_triggered=True

        elif stable_gesture is not None:
            open_palm_triggered=False


        # THREE_FINGERS: screenshot once per hold
        if stable_gesture=="THREE_FINGERS":

            active_gesture=None
            open_palm_triggered=False
            action_text="THREE_FINGERS - Screenshot"

            if not screenshot_triggered:
                screenshot_triggered=True

                if save_active_window_screenshot(last_non_camera_hwnd):
                    pass
                else:
                    print("Click the application window before showing three fingers.")

        elif stable_gesture is not None:
            screenshot_triggered=False


        # Display webcam preview
        if show_camera:

            cv2.putText(
                frame,
                action_text,
                (10,35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,255,0),
                2
            )

            cv2.imshow(window_name,frame)

            if cv2.waitKey(1) & 0xFF==ord("q"):
                break

        else:

            cv2.imshow(window_name,frame)
            cv2.waitKey(1)

            # Re-find the OpenCV window in case Windows recreated its handle.
            found_hwnd=win32gui.FindWindow(None,window_name)
            if found_hwnd:
                camera_hwnd=found_hwnd

            # Mode 2: show the webcam only while the app/window that launched
            # this script is the foreground top-level window.
            active_hwnd=win32gui.GetForegroundWindow()
            active_root_hwnd=(
                win32gui.GetAncestor(active_hwnd,win32con.GA_ROOT)
                if active_hwnd else 0
            ) or active_hwnd
            launch_app_is_active=(
                launch_root_hwnd != 0
                and active_root_hwnd == launch_root_hwnd
            )

            if camera_hwnd and win32gui.IsWindow(camera_hwnd):
                camera_is_visible=bool(win32gui.IsWindowVisible(camera_hwnd))

                if launch_app_is_active:
                    # Re-show and raise the preview without stealing keyboard focus.
                    if not camera_is_visible:
                        win32gui.ShowWindow(camera_hwnd,win32con.SW_SHOWNOACTIVATE)

                    win32gui.SetWindowPos(
                        camera_hwnd,
                        win32con.HWND_TOP,
                        0,0,0,0,
                        win32con.SWP_NOMOVE |
                        win32con.SWP_NOSIZE |
                        win32con.SWP_NOACTIVATE |
                        win32con.SWP_SHOWWINDOW
                    )
                elif camera_is_visible:
                    win32gui.ShowWindow(camera_hwnd,win32con.SW_HIDE)

            time.sleep(0.03)


except KeyboardInterrupt:
    print("\nGesture control stopped.")

finally:

    camera.release()
    hands.close()
    cv2.destroyAllWindows()

