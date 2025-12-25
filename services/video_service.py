import cv2
import pandas as pd
import numpy as np
from datetime import datetime
import os
import time
import io
import csv
import logging
import json
from typing import Dict, Optional, List, Tuple
from config import Config
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class VideoAnalysisService:
    """Service for video analysis using OpenCV with face/head detection"""

    def __init__(self):
        self.config = Config()

    def analyze(self, video_path: str) -> Dict:
        """
        Perform comprehensive video analysis with OpenCV detection

        Args:
            video_path: Path to the video file

        Returns:
            Dict containing analysis results
        """
        return self.analyze_video(video_path)
    
    def analyze_video(self, video_path: str) -> Dict:
        """
        Internal method for video analysis with OpenCV detection

        Args:
            video_path: Path to the video file

        Returns:
            Dict containing analysis results
        """
        try:
            logger.info(f"Starting video analysis for: {video_path}")

            # Perform basic video analysis
            analysis_result = self._analyze_video_basic(video_path)

            if not analysis_result.get('success'):
                raise ValueError(f"Video analysis failed: {analysis_result.get('error', 'Unknown error')}")

            # Prepare return results
            results = {
                'unique_people': analysis_result.get('unique_people', 0),
                'total_people_detections': analysis_result.get('total_people_detections', 0),
                'total_faces': analysis_result.get('total_faces', 0),
                'total_heads': analysis_result.get('total_heads', 0),
                'total_objects': 0,  # Keep for compatibility
                'frames_analyzed': analysis_result.get('frames_analyzed', 0),
                'total_frames': analysis_result.get('total_frames', 0),
                'processing_time': analysis_result.get('processing_time', 0),
                'video_duration': analysis_result.get('duration', 0),
                'fps': analysis_result.get('fps', 0),
                'resolution': analysis_result.get('resolution', ''),
                'video_filename': analysis_result.get('video_filename', os.path.basename(video_path)),
                'peak_people': analysis_result.get('peak_people', 0),
                'avg_people_per_frame': analysis_result.get('avg_people_per_frame', 0),
                'people_details': analysis_result.get('people_details', []),
                'csv_data': '',
                'csv_filename': analysis_result.get('csv_file', 'analysis.csv'),
                'json_file': analysis_result.get('json_file', ''),
                'success': True
            }

            # Read CSV data if available
            csv_file_path = analysis_result.get('csv_file')
            if csv_file_path and os.path.exists(csv_file_path):
                with open(csv_file_path, 'r') as f:
                    results['csv_data'] = f.read()
                # Clean up the file
                try:
                    os.remove(csv_file_path)
                except:
                    pass

            # Clean up JSON file if exists
            json_file_path = analysis_result.get('json_file')
            if json_file_path and os.path.exists(json_file_path):
                try:
                    os.remove(json_file_path)
                except:
                    pass

            # Clean up uploaded video
            if os.path.exists(video_path):
                try:
                    os.remove(video_path)
                except:
                    pass

            logger.info(f"Video analysis completed: {results['unique_people']} unique people, "
                       f"{results['total_faces']} faces, {results['total_heads']} heads")

            return results

        except Exception as e:
            logger.error(f"Error in video analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'processing_time': 0
            }

    def _analyze_video_basic(self, video_path: str) -> Dict:
        """
        Enhanced video analysis with detailed metrics and face detection
        Uses smart frame sampling and parallel processing for speed

        Args:
            video_path: Path to the video file

        Returns:
            Dict containing detailed analysis results
        """
        try:
            start_time = time.time()
            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                return {
                    'success': False,
                    'error': f"Could not open video file: {video_path}",
                    'processing_time': 0
                }

            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0
            
            if fps == 0:
                fps = 30  # Default fallback
                
            # Initialize detectors
            hog = cv2.HOGDescriptor()
            hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            
            # Load cascade classifiers for face and eyes detection
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_eye.xml'
            )

            # Smart frame sampling - more frames at start, middle, end for better accuracy
            frame_data = []
            frame_indices = self._get_smart_frame_indices(total_frames)
            
            # Initialize tracking
            unique_people_ids = set()
            face_detections = []
            people_per_frame = []
            frames_with_motion = []
            confidence_scores = []
            temporal_analysis = []
            
            # Scene change detection
            last_frame = None
            scene_changes = []
            
            frame_num = 0
            processed_frames = 0
            previous_gray = None

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_num += 1
                
                # Only process selected frames
                if frame_num not in frame_indices:
                    continue

                processed_frames += 1
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Scene change detection
                if previous_gray is not None:
                    flow = cv2.absdiff(frame_gray, previous_gray)
                    motion_intensity = np.sum(flow) / frame.size
                    
                    if motion_intensity > 2.0:  # Threshold for significant motion
                        scene_changes.append({
                            'frame': frame_num,
                            'intensity': round(motion_intensity, 2)
                        })

                # Resize for faster processing
                detection_frame = cv2.resize(frame_gray, (320, 240))
                full_frame = cv2.resize(frame, (640, 480))
                
                # People detection using HOG
                try:
                    result = hog.detectMultiScale(
                        detection_frame,
                        winStride=(4, 4),
                        padding=(8, 8),
                        scale=1.05,
                        useMeanshiftGrouping=True
                    )

                    if isinstance(result, tuple):
                        people_boxes, scores = result
                    else:
                        people_boxes = result
                        scores = np.array([0.5] * len(result))

                    people_count = len(people_boxes)
                    
                    # Scale boxes back to original size
                    scaled_boxes = []
                    for (x, y, w, h) in people_boxes:
                        scaled_x = int(x * (640/320))
                        scaled_y = int(y * (480/240))
                        scaled_w = int(w * (640/320))
                        scaled_h = int(h * (480/240))
                        scaled_boxes.append((scaled_x, scaled_y, scaled_w, scaled_h))
                        confidence_scores.append(round(float(scores[len(scaled_boxes)-1]) if len(scores) > 0 else 0.5, 3))

                except Exception as e:
                    people_count = 0
                    scaled_boxes = []
                    logger.debug(f"People detection error: {e}")

                # Face detection using Cascade
                try:
                    faces = face_cascade.detectMultiScale(
                        full_frame,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(30, 30),
                        maxSize=(300, 300)
                    )
                    
                    faces_in_frame = len(faces)
                    
                    # Track eyes in detected faces
                    eyes_detected = 0
                    for (x, y, w, h) in faces:
                        roi_gray = full_frame[y:y+h, x:x+w]
                        eyes = eye_cascade.detectMultiScale(roi_gray)
                        eyes_detected += len(eyes)
                        
                        face_detections.append({
                            'frame': frame_num,
                            'x': x,
                            'y': y,
                            'width': w,
                            'height': h,
                            'eyes': len(eyes)
                        })
                    
                except Exception as e:
                    faces_in_frame = 0
                    eyes_detected = 0
                    logger.debug(f"Face detection error: {e}")

                # Combined detection
                combined_people = max(people_count, faces_in_frame)
                
                # Assign unique IDs to detected people
                for i in range(combined_people):
                    person_id = f"Person_{frame_num}_{i}"
                    unique_people_ids.add(person_id)

                # Frame analysis
                people_per_frame.append(combined_people)
                
                temporal_analysis.append({
                    'frame': frame_num,
                    'people': combined_people,
                    'faces': faces_in_frame,
                    'motion': motion_intensity if previous_gray is not None else 0,
                    'timestamp': round((frame_num / fps), 2) if fps > 0 else 0
                })

                previous_gray = frame_gray.copy()

            cap.release()
            processing_time = time.time() - start_time

            # Calculate statistics
            max_people = max(people_per_frame) if people_per_frame else 0
            avg_people = np.mean(people_per_frame) if people_per_frame else 0
            total_people_detections = sum(people_per_frame)
            total_faces = len(face_detections)
            
            # Video quality score
            video_quality_score = min(100, int((total_frames / processed_frames) * 10))

            return {
                'success': True,
                'unique_people': len(unique_people_ids),
                'total_people_detections': total_people_detections,
                'total_faces': total_faces,
                'total_heads': total_faces,  # Heads approximation from faces
                'frames_analyzed': processed_frames,
                'total_frames': total_frames,
                'processing_time': round(processing_time, 2),
                'duration': round(duration, 2),
                'fps': round(fps, 2),
                'resolution': f"{width}x{height}",
                'video_filename': os.path.basename(video_path),
                'peak_people': int(max_people),
                'avg_people_per_frame': round(avg_people, 2),
                'confidence_score': round(np.mean(confidence_scores) * 100, 1) if confidence_scores else 0,
                'scene_changes': len(scene_changes),
                'motion_events': len([s for s in scene_changes if s['intensity'] > 3.0]),
                'average_fps_processed': round(processed_frames / processing_time, 1) if processing_time > 0 else 0,
                'video_quality_score': video_quality_score,
                'temporal_data': temporal_analysis[:20],  # First 20 frames detailed
                'scene_analysis': scene_changes,
                'people_details': [],
                'csv_file': None
            }

        except Exception as e:
            logger.error(f"Error in enhanced video analysis: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'processing_time': 0
            }

    def _get_smart_frame_indices(self, total_frames: int) -> set:
        """
        Get smart frame sampling indices for faster but comprehensive analysis
        Samples more frames at beginning, middle, and end
        
        Args:
            total_frames: Total number of frames in video
            
        Returns:
            Set of frame indices to process
        """
        indices = set()
        
        if total_frames <= 100:
            # For short videos, process all frames
            return set(range(1, total_frames + 1))
        
        # Sample strategy: 20% of frames
        sample_size = max(50, int(total_frames * 0.2))
        
        # Beginning (first 10%)
        start_segment = int(total_frames * 0.1)
        indices.update(range(1, min(sample_size // 4, start_segment)))
        
        # Middle (40-60%)
        middle_start = int(total_frames * 0.4)
        middle_end = int(total_frames * 0.6)
        middle_samples = np.linspace(middle_start, middle_end, sample_size // 3)
        indices.update(set(int(x) for x in middle_samples))
        
        # End (last 10%)
        end_segment = int(total_frames * 0.9)
        indices.update(range(end_segment, total_frames))
        
        # Distributed throughout
        distributed = np.linspace(1, total_frames, sample_size // 4)
        indices.update(set(int(x) for x in distributed))
        
        return indices
