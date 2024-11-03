# app/routes/ml_routes.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.models.blueprint import BlueprintData
from app.database import get_db
from bson import ObjectId
from app.routes.auth import get_current_user
import requests

# Initialize the FastAPI router
router = APIRouter()

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from PIL import Image
import io
import base64
import datetime

router = APIRouter()

from typing import Optional

class ModBlueprintData(BaseModel):
    name: str
    description: str
    drawing_data: str  # Base64 String image

    

@router.post("/ai/steampunkify")
async def steampunkify(
    data: ModBlueprintData,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    # Convert canvas data to image (assuming data.drawing_data contains a base64 image string)
    # This part will depend on how you store and access your canvas data
    try:
        # Assume data.drawing_data is a base64 string representing the image
        image_data = base64.b64decode(data.drawing_data)
        image = Image.open(io.BytesIO(image_data))
        
        # Save the image to a temporary location or send it directly
        image_path = "temp_image.png"  # Temporary image file path
        image.save(image_path)

        # Post to DeepAI API
        with open(image_path, 'rb') as img_file:
            r = requests.post(
                "https://api.deepai.org/api/image-editor",
                files={
                    'image': img_file,
                    'text': data.description,  # You can adjust this depending on your requirements
                },
                headers={'api-key': '7c6b4347-d8ef-4862-a230-93b9eac85eaf'}
            )

        # Get response
        response_data = r.json()
        print(response_data)
        # Handle the response as needed
        if r.status_code == 200:
            # Assume the returned image URL is in response_data['output_url']
            return JSONResponse(content={"image_url": response_data['output_url']})
        else:
            return JSONResponse(content={"error": response_data.get('message', 'Error processing image')}, status=r.status_code)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status=500)