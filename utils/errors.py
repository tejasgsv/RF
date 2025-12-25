"""
Error handling and standardized responses
"""
import logging
from functools import wraps
from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base API error class"""
    def __init__(self, message: str, status_code: int = 400, payload: dict = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload or {}
    
    def to_dict(self):
        rv = {'error': self.message, 'success': False}
        rv.update(self.payload)
        return rv

class ValidationError(APIError):
    """Validation error (400)"""
    def __init__(self, message: str, payload: dict = None):
        super().__init__(message, 400, payload)

class NotFoundError(APIError):
    """Resource not found (404)"""
    def __init__(self, message: str, payload: dict = None):
        super().__init__(message, 404, payload)

class ProcessingError(APIError):
    """Processing error (500)"""
    def __init__(self, message: str, payload: dict = None):
        super().__init__(message, 500, payload)

class RateLimitError(APIError):
    """Rate limit exceeded (429)"""
    def __init__(self, message: str = "Too many requests", payload: dict = None):
        super().__init__(message, 429, payload)

def success_response(data: dict = None, message: str = "Success", status_code: int = 200):
    """Standardized success response"""
    response = {
        'success': True,
        'message': message,
        'data': data or {}
    }
    return jsonify(response), status_code

def error_response(error: APIError):
    """Standardized error response"""
    response = error.to_dict()
    logger.warning(f"API Error ({error.status_code}): {error.message}")
    return jsonify(response), error.status_code

def handle_api_error(f):
    """Decorator to handle API errors in route handlers"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            return error_response(e)
        except HTTPException as e:
            return jsonify({
                'success': False,
                'error': e.description or str(e),
                'status_code': e.code
            }), e.code
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': 'Internal server error',
                'status_code': 500
            }), 500
    
    return decorated_function

def register_error_handlers(app):
    """Register error handlers with Flask app"""
    
    @app.errorhandler(APIError)
    def handle_api_error_handler(error):
        return error_response(error)
    
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({
            'success': False,
            'error': 'Resource not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(e):
        logger.error(f"Internal server error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'status_code': 500
        }), 500
    
    @app.errorhandler(413)
    def handle_request_entity_too_large(e):
        return jsonify({
            'success': False,
            'error': 'File too large',
            'status_code': 413
        }), 413
