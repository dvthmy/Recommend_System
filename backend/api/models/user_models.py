from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserProfile(BaseModel):
    user_id: str
    username: Optional[str] = None
    name: Optional[str] = None
    age: Optional[int] = None
    age_group: Optional[str] = None  # Auto-calculated from age (e.g., "18-30", "30-34")
    gender: Optional[str] = None
    locale: Optional[str] = None
    skill_level: Optional[str] = None
    max_cook_time: Optional[int] = Field(None, ge=1, le=480)
    meal_preferences: Optional[List[str]] = None
    completed_onboarding: Optional[bool] = False  # Track if user completed onboarding
    avatar_url: Optional[str] = None  # User profile avatar image URL
    # Dietary plan fields
    dietary_plan: Optional[str] = None  # "low_carb", "high_protein", "low_fat", "keto", "weight_gain", "weight_loss", or None
    auto_dietary_plan: Optional[bool] = False  # If True, automatically calculate from BMI
    bmi: Optional[float] = None
    weight_kg: Optional[float] = Field(None, ge=1, le=500)
    height_cm: Optional[float] = Field(None, ge=50, le=300)
    activity_level: Optional[str] = None  # "sedentary", "light", "moderate", "active", "very_active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    access_token: Optional[str] = None
    token_type: Optional[str] = None

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=150)
    gender: Optional[str] = None
    locale: Optional[str] = None
    skill_level: Optional[str] = None
    max_cook_time: Optional[int] = Field(None, ge=1, le=480)
    meal_preferences: Optional[List[str]] = None
    completed_onboarding: Optional[bool] = None  # Track if user completed onboarding
    avatar_url: Optional[str] = None  # User profile avatar image URL
    # Dietary plan fields
    dietary_plan: Optional[str] = None  # "low_carb", "high_protein", "low_fat", "keto", "weight_gain", "weight_loss", or None
    auto_dietary_plan: Optional[bool] = None  # If True, automatically calculate from BMI
    weight_kg: Optional[float] = Field(None, ge=1, le=500)
    height_cm: Optional[float] = Field(None, ge=50, le=300)
    activity_level: Optional[str] = None  # "sedentary", "light", "moderate", "active", "very_active"

class SignUpRequest(BaseModel):
    username: str
    name: Optional[str] = None
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

class CuisinePreferencesUpdate(BaseModel):
    """Batch update cuisine preferences (for onboarding or profile edit)"""
    cuisines: List[str] = Field(default=[], description="List of cuisine names. Empty list = No Preferences")

class DietRequest(BaseModel):
    """Single diet to add"""
    diet_name: str

class DietsUpdate(BaseModel):
    """Batch update diets (for onboarding or profile edit)"""
    diets: List[str] = Field(default=[], description="List of diet names. Empty list = No Diet Restrictions")