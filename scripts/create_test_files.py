"""Create minimal test files for upload testing"""
import os
from PIL import Image, ImageDraw
import random

out_dir = 'd:/PYTHON/test_uploads'
os.makedirs(out_dir, exist_ok=True)

# Create a simple test image with shapes
img = Image.new('RGB', (640, 480), color='white')
draw = ImageDraw.Draw(img)

# Draw some shapes to simulate content
draw.rectangle([50, 50, 200, 200], fill='red', outline='black', width=3)
draw.ellipse([250, 100, 400, 250], fill='blue', outline='black', width=3)
draw.polygon([(450, 50), (550, 200), (400, 300)], fill='green', outline='black')

# Add text
draw.text((100, 350), "Test Image", fill='black')

img_path = os.path.join(out_dir, 'test_image.png')
img.save(img_path)
print(f"✓ Created test image: {img_path}")

# Create a test document (simple text PDF-like content using PIL)
# For simplicity, just create a text file as placeholder
txt_path = os.path.join(out_dir, 'test_document.txt')
with open(txt_path, 'w') as f:
    f.write("Test Document\n")
    f.write("="*50 + "\n\n")
    f.write("This is a test document for upload analysis.\n")
    f.write("Line 1: Lorem ipsum dolor sit amet.\n")
    f.write("Line 2: Consectetur adipiscing elit.\n")
    f.write("Line 3: Sed do eiusmod tempor incididunt.\n"*10)
print(f"✓ Created test document: {txt_path}")

# For video, we'll create a minimal MP4-like placeholder (ffmpeg can read this)
# If ffmpeg is available, we can create a real video frame
try:
    import subprocess
    import shutil
    ffmpeg_bin = shutil.which('ffmpeg')
    if ffmpeg_bin:
        # Create a video with solid colors
        video_path = os.path.join(out_dir, 'test_video.mp4')
        cmd = f'"{ffmpeg_bin}" -y -f lavfi -i color=c=red:s=640x480:d=3 -f lavfi -i sine=f=1000:d=3 "{video_path}"'
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        if proc.returncode == 0:
            print(f"✓ Created test video: {video_path}")
        else:
            print(f"✗ ffmpeg failed: {proc.stderr.decode()[:100]}")
    else:
        print("⚠ ffmpeg not found on PATH; skipping video creation")
except Exception as e:
    print(f"⚠ Video creation skipped: {e}")

print(f"\n✓ Test files ready in: {out_dir}")
