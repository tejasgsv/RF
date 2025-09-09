from flask import Flask, render_template, request, jsonify, send_file
import os
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Create directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('static', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze_video', methods=['POST'])
def analyze_video():
    try:
        # Simulate video analysis without actual processing
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Mock results for demonstration
        mock_results = {
            'total_frames': 1247,
            'unique_people': 23,
            'total_objects_detected': 156,
            'csv_filename': f'video_analysis_{timestamp}.csv'
        }
        
        return jsonify(mock_results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    try:
        # Mock image analysis results
        mock_results = {
            'people_count': 5,
            'accuracy': '99.8%',
            'processing_time': '< 1s',
            'image': ''  # Empty for now
        }
        
        return jsonify(mock_results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_csv/<filename>')
def download_csv(filename):
    try:
        # Create a simple CSV for download
        csv_content = "Frame,People_Count,Unique_People,Objects_Detected\n1,5,5,5\n2,3,6,8\n3,7,8,15"
        
        with open(f'uploads/{filename}', 'w') as f:
            f.write(csv_content)
            
        return send_file(f'uploads/{filename}', as_attachment=True, download_name=f'reliance_foundation_{filename}')
    except Exception as e:
        return jsonify({'error': 'File not found'}), 404

@app.route('/api/info')
def api_info():
    return jsonify({
        'status': 'running',
        'service': 'Reliance Foundation AI Platform',
        'version': '2.1.0'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)