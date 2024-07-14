import pytest
from fastapi import status
from sqlalchemy import select

from src.db import Post


def test_post_no_auth(client, test_db):
    r = client.post("/posts", json={"title": "title", "content": "content"})
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "content", ["how are you?", "fuck you"], ids=["without profanity", "with profanity"]
)
def test_create_post(test_db, client_authorized, content):
    client, user_data = client_authorized
    r = client.post("/posts", json={"title": "title", "content": content})
    assert r.status_code == status.HTTP_201_CREATED

    post = test_db.scalar(
        select(Post)
        .where(Post.id == r.json()["id"])
        .where(Post.user_id == user_data["id"])
    )
    assert post
    assert post.content == content
    assert post.blocked if "fuck" in content else not post.blocked


def test_get_all_post(test_db, test_post):
    client, post = test_post
    r = client.get("/posts/all")
    assert r.status_code == status.HTTP_200_OK

    data = r.json()
    assert len(data) == 1
    api_post = data[0]
    assert api_post["title"] == post.title
    assert api_post["content"] == post.content


def test_get_post(test_db, test_post):
    client, post = test_post
    r = client.get(f"/posts/{post.id}")
    assert r.status_code == status.HTTP_200_OK

    api_post = r.json()
    assert api_post["title"] == post.title
    assert api_post["content"] == post.content


@pytest.mark.parametrize(
    "content", ["how are you?", "fuck you"], ids=["without profanity", "with profanity"]
)
def test_update_post(test_db, test_post, content):
    client, post = test_post
    r = client.put(f"/posts/{post.id}", json={"title": "title", "content": content})
    assert r.status_code == status.HTTP_200_OK
    updated_post = r.json()

    assert updated_post["id"] == post.id
    assert updated_post["user_id"] == post.user_id
    assert updated_post["blocked"] if "fuck" in content else not updated_post["blocked"]
    assert updated_post["content"] != post.content


def test_delete_post(test_db, test_post):
    client, post = test_post
    r = client.delete(f"/posts/{post.id}")
    assert r.status_code == status.HTTP_204_NO_CONTENT

    r = client.get("/posts/all")
    assert not r.json()
