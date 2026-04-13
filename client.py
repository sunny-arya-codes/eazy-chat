import json
import httpx
from config import Config


class NvidiaClient:
    def __init__(self):
        self.url = Config.API_URL
        self.headers = {
            "Authorization": f"Bearer {Config.API_KEY}",
            "Content-Type": "application/json",
        }

    def _build_payload(self, message: str, stream: bool = False) -> dict:
        return {
            "model": Config.MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are EazyAI, an intelligent and helpful AI assistant. You must always identify yourself as EazyAI. Never mention OpenAI, Google, Meta, Anthropic, or any other creator or underlying model name. Do not say you are a large language model trained by anyone else."
                },
                {"role": "user", "content": message}
            ],
            "max_tokens": Config.MAX_TOKENS,
            "temperature": Config.TEMPERATURE,
            "top_p": Config.TOP_P,
            "stream": stream,
            "chat_template_kwargs": {"enable_thinking": False},
        }

    async def stream_chat(self, message: str):
        """Async generator that yields SSE-formatted chunks from NVIDIA API."""
        payload = self._build_payload(message, stream=True)

        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                "POST",
                self.url,
                headers={**self.headers, "Accept": "text/event-stream"},
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data = line[len("data: "):]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        yield chunk
                    except json.JSONDecodeError:
                        continue

    def chat(self, message: str) -> dict:
        """Synchronous non-streaming chat call."""
        payload = self._build_payload(message, stream=False)
        response = httpx.post(
            self.url,
            headers={**self.headers, "Accept": "application/json"},
            json=payload,
            timeout=300.0,
        )
        response.raise_for_status()
        return response.json()