from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/ecommerce_api"
    rapidapi_proxy_secret: str = ""
    cache_ttl_seconds: int = 300
    max_requests_per_minute: int = 60

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
