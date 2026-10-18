
import cv2
import mediapipe as mp
import joblib
import pandas as pd

model=joblib.load("gesture_model.pkl")

camera=cv2.VideoCapture(0)

mp_hands=mp.solutions.hands
mp_draw=mp.solutions.drawing_utils

hands=mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

while True:
    success,frame=camera.read()

    if not success:
        print("Camera access failed")
        break

    frame=cv2.flip(frame,1)

    rgb_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

    results=hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            features=[]

            for landmark in hand_landmarks.landmark:
                features.extend([
                    landmark.x,
                    landmark.y,
                    landmark.z
                ])

            columns=[]

            for i in range(21):
                columns.extend([
                    f"x{i}",
                    f"y{i}",
                    f"z{i}"
                ])

            input_data=pd.DataFrame([features],columns=columns)

            prediction=model.predict(input_data)[0]

            cv2.putText(
                frame,
                prediction,
                (20,50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0,255,0),
                2
            )

    cv2.imshow("Real-Time Gesture Prediction",frame)

    if cv2.waitKey(1) & 0xFF==ord("q"):
        break

camera.release()
hands.close()
cv2.destroyAllWindows()
