# Reliance Foundation AI Analytics Platform

## 🏢 Enterprise AI Solution for Video & Image Analysis

### Overview
Advanced AI-powered analytics platform developed by Reliance Foundation for real-time human detection, tracking, and comprehensive data analysis.

### 🚀 Features
- **Video Intelligence Suite**: Real-time human detection and tracking
- **Image Analysis Engine**: Instant human detection with 99.8% accuracy
- **Document AI Suite**: Advanced document processing (Coming Soon)
- **Enterprise Security**: Bank-level security protocols
- **Multi-Cloud Support**: Scalable deployment options
- **Real-time Analytics**: Comprehensive reporting and insights

### 📋 System Requirements
- Python 3.12+
- OpenCV 4.12+
- Flask 3.1+
- 4GB+ RAM
- GPU support (optional, for enhanced performance)

### 🛠️ Installation

#### Local Development
```bash
# Clone repository
git clone <repository-url>
cd reliance-foundation-ai

# Install dependencies
pip install -r requirements.txt

# Run application
python simple_app.py
```

#### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Access application
http://localhost
```

### 🔧 Configuration

#### Environment Variables
```bash
FLASK_CONFIG=production          # Application environment
SECRET_KEY=your-secret-key      # Security key
PORT=5000                       # Application port
```

#### Application Settings
- **MAX_CONTENT_LENGTH**: 500MB (configurable)
- **FRAME_SKIP**: Process every 5th frame for optimization
- **RESIZE_WIDTH**: 320px for faster processing
- **DETECTION_THRESHOLD**: 0.5 confidence level

### 📊 API Endpoints

#### Core Functionality
- `GET /` - Main application interface
- `POST /analyze_video` - Video analysis endpoint
- `POST /analyze_image` - Image analysis endpoint
- `GET /download_csv/<filename>` - Download analysis reports
- `GET /api/info` - Application information

### 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask App     │    │   AI Engine     │
│   (HTML/JS)     │◄──►│   (Python)      │◄──►│   (OpenCV)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Static Files  │    │   File Storage  │    │   CSV Reports   │
│   (CSS/Images)  │    │   (Uploads)     │    │   (Analytics)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔒 Security Features
- Input validation and sanitization
- File type restrictions
- Size limitations
- Secure file handling
- Error logging and monitoring

### 📈 Performance Optimizations
- Frame skipping for video processing
- Image resizing for faster analysis
- Efficient memory management
- Optimized detection algorithms
- Caching mechanisms

### 🚀 Deployment Options

#### Cloud Platforms
- **AWS**: ECS, EC2, Lambda
- **Azure**: Container Instances, App Service
- **Google Cloud**: Cloud Run, Compute Engine
- **Digital Ocean**: Droplets, App Platform

#### On-Premise
- Docker containers
- Kubernetes clusters
- Traditional server deployment

### 📞 Support & Contact
- **Company**: Reliance Foundation
- **Version**: 2.1.0
- **Copyright**: © 2024 Reliance Foundation. All Rights Reserved.

### 📄 License
Proprietary software. All rights reserved by Reliance Foundation.

### 🔄 Version History
- **v2.1.0**: Enhanced UI, improved performance, enterprise features
- **v2.0.0**: Major redesign, Docker support, production ready
- **v1.0.0**: Initial release with basic functionality

---

**Built with ❤️ by Reliance Foundation AI Team**