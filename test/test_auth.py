import pytest
from sqlalchemy import select
from fastapi import status

from src.db import User

params = [
    pytest.param("123", "Password should be at least 8 characters", id="too short"),
    pytest.param(
        "user@example.com", "Password should not contain e-mail", id="email in password"
    ),
]


def test_auth(client, test_db):
    data = {"email": "user@example.com", "password": "password12345"}
    r = client.post("/auth/register", json=data)
    assert r.status_code == status.HTTP_201_CREATED

    db_user = test_db.scalar(select(User).where(User.id == r.json()["id"]))
    assert db_user.email == r.json()["email"]

    r = client.post(
        "/auth/jwt/login",
        data={"username": data["email"], "password": data["password"]},
    )
    assert r.status_code == status.HTTP_200_OK
    assert "access_token" in r.json()


@pytest.mark.parametrize(["password", "error"], params)
def test_validate_password(client, test_db, password, error):
    r = client.post(
        "/auth/register", json={"email": "user@example.com", "password": password}
    )
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert error in r.text


def test_double_registration(client, test_db):
    data = {"email": "user@example.com", "password": "password12345"}
    r = client.post("/auth/register", json=data)
    assert r.status_code == status.HTTP_201_CREATED

    data = {"email": "user@example.com", "password": "password12345"}
    r = client.post("/auth/register", json=data)
    assert r.status_code == status.HTTP_400_BAD_REQUEST
    assert "REGISTER_USER_ALREADY_EXISTS" in r.text
