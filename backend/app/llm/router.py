from typing import Optional, Dict
from app.llm.base import ModelConfig

class ModelRouter:
    def __init__(self, mode: str, default: dict, router_map: Optional[dict] = None):
        self.mode = mode
        self.default = ModelConfig(**default)
        self.router_map = {k: ModelConfig(**v) for k, v in (router_map or {}).items()}

    def get_config(self, task_type: str) -> ModelConfig:
        if self.mode == "single" or task_type not in self.router_map:
            return self.default
        return self.router_map[task_type]
