from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed test configuration. Values come from env vars, then `.env`, then defaults."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    base_url: str = "https://practicesoftwaretesting.com"
    api_url: str = "https://api.practicesoftwaretesting.com"
    api_timeout: float = 10.0

    customer_email: str
    customer_password: SecretStr


@lru_cache
def get_settings() -> Settings:
    return Settings()
