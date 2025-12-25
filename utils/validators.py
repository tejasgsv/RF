"""
Input validation and file handling utilities
"""
import os
import logging
from pathlib import Path
from werkzeug.utils import secure_filename
from config import Config

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom validation exception"""
    pass

class FileValidator:
    """Validate uploaded files before processing"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
    
    def validate_file_upload(self, file_object, file_type: str) -> dict:
        """
        Comprehensive file validation
        
        Args:
            file_object: Flask request file object
            file_type: 'video', 'image', or 'document'
            
        Returns:
            dict with validation result and sanitized filename
            
        Raises:
            ValidationError if validation fails
        """
        # Check if file exists
        if not file_object:
            raise ValidationError("No file provided")
        
        if file_object.filename == '':
            raise ValidationError("File name is empty")
        
        # Get extension
        if '.' not in file_object.filename:
            raise ValidationError("File has no extension")
        
        filename = secure_filename(file_object.filename)
        extension = filename.rsplit('.', 1)[1].lower()
        
        # Validate extension by type
        if file_type == 'video':
            if extension not in self.config.ALLOWED_VIDEO_EXTENSIONS:
                raise ValidationError(
                    f"Invalid video format. Allowed: {', '.join(self.config.ALLOWED_VIDEO_EXTENSIONS)}"
                )
        elif file_type == 'image':
            if extension not in self.config.ALLOWED_IMAGE_EXTENSIONS:
                raise ValidationError(
                    f"Invalid image format. Allowed: {', '.join(self.config.ALLOWED_IMAGE_EXTENSIONS)}"
                )
        elif file_type == 'document':
            if extension not in self.config.ALLOWED_DOCUMENT_EXTENSIONS:
                raise ValidationError(
                    f"Invalid document format. Allowed: {', '.join(self.config.ALLOWED_DOCUMENT_EXTENSIONS)}"
                )
        else:
            raise ValidationError(f"Unknown file type: {file_type}")
        
        # Check file size (before saving)
        file_object.seek(0, os.SEEK_END)
        file_size = file_object.tell()
        file_object.seek(0)
        
        if file_size == 0:
            raise ValidationError("File is empty")
        
        if file_size > self.config.MAX_CONTENT_LENGTH:
            size_mb = file_size / (1024 * 1024)
            max_mb = self.config.MAX_CONTENT_LENGTH / (1024 * 1024)
            raise ValidationError(f"File too large ({size_mb:.1f}MB). Max: {max_mb:.0f}MB")
        
        return {
            'valid': True,
            'filename': filename,
            'extension': extension,
            'size_mb': file_size / (1024 * 1024)
        }
    
    def validate_file_path(self, filepath: str) -> bool:
        """Verify file exists and is accessible"""
        try:
            return os.path.isfile(filepath) and os.access(filepath, os.R_OK)
        except Exception:
            return False

class FileManager:
    """Handle file operations safely"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.upload_dir = Path(self.config.UPLOAD_FOLDER)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def save_upload(self, file_object, unique_filename: str) -> str:
        """
        Save uploaded file with unique name
        
        Args:
            file_object: Flask request file object
            unique_filename: Unique filename to save as
            
        Returns:
            Full path to saved file
        """
        filepath = self.upload_dir / unique_filename
        file_object.save(str(filepath))
        logger.info(f"File saved: {filepath}")
        return str(filepath)
    
    def cleanup_file(self, filepath: str) -> bool:
        """Safely delete a file"""
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"File cleaned up: {filepath}")
                return True
        except Exception as e:
            logger.warning(f"Failed to cleanup {filepath}: {e}")
        return False
    
    def cleanup_old_files(self, hours: int = 24) -> int:
        """Clean up files older than specified hours"""
        from datetime import datetime, timedelta
        import time
        
        cutoff_time = time.time() - (hours * 3600)
        deleted = 0
        
        try:
            for filepath in self.upload_dir.glob('*'):
                if filepath.is_file() and os.path.getmtime(filepath) < cutoff_time:
                    try:
                        os.remove(filepath)
                        deleted += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete old file {filepath}: {e}")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old files")
        
        return deleted
    
    def get_file_size_mb(self, filepath: str) -> float:
        """Get file size in MB"""
        try:
            return os.path.getsize(filepath) / (1024 * 1024)
        except Exception:
            return 0

def generate_analysis_id() -> str:
    """Generate unique analysis ID"""
    import time
    import random
    import string
    
    timestamp = int(time.time() * 1000)  # milliseconds
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"analysis_{timestamp}_{random_suffix}"
