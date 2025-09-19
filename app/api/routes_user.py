from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Body
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserRead, UserUpdate, UserLogin, Token, PasswordReset, PasswordChange, EmailRequest
from app.schemas.otp import OTPVerify
from app.crud import user as crud_user
from app.crud import otp as crud_otp
from app.core import security, email_utils
from app.api.deps import get_db, get_current_user
from jose import jwt
from datetime import timedelta
from app.crud import user_profile as crud_user_profile
from app.schemas.user_profile import UserProfileCreate , UserProfileRead
from app.schemas.user import UserWithProfileRead
from pydantic import BaseModel


# Custom login form without OAuth2 extra fields
class SimpleLoginForm(BaseModel):
    email: str
    password: str


router = APIRouter()

# Registration (send OTP)
@router.post("/register", response_model=UserWithProfileRead)  # Changed response model
def register_user(user_in: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_user = crud_user.get_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = crud_user.create_user(db, user_in)

    profile = None
    if user_in.profile:
        profile = crud_user_profile.create_profile(db, user.id, user_in.profile)

    otp_obj = crud_otp.create_otp(db, user.email, "activation")
    background_tasks.add_task(email_utils.send_otp_email, user.email, otp_obj.otp_code, "activation")

    # Return user with profile data
    return {**user.__dict__, "profile": profile}

# Resend activation OTP
@router.post("/resend-activation-otp")
def resend_activation_otp(email_req: EmailRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = crud_user.get_by_email(db, email=email_req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="User already activated")
    otp_obj = crud_otp.create_otp(db, user.email, "activation")
    background_tasks.add_task(email_utils.send_otp_email, user.email, otp_obj.otp_code, "activation")
    return {"msg": "Activation OTP resent"}

# Verify activation OTP
@router.post("/activate-otp")
def activate_user_otp(verify_in: OTPVerify, db: Session = Depends(get_db)):
    user = crud_user.get_by_email(db, email=verify_in.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    otp_obj = crud_otp.verify_otp(db, verify_in.email, verify_in.otp_code, "activation")
    if not otp_obj:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    crud_otp.mark_otp_used(db, otp_obj)
    crud_user.set_verified(db, user, True)
    return {"msg": "User activated"}

# Login - Updated to use simple form
@router.post("/login", response_model=Token)
def login_user(login_data: SimpleLoginForm, db: Session = Depends(get_db)):
    user = crud_user.get_by_email(db, email=login_data.email)
    if not user or not crud_user.check_password(user, login_data.password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_verified:
        raise HTTPException(status_code=400, detail="User not activated")
    access_token = security.create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Forgot password (send OTP)
@router.post("/forgot-password")
def forgot_password(email_req: EmailRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = crud_user.get_by_email(db, email=email_req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    otp_obj = crud_otp.create_otp(db, user.email, "reset")
    background_tasks.add_task(email_utils.send_otp_email, user.email, otp_obj.otp_code, "password reset")
    return {"msg": "Password reset OTP sent"}

# Verify reset OTP and set new password
@router.post("/reset-password-otp")
def reset_password_otp(verify_in: OTPVerify, reset_in: PasswordReset, db: Session = Depends(get_db)):
    user = crud_user.get_by_email(db, email=verify_in.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    otp_obj = crud_otp.verify_otp(db, verify_in.email, verify_in.otp_code, "reset")
    if not otp_obj:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    crud_otp.mark_otp_used(db, otp_obj)
    crud_user.set_password(db, user, reset_in.password)
    return {"msg": "Password reset successful"}

# Change password
@router.post("/change-password")
def change_password(change_in: PasswordChange, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if not crud_user.check_password(current_user, change_in.old_password):
        raise HTTPException(status_code=400, detail="Old password incorrect")
    crud_user.set_password(db, current_user, change_in.new_password)
    return {"msg": "Password changed"}

# Get user details
@router.get("/me", response_model=UserWithProfileRead)
def get_me(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    profile = crud_user_profile.get_by_user_id(db, current_user.id)
    return {**current_user.__dict__, "profile": profile}

# Update user details
@router.put("/me", response_model=UserWithProfileRead)  # Changed from UserRead
def update_me(user_in: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = crud_user.update_user(db, current_user, user_in)

    # Fetch profile data to include in response
    profile = crud_user_profile.get_by_user_id(db, user.id)

    # Return user with profile data (same as GET /me)
    return {**user.__dict__, "profile": profile}

@router.delete("/me", status_code=204)
def delete_me(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    crud_user.delete_user(db, current_user)
    return None


@router.post("/verify-access-token")
def verify_access_token(token: str = Body(...), db: Session = Depends(get_db)):
    payload = security.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    email = payload.get("sub")
    user = crud_user.get_by_email(db, email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"valid": True, "user": {"email": user.email, "id": user.id, "is_active": user.is_active, "is_verified": user.is_verified}}

@router.post("/verify-refresh-token")
def verify_refresh_token(token: str = Body(...)):
    # Simulate refresh token verification (in real apps, use a separate refresh token secret/logic)
    payload = security.decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    email = payload.get("sub")
    # Issue a new access token
    new_access_token = security.create_access_token({"sub": email})
    return {"valid": True, "access_token": new_access_token, "token_type": "bearer"}
