from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="ignore",
    )

    env: str = Field("development", alias="ENVIRONMENT")
    app_name: str = Field("__APP_NAME__", alias="APP_NAME")
    mysql_url: str = Field("__MYSQL_URL__", alias="MYSQL_URL")
    redis_url: str = Field("__REDIS_URL__", alias="REDIS_URL")
    celery_broker_url: str = Field("__CELERY_BROKER_URL__", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field("__CELERY_RESULT_BACKEND__", alias="CELERY_RESULT_BACKEND")
    log_level: str = Field("__LOG_LEVEL__", alias="LOG_LEVEL")
    log_dir: str = Field("__LOG_DIR__", alias="LOG_DIR")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


