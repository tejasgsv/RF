# AI Analytics Platform - Professional Startup Guide

## ✅ Status: READY TO RUN

The application has been successfully refactored into a production-ready platform with:
- ✅ Factory pattern application architecture
- ✅ SQLAlchemy database persistence
- ✅ Job scheduler with bounded concurrency
- ✅ Modular blueprint routes
- ✅ Comprehensive error handling
- ✅ File validation before save
- ✅ RESTful API endpoints

## System Requirements

- **Python**: 3.8+ (tested with 3.10, 3.11, 3.12)
- **Virtual Environment**: Recommended (`.venv` already configured)
- **Disk Space**: 500MB+ for uploads
- **RAM**: 4GB+ for video processing

## Installation

### 1. Verify Virtual Environment
```bash
# On Windows
.venv\Scripts\activate

# On macOS/Linux
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
# All dependencies from requirements.txt
pip install -r requirements.txt

# Or individually
pip install Flask==3.0.0
pip install Flask-SQLAlchemy==3.1.1
pip install Flask-Cors==4.0.0
pip install opencv-python==4.8.1.78
pip install pandas==2.1.3
pip install numpy==1.24.3
pip install APScheduler==3.10.4
pip install python-dotenv==1.0.0
```

### 3. Verify Installation
```bash
python verify_setup.py
```

**Expected Output**:
```
OK: config
OK: database
OK: errors
OK: validators
OK: job_scheduler
```

## Running the Application

### Quick Start (Development)
```bash
# Activate virtual environment
.venv\Scripts\activate

# Run the app
python app.py
```

**Expected Output**:
```
============================================================
AI Analytics Platform
Version: 3.0.0
Config: development
Debug: True
Running on: http://0.0.0.0:5000
============================================================
```

### Production Start
```bash
set FLASK_ENV=production
set DATABASE_URL=postgresql://user:pass@localhost/dbname
python app.py
```

### With Custom Port
```bash
set PORT=8080
python app.py
```

## API Quick Reference

### 1. Submit Analysis
**Endpoint**: `POST /analyze`

```bash
curl -X POST http://localhost:5000/analyze \
  -F "file=@sample.mp4" \
  -F "file_type=video"
```

**Response (202 Accepted)**:
```json
{
    "analysis_id": "abc123def456",
    "job_id": "job_xyz789",
    "status": "queued",
    "file_type": "video",
    "filename": "20231128_101530_sample.mp4"
}
```

### 2. Check Progress
**Endpoint**: `GET /api/progress/<analysis_id>`

```bash
curl http://localhost:5000/api/progress/abc123def456
```

**Response**:
```json
{
    "analysis_id": "abc123def456",
    "status": "processing",
    "progress": 45,
    "message": "Processing frame 1250 of 2500",
    "elapsed_time": 23.45
}
```

### 3. Get Results
**Endpoint**: `GET /results/<analysis_id>`

```bash
curl http://localhost:5000/results/abc123def456
```

**Response**:
```json
{
    "id": "abc123def456",
    "status": "completed",
    "filename": "20231128_101530_sample.mp4",
    "file_type": "video",
    "results": {
        "total_people_detected": 5,
        "total_faces_detected": 4,
        "total_heads_detected": 5,
        "frames_analyzed": 450,
        "processing_time_seconds": 23.45
    }
}
```

### 4. Download Results
**Endpoint**: `GET /results/<analysis_id>/download/<format>`

```bash
# As JSON
curl http://localhost:5000/results/abc123def456/download/json \
  -o results.json

# As CSV
curl http://localhost:5000/results/abc123def456/download/csv \
  -o results.csv

# As Text
curl http://localhost:5000/results/abc123def456/download/txt \
  -o results.txt
```

### 5. Get Statistics
**Endpoint**: `GET /api/statistics`

```bash
curl http://localhost:5000/api/statistics
```

**Response**:
```json
{
    "total_analyses": 42,
    "completed": 38,
    "failed": 2,
    "processing": 2,
    "queued": 0,
    "success_rate": 90.48,
    "avg_processing_time": 45.23,
    "by_file_type": {
        "video": { "total": 30, "completed": 28, "success_rate": 93.33 },
        "image": { "total": 10, "completed": 9, "success_rate": 90.0 },
        "document": { "total": 2, "completed": 1, "success_rate": 50.0 }
    }
}
```

### 6. Get Analysis History
**Endpoint**: `GET /api/history`

```bash
# Get last 7 days
curl "http://localhost:5000/api/history?days=7"

# Get specific file type
curl "http://localhost:5000/api/history?file_type=video"

# Get specific status
curl "http://localhost:5000/api/history?status=completed"

# Combine filters
curl "http://localhost:5000/api/history?days=30&file_type=video&status=completed"
```

## Web Interface URLs

| URL | Purpose |
|-----|---------|
| `http://localhost:5000/` | Main Dashboard |
| `http://localhost:5000/analytics` | Analytics Page |
| `http://localhost:5000/api/health` | Health Check |

