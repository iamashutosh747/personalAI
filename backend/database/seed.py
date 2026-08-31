from sqlalchemy.orm import Session

from backend.config import settings
from backend.database.models import User


def ensure_default_user(db: Session) -> User:
    """Temporary stand-in until real authentication (Phase 11).

    Seeds and returns a single owner account, identified by OWNER_EMAIL,
    so every row can already be scoped by user_id ahead of multi-user support.
    """
    user = db.query(User).filter(User.email == settings.owner_email).first()
    if user is None:
        user = User(email=settings.owner_email)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
