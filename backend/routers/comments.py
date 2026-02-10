from fastapi import APIRouter, Depends
from models.comment import CommentRepo
from pydantic import BaseModel

router = APIRouter(prefix="/comments", tags=["Comments"])
repo = CommentRepo()

class CommentCreate(BaseModel):
    post_id: int
    content: str

def get_current_user_id():
    return 1

@router.post("/")
def create_comment(data: CommentCreate, user_id: int = Depends(get_current_user_id)):
    if not data.content.strip():
        return {"error": "Comment cannot be empty"}
    return repo.create(data.post_id, user_id, data.content)

@router.get("/post/{post_id}")
def get_comments(post_id: int):
    return repo.get_by_post(post_id)
