import httpx
from app.llm.base import LLMClient, ModelConfig

class OpenAICompatibleClient(LLMClient):
    def generate(self, prompt: str, config: ModelConfig) -> str:
        base_url = config.base_url or "https://api.openai.com"
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens
        }
        resp = httpx.post(f"{base_url}/v1/chat/completions", headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
