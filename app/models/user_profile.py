from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Date
from sqlalchemy.orm import relationship
from app.db.base import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    age = Column(Integer, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    skin_type = Column(String, nullable=True)
    shine_on_face = Column(String, nullable=True)
    skin_sensitivity = Column(String, nullable=True)
    skin_concern = Column(String, nullable=True)  # comma-separated
    skin_care_routine = Column(String, nullable=True)
    skin_goals = Column(String, nullable=True)  # comma-separated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="profile", uselist=False)