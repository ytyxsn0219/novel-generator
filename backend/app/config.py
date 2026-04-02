from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/novel_generator"
    redis_url: str = "redis://localhost:6379/0"
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4o"
    default_llm_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
