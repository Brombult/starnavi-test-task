import pytest
from sqlalchemy import select
from fastapi import status

from src.db import User

TEST_USER_CREDS = {"email": "user@example.com", "password": "password12345"}

params = [
    pytest.param("123", "Password should be at least 8 characters", id="too short"),
    pytest.param(
        TEST_USER_CREDS["email"],
        "Password should not contain e-mail",
        id="email in password",
    ),
]


def test_auth(client, test_db):
    r = client.post("/auth/register", json=TEST_USER_CREDS)
    assert r.status_code == status.HTTP_201_CREATED

    db_user = test_db.scalar(select(User).where(User.id == r.json()["id"]))
    assert db_user.email == r.json()["email"]

    r = client.post(
        "/auth/jwt/login",
        data={
            "username": TEST_USER_CREDS["email"],
            "password": TEST_USER_CREDS["password"],
        },
    )
    assert r.status_code == status.HTTP_200_OK
    assert "access_token" in r.json()


@pytest.mark.parametrize(["password", "error"], params)
def test_validate_password(client, test_db, password, error):
    r = client.post(
        "/auth/register", json={"email": TEST_USER_CREDS["email"], "password": password}
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert error in r.text


def test_double_registration(client, test_db):
    r = client.post("/auth/register", json=TEST_USER_CREDS)
    assert r.status_code == status.HTTP_201_CREATED

    r = client.post("/auth/register", json=TEST_USER_CREDS)
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert "REGISTER_USER_ALREADY_EXISTS" in r.text
