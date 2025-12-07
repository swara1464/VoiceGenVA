# backend/agent/executor.py
import re
from flask import session
from google_services.gmail_utils import send_draft_email
from google_services.gmail_compose import build_gmail_preview
from google_services.calendar_utils import create_calendar_event, get_upcoming_events, get_event_meet_link, create_instant_meet
from google_services.drive_utils import search_drive_files, list_recent_files, get_shareable_link, list_files_in_folder
from google_services.docs_utils import create_document, append_to_document, search_documents
from google_services.sheets_utils import create_spreadsheet, add_row_to_sheet, read_sheet_data, update_sheet_cell
from google_services.tasks_utils import create_task, list_tasks, complete_task, delete_task, list_task_lists, update_task
from google_services.keep_utils import create_note, list_notes, delete_note
from google_services.contacts_utils import list_contacts, search_contacts, get_contact_email
from logs.log_utils import log_execution
from planner.router import generate_email_body
from utils.intent_classifier import classify_intent 

# --- Tool Call Dispatcher (Simplified) ---

def execute_action(action: str, params: dict, user_email: str):
    """
    Dispatches a single action to the correct G-Suite wrapper function.
    """

    log_execution(user_email, action, "ATTEMPTING", {"params": params})

    if action == "GMAIL_SEND":
        result = send_draft_email(
            params.get('to'),
            params.get('subject'),
            params.get('body'),
            params.get('cc'),
            params.get('bcc'),
            user_email,
            approved=params.get('approved', False)
        )
        action_name = "Email Sent"

    elif action == "GMAIL_COMPOSE":
        result = build_gmail_preview(
            user_instruction=params.get('instruction', ''),
            recipient_text=params.get('to', ''),
            cc_text=params.get('cc', ''),
            bcc_text=params.get('bcc', ''),
            user_email=user_email,
            user_full_name=params.get('user_name', '')
        )
        action_name = "Email Preview Built"

    elif action == "CALENDAR_CREATE":
        result = create_calendar_event(
            params.get('summary'),
            params.get('description', 'Scheduled via Vocal Agent'),
            params.get('start_time'),
            params.get('end_time'),
            params.get('attendees'),
            user_email
        )
        action_name = "Calendar Event Created"

    elif action == "CALENDAR_LIST":
        result = get_upcoming_events(params.get('max_results', 10), user_email)
        action_name = "Upcoming Events Retrieved"

    elif action == "CALENDAR_GET_MEET_LINK":
        result = get_event_meet_link(
            params.get('event_id'),
            params.get('summary_search'),
            user_email
        )
        action_name = "Meet Link Retrieved"

    elif action == "CALENDAR_INSTANT_MEET":
        result = create_instant_meet(
            title=params.get('title', 'Google Meet'),
            attendees=params.get('attendees', []),
            user_email=user_email,
            timezone=params.get('timezone', 'UTC')
        )
        action_name = "Instant Meet Created"

    elif action == "DRIVE_SEARCH":
        result = search_drive_files(params.get('query'), user_email)
        action_name = "Drive Search Performed"

    elif action == "DOCS_CREATE":
        result = create_document(params.get('title'), params.get('content', ''), user_email)
        action_name = "Document Created"

    elif action == "DOCS_APPEND":
        result = append_to_document(params.get('doc_id'), params.get('content'), user_email)
        action_name = "Content Appended to Document"

    elif action == "DOCS_SEARCH":
        result = search_documents(params.get('query'), user_email)
        action_name = "Documents Searched"

    elif action == "SHEETS_CREATE":
        result = create_spreadsheet(params.get('title'), user_email)
        action_name = "Spreadsheet Created"

    elif action == "SHEETS_ADD_ROW":
        result = add_row_to_sheet(
            params.get('sheet_id'),
            params.get('range', 'Sheet1!A:Z'),
            params.get('values', []),
            user_email
        )
        action_name = "Row Added to Sheet"

    elif action == "SHEETS_READ":
        result = read_sheet_data(params.get('sheet_id'), params.get('range'), user_email)
        action_name = "Sheet Data Read"

    elif action == "SHEETS_UPDATE":
        result = update_sheet_cell(
            params.get('sheet_id'),
            params.get('range'),
            params.get('value'),
            user_email
        )
        action_name = "Sheet Cell Updated"

    elif action == "TASKS_CREATE":
        result = create_task(
            params.get('title'),
            params.get('notes', ''),
            params.get('due_date'),
            params.get('tasklist_id', '@default'),
            user_email
        )
        action_name = "Task Created"

    elif action == "TASKS_LIST":
        result = list_tasks(
            params.get('tasklist_id', '@default'),
            params.get('max_results', 10),
            user_email
        )
        action_name = "Tasks Listed"

    elif action == "TASKS_COMPLETE":
        result = complete_task(
            params.get('task_id'),
            params.get('tasklist_id', '@default'),
            user_email
        )
        action_name = "Task Completed"

    elif action == "TASKS_DELETE":
        result = delete_task(
            params.get('task_id'),
            params.get('tasklist_id', '@default'),
            user_email
        )
        action_name = "Task Deleted"

    elif action == "KEEP_CREATE":
        result = create_note(params.get('title'), params.get('content'), user_email)
        action_name = "Note Created"

    elif action == "KEEP_LIST":
        result = list_notes(params.get('max_results', 10), user_email)
        action_name = "Notes Listed"

    elif action == "CONTACTS_LIST":
        result = list_contacts(params.get('max_results', 20), user_email)
        action_name = "Contacts Listed"

    elif action == "CONTACTS_SEARCH":
        result = search_contacts(params.get('query'), user_email)
        action_name = "Contacts Searched"

    elif action == "CONTACTS_GET_EMAIL":
        result = get_contact_email(params.get('name'), user_email)
        action_name = "Contact Email Retrieved"

    elif action == "DRIVE_RECENT":
        result = list_recent_files(params.get('limit', 10), user_email)
        action_name = "Recent Files Listed"

    elif action == "DRIVE_GET_LINK":
        result = get_shareable_link(params.get('file_id'), user_email)
        action_name = "Shareable Link Retrieved"

    elif action == "DRIVE_LIST_FOLDER":
        result = list_files_in_folder(params.get('folder_name'), user_email)
        action_name = "Folder Files Listed"

    elif action == "TASKS_UPDATE":
        result = update_task(
            params.get('task_id'),
            params.get('title'),
            params.get('notes'),
            params.get('due_date'),
            params.get('status'),
            params.get('tasklist_id', '@default'),
            user_email
        )
        action_name = "Task Updated"

    elif action == "TASKS_LIST_ALL":
        result = list_task_lists(user_email)
        action_name = "Task Lists Retrieved"

    else:
        result = {"success": False, "message": f"Unknown action: {action}"}
        action_name = "Unknown Action"

    if result['success']:
        log_execution(user_email, action_name, "SUCCESS", result)
    else:
        log_execution(user_email, action_name, "FAILED", result)

    return result


