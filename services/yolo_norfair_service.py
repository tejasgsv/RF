"""
YOLO + Norfair based people tracker service adapted from a Colab script.
This module is defensive: if `ultralytics` or `norfair` are not installed it
returns structured error dicts so callers can fallback to other analyzers.

Usage:
    from services.yolo_norfair_service import YOLONorfairService
    svc = YOLONorfairService(model_path='yolov8n.pt')
    results = svc.analyze(video_path)

Returns a dict with keys including: success, frames_processed, unique_people, fps, processing_time
"""
from typing import Optional, Dict
import time
import logging
import os
import numpy as np

logger = logging.getLogger(__name__)


class YOLONorfairService:
    def __init__(self, model_path: Optional[str] = None, device: Optional[str] = None):
        self.model_path = model_path or 'yolov8n.pt'
        self.device = device  # allow 'cpu' or 'cuda'
        # Lazy imports
        self._model = None
        self._norfair = None

    def _load_model(self):
        if self._model is not None:
            return True, None
        try:
            from ultralytics import YOLO
        except Exception as e:
            return False, f'ultralytics not available: {e}'

        try:
            # load model; allow missing weights (ultralytics may download automatically if configured)
            self._model = YOLO(self.model_path)
            if self.device:
                try:
                    self._model.to(self.device)
                except Exception:
                    pass
            return True, None
        except Exception as e:
            return False, f'Failed to load YOLO model: {e}'

    def _load_norfair(self):
        if self._norfair is not None:
            return True, None
        try:
            import norfair
            from norfair import Detection, Tracker
            self._norfair = {'module': norfair, 'Detection': Detection, 'Tracker': Tracker}
            return True, None
        except Exception as e:
            return False, f'norfair not available: {e}'

    def analyze(self, video_path: str, max_frames: Optional[int] = None, person_class: int = 0, distance_threshold: float = 30.0) -> Dict:
        """
        Analyze a video and track people with YOLO + Norfair.

        Args:
            video_path: path to video file
            max_frames: optional max frames to process (None = all)
            person_class: class index for 'person' in the YOLO model (default 0)
            distance_threshold: tracker distance threshold in pixels

        Returns:
            dict with analysis results or structured error
        """
        start_time = time.time()

        if not os.path.exists(video_path):
            return {'success': False, 'error': f'Video not found: {video_path}'}

        ok, err = self._load_model()
        if not ok:
            return {'success': False, 'error': err}

        ok, err = self._load_norfair()
        if not ok:
            return {'success': False, 'error': err}

        # local references
        Detection = self._norfair['Detection']
        Tracker = self._norfair['Tracker']

        # Tracker expects a distance function; use Euclidean
        def euclidean(a, b):
            a = np.asarray(a)
            b = np.asarray(b)
            return np.linalg.norm(a - b)

        tracker = Tracker(distance_function=euclidean, distance_threshold=distance_threshold)

        import cv2

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {'success': False, 'error': 'Could not open video file'}

        frame_number = 0
        unique_ids = set()

        # Process frames
        while True:
            if max_frames and frame_number >= max_frames:
                break
            ret, frame = cap.read()
            if not ret:
                break
            frame_number += 1

            # Run YOLO inference
            try:
                results = self._model(frame)[0]
            except Exception as e:
                logger.debug(f'YOLO inference failed on frame {frame_number}: {e}')
                continue

            detections = []
            # results.boxes is expected; handle multiple shapes defensively
            try:
                for box in results.boxes:
                    cls = int(getattr(box, 'cls', box.cls[0] if hasattr(box, 'cls') else -1))
                    if cls != person_class:
                        continue
                    xyxy = getattr(box, 'xyxy', None)
                    if xyxy is None:
                        xyxy = getattr(box, 'xyxy0', None)
                    if xyxy is None:
                        # try converting from tensor-like
                        try:
                            arr = np.array(box.xyxy[0])
                        except Exception:
                            continue
                    coords = np.array(list(map(int, xyxy[0].tolist()))) if hasattr(xyxy, 'tolist') else np.array(list(map(int, xyxy[0])))
                    x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]
                    cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)
                    detections.append(Detection(points=np.array([[cx, cy]])))
            except Exception as e:
                logger.debug(f'Failed to parse YOLO boxes on frame {frame_number}: {e}')

            try:
                tracked = tracker.update(detections=detections)
                for obj in tracked:
                    unique_ids.add(int(obj.id))
            except Exception as e:
                logger.debug(f'Norfair tracker error on frame {frame_number}: {e}')
                # continue without breaking

        cap.release()
        processing_time = round(time.time() - start_time, 2)

        # Try to get FPS from video
        try:
            cap2 = cv2.VideoCapture(video_path)
            fps = cap2.get(cv2.CAP_PROP_FPS) or 0
            cap2.release()
        except Exception:
            fps = 0

        return {
            'success': True,
            'frames_processed': frame_number,
            'unique_people': len(unique_ids),
            'unique_ids_sample': list(sorted(unique_ids))[:50],
            'fps': float(fps),
            'processing_time': processing_time
        }


# Export default instance
default_yolo_norfair_service = YOLONorfairService()
