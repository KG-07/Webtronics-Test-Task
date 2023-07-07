from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    password: str

class Post(BaseModel):
    title: str
    content: str
    author: str

class Like(BaseModel):
    post_id: int
    user_id: int

users = []
posts = []
likes = []

@app.post("/signup")
def signup(user: User):
    if user.username in [u.username for u in users]:
        raise HTTPException(status_code=400, detail="Username already exists")
    users.append(user)
    return {"message": "User created successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = next((u for u in users if u.username == form_data.username), None)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if user.password != form_data.password:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return {"access_token": "secret"}

@app.get("/posts")
def get_posts():
    return posts

@app.post("/posts")
def create_post(post: Post, token: str = Depends(oauth2_scheme)):
    author = next((u for u in users if u.username == token), None)
    if not author:
        raise HTTPException(status_code=401, detail="Invalid token")
    post.author = author.username
    posts.append(post)
    return {"message": "Post created successfully"}

@app.put("/posts/{post_id}")
def edit_post(post_id: int, post: Post, token: str = Depends(oauth2_scheme)):
    author = next((u for u in users if u.username == token), None)
    if not author:
        raise HTTPException(status_code=401, detail="Invalid token")
    p = next((p for p in posts if p.id == post_id), None)
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    if p.author != author.username:
        raise HTTPException(status_code=403, detail="You are not the author of this post")
    p.title = post.title
    p.content = post.content
    return {"message": "Post updated successfully"}

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, token: str = Depends(oauth2_scheme)):
    author = next((u for u in users if u.username == token), None)
    if not author:
        raise HTTPException(status_code=401, detail="Invalid token")
    p = next((p for p in posts if p.id == post_id), None)
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    if p.author != author.username:
        raise HTTPException(status_code=403, detail="You are not the author of this post")
    posts.remove(p)
    return {"message": "Post deleted successfully"}

@app.post("/likes")
def like_post(like: Like):
    if like.user_id == next((l.user_id for l in likes if l.post_id == like.post_id), None):
        raise HTTPException(status_code=400, detail="You cannot like your own post")
    likes.append(like)
    return {"message": "Post liked successfully"}

@app.delete("/likes/{post_id}")
def dislike_post(post_id: int):
    like = next((l for l in likes if l.post_id == post_id), None)
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    likes.remove(like)

