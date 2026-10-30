from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "IndexGuard API"
    app_env: str = "development"
    database_url: str = (
        "postgresql+psycopg://indexguard:indexguard@localhost:5432/indexguard"
    )
    log_level: str = "INFO"
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
