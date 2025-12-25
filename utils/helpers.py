import os
import logging
from config import Config

def setup_logging():
    """Setup application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log', mode='a')
        ]
    )

def ensure_upload_directory():
    """Ensure upload directory exists"""
    config = Config()
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

def validate_file_extension(filename, allowed_extensions):
    """Validate file extension"""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions

def get_file_size_mb(file_path):
    """Get file size in MB"""
    return os.path.getsize(file_path) / (1024 * 1024)

def cleanup_file(file_path):
    """Safely remove a file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Failed to cleanup file {file_path}: {e}")
