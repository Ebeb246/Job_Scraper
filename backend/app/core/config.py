from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str  # injected via env (see docker-compose.yml)
    job_source_url: str = "https://remoteok.com/api"
    cors_origins: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
