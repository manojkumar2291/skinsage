# app/services/llm_proc.py
import requests
from typing import Tuple

from app.core.config import settings

def validate_image_is_dermatological(image_bytes: bytes) -> Tuple[bool, str]:
    """
    Placeholder/light validation function. 
    (Future improvement: Use HuggingFace API here)
    """
    # Placeholder: Always returns True for now
    return True, "Validation skipped (Robustness)"


def call_openrouter_model(messages: list) -> requests.Response:
    """Sends a request to the OpenRouter API."""
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is not set.")

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": settings.MODEL_NAME,
        "messages": messages,
        "temperature": 0.5
    }

    return requests.post(settings.OPENROUTER_URL, headers=headers, json=payload, timeout=settings.OPENROUTER_TIMEOUT)