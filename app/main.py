from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# Import your routers
from app.api.analysis import router as analysis_router
from app.api.auth import router as auth_router
from app.api.provider import router as provider_router
from app.api.cases import router as case_router
from app.api.appointments import router as appointment_router
from app.database import mysql_conn

# 1. Initialize Database (Creates tables if they don't exist)
mysql_conn.initialize_db()

# 2. Initialize Static Directory
static_dir = Path("uploads")
static_dir.mkdir(exist_ok=True)

app = FastAPI(
    title="SkinSage API",
    version="1.0",
    description="Unified Backend for Authentication and AI Analysis"
)

# 3. Mount Static Files (For serving user uploaded images)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# 4. CORS Configuration
origins = [
    "http://localhost:5173",      # React Localhost
    "http://127.0.0.1:5500", # Production Domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Register Routers (The Important Part)

# Auth Routes -> http://localhost:8000/api/auth/login
app.include_router(
    auth_router, 
    prefix="/api/auth", 
    tags=["Authentication"] 
)

# Analysis Routes -> http://localhost:8000/api/v1/analyze
app.include_router(
    analysis_router,  # No need for .router anymore
    prefix="/api/v1", 
    tags=["AI Analysis"]
)

app.include_router(
    provider_router,
    prefix='/api/provider',
    tags=["provider"]
)

app.include_router(
    case_router,
    prefix='/api/case',
    tags=["Cases"]
)
app.include_router(
    appointment_router,
    prefix='/api/appointment'
)

@app.get("/")
def root():
    return {"message": "SkinSage API is running", "docs_url": "/docs"}