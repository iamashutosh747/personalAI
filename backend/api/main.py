import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from anthropic import APIConnectionError, APIError
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.auth.current_user import get_current_user
from backend.config import settings
from backend.database.models import Conversation, Memory, Message, User
from backend.database.session import check_db_connection, get_db, init_db
from backend.memory.service import classify_and_store, retrieve_relevant_memories
from backend.services.anthropic_client import ask_claude


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Personal AI Agent", lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str
    conversation_id: uuid.UUID | None = None


class ChatResponse(BaseModel):
    conversation_id: uuid.UUID
    reply: str


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    role: str
    content: str
    created_at: datetime


class MemoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    content: str
    category: str
    importance: int
    confidence: float
    source: str
    created_at: datetime
    expires_at: datetime | None


def _build_system_prompt(memories: list[Memory]) -> str:
    base = (
        "You are a helpful, concise personal AI assistant. Only treat facts listed below under "
        "'Known about the user' as things you actually remember — never claim to recall something "
        "that is not listed there."
    )
    if not memories:
        return base
    facts = "\n".join(f"- {m.content}" for m in memories)
    return f"{base}\n\nKnown about the user:\n{facts}"


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "environment": settings.environment}


@app.get("/health/db")
def health_db() -> dict:
    try:
        check_db_connection()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {exc}") from exc
    return {"status": "ok"}


@app.get("/api/conversations", response_model=list[ConversationOut])
def list_conversations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Conversation]:
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


@app.get("/api/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def get_conversation_messages(
    conversation_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Message]:
    conversation = _get_owned_conversation(db, user, conversation_id)
    return conversation.messages


@app.get("/api/memories", response_model=list[MemoryOut])
def list_memories(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Memory]:
    return db.query(Memory).filter(Memory.user_id == user.id).order_by(Memory.created_at.desc()).all()


@app.delete("/api/memories/{memory_id}", status_code=204)
def delete_memory(
    memory_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> None:
    memory = db.query(Memory).filter(Memory.id == memory_id, Memory.user_id == user.id).first()
    if memory is None:
        raise HTTPException(status_code=404, detail="Memory not found")
    db.delete(memory)
    db.commit()


@app.post("/api/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ChatResponse:
    if request.conversation_id is not None:
        conversation = _get_owned_conversation(db, user, request.conversation_id)
    else:
        conversation = Conversation(user_id=user.id, title=request.message[:50])
        db.add(conversation)
        db.flush()

    db.add(Message(conversation_id=conversation.id, role="user", content=request.message))
    db.commit()

    recent = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id)
        .order_by(Message.created_at.desc())
        .limit(settings.max_history_messages)
        .all()
    )
    recent.reverse()
    claude_messages = [{"role": m.role, "content": m.content} for m in recent]

    relevant_memories = retrieve_relevant_memories(
        db, user.id, request.message, top_k=settings.memory_retrieval_top_k
    )
    system_prompt = _build_system_prompt(relevant_memories)

    try:
        reply = ask_claude(claude_messages, system=system_prompt)
    except (APIError, APIConnectionError) as exc:
        raise HTTPException(status_code=502, detail=f"Claude API error: {exc}") from exc

    db.add(Message(conversation_id=conversation.id, role="assistant", content=reply))
    conversation.updated_at = datetime.now(timezone.utc)
    db.commit()

    background_tasks.add_task(classify_and_store, user.id, request.message, reply)

    return ChatResponse(conversation_id=conversation.id, reply=reply)


def _get_owned_conversation(db: Session, user: User, conversation_id: uuid.UUID) -> Conversation:
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == user.id)
        .first()
    )
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation
