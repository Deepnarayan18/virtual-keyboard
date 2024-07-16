import cv2
import numpy as np
import pyautogui
import mediapipe as mp
import time 


try:
    import pyautogui
except ImportError:
    print("The 'pyautogui' module is not installed.")
    print("Attempting to install 'pyautogui'...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
    try:
        import pyautogui
    except ImportError:
        print("Failed to install 'pyautogui'. Please install it manually.")
        sys.exit(1)

# Initialize MediaPipe Hand module
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1480)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Full keyboard layout
keys = [
    ["Esc", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
    ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
    ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
    ["CapsLock", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter"],
    ["Shift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift"],
    ["Ctrl", "Win", "Alt", "Space", "Alt", "Win", "Menu", "Ctrl"]
]

# Define key size and position
key_width = 70
key_height = 70
key_gap = 12
keyboard_offset_x = 80
keyboard_offset_y = 160

# Calculate keyboard dimensions
keyboard_width = (14 * (key_width + key_gap)) - key_gap + 2 * keyboard_offset_x
keyboard_height = (6 * (key_height + key_gap)) - key_gap + 2 * keyboard_offset_y

# Key sizes and positions can be adjusted individually for special keys
special_key_widths = {
    "Backspace": 2 * key_width + key_gap,
    "Tab": 1.5 * key_width + key_gap / 2,
    "CapsLock": 1.75 * key_width + key_gap / 2,
    "Enter": 2.25 * key_width + key_gap,
    "Shift": 2.25 * key_width + key_gap,
    "Space": 7 * key_width + 6 * key_gap
}

# Initialize variables for debouncing and press effects
last_pressed_key = None
last_pressed_time = 0
debounce_time = 0.5  # seconds
pressed_keys = {}
pressed_key_text = ""
key_press_cooldown = 0.5  # time to reset key press state

def draw_key(frame, x, y, width, height, key, is_pressed):
    overlay = frame.copy()
    alpha = 0.6  # Transparency factor

    # Convert x, y, width, height to integers
    x, y, width, height = int(x), int(y), int(width), int(height)

    # Draw key background
    if is_pressed:
        cv2.rectangle(overlay, (x, y), (x + width, y + height), (200, 200, 200), cv2.FILLED)
    else:
        cv2.rectangle(overlay, (x, y), (x + width, y + height), (255, 255, 255), cv2.FILLED)
    
    # Apply transparency to the rectangle
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    # Draw 3D effect
    cv2.line(frame, (x, y), (x + width, y), (150, 150, 150), 2)
    cv2.line(frame, (x, y), (x, y + height), (150, 150, 150), 2)
    cv2.line(frame, (x + width, y), (x + width, y + height), (50, 50, 50), 2)
    cv2.line(frame, (x, y + height), (x + width, y + height), (50, 50, 50), 2)
    
    # Draw key label
    cv2.putText(frame, key, (x + 10, y + 55), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

def draw_keyboard(frame):
    overlay = frame.copy()
    alpha = 0.3  # Transparency factor for keyboard background

    # Draw the outer rectangle for the keyboard
    cv2.rectangle(overlay, 
                  (keyboard_offset_x - 10, keyboard_offset_y - 10), 
                  (keyboard_offset_x + keyboard_width - 50, keyboard_offset_y + keyboard_height - 50), 
                  (0, 0, 0), cv2.FILLED)
    
    # Apply transparency to the outer rectangle
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    y = keyboard_offset_y
    for row in keys:
        x = keyboard_offset_x
        for key in row:
            width = special_key_widths.get(key, key_width)
            is_pressed = pressed_keys.get(key, False)
            draw_key(frame, x, y, width, key_height, key, is_pressed)
            x += width + key_gap
        y += key_height + key_gap
    return frame

def is_key_pressed(cx, cy):
    global last_pressed_key, last_pressed_time, pressed_key_text
    y = keyboard_offset_y
    for row in keys:
        x = keyboard_offset_x
        for key in row:
            width = special_key_widths.get(key, key_width)
            if x < cx < x + width and y < cy < y + key_height:
                current_time = time.time()
                if last_pressed_key != key or (current_time - last_pressed_time > key_press_cooldown):
                    last_pressed_key = key
                    last_pressed_time = current_time
                    pressed_keys[key] = True
                    if key == "Space":
                        pressed_key_text += ' '
                    elif key == "Enter":
                        pressed_key_text += '\n'
                    elif key == "Backspace":
                        pressed_key_text = pressed_key_text[:-1]
                    elif key == "Tab":
                        pressed_key_text += '\t'
                    elif key not in ["Shift", "Ctrl", "Alt", "CapsLock", "Win", "Menu", "Esc"]:
                        pressed_key_text += key
                    if key == "Shift" or key == "Ctrl" or key == "Alt" or key == "CapsLock" or key == "Win" or key == "Menu" or key == "Esc" or key.startswith("F") and key[1:].isdigit():
                        pyautogui.press(key.lower())
                    return key
            x += width + key_gap
        y += key_height + key_gap
    return None

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Reduce frame size for faster processing
    small_frame = cv2.resize(frame_rgb, (320, 240))
    results = hands.process(small_frame)

    frame = draw_keyboard(frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get the tip of the index finger
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            h, w, c = frame.shape
            cx, cy = int(index_tip.x * w), int(index_tip.y * h)
            
            cv2.circle(frame, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
            
            pressed_key = is_key_pressed(cx, cy)
            if pressed_key:
                print(f"Key Pressed: {pressed_key}")

    # Draw text input box
    cv2.rectangle(frame, (50, 50), (1280 - 50, 120), (0, 0, 0), -1)
    cv2.putText(frame, pressed_key_text, (60, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Reset pressed keys after a short delay
    for key in list(pressed_keys):
        if time.time() - last_pressed_time > key_press_cooldown:
            pressed_keys[key] = False

    cv2.imshow('Virtual Keyboard', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
