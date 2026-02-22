from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "MediScan AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Azure Blob Storage (HIPAA-aware image persistence)
    AZURE_STORAGE_CONNECTION_STRING: str = ""
    AZURE_CONTAINER_NAME: str = "mediscan-scans"

    # GCP
    GCP_PROJECT_ID: str = ""
    GCP_BUCKET_NAME: str = ""

    # W&B experiment tracking
    WANDB_API_KEY: str = ""
    WANDB_PROJECT: str = "mediscan-ai"

    # Model settings
    DENSENET_MODEL: str = "densenet121-res224-chex"  # torchxrayvision model key
    MAX_IMAGE_SIZE_MB: int = 10

    # HIPAA audit log retention (days)
    AUDIT_LOG_RETENTION_DAYS: int = 2190  # 6 years per HIPAA §164.312(b)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
