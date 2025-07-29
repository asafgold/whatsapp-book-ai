import os
import openai
from flask import Flask, request, send_file
from fpdf import FPDF
import tempfile

# הגדרות OpenRouter
openai.api_key = os.getenv("OPENROUTER_API_KEY")
openai.api_base = "https://openrouter.ai/api/v1"

app = Flask(__name__)

@app.route('/api/generate-book', methods=['POST'])
def generate_book():
    if 'file' not in request.files:
        return "Missing file", 400

    uploaded_file = request.files['file']
    if uploaded_file.filename == '':
        return "Empty filename", 400

    file_content = uploaded_file.read().decode('utf-8')

    # בקשת סיכום מהמודל
    prompt = f"""הקובץ הבא מכיל שיחות WhatsApp של קבוצה. כתוב סיכום מעניין של מה שקרה, כלול נקודות עיקריות, רגעים מצחיקים ודמויות מרכזיות:
    
    {file_content[:3000]}"""  # נגביל כדי לא לחרוג מהמגבלות

    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mixtral-8x7b",  # אפשר גם gpt-4 אם מוגדר
            messages=[
                {"role": "system", "content": "אתה עורך ספרים מקצועי שמתמחה בסיכומי קבוצות וואטסאפ."},
                {"role": "user", "content": prompt}
            ]
        )
        summary = response.choices[0].message.content.strip()
    except Exception as e:
        return f"שגיאה מהמודל: {e}", 500

    # יצירת PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in summary.split('\n'):
        pdf.multi_cell(0, 10, line)

    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_pdf.name)

    return send_file(temp_pdf.name, as_attachment=True, download_name="whatsapp_book.pdf")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
