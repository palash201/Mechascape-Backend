# app/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends, FastAPI
from fastapi import Request

# Replace with your actual MongoDB connection string and database name
MONGODB_URL = "your_mongodb_atlas_connection_string"
DB_NAME = "mechascape_db"

# Initialize the MongoDB client
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DB_NAME]

async def get_db(request: Request):
    # Return the database object to the route handlers
    return db

async def close_db_connection():
    # Close the database connection
    client.close()

# In your main FastAPI app file, you need to register the shutdown event
app = FastAPI()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db_connection()
