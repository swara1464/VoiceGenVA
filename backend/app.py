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
from planner.router import run_planner
from agent.executor import process_planner_output, execute_action
from logs.log_utils import init_log_db, get_logs
from models.session_store import init_db as init_token_db

load_dotenv()
init_log_db()  # Initialize log DB
init_token_db()  # Initialize OAuth token storage

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


# Diagnostic endpoint
@app.route("/test/email-detection", methods=["POST", "OPTIONS"])
def test_email_detection():
    """Quick diagnostic endpoint to test email detection"""
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    test_input = data.get("prompt", "")

    # Test the failsafe logic
    email_keywords = ["send", "email", "mail", "compose", "draft", "message", "write to"]
    user_wants_email = any(keyword in test_input.lower() for keyword in email_keywords)

    result = {
        "input": test_input,
        "email_keywords_found": [kw for kw in email_keywords if kw in test_input.lower()],
        "should_trigger_email": user_wants_email,
        "failsafe_would_activate": user_wants_email
    }

    print(f"🧪 EMAIL DETECTION TEST: {result}")
    return jsonify(result)


# Planner route - NEW: Cohere returns JSON plan, executor processes it
@app.route("/planner/run", methods=["POST", "OPTIONS"])
def planner_run():
    print("\n" + "="*80)
    print("🌐 INCOMING REQUEST TO /planner/run")
    print("="*80)

    if request.method == "OPTIONS":
        print("⚡ OPTIONS request - returning early")
        return jsonify({}), 200

    data = request.json
    prompt = data.get("prompt", "")
    user = get_user_from_jwt()

    print(f"📨 Prompt received: '{prompt}'")
    print(f"👤 User authenticated: {user.get('email') if user else 'None'}")
    print("="*80)

    if not user:
        print("❌ User not logged in")
        return jsonify({"response_type": "ERROR", "response": "User not logged in"}), 401
    if not prompt:
        print("❌ No prompt provided")
        return jsonify({"response_type": "ERROR", "response": "No prompt provided"}), 400

    try:
        # Step 1: Get JSON plan from Cohere LLM (with contact resolution)
        print("📋 Step 1: Calling run_planner...")
        plan = run_planner(prompt, user["email"])
        print(f"📋 Planner returned: {plan}")

        # Step 2: Process the plan (no parsing, just read JSON)
        print("⚙️ Step 2: Processing planner output...")
        execution_result = process_planner_output(plan, user["email"])
        print(f"✅ Execution result: {execution_result}")
        print(f"✅ Response type being returned: {execution_result.get('response_type')}")

        if execution_result.get('response_type') == 'EMAIL_PREVIEW':
            print("🎯 EMAIL_PREVIEW CONFIRMED - Frontend should open email form")
            print(f"🎯 Email params: {execution_result.get('params')}")

        return jsonify(execution_result)

    except Exception as e:
        print(f"❌ CRITICAL ERROR in planner_run: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "response_type": "ERROR",
            "response": f"An error occurred: {str(e)}"
        })


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


# Gmail compose (build preview)
@app.route("/api/gmail/compose", methods=["POST", "OPTIONS"])
def gmail_compose():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    user = get_user_from_jwt()

    if not user:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    user_email = user["email"]
    from google_services.gmail_compose import build_gmail_preview

    preview = build_gmail_preview(
        user_instruction=data.get('instruction', ''),
        recipient_text=data.get('to', ''),
        cc_text=data.get('cc', ''),
        bcc_text=data.get('bcc', ''),
        user_email=user_email,
        user_full_name=user.get('name', '')
    )

    return jsonify(preview)


# Gmail send (with approval check)
@app.route("/api/gmail/send", methods=["POST", "OPTIONS"])
def gmail_send():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.json
    user = get_user_from_jwt()

    if not user:
        return jsonify({"success": False, "error": "Not logged in"}), 401

    user_email = user["email"]
    from google_services.gmail_utils import send_draft_email

    result = send_draft_email(
        to=data.get('to'),
        subject=data.get('subject', ''),
        body=data.get('body', ''),
        cc=data.get('cc'),
        bcc=data.get('bcc'),
        user_email=user_email,
        approved=data.get('approved', False)
    )

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
