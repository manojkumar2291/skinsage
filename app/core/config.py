# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

# --- System Prompts ---
ANALYSIS_SYSTEM_PROMPT = (
    "You are a vision-focused dermatological assistant. Your primary task is to analyze the uploaded images. "
    "The user has completed a preliminary symptom questionnaire, which is provided in the conversation history. "
    "Based *only* on the **visual evidence in the images** and the user's *complete history* (initial condition, duration, severity, etc.), provide a thorough, structured final report. "
    "Your report MUST include:\n"
    "1) **Summary of Symptom History** (1-2 sentences based on the text history)\n"
    "2) **Visual Observations** (Detailed description of what you observe *in the images*)\n"
    "3) **Possible Condition/Diagnosis** (Clearly state this is NOT a definitive medical diagnosis)\n"
    "4) **Recommendation** (Whether immediate doctor consultation is recommended (yes/no) with reasoning based on the visual severity)\n"
    "5) **General Care Suggestions** (Brief, appropriate tips)\n"
    "6) **Disclaimer** (A clear disclaimer that this is for informational purposes only and not a replacement for professional medical advice).\n\n"
    "**CRITICAL OUTPUT RULE: Your final line MUST be a single, unambiguous key-value pair indicating medical urgency: Recommendation_Required: [Yes or No]**"
)


class Settings(BaseSettings):
    # Configure Pydantic to look for .env file in the project root
    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'), extra='ignore')

    # LLM Settings
    OPENROUTER_API_KEY: str
    MODEL_NAME: str = "openai/gpt-4o-mini"
    OPENROUTER_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_TIMEOUT: int = 120


   #------------------------ LLM Settings (prod OpenAI Config) -----------------------   
    # OPENAI_API_KEY: str 
    # MODEL_NAME: str = "gpt-4o-mini"
    # OPENAI_URL: str = "https://api.openai.com/v1/chat/completions"
    # OPENAI_TIMEOUT: int = 120


    HUGGINGFACE_API_KEY: str
    HUGGINGFACE_MODEL_URL: str = "https://router.huggingface.co/hf-inference/models/google/vit-base-patch16-224"

    
    DB_HOST: str 
    DB_PORT: str 
    DB_NAME: str 
    DB_USER: str 
    DB_PASSWORD: str  
    SECRET_KEY: str # .env
    GOOGLE_CLIENT_ID: str # .env
    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str

    # email settings
    EMAIL_HOST:str = "webhosting2053.is.cc"
    EMAIL_PORT :int= 465
    EMAIL_USER: str  # .env
    EMAIL_PASS: str  # .env

    AGORA_APP_ID: str  # .env
    AGORA_APP_CERTIFICATE: str  # .env

    FRONTENDURL: str
    ENCRYPTION_KEY: str
    
    MICROSOFT_CLIENT_ID: str = "optional_default" # .env usually
    MICROSOFT_TENANT_ID: str = "common" # .env usually


    AGORA_APP_CERTIFICATE: str  # .env
    AGORA_APP_ID: str  # .env

   


    ANALYSIS_SYSTEM_PROMPT: str = (
        "You are a vision-focused dermatological assistant. Your primary task is to analyze the uploaded images. "
        "The user has completed a preliminary symptom questionnaire, which is provided in the conversation history. "
        "Based *only* on the **visual evidence in the images** and the user's *complete history* (initial condition, duration, severity, etc.), provide a thorough, structured final report. "
        "Your report MUST include:\n"
        "1) **Summary of Symptom History** (1-2 sentences based on the text history)\n"
        "2) **Visual Observations** (Detailed description of what you observe *in the images*)\n"
        "3) **Possible Condition/Diagnosis** (Clearly state this is NOT a definitive medical diagnosis)\n"
        "4) **Recommendation** (Whether immediate doctor consultation is recommended (yes/no) with reasoning based on the visual severity)\n"
        "5) **General Care Suggestions** (Brief, appropriate tips)\n"
        "6) **Disclaimer** (A clear disclaimer that this is for informational purposes only and not a replacement for professional medical advice).\n\n"
        "**CRITICAL OUTPUT RULE: Your final line MUST be a single, unambiguous key-value pair indicating medical urgency: Recommendation_Required: [Yes or No]**"
    )





settings = Settings()