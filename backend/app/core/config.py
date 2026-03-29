from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import json
import os
import warnings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    CORS_ORIGINS: List[str] = ["http://localhost:2001"]

    UPLOAD_DIR: str = "uploads"

    SSO_ENABLED: bool = False
    SSO_FRONTEND_SUCCESS_URL: Optional[str] = None
    SSO_BACKEND_PUBLIC_URL: Optional[str] = None

    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None

    GOOGLE_ISSUER: str = "https://accounts.google.com"
    
    # SMTP Config
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: str = "Aide"
    
    # Redis Config
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = "utf-8"

   
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return json.loads(v)
            return [origin.strip() for origin in v.split(",")]
        return v

    
    @property
    def sso_callback_url(self) -> Optional[str]:
        if not self.SSO_BACKEND_PUBLIC_URL:
            return None
        base = self.SSO_BACKEND_PUBLIC_URL.rstrip("/")
        return f"{base}/api/v1/auth/sso/callback"

    @property
    def google_provider_config(self) -> Optional[dict]:
        if not (
            self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET
        ):
            return None

        return {
            "issuer": self.GOOGLE_ISSUER,
            "client_id": self.GOOGLE_CLIENT_ID,
            "client_secret": self.GOOGLE_CLIENT_SECRET,
        }


settings = Settings()


if not os.path.exists(".env"):
    warnings.warn(
        "⚠️ No .env file found. Set environment variables manually in production.",
        UserWarning
    )

if settings.SECRET_KEY.startswith("dev-"):
    warnings.warn(
        "⚠️ You are using a development SECRET_KEY. Change this in production!",
        UserWarning
    )