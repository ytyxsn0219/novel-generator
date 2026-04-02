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


def get_db_llm_config(db):
    """从数据库获取 LLM 配置，如果不存在则使用环境变量默认值"""
    from app.models import SystemConfig

    def get_config_value(key: str, default: str = "") -> str:
        config = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        return config.value if config else default

    provider = get_config_value("llm_provider", settings.default_llm_provider)
    model = get_config_value("llm_model", settings.default_llm_model)
    api_key = get_config_value("llm_api_key", settings.default_llm_api_key)
    base_url = get_config_value("llm_base_url", settings.default_llm_base_url or "")

    # 如果没有配置 API Key，尝试使用环境变量
    if not api_key:
        api_key = settings.default_llm_api_key

    return {
        "provider": provider,
        "model": model,
        "api_key": api_key,
        "base_url": base_url if base_url else None,
        "temperature": float(get_config_value("llm_temperature", "0.7")),
        "max_tokens": int(get_config_value("llm_max_tokens", "4000"))
    }
