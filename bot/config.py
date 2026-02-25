from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    BOT_TOKEN: str
    DATABASE_URL: str
    WEBAPP_URL: str
    ADMIN_ID: Optional[int] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()