from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "API is live."

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    # בדיקה שהקובץ קיים בבקשה
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    # שמירת הקובץ
    filename = secure_filename(file.filename)
    filepath = os.path.join("/tmp", filename)
    file.save(filepath)

    # קריאת תוכן הקובץ
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return jsonify({"error": f"Failed to read file: {str(e)}"}), 500

    # כאן תוכל להוסיף עיבוד, שליחה ל־OpenRouter וכו'
    # למשל: שלח את התוכן למודל AI או הפוך אותו ל־PDF

    return jsonify({
        "message": f"File '{filename}' received and read successfully.",
        "preview": content[:300]  # הצצה לתוכן
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
