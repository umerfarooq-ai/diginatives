from pydantic import BaseModel, EmailStr
from typing import Literal

class OTPCreate(BaseModel):
    email: EmailStr
    purpose: Literal['activation', 'reset']

class OTPVerify(BaseModel):
    email: EmailStr
    otp_code: str
    purpose: Literal['activation', 'reset'] 