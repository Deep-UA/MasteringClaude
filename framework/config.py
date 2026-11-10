from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed test configuration. Values come from env vars, then `.env`, then defaults."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    base_url: str = "https://practicesoftwaretesting.com"
    api_url: str = "https://api.practicesoftwaretesting.com"
    api_timeout: float = 10.0
    # Admin login used only to delete the per-session test user. Unset -> cleanup is skipped.
    admin_email: str | None = None
    admin_password: SecretStr | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
