import os
import cv2
import mediapipe as mp
from datetime import datetime
from siren_player import play_siren
from location_tracker import get_live_location
from email_alert import send_email

TO_EMAIL = os.getenv("TO_EMAIL")
print("📥 Loaded TO_EMAIL:", TO_EMAIL)

mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands()
face_detection = mp_face.FaceDetection(min_detection_confidence=0.5)

gesture_count = 0
was_closed = False
capture_dir = "captures"
os.makedirs(capture_dir, exist_ok=True)

cap = cv2.VideoCapture(0)

def is_hand_closed(landmarks):
    tip_ids = [8, 12, 16, 20]
    closed_fingers = 0
    for tip_id in tip_ids:
        if landmarks[tip_id].y > landmarks[tip_id - 2].y:
            closed_fingers += 1
    return closed_fingers >= 3

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    hand_results = hands.process(imgRGB)
    face_results = face_detection.process(imgRGB)

    face_present = face_results.detections is not None
    hand_present = hand_results.multi_hand_landmarks is not None

    if face_present:
        for detection in face_results.detections:
            bboxC = detection.location_data.relative_bounding_box
            x = int(bboxC.xmin * w)
            y = int(bboxC.ymin * h)
            width = int(bboxC.width * w)
            height = int(bboxC.height * h)

            color = (0, 255, 255)
            thickness = 2
            corner_len = 20

            cv2.line(frame, (x, y), (x + corner_len, y), color, thickness)
            cv2.line(frame, (x, y), (x, y + corner_len), color, thickness)
            cv2.line(frame, (x + width, y), (x + width - corner_len, y), color, thickness)
            cv2.line(frame, (x + width, y), (x + width, y + corner_len), color, thickness)
            cv2.line(frame, (x, y + height), (x + corner_len, y + height), color, thickness)
            cv2.line(frame, (x, y + height), (x, y + height - corner_len), color, thickness)
            cv2.line(frame, (x + width, y + height), (x + width - corner_len, y + height), color, thickness)
            cv2.line(frame, (x + width, y + height), (x + width, y + height - corner_len), color, thickness)

            label = "Face Tracking"
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(frame, (x, y - th - 10), (x + tw + 10, y), (0, 255, 255), -1)
            cv2.putText(frame, label, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    if face_present and hand_present:
        for handLms in hand_results.multi_hand_landmarks:
            x_vals = [int(lm.x * w) for lm in handLms.landmark]
            y_vals = [int(lm.y * h) for lm in handLms.landmark]
            x_min, x_max = min(x_vals), max(x_vals)
            y_min, y_max = min(y_vals), max(y_vals)

            cv2.rectangle(frame, (x_min - 20, y_min - 20), (x_max + 20, y_max + 20), (0, 255, 0), 2)
            mp_drawing.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)

            if is_hand_closed(handLms.landmark):
                if not was_closed:
                    gesture_count += 1
                    print(f"✊ Closed Hand Detected ({gesture_count}/3)")
                    was_closed = True

                    if gesture_count == 3:
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        img_path = f"{capture_dir}/gesture_{ts}.jpg"
                        cv2.imwrite(img_path, frame)
                        print(f"📸 Image captured at {img_path}")

                        play_siren()
                        location = get_live_location()
                        if location and TO_EMAIL:
                            print(f"📤 Sending email to: {TO_EMAIL}")
                            send_email(TO_EMAIL, location)
                        gesture_count = 0
            else:
                was_closed = False

   
    cv2.putText(frame, f"HELP HAND x{gesture_count}", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

    cv2.imshow("Gesture + Face Detection", frame)
    if cv2.waitKey(10) == 27:
        break

cap.release()
cv2.destroyAllWindows()
