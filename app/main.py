from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app import models
from app.routers import auth, user 

# Creates all tables in DB automatically on startup
models.Base.metadata.create_all(bind=engine)

security = HTTPBearer()

app = FastAPI(
    title="Adaptive Authentication System",
    description="A login system with intelligent risk detection",
    version="1.0.0"
)

# ✅ ADD CORS - Allows frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",      # Your local React frontend
        "http://localhost:3000",      # Alternative local port
        "https://adaptive-auth-frontend.onrender.com",
        "https://adaptive-auth-system.onrender.com"  # Production (if you have a frontend deployed)
    ],
    allow_credentials=True,            # Allow cookies & auth headers
    allow_methods=["*"],               # Allow all HTTP methods (GET, POST, etc)
    allow_headers=["*"],               # Allow all headers
)

app.include_router(auth.router) 
app.include_router(user.router)  

@app.get("/")
def root():
    return {"message": "Adaptive Auth System is running 🚀"}
