from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate, UserProfileRead
from app.crud import user_profile as crud_user_profile
from app.api.deps import get_db, get_current_user

router = APIRouter()

@router.post("/profile", response_model=UserProfileRead)
def create_profile(profile_in: UserProfileCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    existing = crud_user_profile.get_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")
    profile = crud_user_profile.create_profile(db, current_user.id, profile_in)
    return profile

@router.get("/profile", response_model=UserProfileRead)
def get_profile(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    profile = crud_user_profile.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/profile", response_model=UserProfileRead)
def update_profile(profile_in: UserProfileUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    profile = crud_user_profile.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    updated = crud_user_profile.update_profile(db, profile, profile_in)
    return updated

@router.delete("/profile", status_code=204)
def delete_profile(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    profile = crud_user_profile.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    crud_user_profile.delete_profile(db, profile)
    return