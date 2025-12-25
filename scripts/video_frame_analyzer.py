#!/usr/bin/env python3
"""
Advanced Video Frame Analyzer with YOLO
Breaks video into frames and analyzes each frame for people detection
Provides frame-by-frame output and comprehensive counting
"""

import cv2
import sys
import os
from pathlib import Path
from collections import defaultdict, deque
import numpy as np
from typing import Dict, List, Tuple, Set


class FrameAnalyzer:
    """Analyzes frames for people detection using YOLO"""
    
    def __init__(self, model_name: str = "yolov8n.pt", confidence: float = 0.45):
        """Initialize YOLO model"""
        self.model_name = model_name
        self.confidence = confidence
        self.model = None
        self.load_model()
        
    def load_model(self):
        """Load YOLO model with error handling"""
        try:
            from ultralytics import YOLO
            print(f"📦 Loading YOLO model: {self.model_name}")
            self.model = YOLO(self.model_name)
            print(f"✅ Model loaded successfully\n")
        except ImportError:
            print("❌ ERROR: ultralytics not installed")
            print("   Run: pip install ultralytics opencv-python")
            sys.exit(1)
        except Exception as e:
            print(f"❌ ERROR loading model: {e}")
            sys.exit(1)


class CentroidTracker:
    """Track people across frames using centroid matching"""
    
    def __init__(self, max_distance: float = 50.0, max_age: int = 30):
        self.tracks = {}  # {track_id: {centroid, age, frames_seen, first_seen, last_seen}}
        self.next_id = 0
        self.max_distance = max_distance
        self.max_age = max_age
        self.all_ids = set()  # Track all IDs ever created
        
    def update(self, detections: List[Tuple[float, float, float, float, float]]) -> Dict:
        """
        Update tracker with new detections
        detections: list of (x1, y1, x2, y2, confidence) tuples
        Returns: dict of track_id -> centroid
        """
        current_detections = []
        for x1, y1, x2, y2, conf in detections:
            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2
            current_detections.append({
                'centroid': (cx, cy),
                'box': (x1, y1, x2, y2),
                'confidence': conf
            })
        
        # If no tracks exist, create new ones for all detections
        if not self.tracks:
            for det in current_detections:
                track_id = self.next_id
                self.tracks[track_id] = {
                    'centroid': det['centroid'],
                    'box': det['box'],
                    'confidence': det['confidence'],
                    'age': 0,
                    'frames_seen': 1,
                    'first_seen': 0,
                    'last_seen': 0
                }
                self.all_ids.add(track_id)
                self.next_id += 1
            return self.tracks
        
        # Match existing tracks to current detections
        matched_indices = set()
        used_detections = set()
        
        for track_id, track_data in list(self.tracks.items()):
            best_distance = float('inf')
            best_detection_idx = -1
            
            for det_idx, det in enumerate(current_detections):
                if det_idx in used_detections:
                    continue
                
                # Calculate Euclidean distance
                dx = track_data['centroid'][0] - det['centroid'][0]
                dy = track_data['centroid'][1] - det['centroid'][1]
                distance = np.sqrt(dx*dx + dy*dy)
                
                if distance < best_distance and distance < self.max_distance:
                    best_distance = distance
                    best_detection_idx = det_idx
            
            # Update track if match found
            if best_detection_idx >= 0:
                det = current_detections[best_detection_idx]
                self.tracks[track_id]['centroid'] = det['centroid']
                self.tracks[track_id]['box'] = det['box']
                self.tracks[track_id]['confidence'] = det['confidence']
                self.tracks[track_id]['age'] = 0
                self.tracks[track_id]['frames_seen'] += 1
                self.tracks[track_id]['last_seen'] += 1
                matched_indices.add(track_id)
                used_detections.add(best_detection_idx)
            else:
                # No match found, increment age
                self.tracks[track_id]['age'] += 1
        
        # Create new tracks for unmatched detections
        for det_idx, det in enumerate(current_detections):
            if det_idx not in used_detections:
                track_id = self.next_id
                self.tracks[track_id] = {
                    'centroid': det['centroid'],
                    'box': det['box'],
                    'confidence': det['confidence'],
                    'age': 0,
                    'frames_seen': 1,
                    'first_seen': 0,
                    'last_seen': 0
                }
                self.all_ids.add(track_id)
                self.next_id += 1
        
        # Remove old tracks
        tracks_to_remove = [tid for tid, data in self.tracks.items() if data['age'] > self.max_age]
        for tid in tracks_to_remove:
            del self.tracks[tid]
        
        return self.tracks
    
    def get_confident_tracks(self, min_frames: int = 3) -> Dict:
        """Get tracks with minimum frames seen (high confidence)"""
        return {tid: data for tid, data in self.tracks.items() if data['frames_seen'] >= min_frames}


