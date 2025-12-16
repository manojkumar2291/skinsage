# app/services/llm_proc.py
import requests
from typing import Tuple

from app.core.config import settings


HF_MODEL_URL = "https://router.huggingface.co/hf-inference/models/google/vit-base-patch16-224"

def validate_image_is_dermatological(image_bytes: bytes) -> Tuple[bool, str]:
    """
    Validates if an image appears to be dermatological/skin-related using HuggingFace API.
    
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    
    api_key = getattr(settings, "HUGGINGFACE_API_KEY", None)
    if not api_key:
        
        return True, "Validation skipped: No API Key"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/octet-stream"
    }

    try:
        response = requests.post(HF_MODEL_URL, headers=headers, data=image_bytes)
        
        if response.status_code != 200:
            print(f"HF API Error: {response.status_code}")
            return True, "Validation skipped (Service unavailable)"

        predictions = response.json()
        print(f"HF Predictions: {predictions}")
        
        
        skin_keywords = [
            # Direct anatomy
            "skin", "face", "cheek", "neck", "arm", "hand", "leg", "foot", "toe",
            "chest", "back", "flesh", "ear", "nose", "mouth", "lip", "head", "muzzle",
            
            # Hair & Scalp (Dermatology includes hair/scalp conditions)
            "hair", "scalp", "wig", "coiffure", "barbershop", "comb", "brush", "braid",
            
            # Medical terms
            "wound", "bandage", "band-aid", "medical", "patient", "doctor", 
            "nurse", "hospital", "pill", "syringe",
            
            # Common misclassifications for Rashes/Skin conditions in ViT:
            "nematode", "parasite", "tick", "insect", # Often confused with spots
            "velvet", "silk", "wool", # Skin texture often confuses model
            "petri", "dish", "soap", "lotion", "sunscreen",
            
            # Context (Clothing/Bedding often visible in telederm)
            "pajama", "jersey", "shirt", "blouse", "clothing", "sleeve",
            "maillot", "diaper", "sheet", "pillow", "quilt",
            
            # TEXTURE HALLUCINATIONS (Fail-Safe for Hairy Skin):
            # ImageNet models see hair/fur and guess dog breeds. We must allow these 
            # to prevent blocking patients with hairy arms/legs or scalp conditions.
            "terrier", "retriever", "shepherd", "dog", "hound", "setter", "spaniel", 
            "mastiff", "rottweiler", "griffon", "pinscher", "poodle", "collie"
        ]
        if isinstance(predictions, list):
            # FIX: Check top 5 instead of top 3 to be more permissive
            top_predictions = predictions[:5]
            top_labels = [p.get("label", "").lower() for p in top_predictions]
        
            is_dermatological = any(
                keyword in label 
                for label in top_labels 
                for keyword in skin_keywords
            )
            
            if is_dermatological:
                return True, f"Valid content detected: {top_labels[0]}"
            else:
                # Returns False here to trigger the 400 Error in the endpoint
                return False, f"Image rejected. Detected: '{top_labels[0]}'. Please ensure the photo clearly shows skin."

        return True, "Validation passed (Generic)"

    except Exception as e:
        print(f"AI Validation Exception: {e}")
        return True, "Validation skipped (System Error)"


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