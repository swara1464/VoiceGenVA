# backend/google_services/gmail_utils.py

import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from flask import session
import sqlite3
import json # ADDED
from ..models.session_store import store_token, init_db, get_token # MODIFIED: imported get_token

init_db()  # ensure DB exists

def get_token_from_db(user_email):
    """
    Retrieves the token JSON string from the SQLite database using the imported get_token function.
    (This function name is still used in this file's get_google_service for backward compatibility
    with the original logic).
    """
    token_json_str = get_token(user_email)
    if token_json_str:
        return json.loads(token_json_str)
    return None

def get_google_service(api_name: str, api_version: str, user_email=None):
    """
    Initializes a Google API service object using session or DB token.
    """
    token_data = session.get("google_token")
    if not token_data and user_email:
        # If token is not in the ephemeral session, look up the persisted token
        token_data = get_token_from_db(user_email) # Calls the function that uses session_store.get_token()

    if not token_data:
        return None, "Error: Google token not found. Please re-login."

    try:
        creds = Credentials.from_authorized_user_info(token_data)
        service = build(api_name, api_version, credentials=creds)
        return service, None
    except Exception as e:
        return None, f"Error building {api_name} service: {e}"


def create_message(to, subject, body):
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}


def send_draft_email(to: str, subject: str, body: str, user_email=None):
    """
    Creates and sends an email using Gmail API. Falls back to DB token if session missing.
    """
    # 🔥 CRITICAL FIX: Pass user_email to get_google_service
    service, error = get_google_service("gmail", "v1", user_email) # MODIFIED
    if error:
        return {"success": False, "message": error}

    try:
        message = create_message(to, subject, body)
        send_response = service.users().messages().send(userId="me", body=message).execute()
        return {
            "success": True,
            "message": f"Email successfully sent to {to}. Message ID: {send_response['id']}",
            "details": send_response
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to send email: {e}"}
