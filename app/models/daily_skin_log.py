from sqlalchemy import Column, Integer, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime


class DailySkinLog(Base):
    __tablename__ = "daily_skin_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    log_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # All text fields - simple and flexible
    skin_feel = Column(Text, nullable=False)  # "normal", "dry", "oily", etc.
    skin_description = Column(Text, nullable=False)  # "oily", "dry", "combination", etc.
    sleep_hours = Column(Text, nullable=False)  # "0-3", "3-6", "6-9", "9+"
    diet_items = Column(Text)  # "dairy, seafood, meat, snacks"
    water_intake = Column(Text)  # "400ml", "2 bottles", "8 glasses"

    # Relationship
    user = relationship("User", back_populates="daily_skin_logs")