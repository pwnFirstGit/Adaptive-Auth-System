# import redis
# import random
# import os

# r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# def generate_otp() -> str:
#     """Generate a random 6-digit OTP"""
#     return str(random.randint(100000, 999999))

# def save_otp(user_id: int, otp: str):
#     """Save OTP in Redis with 5 minute expiry"""
#     key = f"otp:{user_id}"
#     r.setex(key, 300, otp)  # 300 seconds = 5 minutes

# def verify_otp(user_id: int, otp: str) -> bool:
#     """Check if submitted OTP matches stored OTP"""
#     key = f"otp:{user_id}"
#     stored = r.get(key)
#     if not stored:
#         return False  # expired or never set
#     if stored.decode() == otp:
#         r.delete(key)  # OTP used → delete immediately
#         return True
#     return False

import random
import string
from datetime import datetime, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_otp(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))

def hash_otp(otp: str) -> str:
    return pwd_context.hash(otp)

def verify_otp(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def otp_expiry(minutes: int = 10) -> datetime:
    return datetime.utcnow() + timedelta(minutes=minutes)