from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class APIStatus(BaseModel):
    status: str = "ok"
    version: Optional[str] = None

class Page(BaseModel):
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class Message(BaseModel):
    message: str