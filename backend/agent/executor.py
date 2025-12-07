# backend/agent/executor.py
from google_services.gmail_utils import send_draft_email
from google_services.calendar_utils import create_calendar_event, get_upcoming_events, create_instant_meet, delete_calendar_event
from google_services.drive_utils import search_drive_files
from google_services.contacts_utils import search_contacts
from logs.log_utils import log_execution
from planner.router import call_llm_for_small_talk
import dateparser
from datetime import datetime, timedelta
import pytz

def execute_action(action: str, params: dict, user_email: str):
    """
    Dispatches a single action to the correct API wrapper.
    NO PARSING. NO GUESSING. Just execute what the planner says.
    """
    log_execution(user_email, action, "ATTEMPTING", {"params": params})

    # GMAIL
    if action == "GMAIL_SEND":
        result = send_draft_email(
            to=params.get('to'),
            subject=params.get('subject'),
            body=params.get('body'),
            cc=params.get('cc'),
            bcc=params.get('bcc'),
            user_email=user_email,
            approved=params.get('approved', False)
        )
        action_name = "Email Sent"

    # CALENDAR
    elif action == "CALENDAR_CREATE":
        if params.get('instant'):
            result = create_instant_meet(
                title=params.get('summary', 'Instant Meeting'),
                attendees=params.get('attendees', []),
                user_email=user_email,
                timezone='UTC'
            )
        else:
            result = create_calendar_event(
                summary=params.get('summary'),
                description=params.get('description', 'Scheduled via Vocal Agent'),
                start_time=params.get('start_time'),
                end_time=params.get('end_time'),
                attendees=params.get('attendees'),
                user_email=user_email
            )
        action_name = "Calendar Event Created"

    elif action == "CALENDAR_LIST":
        result = get_upcoming_events(params.get('max_results', 10), user_email)
        action_name = "Upcoming Events Retrieved"

    elif action == "CALENDAR_DELETE":
        result = delete_calendar_event(
            event_id=params.get('event_id'),
            user_email=user_email
        )
        action_name = "Calendar Event Deleted"

    # CONTACTS
    elif action == "CONTACTS_SEARCH":
        result = search_contacts(params.get('query'), user_email)
        action_name = "Contacts Searched"

    # DRIVE (already working, minimal changes)
    elif action == "DRIVE_SEARCH":
        result = search_drive_files(params.get('query'), user_email)
        action_name = "Drive Search Performed"

    else:
        result = {"success": False, "message": f"Unknown action: {action}"}
        action_name = "Unknown Action"

    if result.get('success'):
        log_execution(user_email, action_name, "SUCCESS", result)
    else:
        log_execution(user_email, action_name, "FAILED", result)

    return result

