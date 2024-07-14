import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker

from src.app import app
from src.db.db import Base, Post
from src.settings import settings

engine = create_engine(settings.test_db_url, connect_args={"check_same_thread": False})

session_maker = sessionmaker(engine, expire_on_commit=False)
Base.metadata.create_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def token_and_user_data(client) -> tuple[str, dict[str, str]]:
    creds = {"email": "test@example.com", "password": "test12345"}
    user_data = client.post("/auth/register", json=creds).json()
    token = client.post(
        "/auth/jwt/login",
        data={
            "username": creds["email"],
            "password": creds["password"],
        },
    ).json()["access_token"]
    return token, user_data


@pytest.fixture
def client_authorized(token_and_user_data) -> tuple[TestClient, dict[str, str]]:
    token, user_data = token_and_user_data
    return TestClient(app, headers={"Authorization": f"Bearer {token}"}), user_data


@pytest.fixture
def test_db():
    session = session_maker()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    yield session
    session.close()


@pytest.fixture
def test_post(test_db, client_authorized) -> tuple[TestClient, Post]:
    client, user = client_authorized
    post = test_db.scalar(
        insert(Post)
        .values(title="test", content="test", user_id=user["id"])
        .returning(Post)
    )
    test_db.commit()
    return client, post
