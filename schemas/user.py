from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str
    district: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str
    email: str
    role: str
    district: Optional[str] = None
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
