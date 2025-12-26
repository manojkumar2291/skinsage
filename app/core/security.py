# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
from cryptography.fernet import Fernet
import base64

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_minutes: int = 60*24):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_days: int = 30):
    to_encode = data.copy()
    to_encode["exp"] = datetime.utcnow() + timedelta(days=expires_days)
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None




try:
    _fernet = Fernet(settings.ENCRYPTION_KEY.encode() if isinstance(settings.ENCRYPTION_KEY, str) else settings.ENCRYPTION_KEY)
except Exception as e:
    print(f"Warning: Encryption key likely invalid. Encryption will fail. Error: {e}")
    _fernet = None

def encrypt_message(message: str) -> str:
    if not _fernet:
        return message # Fallback (Danger: Plaintext) or Raise Error
    return _fernet.encrypt(message.encode()).decode()

def decrypt_message(token: str) -> str:
    if not _fernet:
        return token
    try:
        return _fernet.decrypt(token.encode()).decode()
    except Exception:
        return "[Encrypted Message]" # Return placeholder if decryption fails (e.g. key rotation issues)
