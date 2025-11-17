from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from ..config import settings

# JWT Configuration
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_user_id_from_token(token: str) -> Optional[str]:
    """Extract user_id from token"""
    payload = verify_token(token)
    if payload:
        return payload.get("sub")  # 'sub' is standard JWT claim for subject (user_id)
    return None

def refresh_access_token(token: str) -> Optional[str]:
    """Refresh an access token if it's still valid"""
    payload = verify_token(token)
    if payload:
        user_id = payload.get("sub")
        if user_id:
            # Create new token with same user_id
            return create_access_token(data={"sub": user_id})
    return None