def parse_and_execute_plan(raw_plan: str, user_input: str, user_email: str):

    """
    Parses the Cohere plan output and extracts a high-level action
    and parameters for execution. Supports all Google Workspace services.
    """
    # Note: user_email is passed from the authenticated context (JWT/session)
    if not user_email or user_email == "unknown_user":
        return {"response_type": "ERROR", "response": "User not logged in. Cannot execute action."}

    normalized_plan = raw_plan.upper().replace('\n', ' ').strip()
    normalized_input = user_input.upper()

    # TASKS/TODO Intent (Enhanced natural language support)
    if any(keyword in normalized_plan for keyword in ["TASK", "TODO", "TO-DO", "TO DO"]) or \
       any(keyword in normalized_input for keyword in ["TASK", "TODO", "TO-DO", "TO DO"]):

        # Check if user wants to list/show tasks
        if any(keyword in normalized_plan or keyword in normalized_input for keyword in ["LIST", "SHOW", "VIEW", "DISPLAY", "GET MY", "WHAT ARE", "SEE MY"]):
            result = execute_action("TASKS_LIST", {"max_results": 10}, user_email)
            if result['success'] and 'details' in result:
                response = f"{result['message']}\n"
                for task in result['details']:
                    status_icon = "✅" if task.get('status') == 'completed' else "⏳"
                    response += f"\n{status_icon} {task.get('title')}"
                return {"response_type": "RESULT", "response": response}
            return {"response_type": "RESULT", "response": result.get('message', '')}

        # Check if user wants to mark task as complete
        elif any(keyword in normalized_input for keyword in ["COMPLETE", "DONE", "FINISH", "MARK AS COMPLETE", "MARK AS DONE"]):
            # This will be handled by the expanded Tasks UI feature
            return {"response_type": "RESULT", "response": "Task completion feature requires task selection. Please use the Tasks UI to select and complete specific tasks."}

        # Check if user wants to delete a task
        elif any(keyword in normalized_input for keyword in ["DELETE", "REMOVE", "CANCEL"]):
            return {"response_type": "RESULT", "response": "Task deletion requires task selection. Please use the Tasks UI to select and delete specific tasks."}

        # Default: Create a new task
        else:
            # Extract task title from natural language
            task_title = user_input

            # Remove common command prefixes
            task_title = re.sub(r'(?i)^(create|add|make|new)\s+(a\s+)?(task|todo|to-do|to do)\s+(to\s+)?', '', task_title).strip()
            task_title = re.sub(r'(?i)^(remind me to|reminding me to)\s+', '', task_title).strip()

            # Extract due date if mentioned (tomorrow, today, specific date)
            due_date = None
            if "tomorrow" in user_input.lower():
                import datetime
                due_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%dT00:00:00Z')
            elif "today" in user_input.lower():
                import datetime
                due_date = datetime.datetime.now().strftime('%Y-%m-%dT00:00:00Z')

            if not task_title:
                task_title = f"Task: {user_input[:50]}"

            action = "TASKS_CREATE"
            params = {
                "title": task_title,
                "notes": f"Created via Vocal Agent from: {user_input}",
                "due_date": due_date
            }

            return {
                "response_type": "APPROVAL",
                "action": action,
                "message": f"Ready to create task: '{task_title}'{' (Due: Tomorrow)' if due_date and 'tomorrow' in user_input.lower() else ''}. Approve?",
                "params": params
            }

    # KEEP/NOTE Intent
    elif any(keyword in normalized_plan for keyword in ["KEEP", "NOTE"]) or \
         any(keyword in normalized_input for keyword in ["NOTE", "REMINDER"]):

        if "LIST" in normalized_plan or "SHOW" in normalized_plan:
            result = execute_action("KEEP_LIST", {"max_results": 10}, user_email)
            if result['success'] and 'details' in result:
                response = f"{result['message']}\n"
                for note in result['details']:
                    title = note.get('title', 'Untitled')
                    link = note.get('link', '')
                    response += f"\n- {title} ({link})"
                return {"response_type": "RESULT", "response": response}
            return {"response_type": "RESULT", "response": result.get('message', '')}
        else:
            note_title = f"Note: {user_input[:50]}"
            note_content = user_input

            action = "KEEP_CREATE"
            params = {"title": note_title, "content": note_content}

            return {
                "response_type": "APPROVAL",
                "action": action,
                "message": f"Ready to create note: '{note_title}'. Approve?",
                "params": params
            }

    # DOCS/DOCUMENT Intent
    elif any(keyword in normalized_plan for keyword in ["DOC", "DOCUMENT"]):

        if "SEARCH" in normalized_plan:
            query_match = re.search(r"SEARCH (\w+)", normalized_plan)
            query = query_match.group(1).strip() if query_match else user_input.split()[-1]

            result = execute_action("DOCS_SEARCH", {"query": query}, user_email)
            if result['success'] and 'details' in result:
                response = f"{result['message']}\n"
                for doc in result['details']:
                    name = doc.get('name', 'Unnamed')
                    link = doc.get('link', '')
                    response += f"\n- {name} ({link})"
                return {"response_type": "RESULT", "response": response}
            return {"response_type": "RESULT", "response": result.get('message', '')}
        else:
            doc_title = f"Document: {user_input[:50]}"
            doc_content = user_input

            action = "DOCS_CREATE"
            params = {"title": doc_title, "content": doc_content}

            return {
                "response_type": "APPROVAL",
                "action": action,
                "message": f"Ready to create document: '{doc_title}'. Approve?",
                "params": params
            }

    # SHEETS/SPREADSHEET Intent
    elif any(keyword in normalized_plan for keyword in ["SHEET", "SPREADSHEET"]):

        sheet_title = f"Spreadsheet: {user_input[:50]}"

        action = "SHEETS_CREATE"
        params = {"title": sheet_title}

        return {
            "response_type": "APPROVAL",
            "action": action,
            "message": f"Ready to create spreadsheet: '{sheet_title}'. Approve?",
            "params": params
        }

    # CONTACTS Intent
    elif any(keyword in normalized_plan for keyword in ["CONTACT", "PHONE", "PEOPLE"]):

        if "SEARCH" in normalized_plan or "FIND" in normalized_plan:
            query_match = re.search(r"(SEARCH|FIND) (\w+)", normalized_plan)
            query = query_match.group(2).strip() if query_match else user_input.split()[-1]

            result = execute_action("CONTACTS_SEARCH", {"query": query}, user_email)
            if result['success'] and 'details' in result:
                response = f"{result['message']}\n"
                for contact in result['details']:
                    name = contact.get('name', 'Unknown')
                    email = contact.get('email', '')
                    response += f"\n- {name}: {email}"
                return {"response_type": "RESULT", "response": response}
            return {"response_type": "RESULT", "response": result.get('message', '')}
        else:
            result = execute_action("CONTACTS_LIST", {"max_results": 20}, user_email)
            if result['success'] and 'details' in result:
                response = f"{result['message']}\n"
                for contact in result['details'][:5]:
                    name = contact.get('name', 'Unknown')
                    email = contact.get('email', '')
                    response += f"\n- {name}: {email}"
                return {"response_type": "RESULT", "response": response}
            return {"response_type": "RESULT", "response": result.get('message', '')}

    # DRIVE/SEARCH Intent
    elif "DRIVE" in normalized_plan or ("SEARCH" in normalized_plan and "FILE" in normalized_plan):

        # Check for recent files request
        if "RECENT" in normalized_plan or "RECENT FILES" in user_input.upper():
            result = execute_action("DRIVE_RECENT", {"limit": 10}, user_email)
            if result['success'] and 'details' in result:
                drive_response = f"{result['message']}\n"
                for file in result['details']:
                    name = file.get('name', 'Unnamed')
                    link = file.get('link', '')
                    drive_response += f"\n- {name} ({link})"
                return {"response_type": "RESULT", "response": drive_response}
            return {"response_type": "RESULT", "response": result.get('message', '')}

        # Check for folder listing request
        elif "FOLDER" in normalized_plan or "IN MY" in user_input.upper():
            folder_match = re.search(r"(?:in my|inside|folder)\s+(\w+)", user_input.lower())
            folder_name = folder_match.group(1) if folder_match else "Documents"

            result = execute_action("DRIVE_LIST_FOLDER", {"folder_name": folder_name}, user_email)
            if result['success'] and 'details' in result:
                folder_data = result['details']
                drive_response = f"{result['message']}\n"
                for file in folder_data.get('files', [])[:10]:
                    name = file.get('name', 'Unnamed')
                    link = file.get('link', '')
                    drive_response += f"\n- {name} ({link})"
                return {"response_type": "RESULT", "response": drive_response}
            return {"response_type": "RESULT", "response": result.get('message', '')}

        # Default: search Drive
        else:
            query_match = re.search(r"SEARCH (.+?)(?:IN|FOR|$)", normalized_plan)
            query = query_match.group(1).strip() if query_match else user_input.split()[-1]

            result = execute_action("DRIVE_SEARCH", {"query": query}, user_email)

            if result['success'] and 'details' in result:
                drive_response = f"{result['message']}\n"
                if isinstance(result['details'], list):
                    for file in result['details']:
                        name = file.get('name', 'Unnamed')
                        link = file.get('link', '')
                        drive_response += f"\n- {name} ({link})"
                return {"response_type": "RESULT", "response": drive_response}
            else:
                return {"response_type": "RESULT", "response": result.get('message', '')}

    # CALENDAR/EVENT/MEETING Intent (Enhanced for natural language + instant meetings + Meet links)
    elif "CALENDAR" in normalized_plan or "EVENT" in normalized_plan or "SCHEDULE" in normalized_plan or "MEETING" in normalized_plan or "MEET" in normalized_plan:

        # Check if user wants to list upcoming events
        if any(keyword in normalized_input for keyword in ["LIST", "SHOW", "UPCOMING", "NEXT", "MY EVENTS"]):
            result = execute_action("CALENDAR_LIST", {"max_results": 10}, user_email)
            if result['success'] and 'details' in result:
                response = f"{result['message']}\n\n"
                for event in result['details']:
                    summary = event.get('summary', 'No Title')
                    start = event.get('start', 'No time')
                    meet_link = event.get('meet_link', 'No Meet link')
                    response += f"\n📅 {summary}\n   ⏰ {start}\n   🔗 {meet_link}\n"
                return {"response_type": "RESULT", "response": response}
            return {"response_type": "RESULT", "response": result.get('message', '')}

        # Check if user wants to get Meet link
        elif any(keyword in normalized_input for keyword in ["MEET LINK", "MEETING LINK", "GET LINK", "WHAT IS THE LINK"]):
            # Try to extract meeting name/title
            link_match = re.search(r'(?:link for|link of)\s+(.+?)(?:\s+meeting|\s+$)', user_input, re.IGNORECASE)
            if link_match:
                meeting_name = link_match.group(1).strip()
                result = execute_action("CALENDAR_GET_MEET_LINK", {"summary_search": meeting_name}, user_email)
                if result['success']:
                    return {"response_type": "RESULT", "response": result.get('message', '')}
                return {"response_type": "RESULT", "response": result.get('message', '')}
            else:
                # Get the next upcoming meeting
                result = execute_action("CALENDAR_LIST", {"max_results": 1}, user_email)
                if result['success'] and 'details' in result and len(result['details']) > 0:
                    event = result['details'][0]
                    meet_link = event.get('meet_link', 'No Meet link available')
                    return {"response_type": "RESULT", "response": f"Next meeting: {event.get('summary')}\nMeet link: {meet_link}"}
                return {"response_type": "RESULT", "response": "No upcoming meetings found."}

        # Create a new meeting/event (existing logic continues below)

        import datetime
        import pytz

        # Extract meeting title/summary
        summary = f"Meeting via Vocal Agent"

        # Try to extract topic after "about", "for", "regarding"
        topic_match = re.search(r'(?:about|for|regarding|on)\s+(.+?)(?:\s+at|\s+tomorrow|\s+today|\s+next|\s+with|\s+$)', user_input, re.IGNORECASE)
        if topic_match:
            summary = topic_match.group(1).strip().capitalize()
        else:
            # Try to extract after "meeting"
            meeting_match = re.search(r'meeting\s+(.+?)(?:\s+at|\s+tomorrow|\s+today|\s+next|\s+with|\s+$)', user_input, re.IGNORECASE)
            if meeting_match:
                summary = meeting_match.group(1).strip().capitalize()

        # Parse time - check for instant meeting
        now = datetime.datetime.now(pytz.UTC)
        start_time = now
        end_time = now + datetime.timedelta(hours=1)

        if any(keyword in user_input.lower() for keyword in ["right now", "now", "instant", "immediately", "create a meeting"]):
            # Instant meeting
            start_time = now
            end_time = now + datetime.timedelta(hours=1)
            summary = f"{summary} (Instant Meeting)" if summary != "Meeting via Vocal Agent" else "Instant Meeting"
        elif "tomorrow" in user_input.lower():
            # Tomorrow - default to 10 AM
            tomorrow = now + datetime.timedelta(days=1)
            start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
            end_time = start_time + datetime.timedelta(hours=1)
        elif "today" in user_input.lower():
            # Today - try to extract time or use current time
            today = now.replace(minute=0, second=0, microsecond=0)
            start_time = today
            end_time = start_time + datetime.timedelta(hours=1)

        # Try to parse specific time mentions (e.g., "at 2 PM", "at 14:00")
        time_match = re.search(r'at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', user_input, re.IGNORECASE)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            meridiem = time_match.group(3)

            if meridiem and meridiem.lower() == 'pm' and hour != 12:
                hour += 12
            elif meridiem and meridiem.lower() == 'am' and hour == 12:
                hour = 0

            start_time = start_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            end_time = start_time + datetime.timedelta(hours=1)

        # Extract attendees
        attendees = []
        # Look for email addresses
        email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_input)
        attendees.extend(email_matches)

        # Look for "invite X" or "with X" patterns
        invite_match = re.search(r'(?:invite|with|and)\s+([A-Za-z\s]+?)(?:\s+at|\s+tomorrow|\s+$)', user_input, re.IGNORECASE)
        if invite_match:
            names = invite_match.group(1).strip()
            # Split by "and" or comma
            name_list = re.split(r'[,]|\s+and\s+', names, flags=re.IGNORECASE)
            for name in name_list:
                name = name.strip()
                if name and '@' not in name:
                    # Create placeholder email
                    attendees.append(f"{name.lower().replace(' ', '.')}@company.com")

        action = "CALENDAR_CREATE"
        params = {
            "summary": summary,
            "description": f"Meeting created via Vocal Agent: {user_input}",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "attendees": attendees if attendees else None
        }

        return {
            "response_type": "APPROVAL",
            "action": action,
            "message": f"Ready to schedule: '{summary}' at {start_time.strftime('%Y-%m-%d %H:%M')} (1 hour). {'Attendees: ' + ', '.join(attendees) if attendees else ''} Approve?",
            "params": params
        }

    # GMAIL/EMAIL Intent
    elif "GMAIL" in normalized_plan or "EMAIL" in normalized_plan or "SEND" in normalized_plan or "MAIL" in normalized_plan:
        # Extract recipient email from user input or plan
        to_email = ""
        parsed_match = re.search(r"(\S+@\S+)", user_input)
        if parsed_match:
            to_email = parsed_match.group(1)

        # Try to extract recipient from natural language if no email found
        if not to_email:
            # Look for patterns like "to HR", "send to john", etc.
            recipient_match = re.search(r'(?:to|email|mail)\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)', user_input, re.IGNORECASE)
            if recipient_match:
                recipient_name = recipient_match.group(1).strip()
                # Construct placeholder email that user can edit
                to_email = f"{recipient_name.lower().replace(' ', '.')}@company.com"

        # Generate subject from user input (try to extract topic after "about")
        subject = "Message from Vocal Agent"

        # Check for "about" pattern to extract subject
        about_match = re.search(r'about\s+(.+?)(?:\s+to|\s+$)', user_input, re.IGNORECASE)
        if about_match:
            topic = about_match.group(1).strip()
            # Clean up topic
            topic = re.sub(r'\s+to\s+.+$', '', topic, flags=re.IGNORECASE)
            subject = topic.capitalize()
        else:
            # Try keyword matching
            subject_keywords = ["complaint", "report", "update", "inquiry", "question", "feedback", "follow-up", "followup", "meeting", "reminder", "onboarding"]
            for keyword in subject_keywords:
                if keyword in user_input.lower():
                    subject = f"{keyword.capitalize()}"
                    break

        # Generate professional email body using LLM
        body = generate_email_body(user_input, to_email, subject)

        return {
            "response_type": "EMAIL_FORM",
            "action": "GMAIL_SEND",
            "message": "I've drafted an email for you. Please review and edit before sending.",
            "params": {
                "to": to_email,
                "cc": "",
                "bcc": "",
                "subject": subject,
                "body": body
            }
        }

    # Fallback
    else:
        # If planner output doesn't map to an action, return plan-only
        return {"response_type": "PLAN_ONLY", "response": raw_plan}
