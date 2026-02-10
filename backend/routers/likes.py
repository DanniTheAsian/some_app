from fastapi import APIRouter, Depends
from models.likes import LikesRepo

router = APIRouter(prefix="/likes", tags=["Likes"])
repo = LikesRepo()

def get_current_user_id():
    return 1

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
