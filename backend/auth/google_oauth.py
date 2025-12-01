# auth/google_oauth.py
from flask import Blueprint, redirect, session, request
from oauthlib.oauth2 import WebApplicationClient
import requests
import os

# ✅ Allowed tester emails
ALLOWED_TESTERS = ["swarapawanekar@gmail.com", "other.tester@gmail.com"]

google_bp = Blueprint("google_bp", __name__)
client = WebApplicationClient(os.getenv("GOOGLE_CLIENT_ID"))
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5050/auth/callback"

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
            "https://www.googleapis.com/auth/drive.readonly"
        ]
    )
    return redirect(authorization_url)

# 2️⃣ Callback route
@google_bp.route("/callback")
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

    # Add client secret manually (required by Google)
    body = body + f"&client_secret={CLIENT_SECRET}"

    token_response = requests.post(token_url, headers=headers, data=body)
    client.parse_request_body_response(token_response.text)

    # Save token
    session["google_token"] = token_response.json()

    # Get Google user info
    userinfo = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {session['google_token']['access_token']}"}
    ).json()

    email = userinfo.get("email")
    if email not in ALLOWED_TESTERS:
        return "Unauthorized email", 403

    # Save user info in session
    session["user"] = {
        "email": email,
        "name": userinfo.get("name"),
        "picture": userinfo.get("picture"),
    }

    # Redirect to frontend dashboard
    return redirect("http://localhost:5173/dashboard?login=success")

# 3️⃣ Check login status
@google_bp.route("/me")
def me():
    if "user" in session:
        return session["user"]
    return {"error": "Not logged in"}, 401

# 4️⃣ Logout
@google_bp.route("/logout")
def logout():
    session.clear()
    # Redirect to frontend login page after logout
    return redirect("http://localhost:5173/")
