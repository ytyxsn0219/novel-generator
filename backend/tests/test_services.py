from app.services.prompt_builder import build_settings_prompt

def test_build_settings_prompt_includes_theme():
    prompt = build_settings_prompt("A cyberpunk detective")
    assert "cyberpunk" in prompt

from unittest.mock import MagicMock
from app.services.settings_generator import generate_settings

def test_generate_settings_returns_json():
    mock_client = MagicMock()
    mock_client.generate.return_value = '{"world_view": "w", "characters": [], "outline": [], "style": "s"}'
    from app.llm.base import ModelConfig
    result = generate_settings(mock_client, "theme", ModelConfig(provider="x", model="m", api_key="k"))
    assert result["world_view"] == "w"
