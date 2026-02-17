from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timedelta
from models.user import UserRepository
from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(env_path)

router = APIRouter(tags=["Auth"])

user_model = UserRepository()

SECRET_KEY = os.getenv("SECRETKEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRES_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", 60))

security = HTTPBearer()


def create_access_token(data: dict):
    if not SECRET_KEY:
        raise ValueError("SECRETKEY environment variable is not set")
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


class LoginData(BaseModel):
    identifier: str | None = None
    email: str | None = None
    password: str


class RegisterData(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str


@router.post("/login")
def login(data: LoginData):

    ident = data.identifier or data.email

    if not ident:
        raise HTTPException(status_code=400, detail="Missing login field")

    user = user_model.get_by_email(ident)

    if not user:
        user = user_model.get_by_username(ident)

    if user and user_model.verify_password(user, data.password):

        access_token = create_access_token(
            data={"sub": str(user.id)}
        )

        return {
            "access_token": access_token
        }

    raise HTTPException(status_code=401, detail="Wrong credentials")

@router.post("/register")
def register(data: RegisterData):
    user = user_model.create_user(
        data.username,
        data.email,
        data.first_name,
        data.last_name,
        data.password
    )
    if user:
        return {"message": "User created"}
    raise HTTPException(status_code=400)


@router.get("/me")
def read_users_me(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        user = user_model.get_by_id(user_id)

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username
        }

    except JWTError:
        raise HTTPException(status_code=401)


@router.post("/logout")
def logout():
    return {"message": "Logged out"}



def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        user = user_model.get_by_id(user_id)

        if not user:
            raise HTTPException(status_code=401)

        return user

    except JWTError:
        raise HTTPException(status_code=401)
