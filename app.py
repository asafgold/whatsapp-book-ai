import os
from flask import Flask, request, send_file, jsonify
import requests
from fpdf import FPDF

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # ודא שזה מוגדר ב-Render

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    if 'file' not in request.files:
        return jsonify({"error": "Missing file"}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # קריאת טקסט מתוך הקובץ
    text = uploaded_file.read().decode('utf-8')

    # הכנת בקשה ל-OpenRouter
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "mistralai/mistral-7b-instruct",  # או כל מודל אחר הנתמך ע"י OpenRouter
        "messages": [
            {"role": "system", "content": "הפוך את ההיסטוריה לסיפור מצחיק וקליל בסגנון ספר"},
            {"role": "user", "content": text}
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=body
        )
        response.raise_for_status()
        result = response.json()
        book_text = result['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # יצירת PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in book_text.split('\n'):
        pdf.multi_cell(0, 10, line)
    output_path = "/tmp/book.pdf"
    pdf.output(output_path)

    return send_file(output_path, as_attachment=True, download_name="book.pdf")

@app.route("/")
def home():
    return "API is running"
