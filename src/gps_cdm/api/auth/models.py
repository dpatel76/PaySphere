"""
GPS CDM - Auth Models
Pydantic models for authentication and authorization
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# Permission Models
# ============================================================================

class PermissionBase(BaseModel):
    name: str
    description: Optional[str] = None
    resource: str
    action: str


class Permission(PermissionBase):
    permission_id: str

    class Config:
        from_attributes = True


# ============================================================================
# Role Models
# ============================================================================

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class Role(RoleBase):
    role_id: str
    is_system_role: bool = False
    permissions: List[Permission] = []

    class Config:
        from_attributes = True


class RoleCreate(RoleBase):
    permission_ids: List[str] = []


# ============================================================================
# User Models
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role_ids: List[str] = []


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserPasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class User(UserBase):
    user_id: str
    is_active: bool = True
    is_superuser: bool = False
    last_login: Optional[datetime] = None
    created_at: datetime
    roles: List[Role] = []
    permissions: List[str] = []  # Flattened permission names

    class Config:
        from_attributes = True


class UserInDB(User):
    password_hash: str


# ============================================================================
# Authentication Models
# ============================================================================

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


# ============================================================================
# Response Models
# ============================================================================

class UserResponse(BaseModel):
    user_id: str
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_superuser: bool
    roles: List[str]
    permissions: List[str]


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse
