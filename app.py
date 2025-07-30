from flask import Flask, request, send_file, jsonify, render_template_string
from fpdf import FPDF
import os
import tempfile

app = Flask(__name__)

# הגדרת שם הפונט
FONT_PATH = "NotoSansHebrewVariableFont.ttf"
FONT_NAME = "Noto"

# HTML להצגת הטופס והתוצאה
HTML_FORM = """
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>המרת וואטסאפ לספר</title>
    <style>
        body { font-family: sans-serif; text-align: center; margin-top: 100px; }
        #status { margin-top: 20px; padding: 10px; background-color: #fdd; color: #333; font-size: 18px; }
        .success { background-color: #dfd; }
    </style>
</head>
<body>
    <form method="POST" action="/api/generate-book" enctype="multipart/form-data" id="bookForm">
        <input type="file" name="file" required>
        <button type="submit">📘 צור ספר PDF</button>
    </form>
    <div id="status" class="{{ status_class|default('') }}">
        {{ message|default('') }}
    </div>
</body>
</html>
"""

class HebrewPDF(FPDF):
    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.add_page()
        self.add_font(FONT_NAME, "", FONT_PATH, uni=True)
        self.set_font(FONT_NAME, size=14)

    def write_text(self, text):
        self.set_auto_page_break(auto=True, margin=15)
        lines = text.split('\n')
        for line in lines:
            if self.get_y() > 270:
                self.add_page()
            self.multi_cell(0, 10, txt=line.strip(), align='R')

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_FORM)

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    try:
        uploaded_file = request.files.get("file")
        if not uploaded_file:
            return render_template_string(HTML_FORM, message="❌ שגיאה: לא נשלח קובץ", status_class="error")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_txt:
            uploaded_file.save(temp_txt.name)
            temp_txt.seek(0)
            content = temp_txt.read().decode("utf-8")

        pdf = HebrewPDF()
        pdf.write_text(content)

        pdf_path = os.path.join(tempfile.gettempdir(), "whatsapp_book.pdf")
        pdf.output(pdf_path)

        return send_file(pdf_path, as_attachment=True, download_name="whatsapp_book.pdf")

    except UnicodeDecodeError:
        return render_template_string(HTML_FORM, message="❌ שגיאה: הקובץ אינו בפורמט UTF-8", status_class="error")

    except Exception as e:
        return render_template_string(HTML_FORM, message=f"❌ שגיאה: {str(e)}", status_class="error")

if __name__ == "__main__":
    app.run(debug=True)
