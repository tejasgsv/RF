import os
import logging
from pathlib import Path

def setup_logging(app):
    """Setup application logging"""
    logger = logging.getLogger()
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Setup formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    
    # File handler
    log_file = app.config.get('LOG_FILE', 'app.log')
    try:
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    except:
        logger.warning(f"Could not create log file: {log_file}")
    
    logger.setLevel(logging.DEBUG)

def ensure_directories(app):
    """Ensure all required directories exist"""
    directories = [
        app.config.get('UPLOAD_FOLDER', 'uploads'),
        app.config.get('DATABASE_DIR', 'data'),
        os.path.dirname(app.config.get('LOG_FILE', 'app.log'))
    ]

    for directory in directories:
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError as e:
                # Handle read-only file system (common in serverless environments)
                if e.errno == 30:  # Read-only file system
                    print(f"Warning: Read-only file system detected. Skipping directory creation for {directory}")
                    continue  # Skip this directory, don't crash
                else:
                    print(f"Error: Failed to create directory {directory}: {e}")
                    continue  # Continue with other directories
            except Exception as e:
                print(f"Error: Failed to create directory {directory}: {e}")
                continue  # Continue with other directories

def validate_file_extension(filename, allowed_extensions):
    """Validate file extension"""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions

def get_file_size_mb(file_path):
    """Get file size in MB"""
    try:
        return os.path.getsize(file_path) / (1024 * 1024)
    except:
        return 0

def cleanup_file(file_path):
    """Safely remove a file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        logging.getLogger(__name__).warning(f"Failed to cleanup file {file_path}: {e}")
