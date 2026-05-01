from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, LoginHistory
from app.utils.jwt import verify_access_token
from app.schemas import UserResponse

router = APIRouter(prefix="/user", tags=["User"])

# Tells FastAPI where to expect the token from
oauth2_scheme = HTTPBearer()


# ─────────────────────────────────────────
# Helper — extract current user from token
# ─────────────────────────────────────────
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials  # extracts token from "Bearer <token>"
    payload = verify_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# ─────────────────────────────────────────
# GET /user/me — Protected route
# ─────────────────────────────────────────
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return current logged-in user's profile"""
    return current_user


# ─────────────────────────────────────────
# GET /user/me/login-history — Protected route
# ─────────────────────────────────────────
@router.get("/me/login-history")
def get_login_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return last 10 logins with risk scores for current user"""
    history = (
        db.query(LoginHistory)
        .filter(LoginHistory.user_id == current_user.id)
        .order_by(LoginHistory.login_time.desc())
        .limit(10)
        .all()
    )

    return [
        {
            "ip_address":  h.ip_address,
            "location":    h.location,
            "device":      h.device,
            "login_time":  h.login_time,
            "status":      h.status,
            "risk_score":  h.risk_score
        }
        for h in history
    ]