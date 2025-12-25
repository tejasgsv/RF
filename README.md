<!-- redeploy -->
# 🚀 Reliance Foundation AI Analytics Platform

## 🏗️ Architecture

### Frontend (GitHub Pages)
- **Static Website**: https://tejasgsv.github.io/RF
- **Technologies**: HTML, CSS, JavaScript
- **Hosting**: GitHub Pages (Free)

### Backend (Local/Cloud)
- **Flask Application**: `app.py`
- **AI Detection**: `human_detector.py`
- **Local URL**: http://localhost:5000

## 📋 Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/tejasgsv/RF.git
cd RF
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Flask Server
```bash
python app.py
```

### 4. Access Website
- **Frontend**: https://tejasgsv.github.io/RF
- **Full App**: http://localhost:5000

## ⚠️ Important Notes

### GitHub Pages Limitation
- GitHub Pages केवल static files (HTML, CSS, JS) host करता है
- Python Flask backend वहाँ run नहीं हो सकता
- Backend को locally या cloud server पर run करना होगा

### Solution Architecture
```
┌─────────────────┐    ┌─────────────────┐
│   GitHub Pages  │    │  Local/Cloud    │
│   (Frontend)    │◄──►│  Flask Server   │
│   Static Files  │    │  (Backend)      │
└─────────────────┘    └─────────────────┘
```

## 🌐 Deployment Options

### Frontend
- ✅ GitHub Pages (Current)
- ✅ Netlify
- ✅ Vercel

### Backend
- 🔧 Local Development
- ☁️ Heroku
- ☁️ Railway
- ☁️ Render
- ☁️ AWS/Azure/GCP

## 🎯 Features
- 🎥 Video Analysis with AI
- 📸 Image Detection
- 📊 CSV Report Generation
- 🏢 Reliance Foundation Branding

---
**© 2024 Reliance Foundation. All Rights Reserved.**
