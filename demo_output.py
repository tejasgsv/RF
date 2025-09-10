import pandas as pd
import numpy as np
from datetime import datetime

def create_demo_csv():
    """Create demo CSV showing expected output format"""
    
    # Generate realistic demo data
    np.random.seed(42)
    
    frame_data = []
    unique_people = 0
    total_people = 0
    total_objects = 0
    
    # Simulate 30 seconds of video at 30 FPS (processing every 5th frame)
    for frame in range(5, 901, 5):  # Every 5th frame from 5 to 900
        timestamp = (frame - 1) / 30.0  # 30 FPS
        
        # Simulate realistic people detection
        if 5 <= timestamp <= 10:  # Activity period 1
            people_count = np.random.randint(0, 3)
        elif 15 <= timestamp <= 20:  # Activity period 2
            people_count = np.random.randint(1, 4)
        else:
            people_count = np.random.randint(0, 2)
        
        # Simulate object detection
        objects_count = np.random.randint(0, 5)
        
        # Update totals
        total_people += people_count
        total_objects += objects_count
        
        # Update unique people (simplified)
        if people_count > 0:
            unique_people += np.random.randint(0, people_count + 1)
        
        frame_data.append({
            'Frame': frame,
            'Timestamp_Sec': round(timestamp, 2),
            'People_Count': people_count,
            'Objects_Count': objects_count,
            'Unique_People': unique_people,
            'Total_People_Detected': total_people,
            'Total_Objects_Detected': total_objects
        })
    
    # Create DataFrame
    df = pd.DataFrame(frame_data)
    
    # Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'RF_DEMO_VideoAnalysis_{timestamp}.csv'
    df.to_csv(csv_filename, index=False)
    
    print("DEMO CSV GENERATED!")
    print("=" * 40)
    print(f"File: {csv_filename}")
    print(f"Frames: {len(frame_data)}")
    print(f"Unique People: {unique_people}")
    print(f"Total People: {total_people}")
    print(f"Total Objects: {total_objects}")
    print("=" * 40)
    
    # Show sample data
    print("\nSample Data (first 10 rows):")
    print(df.head(10).to_string(index=False))
    
    return csv_filename

if __name__ == "__main__":
    create_demo_csv()