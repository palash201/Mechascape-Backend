# app/routes/ml_routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models.machine_learning import MLModel

# Initialize the FastAPI router
router = APIRouter()

# Define the request model for predictions
class PredictionRequest(BaseModel):
    text: str

# Instantiate your ML model (make sure to replace 'your-model-name' with the actual model name or path)
ml_model = MLModel("your-model-name-or-path")

@router.post("/predict")
async def make_prediction(request: PredictionRequest):
    try:
        prediction = ml_model.predict(request.text)
        return {"prediction": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/steampunkify")
async def steampunkify():
    pass

# Include this router in your main application
