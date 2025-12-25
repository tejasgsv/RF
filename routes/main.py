from flask import Blueprint, render_template, request, jsonify, send_file, send_from_directory
import os
import csv
import io
import time
import threading
import logging
from datetime import datetime, timedelta
import json
from werkzeug.utils import secure_filename

from config import Config
from models.analysis import AnalysisResult, AnalyticsData
from services.video_service import VideoAnalysisService
from services.image_service import ImageAnalysisService
from services.diamond_service import DiamondAnalysisService
from services.office_service import OfficeAnalysisService

logger = logging.getLogger(__name__)

# Create blueprint
main_bp = Blueprint('main', __name__)

# Initialize services
config = Config()
video_service = VideoAnalysisService()
image_service = ImageAnalysisService()
diamond_service = DiamondAnalysisService()
office_service = OfficeAnalysisService()

# Global storage for analysis results and analytics
analysis_results = {}
analytics_data = AnalyticsData()

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_file_size(file, max_size):
    """Validate file size"""
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    return file_size <= max_size

@main_bp.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@main_bp.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@main_bp.route('/analyze', methods=['POST'])
def analyze():
    """Handle analysis requests for different file types"""
    try:
        file_type = request.form.get('type')

        if not file_type:
            return jsonify({'error': 'File type not specified', 'success': False}), 400

        if file_type == 'video':
            return handle_video_analysis()
        elif file_type == 'image':
            return handle_image_analysis()
        elif file_type == 'office':
            return handle_office_analysis()
        elif file_type == 'diamond':
            return handle_diamond_analysis()
        elif file_type == 'analytics':
            return handle_analytics_request()
        else:
            return jsonify({'error': 'Unsupported file type', 'success': False}), 400

    except Exception as e:
        logger.error(f"Error in analyze endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error', 'success': False}), 500

def handle_video_analysis():
    """Handle video file analysis"""
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': 'No file uploaded', 'success': False}), 400

    if not allowed_file(file.filename, config.ALLOWED_VIDEO_EXTENSIONS):
        return jsonify({'error': 'Invalid file type', 'success': False}), 400

    if not validate_file_size(file, config.MAX_CONTENT_LENGTH):
        return jsonify({'error': 'File too large', 'success': False}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(config.UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Generate unique analysis ID
    analysis_id = f"analysis_{int(time.time())}"

    # Create analysis result object
    analysis_result = AnalysisResult(
        analysis_id=analysis_id,
        file_type='video',
        filename=filename,
        status='pending'
    )
    analysis_results[analysis_id] = analysis_result

    # Start analysis in background thread
    thread = threading.Thread(target=process_video_analysis, args=(filepath, analysis_id))
    thread.start()

    return jsonify({
        'analysis_id': analysis_id,
        'message': 'Analysis started',
        'estimated_time': '25-30 seconds',
        'success': True
    })

def process_video_analysis(filepath, analysis_id):
    """Process video analysis in background thread"""
    try:
        analysis_result = analysis_results[analysis_id]
        analysis_result.status = 'processing'

        # Perform video analysis
        results = video_service.analyze_video(filepath)

        # Update analysis result
        analysis_result.complete(results, results['processing_time'])

        # Update analytics
        csv_size_mb = len(results.get('csv_data', '')) / (1024 * 1024)
        analytics_data.update(results['processing_time'], True, csv_size_mb)

        logger.info(f"Video analysis completed: {analysis_id}")

    except Exception as e:
        logger.error(f"Video analysis failed: {analysis_id} - {str(e)}")
        analysis_result = analysis_results.get(analysis_id)
        if analysis_result:
            analysis_result.fail(str(e))

def handle_image_analysis():
    """Handle image file analysis"""
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': 'No file uploaded', 'success': False}), 400

    if not allowed_file(file.filename, config.ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({'error': 'Invalid file type', 'success': False}), 400

    if not validate_file_size(file, config.MAX_CONTENT_LENGTH):
        return jsonify({'error': 'File too large', 'success': False}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(config.UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        # Perform image analysis
        results = image_service.analyze_image(filepath)

        # Update analytics
        analytics_data.update(results['processing_time'], True)

        # Clean up uploaded file
        os.remove(filepath)

        return jsonify(results)

    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        return jsonify({'error': 'Analysis failed', 'success': False}), 500

def handle_office_analysis():
    """Handle office document analysis"""
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': 'No file uploaded', 'success': False}), 400

    # For now, accept common office extensions
    allowed_office = {'doc', 'docx', 'pdf', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx'}
    if not allowed_file(file.filename, allowed_office):
        return jsonify({'error': 'Invalid file type', 'success': False}), 400

    if not validate_file_size(file, config.MAX_CONTENT_LENGTH):
        return jsonify({'error': 'File too large', 'success': False}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(config.UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        # Perform document analysis
        results = office_service.analyze_document(filepath)

        # Update analytics
        analytics_data.update(results['processing_time'], True)

        # Clean up uploaded file
        os.remove(filepath)

        return jsonify(results)

    except Exception as e:
        logger.error(f"Document analysis error: {str(e)}")
        return jsonify({'error': 'Analysis failed', 'success': False}), 500

def handle_diamond_analysis():
    """Handle diamond analysis"""
    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({'error': 'No file uploaded', 'success': False}), 400

    # Accept image files for diamond analysis
    if not allowed_file(file.filename, config.ALLOWED_IMAGE_EXTENSIONS):
        return jsonify({'error': 'Invalid file type', 'success': False}), 400

    if not validate_file_size(file, config.MAX_CONTENT_LENGTH):
        return jsonify({'error': 'File too large', 'success': False}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(config.UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        # Perform diamond analysis
        results = diamond_service.analyze_diamond(filepath)

        # Update analytics
        analytics_data.update(results['processing_time'], True)

        # Clean up uploaded file
        os.remove(filepath)

        return jsonify(results)

    except Exception as e:
        logger.error(f"Diamond analysis error: {str(e)}")
        return jsonify({'error': 'Analysis failed', 'success': False}), 500

def handle_analytics_request():
    """Handle analytics data request"""
    return jsonify({
        'total_analyses': analytics_data.total_analyses,
        'avg_processing_time': round(analytics_data.avg_processing_time, 1),
        'success_rate': round(analytics_data.success_rate, 1),
        'data_processed': round(analytics_data.data_processed_mb, 1),
        'success': True
    })

@main_bp.route('/check_analysis/<analysis_id>')
def check_analysis(analysis_id):
    """Check analysis progress"""
    if analysis_id not in analysis_results:
        return jsonify({'error': 'Analysis not found', 'success': False}), 404

    result = analysis_results[analysis_id]

    if result.status == 'completed':
        return jsonify({
            'unique_people': result.results.get('unique_people', 0),
            'total_objects': result.results.get('total_objects', 0),
            'total_frames': result.results.get('frames_analyzed', 0),
            'processing_time': result.processing_time,
            'video_duration': result.results.get('video_duration', 0),
            'csv_data': result.results.get('csv_data', ''),
            'csv_filename': result.results.get('csv_filename', ''),
            'success': True,
            'completed': True
        })
    elif result.status == 'failed':
        return jsonify({
            'error': result.error_message,
            'success': False,
            'completed': True
        })
    else:
        return jsonify({'completed': False, 'message': 'Analysis in progress...'})

@main_bp.route('/download_csv', methods=['POST'])
def download_csv():
    """Download CSV analysis results"""
    data = request.get_json()
    analysis_id = data.get('analysis_id')

    if not analysis_id or analysis_id not in analysis_results:
        return jsonify({'error': 'No analysis data found', 'success': False}), 404

    result = analysis_results[analysis_id]
    if result.status != 'completed':
        return jsonify({'error': 'Analysis not completed', 'success': False}), 400

    csv_data = result.results.get('csv_data', '')
    filename = result.results.get('csv_filename', 'analysis.csv')

    return send_file(
        io.BytesIO(csv_data.encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

@main_bp.route('/analytics')
def analytics_dashboard():
    """Serve the analytics dashboard"""
    return render_template('analytics.html')

@main_bp.route('/api/analytics/summary')
def analytics_summary():
    """Get analytics summary data"""
    try:
        # Calculate file type distribution
        file_type_distribution = {}
        success_rate_by_type = {}

        for analysis_id, result in analysis_results.items():
            file_type = result.file_type
            if file_type not in file_type_distribution:
                file_type_distribution[file_type] = 0
                success_rate_by_type[file_type] = {'completed': 0, 'total': 0}

            file_type_distribution[file_type] += 1
            success_rate_by_type[file_type]['total'] += 1
            if result.status == 'completed':
                success_rate_by_type[file_type]['completed'] += 1

        # Calculate success rates
        for file_type in success_rate_by_type:
            total = success_rate_by_type[file_type]['total']
            completed = success_rate_by_type[file_type]['completed']
            success_rate_by_type[file_type]['rate'] = round((completed / total * 100), 1) if total > 0 else 0

        # Calculate recent analyses (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_analyses = sum(1 for result in analysis_results.values()
                            if hasattr(result, 'timestamp') and result.timestamp and result.timestamp > recent_cutoff)

        return jsonify({
            'total_analyses': analytics_data.total_analyses,
            'avg_processing_time': round(analytics_data.avg_processing_time, 1),
            'success_rate': round(analytics_data.success_rate, 1),
            'data_processed_mb': round(analytics_data.data_processed_mb, 1),
            'file_type_distribution': file_type_distribution,
            'success_rate_by_type': success_rate_by_type,
            'recent_analyses_24h': recent_analyses,
            'success': True
        })

    except Exception as e:
        logger.error(f"Error in analytics summary: {str(e)}")
        return jsonify({'error': 'Failed to generate analytics summary', 'success': False}), 500

@main_bp.route('/api/analytics/history')
def analytics_history():
    """Get analysis history with pagination and filtering"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        file_type_filter = request.args.get('file_type', '')

        # Filter results
        filtered_results = []
        for analysis_id, result in analysis_results.items():
            if file_type_filter and result.file_type != file_type_filter:
                continue
            filtered_results.append({
                'analysis_id': analysis_id,
                'file_type': result.file_type,
                'filename': result.filename,
                'status': result.status,
                'processing_time': result.processing_time,
                'timestamp': result.created_at.isoformat() if hasattr(result, 'created_at') and result.created_at else None
            })

        # Sort by timestamp (newest first)
        filtered_results.sort(key=lambda x: x['timestamp'] or '', reverse=True)

        # Paginate
        total_results = len(filtered_results)
        total_pages = (total_results + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_results = filtered_results[start_idx:end_idx]

        return jsonify({
            'history': paginated_results,
            'current_page': page,
            'total_pages': total_pages,
            'total_results': total_results,
            'per_page': per_page,
            'success': True
        })

    except Exception as e:
        logger.error(f"Error in analytics history: {str(e)}")
        return jsonify({'error': 'Failed to retrieve analysis history', 'success': False}), 500
