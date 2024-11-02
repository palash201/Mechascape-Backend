# main.py
from fastapi import FastAPI
from app.routes import auth, blueprint
from app.database import connect_to_db, close_db_connection  # Assuming you have a function to connect to your DB

app = FastAPI()

# Include routers
app.include_router(auth.router)
app.include_router(blueprint.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Mechascape!"}

# Connect to the database on startup
@app.on_event("startup")
async def startup_event():
    await connect_to_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db_connection()  # Close the database connection when the app shuts down
