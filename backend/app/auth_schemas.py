"""
Authentication Schemas for City Governance System
Pydantic models for user authentication, registration, and OAuth
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    CITIZEN = "citizen"
    DEPARTMENT_USER = "department_user"
    ADMIN = "admin"


class Department(str, Enum):
    """Department enumeration"""
    WATER = "water"
    FIRE = "fire"
    SANITATION = "sanitation"
    ENGINEERING = "engineering"
    FINANCE = "finance"
    HEALTH = "health"


# ==================== Request Schemas ====================

class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    role: Optional[UserRole] = UserRole.CITIZEN
    department: Optional[Department] = None
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset with token"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class GoogleAuthRequest(BaseModel):
    """Google OAuth authentication request"""
    id_token: str  # Google ID token from frontend


# ==================== Response Schemas ====================

class Token(BaseModel):
    """Authentication token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """User information response"""
    id: int
    email: str
    full_name: str
    role: str
    department: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Complete authentication response"""
    user: UserResponse
    token: Token
    message: str = "Authentication successful"


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True


# ==================== Internal Models ====================

class User(BaseModel):
    """User model (database representation)"""
    id: int
    email: str
    password_hash: Optional[str]
    full_name: str
    role: str
    department: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


class Session(BaseModel):
    """Session model"""
    id: int
    user_id: int
    token: str
    refresh_token: Optional[str]
    expires_at: datetime
    created_at: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    
    class Config:
        from_attributes = True


class OAuthToken(BaseModel):
    """OAuth token model"""
    id: int
    user_id: int
    provider: str
    provider_user_id: str
    access_token: Optional[str]
    refresh_token: Optional[str]
    token_expiry: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
