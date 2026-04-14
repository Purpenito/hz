from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "arb_bot"
    env: str = "dev"
    log_level: str = "INFO"

    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    scanner_interval_sec: int = 15
    scanner_symbols_per_exchange_cycle: int = 80

    db_url: str = Field(
        default="postgresql+asyncpg://arb:arb@postgres:5432/arb", alias="DB_URL"
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")


@lru_cache(1)
def get_settings() -> Settings:
    return Settings()
