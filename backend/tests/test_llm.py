from app.llm.base import LLMClient, ModelConfig

def test_model_config_creation():
    cfg = ModelConfig(provider="test", model="m", api_key="k")
    assert cfg.provider == "test"

from unittest.mock import patch, MagicMock
from app.llm.openai_client import OpenAICompatibleClient
from app.llm.base import ModelConfig

def test_openai_client_generate():
    client = OpenAICompatibleClient()
    cfg = ModelConfig(provider="openai", model="gpt-4o", api_key="fake-key")
    with patch("httpx.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {
            "choices": [{"message": {"content": "hello"}}]
        })
        result = client.generate("say hi", cfg)
        assert result == "hello"

from app.llm.router import ModelRouter

def test_single_mode_router():
    router = ModelRouter(mode="single", default={"provider":"openai","model":"gpt-4o","api_key":"k"})
    cfg = router.get_config("writing")
    assert cfg.provider == "openai"

def test_multi_mode_router():
    router = ModelRouter(
        mode="multi",
        default={"provider":"x","model":"m","api_key":"k"},
        router_map={"writing": {"provider":"deepseek","model":"v3","api_key":"dk"}}
    )
    cfg = router.get_config("writing")
    assert cfg.provider == "deepseek"

from app.config import get_llm_router

def test_get_llm_router_single():
    router = get_llm_router()
    assert router.mode == "single"
    cfg = router.get_config("writing")
    assert cfg.provider == "openai"
