from fastapi import FastAPI, HTTPException, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from ..user import User
from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"

print("Loading ENV from:", env_path)

load_dotenv(env_path)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

user_model = User()

SECRET_KEY = os.getenv("SECRETKEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRES_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", 60))



def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


class LoginData(BaseModel):
    email: str
    password: str


class RegisterData(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str


@app.post("/login")
def login(data: LoginData, response: Response):
    if user_model.verify_password(data.email, data.password):
        access_token = create_access_token(data={"sub": data.email})

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="lax",   
            secure=False    
        )

        return {"message": "Login succes"}

    raise HTTPException(status_code=401, detail="wrong credentials")


@app.post("/register")
def register(data: RegisterData):
    user = user_model.create_user(
        data.username,
        data.email,
        data.first_name,
        data.last_name,
        data.password
    )
    if user:
        return {"message": "user created"}
    raise HTTPException(status_code=400, detail="user exists or error")


@app.get("/me")
def read_users_me(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not logged in")

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        return {"email": email}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "logged out"}
