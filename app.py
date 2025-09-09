from flask import Flask, render_template_string, request, jsonify
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Simple HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Reliance Foundation AI Platform</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea, #764ba2); 
               color: white; margin: 0; padding: 20px; min-height: 100vh; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .logo { width: 80px; height: 80px; background: #ff6b35; border-radius: 50%; 
                display: inline-flex; align-items: center; justify-content: center;
                color: white; font-weight: bold; font-size: 24px; margin-bottom: 20px; }
        .upload-area { background: rgba(255,255,255,0.1); border: 2px dashed #fff; 
                       border-radius: 15px; padding: 40px; text-align: center; margin: 20px 0; }
        .btn { background: linear-gradient(45deg, #ff6b35, #f7931e); color: white; 
               border: none; padding: 15px 30px; border-radius: 25px; cursor: pointer; 
               font-size: 16px; margin: 10px; }
        .btn:hover { transform: scale(1.05); }
        .result { background: rgba(0,0,0,0.3); padding: 20px; border-radius: 15px; margin: 20px 0; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
        .stat-card { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; text-align: center; }
        .stat-number { font-size: 2rem; font-weight: bold; color: #60a5fa; }
        .stat-label { font-size: 0.9rem; opacity: 0.8; }
        .success { background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; 
                   border-radius: 10px; padding: 20px; margin: 20px 0; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">RF</div>
            <h1>Reliance Foundation</h1>
            <h2>AI Analytics Platform</h2>
            <div class="success">
                <h3>🎉 Deployment Successful!</h3>
                <p>Your Reliance Foundation AI Platform is now live on Render!</p>
            </div>
        </div>
        
        <div class="upload-area">
            <h3>📊 Platform Status</h3>
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">✅</div>
                    <div class="stat-label">Server Running</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">🚀</div>
                    <div class="stat-label">Render Deployed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">🏢</div>
                    <div class="stat-label">RF Platform</div>
                </div>
            </div>
            <p>Ready for AI image and video analysis!</p>
            <button class="btn" onclick="testAPI()">🔍 Test API</button>
        </div>
        
        <div id="result" class="result" style="display: none;">
            <h3>📊 API Response</h3>
            <div id="resultContent"></div>
        </div>
    </div>

    <script>
        function testAPI() {
            fetch('/api/info')
            .then(response => response.json())
            .then(data => {
                document.getElementById('resultContent').innerHTML = `
                    <div class="stats">
                        <div class="stat-card">
                            <div class="stat-number">${data.status}</div>
                            <div class="stat-label">Status</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data.version}</div>
                            <div class="stat-label">Version</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">✅</div>
                            <div class="stat-label">API Working</div>
                        </div>
                    </div>
                    <p><strong>Service:</strong> ${data.service}</p>
                `;
                document.getElementById('result').style.display = 'block';
            })
            .catch(error => {
                document.getElementById('resultContent').innerHTML = `
                    <p style="color: #ef4444;">Error: ${error}</p>
                `;
                document.getElementById('result').style.display = 'block';
            });
        }
        
        // Auto test on load
        window.addEventListener('load', () => {
            setTimeout(testAPI, 1000);
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/info')
def api_info():
    return jsonify({
        'status': 'running',
        'service': 'Reliance Foundation AI Platform',
        'version': '2.1.0',
        'message': 'Deployment Successful on Render!'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'platform': 'render'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)