"""
Background job scheduling and monitoring
"""
import logging
import threading
import uuid
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)

class JobStatus:
    """Job status constants"""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    TIMEOUT = 'timeout'

class JobScheduler:
    """
    Manage background jobs with proper threading and timeout handling
    Uses ThreadPoolExecutor for bounded concurrency
    """
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def submit_job(self, task_func: Callable, *args, timeout: int = 600, **kwargs) -> str:
        """
        Submit a background job
        
        Args:
            task_func: Callable to execute
            *args: Positional arguments for task
            timeout: Timeout in seconds (default 10 minutes)
            **kwargs: Keyword arguments for task
            
        Returns:
            job_id: Unique identifier for this job
        """
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        
        with self.lock:
            self.jobs[job_id] = {
                'status': JobStatus.PENDING,
                'result': None,
                'error': None,
                'progress': 0,
                'created_at': datetime.utcnow(),
                'started_at': None,
                'completed_at': None,
                'task_func': task_func,
                'args': args,
                'kwargs': kwargs,
                'timeout': timeout,
                'future': None
            }
        
        # Submit to executor
        def execute_with_context():
            with self.lock:
                self.jobs[job_id]['status'] = JobStatus.PROCESSING
                self.jobs[job_id]['started_at'] = datetime.utcnow()
            
            try:
                result = task_func(*args, **kwargs)
                with self.lock:
                    self.jobs[job_id]['result'] = result
                    self.jobs[job_id]['status'] = JobStatus.COMPLETED
                    self.jobs[job_id]['completed_at'] = datetime.utcnow()
                logger.info(f"Job {job_id} completed successfully")
            except Exception as e:
                logger.error(f"Job {job_id} failed: {str(e)}")
                with self.lock:
                    self.jobs[job_id]['status'] = JobStatus.FAILED
                    self.jobs[job_id]['error'] = str(e)
                    self.jobs[job_id]['completed_at'] = datetime.utcnow()
        
        future = self.executor.submit(execute_with_context)
        
        with self.lock:
            self.jobs[job_id]['future'] = future
        
        logger.info(f"Job {job_id} submitted")
        return job_id
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status and progress"""
        with self.lock:
            if job_id not in self.jobs:
                return {'error': 'Job not found'}
            
            job = self.jobs[job_id]
            
            # Check for timeout
            if job['status'] == JobStatus.PROCESSING and job['timeout']:
                elapsed = (datetime.utcnow() - job['started_at']).total_seconds()
                if elapsed > job['timeout']:
                    job['status'] = JobStatus.TIMEOUT
                    job['error'] = f'Job timed out after {elapsed:.0f} seconds'
                    logger.warning(f"Job {job_id} timed out")
            
            return {
                'job_id': job_id,
                'status': job['status'],
                'progress': job['progress'],
                'result': job['result'],
                'error': job['error'],
                'created_at': job['created_at'].isoformat(),
                'started_at': job['started_at'].isoformat() if job['started_at'] else None,
                'completed_at': job['completed_at'].isoformat() if job['completed_at'] else None
            }
    
    def get_job_result(self, job_id: str) -> Any:
        """Get job result (if completed)"""
        status = self.get_job_status(job_id)
        
        if status.get('status') == JobStatus.COMPLETED:
            return status.get('result')
        elif status.get('status') == JobStatus.FAILED:
            raise Exception(f"Job failed: {status.get('error')}")
        elif status.get('status') == JobStatus.TIMEOUT:
            raise TimeoutError(f"Job timeout: {status.get('error')}")
        else:
            raise ValueError(f"Job still processing or not found")
    
    def update_job_progress(self, job_id: str, progress: int):
        """Update job progress (0-100)"""
        if 0 <= progress <= 100:
            with self.lock:
                if job_id in self.jobs:
                    self.jobs[job_id]['progress'] = progress
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending/processing job"""
        with self.lock:
            if job_id not in self.jobs:
                return False
            
            job = self.jobs[job_id]
            if job['status'] in [JobStatus.PENDING, JobStatus.PROCESSING]:
                if job['future']:
                    job['future'].cancel()
                job['status'] = JobStatus.FAILED
                job['error'] = 'Job cancelled by user'
                job['completed_at'] = datetime.utcnow()
                return True
        
        return False
    
    def cleanup_completed_jobs(self, keep_hours: int = 24) -> int:
        """Remove completed jobs older than keep_hours"""
        import time
        cutoff = datetime.utcnow().timestamp() - (keep_hours * 3600)
        deleted = 0
        
        with self.lock:
            job_ids_to_delete = [
                job_id for job_id, job in self.jobs.items()
                if job['status'] in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.TIMEOUT]
                and job['completed_at']
                and job['completed_at'].timestamp() < cutoff
            ]
            
            for job_id in job_ids_to_delete:
                del self.jobs[job_id]
                deleted += 1
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} old jobs")
        
        return deleted
    
    def shutdown(self):
        """Graceful shutdown of executor"""
        self.executor.shutdown(wait=True)
        logger.info("Job scheduler shutdown complete")

# Global job scheduler instance
_scheduler = None

def get_scheduler(max_workers: int = 4) -> JobScheduler:
    """Get or create global job scheduler"""
    global _scheduler
    if _scheduler is None:
        _scheduler = JobScheduler(max_workers=max_workers)
    return _scheduler
