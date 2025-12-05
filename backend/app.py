# backend/app.py
from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os
import json 
from dotenv import load_dotenv
# FIX: Added path modification to ensure submodules are found when running from root
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__))) 

# Imports for core logic
from planner.router import call_llm, run_planner
from agent.executor import parse_and_execute_plan, execute_action 
from logs.log_utils import init_log_db, get_logs 

load_dotenv()

# Initialize log DB on startup
init_log_db() 

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
    SESSION_COOKIE_SECURE=True, # Enforce secure cookie for HTTPS deployment
)

# Register Google OAuth blueprint
from auth.google_oauth import google_bp
app.register_blueprint(google_bp, url_prefix="/auth")


# Add CORS headers after each request
@app.after_request
def after_request(response):
    # DYNAMIC CORS HEADER: Set Access-Control-Allow-Origin to the requesting origin if credentials are used
    origin = request.headers.get('Origin')
    # Check if the origin is one of our allowed origins (including the wildcard pattern)
    if origin in ["https://voicegenva.onrender.com", "http://localhost:5173"] or (origin and 'onrender.com' in origin):
        response.headers.add("Access-Control-Allow-Origin", origin)
    else:
        # Default to the primary production host if origin is not recognized
        response.headers.add("Access-Control-Allow-Origin", "https://voicegenva.onrender.com")

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

# Planner route (UPDATED to call the executor logic)
@app.route("/planner/run", methods=["POST"])
def planner_run():
    data = request.json
    prompt = data.get("prompt", "")
    
    if not session.get("user"):
         return jsonify({"response_type": "ERROR", "response": "User not logged in. Please log in to run the planner."}), 401

    if not prompt:
        return jsonify({"response_type": "ERROR", "response": "No prompt provided"}), 400

    # 1. Get the LLM's plan
    raw_plan = run_planner(prompt)
    
    # 2. Parse the plan and decide on the next action (Execution Engine)
    execution_result = parse_and_execute_plan(raw_plan, prompt)
    
    return jsonify(execution_result) 

# Echo route (LLM) - UNCHANGED
@app.route("/echo", methods=["POST", "OPTIONS"])
def echo():
    if request.method == "OPTIONS":
        return jsonify({}), 200  # respond to preflight

    data = request.json
    user_message = data.get("message", "")
    if not user_message:
        return jsonify({"response": "No message provided"}), 400

    llm_response = call_llm(user_message)
    return jsonify({"response": llm_response})

# NEW ROUTE: Final execution endpoint (called by frontend after user approval)
@app.route("/agent/execute", methods=["POST"])
def agent_execute():
    data = request.json
    action = data.get("action")
    params = data.get("params")
    
    if not session.get("user"):
         return jsonify({"success": False, "message": "User not logged in"}), 401

    if not action or not params:
        return jsonify({"success": False, "message": "Missing action or parameters"}), 400
    
    user_email = session["user"]["email"]
    
    # Execute the action using the executor
    result = execute_action(action, params, user_email)
    
    return jsonify(result)

# NEW ROUTE: Fetch logs
@app.route("/logs", methods=["GET"])
def logs_route():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    user_email = session["user"]["email"]
    user_logs = get_logs(user_email)
    
    # Convert logs to a list of dicts for JSON serialization
    log_list = []
    for log in user_logs:
        log_list.append({
            "id": log[0], 
            "timestamp": log[1], 
            "action": log[3],
            "status": log[4],
            "details": json.loads(log[5]) 
        })
        
    return jsonify({"logs": log_list})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    app.run(host="0.0.0.0", port=port, debug=True)
