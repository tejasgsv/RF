# 🚀 Professional Dashboard - User Guide

## Quick Start

### 1. Access the Dashboard
Open your web browser and go to: **http://localhost:5000**

You should see the Reliance Foundation AI Analytics Platform dashboard with a professional design.

---

## Dashboard Overview

### Header
- **Reliance Foundation Logo** (top left)
- **Platform Name & Version** (3.0.0)
- **Live Status Indicator** (green dot)

### Navigation Tabs
1. 📤 **Upload & Analyze** - Upload files for analysis (default tab)
2. 📊 **Results** - View all completed analyses
3. 📜 **History** - See upload history
4. 📈 **Statistics** - Platform statistics and charts

---

## How to Upload & Analyze

### Step 1: Select File Type
Choose one of three options:
- **🎥 Video** - MP4, AVI, MOV, MKV (< 200MB)
- **🖼️ Image** - JPG, PNG, BMP, GIF (< 200MB)
- **📄 Document** - PDF, DOCX, XLSX, PPTX (< 200MB)

### Step 2: Upload Your File
**Option A - Drag & Drop**
- Drag your file over the upload area
- Drop to upload automatically

**Option B - Click to Browse**
- Click the upload area
- Select file from your computer

**File Requirements:**
- Format: MP4, JPG, PNG, PDF, DOCX, XLSX, etc.
- Size: Under 200 MB
- No special characters in filename

### Step 3: Start Analysis
Click the **▶️ Start Analysis** button

### Step 4: Monitor Progress
- Watch the progress bar fill
- Status updates in real-time
- Processing time varies by file size

### Step 5: View Results
Once complete, see:
- **Unique People Detected** - Number of individuals
- **Total Face Detections** - Total face count
- **Processing Time** - How long it took
- **Video Resolution** - Video dimensions (if video)

---

## Results Tab

### View All Analyses
Click the **📊 Results** tab to see:
- List of all uploaded files
- File type (Video, Image, Document)
- Status (Completed, Processing, Failed)
- Upload date and time
- Action buttons

### Download Results
After analysis is complete:
1. Go to **Results** tab
2. Click the file you want
3. Choose export format:
   - **CSV** - Spreadsheet format
   - **JSON** - Raw data format
   - **PDF** - PDF report
   - **Print** - Print directly

---

## History Tab

### Upload History
View timeline of all uploads:
- File names
- Upload dates
- File types
- Status indicators
- Color-coded status:
  - 🟢 **Green** - Completed successfully
  - 🔵 **Blue** - Queued/Waiting
  - 🟠 **Orange** - Currently processing
  - 🔴 **Red** - Failed/Error

---

## Statistics Tab

### Platform Statistics
View overall analytics:
- **Total Analyses** - How many files processed
- **Success Rate** - Percentage completed successfully
- **Average Processing Time** - Average time per file

### Charts
- **Pie Chart** - Analyses by file type (Video/Image/Document)
- **Bar Chart** - Status distribution (Completed/Failed)

---

## Features Explained

### 📤 Smart File Upload
- **Validation** - File checked before upload
- **Security** - Secure filename handling
- **Error Messages** - Clear error notifications
- **Progress Tracking** - Real-time upload progress

### 🔍 Analysis Engine
- **Face Detection** - Detects and counts faces
- **Person Detection** - Identifies people in videos
- **Head Detection** - Detects head positions
- **Frame Analysis** - Analyzes video frame by frame
- **Time Tracking** - Measures processing duration

### 📊 Results Display
- **Visual Cards** - Key metrics in easy-to-read cards
- **Color Coding** - Different colors for different metrics
- **Real-time Updates** - Results appear as soon as ready
- **Multiple Formats** - Export in CSV, JSON, PDF

### 🔄 Progress Tracking
- **Live Updates** - Progress bar updates in real-time
- **Status Messages** - Know what's happening
- **Percentage Display** - See completion percentage
- **Time Estimate** - Estimated time remaining

### 💾 Data Export
- **CSV Format** - Use in spreadsheet applications
- **JSON Format** - Use in custom applications
- **PDF Reports** - Professional reports
- **Print Support** - Print directly from browser

---

## Example Analysis Results (Video)

```
Unique People Detected:     5
Total Face Detections:      45
Total Head Detections:      48
Frames Analyzed:            300/450
Processing Time:            45.23 seconds
Video Duration:             15 minutes
Resolution:                 1920x1080 (Full HD)
FPS:                        30 frames/second
```

---

## Color Guide

### Status Colors
- 🟢 **Green** - Success, Complete
- 🟠 **Orange** - Warning, Processing
- 🔵 **Blue** - Info, Queued
- 🔴 **Red** - Error, Failed

