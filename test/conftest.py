import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.app import app
from src.db.db import Base
from src.settings import settings

engine = create_engine(settings.test_db_url, connect_args={"check_same_thread": False})

session_maker = sessionmaker(engine, expire_on_commit=False)
Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def test_db():
    session = session_maker()
    yield session
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()
