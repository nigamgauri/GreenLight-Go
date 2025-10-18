# predict.py
from ultralytics import YOLO
import os
import time

# --- CONFIGURATION ---
AMBULANCE_CLASS_ID = 0 
SIGNAL_FILE = 'emergency_signal.txt'
MODEL_PATH = 'runs/detect/train/weights/best.pt'
VIDEO_SOURCE = 'videos/Ambulance Stuck in traffic india Punjab #ambulance #traffic #india.mp4'

# --- SCRIPT ---
def send_signal():
    if not os.path.exists(SIGNAL_FILE):
        print(">>> AMBULANCE DETECTED! Sending signal to simulation...")
        with open(SIGNAL_FILE, 'w') as f:
            f.write('emergency')

def main():
    model = YOLO(MODEL_PATH)

    # --- THIS LINE IS UPDATED ---
    # show=True will open a window showing the video with detections
    results = model(VIDEO_SOURCE, stream=True, show=True, verbose=False)

    print(f"Starting detection on '{VIDEO_SOURCE}'... Press 'q' to quit the video window.")

    try:
        for result in results:
            if os.path.exists(SIGNAL_FILE):
                continue
            for box in result.boxes:
                if int(box.cls) == AMBULANCE_CLASS_ID:
                    send_signal()
                    time.sleep(5)
                    break
    except KeyboardInterrupt:
        print("\nDetection stopped by user.")

if __name__ == "__main__":
    main()