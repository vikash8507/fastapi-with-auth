from datetime import datetime
from fastapi import APIRouter, status, Depends
from typing import List
from sqlalchemy.orm import Session
from fastapi_pagination import Page, paginate
from app.auth.model import User

from app.blog.schema import Blog as BlogSchema, CreateBlog as CreateBlogSchema
from app.database import get_db
from app.blog.model import Blog
from app.utils.auth import get_current_user
from app.utils.checks import get_blog_by_id

router = APIRouter(
    tags=["blogs"],
    prefix="/blogs"
)


@router.get("/", response_model=Page[BlogSchema], status_code=status.HTTP_200_OK)
def all_blogs(db: Session = Depends(get_db)):
    return paginate(db.query(Blog).all())


@router.post("/", response_model=BlogSchema, status_code=status.HTTP_201_CREATED)
def create_blog(request: CreateBlogSchema, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    blog = Blog(title=request.title, description=request.description,
                created_at=datetime.now())
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


@router.get("/{id}", response_model=BlogSchema, status_code=status.HTTP_200_OK)
def read_blog(id: int, db: Session = Depends(get_db)):
    blog = get_blog_by_id(id, db)
    return blog


@router.patch("/{id}", response_model=BlogSchema, status_code=status.HTTP_200_OK)
def update_blogs(id: int, request: CreateBlogSchema, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    blog = get_blog_by_id(id, db)
    blog.title = request.title
    blog.description = request.description
    blog.updated_at = datetime.now()
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blogs(id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    blog = get_blog_by_id(id, db)
    db.delete(blog)
    db.commit()
