import hashlib
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..models.user_models import SignUpRequest, SignInRequest, UserProfile, TokenResponse, TokenVerifyResponse
from ..db import get_session
from ..utils.jwt import create_access_token, verify_token, get_user_id_from_token, refresh_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

def hash_password(password: str) -> str:
    """Simple password hashing using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def calculate_age_group(age: int) -> str:
    """Calculate age_group from age number"""
    if age < 18:
        return "<18"
    elif 18 <= age <= 30:
        return "18-30"
    elif 31 <= age <= 34:
        return "30-34"
    elif 35 <= age <= 44:
        return "35-44"
    elif 45 <= age <= 54:
        return "45-54"
    else:  # age >= 55
        return "55+"

@router.post("/signup", response_model=UserProfile)
async def signup(request: SignUpRequest):
    """Sign up a new user with username, password, age, and gender"""
    now = datetime.now().isoformat()
    uid = f"user_{uuid.uuid4().hex[:8]}"
    password_hash = hash_password(request.password)
    
    # Check if username already exists
    check_q = """
    MATCH (u:User {username: $username})
    RETURN u.user_id AS user_id
    """
    
    with get_session() as s:
        existing = s.run(check_q, username=request.username).single()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Calculate age_group from age
        age_group = calculate_age_group(request.age) if request.age else None
        
        # Create new user
        create_q = """
        CREATE (u:User {
            user_id: $uid,
            username: $username,
            name: $name,
            password_hash: $password_hash,
            age: $age,
            age_group: $age_group,
            gender: $gender,
            locale: $locale,
            skill_level: $skill_level,
            max_cook_time: $max_time,
            meal_preferences: $dp,
            completed_onboarding: $completed_onboarding,
            created_at: $now,
            updated_at: $now
        })
        RETURN u.user_id AS user_id, u.username AS username, u.name AS name, u.age AS age, 
               u.age_group AS age_group, u.gender AS gender, u.locale AS locale, u.skill_level AS skill_level,
               u.max_cook_time AS max_cook_time, u.meal_preferences AS meal_preferences,
               u.completed_onboarding AS completed_onboarding,
               u.created_at AS created_at, u.updated_at AS updated_at
        """
        
        rec = s.run(
            create_q,
            uid=uid,
            username=request.username,
            name=request.name,
            password_hash=password_hash,
            age=request.age,
            age_group=age_group,
            gender=request.gender,
            locale="vi-VN",
            skill_level="beginner",
            completed_onboarding=False,
            max_time=60,
            dp=[],
            now=now
        ).single()
        
        if not rec:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        # Create BELONGS_TO relationship if gender and age_group are available
        if request.gender and age_group:
            s.run("""
                MATCH (u:User {user_id: $uid})
                MERGE (g:Group {gender: $gender, age_group: $age_group})
                MERGE (u)-[:BELONGS_TO]->(g)
            """, uid=uid, gender=request.gender, age_group=age_group)
        
        user_data = dict(rec)
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user_data["user_id"]})
        
        # Return user data with token
        return {
            **user_data,
            "access_token": access_token,
            "token_type": "bearer"
        }

@router.post("/signin", response_model=UserProfile)
async def signin(request: SignInRequest):
    """Sign in with username and password"""
    password_hash = hash_password(request.password)
    
    q = """
    MATCH (u:User {username: $username, password_hash: $password_hash})
    RETURN u.user_id AS user_id, u.username AS username, u.name AS name, u.age AS age,
           u.age_group AS age_group, u.gender AS gender, u.locale AS locale, u.skill_level AS skill_level,
           u.max_cook_time AS max_cook_time, u.meal_preferences AS meal_preferences,
           u.completed_onboarding AS completed_onboarding,
           u.created_at AS created_at, u.updated_at AS updated_at
    """
    
    with get_session() as s:
        rec = s.run(q, username=request.username, password_hash=password_hash).single()
        if not rec:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        user_data = dict(rec)
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user_data["user_id"]})
        
        # Return user data with token
        return {
            **user_data,
            "access_token": access_token,
            "token_type": "bearer"
        }

@router.post("/verify", response_model=TokenVerifyResponse)
async def verify_token_endpoint(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """Verify if a JWT token is valid"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload:
        user_id = payload.get("sub")
        if user_id:
            # Verify user exists in database
            q = """
            MATCH (u:User {user_id: $user_id})
            RETURN u.user_id AS user_id
            """
            with get_session() as s:
                rec = s.run(q, user_id=user_id).single()
                if rec:
                    return {
                        "valid": True,
                        "user_id": user_id,
                        "message": "Token is valid"
                    }
        
        return {
            "valid": False,
            "message": "User not found"
        }
    
    return {
        "valid": False,
        "message": "Invalid or expired token"
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token_endpoint(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """Refresh an access token"""
    token = credentials.credentials
    new_token = refresh_access_token(token)
    
    if not new_token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return {
        "access_token": new_token,
        "token_type": "bearer"
    }
