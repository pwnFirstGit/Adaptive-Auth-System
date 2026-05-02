import redis
import random
import os

r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

def generate_otp() -> str:
    """Generate a random 6-digit OTP"""
    return str(random.randint(100000, 999999))

def save_otp(user_id: int, otp: str):
    """Save OTP in Redis with 5 minute expiry"""
    key = f"otp:{user_id}"
    r.setex(key, 300, otp)  # 300 seconds = 5 minutes

def verify_otp(user_id: int, otp: str) -> bool:
    """Check if submitted OTP matches stored OTP"""
    key = f"otp:{user_id}"
    stored = r.get(key)
    if not stored:
        return False  # expired or never set
    if stored.decode() == otp:
        r.delete(key)  # OTP used → delete immediately
        return True
    return False