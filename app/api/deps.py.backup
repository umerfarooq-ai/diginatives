from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer
from app.db.session import SessionLocal
from app.core.security import decode_access_token
from app.crud.user import get_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user 