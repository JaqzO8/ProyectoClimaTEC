from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: str = "development"
    APP_NAME: str = "ProyectoClimatico"
    APP_VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    WEATHER_PROVIDER: Literal["open_meteo"] = "open_meteo"
    OPEN_METEO_API_KEY: SecretStr = SecretStr("")
    OPEN_METEO_API_MODE: Literal["free", "commercial"] = "free"
    WEATHER_TIMEOUT_SECONDS: float = Field(5.0, gt=0, le=30)
    WEATHER_CACHE_TTL_SECONDS: int = Field(300, gt=0)
    GEOCODING_CACHE_TTL_SECONDS: int = Field(1800, gt=0)

    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    LOG_LEVEL: str = "INFO"
    RATE_LIMIT_ENABLED: bool = False
    TRUST_ALB_HEADERS: bool = False
    RATE_LIMIT_REQUESTS: int = Field(120, gt=0)
    RATE_LIMIT_WINDOW_SECONDS: int = Field(60, gt=0)

    @model_validator(mode="after")
    def validate_provider(self) -> "Settings":
        if (
            self.OPEN_METEO_API_MODE == "commercial"
            and not self.OPEN_METEO_API_KEY.get_secret_value()
        ):
            raise ValueError("OPEN_METEO_API_KEY is required in commercial mode")
        if "*" in self.cors_origins_list:
            raise ValueError("CORS_ORIGINS must contain explicit origins")
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
