# app/core/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.security import verify_token
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database.mysql_conn import get_db_connection
from app.core.config import settings

oauth2_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    token = credentials.credentials

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user_id = payload.get("id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Fetch user
    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    # Profile completeness
    is_complete = all([user.get('phone'), user.get('dob'), user.get('gender')])

    # If user is provider, fetch provider_id
    provider_id = None
    if user.get("role") == "provider":  # adjust if your role field is different
        cur.execute("SELECT id FROM providers WHERE user_id=%s", (user_id,))
        provider = cur.fetchone()
        if provider:
            provider_id = provider.get("id")

    # Cleanup sensitive data
    user.pop("password_hash", None)

    # Fix profile photo URL
    if user.get("profile_photo") and not user["profile_photo"].startswith("http"):
        user["profile_photo"] = f"{settings.BACKEND_URL}/{user['profile_photo']}"

    # Final response
    response = {**user, "profile_complete": is_complete}

    if provider_id:
        response["provider_id"] = provider_id

    return response

    
def role_required(*allowed_roles):
    def wrapper(current_user=Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return current_user
    return wrapper
