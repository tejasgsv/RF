# API Reference - Complete Endpoint Documentation

## Base URL
```
http://localhost:5000
```

---

## 1. ANALYSIS ENDPOINTS

### 1.1 Submit File for Analysis
**Endpoint**: `POST /analyze`
**Status Code**: 202 (Accepted)

**Request**:
```bash
curl -X POST http://localhost:5000/analyze \
  -F "file=@/path/to/video.mp4" \
  -F "file_type=video"
```

**Request Parameters**:
| Parameter | Type | Required | Values | Example |
|-----------|------|----------|--------|---------|
| file | File | Yes | Any video/image/document | sample.mp4 |
| file_type | String | Yes | "video", "image", "document" | "video" |

**Response (202)**:
```json
{
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "job_id": "job_123456789",
    "status": "queued",
    "message": "Video analysis queued successfully",
    "file_type": "video",
    "filename": "20231128_101530_sample.mp4"
}
```

**Error Response (400 - Bad Request)**:
```json
{
    "error": "No file provided",
    "status_code": 400,
    "details": {
        "field": "file"
    }
}
```

**Error Response (400 - Invalid Type)**:
```json
{
    "error": "Invalid file type: xyz",
    "status_code": 400,
    "details": {
        "field": "file_type",
        "allowed": ["video", "image", "document"]
    }
}
```

**Error Response (400 - File Size)**:
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

---

## 2. RESULTS ENDPOINTS

### 2.1 List All Results
**Endpoint**: `GET /results`
**Status Code**: 200 (OK)

**Request**:
```bash
# Get all results
curl http://localhost:5000/results

# With pagination
curl "http://localhost:5000/results?page=2&per_page=10"

# Filter by status
curl "http://localhost:5000/results?status=completed"

# Combine filters
curl "http://localhost:5000/results?status=completed&page=1&per_page=20"
```

**Query Parameters**:
| Parameter | Type | Default | Values |
|-----------|------|---------|--------|
| page | Integer | 1 | 1, 2, 3, ... |
| per_page | Integer | 20 | 1-100 |
| status | String | null | "queued", "processing", "completed", "failed" |

**Response (200)**:
```json
{
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "file_type": "video",
            "filename": "20231128_101530_sample.mp4",
            "status": "completed",
            "created_at": "2023-11-28T10:15:30",
            "completed_at": "2023-11-28T10:16:00",
            "processing_time": 30.5,
            "results": {
                "total_people_detected": 5,
                "total_faces_detected": 4
            },
            "error_message": null
        }
    ],
    "total": 42,
    "page": 1,
    "per_page": 20,
    "pages": 3,
    "has_next": true,
    "has_prev": false
}
```

---

### 2.2 Get Specific Result
**Endpoint**: `GET /results/<analysis_id>`
**Status Code**: 200 (OK)

**Request**:
```bash
curl http://localhost:5000/results/550e8400-e29b-41d4-a716-446655440000
```

**Response (200)**:
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "file_type": "video",
    "filename": "20231128_101530_sample.mp4",
    "status": "completed",
    "created_at": "2023-11-28T10:15:30",
    "completed_at": "2023-11-28T10:16:00",
    "processing_time": 30.5,
    "results": {
        "total_people_detected": 5,
        "total_faces_detected": 4,
        "total_heads_detected": 5,
        "frames_analyzed": 450,
        "processing_time_seconds": 30.5
    },
    "error_message": null
}
```

**Error Response (404)**:
```json
{
    "error": "Analysis not found",
    "status_code": 404
}
```

---

### 2.3 Get Result Status Only
**Endpoint**: `GET /results/<analysis_id>/status`
**Status Code**: 200 (OK)

**Request**:
```bash
curl http://localhost:5000/results/550e8400-e29b-41d4-a716-446655440000/status
```

**Response (200 - Processing)**:
```json
{
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "file_type": "video",
    "filename": "20231128_101530_sample.mp4",
    "created_at": "2023-11-28T10:15:30",
    "job_status": {
        "status": "running",
        "progress": 45,
        "message": "Processing frame 1250 of 2500"
    },
    "progress": 45
}
```

**Response (200 - Completed)**:
```json
{
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "file_type": "video",
    "filename": "20231128_101530_sample.mp4",
    "created_at": "2023-11-28T10:15:30",
    "completed_at": "2023-11-28T10:16:00",
    "progress": 100,
    "message": "Completed",
    "result_summary": {
        "metrics_count": 8,
        "has_visualization": false
    }
}
```

**Response (200 - Failed)**:
```json
{
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "failed",
    "file_type": "video",
    "filename": "20231128_101530_sample.mp4",
    "created_at": "2023-11-28T10:15:30",
    "progress": 0,
    "message": "File corrupted",
    "error_message": "File corrupted: Invalid MP4 header"
}
```

---

### 2.4 Download Results
**Endpoint**: `GET /results/<analysis_id>/download/<format>`
**Status Code**: 200 (OK)

**Request**:
```bash
# Download as JSON
curl http://localhost:5000/results/550e8400-e29b-41d4-a716-446655440000/download/json \
  -o results.json

