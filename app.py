from flask import Flask, render_template, request, jsonify, send_file
import os
import csv
import io
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    file_type = request.form.get('type')
    
    if file_type == 'video':
        return jsonify({
            'unique_people': 23,
            'total_objects': 156,
            'total_frames': 1247,
            'success': True
        })
    elif file_type == 'image':
        return jsonify({
            'people_detected': 5,
            'objects_detected': 12,
            'success': True
        })
    elif file_type == 'office':
        return jsonify({
            'word_count': 2847,
            'page_count': 15,
            'success': True
        })

@app.route('/download_csv', methods=['POST'])
def download_csv():
    data = request.get_json()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Analysis Report', 'Reliance Foundation AI Analytics'])
    writer.writerow(['Generated On', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow(['File Name', data.get('fileName', 'N/A')])
    writer.writerow(['File Type', data.get('fileType', 'N/A')])
    writer.writerow(['Process Time', data.get('processTime', 'N/A') + 's'])
    writer.writerow([])
    
    if data.get('fileType') == 'video':
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Unique People', data.get('unique_people', 0)])
        writer.writerow(['Total Objects', data.get('total_objects', 0)])
        writer.writerow(['Total Frames', data.get('total_frames', 0)])
    elif data.get('fileType') == 'image':
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['People Detected', data.get('people_detected', 0)])
        writer.writerow(['Objects Detected', data.get('objects_detected', 0)])
    elif data.get('fileType') == 'office':
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Word Count', data.get('word_count', 0)])
        writer.writerow(['Page Count', data.get('page_count', 0)])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'analysis_report_{datetime.now().strftime("%Y%m%d")}.csv'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)