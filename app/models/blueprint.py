# app/models/blueprint.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import datetime

class BlueprintData(BaseModel):
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat())
    drawing_data: Dict[str, Any]  # Field to store the raw canvas drawing as a JSON object
