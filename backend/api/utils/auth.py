from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from ..utils.jwt import verify_token, get_user_id_from_token
from ..db import get_session

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """Get current user from JWT token - raises error if no valid token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    user_id = get_user_id_from_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify user exists in database
    q = """
    MATCH (u:User {user_id: $user_id})
    RETURN u.user_id AS user_id
    """
    
    with get_session() as s:
        rec = s.run(q, user_id=user_id).single()
        if not rec:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    return user_id

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """Get current user from JWT token (optional - doesn't raise error if no token)"""
    if not credentials:
        return None
    
    token = credentials.credentials
    user_id = get_user_id_from_token(token)
    return user_id

