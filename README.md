# 🔐 Adaptive Authentication System

A **production-level full-stack authentication service** with an **intelligent risk engine** that detects suspicious login activity in real time — and verifies identity via OTP email when risk is detected.

🌐 **Live Frontend:** [https://adaptive-auth-frontend.onrender.com](https://adaptive-auth-frontend.onrender.com)  
🌐 **Live API:** [https://adaptive-auth-system.onrender.com/docs](https://adaptive-auth-system.onrender.com/docs)  
📦 **GitHub Backend:** [https://github.com/pwnFirstGit/Adaptive-Auth-System](https://github.com/pwnFirstGit/Adaptive-Auth-System)  
📦 **GitHub Frontend:** [https://github.com/pwnFirstGit/adaptive-auth-frontend](https://github.com/pwnFirstGit/adaptive-auth-frontend)

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
Score 0–29   → Allow login directly ✅
Score 30–99  → Send OTP to email → verify before access 📧
Score 100+   → Block login completely ❌
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
          ↓
Dashboard: View login history + risk scores
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT BROWSER                          │
│  (https://adaptive-auth-frontend.onrender.com)             │
│  - React.js + Vite                                         │
│  - Axios for API calls                                     │
│  - Tailwind CSS styling                                    │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND API (FastAPI)                      │
│  (https://adaptive-auth-system.onrender.com)               │
│                                                              │
│  Risk Engine ──→ Redis (rate limiting + OTP storage)       │
│       ↓         ──→ ip-api.com (geolocation)               │
│       ↓         ──→ SendGrid (OTP email delivery)          │
│       ↓                                                      │
│  PostgreSQL (users, login history, devices)                │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend Framework** | React 18 + Vite |
| **Frontend Styling** | Tailwind CSS |
| **HTTP Client** | Axios |
| **Routing** | React Router v6 |
| **Backend Framework** | FastAPI (Python) |
| **Database** | PostgreSQL 15 |
| **Cache** | Redis 7 |
| **ORM** | SQLAlchemy 2.0 |
| **Authentication** | JWT (python-jose) |
| **Password Hashing** | bcrypt (passlib) |
| **Data Validation** | Pydantic v2 |
| **Geolocation** | ip-api.com |
| **Email Delivery** | SendGrid |
| **Frontend Deployment** | Render (Node) |
| **Backend Deployment** | Render (Python) |

---

## 📁 Project Structure

### Backend
```
AdaptiveAuthSystem/
├── app/
│   ├── main.py                   # FastAPI entry point + CORS config
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

### Frontend
```
adaptive-auth-frontend/
├── src/
│   ├── api/
│   │   └── axios.js              # API client with baseURL
│   ├── pages/
│   │   ├── Landing.jsx           # Home page
│   │   ├── Login.jsx             # Login + OTP verification
│   │   ├── Signup.jsx            # User registration
│   │   └── Dashboard.jsx         # User profile + login history
│   ├── App.jsx                   # Routing setup
│   ├── App.css                   # Global styles
│   ├── main.jsx                  # React entry point
│   └── index.css                 # Tailwind CSS
├── public/
├── package.json                  # Dependencies + scripts
├── vite.config.js                # Vite configuration
└── tailwind.config.js            # Tailwind CSS config
```

---

## 🗄️ Database Schema

```
users
├── id (PK), email, password_hash, is_active, created_at

login_history  ← powers the risk engine
├── id (PK), user_id (FK), ip_address, location
├── device, login_time, status, risk_score

known_devices
├── id (PK), user_id (FK), device_hash, last_used

failed_attempts
├── id (PK), user_id (FK), ip_address, attempted_at
```

---

## 🔌 API Endpoints

### Authentication (Public)
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/signup` | Register a new user |
| POST | `/api/auth/login` | Login + run risk engine |
| POST | `/api/auth/verify-otp` | Submit OTP to complete login |

### Protected Routes (JWT Required)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/user/me` | Get current user profile |
| GET | `/api/user/me/login-history` | Last 10 logins with risk scores |

---

## 📦 Sample API Responses

**POST /api/auth/login — Low Risk (allow)**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs......",
  "token_type": "bearer",
  "action": "allow",
  "risk_assessment": {
    "user_id": 1,
    "risk_score": 0,
    "reasons": ["No suspicious activity detected"]
  }
}
```

**POST /api/auth/login — Medium Risk (OTP triggered)**
```json
{
  "action": "require_otp",
  "otp_token": "eyJhbGciOiJIUzI1NiIs......",
  "message": "OTP sent to your registered email"
}
```

**POST /api/auth/verify-otp — Success**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs......",
  "token_type": "bearer",
  "message": "OTP verified. Login successful."
}
```

**GET /api/user/me/login-history — Login History**
```json
[
  {
    "id": 1,
    "login_time": "2026-05-03T20:45:00",
    "ip_address": "203.0.113.45",
    "location": "Imphal, India",
    "device": "Chrome on Windows",
    "risk_score": 0,
    "status": "success"
  }
]
```

---

## 🚀 Run Locally

### Prerequisites
- **Backend:** Python 3.11+, Docker Desktop
- **Frontend:** Node.js 18+, npm/yarn

### Backend Setup

**1. Clone the backend repo**
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

**6. Run the backend server**
```bash
uvicorn app.main:app --reload
```

Backend: http://127.0.0.1:8000  
API Docs: http://127.0.0.1:8000/docs

---

### Frontend Setup

**1. Clone the frontend repo**
```bash
git clone https://github.com/pwnFirstGit/adaptive-auth-frontend.git
cd adaptive-auth-frontend
```

**2. Install dependencies**
```bash
npm install
```

**3. Create environment variables (optional)**

Create `.env.local`:
```env
VITE_API_URL=http://localhost:8000
```

**4. Run development server**
```bash
npm run dev
```

Frontend: http://localhost:5173

**5. Build for production**
```bash
npm run build
npm start
```

---

## 🚀 Deploy to Production

### Backend Deployment (Render)

1. Push to GitHub: `git push`
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Create **New Web Service**
4. Connect your GitHub repo
5. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables in Render settings
7. Deploy! ✅

### Frontend Deployment (Render)

1. Push to GitHub: `git push`
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Create **New Web Service**
4. Connect your GitHub repo
5. Configure:
   - **Environment:** Node
   - **Build Command:** `npm install && npm run build`
   - **Start Command:** `npm start`
   - **Publish directory:** `dist`
6. Add environment variable: `VITE_API_URL=https://your-backend.onrender.com`
7. Deploy! ✅

---

## 🔒 Security Features

- ✅ Passwords never stored in plain text (bcrypt hashed)
- ✅ JWT tokens expire after 30 minutes
- ✅ OTP expires after 5 minutes (stored in Redis)
- ✅ OTP deleted immediately after use
- ✅ Brute force protection via Redis rate limiting
- ✅ Risk scoring blocks suspicious logins automatically
- ✅ Device fingerprint stored as MD5 hash
- ✅ CORS configured to allow only trusted origins
- ✅ No sensitive data exposed in API responses
- ✅ HTTPS enforced in production

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
Calculate Risk Score (0-100+)
        ↓
Decision:
  • 0-29   → Allow login directly
  • 30-99  → Send OTP to email
  • 100+   → Block login
        ↓
Response to Frontend + Login History Updated
```

---

## 📊 Features

### Authentication
- ✅ Sign up with email/password
- ✅ Secure login with risk detection
- ✅ OTP verification for suspicious activity
- ✅ JWT token-based sessions
- ✅ Logout functionality

### Risk Detection
- ✅ IP address tracking
- ✅ Geolocation analysis
- ✅ Device fingerprinting
- ✅ Login time pattern analysis
- ✅ Failed attempt tracking
- ✅ Rate limiting (brute force protection)

### User Dashboard
- ✅ View profile information
- ✅ Login history with risk scores
- ✅ Risk level indicators (🟢 Safe, 🟡 Low, 🟠 Medium, 🔴 High)
- ✅ Device and location information
- ✅ Real-time risk assessment

---

## 🧪 Testing

### Test Accounts

Create a test account:
1. Go to signup page
2. Enter email and password
3. Verify email (or use test email)
4. Login from same location/device = Low risk ✅
5. Login from different location = OTP required 📧

### API Testing

Use Swagger UI at: `https://adaptive-auth-system.onrender.com/docs`

Or use cURL:
```bash
# Sign up
curl -X POST https://adaptive-auth-system.onrender.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Login
curl -X POST https://adaptive-auth-system.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

---

## 📝 Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@host:5432/db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SENDGRID_API_KEY=your-api-key
EMAIL_ADDRESS=noreply@example.com
```

### Frontend (.env.local)
```
VITE_API_URL=https://your-backend-url.onrender.com
```

---

## 🐛 Troubleshooting

### CORS Errors
- Make sure backend's `allow_origins` includes your frontend URL
- Check that both frontend and backend are deployed to the same region

### OTP Not Received
- Check SendGrid API key in backend .env
- Verify email address is SendGrid verified sender

### Login Blocked by Risk Detection
- Try logging in from same location/device as before
- Or wait 5 minutes and try again (rate limit reset)

### Backend Not Responding
- Check Render service is running (may be on free tier and spinning down)
- Visit API docs to wake it up: https://adaptive-auth-system.onrender.com/docs

---

## 📚 Learning Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/)
- [JWT Explained](https://jwt.io/introduction)

---

## 👨‍💻 Author

**Pawan Kumar Dangi**
- GitHub: [@pwnFirstGit](https://github.com/pwnFirstGit)
- Location: Imphal, Manipur, India 🇮🇳

---

## 📄 License

MIT License - Feel free to use this project for learning and development!

---

## 🎉 Status

✅ **FULLY DEPLOYED TO PRODUCTION**
- Frontend: https://adaptive-auth-frontend.onrender.com
- Backend: https://adaptive-auth-system.onrender.com
- Database: PostgreSQL on Render
- Cache: Redis configured
- Email: SendGrid integration active

**Ready for use!** 🚀
