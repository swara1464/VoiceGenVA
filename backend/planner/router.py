# backend/planner/router.py
import os
import json
from dotenv import load_dotenv
import cohere

load_dotenv()

# --- Cohere Configuration (LLM for planning) ---
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# System prompt for the agent planner
PLANNER_SYSTEM_PROMPT = (
    "You are an intelligent AI agent planner for a voice-controlled Google Workspace automation system. "
    "Your role is to analyze user voice commands and create execution plans.\n\n"

    "AVAILABLE SERVICES:\n"
    "- GMAIL: Send emails, draft messages\n"
    "- CALENDAR: Create events, schedule meetings (with Google Meet links)\n"
    "- DRIVE: Search for files, access documents\n"
    "- DOCS: Create or search Google Docs, append content\n"
    "- SHEETS: Create spreadsheets, add rows, read/update cells\n"
    "- TASKS: Create, list, complete, or delete tasks\n"
    "- KEEP: Create or list notes (stored as Google Docs)\n"
    "- CONTACTS: Search or list contacts, get email addresses\n\n"

    "PLANNING RULES:\n"
    "1. Identify the PRIMARY service needed based on keywords:\n"
    "   - Email/send/message → GMAIL\n"
    "   - Schedule/meeting/event/calendar → CALENDAR\n"
    "   - Search files/drive/find document → DRIVE\n"
    "   - Create document/doc/write → DOCS\n"
    "   - Spreadsheet/sheet/table → SHEETS\n"
    "   - Task/todo/to-do → TASKS\n"
    "   - Note/reminder/keep → KEEP\n"
    "   - Contact/phone/people/email address → CONTACTS\n\n"

    "2. For multi-step requests, list ALL steps in order, identifying the service for each.\n"
    "3. Extract key parameters:\n"
    "   - Email addresses (recipient@domain.com)\n"
    "   - Search queries (file names, keywords)\n"
    "   - Dates and times (convert natural language to specific times)\n"
    "   - Task/note titles and content\n\n"

    "4. Be EXPLICIT about the action:\n"
    "   - 'SEARCH Drive for attendance sheet'\n"
    "   - 'SEND email to hr@company.com'\n"
    "   - 'CREATE task: Complete project report'\n"
    "   - 'SCHEDULE meeting tomorrow at 2 PM'\n\n"

    "OUTPUT FORMAT:\n"
    "Provide a numbered list of steps with the service name clearly stated. Example:\n"
    "1. DRIVE: Search for 'attendance sheet' file\n"
    "2. GMAIL: Send email to hr@company.com with the file\n"
    "3. CALENDAR: Schedule follow-up meeting next week\n\n"

    "Keep your plan concise and actionable. Do NOT execute the steps yourself. "
    "Do NOT add conversational filler. Only provide the plan."
)


def call_llm(prompt: str) -> str:
    """
    Sends a prompt to the Cohere LLM for the /echo route (simple response).
    """
    if not COHERE_API_KEY:
        return "Error: COHERE_API_KEY is not set in the environment. Please set it to proceed."
    
    # Use a generic system prompt for the raw /echo route
    echo_system_prompt = "You are a helpful assistant. Respond concisely to the user's message."
    
    # FIX: Combine system prompt and user message into the 'message' argument.
    full_prompt = f"{echo_system_prompt}\n\nUser Message: {prompt}"

    try:
        # 1. Initialize Cohere Client
        co = cohere.Client(COHERE_API_KEY)
        
        # 2. Call the chat endpoint (UNSUPPORTED 'system_prompt' removed)
        response = co.chat(
            model='command-a-03-2025', # Using command-a-03-2025 for a capable and fast model
            message=full_prompt, # Now contains the system instruction
            max_tokens=512,
            temperature=0.7,
        )
        
        # 3. Process response
        if response.text:
            llm_response = response.text.strip()
            return f"[Echo Response via Cohere LLM]: {llm_response}"
        else:
            return f"Error: Cohere Chat returned an empty response."

    except Exception as e:
        print(f"Error calling Cohere API: {e}")
        return f"Error calling Cohere API: {str(e)}"


def run_planner(user_input: str) -> str:
    """
    Takes user input and sends it to the Cohere LLM with the specific planning
    system prompt. This is used by the /planner/run route.
    """
    if not COHERE_API_KEY:
        return "Error: COHERE_API_KEY is not set in the environment. Please set it to proceed."
    
    # FIX: Combine the planner system prompt and user input into the 'message' argument.
    full_planner_prompt = f"{PLANNER_SYSTEM_PROMPT}\n\nUser Request: {user_input}"

    try:
        co = cohere.Client(COHERE_API_KEY)
        
        # We use the dedicated planning system prompt here (UNSUPPORTED 'system_prompt' removed)
        response = co.chat(
            model='command-a-03-2025', 
            message=full_planner_prompt, # Now contains the planning instruction
            max_tokens=1024,
            temperature=0.3,
        )
        
        if response.text:
            plan = response.text.strip()
            return f"[Agent Plan via Cohere LLM]:\n{plan}"
        else:
            return f"Error: Cohere Chat returned an empty plan response."

    except Exception as e:
        print(f"Error calling Cohere Planner API: {e}")
        return f"Error calling Cohere Planner API: {str(e)}"