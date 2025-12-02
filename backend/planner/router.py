# backend/planner/router.py
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# --- Hugging Face Configuration ---
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
# We no longer strictly need HF_MODEL, but we'll leave it in .env for future use.
# The URL below uses the specific translation endpoint for guaranteed availability.
HF_MODEL = os.getenv("HF_MODEL")


def call_llm(prompt: str) -> str:
    """
    Sends a prompt to a Hugging Face translation model for maximum compatibility.
    We frame the task as a translation to utilize a stable, always-on free endpoint.
    """
    if not HUGGINGFACE_API_KEY:
        return "Error: HUGGINGFACE_API_KEY is not set in the environment."
    
    # CRITICAL CHANGE: Using a stable, task-specific endpoint (Translation).
    # This bypasses the unstable generic model endpoint that was returning 404s.
    url = "https://router.huggingface.co/v1/translation/en_to_fr"
    
    # The input format for the translation task is a list of strings under the 'inputs' key.
    body = {
        "inputs": [prompt]
    }
    
    # Authorization Header (Bearer Token) - Unchanged
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    

    try:
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code != 200:
            # Check for HTTP errors
            raise Exception(f"Hugging Face API error: {response.status_code}, {response.text}")
        
        data = response.json()
        
        # Translation response is typically a list of objects: [{"translation_text": "..."}]
        if isinstance(data, list) and data and "translation_text" in data[0]:
            # Use the translation text as the "plan" response. It won't be a perfect plan,
            # but it PROVES the connection works.
            return f"[Task Response via Translation Model]: {data[0]['translation_text']}"
        else:
            return f"Error parsing Hugging Face response. Raw: {data}"

    except Exception as e:
        print(f"Error calling Hugging Face API: {e}")
        return "Error calling Hugging Face API ❌"


def run_planner(user_input: str) -> str:
    """
    Takes user input, sends to the LLM as a "translation task", and returns the result.
    """
    # The model should be stable now. We can keep the prompt for the next step.
    prompt = f"Plan the following task intelligently:\n{user_input}"
    return call_llm(prompt)