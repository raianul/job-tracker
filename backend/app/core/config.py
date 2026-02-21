from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    database_url: str = "postgresql://postgres:postgres@localhost:5432/jobtracker"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days
    google_client_id: str = ""
    google_client_secret: str = ""
    linkedin_client_id: str = ""
    linkedin_client_secret: str = ""
    admin_emails: str = ""  # comma-separated
    frontend_url: str = "http://localhost:3000"
    backend_origin: str = "http://localhost:8000"  # for OAuth redirect_uri

    @property
    def admin_emails_list(self) -> List[str]:
        if not self.admin_emails:
            return []
        return [e.strip().lower() for e in self.admin_emails.split(",") if e.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
