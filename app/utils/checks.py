from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.blog.model import Blog


def get_blog_by_id(id: int, db: Session) -> Blog:
    blog = db.query(Blog).filter(Blog.id == id)
    if blog.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found")
    return blog.first()
