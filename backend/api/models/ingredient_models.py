from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class IngredientDetail(BaseModel):
    ingredient_id: str
    canonical_name: str
    name: Optional[str] = None
    category: Optional[str] = None
    allergen: Optional[bool] = False
    alternative_names: Optional[List[str]] = None
    description: Optional[str] = None
    nutrition_info: Optional[Dict[str, Any]] = None