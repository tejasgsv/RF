import os

class Config:
    # Application Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'reliance-foundation-ai-2024'
    
    # Upload Configuration
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv'}
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif'}
    
    # Processing Configuration
    FRAME_SKIP = 5  # Process every 5th frame for speed
    RESIZE_WIDTH = 320  # Resize frame width for faster processing
    DETECTION_THRESHOLD = 0.5
    TRACKING_DISTANCE = 100
    
    # Application Info
    APP_NAME = "Reliance Foundation AI Analytics"
    APP_VERSION = "2.1.0"
    COMPANY = "Reliance Foundation"
    COPYRIGHT_YEAR = "2024"
    
    # Performance Settings
    THREADED = True
    DEBUG = False  # Set to False for production

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}