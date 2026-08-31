from fastapi import Depends
from sqlalchemy.orm import Session

from backend.database.models import User
from backend.database.seed import ensure_default_user
from backend.database.session import get_db


def get_current_user(db: Session = Depends(get_db)) -> User:
    """Placeholder for real authentication, added in Phase 11."""
    return ensure_default_user(db)
