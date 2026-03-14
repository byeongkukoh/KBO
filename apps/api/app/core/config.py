from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(default="sqlite:///./kbo_record.db", alias="DATABASE_URL")
    kbo_base_url: str = Field(default="https://www.koreabaseball.com", alias="KBO_BASE_URL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def clear_settings_cache() -> None:
    get_settings.cache_clear()
