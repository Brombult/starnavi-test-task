from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    db_url: str = "sqlite+aiosqlite:///./app.db"
    test_db_url: str = "sqlite:///./app.db"
    secret: str = ""
    api_key: str = ""


settings = Settings(_env_file="prod.env", _env_file_encoding="utf-8")
