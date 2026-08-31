import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.database.models import Memory
from backend.database.session import SessionLocal
from backend.services.anthropic_client import ask_utility
from backend.services.voyage_client import embed_text

logger = logging.getLogger(__name__)

_CLASSIFY_PROMPT = """You help a personal AI assistant decide what is worth remembering long-term about its user.

Given one exchange below, decide if it contains a stable fact, preference, decision, or project \
detail worth remembering beyond this conversation. Small talk, one-off questions, and anything \
already obvious from context should NOT be remembered.

Respond with ONLY a JSON object, no other text:
- If worth remembering: {{"should_remember": true, "content": "<concise standalone fact, written \
in third person>", "category": "profile"|"preference"|"project"|"decision"|"other", \
"importance": <1-5>, "confidence": <0.0-1.0>}}
- If not: {{"should_remember": false}}

User said: {user_message}
Assistant replied: {assistant_reply}
"""


def classify_and_store(user_id: uuid.UUID, user_message: str, assistant_reply: str) -> None:
    """Runs as a background task after a chat reply has already been sent.

    Opens its own DB session, since the request's session is closed by the
    time a background task runs. Any failure here is logged and swallowed —
    it must never affect the chat response the user already received.
    """
    try:
        prompt = _CLASSIFY_PROMPT.format(user_message=user_message, assistant_reply=assistant_reply)
        decision = json.loads(ask_utility([{"role": "user", "content": prompt}]))

        if not decision.get("should_remember"):
            return

        content = decision.get("content")
        if not content:
            return

        embedding = embed_text(content, input_type="document")

        db = SessionLocal()
        try:
            db.add(
                Memory(
                    user_id=user_id,
                    content=content,
                    category=decision.get("category", "other"),
                    importance=int(decision.get("importance", 3)),
                    confidence=float(decision.get("confidence", 0.5)),
                    source="conversation",
                    embedding=embedding,
                )
            )
            db.commit()
        finally:
            db.close()
    except Exception:
        logger.exception("Memory classification/storage failed; skipping this turn's memory.")


def retrieve_relevant_memories(db: Session, user_id: uuid.UUID, query_text: str, top_k: int) -> list[Memory]:
    """Semantic search over the user's long-term memories. Fails soft: an
    embedding-service outage degrades to "no memory context" rather than
    breaking the chat request.
    """
    try:
        query_embedding = embed_text(query_text, input_type="query")
    except Exception:
        logger.exception("Memory retrieval embedding failed; continuing without memory context.")
        return []

    now = datetime.now(timezone.utc)
    return (
        db.query(Memory)
        .filter(Memory.user_id == user_id)
        .filter(or_(Memory.expires_at.is_(None), Memory.expires_at > now))
        .order_by(Memory.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )
