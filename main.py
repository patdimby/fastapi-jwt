"""Mini-blog demo: each process owns its temporary account and post stores."""
from fastapi import FastAPI, Depends, HTTPException
from app.model import PostSchema, UserSchema, UserLoginSchema
from app.auth.jwt_handler import signJWT
from app.auth.jwt_bearer import JWTBearer
from app.auth.passwords import hash_password, verify_password

posts = [
    {"id": 1, "title": "Penguins are awesome", "content": "They are the most awesome animals ever"},
    {"id": 2, "title": "Tigers are awesome", "content": "Wear stripes like a tiger"},
    {"id": 3, "title": "Elephants are awesome", "content": "Large Herbivorous Mammals"},
]
users = []
app = FastAPI(title="FastAPI JWT Mini Blog", version="1.0.0")

@app.get("/", tags=["test"])
def greet(): return {"message": "Hello World"}

@app.get("/posts", tags=["posts"])
def get_posts(): return {"data": posts}

@app.get("/posts/{id}", tags=["posts"])
def get_post(id: int):
    for post in posts:
        if post["id"] == id: return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.post("/posts", dependencies=[Depends(JWTBearer())], tags=["posts"])
def create_post(post: PostSchema):
    post.id = max((item["id"] for item in posts), default=0) + 1
    posts.append(post.model_dump())
    return {"message": "Post created successfully"}

@app.post("/users/signup", tags=["user"])
def user_signup(user: UserSchema):
    if any(existing["email"] == user.email for existing in users):
        raise HTTPException(status_code=409, detail="Email already registered")
    users.append({"fullname": user.fullname, "email": str(user.email), "password_hash": hash_password(user.password)})
    return signJWT(str(user.email))

def check_user(data: UserLoginSchema):
    # Search all users, rather than returning after the first nonmatching account.
    for user in users:
        if user["email"] == data.email:
            return verify_password(data.password, user["password_hash"])
    return False

@app.post("/users/login", tags=["user"])
def user_login(data: UserLoginSchema):
    if check_user(data): return signJWT(str(data.email))
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/users", dependencies=[Depends(JWTBearer())], tags=["users"])
def get_users():
    # Never expose plaintext credentials or hashes in HTTP responses.
    return {"data": [{"fullname": user["fullname"], "email": user["email"]} for user in users]}
