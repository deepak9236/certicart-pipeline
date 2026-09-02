"""Validated pipeline configuration."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="CERTIKART_",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Literal["development", "test", "staging", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: SecretStr = SecretStr(
        "postgresql+psycopg://certikart:certikart_dev_only@localhost:5432/certikart"
    )
    request_timeout_seconds: float = Field(default=30.0, gt=0, le=120)
    max_source_concurrency: int = Field(default=2, ge=1, le=10)
    obey_robots_txt: bool = True
    collection_profile: Literal["smoke", "shadow", "incremental", "backfill"] = "smoke"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
