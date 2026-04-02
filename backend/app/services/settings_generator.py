import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.llm.base import LLMClient, ModelConfig
from app.services.prompt_builder import build_settings_prompt


def generate_settings(client: "LLMClient", theme: str, config: "ModelConfig") -> dict:
    prompt = build_settings_prompt(theme)
    raw = client.generate(prompt, config)
    # Strip markdown code fences if present
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)
