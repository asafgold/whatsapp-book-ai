import os
from flask import Flask, request, send_file, jsonify
import requests
from fpdf import FPDF
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

FONT_PATH = "NotoSansHebrew-Regular.ttf"

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.add_font('Noto', '', FONT_PATH, uni=True)
        self.set_font('Noto', '', 14)

    def write_hebrew_text(self, text):
        for line in text.split('\n'):
            self.multi_cell(0, 10, txt=line, align='R')

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    if 'file' not in request.files:
        return jsonify({"error": "לא נשלח קובץ"}), 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return jsonify({"error": "שם קובץ ריק"}), 400

    try:
        text = uploaded_file.read().decode('utf-8')
        if len(text.strip()) == 0:
            return jsonify({"error": "הקובץ ריק"}), 400
    except Exception as e:
        return jsonify({"error": f"שגיאה בקריאת הקובץ: {str(e)}"}), 400

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "הפוך את ההיסטוריה של השיחה לסיפור מצחיק ומסודר בסגנון ספר"},
            {"role": "user", "content": text}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)

        if not response.ok:
            return jsonify({"error": f"שגיאת OpenRouter ({response.status_code}): {response.text}"}), 500

        result = response.json()
        book_text = result['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({"error": f"שגיאה בתקשורת עם OpenRouter: {str(e)}"}), 500

    try:
        pdf = PDF()
        pdf.write_hebrew_text(book_text)
        output_path = "/tmp/book.pdf"
        pdf.output(output_path)
        return send_file(output_path, as_attachment=True, download_name="book.pdf")
    except Exception as e:
        return jsonify({"error": f"שגיאה ביצירת PDF: {str(e)}"}), 500

@app.route("/")
def home():
    return "API is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
