import cv2
import pandas as pd
import numpy as np
from datetime import datetime
import os
import time

def analyze_video_detailed(video_path):
    """Complete video analysis with frame-by-frame tracking"""

    if not os.path.exists(video_path):
        print(f"ERROR: Video file not found: {video_path}")
        return None

    try:
        # Initialize video capture
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"ERROR: Could not open video file: {video_path}")
            return None

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0

        print("RELIANCE FOUNDATION - VIDEO ANALYZER")
        print("=" * 50)
        print(f"Video: {os.path.basename(video_path)}")
        print(f"Resolution: {width}x{height}")
        print(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        print(f"Total Frames: {total_frames}")
        print(f"FPS: {fps:.2f}")
        print("=" * 50)

        # Initialize HOG detector for people
        try:
            hog = cv2.HOGDescriptor()
            hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            print("HOG detector initialized successfully")
        except Exception as e:
            print(f"ERROR: Failed to initialize HOG detector: {e}")
            return None

        # Analysis variables
        frame_data = []
        unique_people_tracker = set()
        frame_number = 0
        total_people_detected = 0
        total_objects_detected = 0

        start_time = time.time()
        last_update = start_time

        print("Starting frame-by-frame analysis...")

        # Limit analysis to first 300 frames for faster processing (adjustable)
        max_frames_to_analyze = min(300, total_frames)
        frame_skip = max(1, total_frames // max_frames_to_analyze)

        while frame_number < total_frames:
            ret, frame = cap.read()
            if not ret:
                break

            frame_number += 1

            # Process frames based on skip factor
            if frame_number % frame_skip != 0:
                continue

            # Calculate timestamp
            timestamp_sec = (frame_number - 1) / fps if fps > 0 else frame_number - 1

            try:
                # Resize frame for detection
                detection_frame = cv2.resize(frame, (640, 480))

                # Detect people using HOG
                try:
                    result = hog.detectMultiScale(
                        detection_frame,
                        winStride=(8, 8),
                        padding=(16, 16),
                        scale=1.05
                    )

                    # Handle different OpenCV versions
                    if isinstance(result, tuple):
                        people_boxes, people_weights = result
                    else:
                        people_boxes = result
                        people_weights = []

                except Exception as e:
                    print(f"HOG detection error on frame {frame_number}: {e}")
                    people_boxes = []
                    people_weights = []

                people_count = len(people_boxes)
                total_people_detected += people_count

                # Simple object detection (using contours for moving objects)
                gray = cv2.cvtColor(detection_frame, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)

                # Find contours for objects
                contours, _ = cv2.findContours(cv2.Canny(blurred, 50, 150), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Filter contours by area to get significant objects
                objects_count = 0
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if 500 < area < 10000:  # Filter by reasonable object size
                        objects_count += 1

                total_objects_detected += objects_count

                # Track unique people (simplified tracking based on frame groups)
                minute_group = int(timestamp_sec / 60)
                second_group = int(timestamp_sec / 10)  # Group by 10-second intervals

                for i in range(people_count):
                    person_id = f"Person_{minute_group}_{second_group}_{i}"
                    unique_people_tracker.add(person_id)

                # Store frame data
                frame_info = {
                    'Frame': frame_number,
                    'Timestamp_Sec': round(timestamp_sec, 2),
                    'People_Count': people_count,
                    'Objects_Count': objects_count,
                    'Unique_People': len(unique_people_tracker),
                    'Total_People_Detected': total_people_detected,
                    'Total_Objects_Detected': total_objects_detected
                }

                frame_data.append(frame_info)

            except Exception as e:
                print(f"Error processing frame {frame_number}: {e}")
                continue

            # Progress update every 5 seconds
            current_time = time.time()
            if current_time - last_update >= 5.0:
                progress = (frame_number / total_frames) * 100
                elapsed = current_time - start_time
                eta = (elapsed / progress * 100 - elapsed) if progress > 0 else 0

                print(f"Progress: {progress:.1f}% | Frame {frame_number}/{total_frames} | "
                      f"People: {people_count} | Objects: {objects_count} | "
                      f"Unique: {len(unique_people_tracker)} | ETA: {eta:.0f}s")
                last_update = current_time

        cap.release()

        # Calculate final statistics
        processing_time = time.time() - start_time

        print("\n" + "=" * 50)
        print("ANALYSIS COMPLETE!")
        print("=" * 50)
        print(f"Processing Time: {processing_time:.2f} seconds")
        print(f"Frames Analyzed: {len(frame_data)}")
        print(f"Unique People: {len(unique_people_tracker)}")
        print(f"Total People Detections: {total_people_detected}")
        print(f"Total Object Detections: {total_objects_detected}")
        print("=" * 50)

        # Create DataFrame and save to CSV
        df = pd.DataFrame(frame_data)

        # Generate CSV report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f'RF_VideoAnalysis_{timestamp}.csv'

        # Save detailed CSV
        df.to_csv(csv_filename, index=False)

        # Create summary CSV
        summary_filename = f'RF_Summary_{timestamp}.csv'
        summary_data = {
            'Metric': [
                'Video File', 'Analysis Date', 'Processing Time (seconds)',
                'Video Duration (seconds)', 'Total Frames', 'Frames Analyzed',
                'Video FPS', 'Resolution', 'Unique People Detected',
                'Total People Detections', 'Total Object Detections',
                'Peak People Count', 'Peak Objects Count', 'Average People per Frame'
            ],
            'Value': [
                os.path.basename(video_path), datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                round(processing_time, 2), round(duration, 2), total_frames, len(frame_data),
                round(fps, 2), f"{width}x{height}", len(unique_people_tracker),
                total_people_detected, total_objects_detected,
                df['People_Count'].max() if len(df) > 0 else 0,
                df['Objects_Count'].max() if len(df) > 0 else 0,
                round(df['People_Count'].mean(), 2) if len(df) > 0 else 0
            ]
        }

        pd.DataFrame(summary_data).to_csv(summary_filename, index=False)

        print(f"CSV Reports Generated:")
        print(f"  - Detailed: {csv_filename}")
        print(f"  - Summary: {summary_filename}")

        return {
            'csv_file': csv_filename,
            'summary_file': summary_filename,
            'unique_people': len(unique_people_tracker),
            'total_people': total_people_detected,
            'total_objects': total_objects_detected,
            'frames_analyzed': len(frame_data),
            'processing_time': round(processing_time, 2)
        }

    except Exception as e:
        print(f"ERROR: Video analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Get video file from user
    video_file = input("Enter video filename: ").strip()
    if not video_file:
        print("No filename provided!")
    else:
        result = analyze_video_detailed(video_file)
        if result:
            print(f"\nSUCCESS! Analysis complete.")
            print(f"Unique People: {result['unique_people']}")
            print(f"CSV File: {result['csv_file']}")
        else:
            print("Analysis failed!")