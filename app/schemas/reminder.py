from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.reminder import ReminderFrequency

class ReminderCreate(BaseModel):
    name: str
    time: str  # "22:00"
    frequency: ReminderFrequency
    selected_days: Optional[str] = None  # "1,3,5" for weekly or "1,15,30" for monthly

class ReminderUpdate(BaseModel):
    name: Optional[str] = None
    time: Optional[str] = None
    frequency: Optional[ReminderFrequency] = None
    selected_days: Optional[str] = None
    is_active: Optional[bool] = None

class ReminderRead(BaseModel):
    id: int
    user_id: int
    name: str
    time: str
    frequency: ReminderFrequency
    selected_days: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReminderResponse(BaseModel):
    success: bool
    message: str
    data: Optional[ReminderRead] = None

class ReminderListResponse(BaseModel):
    success: bool
    data: List[ReminderRead]
    total: int