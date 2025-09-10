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
    
    writer.writerow(['Frame', 'People_Count', 'Objects_Count', 'Unique_People'])
    
    # Generate sample frame data
    for i in range(5, 901, 5):
        frame = i
        people = 1 if i % 50 == 0 else 0
        objects = i // 100
        unique = (i // 50) + 1
        writer.writerow([frame, people, objects, unique])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'RF_analysis_{datetime.now().strftime("%Y%m%d")}.csv'
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)