# Download as CSV
curl http://localhost:5000/results/550e8400-e29b-41d4-a716-446655440000/download/csv \
  -o results.csv

# Download as Text
curl http://localhost:5000/results/550e8400-e29b-41d4-a716-446655440000/download/txt \
  -o results.txt
```

**Supported Formats**:
| Format | Mimetype | Use Case |
|--------|----------|----------|
| json | application/json | Data processing, API integration |
| csv | text/csv | Excel, spreadsheets |
| txt | text/plain | Human readable, reports |

**Response Headers**:
```
Content-Disposition: attachment; filename="550e8400-e29b-41d4-a716-446655440000_results.csv"
Content-Type: text/csv
```

**CSV Output Example**:
```csv
Metric,Value
total_people_detected,5
total_faces_detected,4
total_heads_detected,5
frames_analyzed,450
processing_time_seconds,30.5
```

**Error Response (400 - Not Ready)**:
```json
{
    "error": "Analysis not completed. Status: processing",
    "status_code": 400
}
```

---

## 3. API MONITORING ENDPOINTS

### 3.1 Get Job Progress
**Endpoint**: `GET /api/progress/<analysis_id>`
**Status Code**: 200 (OK)

**Request**:
```bash
curl http://localhost:5000/api/progress/550e8400-e29b-41d4-a716-446655440000
```

**Response (200 - Queued)**:
```json
{
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "queued",
    "elapsed_time": 0.5,
    "created_at": "2023-11-28T10:15:30",
    "progress": 0,
    "message": "Queued for processing"
}
```

**Response (200 - Processing)**:
```json
{
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "elapsed_time": 15.3,
    "created_at": "2023-11-28T10:15:30",
    "progress": 45,
    "message": "Processing frame 1250 of 2500"
}
```

**Response (200 - Completed)**:
```json
{
    "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "elapsed_time": 30.5,
    "created_at": "2023-11-28T10:15:30",
    "completed_at": "2023-11-28T10:16:00",
    "progress": 100,
    "message": "Completed"
}
```

---

### 3.2 Get Overall Statistics
**Endpoint**: `GET /api/statistics`
**Status Code**: 200 (OK)

**Request**:
```bash
curl http://localhost:5000/api/statistics
```

**Response (200)**:
```json
{
    "total_analyses": 42,
    "completed": 38,
    "failed": 2,
    "processing": 1,
    "queued": 1,
    "success_rate": 90.48,
    "avg_processing_time": 45.23,
    "by_file_type": {
        "video": {
            "total": 30,
            "completed": 28,
            "success_rate": 93.33
        },
        "image": {
            "total": 10,
            "completed": 9,
            "success_rate": 90.0
        },
        "document": {
            "total": 2,
            "completed": 1,
            "success_rate": 50.0
        }
    },
    "timestamp": "2023-11-28T10:20:00"
}
```

---

### 3.3 Get Analysis History
**Endpoint**: `GET /api/history`
**Status Code**: 200 (OK)

**Request**:
```bash
# Last 7 days
curl http://localhost:5000/api/history

# Last 30 days
curl "http://localhost:5000/api/history?days=30"

# Specific file type
curl "http://localhost:5000/api/history?file_type=video"

# Specific status
curl "http://localhost:5000/api/history?status=completed"

# Combine filters
curl "http://localhost:5000/api/history?days=30&file_type=video&status=completed&limit=50"
```

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| days | Integer | 7 | Number of days to include |
| file_type | String | null | Filter: "video", "image", "document" |
| status | String | null | Filter: "queued", "processing", "completed", "failed" |
| limit | Integer | 100 | Max results to return |

**Response (200)**:
```json
{
    "history": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "file_type": "video",
            "filename": "20231128_101530_sample.mp4",
            "status": "completed",
            "created_at": "2023-11-28T10:15:30",
            "completed_at": "2023-11-28T10:16:00",
            "processing_time": 30.5
        }
    ],
    "total": 15,
    "days": 7,
    "filters": {
        "file_type": "video",
        "status": "completed"
    }
}
```

---

### 3.4 Get Daily Statistics
**Endpoint**: `GET /api/stats/daily`
**Status Code**: 200 (OK)

**Request**:
```bash
# Last 30 days
curl http://localhost:5000/api/stats/daily

