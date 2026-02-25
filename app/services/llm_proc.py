import requests

from transformers import pipeline
from PIL import Image
import io
from typing import Tuple
from app.core.config import settings


print(" Loading AI Model locally... (This happens only once)")
try:
    classifier = pipeline("image-classification", model="google/vit-base-patch16-224")
    print(" AI Model loaded successfully!")
except Exception as e:
    print(f" Failed to load model: {e}")
    classifier = None

def validate_image_is_dermatological(image_bytes: bytes, expected_category: str = "General") -> Tuple[bool, str]:
    """
    Validates image LOCALLY using the loaded Hugging Face model.
    No API calls, no rate limits.
    """
    
    if classifier is None:
        return True, "Validation skipped (Model not loaded)"

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        predictions = classifier(image, top_k=5)
        
        top_labels = [p['label'].lower() for p in predictions]
        # print(f"🔍 Local AI saw: {top_labels} | Expected: {expected_category}")

       
        skin_keywords = [
            "skin", "face", "cheek", "neck", "arm", "hand", "leg", "foot", "toe",
            "chest", "back", "flesh", "ear", "nose", "mouth", "lip", "head",
            "wound", "bandage", "band-aid", "patient", "doctor", "nurse",
            "sunscreen", "lotion", "soap", "bath", "pajama", "jersey", "shirt", 
            "clothing", "mask", "sunglasses", "hat"
        ]

        hair_keywords = [
            "hair", "scalp", "wig", "coiffure", "barbershop", "comb", "brush", "braid",
            "fur", "dog", "terrier", "retriever", "shepherd", "spaniel", "poodle", 
            "head", "face", "bobby pin", "hair slide"
        ]

        if expected_category.lower() == "hair":
            valid_keywords = hair_keywords
        else:
            valid_keywords = skin_keywords

        is_valid = any(
            keyword in label 
            for label in top_labels 
            for keyword in valid_keywords
        )
        
        if is_valid:
            return True, "Valid"
        else:
            detected = ", ".join(top_labels[:2])
            return False, f"Image rejected. Detected: '{detected}'. Please upload a clear photo of the {expected_category} issue."

    except Exception as e:
        print(f"Local Validation Exception: {e}")
        return False , "Validation skipped (Processing Error)"


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
        "temperature": 0.5,
        "max_tokens": 4000
    }

    return requests.post(settings.OPENROUTER_URL, headers=headers, json=payload, timeout=settings.OPENROUTER_TIMEOUT)