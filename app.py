from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from utils.translator import process_video, INDIAN_LANGUAGES
import os

from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# List of supported languages
@app.route('/api/languages', methods=['GET'])
def get_languages():
    return jsonify({'languages': INDIAN_LANGUAGES})

# Endpoint to handle video translation
@app.route('/api/translate', methods=['POST'])
def translate_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    source_language = request.form.get('sourceLanguage', 'en-US')
    
    try:
        results = process_video(video_file, source_language)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to serve audio files
@app.route('/api/audio/<filename>', methods=['GET'])
def get_audio(filename):
    try:
        file_path = os.path.join('temp', filename)
        return send_file(file_path, mimetype='audio/mp3')
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
