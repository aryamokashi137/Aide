from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)
    role: Optional[UserRole] = UserRole.USER


class UserSelfUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    blood_group: Optional[str] = Field(None, max_length=10)
    emergency_contact_1: Optional[str] = Field(None, max_length=20)
    emergency_contact_2: Optional[str] = Field(None, max_length=20)
    profile_image: Optional[str] = Field(None, max_length=500)
    
    social_instagram: Optional[str] = Field(None, max_length=255)
    social_linkedin: Optional[str] = Field(None, max_length=255)
    social_github: Optional[str] = Field(None, max_length=255)
    
    push_notifications: Optional[bool] = None

class UserUpdate(UserSelfUpdate):
    pass

class UserAdminUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    blood_group: Optional[str] = None
    emergency_contact_1: Optional[str] = None
    emergency_contact_2: Optional[str] = None
    profile_image: Optional[str] = None
    social_instagram: Optional[str] = None
    social_linkedin: Optional[str] = None
    social_github: Optional[str] = None
    push_notifications: bool
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class PaginatedUsers(BaseModel):
    total: int
    items: List[UserResponse]


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)