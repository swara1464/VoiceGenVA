# backend/utils/intent_classifier.py
import re
import json
from logs.log_utils import log_execution
import cohere
import os
from dotenv import load_dotenv

load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")

GREETING_PATTERNS = [
    r'\b(hi|hello|hey|howdy|greetings|what\'?s\s*up|how are you|how r u|aapka naam|kon ho|tum koun ho)\b'
]

SMALL_TALK_PATTERNS = [
    r'\b(thank you|thanks|no thanks|okay|sure|yes|no|maybe|k|ok|cool|nice|good|bye|goodbye|see you)\b',
    r'\b(how are you|how\'?s it|what\'?s up)\b'
]

EMAIL_PATTERNS = [
    r'\b(send|email|mail|compose|draft|write.*email|message)\b'
]

DRIVE_PATTERNS = [
    r'\b(search|find|look for|get|open|download).*drive\b',
    r'\b(drive).*(search|find|look for|get|open|file)\b',
    r'\b(search|find|look for).*file\b',
    r'\b(recent|my).*(files|documents)\b'
]

CALENDAR_PATTERNS = [
    r'\b(schedule|create|add|book).*(meeting|event|calendar|appointment)\b',
    r'\b(calendar).*(create|schedule|add|book)\b',
    r'\b(meeting|event)\b'
]

MEET_PATTERNS = [
    r'\b(start|create|begin).*(meet|google meet|video call|call)\b',
    r'\b(meet link|google meet)\b'
]

def is_greeting_or_smalltalk(text: str) -> bool:
    """Check if text is greeting or small talk."""
    text_lower = text.lower()

    for pattern in GREETING_PATTERNS + SMALL_TALK_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return True

    return False

def classify_intent_heuristic(text: str) -> dict:
    """
    Heuristic-based intent classification (fast, no LLM).
    Returns: {"intent": "chat|email|drive|calendar|meet", "confidence": 0-1, "method": "heuristic"}
    """
    text_lower = text.lower()

    if is_greeting_or_smalltalk(text):
        return {
            "intent": "chat",
            "confidence": 0.95,
            "method": "heuristic"
        }

    if any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in EMAIL_PATTERNS):
        return {
            "intent": "email",
            "confidence": 0.85,
            "method": "heuristic"
        }

    if any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in MEET_PATTERNS):
        return {
            "intent": "meet",
            "confidence": 0.9,
            "method": "heuristic"
        }

    if any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in CALENDAR_PATTERNS):
        return {
            "intent": "calendar",
            "confidence": 0.85,
            "method": "heuristic"
        }

    if any(re.search(pattern, text_lower, re.IGNORECASE) for pattern in DRIVE_PATTERNS):
        return {
            "intent": "drive",
            "confidence": 0.85,
            "method": "heuristic"
        }

    return {
        "intent": "chat",
        "confidence": 0.5,
        "method": "heuristic"
    }

def classify_intent_llm(text: str) -> dict:
    """
    LLM-based intent classification for ambiguous cases.
    Returns: {"intent": "chat|email|drive|calendar|meet", "confidence": 0-1, "method": "llm"}
    """
    if not COHERE_API_KEY:
        return classify_intent_heuristic(text)

    prompt = (
        "Classify the user's intent into ONE category: 'chat', 'email', 'drive', 'calendar', or 'meet'.\n"
        "Return ONLY valid JSON: {\"intent\": \"<category>\", \"confidence\": <0-1>}\n\n"
        f"User text: {text}"
    )

    try:
        co = cohere.Client(COHERE_API_KEY)
        response = co.chat(
            model='command-a-03-2025',
            message=prompt,
            max_tokens=100,
            temperature=0.3
        )

        result_text = response.text.strip()

        try:
            result = json.loads(result_text)
            return {
                "intent": result.get("intent", "chat"),
                "confidence": result.get("confidence", 0.5),
                "method": "llm"
            }
        except json.JSONDecodeError:
            return classify_intent_heuristic(text)

    except Exception as e:
        print(f"LLM intent classification failed: {e}")
        return classify_intent_heuristic(text)

def classify_intent(text: str, user_email: str = "") -> dict:
    """
    Main intent classifier: tries heuristic first, falls back to LLM for ambiguous cases.

    Returns:
    {
        "intent": "chat|email|drive|calendar|meet",
        "confidence": 0-1,
        "method": "heuristic|llm"
    }
    """
    result = classify_intent_heuristic(text)

    if result["confidence"] < 0.7:
        result = classify_intent_llm(text)

    log_msg = f"INTENT_CLASSIFIED: '{text[:50]}...' -> {result['intent']} (confidence={result['confidence']:.2f} method={result['method']})"
    if user_email:
        log_execution(user_email, "INTENT_CLASSIFIER", "CLASSIFIED", result)
    else:
        print(log_msg)

    return result
