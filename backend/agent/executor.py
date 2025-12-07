# backend/agent/executor.py
from google_services.gmail_utils import send_draft_email, search_inbox, read_email, list_unread_emails, download_attachment
from google_services.calendar_utils import create_calendar_event, get_upcoming_events, create_instant_meet, delete_calendar_event, update_calendar_event
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

    elif action == "GMAIL_SEARCH":
        result = search_inbox(
            query=params.get('query', ''),
            max_results=params.get('max_results', 10),
            user_email=user_email
        )
        action_name = "Inbox Searched"

    elif action == "GMAIL_READ":
        result = read_email(
            message_id=params.get('message_id'),
            user_email=user_email
        )
        action_name = "Email Read"

    elif action == "GMAIL_LIST_UNREAD":
        result = list_unread_emails(
            max_results=params.get('max_results', 10),
            user_email=user_email
        )
        action_name = "Unread Emails Listed"

    elif action == "GMAIL_DOWNLOAD_ATTACHMENT":
        result = download_attachment(
            message_id=params.get('message_id'),
            attachment_id=params.get('attachment_id'),
            user_email=user_email
        )
        action_name = "Attachment Downloaded"

    # CALENDAR
    elif action == "CALENDAR_CREATE":
        if params.get('instant'):
            result = create_instant_meet(
                title=params.get('summary', 'Instant Meeting'),
                attendees=params.get('attendees', []),
                user_email=user_email,
                timezone='Asia/Kolkata'
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
            summary=params.get('summary'),
            user_email=user_email
        )
        action_name = "Calendar Event Deleted"

    elif action == "CALENDAR_UPDATE":
        result = update_calendar_event(
            event_id=params.get('event_id'),
            summary_search=params.get('summary_search'),
            new_summary=params.get('new_summary'),
            new_start_time=params.get('new_start_time'),
            new_end_time=params.get('new_end_time'),
            new_description=params.get('new_description'),
            new_attendees=params.get('new_attendees'),
            user_email=user_email
        )
        action_name = "Calendar Event Updated"

    # CONTACTS
    elif action == "CONTACTS_SEARCH":
        result = search_contacts(params.get('query'), user_email)
        action_name = "Contacts Searched"

    elif action == "CONTACTS_CREATE":
        from google_services.contacts_utils import create_contact
        result = create_contact(
            given_name=params.get('given_name'),
            family_name=params.get('family_name'),
            email=params.get('email'),
            phone=params.get('phone'),
            user_email=user_email
        )
        action_name = "Contact Created"

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
    """Safely parses a natural language date string into ISO 8601 format with IST timezone."""
    try:
        # Use IST timezone for all date operations
        ist_tz = pytz.timezone('Asia/Kolkata')
        base_dt = datetime.now(ist_tz)

        # Parse the start time using dateparser
        start_dt = dateparser.parse(
            date_string,
            settings={
                'RELATIVE_BASE': base_dt,
                'TIMEZONE': 'Asia/Kolkata',  # Use IST timezone
                'RETURN_AS_TIMEZONE_AWARE': True
            }
        )

        if not start_dt:
            raise ValueError("Could not parse the date/time.")

        # Ensure timezone is IST
        if start_dt.tzinfo is None:
            start_dt = ist_tz.localize(start_dt)
        elif start_dt.tzinfo != ist_tz:
            start_dt = start_dt.astimezone(ist_tz)

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
        print(f"📧 GMAIL_COMPOSE detected")
        print(f"📧 To: {plan.get('to')}")
        print(f"📧 Subject: {plan.get('subject')}")
        print(f"📧 Body preview: {plan.get('body', '')[:100]}")

        result = {
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
        print(f"✅ Returning EMAIL_PREVIEW: {result}")
        return result

    # Handle Gmail Search - execute immediately
    if action == "GMAIL_SEARCH":
        result = execute_action("GMAIL_SEARCH", {
            "query": plan.get("query", ""),
            "max_results": plan.get("max_results", 10)
        }, user_email)

        if result.get('success') and 'emails' in result:
            if not result['emails']:
                return {"response_type": "RESULT", "response": result.get('message', 'No emails found')}

            response = f"{result['message']}\n\n"
            for email in result['emails']:
                response += f"📧 From: {email.get('from', 'Unknown')}\n"
                response += f"📨 Subject: {email.get('subject', '(No Subject)')}\n"
                response += f"📅 Date: {email.get('date', 'Unknown')}\n"
                response += f"💬 {email.get('snippet', '')[:100]}...\n"
                response += f"ID: {email.get('id')}\n\n"
            return {"response_type": "RESULT", "response": response}
        else:
            return {"response_type": "RESULT", "response": result.get('message', 'Search failed')}

    # Handle Gmail List Unread - execute immediately
    if action == "GMAIL_LIST_UNREAD":
        result = execute_action("GMAIL_LIST_UNREAD", {
            "max_results": plan.get("max_results", 10)
        }, user_email)

        if result.get('success') and 'emails' in result:
            if not result['emails']:
                return {"response_type": "RESULT", "response": "You have no unread emails! 🎉"}

            response = f"{result['message']}\n\n"
            for email in result['emails']:
                response += f"📧 From: {email.get('from', 'Unknown')}\n"
                response += f"📨 Subject: {email.get('subject', '(No Subject)')}\n"
                response += f"📅 Date: {email.get('date', 'Unknown')}\n"
                response += f"💬 {email.get('snippet', '')[:100]}...\n"
                response += f"ID: {email.get('id')}\n\n"
            return {"response_type": "RESULT", "response": response}
        else:
            return {"response_type": "RESULT", "response": result.get('message', 'Failed to retrieve unread emails')}

    # Handle Gmail Read - execute immediately
    if action == "GMAIL_READ":
        result = execute_action("GMAIL_READ", {
            "message_id": plan.get("message_id")
        }, user_email)

        if result.get('success') and 'email' in result:
            email = result['email']
            response = f"📧 Email Details\n\n"
            response += f"From: {email.get('from', 'Unknown')}\n"
            response += f"To: {email.get('to', 'Unknown')}\n"
            response += f"Subject: {email.get('subject', '(No Subject)')}\n"
            response += f"Date: {email.get('date', 'Unknown')}\n\n"
            response += f"Body:\n{email.get('body', 'No body content')}\n\n"

            if email.get('attachments'):
                response += f"Attachments ({len(email['attachments'])}):\n"
                for att in email['attachments']:
                    response += f"  📎 {att['filename']} ({att['size']} bytes)\n"

            return {"response_type": "RESULT", "response": response}
        else:
            return {"response_type": "RESULT", "response": result.get('message', 'Failed to read email')}

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
        # Format time in IST for display
        try:
            ist_tz = pytz.timezone('Asia/Kolkata')
            start_dt = datetime.fromisoformat(plan.get('start_time').replace('Z', '+00:00'))
            if start_dt.tzinfo is None:
                start_dt = ist_tz.localize(start_dt)
            else:
                start_dt = start_dt.astimezone(ist_tz)
            display_time = start_dt.strftime('%B %d at %I:%M %p IST')
            message_prefix = f"Ready to schedule: '{plan.get('summary')}' on {display_time}."
        except:
            message_prefix = f"Ready to schedule: '{plan.get('summary')}'."

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

    # Handle Calendar Delete - execute immediately
    if action == "CALENDAR_DELETE":
        result = execute_action("CALENDAR_DELETE", {
            "event_id": plan.get("event_id"),
            "summary": plan.get("summary")
        }, user_email)

        if result.get('success'):
            return {"response_type": "RESULT", "response": result['message']}
        else:
            return {"response_type": "ERROR", "response": result.get('message', 'Failed to delete event')}

    # Handle Calendar Update/Reschedule - with approval
    if action == "CALENDAR_UPDATE":
        # Parse new times if provided
        new_start_time = plan.get("new_start_time")
        new_end_time = plan.get("new_end_time")

        if new_start_time and not new_end_time:
            # If only start time provided, calculate end time
            date_info = parse_date_string_to_iso(new_start_time)
            if date_info['success']:
                new_start_time = date_info['start_time']
                new_end_time = date_info['end_time']

        try:
            ist_tz = pytz.timezone('Asia/Kolkata')
            if new_start_time:
                start_dt = datetime.fromisoformat(new_start_time.replace('Z', '+00:00'))
                if start_dt.tzinfo is None:
                    start_dt = ist_tz.localize(start_dt)
                else:
                    start_dt = start_dt.astimezone(ist_tz)
                display_time = start_dt.strftime('%B %d at %I:%M %p IST')
                message_prefix = f"Ready to reschedule '{plan.get('summary_search')}' to {display_time}."
            else:
                message_prefix = f"Ready to update event '{plan.get('summary_search')}'."
        except:
            message_prefix = f"Ready to update event '{plan.get('summary_search')}'."

        return {
            "response_type": "APPROVAL",
            "action": "CALENDAR_UPDATE",
            "message": message_prefix,
            "params": {
                "event_id": plan.get("event_id", ""),
                "summary_search": plan.get("summary_search"),
                "new_summary": plan.get("new_summary"),
                "new_start_time": new_start_time,
                "new_end_time": new_end_time,
                "new_description": plan.get("new_description"),
                "new_attendees": plan.get("new_attendees", [])
            }
        }

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

    # Handle Contacts Create - with approval
    if action == "CONTACTS_CREATE":
        message = f"Ready to add contact: {plan.get('given_name', '')} {plan.get('family_name', '')} ({plan.get('email', 'No email')})."
        return {
            "response_type": "APPROVAL",
            "action": "CONTACTS_CREATE",
            "message": message,
            "params": {
                "given_name": plan.get("given_name"),
                "family_name": plan.get("family_name"),
                "email": plan.get("email"),
                "phone": plan.get("phone")
            }
        }

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
