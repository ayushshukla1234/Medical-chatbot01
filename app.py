from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import os

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Load Environment Variables
load_dotenv()

# OpenAI Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")

@app.route("/")
def home():
    return redirect(url_for("chat_page"))

@app.route("/chat")
def chat_page():
    return render_template("chat.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()

        if not user_message:
            return jsonify({"reply": "Please enter a valid medical question."})

        messages = [
            SystemMessage(content=(
                "You are MedAssist, a trusted medical assistant chatbot. "
                "Provide medical information in simple language. "
                "This is not a medical diagnosis. Recommend doctor visits when needed."
            )),
            HumanMessage(content=user_message)
        ]

        ai_response = llm.invoke(messages)
        reply_text = getattr(ai_response, "content", str(ai_response))

        print("🤖 AI Reply:", reply_text)

        return jsonify({"reply": reply_text})

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"reply": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
