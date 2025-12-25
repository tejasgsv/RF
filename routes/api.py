"""
API routes - Statistics, history, and monitoring endpoints
GET /api/progress/<id> - Get job progress
GET /api/statistics - Get overall statistics
GET /api/history - Get analysis history
"""
import logging
from flask import Blueprint, request, jsonify, send_file
import os
from sqlalchemy import func
from datetime import datetime, timedelta

from models.database import db, Analysis, AnalysisStatistics
from utils.errors import handle_api_error, error_response
from services.job_scheduler import get_scheduler

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

scheduler = get_scheduler(max_workers=4)


@api_bp.route('/progress/<analysis_id>', methods=['GET'])
@handle_api_error
def get_progress(analysis_id):
    """
    Get analysis progress
    
    Returns:
    - status: Current status
    - progress: Progress percentage (0-100)
    - message: Status message
    - elapsed_time: Seconds elapsed
    """
    try:
        analysis = Analysis.query.filter_by(id=analysis_id).first()
        
        if not analysis:
            return error_response('Analysis not found', 404)
        
        # Calculate elapsed time
        elapsed = 0
        if analysis.created_at:
            if analysis.completed_at:
                elapsed = (analysis.completed_at - analysis.created_at).total_seconds()
            else:
                elapsed = (datetime.utcnow() - analysis.created_at).total_seconds()
        
        response = {
            'analysis_id': analysis_id,
            'status': analysis.status,
            'elapsed_time': round(elapsed, 2),
            'created_at': analysis.created_at.isoformat() if analysis.created_at else None,
        }
        
        # Get job progress if processing
        if analysis.status == 'processing' and analysis.job_id:
            job_status = scheduler.get_job_status(analysis.job_id)
            if job_status:
                response['progress'] = job_status.get('progress', 0)
                response['message'] = job_status.get('message', 'Processing...')
            else:
                response['progress'] = 50
                response['message'] = 'Processing...'
        
        elif analysis.status == 'completed':
            response['progress'] = 100
            response['message'] = 'Completed'
            response['completed_at'] = analysis.completed_at.isoformat() if analysis.completed_at else None
        
        elif analysis.status == 'failed':
            response['progress'] = 0
            response['message'] = analysis.error_message or 'Analysis failed'
            response['error'] = analysis.error_message
        
        elif analysis.status == 'queued':
            response['progress'] = 0
            response['message'] = 'Queued for processing'
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting progress for {analysis_id}: {e}")
        raise


