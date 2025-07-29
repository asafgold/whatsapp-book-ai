import os
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    file_content = file.read().decode("utf-8")

    prompt = f"""
    קובץ זה מכיל את היסטוריית הצ'אט של קבוצת וואטסאפ. צור ספר PDF מעניין, מצחיק ומרגש הכולל:
    - סיפורים משעשעים מתוך הקבוצה
    - רגעים בלתי נשכחים
    - פילוח של מי כתב הכי הרבה ומי הכי שתק
    - רגעים מרגשים
    - כולל עיצוב ספר

    הנה ההיסטוריה:
    {file_content[:10000]}  # חותכים ל־10000 תווים כדי לא להעמיס
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    json_data = {
        "model": "openai/gpt-4",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=json_data)

    if response.status_code != 200:
        return jsonify({"error": "Failed to generate book"}), 500

    gpt_output = response.json()["choices"][0]["message"]["content"]

    # שמירה זמנית לקובץ PDF (כ־.txt לצורך הדגמה)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(gpt_output.encode("utf-8"))
        tmp_path = tmp.name

    return jsonify({"message": "Book generated successfully", "path": tmp_path})
