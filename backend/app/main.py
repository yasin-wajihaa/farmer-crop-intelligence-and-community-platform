from fastapi import FastAPI
from app.database import engine, Base
from app.routers import users, posts, crops

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(crops.router)

@app.get("/")
def root():
    return {"message": "Backend running"}