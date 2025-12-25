"""
YOLO + Norfair based people tracker service with advanced tracking logic.
Improved version with centroid-based tracking, face detection, and robust unique person counting.

Usage:
    from services.yolo_norfair_service_v2 import YOLONorfairServiceV2
    svc = YOLONorfairServiceV2(model_path='yolov8n.pt')
    results = svc.analyze(video_path)

Returns a dict with: success, frames_processed, unique_people, fps, processing_time, detailed_tracking
"""
from typing import Optional, Dict, List, Tuple, Set
import time
import logging
import os
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class CentroidTracker:
    """Advanced centroid-based person tracker with robust ID management"""
    def __init__(self, max_distance: float = 50.0, max_age: int = 30):
        self.max_distance = max_distance
        self.max_age = max_age
        self.tracks = {}  # {track_id: track_data}
        self.next_id = 1
        self.retired_ids = set()
        self.total_ids_created = 0
        
    def update(self, detections: List[Tuple[int, int, int, int, float]]) -> Dict:
        """Update tracker with new detections (x1, y1, x2, y2, confidence)"""
        # Convert boxes to centroids
        current_detections = {}
        for x1, y1, x2, y2, conf in detections:
            cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
            current_detections[len(current_detections)] = {
                'box': (x1, y1, x2, y2),
                'centroid': (cx, cy),
                'confidence': conf
            }
        
        matched_tracks = set()
        matched_detections = set()
        
        # Match detections to existing tracks
        for track_id, track_data in list(self.tracks.items()):
            best_match = None
            best_dist = self.max_distance
            
            for det_id, det_data in current_detections.items():
                if det_id in matched_detections:
                    continue
                
                dist = np.linalg.norm(
                    np.array(track_data['centroid']) - np.array(det_data['centroid'])
                )
                
                if dist < best_dist:
                    best_dist = dist
                    best_match = (det_id, det_data)
            
            if best_match:
                det_id, det_data = best_match
                self.tracks[track_id].update({
                    'centroid': det_data['centroid'],
                    'box': det_data['box'],
                    'confidence': det_data['confidence'],
                    'age': 0,
                    'frames_seen': self.tracks[track_id].get('frames_seen', 0) + 1
                })
                matched_detections.add(det_id)
                matched_tracks.add(track_id)
            else:
                # Age out track
                self.tracks[track_id]['age'] += 1
                if self.tracks[track_id]['age'] > self.max_age:
                    self.retired_ids.add(track_id)
        
        # Create new tracks for unmatched detections
        for det_id, det_data in current_detections.items():
            if det_id not in matched_detections:
                track_id = self.next_id
                self.next_id += 1
                self.total_ids_created += 1
                
                self.tracks[track_id] = {
                    'centroid': det_data['centroid'],
                    'box': det_data['box'],
                    'confidence': det_data['confidence'],
                    'age': 0,
                    'frames_seen': 1,
                    'created_frame': 0
                }
                matched_tracks.add(track_id)
        
        # Return current tracked objects
        result = {}
        for track_id in matched_tracks:
            if track_id not in self.retired_ids:
                track = self.tracks[track_id]
                result[track_id] = {
                    'centroid': track['centroid'],
                    'box': track['box'],
                    'confidence': track['confidence'],
                    'frames_seen': track['frames_seen']
                }
        
        return result
    
    def get_all_tracked_ids(self) -> Set[int]:
        """Get all unique person IDs ever tracked"""
        return set(self.tracks.keys())
    
    def get_confident_tracks(self, min_frames: int = 3) -> Set[int]:
        """Get IDs that appeared in at least min_frames (reduces noise)"""
        return {tid for tid, data in self.tracks.items() 
                if data.get('frames_seen', 0) >= min_frames}


