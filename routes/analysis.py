"""
Analysis routes - Handle file uploads and start analysis jobs
POST /analyze - Submit analysis job
"""
import logging
import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, current_app
from werkzeug.datastructures import FileStorage

from config import config
from models.database import db, Analysis
from utils.validators import FileValidator, FileManager, generate_analysis_id
from services.upload_service import upload_service
from utils.errors import ValidationError, handle_api_error, error_response
from services.job_scheduler import get_scheduler
from services.video_service import VideoAnalysisService
from services.image_service import ImageAnalysisService
from services.office_service import OfficeAnalysisService
from services.yolo_norfair_service import default_yolo_norfair_service

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__)

# Initialize services
video_service = VideoAnalysisService()
image_service = ImageAnalysisService()
office_service = OfficeAnalysisService()

def smart_video_analyze(filepath: str) -> dict:
    """
    Smart video analyzer: try YOLO+Norfair first, fallback to VideoAnalysisService
    """
    try:
        # Attempt YOLO+Norfair (high accuracy people tracking)
        logger.info(f"Attempting YOLO+Norfair analysis for {filepath}")
        result = default_yolo_norfair_service.analyze(filepath, max_frames=500)
        if result.get('success'):
            logger.info(f"YOLO+Norfair succeeded: {result.get('unique_people')} unique people")
            return result
        else:
            logger.warning(f"YOLO+Norfair failed: {result.get('error')}")
    except Exception as e:
        logger.warning(f"YOLO+Norfair exception: {e}")

    # Fallback to traditional VideoAnalysisService
    logger.info(f"Falling back to traditional VideoAnalysisService for {filepath}")
    try:
        result = video_service.analyze(filepath)
        if result.get('success'):
            logger.info(f"VideoAnalysisService succeeded: {result.get('unique_people')} unique people")
            return result
    except Exception as e:
        logger.error(f"VideoAnalysisService also failed: {e}")
        return {'success': False, 'error': str(e)}

    return result

# File validators
file_validator = FileValidator(config['development'])
file_manager = FileManager(config['development'])

# Job scheduler
scheduler = get_scheduler(max_workers=4)


@analysis_bp.route('/', methods=['GET'])
def index():
    """Render main analysis dashboard"""
    return render_template('modern_dashboard.html')


@analysis_bp.route('/analytics', methods=['GET'])
def analytics():
    """Render analytics page"""
    return render_template('analytics.html')


