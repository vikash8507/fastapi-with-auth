from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BlogBase(BaseModel):
    title: str = Field(
        default=None, title="Title of the blog", max_length=150
    )
    description: str = Field(
        default=None, title="Description of the blog", max_length=500
    )

class CreateBlog(BlogBase):
    image: str

class Blog(BlogBase):
    id: int
    image: str
    created_at: datetime = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
