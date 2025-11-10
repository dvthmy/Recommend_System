from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserProfile(BaseModel):
    user_id: str
    locale: Optional[str] = None
    skill_level: Optional[str] = None
    max_cook_time: Optional[int] = Field(None, ge=1, le=480)
    dietary_preferences: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserProfileUpdate(BaseModel):
    locale: Optional[str] = None
    skill_level: Optional[str] = None
    max_cook_time: Optional[int] = Field(None, ge=1, le=480)
    dietary_preferences: Optional[List[str]] = None