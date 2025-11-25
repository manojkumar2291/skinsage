from fastapi import HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime
from app.schemas.auth import RegisterSchema, LoginSchema, CompleteProfileSchema, ConsentUpdateSchema
from app.database.mysql_conn import get_db_connection as get_connection
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.config import settings

class AuthService:

    def register(self, data: RegisterSchema):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # Check existing user
        cur.execute("SELECT id FROM users WHERE email=%s", (data.email,))
        if cur.fetchone():
            raise HTTPException(400, "Email already registered")

        hashed = hash_password(data.password)

        # Insert logic
        sql = """
            INSERT INTO users 
            (full_name, email, phone, password_hash, role, dob, gender, language_pref, is_verified)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data.full_name, 
            data.email, 
            data.phone,
            hashed, 
            data.role, 
            data.dob,
            data.gender, 
            data.language_pref, 
            False 
        )

        cur.execute(sql, values)
        conn.commit()
        return {"message": "Account created successfully"}

    def login(self, data: LoginSchema):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM users WHERE email=%s", (data.email,))
        user = cur.fetchone()

        if not user or not verify_password(data.password, user["password_hash"]):
            raise HTTPException(400, "Invalid email or password")

        access = create_access_token({"id": user["id"], "email": user["email"], "role": user["role"]})
        refresh = create_refresh_token({"id": user["id"]})

        cur.execute("UPDATE users SET refresh_token=%s WHERE id=%s", (refresh, user["id"]))
        conn.commit()

        # Helper to check profile completion
        is_complete = all([user.get('phone'), user.get('dob'), user.get('gender')])

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "profile_complete": is_complete,
            "user": user
        }

    def google_login(self, token: str):
        try:
            google_user = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
        except Exception as e:
            print(f"Google Auth Error: {e}")
            raise HTTPException(400, "Invalid Google token")

        email = google_user["email"]
        fullname = google_user.get("name", "Google User")
        google_id = google_user["sub"]

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        profile_complete = False

        if not user:
            # First-time login
            dummy_password = "GOOGLE_USER_NO_PASSWORD"
            
            # Default role is 'patient'
            cur.execute("""
                INSERT INTO users 
                (full_name, email, google_id, password_hash, is_verified, role)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (fullname, email, google_id, dummy_password, True, "patient"))
            
            conn.commit()
            
            # Fetch the new user
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
        else:
            profile_complete = all([
                user.get("phone"),
                user.get("dob"),
                user.get("gender"),
                user.get("language_pref")
            ])

        access = create_access_token({
            "id": user["id"], 
            "email": user["email"], 
            "role": user.get("role", "patient")
        })
        refresh = create_refresh_token({"id": user["id"]})

        cur.execute("UPDATE users SET refresh_token=%s WHERE id=%s", (refresh, user["id"]))
        conn.commit()

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "profile_complete": profile_complete,
            "user": user
        }

    def refresh_tokens(self, refresh_token: str):
        payload = verify_token(refresh_token)
        if not payload:
            raise HTTPException(401, "Invalid or expired refresh token")

        user_id = payload.get("id")
        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT id, refresh_token, email, role FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()

        if not user or user.get("refresh_token") != refresh_token:
            raise HTTPException(401, "Invalid refresh token")

        access = create_access_token({"id": user["id"], "email": user["email"], "role": user.get("role")})
        new_refresh = create_refresh_token({"id": user["id"]})

        cur.execute("UPDATE users SET refresh_token=%s WHERE id=%s", (new_refresh, user["id"]))
        conn.commit()

        return {
            "access_token": access, 
            "refresh_token": new_refresh, 
            "token_type": "bearer",
            "user": user 
        }

    def complete_profile(self, user_id: int, data: CompleteProfileSchema):
        conn = get_connection()
        cur = conn.cursor()

        sql = """
            UPDATE users SET 
                phone=%s,
                dob=%s,
                gender=%s,
                language_pref=%s
            WHERE id=%s
        """
        values = (
            data.phone,
            data.dob,
            data.gender,
            data.language_pref,
            user_id
        )

        cur.execute(sql, values)
        conn.commit()

        return {"message": "Profile completed successfully"}

    def update_consent(self, user_id: int, data: ConsentUpdateSchema):
        conn = get_connection()
        cur = conn.cursor()
        
        # Insert a new consent record
        sql = """
            INSERT INTO consent_type (user_id, consent_type, status, accepted_on)
            VALUES (%s, %s, %s, %s)
        """
        cur.execute(sql, (user_id, data.consent_type, data.status, datetime.now()))
        conn.commit()
            
        return {"message": "Consent updated"}