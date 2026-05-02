from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# ─────────────────────────────────────────
# Auth Schemas (Signup / Login)
# ─────────────────────────────────────────

class SignupRequest(BaseModel):
    """Data user sends to create an account"""
    email:    EmailStr
    password: str

class LoginRequest(BaseModel):
    """Data user sends to log in"""
    email:    EmailStr
    password: str

class TokenResponse(BaseModel):
    """What we return after successful login"""
    access_token: str
    token_type:   str = "bearer"

# ─────────────────────────────────────────
# Risk Engine Schemas
# ─────────────────────────────────────────

class RiskResponse(BaseModel):
    """Risk engine decision returned to client"""
    user_id:    int
    risk_score: float
    action:     str          # "allow" / "require_otp" / "block"
    reasons:    list[str]    # e.g. ["New device", "Unusual location"]

# ─────────────────────────────────────────
# User Schema (for responses)
# ─────────────────────────────────────────

class UserResponse(BaseModel):
    """Safe user data to return (never expose password_hash)"""
    id:         int
    email:      str
    created_at: datetime

    class Config:
        from_attributes = True  # allows reading from SQLAlchemy model

class OTPVerifyRequest(BaseModel):
    otp_token : str   # returned from /login
    otp_code  : str   # 6-digit code from email