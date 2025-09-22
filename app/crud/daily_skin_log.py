from sqlalchemy.orm import Session
from app.models.daily_skin_log import DailySkinLog
from app.schemas.daily_skin_log import DailySkinLogCreate, DailySkinLogUpdate
from datetime import date
from typing import List, Optional


def create_daily_skin_log(db: Session, daily_skin_log: DailySkinLogCreate, user_id: int) -> DailySkinLog:
    # Auto-set log_date to today
    today = date.today()

    db_daily_skin_log = DailySkinLog(
        user_id=user_id,
        log_date=today,  # Auto-generated
        **daily_skin_log.dict()
    )
    db.add(db_daily_skin_log)
    db.commit()
    db.refresh(db_daily_skin_log)
    return db_daily_skin_log


def get_daily_skin_log(db: Session, log_id: int, user_id: int) -> Optional[DailySkinLog]:
    return db.query(DailySkinLog).filter(
        DailySkinLog.id == log_id,
        DailySkinLog.user_id == user_id
    ).first()


def get_daily_skin_logs_by_user(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
) -> List[DailySkinLog]:
    return db.query(DailySkinLog).filter(
        DailySkinLog.user_id == user_id
    ).order_by(DailySkinLog.log_date.desc()).offset(skip).limit(limit).all()


def get_daily_skin_log_by_date(db: Session, user_id: int, log_date: date) -> Optional[DailySkinLog]:
    return db.query(DailySkinLog).filter(
        DailySkinLog.user_id == user_id,
        DailySkinLog.log_date == log_date
    ).first()


def update_daily_skin_log(
        db: Session,
        log_id: int,
        user_id: int,
        daily_skin_log_update: DailySkinLogUpdate
) -> Optional[DailySkinLog]:
    db_daily_skin_log = get_daily_skin_log(db, log_id, user_id)
    if not db_daily_skin_log:
        return None

    update_data = daily_skin_log_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_daily_skin_log, field, value)

    db.commit()
    db.refresh(db_daily_skin_log)
    return db_daily_skin_log


def delete_daily_skin_log(db: Session, log_id: int, user_id: int) -> bool:
    db_daily_skin_log = get_daily_skin_log(db, log_id, user_id)
    if not db_daily_skin_log:
        return False

    db.delete(db_daily_skin_log)
    db.commit()
    return True