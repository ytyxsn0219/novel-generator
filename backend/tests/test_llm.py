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
