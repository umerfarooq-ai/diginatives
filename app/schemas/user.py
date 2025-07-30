from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas.user_profile import UserProfileCreate, UserProfileRead


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image: Optional[str] = None

class UserCreate(UserBase):
    password: str
    profile: Optional[UserProfileCreate] = None


class UserRead(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    class Config:
        from_attributes = True

class UserWithProfileRead(UserRead):
    profile: Optional[UserProfileRead] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: int
    hashed_password: str
    is_active: bool
    is_verified: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class PasswordReset(BaseModel):
    password: str

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

class EmailRequest(BaseModel):
    email: EmailStr 