### Result Card Colors
- 🔵 **Blue** - Primary metrics
- ✨ **Gold** - Important metrics
- 🟢 **Green** - Success metrics
- 🟠 **Orange** - Secondary metrics

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open file browser |
| `Tab` | Navigate elements |
| `Enter` | Submit form/Start analysis |
| `Ctrl+P` | Print results |
| `Ctrl+S` | Save/Export results |

---

## Troubleshooting

### ❌ File Upload Fails
**Solution:**
- Check file size (< 200 MB)
- Verify file format is supported
- Try a different file
- Refresh the page

### ❌ Analysis Takes Too Long
**Solution:**
- File might be large (processing can take time)
- Try smaller file for faster results
- Check system resources
- Server might be busy

### ❌ Results Don't Show
**Solution:**
- Wait a moment for processing
- Refresh the page
- Try different file
- Check browser console for errors

### ❌ Export Button Disabled
**Solution:**
- Analysis must be completed first
- Status must show "Completed"
- Wait for green success message
- Try refreshing page

### ❌ Can't Access Dashboard
**Solution:**
- Ensure Flask app is running
- Check if port 5000 is available
- Try http://localhost:5000
- Or try http://127.0.0.1:5000

---

## Best Practices

### ✅ Do's
- ✅ Use supported file formats
- ✅ Keep files under 200 MB
- ✅ Wait for analysis to complete
- ✅ Export results regularly
- ✅ Check history tab for past analyses

### ❌ Don'ts
- ❌ Don't upload non-standard formats
- ❌ Don't use files > 200 MB
- ❌ Don't close browser during analysis
- ❌ Don't upload corrupted files
- ❌ Don't refresh while processing

---

## Supported File Types

### Video Formats
- MP4 (MPEG-4)
- AVI (Audio Video Interleave)
- MOV (QuickTime)
- MKV (Matroska)
- WebM
- FLV (Flash Video)

### Image Formats
- JPG / JPEG
- PNG (Portable Network Graphics)
- BMP (Bitmap)
- GIF (Graphics Interchange Format)
- TIFF (Tagged Image File)
- WebP

### Document Formats
- PDF (Portable Document Format)
- DOCX (Word Document)
- DOC (Legacy Word)
- XLSX (Excel Spreadsheet)
- XLS (Legacy Excel)
- PPTX (PowerPoint)

---

## File Size Limits

| Type | Max Size | Recommended |
|------|----------|-------------|
| Video | 200 MB | 50-100 MB |
| Image | 200 MB | 5-20 MB |
| Document | 200 MB | 10-50 MB |

---

## Processing Time Estimates

| Type | Small | Medium | Large |
|------|-------|--------|-------|
| Video | 1-2 min | 5-10 min | 15-30 min |
| Image | 5-10 sec | 10-30 sec | 30-60 sec |
| Document | 10-30 sec | 30-60 sec | 1-2 min |

**Note:** Times depend on file size, resolution, and server load

---

## System Requirements

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Internet
- Stable internet connection
- Minimum 5 Mbps upload speed recommended
- No interruptions during upload

### Computer
- 2+ GB RAM
- 500 MB free disk space
- Any OS (Windows, Mac, Linux)

---

## Contact & Support

For issues or questions:
1. Check this guide first
2. Review the "Troubleshooting" section
3. Check application status
4. Contact your administrator

---

## Platform Information

| Property | Value |
|----------|-------|
| Platform | Reliance Foundation AI Analytics |
| Version | 3.0.0 |
| Technology | Python Flask + OpenCV |
| Database | SQLite/PostgreSQL |
| Status | Production Ready |
| Last Updated | December 2025 |

---

## Keyboard Navigation

### Tab Order
1. File Type Selector
2. Upload Area
3. Analyze Button
4. Clear Button
5. Results Section
6. Export Buttons
7. Tab Navigation

### Mouse Support
- All interactive elements are click-able
- Tooltips appear on hover
- Buttons highlight on interaction

---

## Mobile Responsiveness

The dashboard is fully responsive:
- **Mobile (< 768px)** - Single column layout
- **Tablet (768-1024px)** - Two column layout
- **Desktop (> 1024px)** - Full featured layout

Works perfectly on:
- ✅ iPhone
- ✅ Android
- ✅ iPad
- ✅ Tablets
- ✅ Desktop computers

---

## Privacy & Data

### Your Data
- Files are processed on local server
- Results stored in local database
- No data sent to external servers
- Complete privacy protection

### Data Retention
- Results kept for 30 days
- Can be exported anytime
- Can be deleted manually
- Automatic cleanup available

---

**Happy Analyzing! 🚀**

For more detailed technical information, see: [FIXES_AND_FEATURES.md](FIXES_AND_FEATURES.md)
