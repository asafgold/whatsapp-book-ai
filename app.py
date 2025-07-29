import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import requests
from fpdf import FPDF

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    uploaded_file = request.files.get("file")
    if not uploaded_file:
        return jsonify({"error": "No file provided"}), 400

    content = uploaded_file.read().decode("utf-8")

    # Call OpenRouter API
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://yourdomain.com",  # שים את הדומיין שלך כאן
    }

    data = {
        "model": "openrouter/mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "המר את תוכן הצ'אט לספר מצחיק בפורמט סיפורי."},
            {"role": "user", "content": content}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result_text = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # צור PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in result_text.split("\n"):
        pdf.multi_cell(0, 10, line)

    output_path = "/tmp/generated_book.pdf"
    pdf.output(output_path)

    return send_file(output_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