def analyze_video(video_path: str, model_name: str = "yolov8n.pt", max_frames: int = None):
    """Analyze video frame by frame"""
    
    # Validate video file
    if not os.path.exists(video_path):
        print(f"❌ ERROR: Video file not found: {video_path}")
        sys.exit(1)
    
    print("=" * 70)
    print("VIDEO FRAME-BY-FRAME PEOPLE ANALYZER")
    print("=" * 70)
    print(f"📹 Video: {Path(video_path).name}")
    print(f"📍 Path: {video_path}\n")
    
    # Initialize
    analyzer = FrameAnalyzer(model_name=model_name)
    tracker = CentroidTracker(max_distance=60, max_age=20)
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ ERROR: Cannot open video file")
        sys.exit(1)
    
    # Video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"Resolution: {width}x{height}")
    print(f"FPS: {fps:.1f}")
    print(f"Total Frames: {total_frames:,}")
    print(f"Duration: {duration:.1f}s")
    print("\n" + "=" * 70)
    print("FRAME-BY-FRAME ANALYSIS")
    print("=" * 70 + "\n")
    
    # Analysis variables
    frame_count = 0
    people_per_frame = []
    frame_detections = {}  # frame_num -> list of detections
    frame_tracks = {}      # frame_num -> list of track IDs
    
    # Process frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        if max_frames and frame_count > max_frames:
            break
        
        # Run YOLO detection
        try:
            results = analyzer.model(frame, conf=analyzer.confidence, verbose=False)
            
            # Extract person detections (class 0 is person in COCO)
            detections = []
            if len(results) > 0 and results[0].boxes is not None:
                for box in results[0].boxes:
                    cls = int(box.cls[0])
                    if cls == 0:  # Person class
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
                        detections.append((x1, y1, x2, y2, conf))
            
            # Update tracker
            tracks = tracker.update(detections)
            
            # Store results
            frame_detections[frame_count] = len(detections)
            frame_tracks[frame_count] = len(tracks)
            people_per_frame.append(len(tracks))
            
            # Print every 30 frames (approximately 1 second at 30fps)
            print_interval = max(1, int(fps))
            if frame_count % print_interval == 0 or frame_count <= 5:
                progress = (frame_count / total_frames) * 100
                time_elapsed = frame_count / fps
                
                print(f"Frame {frame_count:6d}/{total_frames:6d} | {progress:5.1f}% | {time_elapsed:6.1f}s")
                print(f"  ➤ YOLO Detections: {len(detections):3d} people")
                print(f"  ➤ Active Tracks: {len(tracks):3d} tracked IDs")
                print(f"  ➤ Confident Tracks (3+ frames): {len(tracker.get_confident_tracks(min_frames=3)):3d}")
                print(f"  ➤ All IDs Created: {len(tracker.all_ids):3d}\n")
        
        except Exception as e:
            print(f"❌ Frame {frame_count} error: {e}")
            continue
    
    cap.release()
    
    # Calculate statistics
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE - SUMMARY STATISTICS")
    print("=" * 70 + "\n")
    
    confident_tracks = tracker.get_confident_tracks(min_frames=3)
    
    print(f"📊 PEOPLE DETECTION RESULTS:\n")
    print(f"  Unique People Identified (3+ frames): {len(confident_tracks):,}")
    print(f"  Total IDs Created (all detections): {len(tracker.all_ids):,}")
    print(f"  False Positives Filtered: {len(tracker.all_ids) - len(confident_tracks):,}\n")
    
    if people_per_frame:
        max_people = max(people_per_frame)
        min_people = min(people_per_frame)
        avg_people = sum(people_per_frame) / len(people_per_frame)
        
        print(f"📈 OCCUPANCY STATISTICS:\n")
        print(f"  Max People in Single Frame: {max_people}")
        print(f"  Min People in Single Frame: {min_people}")
        print(f"  Average People per Frame: {avg_people:.1f}\n")
    
    print(f"⏱️  PROCESSING METRICS:\n")
    print(f"  Frames Processed: {frame_count:,}")
    print(f"  Processing Duration: {duration:.1f}s")
    print(f"  Speed: {frame_count/duration:.1f} fps\n")
    
    # Detailed confidence breakdown
    print(f"📋 CONFIDENCE BREAKDOWN:\n")
    confidence_tiers = {
        '1 frame (noise)': len([t for t in tracker.tracks.values() if t['frames_seen'] == 1]),
        '2 frames (weak)': len([t for t in tracker.tracks.values() if t['frames_seen'] == 2]),
        '3+ frames (confident)': len(confident_tracks),
    }
    for tier, count in confidence_tiers.items():
        print(f"  {tier}: {count:,}")
    
    print("\n" + "=" * 70)
    
    return {
        'unique_people': len(confident_tracks),
        'total_ids': len(tracker.all_ids),
        'max_occupancy': max(people_per_frame) if people_per_frame else 0,
        'avg_occupancy': sum(people_per_frame) / len(people_per_frame) if people_per_frame else 0,
        'frames_processed': frame_count,
        'duration': duration
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python video_frame_analyzer.py <video_path> [--model MODEL_NAME]")
        print("Example: python video_frame_analyzer.py video.mp4 --model yolov8m.pt")
        sys.exit(1)
    
    video_path = sys.argv[1]
    model_name = "yolov8n.pt"
    
    if "--model" in sys.argv:
        model_idx = sys.argv.index("--model")
        if model_idx + 1 < len(sys.argv):
            model_name = sys.argv[model_idx + 1]
    
    analyze_video(video_path, model_name=model_name)
