import asyncio

from openai import OpenAI
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import Post
from src.db.db import Comment
from src.settings import settings

client = OpenAI(api_key=settings.api_key)


def generate_comment_response(post_text: str, comment_text: str):
    resp = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Create a response to this comment: '{comment_text}',"
                f"that's related to this post: '{post_text}'",
            }
        ],
        model="gpt-3.5-turbo",
    )
    return resp.choices[0].message.content


async def create_auto_comment(
    wait_time: int, session: AsyncSession, post: Post, comment: Comment, user_id: int
):
    await asyncio.sleep(wait_time)
    response = generate_comment_response(post.content, comment.content)
    await session.execute(
        insert(Comment).values(content=response, user_id=user_id, post_id=post.id)
    )
    await session.commit()
