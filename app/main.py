import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI

import asyncio
from app.services.reminder_service import reminder_service
from app.db.session import SessionLocal

# Import all models to ensure relationships are resolved
from app.models import user, user_profile, skin_analysis, otp, daily_skin_log, reminder

from app.api.routes_user import router as user_router
from app.api.routes_user_profile import router as user_profile_router
from app.api.routes_skin_analysis import router as skin_analysis_router
from app.api.routes_daily_skin_log import router as daily_skin_log_router
from app.api.routes_reminder import router as reminder_router




app = FastAPI()

app.include_router(user_router, prefix="/api", tags=["users"])
app.include_router(user_profile_router, prefix="/api", tags=["user-profile"])
app.include_router(skin_analysis_router, prefix="/api", tags=["skin-analysis"])
app.include_router(daily_skin_log_router, prefix="/api", tags=["daily-skin-log"])
app.include_router(reminder_router, prefix="/api", tags=["reminders"])




@app.on_event("startup")
async def startup_event():
    """Start the reminder service when app starts"""
    db = SessionLocal()
    # Start reminder service in background
    asyncio.create_task(reminder_service.start_reminder_checker(db))

@app.on_event("shutdown")
async def shutdown_event():
    """Stop the reminder service when app shuts down"""
    reminder_service.stop()