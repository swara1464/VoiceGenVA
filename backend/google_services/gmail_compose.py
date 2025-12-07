# backend/google_services/gmail_compose.py
import json
import cohere
import os
from dotenv import load_dotenv
from utils.recipient_resolver import resolve_recipients, parse_multiple_recipients
from logs.log_utils import log_execution

load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

def generate_email_draft(user_instruction: str, recipient_name: str = "", user_full_name: str = "", user_email: str = "") -> dict:
    """
    Generate a professional email subject and body using LLM.

    Returns:
    {
        "subject": "...",
        "body": "...",
        "success": true/false,
        "error": "..."
    }
    """
    if not COHERE_API_KEY:
        return {
            "success": False,
            "error": "LLM not configured",
            "subject": "",
            "body": "Unable to generate email. Please write manually."
        }

    system_prompt = (
        "You are an expert email composer. Generate a professional, courteous email based on the user's instruction.\n"
        "Return ONLY valid JSON (no markdown, no backticks):\n"
        '{"subject": "<subject line, max 80 chars>", "body": "<email body with greeting, content, and signature>"}\n\n'
        "Guidelines:\n"
        "- Include a professional greeting (Dear/Hi [name])\n"
        "- Keep body concise but complete (max 400 chars)\n"
        "- Use professional tone, but friendly\n"
        "- Include closing with signature\n"
        "- Do NOT include To, From, CC, BCC in the body\n"
    )

    recipient_context = f"Recipient: {recipient_name}\n" if recipient_name else ""
    signature_context = f"Signature: {user_full_name}\n" if user_full_name else ""

    full_prompt = (
        f"{system_prompt}"
        f"{recipient_context}"
        f"{signature_context}"
        f"User instruction: {user_instruction}"
    )

    try:
        co = cohere.Client(COHERE_API_KEY)
        response = co.chat(
            model='command-a-03-2025',
            message=full_prompt,
            max_tokens=300,
            temperature=0.6
        )

        response_text = response.text.strip()

        try:
            draft = json.loads(response_text)
            subject = draft.get("subject", "").strip()
            body = draft.get("body", "").strip()

            if not subject or not body:
                raise ValueError("Missing subject or body in LLM response")

            if user_email:
                log_execution(user_email, "GMAIL_COMPOSE", "DRAFT_GENERATED", {
                    "subject": subject[:50],
                    "body_length": len(body)
                })

            return {
                "success": True,
                "subject": subject,
                "body": body,
                "error": None
            }

        except (json.JSONDecodeError, ValueError) as e:
            return {
                "success": False,
                "error": f"Failed to parse LLM response: {e}",
                "subject": "",
                "body": "Unable to generate email. Please write manually."
            }

    except Exception as e:
        print(f"LLM email generation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "subject": "",
            "body": "Unable to generate email. Please write manually."
        }

def build_gmail_preview(user_instruction: str, recipient_text: str, cc_text: str = "", bcc_text: str = "", user_email: str = "", user_full_name: str = "") -> dict:
    """
    Build a complete Gmail preview with resolved recipients and LLM-drafted content.

    Returns:
    {
        "success": true/false,
        "to": ["email@example.com"],
        "cc": ["..."],
        "bcc": ["..."],
        "subject": "...",
        "body": "...",
        "needs_confirmation": bool,
        "disambiguation_prompt": "...",
        "errors": [...]
    }
    """
    errors = []
    warnings = []

    to_resolution = resolve_recipients(recipient_text, user_email)

    if not to_resolution.get('emails'):
        if to_resolution.get('disambiguation_prompt'):
            return {
                "success": False,
                "error": to_resolution['disambiguation_prompt'],
                "needs_confirmation": True,
                "ambiguous_matches": to_resolution.get('ambiguous_matches', []),
                "to": [],
                "cc": [],
                "bcc": [],
                "subject": "",
                "body": ""
            }
        errors.append("No recipient email address found.")

    cc_resolution = resolve_recipients(cc_text, user_email) if cc_text else {"emails": [], "needs_confirmation": False}
    bcc_resolution = resolve_recipients(bcc_text, user_email) if bcc_text else {"emails": [], "needs_confirmation": False}

    if cc_text and not cc_resolution.get('emails'):
        warnings.append(f"Could not resolve CC recipient: {cc_text}")

    if bcc_text and not bcc_resolution.get('emails'):
        warnings.append(f"Could not resolve BCC recipient: {bcc_text}")

    to_emails = to_resolution.get('emails', [])
    cc_emails = cc_resolution.get('emails', [])
    bcc_emails = bcc_resolution.get('emails', [])

    recipient_name = to_resolution.get('ambiguous_matches', [{}])[0].get('name', '') if to_resolution.get('ambiguous_matches') else ""

    draft_result = generate_email_draft(
        user_instruction,
        recipient_name=recipient_name,
        user_full_name=user_full_name,
        user_email=user_email
    )

    result = {
        "success": len(errors) == 0 and draft_result['success'],
        "to": to_emails,
        "cc": cc_emails,
        "bcc": bcc_emails,
        "subject": draft_result.get('subject', ''),
        "body": draft_result.get('body', ''),
        "errors": errors,
        "warnings": warnings,
        "needs_confirmation": to_resolution.get('needs_confirmation', False)
    }

    if user_email:
        log_execution(user_email, "GMAIL_COMPOSE", "PREVIEW_BUILT", {
            "to_count": len(to_emails),
            "cc_count": len(cc_emails),
            "bcc_count": len(bcc_emails),
            "subject_length": len(result['subject'])
        })

    return result
