# app/models/blueprint.py
from pydantic import BaseModel, Field
from typing import Optional

class BlueprintData(BaseModel):
    name: str
    description: Optional[str] = None
    created_at: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