# Last 60 days
curl "http://localhost:5000/api/stats/daily?days=60"
```

**Query Parameters**:
| Parameter | Type | Default |
|-----------|------|---------|
| days | Integer | 30 |

**Response (200)**:
```json
{
    "daily_stats": [
        {
            "date": "2023-11-28",
            "total": 12,
            "completed": 10,
            "failed": 2
        },
        {
            "date": "2023-11-27",
            "total": 8,
            "completed": 8,
            "failed": 0
        }
    ],
    "days": 30
}
```

---

### 3.5 Health Check
**Endpoint**: `GET /api/health`
**Status Code**: 200 (OK)

**Request**:
```bash
curl http://localhost:5000/api/health
```

**Response (200)**:
```json
{
    "status": "healthy",
    "timestamp": "2023-11-28T10:20:00"
}
```

---

## 4. WEB INTERFACE ENDPOINTS

### 4.1 Main Dashboard
**Endpoint**: `GET /`
**Content-Type**: text/html

**Request**:
```bash
curl http://localhost:5000/
```

**Response**: HTML page with upload form and dashboard

---

### 4.2 Analytics Page
**Endpoint**: `GET /analytics`
**Content-Type**: text/html

**Request**:
```bash
curl http://localhost:5000/analytics
```

**Response**: HTML page with analytics charts

---

## 5. ERROR CODES

| Code | Name | Meaning | Example |
|------|------|---------|---------|
| 200 | OK | Success - data returned | GET /results |
| 202 | Accepted | Success - async job queued | POST /analyze |
| 400 | Bad Request | Invalid input | Missing file, invalid type |
| 404 | Not Found | Resource doesn't exist | Analysis ID not found |
| 500 | Server Error | Processing failed | File corrupted, timeout |
| 429 | Rate Limited | Too many requests | Coming in Phase 5 |

---

## 6. WORKFLOW EXAMPLES

### Example 1: Upload and Track Progress

```bash
# 1. Upload file
RESPONSE=$(curl -s -X POST http://localhost:5000/analyze \
  -F "file=@sample.mp4" \
  -F "file_type=video")

# Extract analysis_id
ANALYSIS_ID=$(echo $RESPONSE | jq -r '.analysis_id')

# 2. Check progress repeatedly
for i in {1..10}; do
  curl http://localhost:5000/api/progress/$ANALYSIS_ID
  sleep 5
done

# 3. Download results when complete
curl http://localhost:5000/results/$ANALYSIS_ID/download/csv \
  -o results.csv
```

### Example 2: Batch Processing

```bash
# Upload multiple files
for file in *.mp4; do
  curl -X POST http://localhost:5000/analyze \
    -F "file=@$file" \
    -F "file_type=video"
  sleep 1
done

# Get all results after 5 minutes
curl http://localhost:5000/results?status=completed
```

### Example 3: Statistical Monitoring

```bash
# Get current statistics
curl http://localhost:5000/api/statistics

# Get daily trends
curl "http://localhost:5000/api/stats/daily?days=30"

# Get filtered history
curl "http://localhost:5000/api/history?days=7&status=completed"
```

---

## 7. RESPONSE FORMAT STANDARDS

### Success Response
```json
{
    "data": {...},
    "status": 200
}
```

### Error Response
```json
{
    "error": "Error message",
    "status_code": 400,
    "details": {...}
}
```

### Pagination Response
```json
{
    "results": [...],
    "total": 42,
    "page": 1,
    "per_page": 20,
    "pages": 3,
    "has_next": true,
    "has_prev": false
}
```

---

## 8. RATE LIMITING (Phase 5)

Coming in Phase 5. Currently:
- No rate limits (development)
- Production config: TBD

---

## Testing with cURL

```bash
# Test upload
curl -X POST http://localhost:5000/analyze \
  -F "file=@test.mp4" \
  -F "file_type=video" \
  -v

# Test GET
curl -i http://localhost:5000/api/statistics

# Test with headers
curl -H "Content-Type: application/json" \
  http://localhost:5000/api/history

# Pretty print JSON
curl http://localhost:5000/api/statistics | python -m json.tool

# Save to file
curl http://localhost:5000/results/abc123/download/json > results.json

# With authentication (Phase 5)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5000/results
```

---

**Last Updated**: December 28, 2024
**API Version**: 3.0.0
**Status**: Production Ready