class YOLONorfairServiceV2:
    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        self.model_path = model_path or 'yolov8n.pt'
        self.device = device
        self._model = None
        self._face_cascade = None

    def _load_model(self):
        if self._model is not None:
            return True, None
        try:
            from ultralytics import YOLO
        except Exception as e:
            return False, f'ultralytics not available: {e}'

        try:
            self._model = YOLO(self.model_path)
            if self.device:
                try:
                    self._model.to(self.device)
                except Exception:
                    pass
            return True, None
        except Exception as e:
            return False, f'Failed to load YOLO model: {e}'

    def _load_face_detector(self):
        """Load OpenCV Haar Cascade for face detection"""
        if self._face_cascade is not None:
            return True, None
        try:
            import cv2
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self._face_cascade = cv2.CascadeClassifier(cascade_path)
            if self._face_cascade.empty():
                return False, "Face cascade classifier failed"
            return True, None
        except Exception as e:
            return False, f'Face cascade failed: {e}'

    def analyze(self, video_path: str, max_frames: Optional[int] = None, 
                person_class: int = 0, tracker_distance: float = 50.0) -> Dict:
        """
        Analyze video with YOLO person detection + robust centroid tracking + face detection.

        Args:
            video_path: path to video file
            max_frames: optional max frames to process
            person_class: YOLO class index for 'person' (default 0)
            tracker_distance: centroid distance threshold for track matching

        Returns:
            dict with success status and detailed analysis results
        """
        start_time = time.time()

        if not os.path.exists(video_path):
            return {'success': False, 'error': f'Video not found: {video_path}'}

        ok, err = self._load_model()
        if not ok:
            return {'success': False, 'error': err}

        ok, _ = self._load_face_detector()
        has_face_detection = ok

        import cv2

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {'success': False, 'error': 'Could not open video file'}

        # Initialize tracker
        tracker = CentroidTracker(max_distance=tracker_distance, max_age=30)

        frame_number = 0
        frame_stats = defaultdict(dict)
        total_detections = 0
        face_count_total = 0
        
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Process video frames
        while True:
            if max_frames and frame_number >= max_frames:
                break
            ret, frame = cap.read()
            if not ret:
                break

            frame_number += 1

            # YOLO person detection
            try:
                results = self._model(frame, verbose=False)[0]
            except Exception as e:
                logger.debug(f'YOLO failed on frame {frame_number}: {e}')
                continue

            detections = []
            yolo_people_count = 0
            
            # Extract person boxes from YOLO
            try:
                for box in results.boxes:
                    cls_val = box.cls[0] if hasattr(box.cls, '__len__') else box.cls
                    if int(cls_val) != person_class:
                        continue

                    xyxy = box.xyxy[0] if hasattr(box, 'xyxy') else box.xyxy
                    x1, y1, x2, y2 = map(int, xyxy.tolist() if hasattr(xyxy, 'tolist') else xyxy)
                    conf = float(box.conf[0]) if hasattr(box.conf, '__len__') else float(box.conf)
                    
                    detections.append((x1, y1, x2, y2, conf))
                    yolo_people_count += 1
                    total_detections += 1
                    
            except Exception as e:
                logger.debug(f'YOLO parsing failed on frame {frame_number}: {e}')

            # Face detection as secondary verification
            face_count = 0
            if has_face_detection:
                try:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = self._face_cascade.detectMultiScale(
                        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                    )
                    face_count = len(faces)
                    face_count_total += face_count
                except Exception as e:
                    logger.debug(f'Face detection failed on frame {frame_number}: {e}')

            # Update tracker
            try:
                tracked = tracker.update(detections)
                
                frame_stats[frame_number] = {
                    'yolo_detections': yolo_people_count,
                    'tracked_objects': len(tracked),
                    'faces_detected': face_count,
                    'tracking_ids': list(tracked.keys())
                }
                
            except Exception as e:
                logger.debug(f'Tracker error on frame {frame_number}: {e}')

            if frame_number % 50 == 0:
                logger.info(f"Progress: {frame_number}/{total_frames} - "
                           f"YOLO: {yolo_people_count}, Tracked: {len(tracked)}, Faces: {face_count}")

        cap.release()
        processing_time = round(time.time() - start_time, 2)

        # Calculate final statistics
        all_ids = tracker.get_all_tracked_ids()
        confident_ids = tracker.get_confident_tracks(min_frames=3)  # Filter noise
        
        unique_people = len(confident_ids)
        max_people = max([len(stats.get('tracking_ids', [])) for stats in frame_stats.values()], default=0)
        avg_people = np.mean([len(stats.get('tracking_ids', [])) for stats in frame_stats.values()]) if frame_stats else 0

        return {
            'success': True,
            'frames_processed': frame_number,
            'unique_people': unique_people,  # Confident detections only
            'total_ids_created': tracker.total_ids_created,  # All IDs including noise
            'max_people_in_frame': max_people,
            'avg_people_per_frame': round(avg_people, 2),
            'fps': round(fps, 2),
            'processing_time': processing_time,
            'total_detections': total_detections,
            'faces_detected_total': face_count_total,
            'unique_ids_confident': sorted(list(confident_ids))[:100],
            'confident_threshold': '3+ frames',
            'detection_method': 'YOLO + Centroid Tracking + Face Detection',
            'frame_samples': dict(sorted(frame_stats.items())[:10])  # First 10 frames
        }


# Export default instance
default_yolo_norfair_service_v2 = YOLONorfairServiceV2()
