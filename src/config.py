from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "enterprise_crm.db")

class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

    # Teams Bot Settings
    APP_ID: str = Field(default="")
    APP_PASSWORD: str = Field(default="")
    APP_TYPE: str = Field(default="MultiTenant")
    APP_TENANT_ID: str = Field(default="")
    PORT: int

    # Redis Settings (Strictly Required for Cloud)
    REDIS_HOST: str 
    REDIS_PORT: int 
    REDIS_USERNAME: str 
    REDIS_PASSWORD: str 
    REDIS_SSL: bool 

    # Database Settings
    DATABASE_URL: str = Field(default=f"sqlite:///{DEFAULT_DB_PATH}")

    # Copilot Studio Settings
    COPILOT_URL: str

config = Config()
