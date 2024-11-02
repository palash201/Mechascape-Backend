# app/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends, FastAPI
from fastapi import Request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Replace with your actual MongoDB connection string and database name
uri = "mongodb+srv://palashk1003:kVe877X8SVR1R3El@cluster0.0fvkl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["mechascape_db"]

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
