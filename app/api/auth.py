from fastapi import APIRouter, Depends
from app.schemas.auth import (
    RegisterSchema, 
    LoginSchema, 
    GoogleLoginSchema, 
    RefreshSchema, 
    CompleteProfileSchema, 
    AuthResponse,
    ConsentUpdateSchema
)
from app.services.auth_service import AuthService
from app.core.deps import get_current_user

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

# FIX: Added Depends(get_current_user) so we know WHO is completing the profile
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