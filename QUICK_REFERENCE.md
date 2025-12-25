# Quick Reference Card - AI Analytics Platform v3.0.0

## Getting Started (60 seconds)

```bash
# 1. Activate environment
.venv\Scripts\activate

# 2. Run the app
python app.py

# 3. Open browser
http://localhost:5000

# 4. Upload a video
# (Use web interface or API)
```

---

## Core API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/analyze` | Submit file for analysis |
| GET | `/results` | List results |
| GET | `/results/<id>` | Get specific result |
| GET | `/results/<id>/download/<fmt>` | Download (json/csv/txt) |
| GET | `/api/progress/<id>` | Check progress |
| GET | `/api/statistics` | Overall stats |
| GET | `/api/history` | Analysis history |
| GET | `/api/health` | Health check |

---

## Upload File

```bash
curl -X POST http://localhost:5000/analyze \
  -F "file=@sample.mp4" \
  -F "file_type=video"

# Returns: analysis_id, job_id, status
```

**File Types**: `video`, `image`, `document`
**Max Size**: 200 MB
**Status**: Returns 202 (Accepted)

---

## Check Progress

```bash
curl http://localhost:5000/api/progress/ANALYSIS_ID

# Shows: status, progress%, elapsed_time
```

---

## Get Results

```bash
# As JSON
curl http://localhost:5000/results/ANALYSIS_ID

# Download as CSV
curl http://localhost:5000/results/ANALYSIS_ID/download/csv \
  -o results.csv

# Download as JSON
curl http://localhost:5000/results/ANALYSIS_ID/download/json \
  -o results.json
```

---

## Get Statistics

```bash
curl http://localhost:5000/api/statistics

# Returns: total, completed, failed, success_rate, by_file_type
```

---

## Directory Structure

```
uploads/           # User uploaded files
logs/             # Application logs
data/             # Data files
templates/        # HTML templates
static/           # CSS, JS, images
models/           # Database models
routes/           # API routes
services/         # Business logic
utils/            # Utilities
app.py            # Main application
config.py         # Configuration
```

---

## Configuration

### Environment Variables
```bash
set FLASK_ENV=development    # or production
set PORT=5000
set DATABASE_URL=sqlite:///app.db
set LOG_LEVEL=INFO
```

### Processing Timeouts
- Video: 5 minutes
- Image: 1 minute
- Document: 2 minutes

### File Limits
- Max 200 MB per file
- Video: MP4, AVI, MOV, MKV, WMV, FLV, WebM
- Image: JPG, PNG, BMP, GIF, WebP
- Document: PDF, DOCX, XLSX, PPTX, TXT

---

## Database

### Tables
- `analyses` - Analysis jobs and results
- `analysis_statistics` - Daily statistics

### Query Examples
```sql
-- See recent analyses
SELECT id, status, filename FROM analyses 
ORDER BY created_at DESC LIMIT 10;

-- Count by status
SELECT status, COUNT(*) FROM analyses GROUP BY status;

-- Success rate
SELECT 100.0 * SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) / COUNT(*) 
FROM analyses;
```

---

## Common Commands

```bash
# Activate environment
.venv\Scripts\activate

# Run app
python app.py

# Check imports
python -c "from app import create_app; print('OK')"

# View logs
type logs\app.log

# Test API
curl http://localhost:5000/api/health

# Install packages
pip install -r requirements.txt

# View database
sqlite3 app.db
```

---

## Status Codes

| Code | Name | Meaning |
|------|------|---------|
| 200 | OK | Success - data returned |
| 202 | Accepted | Async job queued |
| 400 | Bad Request | Invalid input |
| 404 | Not Found | Resource missing |
| 500 | Server Error | Processing failed |

---

## Error Handling

### Error Response Format
```json
{
    "error": "File too large",
    "status_code": 400,
    "details": {
        "max_size_mb": 200,
        "file_size_mb": 250
    }
}
```

### Common Errors
- **No file**: Upload file required
- **Invalid type**: Use video, image, or document
- **Too large**: Max 200 MB
- **Not found**: Analysis ID doesn't exist
- **Not ready**: Analysis still processing

---

## Workflow Examples

### Upload → Track → Download (Bash)
```bash
# Upload
ANALYSIS_ID=$(curl -s -X POST http://localhost:5000/analyze \
  -F "file=@sample.mp4" \
  -F "file_type=video" | jq -r '.analysis_id')

# Track (every 5 seconds)
while sleep 5; do
  STATUS=$(curl -s http://localhost:5000/api/progress/$ANALYSIS_ID | jq '.status')
  echo "Status: $STATUS"
  [ "$STATUS" == '"completed"' ] && break
done

# Download
curl http://localhost:5000/results/$ANALYSIS_ID/download/csv \
  -o results.csv
```

### Batch Upload (PowerShell)
```powershell
# Upload all videos
Get-ChildItem *.mp4 | ForEach-Object {
    curl -X POST http://localhost:5000/analyze `
      -F "file=@$_" `
      -F "file_type=video"
    Start-Sleep -Seconds 1
}

# Get all results
curl http://localhost:5000/results?status=completed
```

---

## Docker (Future)

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
docker build -t ai-analytics .
docker run -p 5000:5000 ai-analytics
```

---

## Troubleshooting

### Port in use
```bash
set PORT=8080
python app.py
```

### Database locked
```bash
del app.db
python app.py
```

### Import error
```bash
.venv\Scripts\activate
pip install -r requirements.txt --force-reinstall
```

### Check what's running
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

---

## Documentation Files

| File | Purpose |
|------|---------|
| STARTUP_GUIDE.md | Installation & running |
| API_REFERENCE.md | Full API docs |
| PHASE2_SUMMARY.md | Change summary |
| PHASE2_REFACTORING.md | Architecture details |
| PHASE2_CHECKLIST.md | Completion checklist |
| README.md | Project overview |

---

## Key Concepts

### Factory Pattern
```python
app = create_app('development')
# Creates app with proper initialization
```

### Database Persistence
```python
analysis = Analysis(id=id, status='queued')
db.session.add(analysis)
db.session.commit()
```

### Job Scheduler
```python
job_id = scheduler.submit_job(analyze_video, filepath, timeout=300)
status = scheduler.get_job_status(job_id)
```

### Error Handling
```python
@handle_api_error
def analyze_route():
    raise ValidationError("Invalid input")
    # Returns formatted JSON error
```

### File Validation
```python
# Validates BEFORE saving
validator.validate_file_upload(file, 'video')
manager.save_upload(file, filename)
```

---

## Production Checklist

- [ ] Use ProductionConfig
- [ ] Set HTTPS (PREFERRED_URL_SCHEME='https')
- [ ] Use PostgreSQL (not SQLite)
- [ ] Run with Gunicorn (not Flask dev server)
- [ ] Set SECRET_KEY environment variable
- [ ] Enable CSRF protection
- [ ] Set up monitoring/logging
- [ ] Configure backup strategy
- [ ] Test all endpoints
- [ ] Load testing
- [ ] Security audit

---

## Performance Tips

### Increase Job Workers
```python
# config.py
MAX_WORKERS = 8  # from 4
```

### Use PostgreSQL
```bash
set DATABASE_URL=postgresql://user:pass@localhost/db
```

### Monitor Logs
```bash
type logs\app.log | findstr ERROR
```

### Check Statistics
```bash
curl http://localhost:5000/api/statistics
```

---

## Support Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [OpenCV Docs](https://docs.opencv.org/)
- [Python Docs](https://docs.python.org/)

---

**Version**: 3.0.0
**Status**: Production Ready
**Last Updated**: December 28, 2024
