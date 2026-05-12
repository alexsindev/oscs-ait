import time
import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from loguru import logger
from sqlmodel import Session, select

from app.core.config import settings
from app.db.session import get_session
from app.models.auth import JWTBlacklist
from app.models.user import User

# OAuth2 Bearer scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """
    Decode JWT, ensure it's not revoked/expired (via JWTBlacklist), and return the authenticated user.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from err

    user_id = payload.get("user_id")
    jti = payload.get("jti")
    if not user_id or not jti:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token payload")

    db_token = session.exec(select(JWTBlacklist).where(JWTBlacklist.jti == jti)).first()
    now = int(time.time())
    if not db_token or db_token.exp <= now:
        logger.debug(f"Token jti={jti} is expired or revoked.")
        logger.debug(f"DB Token: {db_token}")
        logger.debug(f"Current time: {now}, Token exp: {db_token.exp if db_token else 'N/A'}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or revoked")

    user = session.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Optional: Enforce that only approved users can authenticate
    # if not user.is_approved:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="User account not approved by admin",
    #     )

    return user
