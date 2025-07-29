import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "WhatsApp Book AI is running."

@app.route('/api/generate-book', methods=['POST'])
def generate_book():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    content = file.read().decode('utf-8')

    # כאן תוכל לקרוא ל-GPT ולעשות כל עיבוד
    return jsonify({'message': 'הקובץ התקבל', 'content': content[:100]})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
