import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Peblo TV Mini API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///./peblo.db"

    # Auth
    SECRET_KEY: str = "super-secret-development-key-change-in-production-32-chars-min"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Storage
    STORAGE_TYPE: str = "local"
    STORAGE_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../storage"))
    CATALOGUE_PATH: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../storage/catalogue.json"))

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
