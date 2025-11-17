from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserInteraction(BaseModel):
    interaction_id: Optional[str] = None
    user_id: str
    recipe_id: str
    event_type: str = Field(..., pattern="^(view|like|rating)$")  
    rating: Optional[int] = Field(None, ge=1, le=5)               
    timestamp: Optional[datetime] = None
