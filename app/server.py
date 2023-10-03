from fastapi import FastAPI, status, HTTPException, Request
from fastapi.responses import FileResponse

from app.blog.router import router as blog_router
from app.auth.router import router as auth_router
from app.blog import model as blog_model
from app.auth import model as auth_model
from app.database import engine

blog_model.Base.metadata.create_all(bind=engine)
auth_model.Base.metadata.create_all(bind=engine)

app = FastAPI(
    docs_url="/api/docs",
    redoc_url="/api/redocs",
    description="Api using FastAPI",
    swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
    servers=[
        {"url": "http://localhost:3000"},
        {"url": "https://dev.api.fastapi.com"},
        {"url": "https://qa.api.fastapi.com"},
        {"url": "https://stage.api.fastapi.com"},
        {"url": "https://sandbox.api.fastapi.com"},
        {"url": "https://runtime.api.fastapi.com"},
        {"url": "https://api.fastapi.com"},
    ],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    print("Middleware start...")
    response = await call_next(request)
    print("Middleware end...")
    return response


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
