from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.crud import daily_skin_log as crud_daily_skin_log
from app.schemas.daily_skin_log import (
    DailySkinLogCreate,
    DailySkinLogUpdate,
    DailySkinLogResponse,
    DailySkinLogRead
)
from datetime import date
from typing import List

router = APIRouter()


@router.post("/daily-skin-log", response_model=DailySkinLogResponse)
def create_daily_skin_log(
        daily_skin_log: DailySkinLogCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new daily skin log entry for today"""

    # Check if log already exists for today
    today = date.today()
    existing_log = crud_daily_skin_log.get_daily_skin_log_by_date(
        db, current_user.id, today
    )
    if existing_log:
        raise HTTPException(
            status_code=400,
            detail=f"Daily skin log already exists for today ({today})"
        )

    db_daily_skin_log = crud_daily_skin_log.create_daily_skin_log(
        db, daily_skin_log, current_user.id
    )

    return DailySkinLogResponse(
        success=True,
        data=DailySkinLogRead.from_orm(db_daily_skin_log)
    )


@router.get("/daily-skin-log/{log_id}", response_model=DailySkinLogResponse)
def get_daily_skin_log(
        log_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific daily skin log entry"""

    db_daily_skin_log = crud_daily_skin_log.get_daily_skin_log(db, log_id, current_user.id)
    if not db_daily_skin_log:
        raise HTTPException(status_code=404, detail="Daily skin log not found")

    return DailySkinLogResponse(
        success=True,
        data=DailySkinLogRead.from_orm(db_daily_skin_log)
    )


@router.get("/daily-skin-log/user/{user_id}/history", response_model=List[DailySkinLogRead])
def get_user_daily_skin_logs(
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get user's daily skin log history"""

    # Verify user can access this data
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this data")

    daily_skin_logs = crud_daily_skin_log.get_daily_skin_logs_by_user(
        db, user_id, skip, limit
    )

    return [DailySkinLogRead.from_orm(log) for log in daily_skin_logs]


@router.put("/daily-skin-log/{log_id}", response_model=DailySkinLogResponse)
def update_daily_skin_log(
        log_id: int,
        daily_skin_log_update: DailySkinLogUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update a daily skin log entry"""

    db_daily_skin_log = crud_daily_skin_log.update_daily_skin_log(
        db, log_id, current_user.id, daily_skin_log_update
    )
    if not db_daily_skin_log:
        raise HTTPException(status_code=404, detail="Daily skin log not found")

    return DailySkinLogResponse(
        success=True,
        data=DailySkinLogRead.from_orm(db_daily_skin_log)
    )


@router.delete("/daily-skin-log/{log_id}")
def delete_daily_skin_log(
        log_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete a daily skin log entry"""

    success = crud_daily_skin_log.delete_daily_skin_log(db, log_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Daily skin log not found")

    return {"success": True, "message": "Daily skin log deleted successfully"}


