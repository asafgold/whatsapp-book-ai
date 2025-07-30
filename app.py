from flask import Flask, request, send_file, jsonify
from fpdf import FPDF
import os
import tempfile

app = Flask(__name__)

# שם הפונט כפי שקיים בתיקייה הראשית (לפי מה ששלחת)
FONT_PATH = "NotoSansHebrewVariableFont.ttf"

class HebrewPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.add_page()
        self.add_font("Noto", "", FONT_PATH, uni=True)
        self.set_font("Noto", size=14)
        self.set_auto_page_break(auto=True, margin=15)

    def write_text(self, text):
        lines = text.split('\n')
        for line in lines:
            if self.get_y() > 270:
                self.add_page()
                self.set_font("Noto", size=14)
            self.multi_cell(0, 10, txt=line.strip(), align='R')

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    try:
        uploaded_file = request.files.get("file")
        if not uploaded_file:
            return jsonify({"error": "❌ שגיאה: לא נשלח קובץ"}), 400

        # קריאת התוכן
        content = uploaded_file.read().decode("utf-8").strip()
        if not content:
            return jsonify({"error": "❌ שגיאה: הקובץ ריק"}), 400

        # יצירת PDF
        pdf = HebrewPDF()
        pdf.write_text(content)

        pdf_path = os.path.join(tempfile.gettempdir(), "whatsapp_book.pdf")
        pdf.output(pdf_path)

        return send_file(pdf_path, as_attachment=True, download_name="whatsapp_book.pdf")

    except UnicodeDecodeError:
        return jsonify({"error": "❌ שגיאה: הקובץ אינו בקידוד UTF-8"}), 400

    except Exception as e:
        return jsonify({"error": f"❌ שגיאה כללית: {str(e)}"}), 500

@app.route("/")
def home():
    return "API is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
