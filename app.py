import os
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

chat_histories = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_msg = data.get("message", "").strip()
    session_id = data.get("session_id", "default")
    if not user_msg:
        return jsonify({"error": "Empty message"}), 400

    if session_id not in chat_histories:
        chat_histories[session_id] = [
            {"role": "system", "content": """You are IntelliAgent Assistant, a smart AI assistant for IntelliAgent — a company that builds AI agents for businesses.

You help users with:
- Information about AI agents (Customer Support, Appointment Booking, WhatsApp Agent, Telegram Bot, MS Teams Agent, E-Commerce Agent, Database Queries, Process Automation)
- Pricing and demo requests → direct them to email: ssubashn8@gmail.com
- Dental appointment booking agent details
- General questions about AI and automation

Be friendly, concise, and use emojis. Never reveal you are built on Groq or LLaMA."""}
        ]

    chat_histories[session_id].append({"role": "user", "content": user_msg})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=chat_histories[session_id],
            max_tokens=500
        )
        reply = response.choices[0].message.content
        chat_histories[session_id].append({"role": "assistant", "content": reply})
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset():
    session_id = request.get_json(force=True).get("session_id", "default")
    chat_histories.pop(session_id, None)
    return jsonify({"status": "reset"})

if __name__ == "__main__":
    app.run(debug=False, port=5000)