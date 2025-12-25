# YOLO People Tracking Guide - Perfect Script

## Overview
This guide explains the improved YOLO+Centroid Tracking script for accurate people counting and tracking in videos.

---

## Key Improvements Over Original Script

### ✅ **Original Issues Fixed:**
1. **Better Unique ID Counting** - Uses centroid distance matching instead of simple ID assignment
2. **Reduces False Positives** - Confidence threshold (3+ frames) filters out noise/flickering detections
3. **Face Detection Integration** - Secondary verification to confirm people
4. **Robust Tracking** - Handles person occlusion and temporary gaps
5. **Complete Statistics** - Shows max people, average, total detections

---

## How It Works

### **1. YOLO Detection**
- Runs YOLOv8 neural network on each frame
- Detects all "person" class objects (class 0)
- Returns bounding boxes with confidence scores

### **2. Centroid Tracking**
```
For each detection:
  - Calculate center point (centroid): (x + x2)/2, (y + y2)/2
  
For each existing track:
  - Find closest detection within max_distance (50 pixels)
  - If match found: Update track centroid, increment frame count
  - If no match: Age out track (delete after 30 frames without detection)
  
For new detections:
  - Assign new unique ID
  - Start new track
```

### **3. Face Detection**
- Optional secondary check using Haar Cascade classifiers
- Verifies human presence in bounding boxes
- Adds confidence to detection

### **4. Unique Person Counting**
- Counts tracks that appeared in **3+ frames** (filters noise)
- Ignores single-frame flickering detections
- Returns confident unique person count

---

## Installation & Usage

### **Install Dependencies:**
```bash
pip install ultralytics opencv-python numpy
```

### **Run Standalone Script:**
```bash
python scripts/yolo_people_tracker.py "path/to/video.mp4"
python scripts/yolo_people_tracker.py "video.mp4" --model yolov8m.pt  # Use larger model for accuracy
```

### **Use in Web App:**
- Upload video via dashboard at `http://127.0.0.1:5000`
- Select "video" as file type
- App automatically uses improved tracker with fallback

---

## Understanding Results

```
Total frames processed:    500 frames analyzed
Total YOLO detections:    1,245 total person detections across all frames
Total faces detected:       342 faces detected (verification)

Tracking Results:
  Unique people (3+ frames):  145 people
  All IDs created:            162 (includes noise)
  Max people in single frame:  35 people
  Avg people per frame:       22.3 people
```

### **Interpreting the Numbers:**
- **Unique people (3+ frames)**: Most reliable count - 145 different individuals
- **All IDs created**: Includes temporary flickering - use with caution
- **Max/Avg in frame**: Peak occupancy - useful for capacity planning

---

## Configuration Tuning

### **For Crowded Scenes (100+ people):**
```python
tracker = CentroidTracker(max_distance=80.0, max_age=50)  # More lenient
```

### **For Precise Counting (Clean Video):**
```python
tracker = CentroidTracker(max_distance=30.0, max_age=10)  # Stricter
confidence_threshold = 5  # Require 5+ frames
```

### **Model Selection:**
- `yolov8n.pt` - Nano (fastest, lower accuracy) ✓ Default
- `yolov8s.pt` - Small (balanced)
- `yolov8m.pt` - Medium (slower, higher accuracy)
- `yolov8l.pt` - Large (very slow, best accuracy)

---

## Sample Output

```
Video: anna_seva_footfall.mp4
  Resolution: 1920x1080
  FPS: 30.0
  Total frames: 18000
  Duration: 600.0s

Processing frames...
  [████░░░░░░░░░░░░░░] 20% - Frame 3600/18000 - YOLO: 28, Tracked: 26, Faces: 12
  [████████░░░░░░░░░░] 40% - Frame 7200/18000 - YOLO: 31, Tracked: 29, Faces: 15
  ...

============================================================
ANALYSIS RESULTS:
============================================================
Total frames processed: 18000
Total YOLO detections: 542,100
Total faces detected: 198,450

Tracking Results:
  Unique people (3+ frames): 2,847
  All IDs created: 3,156
  Max people in single frame: 87
  Avg people per frame: 30.1

Performance:
  Processing speed: 200.0s (3.3x real-time on GPU)
  FPS processed: 90.0
============================================================
```

---

## Advantages Over Original Colab Script

| Feature | Original | Improved |
|---------|----------|----------|
| Unique Person Count | ❌ Inaccurate (ID per frame) | ✅ Centroid matching |
| Noise Filtering | ❌ Counts all | ✅ 3+ frame threshold |
| Face Verification | ❌ No | ✅ Haar Cascade check |
| Tracking Accuracy | ❌ Simple center | ✅ Robust matching |
| Statistics | ⚠️ Basic | ✅ Detailed metrics |
| False Positives | ⚠️ High | ✅ Reduced |

---

## Troubleshooting

### **Getting 0 people?**
- Ensure video has visible people
- Check YOLO model is downloaded (auto-downloads first run)
- Try `--model yolov8m.pt` for better detection

### **Too many unique IDs?**
- Reduce max_distance (tighter tracking)
- Increase min_frames threshold
- Check if video is too dark or low resolution

### **Slow processing?**
- Use smaller model: `yolov8n.pt`
- Reduce frame processing (process every 2nd frame)
- Ensure GPU is available (CUDA)

### **Memory issues?**
- Process in chunks: `max_frames=1000`
- Use smaller model
- Close other applications

---

## Integration with Web App

The improved tracker is automatically used when:
1. User uploads video file via dashboard
2. Selects `video` as file type
3. System attempts YOLO+Norfair tracking
4. Falls back to traditional VideoAnalysisService if YOLO unavailable

**API Endpoint:**
```
POST /analyze
{
  "file": <video_file>,
  "file_type": "video"
}

Response (202 Accepted):
{
  "analysis_id": "analysis_1766680002235_v0lnjl",
  "job_id": "job_aff92a70e607",
  "status": "queued"
}

Results (when complete):
{
  "unique_people": 2847,
  "frames_processed": 18000,
  "max_people_frame": 87,
  "avg_people_frame": 30.1,
  "processing_time": 200.0
}
```

---

## References
- YOLO: https://github.com/ultralytics/ultralytics
- Centroid Tracking: Adrian Rosebrock's PyImageSearch guide
- OpenCV Cascade: https://docs.opencv.org/master/d5/de7/tutorial_cascade_classifier.html

---

**Last Updated:** 2025-12-25  
**Version:** 2.0 - Improved Tracking Algorithm
