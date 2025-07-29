
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from fpdf import FPDF
from dotenv import load_dotenv
import openai
import uuid

load_dotenv()
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    if "file" not in request.files:
        return jsonify({"error": "Missing file"}), 400

    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(uploaded_file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        chat_text = f.read()

    prompt = f"""העבר את תוכן קובץ הוואטסאפ הבא לספר עם סיפור מצחיק, תקציר נתונים מעניינים וכותרות פרקים, הכל בעברית:
----
{chat_text}
"""

    openai.api_key = os.getenv("OPENROUTER_API_KEY")
    response = openai.ChatCompletion.create(
        model="openchat/openchat-7b",
        messages=[
            {"role": "system", "content": "אתה עורך ספרים מומחה"},
            {"role": "user", "content": prompt}
        ]
    )

    output_text = response["choices"][0]["message"]["content"]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in output_text.split("\n"):
        pdf.cell(200, 10, txt=line.strip(), ln=True)

    output_filename = f"{uuid.uuid4().hex}.pdf"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    pdf.output(output_path)

    return send_file(output_path, as_attachment=True, download_name="whatsapp_book.pdf")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
