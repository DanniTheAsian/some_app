from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models.post import Post
from routers.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["Posts"])

class PostCreate(BaseModel):
    title: str
    content: str


class PostUpdate(BaseModel):
    title: str
    content: str

@router.post("/")
def create_post(data: PostCreate, current_user=Depends(get_current_user)):
    post = Post.create_post(
        user_id=current_user.id,
        title=data.title,
        content=data.content
    )

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "created_at": post.created_at
    }


@router.get("/")
def get_posts():
    posts = Post.get_all()

    return [
        {
            "id": p[0],
            "user_id": p[1],
            "title": p[2],
            "content": p[3],
            "created_at": p[4],
            "username": p[5]   # 🔥 her
        }
        for p in posts
    ]

@router.get("/{post_id}")
def get_post(post_id: int):
    post = Post.get_by_id(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "user_id": post.user_id,
        "created_at": post.created_at
    }

@router.put("/{post_id}")
def update_post(post_id: int, data: PostUpdate, current_user=Depends(get_current_user)):
    success = Post.update(
        post_id=post_id,
        user_id=current_user.id,
        title=data.title,
        content=data.content
    )

    if not success:
        raise HTTPException(status_code=403, detail="Du kan kun redigere dine egne posts")

    return {"message": "Post updated"}

@router.delete("/{post_id}")
def delete_post(post_id: int, current_user=Depends(get_current_user)):
    success = Post.delete(post_id, current_user.id)

    if not success:
        raise HTTPException(status_code=403, detail="Du kan kun slette dine egne posts")

    return {"message": "Post deleted"}
