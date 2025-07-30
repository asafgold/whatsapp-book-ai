import os
from flask import Flask, request, jsonify, send_file
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
MODEL = "openrouter/mistralai/mistral-7b-instruct"

@app.route('/')
def index():
    return "WhatsApp Book AI API is running."

@app.route('/api/generate-book', methods=['POST'])
def generate_book():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    with open(filepath, 'r', encoding='utf-8') as f:
        chat_text = f.read()

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://pitzikat.co.il",
        "X-Title": "whatsapp-book",
        "Content-Type": "application/json",
    }

    messages = [
        {"role": "system", "content": "אתה מחולל ספרים מצחיקים מקבוצות וואטסאפ בעברית."},
        {"role": "user", "content": f"המירו את תוכן קובץ הוואטסאפ הבא לספר מצחיק עם סיפורים, נתונים ותמונות (אם יש):\n\n{chat_text[:3000]}"}
    ]

    body = {
        "model": MODEL,
        "messages": messages,
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    output_pdf_path = os.path.join(UPLOAD_FOLDER, 'book_output.pdf')
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in content.splitlines():
        pdf.cell(200, 10, txt=line, ln=True)
    pdf.output(output_pdf_path)

    return send_file(output_pdf_path, as_attachment=True, download_name="whatsapp_book.pdf")