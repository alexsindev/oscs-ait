from loguru import logger
from sqlmodel import SQLModel

from app.core.config import settings
from app.db.session import engine


def init_db() -> None:
    """Initialize database tables."""
    # Import all models to ensure they're registered with SQLModel metadata
    # This must be done before create_all() is called
    from app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)
    
    # Optionally seed default users in development
    if settings.SEED_DEFAULT_USERS:
        logger.info("SEED_DEFAULT_USERS is enabled, creating default users...")
        from app.db.seed_users import create_default_users
        create_default_users()
