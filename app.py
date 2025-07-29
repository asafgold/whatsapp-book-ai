from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# שימוש ב-OpenRouter עם מפתח API שלך
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

@app.route("/", methods=["GET"])
def index():
    return "WhatsApp Book AI is running!"

@app.route("/api/generate-book", methods=["POST"])
def generate_book():
    try:
        data = request.get_json()

        # שליחת השיחה למודל
        response = client.chat.completions.create(
            model="mistralai/mixtral-8x7b",  # תוכל להחליף לכל מודל מ-OpenRouter
            messages=[
                {"role": "system", "content": "אתה יוצר ספר על בסיס שיחות וואטסאפ."},
                {"role": "user", "content": data.get("prompt", "")}
            ]
        )

        content = response.choices[0].message.content
        return jsonify({"book_content": content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
