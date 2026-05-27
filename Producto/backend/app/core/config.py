from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    API_PORT: int = 8000
    YOLO_MODEL_PATH: str = "weights/yolo26n_maduraapp.pt"
    CONFIDENCE_THRESHOLD: float = 0.55
    DB_URL: str = "sqlite+aiosqlite:///./maduraapp_dev.db"
    AUTH_SECRET_KEY: str = "dev_secret_key"
    JWT_SECRET_KEY: str = "dev_jwt_secret_change_in_production"
    JWT_EXPIRE_DAYS: int = 30
    ENVIRONMENT: str = "development"


settings = Settings()