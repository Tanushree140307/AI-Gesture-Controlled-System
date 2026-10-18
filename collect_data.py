
import cv2
import mediapipe as mp
import csv
import os
import time

camera=cv2.VideoCapture(0)

mp_hands=mp.solutions.hands
mp_draw=mp.solutions.drawing_utils

hands=mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

file_name="gesture_data.csv"
target_samples=300
collecting=False
label=None
sample_count=0
last_save_time=0
save_interval=0.05

# Create CSV if it does not exist
if not os.path.exists(file_name):
    with open(file_name,"w",newline="") as file:
        writer=csv.writer(file)
        columns=[]

        for i in range(21):
            columns.extend([
                f"x{i}",
                f"y{i}",
                f"z{i}"
            ])

        columns.append("label")
        writer.writerow(columns)


# Instructions
print("Press 1 for THUMBS_UP")
print("Press 2 for FIST")
print("Press 3 for OPEN_PALM")
print("Press 4 for INDEX_FINGER")
print("Press 5 for THREE_FINGERS")
print("Press Q to quit")


while True:

    success,frame=camera.read()

    if not success:
        print("Camera access failed")
        break

    frame=cv2.flip(frame,1)

    rgb_frame=cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results=hands.process(rgb_frame)


    # Draw detected hand landmarks
    if results.multi_hand_landmarks:

        for hand_landmarks in results.multi_hand_landmarks:

            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )


    key=cv2.waitKey(1) & 0xFF

    if key==ord("q"):
        break


    # Select gesture
    if key in [
        ord("1"),
        ord("2"),
        ord("3"),
        ord("4"),
        ord("5")
    ]:

        if key==ord("1"):
            label="THUMBS_UP"

        elif key==ord("2"):
            label="FIST"

        elif key==ord("3"):
            label="OPEN_PALM"

        elif key==ord("4"):
            label="INDEX_FINGER"

        else:
            label="THREE_FINGERS"

        collecting=True
        sample_count=0
        last_save_time=0

        print(f"Collecting {label}...")


    # Collect landmark samples
    if collecting and results.multi_hand_landmarks:

        current_time=time.time()

        if current_time-last_save_time>=save_interval:

            hand_landmarks=results.multi_hand_landmarks[0]

            row=[]

            for landmark in hand_landmarks.landmark:

                row.extend([
                    landmark.x,
                    landmark.y,
                    landmark.z
                ])

            row.append(label)

            with open(file_name,"a",newline="") as file:

                writer=csv.writer(file)
                writer.writerow(row)

            sample_count+=1
            last_save_time=current_time

            print(
                f"{label}: "
                f"{sample_count}/{target_samples}"
            )

            if sample_count>=target_samples:

                collecting=False

                print(f"{label} collection complete!")
                print("Press another number for the next gesture.")


    # Display collection status
    if collecting:
        status=f"Collecting: {label} {sample_count}/{target_samples}"
    else:
        status="Ready - Press 1, 2, 3, 4 or 5"

    cv2.putText(
        frame,
        status,
        (10,30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0,255,0),
        2
    )

    cv2.imshow("Gesture Data Collection",frame)


camera.release()
hands.close()
cv2.destroyAllWindows()

print("Data collection closed.")
