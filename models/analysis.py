from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class AnalysisResult:
    """Data model for analysis results"""
    analysis_id: str
    file_type: str
    filename: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    results: Optional[Dict] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def complete(self, results: Dict, processing_time: float):
        self.status = 'completed'
        self.results = results
        self.processing_time = processing_time
        self.completed_at = datetime.now()

    def fail(self, error_message: str):
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = datetime.now()

@dataclass
class AnalyticsData:
    """Data model for application analytics"""
    total_analyses: int = 0
    total_processing_time: float = 0.0
    successful_analyses: int = 0
    data_processed_mb: float = 0.0

    def update(self, processing_time: float, success: bool, data_size_mb: float = 0):
        self.total_analyses += 1
        self.total_processing_time += processing_time
        if success:
            self.successful_analyses += 1
        self.data_processed_mb += data_size_mb

    @property
    def success_rate(self) -> float:
        return (self.successful_analyses / max(self.total_analyses, 1)) * 100

    @property
    def avg_processing_time(self) -> float:
        return self.total_processing_time / max(self.total_analyses, 1)
