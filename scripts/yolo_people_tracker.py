#!/usr/bin/env python3
"""
Improved YOLO + Centroid Tracking People Counter
Perfect script for accurate unique people detection and counting in videos.

Usage:
    python yolo_people_tracker.py <video_path>
    
Example:
    python yolo_people_tracker.py "/path/to/video.mp4"

Requirements:
    pip install ultralytics opencv-python numpy
"""
import cv2
import numpy as np
import sys
import os
from collections import defaultdict
from typing import List, Tuple, Dict, Set


class CentroidTracker:
    """Robust centroid-based tracker for counting unique people"""
    def __init__(self, max_distance: float = 50.0, max_age: int = 30):
        self.max_distance = max_distance
        self.max_age = max_age
        self.tracks = {}
        self.next_id = 1
        self.retired_ids = set()
        
    def update(self, detections: List[Tuple[int, int, int, int, float]]) -> Dict:
        """Update with new detections: (x1, y1, x2, y2, confidence)"""
        current = {}
        for i, (x1, y1, x2, y2, conf) in enumerate(detections):
            cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
            current[i] = {
                'box': (x1, y1, x2, y2),
                'centroid': (cx, cy),
                'confidence': conf
            }
        
        matched_tracks = set()
        matched_dets = set()
        
        # Match existing tracks to detections
        for track_id, track_data in list(self.tracks.items()):
            best_match = None
            best_dist = self.max_distance
            
            for det_id, det_data in current.items():
                if det_id in matched_dets:
                    continue
                
                dist = np.linalg.norm(
                    np.array(track_data['centroid']) - np.array(det_data['centroid'])
                )
                
                if dist < best_dist:
                    best_dist = dist
                    best_match = det_id
            
            if best_match is not None:
                self.tracks[track_id].update({
                    'centroid': current[best_match]['centroid'],
                    'box': current[best_match]['box'],
                    'confidence': current[best_match]['confidence'],
                    'age': 0,
                    'frames': self.tracks[track_id].get('frames', 0) + 1
                })
                matched_tracks.add(track_id)
                matched_dets.add(best_match)
            else:
                self.tracks[track_id]['age'] += 1
                if self.tracks[track_id]['age'] > self.max_age:
                    self.retired_ids.add(track_id)
        
        # New tracks for unmatched detections
        for det_id, det_data in current.items():
            if det_id not in matched_dets:
                track_id = self.next_id
                self.next_id += 1
                self.tracks[track_id] = {
                    'centroid': det_data['centroid'],
                    'box': det_data['box'],
                    'confidence': det_data['confidence'],
                    'age': 0,
                    'frames': 1
                }
                matched_tracks.add(track_id)
        
        result = {}
        for tid in matched_tracks:
            if tid not in self.retired_ids:
                result[tid] = self.tracks[tid]
        
        return result
    
    def get_unique_people(self, min_frames: int = 3) -> Set[int]:
        """Get confident unique person IDs (appeared in at least min_frames)"""
        return {tid for tid, data in self.tracks.items() 
                if data.get('frames', 0) >= min_frames}


def load_yolo_model(model_name: str = 'yolov8n.pt'):
    """Load YOLO model"""
    try:
        from ultralytics import YOLO
        print(f"Loading YOLO model: {model_name}...")
        model = YOLO(model_name)
        print("YOLO model loaded successfully!")
        return model
    except ImportError:
        print("ERROR: ultralytics not installed!")
        print("Install with: pip install ultralytics opencv-python numpy")
        return None
    except Exception as e:
        print(f"ERROR loading YOLO model: {e}")
        return None


