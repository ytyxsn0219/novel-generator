from app.llm.base import LLMClient, ModelConfig

def test_model_config_creation():
    cfg = ModelConfig(provider="test", model="m", api_key="k")
    assert cfg.provider == "test"
