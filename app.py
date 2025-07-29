import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return 'Whatsapp Book AI - Backend is live!'

@app.route('/api/generate-book', methods=['POST'])
def generate_book():
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 415

    data = request.get_json()
    messages = data.get("messages", [])

    prompt = "תכתוב ספר מצחיק בעברית על הקבוצה הזאת:\n\n"
    for m in messages:
        prompt += f"{m['name']}: {m['text']}\n"
    prompt += "\n---\nהספר:"

    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {openrouter_api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openchat/openchat-7b:free",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
    )

    if response.status_code != 200:
        return jsonify({"error": f"API Error: {response.text}"}), response.status_code

    result = response.json()
    book_text = result["choices"][0]["message"]["content"]
    return jsonify({"book": book_text})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
