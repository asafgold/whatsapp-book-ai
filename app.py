import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import tempfile
import openai
from fpdf import FPDF

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_type = "openai"
openai.api_version = None

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    content = file.read().decode("utf-8")
    messages = [
        {
            "role": "system",
            "content": "אתה עורך ספרים. תיצור לי תוכן לספר מעניין, מרגש ומצחיק לפי ההיסטוריה של קבוצת וואטסאפ. כלול גם נתונים, רגעים זכורים, בדיחות פרטיות, תיאורים, וגם הצעות לשם לספר."
        },
        {
            "role": "user",
            "content": content
        }
    ]

    response = openai.ChatCompletion.create(
        model="openrouter/mistralai/mistral-7b-instruct",  # תוכל לשנות ל־gpt-4 או אחר
        messages=messages
    )

    book_text = response['choices'][0]['message']['content']

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in book_text.split("\n"):
        pdf.multi_cell(0, 10, line)

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(tmp_file.name)
    tmp_file.close()

    return send_file(tmp_file.name, as_attachment=True, download_name="whatsapp_book.pdf")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
