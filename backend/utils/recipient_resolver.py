# backend/utils/recipient_resolver.py
import re
from difflib import SequenceMatcher
from google_services.contacts_utils import list_contacts, search_contacts
from logs.log_utils import log_execution

EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')

def extract_emails_from_text(text: str) -> list:
    """Extract all email addresses from text using regex."""
    emails = EMAIL_REGEX.findall(text)
    return emails

def normalize_name(name: str) -> str:
    """Normalize contact name for fuzzy matching."""
    name = name.lower().strip()
    honorifics = ['mr.', 'ms.', 'mrs.', 'dr.', 'prof.', 'mr ', 'ms ', 'mrs ', 'dr ', 'prof ']
    for honorific in honorifics:
        name = name.replace(honorific, '')
    name = re.sub(r'\s+', ' ', name)
    return name

def calculate_similarity(a: str, b: str) -> float:
    """Calculate string similarity ratio."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def fuzzy_match_contact(query: str, contacts: list, threshold: float = 0.7) -> dict:
    """
    Fuzzy match a query against a list of contacts.

    Returns:
    {
        "match": matched_contact or None,
        "candidates": [list of contacts with score > 0.5],
        "best_score": highest similarity score
    }
    """
    query_norm = normalize_name(query)
    matches = []

    for contact in contacts:
        contact_name = contact.get('name', '')
        contact_email = contact.get('email', '')

        name_norm = normalize_name(contact_name)
        score_name = calculate_similarity(query_norm, name_norm)
        score_email = calculate_similarity(query.lower(), contact_email.lower())

        best_score = max(score_name, score_email)

        if best_score > 0.5:
            matches.append({
                "contact": contact,
                "score": best_score,
                "matched_field": "name" if score_name > score_email else "email"
            })

    matches.sort(key=lambda x: x['score'], reverse=True)

    if not matches:
        return {
            "match": None,
            "candidates": [],
            "best_score": 0
        }

    best_match = matches[0]

    if best_match['score'] >= threshold:
        return {
            "match": best_match['contact'],
            "candidates": matches[:3],
            "best_score": best_match['score']
        }
    else:
        return {
            "match": None,
            "candidates": matches[:3],
            "best_score": best_match['score']
        }

def resolve_recipients(text: str, user_email: str = None) -> dict:
    """
    Resolve recipient email addresses from natural language text.

    Algorithm:
    1. Extract explicit email addresses (regex)
    2. If no emails found, try contact fuzzy matching
    3. Return resolved emails and any disambiguation prompts

    Returns:
    {
        "emails": ["resolved@example.com"],
        "needs_confirmation": bool,
        "disambiguation_prompt": "...",
        "ambiguous_matches": [...]
    }
    """
    emails = extract_emails_from_text(text)

    if emails:
        if user_email:
            log_execution(user_email, "RECIPIENT_RESOLVER", "EXTRACTED", {
                "method": "regex",
                "emails": emails
            })
        return {
            "emails": emails,
            "needs_confirmation": False,
            "disambiguation_prompt": None,
            "ambiguous_matches": []
        }

    contact_search_result = list_contacts(max_results=100, user_email=user_email)

    if not contact_search_result.get('success'):
        if user_email:
            log_execution(user_email, "RECIPIENT_RESOLVER", "FAILED", {
                "reason": "Cannot fetch contacts"
            })
        return {
            "emails": [],
            "needs_confirmation": False,
            "disambiguation_prompt": "I couldn't access your contacts. Please provide an email address.",
            "ambiguous_matches": []
        }

    contacts = contact_search_result.get('details', [])

    fuzzy_result = fuzzy_match_contact(text, contacts, threshold=0.7)

    if fuzzy_result['match']:
        matched_email = fuzzy_result['match']['email']
        matched_name = fuzzy_result['match']['name']

        if user_email:
            log_execution(user_email, "RECIPIENT_RESOLVER", "FUZZY_MATCHED", {
                "query": text,
                "matched_name": matched_name,
                "matched_email": matched_email,
                "score": fuzzy_result['best_score']
            })

        return {
            "emails": [matched_email],
            "needs_confirmation": fuzzy_result['best_score'] < 0.85,
            "disambiguation_prompt": f"I found '{matched_name}' ({matched_email}). Is this correct?" if fuzzy_result['best_score'] < 0.85 else None,
            "ambiguous_matches": []
        }

    candidates = fuzzy_result['candidates']

    if candidates:
        candidate_options = "\n".join(
            f"• {c['contact']['name']} ({c['contact']['email']})"
            for c in candidates[:5]
        )

        if user_email:
            log_execution(user_email, "RECIPIENT_RESOLVER", "AMBIGUOUS", {
                "query": text,
                "candidates_count": len(candidates)
            })

        return {
            "emails": [],
            "needs_confirmation": True,
            "disambiguation_prompt": f"I found multiple possible matches for '{text}':\n{candidate_options}\nWhich one did you mean?",
            "ambiguous_matches": [c['contact'] for c in candidates]
        }

    if user_email:
        log_execution(user_email, "RECIPIENT_RESOLVER", "NOT_FOUND", {
            "query": text
        })

    return {
        "emails": [],
        "needs_confirmation": True,
        "disambiguation_prompt": f"I couldn't find a contact for '{text}'. Would you like to enter an email address directly?",
        "ambiguous_matches": []
    }

def parse_multiple_recipients(text: str, user_email: str = None) -> dict:
    """
    Parse multiple recipients from text with delimiters like 'and', 'comma', etc.

    Returns:
    {
        "recipients": [
            {
                "input": "Jubi",
                "resolved": {"emails": [...], "needs_confirmation": bool, ...}
            }
        ]
    }
    """
    recipient_splits = re.split(r',\s*|\s+and\s+', text, flags=re.IGNORECASE)
    recipients = []

    for recipient_text in recipient_splits:
        recipient_text = recipient_text.strip()
        if recipient_text:
            resolved = resolve_recipients(recipient_text, user_email)
            recipients.append({
                "input": recipient_text,
                "resolved": resolved
            })

    return {"recipients": recipients}
