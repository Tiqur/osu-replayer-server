from flask import Flask, request, jsonify, send_from_directory
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('osu_replay_server')

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'received_replays'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_replay():
    """Handle replay upload"""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Save file with original filename
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)
    
    logger.info(f"Received replay: {file.filename}")
    
    return jsonify({
        "success": True,
        "message": "Replay received and saved"
    })

@app.route('/list', methods=['GET'])
def list_replays():
    """List all received replays"""
    replays = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.endswith('.osr'):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            replays.append({
                "filename": filename,
                "size": os.path.getsize(filepath)
            })
    
    return jsonify({"replays": replays})

@app.route('/download/<filename>', methods=['GET'])
def download_replay(filename):
    """Download a specific replay"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/', methods=['GET'])
def index():
    """Server status page"""
    replay_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.osr')]
    
    return f"""
    <html>
        <head><title>OSU Replay Server</title></head>
        <body>
            <h1>OSU Replay Server</h1>
            <p>Status: Online</p>
            <p>Total replays: {len(replay_files)}</p>
            <p><a href="/list">View all replays</a></p>
        </body>
    </html>
    """

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='OSU Replay Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    logger.info(f"Starting OSU Replay Server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)
