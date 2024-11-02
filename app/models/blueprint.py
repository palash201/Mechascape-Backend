from pydantic import BaseModel

class Blueprint(BaseModel):
    id: str
    name: str
    parameters: dict  # Define your blueprint parameters as necessary
