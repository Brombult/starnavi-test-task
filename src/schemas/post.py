from datetime import datetime

from pydantic import BaseModel


class Post(BaseModel):
    title: str
    content: str
    blocked: bool = False


class PostCreate(Post):
    pass


class PostUpdate(Post):
    pass


class PostInDB(Post):
    id: int
    created_at: datetime
    user_id: int
