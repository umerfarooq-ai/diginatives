import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI

# Import all models to ensure relationships are resolved
from app.models import user, user_profile, skin_analysis, otp

from app.api.routes_user import router as user_router
from app.api.routes_user_profile import router as user_profile_router
from app.api.routes_skin_analysis import router as skin_analysis_router
from app.api.routes_daily_skin_log import router as daily_skin_log_router


app = FastAPI()

app.include_router(user_router, prefix="/api", tags=["users"])
app.include_router(user_profile_router, prefix="/api", tags=["user-profile"])
app.include_router(skin_analysis_router, prefix="/api", tags=["skin-analysis"])
app.include_router(daily_skin_log_router, prefix="/api", tags=["daily-skin-log"])
