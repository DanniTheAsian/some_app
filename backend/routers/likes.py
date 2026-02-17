from fastapi import APIRouter, Depends, Cookie, HTTPException
from models.likes import LikesRepo
from jose import jwt, JWTError
import os

router = APIRouter(prefix="/likes", tags=["Likes"])
repo = LikesRepo()


SECRET_KEY = os.getenv("SECRETKEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def get_current_user_id(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=401)

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401)


@router.post("/{post_id}")
def like_post(post_id: int, user_id: int = Depends(get_current_user_id)):
    return repo.like_post(user_id, post_id)

@router.delete("/{post_id}")
def unlike_post(post_id: int, user_id: int = Depends(get_current_user_id)):
    repo.unlike_post(user_id, post_id)
    return {"message": "unliked"}

@router.get("/count/{post_id}")
def get_like_count(post_id: int):
    return {"likes": repo.count_likes(post_id)}
