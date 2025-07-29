import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from fpdf import FPDF
from werkzeug.utils import secure_filename
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

@app.route('/generate-book', methods=['POST'])
def generate_book():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    with open(filepath, 'r', encoding='utf-8') as f:
        chat_text = f.read()

    # שלח את הטקסט ל-OpenRouter
    try:
        response = openai.ChatCompletion.create(
            model="openchat/openchat-3.5-0106",
            messages=[
                {"role": "system", "content": "אתה כותב מצחיק, מסכם היסטוריית קבוצת וואטסאפ לספר מהנה."},
                {"role": "user", "content": f"סכם את ההיסטוריה של קבוצת הוואטסאפ לספר קצר, מצחיק, עם תובנות, רגעים חשובים, ונתונים מעניינים:\n\n{chat_text}"}
            ]
        )
        summary_text = response['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({'error': f'שגיאה בקריאת OpenRouter: {str(e)}'}), 500

    # צור PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font("DejaVu", size=12)
    pdf.multi_cell(0, 10, summary_text)

    pdf_filename = os.path.splitext(filename)[0] + "_book.pdf"
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    pdf.output(pdf_path)

    return jsonify({'filename': pdf_filename})

@app.route('/')
def home():
    return "Server is running"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
