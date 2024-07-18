import datetime
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, desc
from profanity_check import predict

from src.db import get_async_session, Post, User
from src.db.db import Comment
from src.endpoints.posts import get_post_by_id
from src.schemas.comments import CommentInDB, CommentCreate, CommentUpdate, Analytics
from src.users import current_user

router = APIRouter()


async def get_comment_by_id(
    comment_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
    post: Post = Depends(get_post_by_id),
) -> Comment:
    comment = await session.scalar(
        select(Comment)
        .where(Comment.id == comment_id)
        .where(Comment.post_id == post.id)
        .where(Comment.user_id == user.id)
    )
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    return comment


@router.post("/", response_model=CommentInDB, status_code=status.HTTP_201_CREATED)
async def create_comment(
    new_comment: CommentCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
    post: Post = Depends(get_post_by_id),
):
    comment = Comment(**new_comment.dict())
    comment.user_id = user.id
    comment.post_id = post.id
    if predict([new_comment.content]).all():
        comment.blocked = True
    session.add(comment)
    await session.commit()
    return comment


@router.get("/all", response_model=list[CommentInDB | None])
async def get_all_comments(session: AsyncSession = Depends(get_async_session)):
    return await session.scalars(select(Comment))


@router.get("/{comment_id}", response_model=CommentInDB)
async def get_comment_by_id(comment: Comment = Depends(get_comment_by_id)):
    return comment


@router.put("/{comment_id}", response_model=CommentInDB)
async def update_comment(
    new_comment: CommentUpdate,
    comment: Comment = Depends(get_comment_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.scalar(
        update(Comment)
        .where(Comment.id == comment.id)
        .values(**new_comment.dict())
        .returning(Comment)
    )
    if predict([new_comment.content]).any():
        result.blocked = True
    session.add(result)
    await session.commit()
    return result


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment: Comment = Depends(get_comment_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    await session.execute(delete(Comment).where(Comment.id == comment.id))
    await session.commit()


@router.get("/analytics/daily", response_model=list[Analytics])
async def get_analytics(
    date_from: date, date_to: date, session: AsyncSession = Depends(get_async_session)
):
    stmt = (
        select(
            Comment.created_at,
            func.count(Comment.created_at).label("num_created"),
            func.count(Comment.id).filter(Comment.blocked).label("num_blocked"),
        )
        .group_by("created_at")
        .order_by("created_at")
        .having(Comment.created_at.between(date_from, date_to))
    )
    query = await session.execute(stmt)
    query = query.all()
    return [
        Analytics(
            created_at=row.created_at,
            num_created=row.num_created,
            num_blocked=row.num_blocked,
        )
        for row in query
    ]
