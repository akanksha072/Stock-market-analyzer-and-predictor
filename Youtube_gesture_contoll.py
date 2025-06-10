import cv2
import mediapipe as mp
import time
import pyautogui
import math

class HandDetector:
    def __init__(self, detectionCon=0.7, trackCon=0.7):
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=detectionCon,
            min_tracking_confidence=trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None

    def findHands(self, img):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLms, mp.solutions.hands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img):
        lmList = []
        if self.results.multi_hand_landmarks:
            hand = self.results.multi_hand_landmarks[0]
            for id, lm in enumerate(hand.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((id, cx, cy))
        return lmList

def count_fingers(lmList):
    if not lmList or len(lmList) < 21:
        return 0

    fingers = []

    # Thumb
    if lmList[4][1] > lmList[3][1]:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers
    for tip in [8, 12, 16, 20]:
        if lmList[tip][2] < lmList[tip - 2][2]:
            fingers.append(1)
        else:
            fingers.append(0)

    return sum(fingers)

def volume_control(lmList, prev_dist):
    x1, y1 = lmList[4][1], lmList[4][2]  # Thumb
    x2, y2 = lmList[8][1], lmList[8][2]  # Index
    length = math.hypot(x2 - x1, y2 - y1)

    diff = length - prev_dist
    steps = int(diff / 10)

    if steps > 0:
        for _ in range(steps):
            pyautogui.press("volumeup")
        print(f"🔊 Volume Up x{steps}")
        return length
    elif steps < 0:
        for _ in range(-steps):
            pyautogui.press("volumedown")
        print(f"🔉 Volume Down x{-steps}")
        return length

    return prev_dist

def main():
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    pTime = 0
    prev_volume_dist = 0
    last_action_time = 0
    last_fingers = -1
    cooldown = 1

    print("💻 Focus your cursor on the YouTube video...")
    time.sleep(2)
    pyautogui.click()  # Automatically click on center of screen to focus YouTube

    while True:
        success, img = cap.read()
        if not success:
            break

        img = detector.findHands(img)
        lmList = detector.findPosition(img)
        fingersUp = count_fingers(lmList)
        current_time = time.time()

        # Accurate gesture detection with cooldown
        if fingersUp != last_fingers and (current_time - last_action_time) > cooldown:
            last_action_time = current_time
            last_fingers = fingersUp

            if fingersUp == 5:
                pyautogui.press('f')
                print("📺 Fullscreen")
            elif fingersUp == 4:
                pyautogui.press('space')
                print("⏯️ Play/Pause")
            elif fingersUp == 0:
                pyautogui.press('esc')
                print("❌ Exit Fullscreen")
            elif fingersUp == 2:
                pyautogui.press('right')
                print("⏩ Seek Forward")
            elif fingersUp == 3:
                pyautogui.press('left')
                print("⏪ Seek Backward")

        # Volume control only when 2 fingers (thumb + index) are up
        if fingersUp == 2 and len(lmList) >= 9:
            prev_volume_dist = volume_control(lmList, prev_volume_dist)

        # FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime + 1e-5)
        pTime = cTime
        cv2.putText(img, f'FPS: {int(fps)}', (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        cv2.imshow("YouTube Gesture Controller", img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
