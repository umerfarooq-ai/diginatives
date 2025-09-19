from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db.session import SessionLocal
from app.core.security import decode_access_token
from app.crud.user import get_by_email

# Use HTTPBearer instead of OAuth2PasswordBearer to avoid OAuth2 UI
security = HTTPBearer(auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
        
    try:
        payload = decode_access_token(credentials.credentials)
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
