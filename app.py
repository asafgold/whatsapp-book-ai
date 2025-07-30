import os
from flask import Flask, request, send_file, jsonify
import requests
from fpdf import FPDF
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # מאפשר שליחה מהאתר שלך (אם נחסם קודם)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    if 'file' not in request.files:
        return jsonify({"error": "Missing file"}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    text = uploaded_file.read().decode('utf-8')

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "openrouter/gpt-4o",  # מודל תקין בוודאות
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