def parse_date_string_to_iso(date_string: str) -> dict:
    """Safely parses a natural language date string into ISO 8601 format."""
    try:
        # Standardize search to UTC for API
        base_dt = datetime.now(pytz.UTC)
        
        # Parse the start time using dateparser
        start_dt = dateparser.parse(
            date_string,
            settings={
                'RELATIVE_BASE': base_dt,
                'TIMEZONE': 'UTC', # Standardize to UTC for API
                'RETURN_AS_TIMEZONE_AWARE': True
            }
        )
        
        if not start_dt:
            raise ValueError("Could not parse the date/time.")
        
        # Calculate a default end time (1 hour later)
        end_dt = start_dt + timedelta(hours=1)

        return {
            "success": True,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat()
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to parse date: {e}"}

def process_planner_output(plan: dict, user_email: str):
    """
    Processes the JSON plan from Cohere LLM.
    NO PARSING. NO REGEX. Just read the JSON and execute or show preview.
    """
    if not user_email or user_email == "unknown_user":
        return {"response_type": "ERROR", "response": "User not logged in"}

    action = plan.get("action")

    # Handle errors and chat modes first
    if action == "ERROR":
        return {"response_type": "ERROR", "response": plan.get("message", "An error occurred")}
    if action == "ASK_USER":
        return {"response_type": "RESULT", "response": plan.get("message", "I need more information. Please provide additional details.")}
    if action == "SMALL_TALK":
        # Ensure 'user_input' is passed back for chat context
        response_text = plan.get("response", "I'm here to help!")
        return {"response_type": "RESULT", "response": response_text}

    # Handle Gmail - show preview before sending
    if action == "GMAIL_COMPOSE":
        return {
            "response_type": "EMAIL_PREVIEW",
            "action": "GMAIL_SEND",
            "message": "Please review your email before sending.",
            "params": {
                "to": plan.get("to", []),
                "cc": plan.get("cc", []),
                "bcc": plan.get("bcc", []),
                "subject": plan.get("subject", ""),
                "body": plan.get("body", "")
            }
        }

    # Handle Calendar - apply date parsing
    if action == "CALENDAR_CREATE":
        start_time_str = plan.get("start_time")

        # Use robust date parsing if NOT instant
        if not plan.get("instant"):
            date_info = parse_date_string_to_iso(start_time_str)
            if not date_info['success']:
                return {"response_type": "ERROR", "response": f"Scheduling failed: {date_info['error']}"}

            # Overwrite LLM's potentially invalid date with guaranteed ISO dates
            plan["start_time"] = date_info['start_time']
            plan["end_time"] = date_info['end_time']

        # Determine Preview/Approval flow
        message_prefix = f"Ready to schedule: '{plan.get('summary')}' at {plan.get('start_time')[:16]}."
        
        return {
            "response_type": "APPROVAL",
            "action": "CALENDAR_CREATE",
            "message": message_prefix,
            "params": {
                "summary": plan.get("summary"),
                "description": plan.get("description", "Scheduled via Vocal Agent"),
                "start_time": plan.get("start_time"),
                "end_time": plan.get("end_time"),
                "attendees": plan.get("attendees", []),
                "instant": plan.get("instant", False)
            }
        }

    # Handle Calendar List - execute immediately
    if action == "CALENDAR_LIST":
        result = execute_action("CALENDAR_LIST", {"max_results": plan.get("max_results", 10)}, user_email)

        if result.get('success') and 'details' in result:
            response = f"{result['message']}\n\n"
            for event in result['details']:
                summary = event.get('summary', 'No Title')
                start = event.get('start', 'No time')
                meet_link = event.get('meet_link', 'No Meet link')
                response += f"📅 {summary}\n⏰ {start}\n🔗 {meet_link}\n\n"
            return {"response_type": "RESULT", "response": response}
        else:
            return {"response_type": "RESULT", "response": result.get('message', 'No events found')}

    # Handle Contacts Search - execute immediately
    if action == "CONTACTS_SEARCH":
        result = execute_action("CONTACTS_SEARCH", {"query": plan.get("query")}, user_email)

        if result.get('success') and 'details' in result:
            response = f"{result['message']}\n\n"
            for contact in result['details'][:5]:
                name = contact.get('name', 'Unknown')
                email = contact.get('email', 'No email')
                phone = contact.get('phone', 'No phone')
                response += f"👤 {name}\nEmail: {email}\nPhone: {phone}\n\n"
            return {"response_type": "RESULT", "response": response}
        else:
            return {"response_type": "RESULT", "response": result.get('message', 'No contacts found')}
    
    # Handle Drive Search - execute immediately
    if action == "DRIVE_SEARCH":
        result = execute_action("DRIVE_SEARCH", {"query": plan.get("query")}, user_email)

        if result.get('success') and 'details' in result:
            response = f"{result['message']}\n\n"
            for file in result['details']:
                name = file.get('name', 'Unnamed')
                link = file.get('link', '')
                response += f"📁 {name}\n🔗 {link}\n\n"
            return {"response_type": "RESULT", "response": response}
        else:
            return {"response_type": "RESULT", "response": result.get('message', 'No files found')}

    # Unknown action
    return {
        "response_type": "ERROR",
        "response": f"Unknown action: {action}"
    }
