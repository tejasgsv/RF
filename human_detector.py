import cv2
from ultralytics import YOLO
from norfair import Detection, Tracker
import numpy as np
import pandas as pd
from datetime import datetime

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Video path
video_path = '26-06-2025.mp4'  # Replace with your video file name
cap = cv2.VideoCapture(video_path)

# Tracker setup
tracker = Tracker(distance_function="euclidean", distance_threshold=30)

unique_ids = set()
frame_number = 0
total_objects_detected = 0
results_data = []

print("🚀 Starting Reliance Foundation AI Video Analysis...")
print("📹 Processing video:", video_path)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_number += 1
    
    # Process every 3rd frame for better performance
    if frame_number % 3 != 0:
        continue
        
    results = model(frame)[0]
    detections = []
    current_frame_objects = 0

    for box in results.boxes:
        if int(box.cls[0]) == 0:  # Class 0 = person
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx, cy = int((x1 + x2)/2), int((y1 + y2)/2)
            detections.append(Detection(points=np.array([[cx, cy]])))
            current_frame_objects += 1
            total_objects_detected += 1

    tracked_objects = tracker.update(detections=detections)

    for obj in tracked_objects:
        unique_ids.add(obj.id)

    # Store frame data
    results_data.append({
        'Frame': frame_number,
        'People_Count': len(tracked_objects),
        'Unique_People': len(unique_ids),
        'Objects_Detected': current_frame_objects
    })

    print(f"🖼️ Frame {frame_number}: {len(tracked_objects)} person(s) tracked, {current_frame_objects} objects detected")

cap.release()

# Save results to CSV
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
csv_filename = f'video_analysis_{timestamp}.csv'
df = pd.DataFrame(results_data)
df.to_csv(csv_filename, index=False)

print("\n📊 ANALYSIS COMPLETE - Reliance Foundation AI")
print("="*50)
print(f"🔢 Total frames processed: {frame_number}")
print(f"👥 Unique people detected: {len(unique_ids)}")
print(f"🎯 Total objects detected: {total_objects_detected}")
print(f"📄 CSV report saved: {csv_filename}")
print("="*50)