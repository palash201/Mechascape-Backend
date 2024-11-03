# app/routes/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.models.user import User
from passlib.context import CryptContext
from bson import ObjectId
import jwt
from datetime import datetime, timedelta
from app.database import get_db  # Import your database connection
from pydantic import BaseModel

# Define router
router = APIRouter()

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Secret key and algorithm for JWT
SECRET_KEY = "fa131bef7d0e429070a6dd313581efd2c133879dcca748509fc3b2e3f97a4bb62ff3cca1ce23dc027ed1cd3cb45ee4e6a31814528e0284e1c107d2595d3cede1b2948b915a8d25dc0a69ace0bb42fe9d38c7d29f8bb7311975e5e6b50ba5b22b50b66bdd2de9dae0157008ddcd0e8ddf34723a5e3ba56b9234fb16c46f024bec997e300aea0424a19f3b2248cea893ae900c00c838cd72a7e3db58c8ed0698c177f65ad0a4859306456f64871202612c7767ca346321cf62b2646ea3be4e6bd6d697e8142d75372fe8e1629c7a0a11b0748b2c50f468139575fdd9226d27fbe37e3f8664c334bb6a527f9bfb87424d5d6ae5f8f716bd5f9ee7578d1e60762909"  # Replace with your actual secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRATION = timedelta(hours=1)  # Access token expiration time
REFRESH_TOKEN_EXPIRATION = timedelta(days=7)  # Refresh token expiration time

async def verify_user(db, username: str, password: str):
    user = db.users.find_one({"username": username})
    if user and pwd_context.verify(password, user['hashed_password']):
        return user
    return None

async def verify_token(token: str, db):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

async def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return str(user["_id"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
class SignupData(BaseModel):
    username: str
    email: str
    password: str

@router.post("/auth/signup")
async def signup(signupData: SignupData, db=Depends(get_db)):
    existing_user = db.users.find_one({"username": signupData.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_email = db.users.find_one({"email": signupData.email})
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        hashed_password = pwd_context.hash(signupData.password)
    
        new_user = {
            "username": signupData.username,
            "email": signupData.email,
            "hashed_password": hashed_password,
        }

        result = db.users.insert_one(new_user)
        return {"message": "Success"}
            
    except Exception as e:
        print(f"Error: {e}")
        return e

class LoginData(BaseModel):
    username: str
    password: str

@router.post("/auth/login")
async def login(logindata: LoginData, db=Depends(get_db)):
    user: User = await verify_user(db, logindata.username, logindata.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token_data = {
        "sub": str(user['_id']),
        "exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRATION,  # Set access token expiration
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm='HS256')
    
    refresh_token_data = {
        "sub": str(user['_id']),
        "exp": datetime.utcnow() + REFRESH_TOKEN_EXPIRATION,  # Set refresh token expiration
    }
    refresh_token = jwt.encode(refresh_token_data, SECRET_KEY, algorithm='HS256')

    return {"access_token": token, "refresh_token": refresh_token}

@router.post("/auth/refresh")
async def refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Generate a new access token
        new_token_data = {
            "sub": user_id,
            "exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRATION,  # Set new access token expiration
        }
        new_token = jwt.encode(new_token_data, SECRET_KEY, algorithm='HS256')

        return {"token": new_token}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@router.get("/auth/me")
async def get_user_profile(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    user: User = await verify_token(token, db)
    return {"username": user["username"], "email": user["email"]}

@router.get("/user/data")
async def get_user_data(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    user: User = await verify_token(token, db)
    
    # Create a response excluding the hashed password
    user_data = {
        "username": user["username"],
        "email": user["email"],
        "blueprints": user.get("blueprints", []),  # Include blueprints if available
    }
    
    return user_data
