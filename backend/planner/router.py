# backend/planner/router.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def call_gemini(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """
    Sends a prompt to Gemini Pro and returns the response text.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        # Optional parameters
        "temperature": 0.7,
        "maxOutputTokens": 200
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code != 200:
            raise Exception(f"Gemini API error: {response.status_code}, {response.text}")
        data = response.json()
        # Extract the response text
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return "Error parsing Gemini response ❌"
    except Exception as e:
        print("Error calling Gemini API:", e)
        return "Error calling Gemini API ❌"

def run_planner(user_input: str) -> str:
    """
    Takes user input, sends to Gemini, and returns the generated plan.
    """
    prompt = f"Plan the following task intelligently:\n{user_input}"
    return call_gemini(prompt)
