import os
from flask import Flask, request, send_file, jsonify
import requests
from fpdf import FPDF
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "openai/gpt-3.5-turbo"  # או מודל אחר מ־OpenRouter

@app.route('/api/generate-book', methods=['POST'])
def generate_book():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    content = file.read().decode('utf-8')

    # שולח ל־OpenRouter (GPT)
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "אתה עורך ספרים. הפוך את ההיסטוריה המצורפת לספר סיפורים מצחיק, מרגש ומסודר לפי נושאים"},
            {"role": "user", "content": content}
        ]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to get response from OpenRouter", "details": response.text}), 500

    result_text = response.json()['choices'][0]['message']['content']

    # מייצר PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    
    for line in result_text.split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf_stream = BytesIO()
    pdf.output(pdf_stream)
    pdf_stream.seek(0)

    return send_file(pdf_stream, as_attachment=True, download_name="whatsapp_book.pdf", mimetype='application/pdf')


@app.route('/')
def home():
    return "WhatsApp Book API is running!"

if __name__ == '__main__':
    app.run(debug=True)
