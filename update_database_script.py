# scripts/reset_and_create_db.py
"""
WARNING: This script will DROP ALL TABLES and recreate them.
Use only in development/testing environments!
"""
from app.db.base import Base
from app.db.session import engine
import app.models.user, app.models.otp, app.models.user_profile, app.models.skin_analysis, app.models.daily_skin_log, app.models.reminder

if __name__ == "__main__":
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Done! Database schema is now up to date with models.")