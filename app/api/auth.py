from fastapi import APIRouter, Depends,HTTPException, BackgroundTasks
from app.schemas.auth import (
    RegisterSchema, 
    LoginSchema, 
    GoogleLoginSchema, 
    RefreshSchema, 
    CompleteProfileSchema, 
    AuthResponse,
    ConsentUpdateSchema,
    OTPGenerateRequest,
    OTPVerifyRequest,
    PasswordResetConfirm,
    PasswordResetRequest

)
import secrets
from datetime import timedelta, datetime
from app.core.security import hash_password, create_access_token, create_refresh_token
from app.services.auth_service import AuthService
from app.core.deps import get_current_user
from app.database.mysql_conn import get_db_connection
from app.utils.email_templetes import otp_verification_template,password_reset_template
from app.services.email_service import send_email_sync
from app.core.config import settings


router = APIRouter(tags=["Authentication"])
service = AuthService()

@router.post("/register")
def register(data: RegisterSchema):
    return service.register(data)

@router.post("/login", response_model=AuthResponse)

def login(data: LoginSchema):
    return service.login(data)

@router.post("/google-login", response_model=AuthResponse)

def google_login(data: GoogleLoginSchema):
    return service.google_login(data.token)

@router.post("/refresh", response_model=AuthResponse)
def refresh_token(payload: RefreshSchema):
    return service.refresh_tokens(payload.refresh_token)

@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/complete-profile")
def complete_profile(
    data: CompleteProfileSchema, 
    current_user: dict = Depends(get_current_user)
):
    return service.complete_profile(user_id=current_user['id'], data=data)

@router.post("/consent")
def consent(
    data: ConsentUpdateSchema,
    current_user: dict = Depends(get_current_user)
):
    return service.update_consent(user_id=current_user['id'], data=data)

@router.post("/otp/generate")
def generate_otp(data: OTPGenerateRequest, background_tasks: BackgroundTasks):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Generate 6-digit code
        otp_code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        expires_at = datetime.now() + timedelta(minutes=10)

        # 2. Store in DB
        cursor.execute("""
            INSERT INTO otps (identifier, code, expires_at) 
            VALUES (%s, %s, %s)
        """, (data.identifier, otp_code, expires_at))
        conn.commit()

        # 3. Send SMS/Email (Mocking it here)
        print(f"DEBUG: OTP for {data.identifier} is {otp_code}")
        otptempletresponse=otp_verification_template(otp_code)

        background_tasks.add_task(send_email_sync, data.identifier,otptempletresponse['subject'], otptempletresponse['body'])
        
        return {"msg": "OTP sent successfully"}
    finally:
        cursor.close()
        conn.close()

@router.post("/otp/verify")
def verify_otp(data: OTPVerifyRequest):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Verify OTP
        cursor.execute("SELECT * FROM otps WHERE identifier=%s AND code=%s AND is_verified=0 AND expires_at > NOW()", (data.identifier, data.code))
        otp_record = cursor.fetchone()
        
        if not otp_record:
            raise HTTPException(400, "Invalid or expired OTP")

        cursor.execute("UPDATE otps SET is_verified=1 WHERE id=%s", (otp_record['id'],))
        
       
        phone_number = data.identifier
        cursor.execute("SELECT * FROM users WHERE phone=%s", (phone_number,))
        user = cursor.fetchone()
        
        
        if not user:
            cursor.execute("""
                INSERT INTO users (phone, password_hash, is_verified, role)
                VALUES (%s, 'OTP_USER_PENDING', 1, 'patient')
            """, (phone_number,))
            conn.commit()
            
            cursor.execute("SELECT * FROM users WHERE phone=%s", (phone_number,))
            user = cursor.fetchone()
        
        # 4. Check Profile Completeness
        # If name or email is missing, force profile completion
        required_fields = [user.get('full_name'), user.get('email'), user.get('dob'), user.get('gender')]
        is_complete = all(field is not None and field != "" for field in required_fields)

        # 5. Generate Tokens
        access = create_access_token({"id": user["id"], "role": "patient"})
        refresh = create_refresh_token({"id": user["id"]})
        
        cursor.execute("UPDATE users SET refresh_token=%s WHERE id=%s", (refresh, user["id"]))
        conn.commit()

        return {
            "access_token": access,
            "refresh_token": refresh,
            "profile_complete": is_complete, # Frontend checks this to redirect
            "user": user
        }

    finally:
        cursor.close()
        conn.close()

        
@router.post("/reset-password")
def reset_password(data: PasswordResetConfirm):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 1. Verify Token
        cursor.execute("""
            SELECT user_id FROM password_resets 
            WHERE token=%s AND used=0 AND expires_at > NOW()
        """, (data.token,))
        record = cursor.fetchone()
        
        if not record:
            raise HTTPException(400, "Invalid or expired token")

        # 2. Update Password
        new_hash = hash_password(data.new_password)
        cursor.execute("UPDATE users SET password_hash=%s WHERE id=%s", (new_hash, record['user_id']))
        
        # 3. Mark token used
        cursor.execute("UPDATE password_resets SET used=1 WHERE token=%s", (data.token,))
        conn.commit()

        return {"msg": "Password updated successfully"}
    finally:
        cursor.close()
        conn.close()
@router.post("/forgot-password")
def forgot_password(
    data: PasswordResetRequest, 
    background_tasks: BackgroundTasks
):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
   
        cursor.execute("SELECT id, full_name FROM users WHERE email=%s", (data.email,))
        user = cursor.fetchone()
        
        if not user:
            return {"msg": "If this email is registered, you will receive a reset link."}

        token = secrets.token_urlsafe(32) 
        expires_at = datetime.now() + timedelta(hours=1) 

        cursor.execute("""
            INSERT INTO password_resets (user_id, token, expires_at, used)
            VALUES (%s, %s, %s, 0)
        """, (user['id'], token, expires_at))
        conn.commit()

        reset_link = f"{settings.FRONTENDURL}/reset-password?token={token}"
        
        print(f"DEBUG: Reset Link for {data.email}: {reset_link}")

        resetPasswordResponse=password_reset_template(user['full_name'],reset_link)
        
        background_tasks.add_task(
            send_email_sync, 
            data.email, 
            resetPasswordResponse['subject'], 
            resetPasswordResponse['body']
        )

        return {"msg": "If this email is registered, you will receive a reset link."}

    except Exception as e:
        print(f"Error in forgot_password: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
    finally:
        cursor.close()
        conn.close()