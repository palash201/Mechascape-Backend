from fastapi import APIRouter, Depends
from app.database import get_db
from bson import ObjectId
from app.routes.auth import get_current_user
from app.models.blueprint import BlueprintData  # Import the model


router = APIRouter()

@router.get("/blueprint/count")
async def count_blueprints(user_id: str = Depends(get_current_user)):
    count = await db.blueprints.count_documents({"owner_id": ObjectId(user_id)})
    return {"count": count}

@router.get("/blueprint/recent")
async def get_recent_blueprints(user_id: str = Depends(get_current_user)):
    recent_blueprints = await db.blueprints.find({"owner_id": ObjectId(user_id)}).sort("created_at", -1).limit(5).to_list(5)
    return [{"id": str(bp["_id"]), "name": bp["name"]} for bp in recent_blueprints]

@router.post("/blueprint")
async def create_blueprint(data: BlueprintData):  # Replace with your actual data model
    # Implement logic for creating a blueprint
    return {"blueprint_id": "generated_id"}