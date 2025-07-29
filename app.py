import os
import json
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

@app.route("/", methods=["GET"])
def index():
    return "API is running"

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "לא נשלח קובץ"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "שם קובץ ריק"}), 400

    try:
        # קריאת תוכן הקובץ
        chat_text = file.read().decode('utf-8')

        # שליחת הבקשה ל-OpenRouter
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "openrouter/gpt-3.5-turbo",  # אפשר לשנות למודל אחר
            "messages": [
                {
                    "role": "user",
                    "content": f"סכם את שיחת ה-WhatsApp הבאה והפוך אותה לפרק בספר מודפס:\n\n{chat_text}"
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            return jsonify({"error": f"שגיאה משרת OpenRouter: {response.text}"}), 500

        result = response.json()
        message = result['choices'][0]['message']['content']
        return jsonify({"result": message})

    except Exception as e:
        return jsonify({"error": f"שגיאה בשרת: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
