from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class RecipeIngredient(BaseModel):
    ingredient_id: str
    ingredient_name: str
    quantity: Optional[str] = None
    unit: Optional[str] = None
    is_optional: bool = False
    preparation: Optional[str] = None

class RecipeDetail(BaseModel):
    recipe_id: str
    title: str
    cuisine: Optional[str] = None
    cook_time_min: Optional[int] = None
    prep_time_min: Optional[int] = None
    total_time_min: Optional[int] = None
    servings: Optional[int] = None
    instructions: Optional[str] = None
    tags: Optional[List[str]] = None
    image_urls: Optional[List[str]] = None
    popularity_views: Optional[int] = 0
    popularity_likes: Optional[int] = 0
    allergens: Optional[List[str]] = None
    # Complete nutrition profile
    nutrition_calories: Optional[float] = None
    nutrition_protein: Optional[float] = None
    nutrition_total_fat: Optional[float] = None
    nutrition_saturated_fat: Optional[float] = None
    nutrition_cholesterol: Optional[float] = None
    nutrition_sodium: Optional[float] = None
    nutrition_total_carbohydrate: Optional[float] = None
    nutrition_dietary_fiber: Optional[float] = None
    nutrition_total_sugars: Optional[float] = None
    nutrition_vitamin_c: Optional[float] = None
    nutrition_calcium: Optional[float] = None
    nutrition_iron: Optional[float] = None
    nutrition_potassium: Optional[float] = None
    # Legacy fields for backward compatibility
    nutrition_fat: Optional[float] = None
    nutrition_carbohydrate: Optional[float] = None
    nutrition_fiber: Optional[float] = None
    nutrition_sugar: Optional[float] = None
    equipment_needed: Optional[List[str]] = None
    alternative_ingredients: Optional[List[str]] = None
    ingredients: Optional[List[RecipeIngredient]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class RecipeSummary(BaseModel):
    recipe_id: str
    title: str
    cuisine: Optional[str] = None
    cook_time_min: Optional[int] = None
    servings: Optional[int] = None
    tags: Optional[List[str]] = None
    image_urls: Optional[List[str]] = None
    popularity_views: Optional[int] = None
    nutrition_calories: Optional[int] = None