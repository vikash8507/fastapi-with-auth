from typing import Union
from fastapi import FastAPI

from app.blog.router import router as blog_router
from app.auth.router import router as auth_router
from app.blog import model
from app.database import engine

model.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(blog_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}
