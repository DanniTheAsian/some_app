from fastapi import APIRouter, Depends, HTTPException, Cookie
from models.comment import CommentRepo
from pydantic import BaseModel
from jose import jwt, JWTError
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(env_path)

router = APIRouter(prefix="/comments", tags=["Comments"])
repo = CommentRepo()

SECRET_KEY = os.getenv("SECRETKEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

class CommentCreate(BaseModel):
    post_id: int
    content: str

def get_current_user_id(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401, detail="No token")
    
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/")
def create_comment(data: CommentCreate, user_id: int = Depends(get_current_user_id)):
    if not data.content.strip():
        return {"error": "Comment cannot be empty"}
    return repo.create(data.post_id, user_id, data.content)

@router.get("/post/{post_id}")
def get_comments(post_id: int):
    return repo.get_by_post(post_id)
