from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str
    OPENAI_API_KEY: str
    RESEND_API_KEY: str
    JWT_SECRET: str
    MAPBOX_TOKEN: str
    NOAA_TOKEN: str
    FRONTEND_URL: str = "http://localhost:3000"
    ADMIN_URL: str = "http://localhost:5173"

    # JWT
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Scheduler
    DEFAULT_CYCLE_HOURS: int = 12
    ELEVATED_CYCLE_HOURS: int = 2


settings = Settings()
