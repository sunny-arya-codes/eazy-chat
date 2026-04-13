import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from client import NvidiaClient

app = FastAPI(title="Eazy AI API")

# Allow specific origins for production and local development frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://eazyai.in",
        "https://chat.eazyai.in",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nvidia_client = NvidiaClient()


class ChatRequest(BaseModel):
    message: str


@app.post("/api/chat")
async def chat(body: ChatRequest, stream: bool = Query(default=True)):
    """
    Chat endpoint.

    - `stream=true`  → returns an SSE stream (text/event-stream)
    - `stream=false` → returns a single JSON response
    """
    if stream:
        return EventSourceResponse(
            _stream_generator(body.message),
            media_type="text/event-stream",
        )

    result = nvidia_client.chat(body.message)
    return result


async def _stream_generator(message: str):
    """Yields SSE events from the NVIDIA streaming response."""
    async for chunk in nvidia_client.stream_chat(message):
        # Extract the delta content if present
        choices = chunk.get("choices", [])
        if choices:
            delta = choices[0].get("delta", {})
            content = delta.get("content", "")
            finish_reason = choices[0].get("finish_reason")

            event_data = {
                "content": content,
                "finish_reason": finish_reason,
            }
            yield json.dumps(event_data)

    # Signal completion
    yield json.dumps({"content": "", "finish_reason": "stop", "done": True})