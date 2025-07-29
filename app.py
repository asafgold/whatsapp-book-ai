import os
import requests
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from fpdf import FPDF
import tempfile

app = Flask(__name__)
CORS(app)

# הפונקציה שמדברת עם OpenRouter
def generate_book(chat_text):
    headers = {
        "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://yourdomain.com",  # שים את כתובת האתר שלך כאן
        "X-Title": "WhatsApp Book"
    }

    messages = [
        {"role": "system", "content": "אתה עוזר שמסכם שיחות ויוצר ספר PDF מצחיק ומעניין."},
        {"role": "user", "content": f"היסטוריית השיחה:\n{chat_text}"}
    ]

    data = {
        "model": "openrouter/mistralai/mistral-7b-instruct",  # תוכל להחליף למודל אחר אם תרצה
        "messages": messages,
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]

# הפונקציה שמייצרת PDF
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    return temp_file.name

# נקודת קצה לקבלת קובץ ויצירת ספר
@app.route('/api/generate-book', methods=['POST'])
def generate_book_endpoint():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    chat_text = file.read().decode('utf-8')
    try:
        summary = generate_book(chat_text)
        pdf_path = create_pdf(summary)
        return send_file(pdf_path, as_attachment=True, download_name='whatsapp_book.pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
