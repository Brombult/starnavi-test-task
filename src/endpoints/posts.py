from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from src.db import get_async_session, Post, User
from src.schemas.post import PostCreate, PostInDB, PostUpdate
from src.users import current_user

router = APIRouter(prefix="/posts", tags=["posts"])


async def get_post_by_id(
    post_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
) -> Post:
    post = await session.scalar(
        select(Post).where(Post.id == post_id).where(Post.user_id == user.id)
    )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@router.post("/", response_model=PostInDB)
async def create_post(
    new_post: PostCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    post = Post(**new_post.dict())
    post.user_id = user.id
    session.add(post)
    await session.commit()
    return post


@router.get("/all", response_model=list[PostInDB | None])
async def get_all_posts(
    session: AsyncSession = Depends(get_async_session),
):
    return await session.scalars(select(Post))


@router.get("/{post_id}", response_model=PostInDB)
async def get_post_by_id(post: Post = Depends(get_post_by_id)):
    return post


@router.put("/{post_id}", response_model=PostInDB)
async def update_post(
    new_post: PostUpdate,
    post: Post = Depends(get_post_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.scalar(
        update(Post).where(Post.id == post.id).values(**new_post.dict()).returning(Post)
    )
    await session.commit()
    return result


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post: Post = Depends(get_post_by_id),
    session: AsyncSession = Depends(get_async_session),
):
    await session.execute(delete(Post).where(Post.id == post.id))
    await session.commit()
