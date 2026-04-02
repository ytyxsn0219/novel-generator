import json
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/novel_generator"
    redis_url: str = "redis://localhost:6379/0"

    llm_mode: str = "single"
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4o"
    default_llm_api_key: str = ""
    default_llm_base_url: Optional[str] = None

    multi_llm_router_json: str = "{}"

    class Config:
        env_file = ".env"


settings = Settings()


def get_llm_router():
    from app.llm.router import ModelRouter
    default = {
        "provider": settings.default_llm_provider,
        "model": settings.default_llm_model,
        "api_key": settings.default_llm_api_key,
        "base_url": settings.default_llm_base_url,
    }
    router_map = json.loads(settings.multi_llm_router_json)
    return ModelRouter(mode=settings.llm_mode, default=default, router_map=router_map)


def get_llm_client(provider: str):
    from app.llm.openai_client import OpenAICompatibleClient
    # Future: switch on provider
    return OpenAICompatibleClient()
