from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.db.base import Base
from datetime import datetime, timedelta

class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    otp_code = Column(String, nullable=False)
    purpose = Column(String, nullable=False)  # 'activation' or 'reset'
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False) 