import json
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.llm.base import LLMClient, ModelConfig
from app.services.prompt_builder import build_chapter_prompt


def generate_chapter(
    client: "LLMClient",
    settings: dict,
    prev_summary: str,
    current_number: int,
    config: "ModelConfig",
    locked_before_summary: Optional[str] = None,
    locked_after_constraint: Optional[str] = None,
) -> tuple[str, str]:
    prompt = build_chapter_prompt(
        settings, prev_summary, current_number, locked_before_summary, locked_after_constraint
    )
    raw = client.generate(prompt, config)
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    data = json.loads(text)
    return data.get("title", ""), data.get("content", "")
