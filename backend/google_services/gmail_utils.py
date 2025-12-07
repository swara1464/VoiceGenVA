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


def search_inbox(query: str, max_results: int = 10, user_email=None):
    """
    Search for emails in the user's inbox using a query string.

    :param query: Search query (e.g., "from:someone@example.com", "subject:meeting", "is:unread")
    :param max_results: Maximum number of results to return
    :param user_email: Email of the user (for token retrieval)
    :return: Dictionary with success status and list of email summaries
    """
    service, error = get_google_service("gmail", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        results = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=max_results
        ).execute()

        messages = results.get("messages", [])

        if not messages:
            return {
                "success": True,
                "message": f"No emails found matching: {query}",
                "emails": []
            }

        email_summaries = []
        for msg in messages:
            msg_data = service.users().messages().get(
                userId="me",
                id=msg["id"],
                format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"]
            ).execute()

            headers = {h["name"]: h["value"] for h in msg_data.get("payload", {}).get("headers", [])}

            email_summaries.append({
                "id": msg["id"],
                "threadId": msg.get("threadId"),
                "from": headers.get("From", "Unknown"),
                "to": headers.get("To", "Unknown"),
                "subject": headers.get("Subject", "(No Subject)"),
                "date": headers.get("Date", "Unknown"),
                "snippet": msg_data.get("snippet", "")
            })

        return {
            "success": True,
            "message": f"Found {len(email_summaries)} email(s) matching: {query}",
            "emails": email_summaries
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to search inbox: {e}"}


def list_unread_emails(max_results: int = 10, user_email=None):
    """
    List unread emails in the user's inbox.

    :param max_results: Maximum number of results to return
    :param user_email: Email of the user (for token retrieval)
    :return: Dictionary with success status and list of unread email summaries
    """
    return search_inbox("is:unread", max_results, user_email)


def read_email(message_id: str, user_email=None):
    """
    Read a specific email by its message ID.

    :param message_id: The ID of the message to read
    :param user_email: Email of the user (for token retrieval)
    :return: Dictionary with success status and email details including body
    """
    service, error = get_google_service("gmail", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        msg = service.users().messages().get(
            userId="me",
            id=message_id,
            format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

        # Extract body
        body = ""
        if "parts" in msg["payload"]:
            for part in msg["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    if "data" in part["body"]:
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8")
                        break
        else:
            if "data" in msg["payload"].get("body", {}):
                body = base64.urlsafe_b64decode(msg["payload"]["body"]["data"]).decode("utf-8")

        # Check for attachments
        attachments = []
        if "parts" in msg["payload"]:
            for part in msg["payload"]["parts"]:
                if part.get("filename"):
                    attachments.append({
                        "filename": part["filename"],
                        "mimeType": part["mimeType"],
                        "size": part["body"].get("size", 0),
                        "attachmentId": part["body"].get("attachmentId")
                    })

        return {
            "success": True,
            "message": "Email retrieved successfully",
            "email": {
                "id": msg["id"],
                "threadId": msg.get("threadId"),
                "from": headers.get("From", "Unknown"),
                "to": headers.get("To", "Unknown"),
                "subject": headers.get("Subject", "(No Subject)"),
                "date": headers.get("Date", "Unknown"),
                "body": body,
                "snippet": msg.get("snippet", ""),
                "attachments": attachments
            }
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to read email: {e}"}


def download_attachment(message_id: str, attachment_id: str, user_email=None):
    """
    Download an attachment from an email.

    :param message_id: The ID of the message containing the attachment
    :param attachment_id: The ID of the attachment to download
    :param user_email: Email of the user (for token retrieval)
    :return: Dictionary with success status and attachment data (base64 encoded)
    """
    service, error = get_google_service("gmail", "v1", user_email)
    if error:
        return {"success": False, "message": error}

    try:
        attachment = service.users().messages().attachments().get(
            userId="me",
            messageId=message_id,
            id=attachment_id
        ).execute()

        return {
            "success": True,
            "message": "Attachment downloaded successfully",
            "data": attachment["data"],
            "size": attachment.get("size", 0)
        }
    except Exception as e:
        return {"success": False, "message": f"Failed to download attachment: {e}"}
