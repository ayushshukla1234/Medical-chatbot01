from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
import os
import requests

# Initialize Flask
app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# Clerk keys
CLERK_FRONTEND_API = os.getenv("CLERK_FRONTEND_API")
CLERK_API_KEY = os.getenv("CLERK_API_KEY")
CLERK_PUBLISHABLE_KEY = os.getenv("CLERK_PUBLISHABLE_KEY")

# OpenAI setup
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model="gpt-3.5-turbo")


# --------- Clerk Authentication Helper --------- #
def verify_clerk_token(token: str) -> bool:
    """Verify a Clerk session token."""
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        res = requests.get("https://api.clerk.com/v1/users/me", headers=headers)

        print("🔍 Clerk Verification Status:", res.status_code)
        return res.status_code == 200

    except Exception as e:
        print("❌ Clerk verification error:", e)
        return False


# --------- Routes --------- #

@app.route("/")
def home():
    return redirect(url_for("chat_page"))


@app.route("/chat")
def chat_page():
    return render_template("chat.html", clerk_publishable_key=CLERK_PUBLISHABLE_KEY)


@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        # Clerk Token Check
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"reply": "Unauthorized — No Clerk token provided."}), 401

        token = auth_header.split(" ")[1]

        if not verify_clerk_token(token):
            return jsonify({"reply": "Invalid or expired Clerk token."}), 403

        # Get User Message
        data = request.get_json()
        user_message = data.get("message", "").strip()
        if not user_message:
            return jsonify({"reply": "Please enter a valid medical question."})

        # Prepare Prompt
        messages = [
            SystemMessage(content=(
                "You are MedAssist, a trusted medical assistant chatbot. "
                "Provide medically accurate, safe, educational information. "
                "Do NOT give personal medical diagnosis. Suggest a doctor visit if needed."
            )),
            HumanMessage(content=user_message),
        ]

        # Get AI Response
        ai_response = llm.invoke(messages)
        reply_text = getattr(ai_response, "content", str(ai_response))

        print("🤖 AI Reply:", reply_text)

        return jsonify({"reply": reply_text})

    except Exception as e:
        print("❌ Backend /api/chat Error:", str(e))
        return jsonify({"reply": "Internal Server Error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
