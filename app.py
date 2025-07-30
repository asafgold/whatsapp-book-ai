from flask import Flask, request, send_file, jsonify
import os
import requests
from fpdf import FPDF
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.route('/')
def index():
    return 'API is working!'

@app.route('/api/generate-book', methods=['POST'])
def generate_book():
    if 'file' not in request.files:
        return jsonify({'error': 'Missing file'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    try:
        headers = {
            'Authorization': f'Bearer {OPENROUTER_API_KEY}',
            'Content-Type': 'application/json',
        }

        data = {
            "model": "openrouter/mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "המר את תוכן הצ'אט לספר מצחיק, מעניין, עם כותרות ופרקים."},
                {"role": "user", "content": content}
            ]
        }

        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers=headers,
            json=data
        )

        response.raise_for_status()
        book_text = response.json()['choices'][0]['message']['content']

        # יצירת PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)

        for line in book_text.split('\n'):
            pdf.multi_cell(0, 10, line)

        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.pdf')
        pdf.output(output_path)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
