from flask import Flask, request, send_file, jsonify
import os
import requests
from fpdf import FPDF
import tempfile

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")  # מוגדר בלוח הסביבה ב-Render

@app.route("/")
def home():
    return "WhatsApp Book AI is running."

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    text = file.read().decode("utf-8")

    prompt = f"""
    צור ספר מסודר, משעשע ומעוצב מהשיחות הבאות בוואטסאפ. אל תכתוב את כל ההודעות, רק תקציר מעניין עם סיפורים מצחיקים, רגעים מרגשים ונתונים מעניינים. השיחות:
    {text}
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

    if response.status_code != 200:
        return jsonify({"error": f"OpenRouter error: {response.status_code}", "details": response.text}), 500

    answer = response.json()["choices"][0]["message"]["content"]

    # צור PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in answer.split("\n"):
        pdf.multi_cell(0, 10, line)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp.name)

    return send_file(tmp.name, as_attachment=True, download_name="whatsapp_book.pdf")
