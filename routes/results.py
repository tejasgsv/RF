"""
Results routes - Retrieve analysis results
GET /results - Get all results
GET /results/<id> - Get specific result  
GET /download/<id>/<format> - Download results
"""
import logging
import io
import csv
import json
from flask import Blueprint, request, jsonify, send_file

from models.database import db, Analysis
from utils.errors import handle_api_error, error_response
from services.job_scheduler import get_scheduler
from flask import render_template

logger = logging.getLogger(__name__)

results_bp = Blueprint('results', __name__, url_prefix='/results')

scheduler = get_scheduler(max_workers=4)


@results_bp.route('', methods=['GET'])
@handle_api_error
def get_all_results():
    """
    Get all analysis results with pagination
    
    Query params:
    - page: Page number (default: 1)
    - per_page: Results per page (default: 20)
    - status: Filter by status (queued, processing, completed, failed)
    
    Returns:
    - results: List of analysis records
    - total: Total count
    - page: Current page
    - pages: Total pages
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status', None)
        
        # Build query
        query = Analysis.query
        
        if status_filter and status_filter in ['queued', 'processing', 'completed', 'failed']:
            query = query.filter_by(status=status_filter)
        
        # Order by newest first
        query = query.order_by(Analysis.created_at.desc())
        
        # Paginate
        paginated = query.paginate(page=page, per_page=per_page)
        
        results = [analysis.to_dict() for analysis in paginated.items]
        
        return jsonify({
            'results': results,
            'total': paginated.total,
            'page': page,
            'per_page': per_page,
            'pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching results: {e}")
        raise


@results_bp.route('/<analysis_id>', methods=['GET'])
@handle_api_error
def get_result(analysis_id):
    """
    Get specific analysis result
    
    Returns:
    - Analysis record with results
    """
    try:
        analysis = Analysis.query.filter_by(id=analysis_id).first()
        
        if not analysis:
            return error_response('Analysis not found', 404)
        
        # If still processing, check job status
        if analysis.status == 'processing' and analysis.job_id:
            job_status = scheduler.get_job_status(analysis.job_id)
            if job_status:
                return jsonify({
                    **analysis.to_dict(),
                    'job_status': job_status
                }), 200
        
        return jsonify(analysis.to_dict()), 200
    except Exception as e:
        logger.error(f"Error fetching result {analysis_id}: {e}")
        raise


@results_bp.route('/view/<analysis_id>', methods=['GET'])
def view_result_page(analysis_id):
    """Render HTML details page for an analysis (JS will fetch JSON)"""
    try:
        return render_template('result_view.html')
    except Exception as e:
        logger.error(f"Error rendering result view for {analysis_id}: {e}")
        raise


@results_bp.route('/<analysis_id>/status', methods=['GET'])
@handle_api_error
def get_result_status(analysis_id):
    """
    Get just the status of an analysis
    
    Returns:
    - status: Current status
    - progress: If processing, progress percentage
    - message: Status message
    """
    try:
        analysis = Analysis.query.filter_by(id=analysis_id).first()
        
        if not analysis:
            return error_response('Analysis not found', 404)
        
        response = {
            'analysis_id': analysis_id,
            'status': analysis.status,
            'file_type': analysis.file_type,
            'filename': analysis.filename,
            'created_at': analysis.created_at.isoformat(),
        }
        
        # If processing, get job status
        if analysis.status == 'processing' and analysis.job_id:
            job_status = scheduler.get_job_status(analysis.job_id)
            if job_status:
                response['job_status'] = job_status
                response['progress'] = job_status.get('progress', 0)
        
        # If completed, add result summary
        if analysis.status == 'completed' and analysis.results_json:
            try:
                results = json.loads(analysis.results_json)
                response['result_summary'] = {
                    'metrics_count': len(results),
                    'has_visualization': 'visualization' in results
                }
            except:
                pass
        
        # If failed, add error message
        if analysis.status == 'failed':
            response['error_message'] = analysis.error_message
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error fetching status {analysis_id}: {e}")
        raise


@results_bp.route('/<analysis_id>/download/<format>', methods=['GET'])
@handle_api_error
def download_result(analysis_id, format):
    """
    Download analysis results in specified format
    
    Formats:
    - json: Raw JSON results
    - csv: CSV table format
    - txt: Text summary
    
    Returns:
    - File for download
    """
    try:
        if format not in ['json', 'csv', 'txt']:
            return error_response(f'Unsupported format: {format}', 400)
        
        analysis = Analysis.query.filter_by(id=analysis_id).first()
        
        if not analysis:
            return error_response('Analysis not found', 404)
        
        if analysis.status != 'completed':
            return error_response(
                f'Analysis not completed. Status: {analysis.status}',
                400
            )
        
        try:
            results = json.loads(analysis.results_json) if analysis.results_json else {}
        except:
            return error_response('Failed to parse results', 500)
        
        # Generate download content
        if format == 'json':
            content = json.dumps(results, indent=2)
            mimetype = 'application/json'
            filename = f"{analysis_id}_results.json"
        
        elif format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['Metric', 'Value'])
            
            # Flatten results and write
            for key, value in results.items():
                if not isinstance(value, (dict, list)):
                    writer.writerow([key, str(value)])
            
            content = output.getvalue()
            mimetype = 'text/csv'
            filename = f"{analysis_id}_results.csv"
        
        else:  # txt
            lines = [
                f"Analysis Results: {analysis_id}",
                f"File Type: {analysis.file_type}",
                f"Filename: {analysis.filename}",
                f"Created: {analysis.created_at.isoformat()}",
                f"Processing Time: {analysis.processing_time_seconds}s" if analysis.processing_time_seconds else "",
                "",
                "Metrics:",
                "-" * 40
            ]
            
            for key, value in results.items():
                if not isinstance(value, (dict, list)):
                    lines.append(f"{key}: {value}")
            
            content = "\n".join(filter(None, lines))
            mimetype = 'text/plain'
            filename = f"{analysis_id}_results.txt"
        
        # Return file
        return send_file(
            io.BytesIO(content.encode() if isinstance(content, str) else content),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error downloading result {analysis_id}: {e}")
        raise
