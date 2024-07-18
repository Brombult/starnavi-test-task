import random
import datetime

import pytest
from fastapi import status
from sqlalchemy import select, insert

from src.db.db import Comment

PARAMS = [
    pytest.param("whatever", id="without profanity"),
    pytest.param("fuck you", id="with profanity"),
]


@pytest.fixture
def generate_comments_for_analytics(test_db, test_post):
    _, post = test_post
    created = [
        test_db.scalars(
            insert(Comment)
            .values(
                content="test",
                post_id=post.id,
                user_id=post.user_id,
                blocked=random.choice([True, False]),
                created_at=random.choice(
                    [
                        datetime.date.today() - datetime.timedelta(days=n)
                        for n in range(7)
                    ]
                ),
            )
            .returning(Comment)
        )
        for _ in range(10)
    ]
    num_blocked = sum([1 for c in created if c.first().blocked])
    test_db.commit()
    return len(created), num_blocked


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


def test_analytics(test_db, generate_comments_for_analytics, client_authorized):
    num_created, num_blocked = generate_comments_for_analytics
    client, _ = client_authorized
    today = datetime.date.today()
    r = client.get(
        "/comments/analytics/daily",
        params={
            "date_from": str(today - datetime.timedelta(days=8)),
            "date_to": str(today + datetime.timedelta(days=1)),
        },
    )
    assert r.status_code == status.HTTP_200_OK

    data = r.json()
    assert sum(d["num_created"] for d in data) == num_created
    assert sum(d["num_blocked"] for d in data) == num_blocked


def test_analytics_out_of_range(
    test_db, generate_comments_for_analytics, client_authorized
):
    client, _ = client_authorized
    today = datetime.date.today()
    r = client.get(
        "/comments/analytics/daily",
        params={
            "date_from": str(today + datetime.timedelta(days=10)),
            "date_to": str(today + datetime.timedelta(days=20)),
        },
    )
    assert r.status_code == status.HTTP_200_OK

    data = r.json()
    assert not len(data)
