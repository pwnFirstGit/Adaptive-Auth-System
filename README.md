# 🔐 Adaptive Authentication System

A production-level backend authentication service with an **intelligent risk engine** that detects suspicious login activity in real time — and verifies identity via OTP email when risk is detected.

🌐 **Live API:** [https://adaptive-auth-system.onrender.com/docs](https://adaptive-auth-system.onrender.com/docs)
📦 **GitHub:** [https://github.com/pwnFirstGit/Adaptive-Auth-System](https://github.com/pwnFirstGit/Adaptive-Auth-System)

---

## 🚨 What Makes This Different

Most login systems just check username and password.

This system goes further — it **analyzes behavior** on every login:

| Signal | Example | Risk Added |
|---|---|---|
| New device | First login from iPhone | +20 |
| Location change | India → Russia in 5 min | +40 |
| Unusual time | Always logs in at 9AM, now 3AM | +10 |
| Failed attempts | 10 wrong passwords then success | +30 |
| Rate abuse | 50 attempts in 60 seconds | +50 |

**Decision Engine:**
```
Score 0–29   → Allow login directly
Score 30–99  → Send OTP to email → verify before access
Score 100+   → Block login completely
```

---

## 🔄 Complete Login Flow

```
User submits email + password
          ↓
Password verified against bcrypt hash
          ↓
Risk Engine collects signals:
  ├── IP address
  ├── Device fingerprint (Browser + OS)
  ├── Geolocation (ip-api.com)
  └── Login time
          ↓
Compare with past behavior (PostgreSQL)
Check rate limit (Redis)
          ↓
Calculate Risk Score
          ↓
   ┌──────────────────────────────┐
   │ Score < 30  → Issue JWT      │
   │ Score 30-99 → Send OTP email │
   │ Score 100+  → Block login    │
   └──────────────────────────────┘
          ↓
If OTP required:
  User receives 6-digit code via email
  Submits to /auth/verify-otp
  On success → Issue JWT token
```

---

## 🏗️ Architecture

```
Client Request
      ↓
FastAPI (REST API)
      ↓
Risk Engine ──→ Redis (rate limiting + OTP storage)
      ↓         ──→ ip-api.com (geolocation)
      ↓         ──→ SendGrid (OTP email delivery)
PostgreSQL (users, login history, known devices)
      ↓
Response (JWT token / OTP required / blocked)
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI (Python) |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| ORM | SQLAlchemy 2.0 |
| Authentication | JWT (python-jose) |
| Password Hashing | bcrypt (passlib) |
| Data Validation | Pydantic v2 |
| Geolocation | ip-api.com |
| Email Delivery | SendGrid |
| Deployment | Render |

---

## 📁 Project Structure

```
AdaptiveAuthSystem/
├── app/
│   ├── main.py                   # FastAPI entry point
│   ├── database.py               # PostgreSQL connection
│   ├── models.py                 # Database table definitions
│   ├── schemas.py                # Request/Response shapes
│   ├── routers/
│   │   ├── auth.py               # /signup, /login, /verify-otp
│   │   └── user.py               # Protected user endpoints
│   ├── services/
│   │   ├── risk_engine.py        # Core risk scoring logic 🔥
│   │   ├── geo_service.py        # IP → location lookup
│   │   ├── device_service.py     # Device fingerprinting
│   │   └── email_service.py      # OTP email via SendGrid
│   └── utils/
│       ├── hashing.py            # bcrypt password hashing
│       ├── jwt.py                # JWT token management
│       └── otp.py                # OTP generate/store/verify
├── requirements.txt
├── .env                          # local secrets (not in git)
├── Procfile                      # Render start command
└── docker-compose.yml            # local PostgreSQL + Redis
```

---

## 🗄️ Database Schema

```
users
├── id, email, password_hash, is_active, created_at

login_history  ← powers the risk engine
├── id, user_id, ip_address, location
├── device, login_time, status, risk_score

known_devices
├── id, user_id, device_hash, last_used

failed_attempts
├── id, user_id, ip_address, attempted_at
```

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/signup` | Register a new user |
| POST | `/auth/login` | Login + run risk engine |
| POST | `/auth/verify-otp` | Submit OTP to complete login |

### Protected Routes (JWT Required)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/user/me` | Get current user profile |
| GET | `/user/me/login-history` | Last 10 logins with risk scores |

---

## 📦 Sample Responses

**POST /auth/login — Low Risk (allow)**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs......",
  "token_type": "bearer",
  "risk_assessment": {
    "user_id": 1,
    "risk_score": 0,
    "action": "allow",
    "reasons": ["No suspicious activity detected"]
  }
}
```

**POST /auth/login — Medium Risk (OTP triggered)**
```json
{
  "action": "require_otp",
  "otp_token": "eyJhbGciOiJIUzI1NiIs......",
  "message": "OTP sent to your registered email"
}
```

**POST /auth/verify-otp — Success**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs......",
  "token_type": "bearer",
  "message": "OTP verified. Login successful."
}
```

---

## 🚀 Run Locally

### Prerequisites
- Python 3.11+
- Docker Desktop

### Steps

**1. Clone the repo**
```bash
git clone https://github.com/pwnFirstGit/Adaptive-Auth-System.git
cd Adaptive-Auth-System
```

**2. Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Create a `.env` file:
```env
DATABASE_URL=postgresql://admin:secret@localhost:5432/authdb
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SENDGRID_API_KEY=your-sendgrid-api-key
EMAIL_ADDRESS=your-verified-sender@gmail.com
```

**5. Start PostgreSQL and Redis**
```bash
docker-compose up -d
```

**6. Run the server**
```bash
uvicorn app.main:app --reload
```

**7. Open Swagger UI**
```
http://127.0.0.1:8000/docs
```

---

## 🔒 Security Features

- Passwords never stored in plain text (bcrypt hashed)
- JWT tokens expire after 30 minutes
- OTP expires after 5 minutes (stored in Redis)
- OTP deleted immediately after use
- Brute force protection via Redis rate limiting
- Risk scoring blocks suspicious logins automatically
- Device fingerprint stored as MD5 hash
- No sensitive data exposed in API responses

---

## 🧠 How the Risk Engine Works

```
Login Request Arrives
        ↓
Collect Signals:
  ├── IP Address
  ├── Device Fingerprint (Browser + OS)
  ├── Geolocation (via ip-api.com)
  └── Login Timestamp
        ↓
Compare With Past Behavior (PostgreSQL):
  ├── Last known location
  ├── Known devices list
  ├── Past login times
  └── Failed attempt history
        ↓
Check Real-time Signals (Redis):
  └── Login attempts in last 60 seconds
        ↓
Calculate Risk Score
        ↓
Decision: Allow / OTP / Block
```

---

## 👨‍💻 Author

**Pawan Kumar Dangi**
- GitHub: [@pwnFirstGit](https://github.com/pwnFirstGit)

---

## 📄 License

MIT License
