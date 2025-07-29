from flask import Flask, request, send_file
from fpdf import FPDF
import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)

def parse_chat(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        return f.read()

def ask_openai(chat_text):
    prompt = f"""
    צור לי ספר קצר ומצחיק, שמתבסס על שיחת הקבוצה בוואטסאפ. חלק אותו לפרקים מעניינים (למשל: "הגיע הזמן לחופשה", "מי שכח את הילקוט?", "ההפתעה של מיכל", "פדיחה עם המורה"), וכתוב את הסיפורים בצורה קלילה ונעימה.
    השיחה:
    {chat_text[:5000]}
    """

    response = openai.ChatCompletion.create(
        model="openai/gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['choices'][0]['message']['content']

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
    if 'chat_file' not in request.files:
        return "Missing file", 400

    file = request.files['chat_file']
    filename = "uploaded_chat.txt"
    file.save(filename)

    raw_text = parse_chat(filename)
    book_text = ask_openai(raw_text)

    output_pdf = "generated_book.pdf"
    create_pdf(book_text, output_pdf)

    return send_file(output_pdf, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
