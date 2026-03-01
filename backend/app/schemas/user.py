from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    organization_id: Optional[int] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class UserSelfUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None


class UserAdminUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserResponse(UserBase):
    id: int
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