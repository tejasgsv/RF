"""Test uploads to the /analyze endpoint"""
import requests
import json
import time
import os
import sys

# Handle unicode in Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:5000"
test_dir = "d:/PYTHON/test_uploads"

def upload_and_track(filepath, file_type):
    """Upload a file and poll for completion"""
    print(f"\n{'='*60}")
    print(f"Uploading: {os.path.basename(filepath)} ({file_type})")
    print(f"{'='*60}")
    
    try:
        # Upload
        with open(filepath, 'rb') as f:
            files = {'file': f}
            data = {'file_type': file_type}
            resp = requests.post(f"{BASE_URL}/analyze", files=files, data=data, timeout=10)
        
        resp.raise_for_status()
        result = resp.json()
        analysis_id = result.get('analysis_id')
        print(f"[OK] Upload successful (202 Accepted)")
        print(f"  Analysis ID: {analysis_id}")
        print(f"  File type: {file_type}")
        
        # Poll for completion
        max_polls = 30
        for poll in range(max_polls):
            time.sleep(1)
            try:
                prog_resp = requests.get(f"{BASE_URL}/api/progress/{analysis_id}", timeout=5)
                prog_resp.raise_for_status()
                prog = prog_resp.json()
                status = prog.get('status')
                progress = prog.get('progress')
                print(f"  [Poll {poll+1}] Status: {status}, Progress: {progress}%")
                
                if status == 'completed':
                    print(f"[OK] Analysis completed!")
                    # Get results
                    res_resp = requests.get(f"{BASE_URL}/results/{analysis_id}", timeout=5)
                    res_resp.raise_for_status()
                    res = res_resp.json()
                    print(f"\n  Results summary:")
                    for k, v in res.items():
                        if k not in ['csv_data', 'json_file', 'people_details']:
                            print(f"    {k}: {v}")
                    break
                elif status == 'failed':
                    print(f"[FAIL] Analysis failed: {prog.get('error', 'Unknown error')}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"  [Poll {poll+1}] Error: {e}")
                break
    except requests.exceptions.RequestException as e:
        print(f"[FAIL] Upload failed: {e}")

# Test files
tests = [
    (os.path.join(test_dir, 'test_image.png'), 'image'),
    (os.path.join(test_dir, 'test_document.txt'), 'document'),
]

print("Starting upload tests...\n")
for filepath, ftype in tests:
    if os.path.exists(filepath):
        upload_and_track(filepath, ftype)
    else:
        print(f"[FAIL] File not found: {filepath}")

print(f"\n{'='*60}")
print("Upload tests completed!")

