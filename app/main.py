# main.py
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routes import auth, blueprint, ml_routes
from app.database import close_db_connection  # Assuming you have a function to connect to your DB

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # Add specific origins or use ["*"] for all
    allow_credentials=True,
    allow_methods=['*'],  # Allows all HTTP methods
    allow_headers=['*'],  # Allows all headers
)

# Include routers
app.include_router(auth.router)
app.include_router(blueprint.router)
app.include_router(ml_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Mechascape!"}
