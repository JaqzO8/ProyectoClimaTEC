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

    WEATHER_PROVIDER: str = "open_meteo"
    WEATHER_TIMEOUT_SECONDS: float = 5.0
    WEATHER_CACHE_TTL_SECONDS: int = 300
    GEOCODING_CACHE_TTL_SECONDS: int = 1800

    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    LOG_LEVEL: str = "INFO"
    RATE_LIMIT_ENABLED: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
