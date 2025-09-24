from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.crud import reminder as crud_reminder
from app.schemas.reminder import (
    ReminderCreate, ReminderUpdate, ReminderResponse, ReminderListResponse
)

router = APIRouter()


@router.post("/reminders", response_model=ReminderResponse)
async def create_reminder(
        reminder: ReminderCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Create a new reminder"""
    try:
        db_reminder = crud_reminder.create_reminder(db, reminder, current_user.id)
        return ReminderResponse(
            success=True,
            message="Reminder created successfully",
            data=db_reminder
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create reminder: {str(e)}")


@router.get("/reminders", response_model=ReminderListResponse)
async def get_user_reminders(
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get user's reminders"""
    reminders = crud_reminder.get_user_reminders(db, current_user.id)
    return ReminderListResponse(
        success=True,
        data=reminders,
        total=len(reminders)
    )


@router.get("/reminders/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(
        reminder_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Get a specific reminder"""
    reminder = crud_reminder.get_reminder_by_id(db, reminder_id, current_user.id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    return ReminderResponse(
        success=True,
        message="Reminder retrieved successfully",
        data=reminder
    )


@router.put("/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
        reminder_id: int,
        reminder_update: ReminderUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Update a reminder"""
    db_reminder = crud_reminder.update_reminder(db, reminder_id, current_user.id, reminder_update)
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    return ReminderResponse(
        success=True,
        message="Reminder updated successfully",
        data=db_reminder
    )


@router.post("/reminders/{reminder_id}/toggle", response_model=ReminderResponse)
async def toggle_reminder(
        reminder_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Toggle reminder active/inactive"""
    db_reminder = crud_reminder.toggle_reminder(db, reminder_id, current_user.id)
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    status = "activated" if db_reminder.is_active else "deactivated"
    return ReminderResponse(
        success=True,
        message=f"Reminder {status} successfully",
        data=db_reminder
    )


@router.delete("/reminders/{reminder_id}")
async def delete_reminder(
        reminder_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """Delete a reminder"""
    success = crud_reminder.delete_reminder(db, reminder_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")

    return {"success": True, "message": "Reminder deleted successfully"}