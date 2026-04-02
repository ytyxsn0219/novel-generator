from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel

class ModelConfig(BaseModel):
    provider: str
    model: str
    api_key: str
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000

class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, config: ModelConfig) -> str:
        ...
