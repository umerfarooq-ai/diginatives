from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserProfileBase(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    skin_type: Optional[str] = None
    shine_on_face: Optional[str] = None
    skin_sensitivity: Optional[str] = None
    skin_concern: Optional[str] = None  # comma-separated
    skin_care_routine: Optional[str] = None
    skin_goals: Optional[str] = None  # comma-separated

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileRead(UserProfileBase):
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True