import os
from flask import Flask, request, jsonify
from fpdf import FPDF
import httpx
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = "openrouter/gpt-3.5-turbo"

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    content = data.get("content", "")

    if not content:
        return jsonify({"error": "Missing 'content' field"}), 400

    try:
        summary = call_openrouter(content)
        pdf_path = generate_pdf(summary)
        return jsonify({"summary": summary, "pdf_url": pdf_path})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def call_openrouter(content):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant who summarizes WhatsApp conversations."},
            {"role": "user", "content": f"Please summarize the following WhatsApp chat:\n\n{content}"}
        ]
    }

    response = httpx.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"]

def generate_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"book_{timestamp}.pdf"
    filepath = os.path.join("static", filename)

    os.makedirs("static", exist_ok=True)
    pdf.output(filepath)

    return f"/static/{filename}"

@app.route("/")
def index():
    return "WhatsApp Book AI is live."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
