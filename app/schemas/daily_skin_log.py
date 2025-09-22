from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class DailySkinLogBase(BaseModel):
    # Remove log_date from user input - it will be auto-generated
    skin_feel: str
    skin_description: str
    sleep_hours: str
    diet_items: Optional[str] = None
    water_intake: Optional[str] = None

class DailySkinLogCreate(DailySkinLogBase):
    pass

class DailySkinLogUpdate(BaseModel):
    skin_feel: Optional[str] = None
    skin_description: Optional[str] = None
    sleep_hours: Optional[str] = None
    diet_items: Optional[str] = None
    water_intake: Optional[str] = None

class DailySkinLogRead(DailySkinLogBase):
    id: int
    user_id: int
    log_date: date  # This will be auto-generated
    created_at: datetime

    class Config:
        from_attributes = True

class DailySkinLogResponse(BaseModel):
    success: bool
    data: DailySkinLogRead