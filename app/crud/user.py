from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

def get_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_in: UserCreate):
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_verified=False,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        image=user_in.image
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_user(db: Session, user: User):
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user: User, user_in: UserUpdate):
    if user_in.first_name is not None:
        user.first_name = user_in.first_name
    if user_in.last_name is not None:
        user.last_name = user_in.last_name
    if user_in.image is not None:
        user.image = user_in.image
    db.commit()
    db.refresh(user)
    return user

def set_password(db: Session, user: User, password: str):
    user.hashed_password = get_password_hash(password)
    db.commit()
    db.refresh(user)
    return user

def check_password(user: User, password: str):
    return verify_password(password, user.hashed_password)

def set_active(db: Session, user: User, active: bool):
    user.is_active = active
    db.commit()
    db.refresh(user)
    return user

def set_verified(db: Session, user: User, verified: bool):
    user.is_verified = verified
    db.commit()
    db.refresh(user)
    return user 