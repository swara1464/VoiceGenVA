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

DETECT USER INTENT:
- Email keywords: "send email", "email to", "mail to", "compose", "draft" -> GMAIL_COMPOSE
- Calendar keywords: "schedule", "meeting", "appointment", "calendar", "create event" -> CALENDAR_CREATE
- Calendar list: "list events", "upcoming events", "my events" -> CALENDAR_LIST
- Calendar delete: "delete event", "remove event", "cancel event" -> CALENDAR_DELETE
- Contact keywords: "what is", "email", "phone number", "contact" -> CONTACTS_SEARCH
- Drive keywords: "search drive", "find file", "look for", "my documents" -> DRIVE_SEARCH
- Small talk: "hi", "hello", "how are you", "thanks", "goodbye" -> SMALL_TALK

JSON OUTPUT FORMATS (COPY EXACTLY):

GMAIL_COMPOSE (for any email request):
{
  "action": "GMAIL_COMPOSE",
  "to": ["recipient@email.com"],
  "cc": [],
  "bcc": [],
  "subject": "Email Subject",
  "body": "Email body with greeting and signature"
}

CALENDAR_CREATE (for scheduling):
{
  "action": "CALENDAR_CREATE",
  "summary": "Meeting Title",
  "description": "Meeting details",
  "start_time": "2025-12-08T14:00:00Z",
  "end_time": "2025-12-08T15:00:00Z",
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
  "event_id": "event_id_here",
  "summary": "event title to find"
}

CONTACTS_SEARCH (for finding contacts):
{
  "action": "CONTACTS_SEARCH",
  "query": "person name"
}

DRIVE_SEARCH (for finding files):
{
  "action": "DRIVE_SEARCH",
  "query": "search keywords"
}

SMALL_TALK (only for greetings/casual chat):
{
  "action": "SMALL_TALK",
  "response": "Your response"
}

STRICT RULES:
1. ANY email request MUST use GMAIL_COMPOSE (never SMALL_TALK)
2. If user mentions a name without email, use "name@placeholder.com" for to field
3. Always generate complete subject and body for emails
4. Parse dates like "tomorrow", "next Monday" to ISO format
5. For "instant meeting" or "meeting now", set instant: true
6. For delete event, extract event title into "summary" field
7. For drive search, extract the KEY TERM (e.g., "Swara's documents" -> "Swara", "project report" -> "project report")
8. Return ONLY the JSON object, nothing else

EXAMPLES:

User: "Send email to Jubi saying I can't attend class tomorrow"
{"action": "GMAIL_COMPOSE", "to": ["jubi@placeholder.com"], "cc": [], "bcc": [], "subject": "Unable to Attend Class Tomorrow", "body": "Hi Jubi,\n\nI wanted to let you know that I won't be able to attend class tomorrow.\n\nThank you for understanding.\n\nBest regards"}

User: "Send email to swarapawanekar@gmail.com cc swarasameerpawanekar@gmail.com bcc 1ms22ai063@msrit.edu saying This is my resume subject Resume"
{"action": "GMAIL_COMPOSE", "to": ["swarapawanekar@gmail.com"], "cc": ["swarasameerpawanekar@gmail.com"], "bcc": ["1ms22ai063@msrit.edu"], "subject": "Resume", "body": "This is my resume"}

User: "Delete the event Daily Sync"
{"action": "CALENDAR_DELETE", "event_id": "", "summary": "Daily Sync"}

User: "Schedule a team meeting for tomorrow at 9 AM"
{"action": "CALENDAR_CREATE", "summary": "Team Meeting", "description": "Scheduled via Vocal Agent", "start_time": "2025-12-08T09:00:00Z", "end_time": "2025-12-08T10:00:00Z", "attendees": [], "instant": false}

User: "What is Swara's email?"
{"action": "CONTACTS_SEARCH", "query": "Swara"}

User: "Search my drive for Devops Report"
{"action": "DRIVE_SEARCH", "query": "Devops Report"}

User: "Hey agent search Drive for Swara's documents"
{"action": "DRIVE_SEARCH", "query": "Swara"}

User: "hi"
{"action": "SMALL_TALK", "response": "Hello! How can I help you today?"}

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
    if not COHERE_API_KEY:
        return {
            "action": "ERROR",
            "message": "Cohere API key not configured"
        }

    # Use system message for better instruction following
    try:
        co = cohere.Client(COHERE_API_KEY)
        response = co.chat(
            model='command-a-03-2025',
            message=f"User request: {user_input}\n\nRespond with ONLY valid JSON:",
            preamble=PLANNER_SYSTEM_PROMPT,
            max_tokens=800,
            temperature=0.2,
        )

        if not response.text:
            return {
                "action": "ERROR",
                "message": "Empty response from LLM"
            }

        # Clean response
        response_text = response.text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        # Parse JSON
        try:
            plan = json.loads(response_text)
            print(f"✓ LLM returned valid JSON: {plan}")

            # Trust LLM output completely - no validation
            return plan

        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"❌ Raw LLM response: {response_text[:500]}")

            # Check if this is an email request that failed to parse
            email_keywords = ["email", "send", "mail", "compose", "draft", "message to"]
            is_email_request = any(keyword in user_input.lower() for keyword in email_keywords)

            if is_email_request:
                # Don't fallback to small talk for email requests
                return {
                    "action": "ERROR",
                    "message": f"I detected you want to send an email, but I couldn't process it properly. Please try again with format: 'Send email to [email] subject [subject] saying [message]'"
                }

            # Only use fallback for genuine small talk
            fallback_response = call_llm_for_small_talk(user_input)
            return {
                "action": "SMALL_TALK",
                "response": fallback_response
            }

    except Exception as e:
        print(f"Error calling Cohere: {e}")
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
