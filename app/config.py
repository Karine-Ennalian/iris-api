from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Iris API"
    app_env: str = "development"
    app_version: str = "0.1.0"

    supabase_url: str
    supabase_service_role_key: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30
    otp_expire_minutes: int = 5
    dev_otp_code: str = "123456"
    return_dev_otp: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
