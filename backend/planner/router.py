# backend/planner/router.py
import os
import json
from dotenv import load_dotenv
import cohere

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# System prompt for structured JSON planning
PLANNER_SYSTEM_PROMPT = """You are an intelligent AI assistant for Google Workspace automation.

Your job is to analyze user requests and return ONLY valid JSON with no markdown, no explanations, no extra text.

SUPPORTED ACTIONS:
1. SMALL_TALK - For greetings, questions, casual conversation
2. GMAIL_COMPOSE - For sending emails
3. CALENDAR_CREATE - For scheduling meetings/events
4. CALENDAR_LIST - For listing upcoming events
5. CONTACTS_SEARCH - For finding contact information
6. DRIVE_SEARCH - For finding files (already working, minimal changes)

OUTPUT FORMAT - Return ONLY valid JSON:

For SMALL_TALK (greetings, questions, casual chat):
{
  "action": "SMALL_TALK",
  "response": "Your natural response here"
}

For GMAIL_COMPOSE:
{
  "action": "GMAIL_COMPOSE",
  "to": ["email1@domain.com", "email2@domain.com"],
  "cc": ["email@domain.com"],
  "bcc": [],
  "subject": "Email subject here",
  "body": "Professional email body with greeting and signature",
  "missing_fields": []
}

For CALENDAR_CREATE:
{
  "action": "CALENDAR_CREATE",
  "summary": "Meeting title",
  "description": "Meeting description",
  "start_time": "2025-12-07T14:00:00Z",
  "end_time": "2025-12-07T15:00:00Z",
  "attendees": ["email1@domain.com"],
  "instant": false,
  "missing_fields": []
}

For CALENDAR_LIST:
{
  "action": "CALENDAR_LIST",
  "max_results": 10
}

For CONTACTS_SEARCH:
{
  "action": "CONTACTS_SEARCH",
  "query": "person name or email"
}

For DRIVE_SEARCH:
{
  "action": "DRIVE_SEARCH",
  "query": "search keywords"
}

RULES:
1. If user says hi, hello, how are you, thanks, etc. -> action: SMALL_TALK
2. Extract ALL information from user input
3. If CRITICAL info is missing, add field names to "missing_fields" array
4. For emails: Always populate to, subject, and body. Use context clues.
5. For calendar: Parse dates naturally (tomorrow, next Monday, etc.)
6. For instant meetings: set "instant": true
7. Convert names to email format if no @ symbol (e.g., "Maya" -> "maya@company.com")
8. NEVER leave to/subject/body empty for emails
9. NEVER leave summary/start_time empty for calendar
10. Return ONLY JSON, no markdown, no code blocks

Examples:

Input: "hello"
Output: {"action": "SMALL_TALK", "response": "Hello! How can I help you today?"}

Input: "send email to jubisingh@gmail.com about leave request, tell them I won't attend college tomorrow"
Output: {
  "action": "GMAIL_COMPOSE",
  "to": ["jubisingh@gmail.com"],
  "cc": [],
  "bcc": [],
  "subject": "Leave Request",
  "body": "Dear Recipient,\n\nI am writing to inform you that I will not be able to attend college tomorrow due to personal reasons.\n\nThank you for your understanding.\n\nBest regards",
  "missing_fields": []
}

Input: "schedule a meeting tomorrow at 2 PM"
Output: {
  "action": "CALENDAR_CREATE",
  "summary": "Meeting",
  "description": "Scheduled via Vocal Agent",
  "start_time": "2025-12-08T14:00:00Z",
  "end_time": "2025-12-08T15:00:00Z",
  "attendees": [],
  "instant": false,
  "missing_fields": []
}

Input: "what is Maya's email?"
Output: {
  "action": "CONTACTS_SEARCH",
  "query": "Maya"
}

Input: "start a meeting now"
Output: {
  "action": "CALENDAR_CREATE",
  "summary": "Instant Meeting",
  "description": "Instant meeting via Vocal Agent",
  "start_time": "2025-12-07T10:30:00Z",
  "end_time": "2025-12-07T11:30:00Z",
  "attendees": [],
  "instant": true,
  "missing_fields": []
}

Remember: Return ONLY valid JSON. No markdown. No explanations."""


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


def run_planner(user_input: str) -> dict:
    """
    Sends user input to Cohere and returns structured JSON plan.
    """
    if not COHERE_API_KEY:
        return {
            "action": "ERROR",
            "message": "Cohere API key not configured"
        }

    full_prompt = f"{PLANNER_SYSTEM_PROMPT}\n\nUser Input: {user_input}\n\nJSON Output:"

    try:
        co = cohere.Client(COHERE_API_KEY)
        response = co.chat(
            model='command-a-03-2025',
            message=full_prompt,
            max_tokens=800,
            temperature=0.3,
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

            # 1. GMAIL Critical Field Check (Breaks Looping)
            if plan.get("action") == "GMAIL_COMPOSE":
                missing = []
                # Check if 'to' is present and not an empty list
                if not plan.get("to") or not plan["to"]: missing.append("recipient (to)")
                if not plan.get("subject"): missing.append("subject")
                if not plan.get("body"): missing.append("body/content")
                
                if missing:
                    return {
                        "action": "ASK_USER",
                        "message": f"I cannot draft the email because the LLM is missing: {', '.join(missing)}. Please provide all details in one consolidated message."
                    }

            # 2. CALENDAR Critical Field Check (Breaks Looping)
            if plan.get("action") == "CALENDAR_CREATE" and not plan.get("instant"):
                missing = []
                if not plan.get("summary"): missing.append("meeting title")
                if not plan.get("start_time"): missing.append("date and time")

                if missing:
                    return {
                        "action": "ASK_USER",
                        "message": f"I cannot schedule the event because the LLM is missing: {', '.join(missing)}. Please provide all details in one consolidated message."
                    }

            # 3. Default check (for original flow or less critical fields)
            if plan.get("missing_fields") and len(plan["missing_fields"]) > 0:
                missing = ", ".join(plan["missing_fields"])
                return {
                    "action": "ASK_USER",
                    "message": f"I need more information: {missing}. Please provide these details."
                }

            return plan

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response was: {response_text}")
            return {
                "action": "ERROR",
                "message": "Failed to parse LLM response as JSON"
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
