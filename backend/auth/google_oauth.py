from flask import Blueprint, redirect, session, request, jsonify, make_response
from oauthlib.oauth2 import WebApplicationClient
import requests
import os
from dotenv import load_dotenv
import jwt
import datetime

# Load environment variables
load_dotenv() 

# ✅ Allowed tester emails
ALLOWED_TESTERS = ["swarapawanekar@gmail.com", "other.tester@gmail.com"]

# JWT secret
JWT_SECRET = os.getenv("SESSION_SECRET", "dev_default_key")

google_bp = Blueprint("google_bp", __name__)
client = WebApplicationClient(os.getenv("GOOGLE_CLIENT_ID"))
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "https://vocalagentapi.onrender.com/auth/callback"

# 1️⃣ Login route
@google_bp.route("/login")
def login():
    authorization_url = client.prepare_request_uri(
        "https://accounts.google.com/o/oauth2/v2/auth",
        redirect_uri=REDIRECT_URI,
        scope=[
            "openid", "email", "profile",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/calendar.events",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/documents",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/tasks",
            "https://www.googleapis.com/auth/contacts.readonly"
        ],
        access_type="offline",
        prompt="consent"
    )
    return redirect(authorization_url)


# 2️⃣ Callback route
@google_bp.route("/callback", strict_slashes=False)
def callback():
    code = request.args.get("code")
    if not code:
        return "No code provided", 400

    token_url, headers, body = client.prepare_token_request(
        "https://oauth2.googleapis.com/token",
        authorization_response=request.url,
        redirect_url=REDIRECT_URI,
        code=code
    )

    body += f"&client_secret={CLIENT_SECRET}"

    token_response = requests.post(token_url, headers=headers, data=body)
    client.parse_request_body_response(token_response.text)

    # Save token safely
    token_data = token_response.json()
    token_data.update({
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret": CLIENT_SECRET,
        "token_uri": "https://oauth2.googleapis.com/token",
        "scopes": request.args.get("scope").split(" ") if request.args.get("scope") else []
    })

    session["google_token"] = token_data

    # Get Google user info
    userinfo_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {session['google_token']['access_token']}"}
    )
    if userinfo_response.status_code != 200:
        return "Failed to fetch user info", 500

    userinfo = userinfo_response.json()
    email = userinfo.get("email")
    if email not in ALLOWED_TESTERS:
        return "Unauthorized email", 403

    # Save user info in session
    session["user"] = {
        "email": email,
        "name": userinfo.get("name"),
        "picture": userinfo.get("picture"),
    }

    # ✅ Generate JWT token
    payload = {
        "email": session["user"]["email"],
        "name": session["user"]["name"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    # Return redirect with make_response to ensure session persistence
    response = make_response(
        redirect(f"https://voicegenva.onrender.com/dashboard?login=success&token={token}")
    )
    # Optional: set HttpOnly cookie for JWT if frontend needs it
    response.set_cookie("session_token", token, httponly=True, max_age=7200)
    return response


# 3️⃣ Check login status via JWT
@google_bp.route("/me")
def me():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        # fallback to cookie if Authorization header missing
        token = request.cookies.get("session_token")
        if not token:
            return {"error": "Not logged in"}, 401
    else:
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return {"error": "Invalid Authorization header"}, 401

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return {"email": payload["email"], "name": payload["name"]}
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}, 401
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}, 401


# 4️⃣ Logout
@google_bp.route("/logout")
def logout():
    session.clear()
    response = jsonify({"success": True})
    response.set_cookie("session_token", "", expires=0)  # clear cookie
    return response, 200
