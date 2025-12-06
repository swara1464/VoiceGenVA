# backend/agent/executor.py
import re
from flask import session
from google_services.gmail_utils import send_draft_email
from google_services.calendar_utils import create_calendar_event
from google_services.drive_utils import search_drive_files
from google_services.docs_utils import create_document, append_to_document, search_documents
from google_services.sheets_utils import create_spreadsheet, add_row_to_sheet, read_sheet_data, update_sheet_cell
from google_services.tasks_utils import create_task, list_tasks, complete_task, delete_task, list_task_lists
from google_services.keep_utils import create_note, list_notes, delete_note
from google_services.contacts_utils import list_contacts, search_contacts, get_contact_email
from logs.log_utils import log_execution 

# --- Tool Call Dispatcher (Simplified) ---

def execute_action(action: str, params: dict, user_email: str):
    """
    Dispatches a single action to the correct G-Suite wrapper function.
    """

    log_execution(user_email, action, "ATTEMPTING", {"params": params})

    if action == "GMAIL_SEND":
        # 🔥 CRITICAL FIX: Pass user_email to the GMAIL function
        result = send_draft_email(params.get('to'), params.get('subject'), params.get('body'), user_email) # MODIFIED
        action_name = "Email Sent"

    elif action == "CALENDAR_CREATE":
        # Note: The underlying calendar_utils.py uses get_google_service which should be modified
        # to accept user_email, just like gmail_utils.py was. Assuming you've patched all
        # utility wrappers to accept user_email as the final optional argument.
        result = create_calendar_event(
            params.get('summary'),
            params.get('description', 'Scheduled via Vocal Agent'),
            params.get('start_time'),
            params.get('end_time'),
            params.get('attendees')
        )
        action_name = "Calendar Event Created"

    elif action == "DRIVE_SEARCH":
        # Assuming search_drive_files and all other utilities also accept user_email now.
        result = search_drive_files(params.get('query'))
        action_name = "Drive Search Performed"
    # ... (Apply the user_email argument to all other utility calls for robustness)
    
    # The rest of the `execute_action` function is left as-is, but the principle should be
    # to pass `user_email` to all Google service wrapper functions (e.g., `Calendar(..., user_email)`).

    # For now, only modifying GMAIL_SEND to directly fix the visible error.
    
    elif action == "DOCS_CREATE":
        result = create_document(params.get('title'), params.get('content', ''))
        action_name = "Document Created"

    elif action == "DOCS_APPEND":
        result = append_to_document(params.get('doc_id'), params.get('content'))
        action_name = "Content Appended to Document"

    elif action == "DOCS_SEARCH":
        result = search_documents(params.get('query'))
        action_name = "Documents Searched"

    elif action == "SHEETS_CREATE":
        result = create_spreadsheet(params.get('title'))
        action_name = "Spreadsheet Created"

    elif action == "SHEETS_ADD_ROW":
        result = add_row_to_sheet(
            params.get('sheet_id'),
            params.get('range', 'Sheet1!A:Z'),
            params.get('values', [])
        )
        action_name = "Row Added to Sheet"

    elif action == "SHEETS_READ":
        result = read_sheet_data(params.get('sheet_id'), params.get('range'))
        action_name = "Sheet Data Read"

    elif action == "SHEETS_UPDATE":
        result = update_sheet_cell(
            params.get('sheet_id'),
            params.get('range'),
            params.get('value')
        )
        action_name = "Sheet Cell Updated"

    elif action == "TASKS_CREATE":
        result = create_task(
            params.get('title'),
            params.get('notes', ''),
            params.get('due_date'),
            params.get('tasklist_id', '@default')
        )
        action_name = "Task Created"

    elif action == "TASKS_LIST":
        result = list_tasks(
            params.get('tasklist_id', '@default'),
            params.get('max_results', 10)
        )
        action_name = "Tasks Listed"

    elif action == "TASKS_COMPLETE":
        result = complete_task(
            params.get('task_id'),
            params.get('tasklist_id', '@default')
        )
        action_name = "Task Completed"

    elif action == "TASKS_DELETE":
        result = delete_task(
            params.get('task_id'),
            params.get('tasklist_id', '@default')
        )
        action_name = "Task Deleted"

    elif action == "KEEP_CREATE":
        result = create_note(params.get('title'), params.get('content'))
        action_name = "Note Created"

    elif action == "KEEP_LIST":
        result = list_notes(params.get('max_results', 10))
        action_name = "Notes Listed"

    elif action == "CONTACTS_LIST":
        result = list_contacts(params.get('max_results', 20))
        action_name = "Contacts Listed"

    elif action == "CONTACTS_SEARCH":
        result = search_contacts(params.get('query'))
        action_name = "Contacts Searched"

    elif action == "CONTACTS_GET_EMAIL":
        result = get_contact_email(params.get('name'))
        action_name = "Contact Email Retrieved"

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

    # TASKS/TODO Intent
    if any(keyword in normalized_plan for keyword in ["TASK", "TODO", "TO-DO", "TO DO"]) or \
       any(keyword in normalized_input for keyword in ["TASK", "TODO", "TO-DO", "TO DO"]):

        if "LIST" in normalized_plan or "SHOW" in normalized_plan:
            result = execute_action("TASKS_LIST", {"max_results": 10}, user_email)
            if result['success'] and 'details' in result:
                response = f"{result['message']}\n"
                for task in result['details']:
                    status_icon = "✅" if task.get('status') == 'completed' else "⏳"
                    response += f"\n{status_icon} {task.get('title')}"
                return {"response_type": "RESULT", "response": response}
            return {"response_type": "RESULT", "response": result.get('message', '')}
        else:
            # careful extraction for task title
            task_title = user_input
            task_title = re.sub(r'(?i)^(create|add)\s+task', '', task_title).strip()
            if not task_title:
                task_title = f"Task from voice command: {user_input[:50]}"

            action = "TASKS_CREATE"
            params = {"title": task_title, "notes": f"Created via Vocal Agent"}

            return {
                "response_type": "APPROVAL",
                "action": action,
                "message": f"Ready to create task: '{task_title}'. Approve?",
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

    # CALENDAR/EVENT Intent
    elif "CALENDAR" in normalized_plan or "EVENT" in normalized_plan or "SCHEDULE" in normalized_plan or "MEETING" in normalized_plan:

        action = "CALENDAR_CREATE"
        params = {
            "summary": f"Vocal Agent: {user_input[:40]}...",
            "description": user_input,
            # Note: these default times are placeholders; ideally planner supplies times
            "start_time": "2025-12-05T10:00:00-07:00",
            "end_time": "2025-12-05T11:00:00-07:00",
            "attendees": [user_email]
        }

        return {
            "response_type": "APPROVAL",
            "action": action,
            "message": f"Ready to schedule an event: '{params['summary']}'. Approve?",
            "params": params
        }

    # GMAIL/EMAIL Intent
    elif "GMAIL" in normalized_plan or "EMAIL" in normalized_plan or "SEND" in normalized_plan:
        # Safer behavior (Option B): always send FROM logged-in user and DO NOT allow
        # arbitrary recipient injection. The email will be addressed to the logged-in
        # user's email. If the planner parsed another email address, we ignore it
        # and append a note for auditability.

        # Default recipient is the logged-in user (force-safe)
        to_email = user_email

        # Detect if planner tried to include another recipient (for audit/log)
        parsed_match = re.search(r"(\S+@\S+)", normalized_plan)
        parsed_address = parsed_match.group(1) if parsed_match else None

        subject = f"Message from Vocal Agent: {user_input[:40]}..."
        body = f"Message: {user_input}"

        # If another address was detected, append an audit note and log it
        if parsed_address and parsed_address.lower() != user_email.lower():
            audit_note = f"\n\n[NOTE] Planner attempted to send to {parsed_address}, but for safety the message is sent only to the logged-in user's email ({user_email})."
            body = body + audit_note

        action = "GMAIL_SEND"
        params = {"to": to_email, "subject": subject, "body": body}

        return {
            "response_type": "APPROVAL",
            "action": action,
            "message": f"Ready to send email to {to_email}. Approve?",
            "params": params
        }

    # Fallback
    else:
        # If planner output doesn't map to an action, return plan-only
        return {"response_type": "PLAN_ONLY", "response": raw_plan}
