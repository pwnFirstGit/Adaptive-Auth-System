import os
import redis
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import LoginHistory, KnownDevice, FailedAttempt
import math

def haversine_distance(lat1, lon1, lat2, lon2) -> float:
    """
    Calculate distance in km between two GPS coordinates
    using the Haversine formula.
    """
    R = 6371  # Earth's radius in km

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c  # distance in km


def check_impossible_travel(
    user_id: int,
    current_lat: float,
    current_lon: float,
    db
) -> tuple[bool, float]:
    """
    Compare current login location with last login.
    Returns (is_impossible, distance_km)
    """
    if current_lat is None or current_lon is None:
        return False, 0

    last_login = (
        db.query(LoginHistory)
        .filter(
            LoginHistory.user_id == user_id,
            LoginHistory.status == "success",
            LoginHistory.latitude != None,
            LoginHistory.longitude != None
        )
        .order_by(LoginHistory.login_time.desc())
        .first()
    )

    if not last_login:
        return False, 0

    # Calculate distance
    distance = haversine_distance(
        last_login.latitude, last_login.longitude,
        current_lat, current_lon
    )

    # Calculate time gap in hours
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    last_time = last_login.login_time
    time_gap_hours = (now - last_time).total_seconds() / 3600

    if time_gap_hours < 0.01:  # less than 36 seconds
        time_gap_hours = 0.01

    # Calculate speed needed
    speed_kmh = distance / time_gap_hours

    # Max commercial plane speed ~900 km/h
    # We use 1000 to give some buffer
    is_impossible = speed_kmh > 1000 and distance > 500

    return is_impossible, distance

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
    latitude: float,
    longitude: float,
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

    # ── Signal 3.5: Impossible Travel ──
    is_impossible, distance = check_impossible_travel(
        user_id, latitude, longitude, db
    )
    if is_impossible:
       risk_score += 80
       reasons.append(
          f"Impossible travel detected — {int(distance)}km gap since last login"
        )

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
