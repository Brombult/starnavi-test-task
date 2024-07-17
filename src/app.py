from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.db import create_db_and_tables
from src.endpoints.posts import router as posts_router
from src.endpoints.comments import router as comments_router
from src.schemas import UserCreate, UserRead, UserUpdate
from src.users import auth_backend, fastapi_users


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    posts_router,
    prefix="/posts",
    tags=["posts"],
)
app.include_router(
    comments_router,
    prefix="/comments",
    tags=["comments"],
)
