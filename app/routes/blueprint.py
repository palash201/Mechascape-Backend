# app/routes/blueprint.py
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from bson import ObjectId
from app.routes.auth import get_current_user
from app.models.blueprint import BlueprintData
from pymongo import collection
import datetime

router = APIRouter()

@router.get("/blueprint/count")
async def count_blueprints(user_id: str = Depends(get_current_user), db=Depends(get_db)) -> dict[str, int]:
    """
    Get the count of blueprints for the authenticated user.
    """
    user_object_id = ""
    try:
        user_object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    # Count documents where the owner_id matches the user's ObjectId
    count = db.blueprints.count_documents({"owner_id": user_object_id})
    print(user_object_id)
    print(db.blueprints.count_documents({}))

    return {"count": count}

@router.get("/blueprint/recent")
async def get_recent_blueprints(user_id: str = Depends(get_current_user), db=Depends(get_db)):
    """
    Get the most recent 5 blueprints created by the authenticated user.
    """
    recent_blueprints = (
        db.blueprints.find({"owner_id": ObjectId(user_id)})
        .sort("created_at", -1)
        .limit(5)
        .to_list(5)
    )
    return [
        {"id": str(bp["_id"]), "name": bp["name"], "description": bp.get("description"), "created_at": bp.get("created_at")}
        for bp in recent_blueprints
    ]

@router.post("/blueprint")
async def create_blueprint(data: BlueprintData, user_id: str = Depends(get_current_user), db=Depends(get_db)):
    """
    Create a new blueprint for the authenticated user.
    """
    new_blueprint = {
        "name": data.name,
        "description": data.description,
        "created_at": data.created_at,
        "drawing_data": data.drawing_data,  # Save the canvas drawing data
        "owner_id": ObjectId(user_id)
    }

    result = db.blueprints.insert_one(new_blueprint)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create the blueprint")

    return {"blueprint_id": str(result.inserted_id)}


@router.get("/blueprint/{blueprint_id}")
async def get_blueprint(blueprint_id: str, user_id: str = Depends(get_current_user), db=Depends(get_db)):
    """
    Fetch an existing blueprint by its ID.
    """
    blueprint = db.blueprints.find_one({"_id": ObjectId(blueprint_id), "owner_id": ObjectId(user_id)})
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found")

    blueprint["_id"] = str(blueprint["_id"])  # Convert ObjectId to string for JSON serialization
    blueprint["owner_id"] = str(blueprint["owner_id"])
    return blueprint

@router.post("/blueprint/generate")
async def generate_blueprint(user_id: str = Depends(get_current_user), db=Depends(get_db)):
    """
    Generate a new blueprint for the authenticated user.
    """
    generated_blueprint = {
        "name": "Generated Blueprint",
        "description": "Automatically generated blueprint",
        "created_at": datetime.datetime.utcnow().isoformat(),
        "owner_id": ObjectId(user_id),
        "drawing_data": None # replace with randomly generated canvas json
    }

    result = db.blueprints.insert_one(generated_blueprint)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to generate the blueprint")

    return {"blueprint_id": str(result.inserted_id), "drawing_data": generated_blueprint["drawing_data"]}

@router.put("/blueprint/{blueprint_id}")
async def update_blueprint(
    blueprint_id: str,
    data: BlueprintData,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Update an existing blueprint for the authenticated user.
    """

    query_filter = {"_id": ObjectId(blueprint_id), "owner_id": ObjectId(user_id)}

    # Check if the blueprint exists and belongs to the user
    blueprint = db.blueprints.find_one(query_filter)
    if not blueprint:
        raise HTTPException(status_code=404, detail="Blueprint not found or access denied")

    # Prepare updated data
    updated_blueprint = blueprint
    updated_blueprint["drawing_data"] = data.drawing_data

    update_operation = { '$set' : updated_blueprint }

    # Update the blueprint in the database
    result = db.blueprints.update_one(query_filter, update_operation)

    if result == None:
        print(result)
        print(blueprint_id)
        print(user_id)
        raise HTTPException(status_code=400, detail="Blueprint update failed")

    return {"message": "Blueprint updated successfully", "blueprint_id": blueprint_id}