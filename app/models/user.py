from pydantic import BaseModel, EmailStr
from bson import ObjectId
from typing import Optional

class User(BaseModel):
    _id: Optional[str] = None  # Optional field for the user ID
    username: str
    email: EmailStr
    hashed_password: str

    class Config:
        # Use this to serialize ObjectId from MongoDB to string
        json_encoders = {ObjectId: str}
 
