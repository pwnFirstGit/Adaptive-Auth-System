from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.device_service import get_device_info
from app.database import get_db
from app.models import User, LoginHistory, KnownDevice, FailedAttempt
from app.schemas import SignupRequest, LoginRequest, TokenResponse, UserResponse
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.schemas import OTPVerifyRequest

import hashlib

router = APIRouter(prefix="/auth", tags=["Authentication"])




# ─────────────────────────────────────────
# POST /auth/signup
# ─────────────────────────────────────────
@router.post("/signup", response_model=UserResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user"""

    # Check if email already exists
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and save user
    new_user = User(
        email=payload.email,
        password_hash=hash_password(payload.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ─────────────────────────────────────────
# POST /auth/login
# ─────────────────────────────────────────
@router.post("/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Login with email & password — runs risk engine on every attempt"""

    ip_address  = request.client.host
    
    device_info  = get_device_info(request)
    device_hash  = device_info["device_hash"]
    device_label = device_info["device_label"]  # e.g. "Chrome_MacOS"

    from app.services.geo_service import get_location_from_ip
    location = get_location_from_ip(ip_address)

    # Find user
    user = db.query(User).filter(User.email == payload.email).first()

    # Wrong credentials → log failed attempt
    if not user or not verify_password(payload.password, user.password_hash):
        if user:
            db.add(FailedAttempt(user_id=user.id, ip_address=ip_address))
            db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # ── Run Risk Engine ──
    from app.services.risk_engine import calculate_risk
    risk_result = calculate_risk(
        user_id=user.id,
        ip_address=ip_address,
        device_hash=device_hash,
        location=location,
        db=db
    )

    # Block high-risk logins
    if risk_result["action"] == "block":
        raise HTTPException(status_code=403, detail={
            "message": "Login blocked due to suspicious activity",
            "reasons": risk_result["reasons"]
        })
    
    if risk_result["action"]=="require_otp":
        from app.utils.otp import generate_otp, hash_otp, otp_expiry
        from app.services.email_service import send_otp_email
        from app.utils.jwt import create_otp_token
        from app.models import OTPVerification

        raw_otp    = generate_otp()
        otp_token  = create_otp_token(user.id)

        otp_record = OTPVerification(
            user_id    = user.id,
            otp_code   = hash_otp(raw_otp),
            otp_token  = otp_token,
            expires_at = otp_expiry(minutes=10),
        )
        db.add(otp_record)
        db.commit()

        email_sent = send_otp_email(
            to_email = user.email,
            otp      = raw_otp
        )

        if not email_sent:
            raise HTTPException(status_code=500, detail="Failed to send OTP. Try again.")

        return {
            "action"    : "require_otp",
            "otp_token" : otp_token,
            "message"   : "OTP sent to your registered email"
        }

    # Save login history with risk score
    db.add(LoginHistory(
        user_id=user.id,
        ip_address=ip_address,
        location=location,
        device=device_label,
        status="success",
        risk_score=risk_result["risk_score"]
    ))

    # Save device if new
    known = db.query(KnownDevice).filter(
        KnownDevice.user_id == user.id,
        KnownDevice.device_hash == device_hash
    ).first()
    if not known:
        db.add(KnownDevice(user_id=user.id, device_hash=device_hash))

    db.commit()

    # Generate JWT token
    token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "risk_assessment": risk_result
    }


@router.post("/verify-otp")
def verify_otp_endpoint(payload: OTPVerifyRequest, db: Session = Depends(get_db)):
    from app.utils.otp import verify_otp
    from app.utils.jwt import decode_otp_token, create_access_token
    from app.models import OTPVerification
    from datetime import datetime

    # 1. Decode session
    user_id = decode_otp_token(payload.otp_token)

    # 2. Find the matching unused OTP record
    record = (
        db.query(OTPVerification)
        .filter(
            OTPVerification.user_id   == user_id,
            OTPVerification.otp_token == payload.otp_token,
            OTPVerification.is_used   == False,
        )
        .order_by(OTPVerification.created_at.desc())
        .first()
    )

    if not record:
        raise HTTPException(status_code=400, detail="No pending OTP found")

    # 3. Check expiry
    if datetime.utcnow() > record.expires_at:
        raise HTTPException(status_code=400, detail="OTP has expired")

    # 4. Verify code
    if not verify_otp(payload.otp_code, record.otp_code):
        raise HTTPException(status_code=400, detail="Incorrect OTP")

    # 5. Mark used
    record.is_used = True
    db.commit()

    # 6. Issue real access token
    access_token = create_access_token(data={"sub": str(user_id)})
    return {
        "access_token" : access_token,
        "token_type"   : "bearer",
        "message"      : "OTP verified. Login successful."
    }
