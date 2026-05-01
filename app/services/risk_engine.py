import os
import redis
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import LoginHistory, KnownDevice, FailedAttempt

# ─────────────────────────────────────────
# Redis connection
# ─────────────────────────────────────────
r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))


# ─────────────────────────────────────────
# Helper — Rate limit check via Redis
# ─────────────────────────────────────────
def check_rate_limit(ip_address: str) -> int:
    """Count login attempts from this IP in last 60 seconds"""
    key = f"login_attempts:{ip_address}"
    attempts = r.incr(key)
    if attempts == 1:
        r.expire(key, 60)  # reset counter after 60 seconds
    return attempts


# ─────────────────────────────────────────
# Helper — Get last login record from DB
# ─────────────────────────────────────────
def get_last_login(user_id: int, db: Session):
    """Fetch most recent successful login for this user"""
    return (
        db.query(LoginHistory)
        .filter(
            LoginHistory.user_id == user_id,
            LoginHistory.status == "success"
        )
        .order_by(LoginHistory.login_time.desc())
        .first()
    )


# ─────────────────────────────────────────
# Helper — Check if device is known
# ─────────────────────────────────────────
def is_known_device(user_id: int, device_hash: str, db: Session) -> bool:
    """Check if this device has been used before by this user"""
    result = db.query(KnownDevice).filter(
        KnownDevice.user_id == user_id,
        KnownDevice.device_hash == device_hash
    ).first()
    return result is not None


# ─────────────────────────────────────────
# Helper — Check unusual login hour
# ─────────────────────────────────────────
def is_unusual_time(user_id: int, db: Session) -> bool:
    """Compare current hour with user's past login hours"""
    current_hour = datetime.utcnow().hour

    past_logins = (
        db.query(LoginHistory)
        .filter(
            LoginHistory.user_id == user_id,
            LoginHistory.status == "success"
        )
        .order_by(LoginHistory.login_time.desc())
        .limit(10)
        .all()
    )

    if not past_logins:
        return False  # no history = can't judge

    # Get hours of past logins
    past_hours = [l.login_time.hour for l in past_logins]
    avg_hour = sum(past_hours) / len(past_hours)

    # If current hour differs by more than 6 hours → unusual
    return abs(current_hour - avg_hour) > 6


# ─────────────────────────────────────────
# Helper — Count recent failed attempts
# ─────────────────────────────────────────
def count_failed_attempts(user_id: int, db: Session) -> int:
    """Count failed login attempts for this user in DB"""
    return (
        db.query(FailedAttempt)
        .filter(FailedAttempt.user_id == user_id)
        .count()
    )


# ─────────────────────────────────────────
# MAIN — Risk Engine
# ─────────────────────────────────────────
def calculate_risk(
    user_id: int,
    ip_address: str,
    device_hash: str,
    location: str,
    db: Session
) -> dict:
    """
    Main risk engine function.
    Returns risk score, action, and reasons.
    """

    risk_score = 0
    reasons = []

    # ── Signal 1: Rate limiting (Redis) ──
    attempts = check_rate_limit(ip_address)
    if attempts > 10:
        risk_score += 50
        reasons.append(f"Too many login attempts from this IP ({attempts} in 60s)")

    # ── Signal 2: New device ──
    if not is_known_device(user_id, device_hash, db):
        risk_score += 20
        reasons.append("Login from an unrecognized device")

    # ── Signal 3: Location change ──
    last_login = get_last_login(user_id, db)
    if last_login and last_login.location != "unknown":
        if last_login.location != location and location != "unknown":
            risk_score += 40
            reasons.append(f"Location changed from {last_login.location} to {location}")

    # ── Signal 4: Unusual login time ──
    if is_unusual_time(user_id, db):
        risk_score += 10
        reasons.append("Login at an unusual time for this user")

    # ── Signal 5: Multiple failed attempts ──
    failed = count_failed_attempts(user_id, db)
    if failed >= 5:
        risk_score += 30
        reasons.append(f"{failed} failed login attempts on record")

    # ── Decision Engine ──
    if risk_score >= 100:
        action = "block"
    elif risk_score >= 70:
        action = "require_otp"
    elif risk_score >= 30:
        action = "require_otp"
    else:
        action = "allow"

    return {
        "user_id": user_id,
        "risk_score": risk_score,
        "action": action,
        "reasons": reasons if reasons else ["No suspicious activity detected"]
    }