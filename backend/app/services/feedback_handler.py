from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.llm.base import LLMClient, ModelConfig
from app.services.prompt_builder import build_feedback_scope_prompt


def infer_feedback_scope(
    client: "LLMClient",
    settings: dict,
    chapter_summary: Optional[str],
    feedback: str,
    config: "ModelConfig",
) -> str:
    prompt = build_feedback_scope_prompt(settings, chapter_summary, feedback)
    raw = client.generate(prompt, config).strip().lower()
    # Extract first valid word
    for token in raw.split():
        token = token.strip(".,;:!?")
        if token in ("chapter", "future", "global"):
            return token
    return "chapter"
