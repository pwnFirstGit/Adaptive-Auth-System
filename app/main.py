from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from app.database import engine
from app import models
from app.routers import auth,user 

# Creates all tables in DB automatically on startup
models.Base.metadata.create_all(bind=engine)

security = HTTPBearer()

app = FastAPI(
    title="Adaptive Authentication System",
    description="A login system with intelligent risk detection",
    version="1.0.0"
)

app.include_router(auth.router) 
app.include_router(user.router)  

@app.get("/")
def root():
    return {"message": "Adaptive Auth System is running 🚀"}