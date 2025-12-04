# backend/planner/router.py
import os
import json
from dotenv import load_dotenv
import cohere
import requests # Keeping this import as it was in the original file

# --- CRITICAL FIX: Define Cohere exception classes manually ---
# This bypasses the ImportError caused by package structure mismatch in your local SDK, 
# ensuring the app starts while still allowing general exception catching.
class APIError(Exception): pass
class CohereError(Exception): pass


load_dotenv()

# --- Cohere Configuration (LLM for planning) ---
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

# System prompt for the agent planner
PLANNER_SYSTEM_PROMPT = (
    "You are an intelligent agent responsible for planning a user's request to interact "
    "with Google Workspace applications (Gmail, Calendar, Drive, Docs, Sheets, Tasks, Contacts, Keep). "
    "Your output MUST be a plan. Analyze the user's request below, break it down "
    "into a concise, numbered list of discrete, actionable steps, and identify the "
    "required Google Workspace service (e.g., Gmail, Calendar, Drive) for each step. "
    "Do not execute the steps or add any conversational filler. Only output the plan."
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

    except APIError as e:
        # These now refer to the generic classes above, but still catch exceptions
        print(f"Cohere API Error: {e}")
        return f"Cohere API Error: {e} ❌"
    except CohereError as e:
        print(f"Cohere Error: {e}")
        return f"Cohere Error: {e} ❌"
    except Exception as e:
        print(f"General Error calling Cohere API: {e}")
        return "General Error calling Cohere API ❌"


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

    except APIError as e:
        print(f"Cohere API Planner Error: {e}")
        return f"Cohere API Planner Error: {e} ❌"
    except CohereError as e:
        print(f"Cohere Planner Error: {e}")
        return f"Cohere Planner Error: {e} ❌"
    except Exception as e:
        print(f"General Error calling Cohere Planner API: {e}")
        return "General Error calling Cohere Planner API ❌"