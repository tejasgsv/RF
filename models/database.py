"""
Database models for analysis results and job tracking
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()


class Analysis(db.Model):
    """Store analysis job information and results"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.String(50), primary_key=True)
    file_type = db.Column(db.String(20), nullable=False)  # 'video', 'image', 'document'
    filename = db.Column(db.String(255), nullable=False)  # Secured filename
    filepath = db.Column(db.String(500), nullable=True)   # Full file path
    thumbnail = db.Column(db.String(500), nullable=True)  # Optional thumbnail path
    
    status = db.Column(
        db.String(20), 
        nullable=False, 
        default='queued'
    )  # queued, processing, completed, failed, timeout
    
    # Job tracking
    job_id = db.Column(db.String(50), nullable=True)  # Link to scheduler job
    
    # Results
    results_json = db.Column(db.Text, nullable=True)  # JSON string
    error_message = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    processing_time_seconds = db.Column(db.Float, nullable=True)
    
    # Metadata
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4 or IPv6
    user_agent = db.Column(db.String(500), nullable=True)
    
    def __repr__(self):
        return f'<Analysis {self.id} - {self.file_type}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        results = None
        if self.results_json:
            try:
                results = json.loads(self.results_json)
            except:
                results = self.results_json
        
        return {
            'id': self.id,
            'file_type': self.file_type,
            'filename': self.filename,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'processing_time': self.processing_time_seconds,
            'results': results,
            'error_message': self.error_message if self.status == 'failed' else None
        }

class AnalysisStatistics(db.Model):
    """Aggregate statistics for dashboard"""
    __tablename__ = 'analysis_statistics'
    
    id = db.Column(db.Integer, primary_key=True)
    stat_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    
    total_analyses = db.Column(db.Integer, default=0)
    successful_analyses = db.Column(db.Integer, default=0)
    failed_analyses = db.Column(db.Integer, default=0)
    
    total_processing_time = db.Column(db.Float, default=0.0)  # seconds
    total_data_processed = db.Column(db.Float, default=0.0)  # MB
    
    video_count = db.Column(db.Integer, default=0)
    image_count = db.Column(db.Integer, default=0)
    document_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<AnalysisStatistics {self.stat_date}>'
    
    @property
    def success_rate(self):
        if self.total_analyses == 0:
            return 0
        return round((self.successful_analyses / self.total_analyses) * 100, 2)
    
    @property
    def avg_processing_time(self):
        if self.successful_analyses == 0:
            return 0
        return round(self.total_processing_time / self.successful_analyses, 2)
    
    def to_dict(self):
        return {
            'date': self.stat_date.isoformat(),
            'total': self.total_analyses,
            'successful': self.successful_analyses,
            'failed': self.failed_analyses,
            'success_rate': self.success_rate,
            'avg_processing_time': self.avg_processing_time,
            'data_processed': round(self.total_data_processed, 2),
            'by_type': {
                'videos': self.video_count,
                'images': self.image_count,
                'documents': self.document_count
            }
        }
