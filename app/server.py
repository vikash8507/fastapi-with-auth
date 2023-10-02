from fastapi import FastAPI, status, HTTPException
from fastapi.responses import FileResponse

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


@app.get("/{directory}/{file}", status_code=status.HTTP_200_OK)
def show_uploaded_file(directory: str, file: str):
    try:
        return FileResponse(f"{directory}/{file}")
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not found")
