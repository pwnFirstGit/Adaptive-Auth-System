# 🔐 Adaptive Authentication System

A production-level backend authentication service with an **intelligent risk engine** that detects suspicious login activity in real time.

Unlike basic login systems, this project combines multiple behavioral signals to assign a **dynamic risk score** on every login attempt — exactly how real fintech and enterprise security systems work.

🌐 **Live API:** [https://adaptive-auth-system.onrender.com/docs](https://adaptive-auth-system.onrender.com/docs)

---

## 🚨 What Makes This Different

Most login systems just check username and password.

This system goes further — it **analyzes behavior**:

|       Signal     |             Example            |   Risk Added   |
|------------------|--------------------------------|----------------|
|    New device    |      First login from iPhone   |     +20        |
|  Location change |    India → Russia in 5 min     |     +40        |
|   Unusual time   | Always logs in at 9AM, now 3AM |     +10        |
|  Failed attempts |10 wrong passwords then success |     +30        |
|    Rate abuse    |   50 attempts in 60 seconds    |     +50        |

**Decision Engine:**

#Score 0–29   → Allow login
#Score 30–99  → Require OTP verification
#Score 100+   → Block login


---

## 🏗️ Architecture

Client Request
      ↓
FastAPI (REST API)
      ↓
Risk Engine ──→ Redis (rate limiting)
      ↓
PostgreSQL (user data, login history, known devices)
      ↓
Response (allow / require_otp / block)

---

## ⚙️ Tech Stack

|        Layer      |    Technology    |
|-------------------|------------------|
| Backend Framework | FastAPI (Python) |
|       Database    | PostgreSQL 15    |
|        Cache      | Redis 7          |
|         ORM       | SQLAlchemy 2.0   |
|  Authentication   | JWT (python-jose)|
|  Password Hashing | bcrypt (passlib) |
|  Data Validation  | Pydantic v2      |
|    Geolocation    | ip-api.com       |
|     Deployment    | Render           |

---

## 📁** Project Structure**


AdaptiveAuthSystem/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── database.py              # PostgreSQL connection
│   ├── models.py                # Database table definitions
│   ├── schemas.py               # Request/Response shapes
│   ├── routers/
│   │   ├── auth.py              # /signup, /login endpoints
│   │   └── user.py              # Protected user endpoints
│   ├── services/
│   │   ├── risk_engine.py       # Core risk scoring logic 🔥
│   │   ├── geo_service.py       # IP geolocation
│   │   └── device_service.py    # Device fingerprinting
│   └── utils/
│       ├── hashing.py           # Password hashing
│       └── jwt.py               # Token management
├── requirements.txt
├── .env
└── docker-compose.yml


---

## 🗄️ Database Schema


users
├── id, email, password_hash, is_active, created_at

login_history  ← powers the risk engine
├── id, user_id, ip_address, location, device
├── login_time, status, risk_score

known_devices
├── id, user_id, device_hash, last_used

failed_attempts
├── id, user_id, ip_address, attempted_at


---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/signup` | Register a new user |
| POST | `/auth/login` | Login + risk analysis |

### Protected Routes (JWT Required)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/user/me` | Get current user profile |
| GET | `/user/me/login-history` | Last 10 logins with risk scores |

---

## 📦 Sample Response

**POST /auth/login**
json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs......",
  "token_type": "bearer",
  "risk_assessment": {
    "user_id": 1,
    "risk_score": 60,
    "action": "require_otp",
    "reasons": [
      "Login from an unrecognized device",
      "Location changed from Imphal, India to Mumbai, India"
    ]
  }
}


---

## 🚀 Run Locally

### Prerequisites
- Python 3.11+
- Docker Desktop

### Steps

**1. Clone the repo**
bash
git clone https://github.com/pwnFirstGit/Adaptive-Auth-System.git
cd Adaptive-Auth-System


**2. Create virtual environment**
bash
python -m venv venv
source venv/bin/activate  # Mac/Linux


**3. Install dependencies**
bash
pip install -r requirements.txt


**4. Set up environment variables**

Create a `.env` file:
env
DATABASE_URL=postgresql://admin:secret@localhost:5432/authdb
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30


**5. Start PostgreSQL and Redis**
bash
docker-compose up -d


**6. Run the server**
bash
uvicorn app.main:app --reload


**7. Open Swagger UI**

http://127.0.0.1:8000/docs


---

## 🔒 Security Features

- Passwords never stored in plain text (bcrypt hashed)
- JWT tokens expire after 30 minutes
- Brute force protection via Redis rate limiting
- Risk scoring blocks suspicious logins automatically
- Device fingerprint stored as MD5 hash
- No sensitive data exposed in API responses

---

## 🧠 How the Risk Engine Works


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


---

## 👨‍💻 Author

**Pawan Kumar Dangi**
- GitHub: [@pwnFirstGit](https://github.com/pwnFirstGit)

---

## 📄 License

MIT License
