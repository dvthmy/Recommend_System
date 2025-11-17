from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserProfile(BaseModel):
    user_id: str
    username: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    locale: Optional[str] = None
    skill_level: Optional[str] = None
    max_cook_time: Optional[int] = Field(None, ge=1, le=480)
    dietary_preferences: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = None

class UserProfileUpdate(BaseModel):
    locale: Optional[str] = None
    skill_level: Optional[str] = None
    max_cook_time: Optional[int] = Field(None, ge=1, le=480)
    dietary_preferences: Optional[List[str]] = None

class SignUpRequest(BaseModel):
    username: str
    password: str
    age: int = Field(..., ge=1, le=150)
    gender: str

class SignInRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenVerifyResponse(BaseModel):
    valid: bool
    user_id: Optional[str] = None
    message: Optional[str] = None

class AllergyUpdateRequest(BaseModel):
    ingredient_ids: List[str]

class CuisinePreferenceRequest(BaseModel):
    cuisine_name: str
    preference_level: int = Field(default=5, ge=1, le=10)