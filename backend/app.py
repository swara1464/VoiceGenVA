# backend/app.py
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
from dotenv import load_dotenv
# CHANGED: Import call_llm instead of call_gemini
from planner.router import call_llm, run_planner

load_dotenv()

app = Flask(__name__)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# CORS configuration
CORS(
    app,
    origins=["http://localhost:5173"],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"]
)

# Session config
app.secret_key = os.getenv("SESSION_SECRET", "dev_default_key")
app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=False,  # Only because we are on localhost
)

# Register Google OAuth blueprint
from auth.google_oauth import google_bp
app.register_blueprint(google_bp, url_prefix="/auth")

# Add CORS headers after each request
@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response

# Health check
@app.route("/health", methods=["GET", "OPTIONS"])
def health():
    return jsonify({"status": "ok"})

# Root route
@app.route("/", methods=["GET", "OPTIONS"])
def root():
    return jsonify({"message": "Vocal Agent backend running"})

# Planner route
@app.route("/planner/run", methods=["POST"])
def planner_run():
    data = request.json
    prompt = data.get("prompt", "")
    if not prompt:
        return jsonify({"response": "No prompt provided"}), 400

    response = run_planner(prompt)
    return jsonify({"response": response})

# Echo route (LLM)
@app.route("/echo", methods=["POST", "OPTIONS"])
def echo():
    if request.method == "OPTIONS":
        return jsonify({}), 200  # respond to preflight

    data = request.json
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"response": "No message provided"}), 400

    # CHANGED: Use call_llm function
    llm_response = call_llm(user_message)
    return jsonify({"response": llm_response})

if __name__ == "__main__":
    app.run(port=5050, debug=True)