from fastapi import HTTPException, Depends
from google.oauth2 import id_token
from google.auth.transport import requests as google_request
import requests 
import secrets
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
from app.core.deps import get_current_user
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

        provider_id = None
        if user["role"] == "provider":
            cur.execute("SELECT id FROM providers WHERE user_id = %s", (user["id"],))
            provider_record = cur.fetchone()
            if provider_record:
                provider_id = provider_record["id"]

        token_payload = {
            "id": user["id"], 
            "email": user["email"], 
            "role": user["role"],
            "provider_id": provider_id
        }
        access = create_access_token(token_payload)
        refresh = create_refresh_token({"id": user["id"]})

        cur.execute("UPDATE users SET refresh_token=%s WHERE id=%s", (refresh, user["id"]))
        conn.commit()

        
        is_complete = all([user.get('phone'), user.get('dob'), user.get('gender')])

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "profile_complete": is_complete,
            "user": {
                "id": user["id"],
                "provider_id": provider_id, # Included here as requested
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "profile_photo": f"{settings.BACKEND_URL}/{user['profile_photo']}" if user.get('profile_photo') else None,
                "profile_complete": is_complete
            }
        }

    def google_login(self, token: str):
        try:
            google_user = id_token.verify_oauth2_token(
                token,
                google_request.Request(),
                settings.GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=10
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
            # Generate a random, unusable password and hash it
            random_password = secrets.token_urlsafe(32)
            hashed_password = hash_password(random_password)
            
            cur.execute("""
                INSERT INTO users 
                (full_name, email, password_hash, is_verified, role)
                VALUES (%s,%s,%s,%s,%s)
            """, (fullname, email, hashed_password, True, "patient"))
            
            conn.commit()
            
            # Fetch the new user
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
            
            cur.execute("INSERT INTO user_oauth (user_id, provider, provider_id) VALUES (%s, %s, %s)", (user['id'], 'google', google_id))
            conn.commit()
        else:
            cur.execute("SELECT id FROM user_oauth WHERE user_id=%s AND provider='google'", (user['id'],))
            if not cur.fetchone():
                cur.execute("INSERT INTO user_oauth (user_id, provider, provider_id) VALUES (%s, %s, %s)", (user['id'], 'google', google_id))
                conn.commit()
                
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
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "profile_photo": f"{settings.BACKEND_URL}/{user['profile_photo']}" if user.get('profile_photo') else None,
                "profile_complete": profile_complete
            }
        }



    def microsoft_login(self, token: str):
    # ----------------------------------
    # 1. Exchange AUTHORIZATION CODE → ACCESS TOKEN
    # ----------------------------------
        token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

        token_data = {
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "client_secret": settings.MICROSOFT_CLIENT_SECRET,
        "code": token,  # <-- this is your incoming "token" (actually code)
        "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
        "grant_type": "authorization_code",
        "scope": "User.Read"
        }

        try:
            token_resp = requests.post(
                token_url,
                data=token_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            print("Token Exchange Status:", token_resp.status_code)
            print("Token Exchange Response:", token_resp.text)

            if token_resp.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to exchange code: {token_resp.text}"
                )

            token_json = token_resp.json()
            access_token = token_json.get("access_token")

            if not access_token:
                raise HTTPException(400, "No access token received from Microsoft")

        except Exception as e:
            print("Token Exchange Error:", e)
            raise HTTPException(400, "Microsoft token exchange failed")

        # ----------------------------------
        # 2. CALL MICROSOFT GRAPH API
        # ----------------------------------
        graph_url = "https://graph.microsoft.com/v1.0/me"
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            resp = requests.get(graph_url, headers=headers)

            print("Graph Status:", resp.status_code)
            print("Graph Response:", resp.text)

            if resp.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Microsoft token invalid: {resp.text}"
                )

            ms_user = resp.json()

        except Exception as e:
            print(f"Microsoft Auth Error: {e}")
            raise HTTPException(400, "Failed to verify Microsoft token")

        # ----------------------------------
        # 3. EXTRACT USER INFO
        # ----------------------------------
        email = ms_user.get("mail") or ms_user.get("userPrincipalName")
        fullname = ms_user.get("displayName", "Microsoft User")
        ms_id = ms_user.get("id")

        if not email:
            raise HTTPException(400, "Microsoft account verification failed: No email found")

        conn = get_connection()
        cur = conn.cursor(dictionary=True)

        # ----------------------------------
        # 4. CHECK / CREATE USER
        # ----------------------------------
        cur.execute("""
            SELECT u.* FROM users u 
            LEFT JOIN user_oauth o ON u.id = o.user_id 
            WHERE u.email=%s 
            OR (o.provider='microsoft' AND o.provider_id=%s)
        """, (email, ms_id))

        user = cur.fetchone()
        profile_complete = False

        if not user:
            import secrets
            random_password = secrets.token_urlsafe(32)
            hashed_password = hash_password(random_password)

            cur.execute("""
                INSERT INTO users 
                (full_name, email, password_hash, is_verified, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (fullname, email, hashed_password, True, "patient"))

            conn.commit()

            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()

            cur.execute("""
                INSERT INTO user_oauth (user_id, provider, provider_id) 
                VALUES (%s, %s, %s)
            """, (user['id'], 'microsoft', ms_id))

            conn.commit()

        else:
            cur.execute("""
                SELECT id FROM user_oauth 
                WHERE user_id=%s AND provider='microsoft'
            """, (user['id'],))

            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO user_oauth (user_id, provider, provider_id) 
                    VALUES (%s, %s, %s)
                """, (user['id'], 'microsoft', ms_id))
                conn.commit()

            profile_complete = all([
                user.get("phone"),
                user.get("dob"),
                user.get("gender"),
                user.get("language_pref")
            ])

        # ----------------------------------
        # 5. GENERATE YOUR TOKENS
        # ----------------------------------
        access = create_access_token({
            "id": user["id"],
            "email": user["email"],
            "role": user.get("role", "patient")
        })

        refresh = create_refresh_token({"id": user["id"]})

        cur.execute(
            "UPDATE users SET refresh_token=%s WHERE id=%s",
            (refresh, user["id"])
        )
        conn.commit()

        # ----------------------------------
        # 6. RETURN RESPONSE
        # ----------------------------------
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer",
            "profile_complete": profile_complete,
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"],
                "role": user["role"],
                "profile_photo": f"{settings.BACKEND_URL}/{user['profile_photo']}" if user.get('profile_photo') else None,
                "profile_complete": profile_complete
            }
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
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user.get("full_name"), 
                "role": user["role"],
                "profile_photo": f"{settings.BACKEND_URL}/{user['profile_photo']}" if user.get('profile_photo') else None
                # Refresh might not check profile complete, omit or None
            } 
        }

    def complete_profile(self, user_id: int, data: CompleteProfileSchema):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        try:
        #     cur.execute("SELECT id FROM users WHERE phone=%s AND id != %s", (data.phone, user_id))
        #     if cur.fetchone():
        #         raise HTTPException(400, "Phone number is already in use by another account")

            
            cur.execute("""
                UPDATE users 
                SET phone=%s, dob=%s, gender=%s, language_pref=%s
                WHERE id=%s
            """, (
                data.phone, 
                data.dob, 
                data.gender, 
                data.language_pref, 
                user_id 
            ))
            conn.commit()

            return {"msg": "Profile updated successfully", "profile_complete": True}

        finally:
            cur.close()
            conn.close()

    def update_consent(self, user_id: int, data: ConsentUpdateSchema):
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        try:
            # Check if consent already exists
            cur.execute("""
                SELECT id FROM consent_type 
                WHERE user_id=%s AND consent_type=%s
            """, (user_id, data.consent_type.value))
            existing_consent = cur.fetchone()

            if existing_consent:
                # Update existing consent
                cur.execute("""
                    UPDATE consent_type 
                    SET status=%s, accepted_on=NOW()
                    WHERE id=%s
                """, (data.status.value, existing_consent['id']))
            else:
                # Insert new consent
                cur.execute("""
                    INSERT INTO consent_type (user_id, consent_type, status, accepted_on)
                    VALUES (%s, %s, %s, NOW())
                """, (user_id, data.consent_type.value, data.status.value))
            
            conn.commit()
            return {"msg": "Consent updated successfully"}
        finally:
            cur.close()
            conn.close()