"""
Upload handling service
- Validates and saves uploads (wraps FileValidator + FileManager)
- Generates thumbnails for images and first-frame for videos
- Returns metadata for use by analysis flow
"""
import os
import logging
from pathlib import Path
from PIL import Image
import io

try:
    import cv2
except Exception:
    cv2 = None

from utils.validators import FileValidator, FileManager
from config import config

logger = logging.getLogger(__name__)

class UploadService:
    def __init__(self, cfg=None):
        self.cfg = cfg or config['development']
        self.validator = FileValidator(self.cfg)
        self.manager = FileManager(self.cfg)

    def process_upload(self, file_storage, file_type: str) -> dict:
        """
        Validate, save, and create optional thumbnail
        Returns metadata dict with keys: filename, filepath, thumbnail (optional), size_mb
        """
        # Validate
        validation = self.validator.validate_file_upload(file_storage, file_type)
        filename = validation['filename']

        # Save
        filepath = self.manager.save_upload(file_storage, filename)

        # Generate thumbnail where appropriate. Be defensive: try image, video, document.
        thumb_path = None
        try:
            if file_type == 'image':
                thumb_path = self._generate_image_thumbnail(filepath, filename)
            elif file_type == 'video':
                # Try multiple strategies for video thumbnails
                try:
                    thumb_path = self._generate_video_thumbnail(filepath, filename)
                except Exception as e_vid:
                    logger.warning(f"Video thumbnail (cv2) failed for {filepath}: {e_vid}")
                    try:
                        thumb_path = self._generate_video_thumbnail_ffmpeg(filepath, filename)
                    except Exception as e_ff:
                        logger.warning(f"Video thumbnail (ffmpeg) failed for {filepath}: {e_ff}")
                        thumb_path = None
            elif file_type == 'document':
                try:
                    thumb_path = self._generate_document_thumbnail(filepath, filename)
                except Exception as e_doc:
                    logger.warning(f"Document thumbnail failed for {filepath}: {e_doc}")
                    thumb_path = None
        except Exception as e:
            logger.warning(f"Thumbnail generation failed for {filepath}: {e}")
            thumb_path = None

        return {
            'filename': filename,
            'filepath': filepath,
            'thumbnail': thumb_path,
            'size_mb': validation.get('size_mb', 0.0),
            'extension': validation.get('extension')
        }

    def _generate_image_thumbnail(self, filepath: str, filename: str) -> str:
        size = (320, 180)
        thumb_dir = Path(self.manager.upload_dir) / 'thumbnails'
        thumb_dir.mkdir(parents=True, exist_ok=True)
        thumb_name = f"thumb_{filename.rsplit('.',1)[0]}.jpg"
        thumb_path = thumb_dir / thumb_name

        with Image.open(filepath) as im:
            im.thumbnail(size)
            # convert to RGB and save as JPG
            if im.mode in ("RGBA", "P"):
                im = im.convert("RGB")
            im.save(str(thumb_path), format='JPEG', quality=80)

        return str(thumb_path)

    def _generate_video_thumbnail(self, filepath: str, filename: str) -> str:
        if cv2 is None:
            raise RuntimeError('OpenCV not available for video thumbnail')

        cap = cv2.VideoCapture(filepath)
        success, frame = cap.read()
        cap.release()
        if not success or frame is None:
            raise RuntimeError('Failed to read video frame')

        # resize frame
        import numpy as np
        from PIL import Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(frame_rgb)
        im.thumbnail((320,180))

        thumb_dir = Path(self.manager.upload_dir) / 'thumbnails'
        thumb_dir.mkdir(parents=True, exist_ok=True)
        thumb_name = f"thumb_{filename.rsplit('.',1)[0]}.jpg"
        thumb_path = thumb_dir / thumb_name
        im.save(str(thumb_path), format='JPEG', quality=80)
        return str(thumb_path)

    def _generate_video_thumbnail_ffmpeg(self, filepath: str, filename: str) -> str:
        """
        Try to extract a single frame using the system `ffmpeg` binary as a fallback.
        """
        import subprocess, shlex, shutil
        from PIL import Image

        ffmpeg_bin = shutil.which('ffmpeg')
        if not ffmpeg_bin:
            raise RuntimeError('ffmpeg not found on system PATH')

        thumb_dir = Path(self.manager.upload_dir) / 'thumbnails'
        thumb_dir.mkdir(parents=True, exist_ok=True)
        thumb_name = f"thumb_{filename.rsplit('.',1)[0]}.jpg"
        thumb_path = thumb_dir / thumb_name

        # Extract frame at 1 second
        cmd = f'"{ffmpeg_bin}" -y -i "{filepath}" -ss 00:00:01 -vframes 1 -q:v 2 "{thumb_path}"'
        proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        if proc.returncode != 0 or not thumb_path.exists():
            raise RuntimeError(f'ffmpeg extraction failed: {proc.stderr.decode(errors="ignore")}')

        # Ensure thumbnail is reasonable size (resize if large)
        with Image.open(str(thumb_path)) as im:
            im.thumbnail((320,180))
            if im.mode in ("RGBA", "P"):
                im = im.convert("RGB")
            im.save(str(thumb_path), format='JPEG', quality=80)

        return str(thumb_path)

    def _generate_document_thumbnail(self, filepath: str, filename: str) -> str:
        """
        Generate a thumbnail for documents (PDF preferred). Uses PyMuPDF (fitz) if available,
        otherwise creates a simple placeholder.
        """
        thumb_dir = Path(self.manager.upload_dir) / 'thumbnails'
        thumb_dir.mkdir(parents=True, exist_ok=True)
        thumb_name = f"thumb_{filename.rsplit('.',1)[0]}.jpg"
        thumb_path = thumb_dir / thumb_name

        try:
            # Attempt PyMuPDF for PDFs
            import fitz
            doc = fitz.open(filepath)
            if doc.page_count > 0:
                page = doc.load_page(0)
                pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                img_bytes = pix.tobytes('jpeg')
                from PIL import Image
                im = Image.open(io.BytesIO(img_bytes))
                im.thumbnail((320, 180))
                if im.mode in ("RGBA", "P"):
                    im = im.convert("RGB")
                im.save(str(thumb_path), format='JPEG', quality=80)
                doc.close()
                return str(thumb_path)
            doc.close()
        except Exception as e:
            logger.debug(f"PyMuPDF failed or not available: {e}")

        # Fallback: simple icon-like placeholder (safe and fast)
        try:
            from PIL import Image, ImageDraw, ImageFont
            im = Image.new('RGB', (320, 180), (245, 245, 245))
            d = ImageDraw.Draw(im)
            text = 'DOCUMENT'
            # Use default font if arial not available
            try:
                font = ImageFont.truetype('arial.ttf', 20)
            except Exception:
                font = ImageFont.load_default()
            # Measure text with textbbox
            bbox = d.textbbox((0, 0), text, font=font) if hasattr(d, 'textbbox') else (0, 0, 50, 15)
            w = bbox[2] - bbox[0] if hasattr(d, 'textbbox') else 50
            h = bbox[3] - bbox[1] if hasattr(d, 'textbbox') else 15
            x = max(0, (320 - w) // 2)
            y = max(0, (180 - h) // 2)
            d.text((x, y), text, fill=(30, 30, 30), font=font)
            im.save(str(thumb_path), format='JPEG', quality=75)
            return str(thumb_path)
        except Exception as e2:
            logger.warning(f"Document thumbnail placeholder also failed: {e2}")
            # Return empty string instead of raising
            return ''

# Export a singleton service instance
upload_service = UploadService()
