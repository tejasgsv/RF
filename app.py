"""
AI Analytics Platform - Main Application
Production-ready Flask application with clean architecture
"""
import os
import logging
import sys
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

from config import config
from models.database import db
from utils.errors import register_error_handlers
from utils.helpers import setup_logging, ensure_directories

def create_app(config_name: str = None) -> Flask:
    """
    Application factory
    
    Args:
        config_name: Configuration name ('development', 'production', 'testing')
        
    Returns:
        Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask app
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Setup logging
    setup_logging(app)
    logger = logging.getLogger(__name__)
    
    # Ensure directories exist
    ensure_directories(app)
    
    # Initialize database
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from routes.analysis import analysis_bp
    from routes.results import results_bp
    from routes.api import api_bp
    
    app.register_blueprint(analysis_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Simple health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': app.config.get('APP_VERSION', '3.0.0')
        }), 200
    
    # Request logging middleware
    @app.before_request
    def log_request():
        request.start_time = datetime.utcnow()
    
    @app.after_request
    def log_response(response):
        if hasattr(request, 'start_time'):
            elapsed = (datetime.utcnow() - request.start_time).total_seconds()
            logger.info(
                f"{request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Time: {elapsed:.3f}s"
            )
        return response
    
    logger.info(f"Application initialized - Config: {config_name} - Version: {app.config.get('APP_VERSION')}")
    
    return app

# Create application instance for production
app = create_app()

if __name__ == '__main__':
    config_name = sys.argv[1] if len(sys.argv) > 1 else 'development'
    app = create_app(config_name)
    
    # Get configuration
    port = int(os.environ.get('PORT', 5000))
    debug = app.config.get('DEBUG', False)
    
    print(f"\n{'='*60}")
    print(f"AI Analytics Platform")
    print(f"Version: {app.config.get('APP_VERSION')}")
    print(f"Config: {config_name}")
    print(f"Debug: {debug}")
    print(f"Running on: http://0.0.0.0:{port}")
    print(f"{'='*60}\n")
    
    # Run with threaded support
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True,
        use_reloader=debug
    )