@api_bp.route('/statistics', methods=['GET'])
@handle_api_error
def get_statistics():
    """
    Get overall statistics
    
    Returns:
    - total_analyses: Total count
    - completed: Completed count
    - failed: Failed count
    - processing: Currently processing
    - success_rate: Percentage successful
    - avg_processing_time: Average seconds
    - by_type: Breakdown by file type
    """
    try:
        # Get overall stats
        total = db.session.query(func.count(Analysis.id)).scalar() or 0
        completed = db.session.query(func.count(Analysis.id)).filter_by(
            status='completed'
        ).scalar() or 0
        failed = db.session.query(func.count(Analysis.id)).filter_by(
            status='failed'
        ).scalar() or 0
        processing = db.session.query(func.count(Analysis.id)).filter_by(
            status='processing'
        ).scalar() or 0
        queued = db.session.query(func.count(Analysis.id)).filter_by(
            status='queued'
        ).scalar() or 0
        
        # Calculate average processing time
        avg_time = 0
        if completed > 0:
            avg_time_result = db.session.query(
                func.avg(Analysis.processing_time_seconds)
            ).filter_by(status='completed').scalar()
            avg_time = float(avg_time_result) if avg_time_result else 0
        
        # Success rate
        success_rate = (completed / total * 100) if total > 0 else 0
        
        # Breakdown by file type
        by_type = {}
        for file_type in ['video', 'image', 'document']:
            type_count = db.session.query(func.count(Analysis.id)).filter_by(
                file_type=file_type
            ).scalar() or 0
            type_completed = db.session.query(func.count(Analysis.id)).filter_by(
                file_type=file_type,
                status='completed'
            ).scalar() or 0
            
            by_type[file_type] = {
                'total': type_count,
                'completed': type_completed,
                'success_rate': (type_completed / type_count * 100) if type_count > 0 else 0
            }
        
        return jsonify({
            'total_analyses': total,
            'completed': completed,
            'failed': failed,
            'processing': processing,
            'queued': queued,
            'success_rate': round(success_rate, 2),
            'avg_processing_time': round(avg_time, 2),
            'by_file_type': by_type,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise


@api_bp.route('/history', methods=['GET'])
@handle_api_error
def get_history():
    """
    Get analysis history
    
    Query params:
    - days: Number of days to include (default: 7)
    - file_type: Filter by file type
    - status: Filter by status
    - limit: Max results (default: 100)
    
    Returns:
    - history: List of analyses
    - total: Total count
    """
    try:
        days = request.args.get('days', 7, type=int)
        file_type = request.args.get('file_type', None)
        status = request.args.get('status', None)
        limit = request.args.get('limit', 100, type=int)
        
        # Build query
        since = datetime.utcnow() - timedelta(days=days)
        query = Analysis.query.filter(Analysis.created_at >= since)
        
        if file_type:
            query = query.filter_by(file_type=file_type)
        
        if status:
            query = query.filter_by(status=status)
        
        # Order by newest first and limit
        query = query.order_by(Analysis.created_at.desc()).limit(limit)
        
        history = [analysis.to_dict() for analysis in query.all()]
        
        return jsonify({
            'history': history,
            'total': len(history),
            'days': days,
            'filters': {
                'file_type': file_type,
                'status': status
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise


@api_bp.route('/stats/daily', methods=['GET'])
@handle_api_error
def get_daily_stats():
    """
    Get daily statistics for the past N days
    
    Query params:
    - days: Number of days (default: 30)
    
    Returns:
    - daily: Array of daily stats
    """
    try:
        days = request.args.get('days', 30, type=int)
        
        stats = []
        for i in range(days):
            date = datetime.utcnow().date() - timedelta(days=i)
            start = datetime.combine(date, datetime.min.time())
            end = start + timedelta(days=1)
            
            day_total = db.session.query(func.count(Analysis.id)).filter(
                Analysis.created_at >= start,
                Analysis.created_at < end
            ).scalar() or 0
            
            day_completed = db.session.query(func.count(Analysis.id)).filter(
                Analysis.created_at >= start,
                Analysis.created_at < end,
                Analysis.status == 'completed'
            ).scalar() or 0
            
            stats.append({
                'date': date.isoformat(),
                'total': day_total,
                'completed': day_completed,
                'failed': db.session.query(func.count(Analysis.id)).filter(
                    Analysis.created_at >= start,
                    Analysis.created_at < end,
                    Analysis.status == 'failed'
                ).scalar() or 0
            })
        
        return jsonify({
            'daily_stats': stats,
            'days': days
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting daily stats: {e}")
        raise


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@api_bp.route('/download/<analysis_id>', methods=['GET'])
@handle_api_error
def download_uploaded_file(analysis_id):
    """Download the original uploaded file for an analysis"""
    try:
        analysis = Analysis.query.filter_by(id=analysis_id).first()
        if not analysis:
            return error_response('Analysis not found', 404)

        filepath = analysis.filepath
        if not filepath or not os.path.exists(filepath):
            return error_response('File not available', 404)

        # Use send_file to stream the file back
        return send_file(filepath, as_attachment=True, download_name=analysis.filename)
    except Exception as e:
        logger.error(f"Error serving upload for {analysis_id}: {e}")
        raise


@api_bp.route('/thumbnail/<analysis_id>', methods=['GET'])
@handle_api_error
def get_thumbnail(analysis_id):
    """Return generated thumbnail for an analysis if available"""
    try:
        analysis = Analysis.query.filter_by(id=analysis_id).first()
        if not analysis:
            return error_response('Analysis not found', 404)

        thumb_path = analysis.thumbnail
        if not thumb_path:
            return error_response('Thumbnail not available', 404)

        if not thumb_path or not os.path.exists(thumb_path):
            return error_response('Thumbnail file missing', 404)

        return send_file(thumb_path, as_attachment=False)
    except Exception as e:
        logger.error(f"Error serving thumbnail for {analysis_id}: {e}")
        raise
