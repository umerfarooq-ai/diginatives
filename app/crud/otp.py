from sqlalchemy.orm import Session
from app.models.otp import OTP
from datetime import datetime, timedelta
import random

def generate_otp():
    return str(random.randint(100000, 999999))

def create_otp(db: Session, email: str, purpose: str, expires_minutes: int = 10):
    otp_code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=expires_minutes)
    otp = OTP(email=email, otp_code=otp_code, purpose=purpose, expires_at=expires_at, is_used=False)
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp

def get_latest_otp(db: Session, email: str, purpose: str):
    return db.query(OTP).filter(OTP.email == email, OTP.purpose == purpose).order_by(OTP.expires_at.desc()).first()

def verify_otp(db: Session, email: str, otp_code: str, purpose: str):
    otp = db.query(OTP).filter(OTP.email == email, OTP.otp_code == otp_code, OTP.purpose == purpose, OTP.is_used == False, OTP.expires_at > datetime.utcnow()).first()
    return otp

def mark_otp_used(db: Session, otp: OTP):
    otp.is_used = True
    db.commit()
    db.refresh(otp)
    return otp 