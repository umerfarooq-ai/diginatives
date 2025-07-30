from sqlalchemy.orm import Session
from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate

def get_by_user_id(db: Session, user_id: int):
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

def create_profile(db: Session, user_id: int, profile_in: UserProfileCreate):
    profile = UserProfile(user_id=user_id, **profile_in.dict())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def update_profile(db: Session, profile: UserProfile, profile_in: UserProfileUpdate):
    for field, value in profile_in.dict(exclude_unset=True).items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile

def delete_profile(db: Session, profile: UserProfile):
    db.delete(profile)
    db.commit()
    return True