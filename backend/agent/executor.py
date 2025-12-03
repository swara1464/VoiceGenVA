# backend/agent/executor.py
import re
from flask import session 
# CORRECTED IMPORTS: Use simple imports now that app.py handles the path
from google_services.gmail_utils import send_draft_email
from google_services.calendar_utils import create_calendar_event
from google_services.drive_utils import search_drive_files
from logs.log_utils import log_execution 

# --- Tool Call Dispatcher (Simplified) ---

def execute_action(action: str, params: dict, user_email: str):
    """
    Dispatches a single action to the correct G-Suite wrapper function.
    """
    
    # 1. Log attempt
    log_execution(user_email, action, "ATTEMPTING", {"params": params})
    
    if action == "GMAIL_SEND":
        result = send_draft_email(params.get('to'), params.get('subject'), params.get('body'))
        action_name = "Email Sent"
        
    elif action == "CALENDAR_CREATE":
        result = create_calendar_event(
            params.get('summary'), 
            params.get('description', 'Scheduled via Vocal Agent'), 
            params.get('start_time'), 
            params.get('end_time'),
            params.get('attendees')
        )
        action_name = "Calendar Event Created"
        
    elif action == "DRIVE_SEARCH":
        result = search_drive_files(params.get('query'))
        action_name = "Drive Search Performed"

    else:
        result = {"success": False, "message": f"Unknown action: {action}"}
        action_name = "Unknown Action"
        
    # 2. Log result
    if result['success']:
        log_execution(user_email, action_name, "SUCCESS", result)
    else:
        log_execution(user_email, action_name, "FAILED", result)
        
    return result


def parse_and_execute_plan(raw_plan: str, user_input: str):
    """
    CRITICAL: Parses the Cohere plan output and extracts a high-level action 
    and parameters for execution.
    
    For the MVP, this relies on the Cohere planner writing clear, keyword-based steps.
    """
    user_email = session.get("user", {}).get("email", "unknown_user")

    if not user_email or user_email == "unknown_user":
        return {"response_type": "ERROR", "response": "User not logged in. Cannot execute action."}

    # Normalize plan text for simple keyword matching
    normalized_plan = raw_plan.upper().replace('\n', ' ').strip()

    # --- Step 1: Intent Classification (Based on plan output) ---
    
    # 1. GMAIL/EMAIL Intent
    if "GMAIL" in normalized_plan or "EMAIL" in normalized_plan or "SEND" in normalized_plan:
        
        # Simplified extraction: target email, subject, body 
        to_match = re.search(r"(\S+@\S+)", normalized_plan)
        # Fallback to the user's email if no explicit recipient is found
        to_email = to_match.group(1) if to_match else user_email 
        
        subject = f"Action Required: {user_input[:40]}..."
        body = f"Drafted content based on your request: '{user_input}'. Please review and send."
        
        action = "GMAIL_SEND"
        params = {"to": to_email, "subject": subject, "body": body}

        return {
            "response_type": "APPROVAL",
            "action": action,
            "message": f"Ready to send an email to {to_email}. Do you approve this action?",
            "params": params
        }

    # 2. CALENDAR/EVENT Intent
    elif "CALENDAR" in normalized_plan or "EVENT" in normalized_plan or "SCHEDULE" in normalized_plan:
        # Simplified parameters for demo
        action = "CALENDAR_CREATE"
        params = {
            "summary": f"Vocal Agent: {user_input[:40]}...",
            "description": user_input, # Use the full input as description
            "start_time": "2025-12-04T10:00:00-07:00", # Fixed demo time 
            "end_time": "2025-12-04T11:00:00-07:00", 
            "attendees": [user_email] 
        }

        return {
            "response_type": "APPROVAL",
            "action": action,
            "message": f"Ready to schedule an event for tomorrow at 10 AM. Do you approve?",
            "params": params
        }

    # 3. DRIVE/SEARCH Intent
    elif "DRIVE" in normalized_plan or "SEARCH" in normalized_plan:
        # Simple extraction of the search query
        query_match = re.search(r"SEARCH (.+?)", normalized_plan)
        query = query_match.group(1).strip() if query_match else "latest files"
        
        # Search executes immediately
        result = execute_action("DRIVE_SEARCH", {"query": query}, user_email)
        
        if result['success']:
            drive_response = f"{result['message']} Found:"
            for file in result['details']:
                 drive_response += f"\n- {file['name']} ({file['link']})"
            return {"response_type": "RESULT", "response": drive_response}
        else:
            return {"response_type": "RESULT", "response": result['message']}
            
    # 4. Fallback (If the plan cannot be mapped to an action)
    else:
        return {"response_type": "PLAN_ONLY", "response": raw_plan}