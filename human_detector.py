import cv2
from ultralytics import YOLO
from norfair import Detection, Tracker
import numpy as np

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Video path
video_path = '26-06-2025.mp4'  # Replace with your video file name
cap = cv2.VideoCapture(video_path)

# Tracker setup
tracker = Tracker(distance_function="euclidean", distance_threshold=30)

unique_ids = set()
frame_number = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_number += 1
    results = model(frame)[0]
    detections = []

    for box in results.boxes:
        if int(box.cls[0]) == 0:  # Class 0 = person
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx, cy = int((x1 + x2)/2), int((y1 + y2)/2)
            detections.append(Detection(points=np.array([[cx, cy]])))

    tracked_objects = tracker.update(detections=detections)

    for obj in tracked_objects:
        unique_ids.add(obj.id)

    print(f"🖼️ Frame {frame_number}: {len(tracked_objects)} person(s) tracked")

cap.release()

print("\n🔢 Total frames processed:", frame_number)
print("👥 Approximate unique people detected:", len(unique_ids))