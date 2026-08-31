from anthropic import APIConnectionError, APIError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.config import settings
from backend.services.anthropic_client import ask_claude

app = FastAPI(title="Personal AI Agent")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "environment": settings.environment}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        reply = ask_claude(request.message)
    except (APIError, APIConnectionError) as exc:
        raise HTTPException(status_code=502, detail=f"Claude API error: {exc}") from exc
    return ChatResponse(reply=reply)
