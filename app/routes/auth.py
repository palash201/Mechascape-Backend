# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.user import User
from passlib.context import CryptContext
from bson import ObjectId
import jwt
from datetime import datetime, timedelta
from app.database import get_db  # Import your database connection
from fastapi import Request

# Define router
router = APIRouter()

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Secret key and algorithm for JWT
SECRET_KEY = "your_secret_key"  # Replace with your actual secret key
ALGORITHM = "HS256"

async def verify_user(db, username: str, password: str):
    user = await db.users.find_one({"username": username})
    if user and pwd_context.verify(password, user['hashed_password']):
        return user
    return None

async def verify_token(token: str, db):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# Add the get_current_user function
async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return str(user["_id"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@router.post("/auth/signup")
async def signup(username: str, email: str, plain_password: str, db=Depends(get_db)):
    existing_user = await db.users.find_one({"username": username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_email = await db.users.find_one({"email": email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        hashed_password = pwd_context.hash(plain_password)
    
        new_user = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
        }

        result = await db.users.insert_one(new_user)
        return {"message":"Success"}
            
    except Exception as e:
        print(f"Error: {e}")
        return e
    

@router.post("/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = await verify_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token_data = {
        "sub": str(user["_id"]),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    return {"token": token}

@router.get("/auth/me")
async def get_user_profile(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    user: User = await verify_token(token, db)
    return {"username": user["username"], "email": user["email"]}
