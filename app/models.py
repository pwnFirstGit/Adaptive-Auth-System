from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.sql import func
from app.database import Base

# ─────────────────────────────────────────
# Table 1: Users
# ─────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())


# ─────────────────────────────────────────
# Table 2: Login History  ← CORE of risk engine
# ─────────────────────────────────────────
class LoginHistory(Base):
    __tablename__ = "login_history"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, index=True, nullable=False)
    ip_address  = Column(String, nullable=True)
    location    = Column(String, nullable=True)   # e.g. "India"
    device      = Column(String, nullable=True)   # e.g. "chrome_windows"
    login_time  = Column(DateTime(timezone=True), server_default=func.now())
    status      = Column(String, default="success")  # success / failed
    risk_score  = Column(Float, default=0.0)


# ─────────────────────────────────────────
# Table 3: Known Devices
# ─────────────────────────────────────────
class KnownDevice(Base):
    __tablename__ = "known_devices"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, index=True, nullable=False)
    device_hash = Column(String, nullable=False)  # hashed fingerprint
    last_used   = Column(DateTime(timezone=True), server_default=func.now())


# ─────────────────────────────────────────
# Table 4: Failed Attempts
# ─────────────────────────────────────────
class FailedAttempt(Base):
    __tablename__ = "failed_attempts"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, index=True, nullable=True)  # nullable if user doesn't exist
    ip_address = Column(String, nullable=False)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())