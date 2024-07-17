from datetime import datetime

from pydantic import BaseModel


class Comment(BaseModel):
    content: str


class CommentCreate(Comment):
    pass


class CommentUpdate(Comment):
    pass


class CommentInDB(Comment):
    id: int
    created_at: datetime
    user_id: int
    post_id: int
    blocked: bool = False
