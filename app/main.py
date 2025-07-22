import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from app.api.routes_user import router as user_router

app = FastAPI()

app.include_router(user_router, prefix="/api", tags=["users"]) 