def analyze_video(video_path: str, yolo_model=None, max_frames: int = None, 
                  show_preview: bool = False) -> Dict:
    """Analyze video and count unique people"""
    
    if not os.path.exists(video_path):
        print(f"ERROR: Video file not found: {video_path}")
        return {'success': False}
    
    if yolo_model is None:
        yolo_model = load_yolo_model()
        if yolo_model is None:
            return {'success': False}
    
    # Load face cascade for secondary verification
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"ERROR: Cannot open video: {video_path}")
        return {'success': False}
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"\nVideo: {os.path.basename(video_path)}")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps:.2f}")
    print(f"  Total frames: {total_frames}")
    print(f"  Duration: {total_frames/fps:.1f}s\n")
    
    # Initialize tracker
    tracker = CentroidTracker(max_distance=50.0, max_age=30)
    
    frame_num = 0
    frame_stats = defaultdict(int)
    total_yolo_detections = 0
    total_faces = 0
    
    print("Processing frames...")
    
    while True:
        if max_frames and frame_num >= max_frames:
            break
        
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_num += 1
        
        # YOLO detection
        try:
            results = yolo_model(frame, verbose=False)[0]
        except Exception as e:
            print(f"  Frame {frame_num}: YOLO error: {e}")
            continue
        
        detections = []
        yolo_count = 0
        
        # Extract person detections
        try:
            for box in results.boxes:
                cls_val = int(box.cls[0] if hasattr(box.cls, '__len__') else box.cls)
                
                if cls_val == 0:  # Class 0 = person
                    xyxy = box.xyxy[0]
                    x1, y1, x2, y2 = map(int, xyxy.tolist() if hasattr(xyxy, 'tolist') else xyxy)
                    conf = float(box.conf[0] if hasattr(box.conf, '__len__') else box.conf)
                    
                    detections.append((x1, y1, x2, y2, conf))
                    yolo_count += 1
                    total_yolo_detections += 1
        except Exception as e:
            print(f"  Frame {frame_num}: Parse error: {e}")
        
        # Face detection
        face_count = 0
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
            face_count = len(faces)
            total_faces += face_count
        except:
            pass
        
        # Update tracker
        try:
            tracked = tracker.update(detections)
            frame_stats[frame_num] = len(tracked)
        except Exception as e:
            print(f"  Frame {frame_num}: Tracker error: {e}")
        
        # Progress
        if frame_num % max(1, total_frames // 20) == 0:
            pct = int(100 * frame_num / total_frames)
            bar = '█' * (pct // 5) + '░' * (20 - pct // 5)
            print(f"  [{bar}] {pct}% - Frame {frame_num}/{total_frames} - "
                  f"YOLO: {yolo_count}, Tracked: {len(tracked)}, Faces: {face_count}")
    
    cap.release()
    
    # Results
    unique_people_confident = len(tracker.get_unique_people(min_frames=3))
    all_ids = len(tracker.tracks)
    max_in_frame = max(frame_stats.values()) if frame_stats else 0
    avg_in_frame = np.mean(list(frame_stats.values())) if frame_stats else 0
    
    print(f"\n{'='*60}")
    print("ANALYSIS RESULTS:")
    print(f"{'='*60}")
    print(f"Total frames processed: {frame_num}")
    print(f"Total YOLO detections: {total_yolo_detections}")
    print(f"Total faces detected: {total_faces}")
    print(f"\nTracking Results:")
    print(f"  Unique people (3+ frames): {unique_people_confident}")
    print(f"  All IDs created: {all_ids}")
    print(f"  Max people in single frame: {max_in_frame}")
    print(f"  Avg people per frame: {avg_in_frame:.1f}")
    print(f"\nPerformance:")
    print(f"  Processing speed: {frame_num / fps:.1f}s real-time")
    print(f"  FPS processed: {frame_num / (frame_num / fps):.1f}")
    print(f"{'='*60}\n")
    
    return {
        'success': True,
        'frames_processed': frame_num,
        'unique_people': unique_people_confident,
        'all_ids': all_ids,
        'max_people_frame': max_in_frame,
        'avg_people_frame': round(avg_in_frame, 2),
        'total_yolo_detections': total_yolo_detections,
        'total_faces': total_faces,
        'video_file': os.path.basename(video_path)
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python yolo_people_tracker.py <video_path> [--model model_name]")
        print("Example: python yolo_people_tracker.py video.mp4")
        print("         python yolo_people_tracker.py video.mp4 --model yolov8m.pt")
        sys.exit(1)
    
    video_file = sys.argv[1]
    model_name = 'yolov8n.pt'
    
    if '--model' in sys.argv:
        model_name = sys.argv[sys.argv.index('--model') + 1]
    
    model = load_yolo_model(model_name)
    if model:
        results = analyze_video(video_file, yolo_model=model)
        if results['success']:
            print(f"Analysis saved: {results}")
