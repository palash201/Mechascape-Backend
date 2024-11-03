# app/models/user.py
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from typing import Optional, List

class Blueprint(BaseModel):
    id: str
    name: str

class User(BaseModel):
    _id: Optional[str] = None  # Optional field for the user ID
    username: str
    email: EmailStr
    hashed_password: str
    blueprints: List[Blueprint] = []  # List of blueprints associated with the user

    class Config:
        # Use this to serialize ObjectId from MongoDB to string
        json_encoders = {ObjectId: str}
