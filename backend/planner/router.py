# backend/planner/router.py
import os
import json
from dotenv import load_dotenv
import cohere

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# System prompt for structured JSON planning
PLANNER_SYSTEM_PROMPT = """YOU MUST RETURN ONLY VALID JSON. NO TEXT. NO EXPLANATIONS. NO MARKDOWN. ONLY JSON.

CRITICAL: Your response MUST be parseable by json.loads(). Do not write anything except JSON.

TIMEZONE: ALL DATES AND TIMES MUST BE IN INDIAN STANDARD TIME (IST, UTC+5:30). When parsing dates like "tomorrow at 2 PM", calculate IST time.

DETECT USER INTENT (MOST IMPORTANT FIRST):
- PRIORITY #1 - Email send keywords: "send", "email", "mail", "compose", "draft", "message to" -> GMAIL_COMPOSE
  ALWAYS use GMAIL_COMPOSE for ANY email send request, even if information is incomplete
- Email search: "search email", "find email", "search inbox", "emails from" -> GMAIL_SEARCH
- Email read: "read email", "show email", "open email" (requires message_id) -> GMAIL_READ
- Email unread: "unread emails", "list unread", "show unread" -> GMAIL_LIST_UNREAD
- Calendar keywords: "schedule", "meeting", "appointment", "calendar", "create event" -> CALENDAR_CREATE
- Calendar list: "list events", "upcoming events", "my events" -> CALENDAR_LIST
- Calendar delete: "delete event", "remove event", "cancel event" -> CALENDAR_DELETE
- Calendar update: "modify event", "reschedule", "change event", "update event" -> CALENDAR_UPDATE
- Contact keywords: "what is", "email", "phone number", "contact" -> CONTACTS_SEARCH
- Contact create: "add contact", "create contact", "new contact" -> CONTACTS_CREATE
- Drive keywords: "search drive", "find file", "look for", "my documents" -> DRIVE_SEARCH
- Task create: "create task", "add task", "new task", "remind me to" -> TASKS_CREATE
- Task list: "list tasks", "show tasks", "my tasks" -> TASKS_LIST
- Task complete: "mark task complete", "complete task", "finish task" -> TASKS_COMPLETE
- Sheets create: "create spreadsheet", "new spreadsheet", "make a sheet" -> SHEETS_CREATE
- Sheets add row: "add row to sheet", "append to spreadsheet" -> SHEETS_ADD_ROW
- Sheets read: "read sheet", "get sheet data", "show spreadsheet" -> SHEETS_READ
- Docs create: "create document", "new doc", "make a document" -> DOCS_CREATE
- Docs append: "add to document", "append to doc", "write to document" -> DOCS_APPEND
- Small talk: "hi", "hello", "how are you", "thanks", "goodbye" -> SMALL_TALK

JSON OUTPUT FORMATS (COPY EXACTLY):

GMAIL_COMPOSE (for sending email):
{
  "action": "GMAIL_COMPOSE",
  "to": ["recipient@email.com"],
  "cc": [],
  "bcc": [],
  "subject": "Email Subject",
  "body": "Email body with greeting and signature"
}

GMAIL_SEARCH (for searching inbox):
{
  "action": "GMAIL_SEARCH",
  "query": "search term or Gmail query syntax",
  "max_results": 10
}

GMAIL_READ (for reading specific email):
{
  "action": "GMAIL_READ",
  "message_id": "message_id_here"
}

GMAIL_LIST_UNREAD (for listing unread emails):
{
  "action": "GMAIL_LIST_UNREAD",
  "max_results": 10
}

CALENDAR_CREATE (for scheduling):
{
  "action": "CALENDAR_CREATE",
  "summary": "Meeting Title",
  "description": "Meeting details",
  "start_time": "2025-12-08T14:00:00+05:30",
  "end_time": "2025-12-08T15:00:00+05:30",
  "attendees": [],
  "instant": false
}

CALENDAR_LIST (for viewing events):
{
  "action": "CALENDAR_LIST",
  "max_results": 10
}

CALENDAR_DELETE (for deleting events):
{
  "action": "CALENDAR_DELETE",
  "event_id": "",
  "summary": "event title to find"
}

CALENDAR_UPDATE (for modifying/rescheduling events):
{
  "action": "CALENDAR_UPDATE",
  "event_id": "",
  "summary_search": "event title to find",
  "new_summary": "",
  "new_start_time": "2025-12-10T10:00:00+05:30",
  "new_end_time": "2025-12-10T11:00:00+05:30",
  "new_description": "",
  "new_attendees": []
}

CONTACTS_SEARCH (for finding contacts):
{
  "action": "CONTACTS_SEARCH",
  "query": "person name"
}

CONTACTS_CREATE (for creating new contacts):
{
  "action": "CONTACTS_CREATE",
  "given_name": "John",
  "family_name": "Doe",
  "email": "john@example.com",
  "phone": "+1234567890"
}

DRIVE_SEARCH (for finding files):
{
  "action": "DRIVE_SEARCH",
  "query": "search keywords"
}

TASKS_CREATE (for creating tasks):
{
  "action": "TASKS_CREATE",
  "title": "Task title",
  "notes": "Task description",
  "due_date": "2025-12-10T00:00:00Z"
}

TASKS_LIST (for listing tasks):
{
  "action": "TASKS_LIST",
  "max_results": 10
}

TASKS_COMPLETE (for marking tasks complete):
{
  "action": "TASKS_COMPLETE",
  "task_id": "",
  "title_search": "task title to find"
}

SHEETS_CREATE (for creating spreadsheets):
{
  "action": "SHEETS_CREATE",
  "title": "Spreadsheet Title"
}

SHEETS_ADD_ROW (for adding data to spreadsheet):
{
  "action": "SHEETS_ADD_ROW",
  "sheet_id": "spreadsheet_id",
  "range_name": "Sheet1!A:D",
  "values": ["Value1", "Value2", "Value3"]
}

SHEETS_READ (for reading spreadsheet data):
{
  "action": "SHEETS_READ",
  "sheet_id": "spreadsheet_id",
  "range_name": "Sheet1!A1:D10"
}

DOCS_CREATE (for creating documents):
{
  "action": "DOCS_CREATE",
  "title": "Document Title"
}

DOCS_APPEND (for adding text to document):
{
  "action": "DOCS_APPEND",
  "doc_id": "document_id",
  "text": "Text to append"
}

SMALL_TALK (only for greetings/casual chat):
{
  "action": "SMALL_TALK",
  "response": "Your response"
}

STRICT RULES (NEVER BREAK THESE):
1. **CRITICAL EMAIL RULE**: ANY email/send/mail/compose/draft request MUST ALWAYS use GMAIL_COMPOSE action. NEVER use SMALL_TALK for emails.
2. For emails: If user mentions name without email, use "name@placeholder.com" for to field
3. For emails: Always generate complete subject and body, even if user only provides partial info
4. For calendar: Parse dates like "tomorrow", "next Monday" to ISO format
5. For calendar: "instant meeting" or "meeting now" sets instant: true
6. For calendar delete: Extract event title into "summary" field
7. For drive: Extract KEY TERM (e.g., "Swara's documents" -> "Swara", "DevOps project" -> "DevOps")
8. Return ONLY JSON - no markdown, no text, no explanations

EXAMPLES:

User: "Send email to Jubi saying I can't attend class tomorrow"
{"action": "GMAIL_COMPOSE", "to": ["jubi@placeholder.com"], "cc": [], "bcc": [], "subject": "Unable to Attend Class Tomorrow", "body": "Hi Jubi,\n\nI wanted to let you know that I won't be able to attend class tomorrow.\n\nThank you for understanding.\n\nBest regards"}

User: "Send email to swarapawanekar@gmail.com cc swarasameerpawanekar@gmail.com bcc 1ms22ai063@msrit.edu saying This is my resume subject Resume"
{"action": "GMAIL_COMPOSE", "to": ["swarapawanekar@gmail.com"], "cc": ["swarasameerpawanekar@gmail.com"], "bcc": ["1ms22ai063@msrit.edu"], "subject": "Resume", "body": "This is my resume"}

User: "Delete the event Daily Sync"
{"action": "CALENDAR_DELETE", "event_id": "", "summary": "Daily Sync"}

User: "Schedule a team meeting for tomorrow at 9 AM"
{"action": "CALENDAR_CREATE", "summary": "Team Meeting", "description": "Scheduled via Vocal Agent", "start_time": "2025-12-08T09:00:00+05:30", "end_time": "2025-12-08T10:00:00+05:30", "attendees": [], "instant": false}

User: "What is Swara's email?"
{"action": "CONTACTS_SEARCH", "query": "Swara"}

User: "Search my drive for Devops Report"
{"action": "DRIVE_SEARCH", "query": "Devops Report"}

User: "Hey agent search Drive for Swara's documents"
{"action": "DRIVE_SEARCH", "query": "Swara"}

User: "hi"
{"action": "SMALL_TALK", "response": "Hello! How can I help you today?"}

User: "Search my inbox for emails from john"
{"action": "GMAIL_SEARCH", "query": "from:john", "max_results": 10}

User: "Show me unread emails"
{"action": "GMAIL_LIST_UNREAD", "max_results": 10}

User: "Find emails about project update"
{"action": "GMAIL_SEARCH", "query": "project update", "max_results": 10}

REMEMBER: ONLY JSON OUTPUT. NO OTHER TEXT."""


