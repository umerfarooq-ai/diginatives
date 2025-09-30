from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.db.base import Base
from sqlalchemy.orm import relationship


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_first_login = Column(Boolean, default=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    image = Column(String, nullable=True)
    device_token = Column(String(255), nullable=True)
    skin_analyses = relationship("SkinAnalysis", back_populates="user")
    daily_skin_logs = relationship("DailySkinLog", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
