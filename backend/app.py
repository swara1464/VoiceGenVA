from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from dotenv import load_dotenv
import sys
import jwt
import datetime

# Ensure submodules are found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Core logic imports
from planner.router import call_llm, run_planner
from agent.executor import parse_and_execute_plan, execute_action
from logs.log_utils import init_log_db, get_logs

load_dotenv()
init_log_db()  # Initialize log DB

app = Flask(__name__)
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

# CORS configuration
CORS(
    app,
    origins=["https://voicegenva.onrender.com", "http://localhost:5173", "https://*.onrender.com"],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"]
)

# Session config
app.secret_key = os.getenv("SESSION_SECRET", "dev_default_key")
app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True,
)

# JWT secret
JWT_SECRET = os.getenv("SESSION_SECRET", "dev_default_key")

# Register Google OAuth blueprint
from auth.google_oauth import google_bp
app.register_blueprint(google_bp, url_prefix="/auth")

# CORS headers dynamically
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ["https://voicegenva.onrender.com", "http://localhost:5173"] or (origin and 'onrender.com' in origin):
        response.headers.add("Access-Control-Allow-Origin", origin)
    else:
        response.headers.add("Access-Control-Allow-Origin", "https://voicegenva.onrender.com")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response

# Helper: extract user info from JWT
def get_user_from_jwt():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# Health check
@app.route("/health", methods=["GET", "OPTIONS"])
def health():
    return jsonify({"status": "ok"})


# Root route
@app.route("/", methods=["GET", "OPTIONS"])
def root():
    return jsonify({"message": "Vocal Agent backend running"})


# Planner route
@app.route("/planner/run", methods=["POST", "OPTIONS"])
def planner_run():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    prompt = data.get("prompt", "")
    user = get_user_from_jwt()

    if not user:
        return jsonify({"response_type": "ERROR", "response": "User not logged in"}), 401
    if not prompt:
        return jsonify({"response_type": "ERROR", "response": "No prompt provided"}), 400

    raw_plan = run_planner(prompt)
    execution_result = parse_and_execute_plan(raw_plan, prompt, user["email"])

    return jsonify(execution_result)


# Echo route
@app.route("/echo", methods=["POST", "OPTIONS"])
def echo():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    data = request.json
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"response": "No message provided"}), 400
    llm_response = call_llm(user_message)
    return jsonify({"response": llm_response})


# Final execution endpoint
@app.route("/agent/execute", methods=["POST", "OPTIONS"])
def agent_execute():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    action = data.get("action")
    params = data.get("params")
    user = get_user_from_jwt()

    if not user:
        return jsonify({"success": False, "message": "User not logged in"}), 401
    if not action or not params:
        return jsonify({"success": False, "message": "Missing action or parameters"}), 400

    user_email = user["email"]
    result = execute_action(action, params, user_email)

    return jsonify(result)


# Fetch logs
@app.route("/logs", methods=["GET", "OPTIONS"])
def logs_route():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    user = get_user_from_jwt()
    if not user:
        return jsonify({"error": "Not logged in"}), 401

    user_email = user["email"]
    user_logs = get_logs(user_email)
    return jsonify({"logs": user_logs})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    is_production = os.environ.get("FLASK_ENV") == "production"
    app.run(host="0.0.0.0", port=port, debug=not is_production)
