# backend/google_services/gmail_utils.py

import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from flask import session
import json
from models.session_store import store_token, init_db, get_token

init_db()  # ensure token DB exists

def get_token_from_db(user_email):
    """
    Retrieves the token JSON string from the Supabase database using the imported get_token function.
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


def create_message(to, subject, body, cc=None, bcc=None):
    """
    Creates an email message with optional CC and BCC.

    :param to: Primary recipient email(s) - comma separated string
    :param subject: Email subject
    :param body: Email body content
    :param cc: CC recipient email(s) - comma separated string (optional)
    :param bcc: BCC recipient email(s) - comma separated string (optional)
    """
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject

    if cc:
        message["cc"] = cc
    if bcc:
        message["bcc"] = bcc

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": raw_message}


def send_draft_email(to: str, subject: str, body: str, cc: str = None, bcc: str = None, user_email=None, approved: bool = False):
    """
    Creates and sends an email using Gmail API with optional CC and BCC.

    :param to: Primary recipient(s) - comma separated or list
    :param subject: Email subject
    :param body: Email body content
    :param cc: CC recipient(s) - comma separated or list (optional)
    :param bcc: BCC recipient(s) - comma separated or list (optional)
    :param user_email: Email of the user (for token retrieval)
    :param approved: Must be True for send to proceed (safety check)
    """
    if not approved:
        from logs.log_utils import log_execution
        if user_email:
            log_execution(user_email, "GMAIL_SEND", "REJECTED", {
                "reason": "approval_missing"
            })
        return {"success": False, "message": "Email send rejected: user approval required"}

    service, error = get_google_service("gmail", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        message = create_message(to, subject, body, cc, bcc)
        send_response = service.users().messages().send(userId="me", body=message).execute()

        to_list = to if isinstance(to, list) else [to]
        recipients = ", ".join(to_list)
        if cc:
            cc_list = cc if isinstance(cc, list) else [cc]
            recipients += f" (CC: {', '.join(cc_list)})"
        if bcc:
            bcc_list = bcc if isinstance(bcc, list) else [bcc]
            recipients += f" (BCC: {', '.join(bcc_list)})"

        from logs.log_utils import log_execution
        if user_email:
            log_execution(user_email, "GMAIL_SENT", "SUCCESS", {
                "messageId": send_response.get('id'),
                "to": to_list,
                "cc": cc if isinstance(cc, list) else [cc] if cc else []
            })

        return {
            "success": True,
            "message": f"Email successfully sent to {recipients}. Message ID: {send_response['id']}",
            "details": send_response
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to send email: {e}"}
