import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "HTTP-Referer": "https://pitzikat.co.il",
    "Content-Type": "application/json"
}
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    file = request.files["file"]
    file_content = file.read().decode("utf-8")

    messages = [
        {
            "role": "system",
            "content": "המשתמש מעלה קובץ היסטוריית וואטסאפ. צור ספר משעשע עם נתונים מעניינים, ציטוטים ותובנות מהשיחה, כאילו נכתב על ידי חבר בקבוצה."
        },
        {
            "role": "user",
            "content": file_content
        }
    ]

    payload = {
        "model": "openrouter/auto",
        "messages": messages
    }

    response = requests.post(OPENROUTER_API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()

    result = response.json()
    generated_text = result["choices"][0]["message"]["content"]

    return jsonify({"result": generated_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
