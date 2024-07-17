import pytest
from fastapi import status
from sqlalchemy import select

from src.db.db import Comment

PARAMS = [
    pytest.param("whatever", id="without profanity"),
    pytest.param("fuck you", id="with profanity"),
]


def test_comment_no_auth(client, test_db):
    r = client.post("/comments", json={"content": "content"})
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize("content", PARAMS)
def test_create_comment(test_db, test_post, content):
    client, post = test_post
    r = client.post(
        f"/comments", json={"content": content}, params={"post_id": post.id}
    )
    assert r.status_code == status.HTTP_201_CREATED

    comment = test_db.scalar(select(Comment).where(Comment.id == r.json()["id"]))
    assert comment
    assert comment.content == content
    assert comment.blocked if "fuck" in content else not comment.blocked


def test_get_all_comments(test_db, test_comment):
    client, comment = test_comment
    r = client.get("/comments/all")
    assert r.status_code == status.HTTP_200_OK

    data = r.json()
    assert len(data) == 1
    data = data[0]
    assert data["content"] == comment.content


def test_get_comment(test_db, test_comment):
    client, comment = test_comment
    r = client.get(f"/comments/{comment.id}", params={"post_id": comment.post_id})
    assert r.status_code == status.HTTP_200_OK

    data = r.json()
    assert data["content"] == comment.content


@pytest.mark.parametrize("content", PARAMS)
def test_update_comment(test_db, test_comment, content):
    client, comment = test_comment
    r = client.put(
        f"/comments/{comment.id}",
        json={"content": content},
        params={"post_id": comment.post_id},
    )
    assert r.status_code == status.HTTP_200_OK

    updated_comment = r.json()
    assert updated_comment["id"] == comment.id
    assert updated_comment["user_id"] == comment.user_id
    assert updated_comment["content"] != comment.content
    assert (
        updated_comment["blocked"]
        if "fuck" in content
        else not updated_comment["blocked"]
    )


def test_delete_comment(test_db, test_comment):
    client, comment = test_comment
    r = client.delete(f"/comments/{comment.id}", params={"post_id": comment.post_id})
    assert r.status_code == status.HTTP_204_NO_CONTENT
