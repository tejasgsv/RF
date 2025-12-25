#!/usr/bin/env python3
"""
Installation & Verification Script
Run this to ensure everything is properly set up
"""

import os
import sys
import json
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    print("\n" + "="*70)
    print("📁 CHECKING FILES")
    print("="*70)
    
    required_files = {
        'templates/dashboard.html': '✨ New Modern Dashboard',
        'templates/analytics_dashboard.html': '📊 Analytics Dashboard',
        'video_analyzer_enhanced.py': '🔍 Enhanced Analyzer',
        'services/video_service.py': '⚙️ Updated Video Service',
        'routes/main.py': '🔗 Updated Routes',
        'QUICKSTART.md': '📖 Quick Start Guide',
        'IMPROVEMENTS.md': '📋 Full Documentation',
        'COMPLETE_UPDATES.md': '✅ Update Summary'
    }
    
    all_exist = True
    for file_path, description in required_files.items():
        exists = os.path.exists(file_path)
        status = "✓" if exists else "✗"
        print(f"{status} {file_path:45} - {description}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n" + "="*70)
    print("📦 CHECKING DEPENDENCIES")
    print("="*70)
    
    required_packages = {
        'flask': 'Web Framework',
        'cv2': 'OpenCV - Computer Vision',
        'pandas': 'Data Processing',
        'numpy': 'Numerical Computing',
        'werkzeug': 'Web Utilities'
    }
    
    all_installed = True
    for package, description in required_packages.items():
        try:
            __import__(package)
            print(f"✓ {package:20} - {description}")
        except ImportError:
            print(f"✗ {package:20} - {description} [MISSING]")
            all_installed = False
    
    return all_installed

def check_structure():
    """Check if directory structure is correct"""
    print("\n" + "="*70)
    print("📂 CHECKING DIRECTORY STRUCTURE")
    print("="*70)
    
    required_dirs = [
        'templates',
        'services',
        'routes',
        'models',
        'utils',
        'static',
        'uploads'
    ]
    
    all_exist = True
    for directory in required_dirs:
        exists = os.path.isdir(directory)
        status = "✓" if exists else "✗"
        print(f"{status} {directory:30}")
        if not exists:
            all_exist = False
    
    return all_exist

def print_features():
    """Print new features summary"""
    print("\n" + "="*70)
    print("✨ NEW & IMPROVED FEATURES")
    print("="*70)
    
    features = {
        "🎨 UI/UX": [
            "Modern gradient purple-pink theme",
            "Smooth animations and transitions",
            "Responsive mobile design",
            "Professional typography",
            "Interactive cards and buttons",
            "Real-time progress bar",
            "Beautiful color scheme"
        ],
        "🔍 Detection": [
            "People detection (HOG Descriptor)",
            "Face detection (Haar Cascade)",
            "Head detection (Haar Cascade)",
            "Confidence scoring",
            "Position & size tracking",
            "Per-person metadata",
            "Timestamp recording"
        ],
        "📊 Analytics": [
            "Summary statistics dashboard",
            "Visual charts (doughnut, bar)",
            "Analysis history with pagination",
            "Auto-refresh capability",
            "Real-time data updates",
            "File type distribution",
            "Success rate tracking"
        ],
        "💾 Export": [
            "CSV export",
            "JSON export",
            "Detailed reports",
            "Statistical summaries",
            "People detection lists",
            "Frame-by-frame data"
        ]
    }
    
    for category, items in features.items():
        print(f"\n{category}")
        for item in items:
            print(f"  ✓ {item}")

def print_urls():
    """Print important URLs"""
    print("\n" + "="*70)
    print("🌐 IMPORTANT URLS")
    print("="*70)
    print("""
    Main Dashboard:
    └─ http://localhost:5000

    Analytics Dashboard:
    └─ http://localhost:5000/analytics

    API Endpoints:
    ├─ POST /analyze (upload and analyze)
    ├─ GET /check_analysis/<id> (check progress)
    └─ GET /api/analytics/summary (get statistics)
    """)

def print_next_steps():
    """Print next steps"""
    print("\n" + "="*70)
    print("🚀 NEXT STEPS")
    print("="*70)
    print("""
    1. Install dependencies (if needed):
       $ pip install flask opencv-python pandas numpy

    2. Run the application:
       $ python app.py

    3. Open your browser:
       → http://localhost:5000

    4. Upload and analyze a video file

    5. Check analytics dashboard:
       → http://localhost:5000/analytics

    6. Download results (CSV or JSON)
    """)

def main():
    """Run all checks"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                                                                      ║")
    print("║          🎉 AI ANALYTICS DASHBOARD - VERIFICATION SCRIPT 🎉          ║")
    print("║                                                                      ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    
    # Run checks
    files_ok = check_files()
    deps_ok = check_dependencies()
    struct_ok = check_structure()
    
    # Print features
    print_features()
    
    # Print URLs
    print_urls()
    
    # Print status
    print("\n" + "="*70)
    print("✅ VERIFICATION SUMMARY")
    print("="*70)
    
    if files_ok and struct_ok:
        print("✓ All required files present")
    else:
        print("✗ Some files are missing")
    
    if deps_ok:
        print("✓ All dependencies installed")
    else:
        print("⚠ Some dependencies are missing")
        print("  Run: pip install -r requirements.txt")
    
    if struct_ok:
        print("✓ Directory structure is correct")
    else:
        print("✗ Directory structure incomplete")
    
    # Print next steps
    print_next_steps()
    
    print("="*70)
    print("For more information, see QUICKSTART.md or IMPROVEMENTS.md")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
