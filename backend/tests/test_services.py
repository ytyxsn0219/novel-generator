from app.services.prompt_builder import build_settings_prompt

def test_build_settings_prompt_includes_theme():
    prompt = build_settings_prompt("A cyberpunk detective")
    assert "cyberpunk" in prompt