## Configuration

### Environment Variables
```bash
# Port
set PORT=5000

# Flask environment
set FLASK_ENV=development  # or production, testing

# Database
set DATABASE_URL=sqlite:///app.db  # Default is SQLite

# Logging
set LOG_LEVEL=INFO
set LOG_FILE=logs/app.log

# Security
set SECRET_KEY=your-secret-key-here
```

### Configuration File (`config.py`)
```python
# Processing timeouts
PROCESSING_TIMEOUTS = {
    'video': 300,      # 5 minutes
    'image': 60,       # 1 minute
    'document': 120    # 2 minutes
}

# Job queue
MAX_WORKERS = 4        # Max concurrent jobs
QUEUE_SIZE = 100       # Max queued jobs

# File limits
MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200MB

# File types
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv', 'webm'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'docx', 'doc', 'xlsx', 'pptx', 'txt'}
```

## Directory Structure

```
D:\PYTHON
├── app.py                          # Main application
├── config.py                       # Configuration
├── requirements.txt               # Dependencies
│
├── models/
│   └── database.py               # Database models
│
├── routes/
│   ├── analysis.py               # Analysis endpoints
│   ├── results.py                # Results endpoints
│   └── api.py                    # API endpoints
│
├── services/
│   ├── video_service.py          # Video analysis
│   ├── image_service.py          # Image analysis
│   ├── office_service.py         # Document analysis
│   └── job_scheduler.py          # Job queue
│
├── utils/
│   ├── errors.py                 # Error handling
│   ├── validators.py             # File validation
│   └── helpers.py                # Utilities
│
├── templates/                     # HTML templates
├── static/                        # CSS, JS, images
├── uploads/                       # Uploaded files
└── logs/                          # Application logs
```

## Troubleshooting

### Issue: Port Already in Use
```bash
# Change port
set PORT=8080
python app.py

# Or kill process on port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Issue: Database Locked
```bash
# Delete old database and restart
del app.db
python app.py
```

### Issue: Upload Directory Missing
```bash
# Create it manually
mkdir uploads
mkdir logs
mkdir data
```

### Issue: Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or activate correct environment
.venv\Scripts\activate
```

### Issue: Video Processing Fails
```bash
# Check OpenCV
pip install opencv-python==4.8.1.78

# Verify it works
python -c "import cv2; print(cv2.__version__)"
```

## Performance Tuning

### For Large Videos (>500MB)
```python
# In config.py
PROCESSING_TIMEOUTS = {
    'video': 900,      # 15 minutes
    'image': 120,      # 2 minutes
    'document': 300    # 5 minutes
}
```

### For High Concurrency
```python
# In config.py
MAX_WORKERS = 8        # Increase from 4
QUEUE_SIZE = 200       # Increase queue
```

### For Database Performance
```bash
# Use PostgreSQL instead of SQLite
set DATABASE_URL=postgresql://user:pass@localhost/ai_analytics

# Connection pooling
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

## Database Management

### View Database
```bash
# SQLite
sqlite3 app.db

# See tables
.tables

# Query results
SELECT id, status, filename FROM analyses ORDER BY created_at DESC LIMIT 10;

# Exit
.quit
```

### Backup Database
```bash
# Windows
copy app.db app.db.backup

# macOS/Linux
cp app.db app.db.backup
```

## Monitoring

### Check Logs
```bash
# Real-time log monitoring
tail -f logs/app.log

# Search for errors
grep ERROR logs/app.log

# Count by level
grep INFO logs/app.log | wc -l
grep ERROR logs/app.log | wc -l
```

### Health Check
```bash
# Simple health check
curl http://localhost:5000/api/health

# Response
{"status": "healthy", "timestamp": "2023-11-28T..."}
```

## Deployment

### Local Development
```bash
python app.py
# http://localhost:5000
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (Recommended for Production)
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Next Steps

1. **Test the API**: Follow API Quick Reference above
2. **Upload a video**: Use any MP4 file
3. **Monitor progress**: Use progress endpoint
4. **Download results**: Use download endpoint
5. **Check statistics**: View overall dashboard
6. **Scale it**: Add PostgreSQL for production

## Support

### Common Commands
```bash
# Activate environment
.venv\Scripts\activate

# Run app
python app.py

# Run verification
python verify_setup.py

# Install packages
pip install -r requirements.txt

# View logs
type logs\app.log

# Test import
python -c "from app import create_app; app = create_app(); print('OK')"
```

### Useful Resources
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [OpenCV Documentation](https://docs.opencv.org/)

## Version Information

- **App Version**: 3.0.0
- **Python**: 3.10+
- **Flask**: 3.0.0
- **SQLAlchemy**: 2.0.23
- **OpenCV**: 4.8.1.78

---

**Last Updated**: December 28, 2024
**Status**: Production Ready
