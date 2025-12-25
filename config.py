import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()

class Config:
    """Base configuration"""
    
    # Application
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    APP_NAME = "AI Analytics Platform"
    APP_VERSION = "3.0.0"
    COMPANY = "Reliance Foundation"
    
    # Flask
    DEBUG = False
    TESTING = False
    THREADED = True
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year for static assets
    JSON_SORT_KEYS = False
    
    # File Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200MB
    
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}
    ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'docx', 'doc', 'xlsx', 'pptx', 'txt'}
    
    # Database - Use in-memory for serverless environments
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        # Check if we're in a serverless environment (read-only file system)
        try:
            # Try to create a test file to check if file system is writable
            test_file = BASE_DIR / '.test_write'
            test_file.write_text('test')
            test_file.unlink()  # Clean up
            # If successful, use file-based database
            database_url = f'sqlite:///{BASE_DIR / "app.db"}'
        except (OSError, PermissionError):
            # Read-only file system detected, use in-memory database
            database_url = 'sqlite:///:memory:'

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Processing
    PROCESSING_TIMEOUTS = {
        'video': 300,      # 5 minutes
        'image': 60,       # 1 minute
        'document': 120    # 2 minutes
    }
    
    # Analysis parameters
    FRAME_SKIP = 5
    RESIZE_WIDTH = 320
    DETECTION_THRESHOLD = 0.5
    
    # Job Queue
    MAX_WORKERS = 4
    QUEUE_SIZE = 100
    JOB_CLEANUP_INTERVAL = 3600  # Clean old jobs every hour
    
    # Security
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PREFERRED_URL_SCHEME = 'http'  # Set to 'https' in production
    
    # CORS
    CORS_HEADERS = 'Content-Type'
    CORS_ORIGINS = ['*']
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', str(BASE_DIR / 'logs' / 'app.log'))
    
    # Directories
    DATABASE_DIR = str(BASE_DIR / 'data')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False
    PREFERRED_URL_SCHEME = 'http'
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    LOG_LEVEL = 'INFO'
    
    # Production-specific settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'echo': False,
    }

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}