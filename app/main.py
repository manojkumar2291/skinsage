from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path



app = FastAPI(
    title="SkinSage API",
    version="1.0",
    description="Unified Backend for Authentication and AI Analysis"
)

# rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Add rate limit exception handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )
from app.api.analysis import router as analysis_router
from app.api.auth import router as auth_router
from app.api.provider import router as provider_router
from app.api.cases import router as case_router
from app.api.appointments import router as appointment_router
from app.api.payment import router as payment_router
# from app.api.notification import router as notification_router
from app.api.visits import router as visits_router
from app.api.videocall import router as videocall_router
from app.api.user import router as user_router
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.remainder_service import send_reminder_emails
from app.api.content import router as content_router
from app.core.config import settings


from app.database import mysql_conn



# mysql_conn.initialize_db()


static_dir = Path("uploads")
static_dir.mkdir(exist_ok=True)

# Global Rate Limiter: Key = Client IP



app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# CORS Configuration

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTENDURL,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Auth Routes 
app.include_router(
    auth_router, 
    prefix="/api/auth", 
    tags=["Authentication"] 
)

# Analysis Routes 
app.include_router(
    analysis_router, 
    prefix="/api/ai", 
    tags=["AI Analysis"]
)

app.include_router(
    user_router,
    prefix="/api",
    tags=["User Management"]
)


# Provider Routes
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
app.include_router(
    payment_router,
    prefix='/api/payment',
    tags=["Payments"]
)
app.include_router(videocall_router, prefix="/api/videocall", tags=["Video Call"]  )
# app.include_router(notification_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(visits_router, prefix="/api/visits", tags=["Visits"])
app.include_router(content_router, prefix="/api/content", tags=["Content Management"] )






scheduler = BackgroundScheduler()
scheduler.add_job(send_reminder_emails, "interval", minutes=30)
scheduler.start()


@app.get("/")
def root():
    return {"message": "SkinSage API is running", "docs_url": "/docs"}