from flask import Flask
import os
import logging
from config import Config, config
from routes.main import main_bp
from utils.helpers import setup_logging, ensure_upload_directory

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Ensure upload directory exists
    ensure_upload_directory()

    # Register blueprints
    app.register_blueprint(main_bp)

    logger.info(f"Application created with config: {config_name}")
    logger.info(f"Debug mode: {app.config['DEBUG']}")
    logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")

    return app

# Create application instance
app = create_app(os.environ.get('FLASK_ENV', 'default'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(
        debug=app.config['DEBUG'],
        host='0.0.0.0',
        port=port,
        threaded=app.config.get('THREADED', True)
    )
