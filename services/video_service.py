import cv2
import pandas as pd
import numpy as np
from datetime import datetime
import os
import time
import io
import csv
import logging
from typing import Dict, Optional
from config import Config
from video_analyzer import analyze_video_detailed

logger = logging.getLogger(__name__)

class VideoAnalysisService:
    """Service for video analysis using OpenCV and HOG detector"""

    def __init__(self):
        self.config = Config()

    def analyze_video(self, video_path: str) -> Dict:
        """
        Perform comprehensive video analysis using the detailed analyzer

        Args:
            video_path: Path to the video file

        Returns:
            Dict containing analysis results
        """
        try:
            logger.info(f"Starting video analysis for: {video_path}")

            # Use the detailed video analyzer
            analysis_result = analyze_video_detailed(video_path)

            if analysis_result is None:
                raise ValueError("Video analysis failed")

            # Read the generated CSV file content
            csv_file_path = analysis_result['csv_file']
            csv_data = ""
            if os.path.exists(csv_file_path):
                with open(csv_file_path, 'r') as f:
                    csv_data = f.read()
                # Clean up the file after reading
                os.remove(csv_file_path)

            # Clean up summary file if it exists
            summary_file_path = analysis_result.get('summary_file')
            if summary_file_path and os.path.exists(summary_file_path):
                os.remove(summary_file_path)

            # Get video properties for additional info
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = total_frames / fps if fps > 0 else 0
            cap.release()

            results = {
                'unique_people': analysis_result['unique_people'],
                'total_people': analysis_result['total_people'],
                'total_objects': analysis_result['total_objects'],
                'frames_analyzed': analysis_result['frames_analyzed'],
                'processing_time': analysis_result['processing_time'],
                'video_duration': round(duration, 2),
                'video_fps': round(fps, 2),
                'video_resolution': f"{width}x{height}",
                'csv_data': csv_data,
                'csv_filename': os.path.basename(csv_file_path),
                'success': True
            }

            logger.info(f"Video analysis completed: {results['unique_people']} unique people, "
                       f"{results['processing_time']}s processing time")

            return results

        except Exception as e:
            logger.error(f"Error in video analysis: {str(e)}")
            raise