@analysis_bp.route('/analyze', methods=['POST'])
@handle_api_error
def analyze_file():
    """
    Submit file for analysis
    
    Expected:
    - file: FileStorage object
    - file_type: 'video' | 'image' | 'document'
    
    Returns:
    - analysis_id: ID for tracking
    - status: 'queued' | 'error'
    """
    # Validate request has file
    if 'file' not in request.files:
        raise ValidationError('No file provided', {'field': 'file'})
    
    file = request.files['file']
    if not isinstance(file, FileStorage):
        raise ValidationError('Invalid file object')
    
    # Get file type from form
    file_type = request.form.get('file_type', 'video').lower()
    
    if file_type not in ['video', 'image', 'document']:
        raise ValidationError(
            f'Invalid file type: {file_type}',
            {'field': 'file_type', 'allowed': ['video', 'image', 'document']}
        )
    
    # Use UploadService to validate, save and prepare thumbnails/metadata
    try:
        upload_meta = upload_service.process_upload(file, file_type)
        secured_filename = upload_meta.get('filename')
        filepath = upload_meta.get('filepath')
        thumbnail = upload_meta.get('thumbnail')
        size_mb = upload_meta.get('size_mb', 0.0)
        logger.info(f"File processed: {filepath} (thumb={thumbnail})")
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Failed to process upload: {e}")
        raise ValidationError('Failed to save file', {'error': str(e)})
    
    # Create analysis record
    try:
        analysis_id = generate_analysis_id()
        
        analysis = Analysis(
            id=analysis_id,
            file_type=file_type,
            filename=secured_filename,
            filepath=filepath,
            thumbnail=thumbnail if 'thumbnail' in locals() else None,
            status='queued',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        logger.info(f"Analysis created: {analysis_id} - Type: {file_type}")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create analysis record: {e}")
        # Clean up uploaded file
        try:
            file_manager.cleanup_file(filepath)
        except:
            pass
        raise ValidationError('Failed to create analysis record', {'error': str(e)})
    
    # Submit to job scheduler
    try:
        # Choose service based on file type
        if file_type == 'video':
            service_method = smart_video_analyze
        elif file_type == 'image':
            service_method = image_service.analyze_image
        else:  # document
            service_method = office_service.analyze_document
        
        # Capture application instance so background thread can push app context
        app_obj = current_app._get_current_object()

        # Wrap service method to capture results
        def analysis_task_wrapper():
            """Wrapper to execute analysis and save results with proper app context"""
            try:
                result = service_method(filepath)
                # If service indicates failure, record error instead
                if isinstance(result, dict) and not result.get('success', True):
                    err = result.get('error', 'Unknown error')
                    with app_obj.app_context():
                        update_analysis_error(analysis_id, str(err))
                    logger.error(f"Service reported failure for {analysis_id}: {err}")
                    return result

                # Update analysis record with results inside app context
                try:
                    with app_obj.app_context():
                        update_analysis_results(analysis_id, result)
                except Exception as e:
                    logger.error(f"Failed to update results in app context: {e}")
                return result
            except Exception as e:
                logger.error(f"Service error: {e}")
                # Update analysis with error inside app context
                try:
                    with app_obj.app_context():
                        update_analysis_error(analysis_id, str(e))
                except Exception as ex:
                    logger.error(f"Failed to update error in app context: {ex}")
                raise
        
        # Submit job with timeout
        timeout_seconds = config['development'].PROCESSING_TIMEOUTS.get(
            file_type, 300
        )
        
        job_id = scheduler.submit_job(
            analysis_task_wrapper,
            timeout=timeout_seconds
        )
        
        # Update analysis with job_id
        analysis.job_id = job_id
        analysis.status = 'processing'
        analysis.started_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Job submitted: {job_id} for analysis {analysis_id}")
        
        return jsonify({
            'analysis_id': analysis_id,
            'job_id': job_id,
            'status': 'queued',
            'message': f'{file_type.capitalize()} analysis queued successfully',
            'file_type': file_type,
            'filename': secured_filename
        }), 202
        
    except Exception as e:
        logger.error(f"Failed to submit job: {e}")
        # Update analysis record with error
        try:
            analysis.status = 'failed'
            analysis.error_message = str(e)
            db.session.commit()
        except:
            pass
        
        raise ValidationError('Failed to queue analysis', {'error': str(e)})


def update_analysis_results(analysis_id: str, results: dict):
    """Update analysis record with completed results"""
    try:
        import json
        from datetime import datetime
        
        analysis = Analysis.query.filter_by(id=analysis_id).first()
        if analysis:
            analysis.results_json = json.dumps(results)
            analysis.status = 'completed'
            analysis.completed_at = datetime.utcnow()
            
            # Calculate processing time
            if analysis.started_at:
                processing_time = (analysis.completed_at - analysis.started_at).total_seconds()
                analysis.processing_time_seconds = processing_time
            
            db.session.commit()
            logger.info(f"Analysis {analysis_id} completed")
    except Exception as e:
        logger.error(f"Failed to update analysis results: {e}")


def update_analysis_error(analysis_id: str, error_message: str):
    """Update analysis record with error"""
    try:
        from datetime import datetime
        
        analysis = Analysis.query.filter_by(id=analysis_id).first()
        if analysis:
            analysis.status = 'failed'
            analysis.error_message = error_message
            analysis.completed_at = datetime.utcnow()
            
            if analysis.started_at:
                processing_time = (analysis.completed_at - analysis.started_at).total_seconds()
                analysis.processing_time_seconds = processing_time
            
            db.session.commit()
            logger.error(f"Analysis {analysis_id} failed: {error_message}")
    except Exception as e:
        logger.error(f"Failed to update analysis error: {e}")


@analysis_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request"""
    return error_response('Bad request', 400, {'details': str(error)})


@analysis_bp.errorhandler(404)
def not_found(error):
    """Handle not found"""
    return error_response('Not found', 404)


@analysis_bp.errorhandler(500)
def server_error(error):
    """Handle server error"""
    logger.error(f"Server error: {error}")
    return error_response('Internal server error', 500)
