from datetime import datetime

from pydantic import BaseModel


class Comment(BaseModel):
    content: str
    blocked: bool = False


class CommentCreate(Comment):
    user_id: int


class CommentUpdate(Comment):
    pass


class CommentInDB(Comment):
    id: int
    created_at: datetime
