from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Valor centinela: si este secreto llega a producción, la app se niega a arrancar.
_INSECURE_JWT_DEFAULT = "dev_jwt_secret_change_in_production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    API_PORT: int = 8000
    YOLO_MODEL_PATH: str = "weights/yolo26n_maduraapp.pt"
    CONFIDENCE_THRESHOLD: float = 0.55
    DB_URL: str = "sqlite+aiosqlite:///./maduraapp_dev.db"
    JWT_SECRET_KEY: str = _INSECURE_JWT_DEFAULT
    JWT_EXPIRE_DAYS: int = 30
    ENVIRONMENT: str = "development"
    # Orígenes permitidos para CORS, separados por coma. "*" solo es válido en dev.
    CORS_ORIGINS: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        """Lista de orígenes para el middleware CORS."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @model_validator(mode="after")
    def _enforce_production_hardening(self) -> "Settings":
        """En producción exige secretos fuertes y CORS acotado (OWASP A02/A05)."""
        if self.ENVIRONMENT == "production":
            if self.JWT_SECRET_KEY == _INSECURE_JWT_DEFAULT:
                raise ValueError(
                    "JWT_SECRET_KEY debe definirse via variable de entorno en producción. "
                    "Genera uno con: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
                )
            if len(self.JWT_SECRET_KEY) < 32:
                raise ValueError(
                    "JWT_SECRET_KEY debe tener al menos 32 caracteres en producción."
                )
            if self.CORS_ORIGINS.strip() == "*":
                raise ValueError(
                    "CORS_ORIGINS no puede ser '*' en producción. "
                    "Define los dominios permitidos separados por coma."
                )
        return self


settings = Settings()
