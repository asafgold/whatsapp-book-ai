
from flask import Flask, request, send_file
from fpdf import FPDF
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

app = Flask(__name__)

def parse_chat(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        return f.read()

def ask_openai(chat_text):
    prompt = """
המשתמש העלה קובץ היסטוריה של קבוצת וואטסאפ. צור לו תמצית מצחיקה או מעניינת של מה שהיה שם, סיכום קצר עם רגעים בולטים, דמויות שחוזרות, או תופעות מעניינות.
"""
    chat_text = chat_text[:5000]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt + chat_text}]
    )
    return response.choices[0].message.content

def create_pdf(content, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in content.split("\n"):
        pdf.multi_cell(0, 10, line)
    pdf.output(output_path)

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    if 'file' not in request.files:
        return "Missing file", 400

    file = request.files['file']
    file_path = "/tmp/chat.txt"
    file.save(file_path)

    chat_text = parse_chat(file_path)
    summary = ask_openai(chat_text)

    output_path = "/tmp/book.pdf"
    create_pdf(summary, output_path)

    return send_file(output_path, as_attachment=True, download_name="book.pdf")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
