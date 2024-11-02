# app/connect_to_db.py
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import FastAPI

MONGODB_URL = "your_mongodb_atlas_connection_string"  # Replace with your actual MongoDB connection string
DB_NAME = "mechascape_db"  # Replace with your actual database name

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DB_NAME]

async def connect_to_db():
    # This function is called at startup
    # You can perform any setup tasks here if needed
    print("Connected to MongoDB!")

async def close_db_connection():
    # This function is called at shutdown
    client.close()
    print("MongoDB connection closed.")
