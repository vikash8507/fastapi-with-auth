from datetime import datetime
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.auth.model import User

from app.blog.schema import Blog as BlogSchema, CreateBlog as CreateBlogSchema
from app.database import get_db
from app.blog.model import Blog
from app.utils.auth import get_current_user
from app.utils.checks import get_blog_by_id
from app.utils.upload import upload_file

router = APIRouter(
    tags=["blogs"],
    prefix="/blogs"
)


@router.get("/", response_model=List[BlogSchema], status_code=status.HTTP_200_OK)
def all_blogs(db: Session = Depends(get_db)):
    return db.query(Blog).all()


@router.post("/", response_model=BlogSchema, status_code=status.HTTP_201_CREATED)
def create_blog(request: CreateBlogSchema, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    blog = Blog(title=request.title, description=request.description,
                created_at=datetime.now(), owner_id=user.id)
    blog.image = upload_file(request.image)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


@router.get("/my-blogs", response_model=List[BlogSchema], status_code=status.HTTP_200_OK)
def delete_blogs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Blog).filter(Blog.owner_id == user.id)


@router.get("/{id}", response_model=BlogSchema, status_code=status.HTTP_200_OK)
def read_blog(id: int, db: Session = Depends(get_db)):
    blog = get_blog_by_id(id, db)
    return blog


@router.patch("/{id}", response_model=BlogSchema, status_code=status.HTTP_200_OK)
def update_blogs(id: int, request: CreateBlogSchema, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    blog = get_blog_by_id(id, db)
    if blog.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can not update this blog")
    if request.title:
        blog.title = request.title
    if request.description:
        blog.description = request.description
    blog.updated_at = datetime.now()
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blogs(id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    blog = get_blog_by_id(id, db)
    if blog.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can not delete this blog")
    db.delete(blog)
    db.commit()