def call_llm_for_small_talk(user_input: str) -> str:
    """
    Generates natural response for small talk using Cohere.
    """
    if not COHERE_API_KEY:
        return "I'm unable to respond right now. Please try again."

    prompt = f"You are a helpful AI assistant. Respond naturally to the user without emojis. Be professional but friendly.\n\nUser: {user_input}\n\nAssistant:"

    try:
        co = cohere.Client(COHERE_API_KEY)
        response = co.chat(
            model='command-a-03-2025',
            message=prompt,
            max_tokens=200,
            temperature=0.7,
        )

        if response.text:
            return response.text.strip()
        return "I'm here to help with Gmail, Calendar, Contacts, and Drive."

    except Exception as e:
        print(f"Error in small talk: {e}")
        return "I'm here to help. What would you like to do?"


def run_planner(user_input: str, user_email: str = None) -> dict:
    """
    Sends user input to Cohere and returns structured JSON plan.
    """
    print("="*80)
    print(f"🎯 PLANNER CALLED with input: {user_input}")
    print(f"👤 User email: {user_email}")
    print("="*80)

    if not COHERE_API_KEY:
        print("❌ No Cohere API key")
        return {
            "action": "ERROR",
            "message": "Cohere API key not configured"
        }

    # Use system message for better instruction following
    try:
        co = cohere.Client(COHERE_API_KEY)
        print("📡 Calling Cohere API...")
        response = co.chat(
            model='command-a-03-2025',
            message=f"User request: {user_input}\n\nRespond with ONLY valid JSON:",
            preamble=PLANNER_SYSTEM_PROMPT,
            max_tokens=800,
            temperature=0.2,
        )

        print(f"📥 Received response from Cohere")

        if not response.text:
            print("❌ Empty response from LLM")
            return {
                "action": "ERROR",
                "message": "Empty response from LLM"
            }

        # Clean response
        response_text = response.text.strip()
        print(f"📝 Raw response (first 200 chars): {response_text[:200]}")

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        # Parse JSON
        try:
            plan = json.loads(response_text)
            print(f"✅ LLM returned valid JSON: {plan}")
            print(f"✅ Action detected: {plan.get('action')}")

            return plan

        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"❌ Raw LLM response: {response_text[:500]}")

            print("💬 JSON failed to parse, returning error")
            return {
                "action": "ERROR",
                "message": "I couldn't understand that request. Could you rephrase it?"
            }

    except Exception as e:
        print(f"❌ Error calling Cohere: {e}")
        import traceback
        traceback.print_exc()
        return {
            "action": "ERROR",
            "message": f"Error calling LLM: {str(e)}"
        }

def generate_email_body(user_instruction: str, recipient: str = "", subject: str = "") -> str:
    """
    This function is deprecated. Email body is now generated by run_planner.
    Kept for backward compatibility.
    """
    if not COHERE_API_KEY:
        return "Please write your email body manually."

    prompt = f"""Generate a professional email body based on this instruction: {user_instruction}

Recipient: {recipient if recipient else 'Not specified'}
Subject: {subject if subject else 'Not specified'}

Write a complete email with greeting, body, and signature. Keep it professional and concise."""

    try:
        co = cohere.Client(COHERE_API_KEY)
        response = co.chat(
            model='command-a-03-2025',
            message=prompt,
            max_tokens=400,
            temperature=0.7,
        )

        if response.text:
            return response.text.strip()
        return "Unable to generate email. Please write manually."

    except Exception as e:
        print(f"Error generating email: {e}")
        return "Unable to generate email. Please write manually."
