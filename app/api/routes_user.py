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

router = APIRouter()

# Registration (send OTP)
@router.post("/register", response_model=UserRead)
def register_user(user_in: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_user = crud_user.get_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud_user.create_user(db, user_in)
    otp_obj = crud_otp.create_otp(db, user.email, "activation")
    background_tasks.add_task(email_utils.send_otp_email, user.email, otp_obj.otp_code, "activation")
    return user

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

# Login
@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud_user.get_by_email(db, email=form_data.username)
    if not user or not crud_user.check_password(user, form_data.password):
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
@router.get("/me", response_model=UserRead)
def get_me(current_user=Depends(get_current_user)):
    return current_user

# Update user details
@router.put("/me", response_model=UserRead)
def update_me(user_in: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = crud_user.update_user(db, current_user, user_in)
    return user

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