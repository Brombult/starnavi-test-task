from datetime import datetime

from pydantic import BaseModel


class Post(BaseModel):
    title: str
    content: str
    auto_response: bool = False
    auto_response_wait_in_sec: int = 0


class PostCreate(Post):
    pass


class PostUpdate(Post):
    pass


class PostInDB(Post):
    id: int
    created_at: datetime
    user_id: int
    blocked: bool
