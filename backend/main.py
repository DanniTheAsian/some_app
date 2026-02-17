from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from routers import auth, posts, likes, comments

app = FastAPI()

app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts="*"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://no-name-git-master-dannis-projects-83a67ffd.vercel.app",
        "https://no-name-beta-lake.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(likes.router)
app.include_router(comments.router)
