from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RecommendationSessionCreate(BaseModel):
    """Request to create a new recommendation session"""
    user_id: str
    ingredient_ids: Optional[List[str]] = None
    ingredient_names: Optional[List[str]] = None
    preferred_cuisines: Optional[List[str]] = None
    max_cook_time: Optional[int] = None

class RecommendationSessionResponse(BaseModel):
    """Response after creating/querying a session"""
    session_id: str
    user_id: str
    created_at: datetime
    traits: Optional[dict] = None  # Group info
    cuisines: List[str] = []
    ingredients: List[str] = []
    recommended_recipes: List[dict] = []

class SessionGraphResponse(BaseModel):
    """Full graph data for visualization"""
    session_id: str
    nodes: List[dict]  # All nodes (User, Session, Group, Cuisine, Ingredient, Recipe)
    relationships: List[dict]  # All relationships
    cypher_query: str  # Query used to generate this graph

