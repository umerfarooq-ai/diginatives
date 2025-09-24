from sqlalchemy.orm import Session
from app.models.reminder import Reminder
from app.schemas.reminder import ReminderCreate, ReminderUpdate
from typing import List, Optional


def create_reminder(db: Session, reminder: ReminderCreate, user_id: int) -> Reminder:
    """Create a new reminder"""
    db_reminder = Reminder(
        user_id=user_id,
        name=reminder.name,
        time=reminder.time,
        frequency=reminder.frequency,
        selected_days=reminder.selected_days
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


def get_user_reminders(db: Session, user_id: int) -> List[Reminder]:
    """Get all active reminders for a user"""
    return db.query(Reminder).filter(
        Reminder.user_id == user_id,
        Reminder.is_active == True
    ).order_by(Reminder.time.asc()).all()


def get_reminder_by_id(db: Session, reminder_id: int, user_id: int) -> Optional[Reminder]:
    """Get reminder by ID"""
    return db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == user_id
    ).first()


def update_reminder(db: Session, reminder_id: int, user_id: int, reminder_update: ReminderUpdate) -> Optional[Reminder]:
    """Update a reminder"""
    db_reminder = get_reminder_by_id(db, reminder_id, user_id)
    if not db_reminder:
        return None

    update_data = reminder_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_reminder, field, value)

    db.commit()
    db.refresh(db_reminder)
    return db_reminder


def delete_reminder(db: Session, reminder_id: int, user_id: int) -> bool:
    """Delete a reminder"""
    db_reminder = get_reminder_by_id(db, reminder_id, user_id)
    if not db_reminder:
        return False

    db.delete(db_reminder)
    db.commit()
    return True


def toggle_reminder(db: Session, reminder_id: int, user_id: int) -> Optional[Reminder]:
    """Toggle reminder active/inactive"""
    db_reminder = get_reminder_by_id(db, reminder_id, user_id)
    if not db_reminder:
        return None

    db_reminder.is_active = not db_reminder.is_active
    db.commit()
    db.refresh(db_reminder)
    return db_reminder