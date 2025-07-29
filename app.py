from flask import Flask, request, send_file
from fpdf import FPDF
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

app = Flask(__name__)

def parse_chat(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        return f.read()

def ask_openrouter(chat_text):
    prompt = f"""
    צור לי ספר קצר ומצחיק, שמתבסס על שיחת הקבוצה בוואטסאפ. חלק אותו לפרקים מעניינים (למשל: "הגיע הזמן לחופשה", "מי שכח את הילקוט?", "ההפתעה של מיכל", "פדיחה עם המורה"), וכתוב את הסיפורים בצורה קלילה ונעימה.
    השיחה:
    {chat_text[:5000]}
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openrouter/gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

    if response.status_code != 200:
        raise Exception(f"OpenRouter Error: {response.status_code}, {response.text}")

    return response.json()["choices"][0]["message"]["content"]

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
    try:
        book_text = ask_openrouter(raw_text)
    except Exception as e:
        return f"Failed to generate book: {str(e)}", 500

    output_pdf = "generated_book.pdf"
    create_pdf(book_text, output_pdf)

    return send_file(output_pdf, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
