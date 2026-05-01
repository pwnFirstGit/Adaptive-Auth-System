
from passlib.context import CryptContext

# bcrypt is the hashing algorithm — industry standard
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Convert raw password → hashed string for DB storage"""
    # bcrypt has 72 byte limit — truncate to be safe
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if entered password matches stored hash"""
    return pwd_context.verify(plain_password[:72], hashed_password)