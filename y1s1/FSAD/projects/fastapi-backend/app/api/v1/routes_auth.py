import time
import uuid
from typing import Annotated

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from loguru import logger
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import get_current_user, oauth2_scheme
from app.db.session import get_session
from app.models.auth import JWTBlacklist, JWTPayload, LoginResponse
from app.models.user import User, UserChangePassword, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    session: Annotated[Session, Depends(get_session)],
) -> UserRead:
    db_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    if user_data.role not in {
        "admin",
        "teacher",
        "student",
        "instructor",
        "guest",
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role specified",
        )
    hashed_pw = bcrypt.hashpw(
        user_data.password.get_secret_value().encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")
    user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        hashed_password=hashed_pw,
        role=user_data.role,
        is_approved=user_data.role == "admin",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user  # automatically serialized by FastAPI as UserRead


@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
) -> LoginResponse:
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not bcrypt.checkpw(
        form_data.password.encode("utf-8"),
        user.hashed_password.encode("utf-8"),
    ):
        logger.warning(f"Failed login attempt for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    now = int(time.time())  # Current Unix timestamp
    exp = now + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    payload = JWTPayload(
        user_id=user.id,
        role=user.role,
        iat=now,
        exp=exp,
        jti=uuid.uuid4(),
    )

    jwt_token = jwt.encode(
        claims=payload.model_dump(mode="json"),
        key=settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )

    session.add(JWTBlacklist(jti=payload.jti, iat=now, exp=exp))
    session.commit()

    logger.info(f"User {user.email} logged in successfully.")

    return LoginResponse(
        access_token=jwt_token,
        token_type="bearer",  # noqa: S106
    )


@router.post("/logout")
def logout(
    session: Annotated[Session, Depends(get_session)],
    jwt_token: Annotated[str, Depends(oauth2_scheme)],
) -> None:
    try:
        payload = jwt.decode(
            jwt_token,
            settings.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        jti = payload.get("jti")
        if not jti:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token: missing jti",
            )
        # Mark the token as blacklisted by updating its exp to now
        db_token = session.exec(select(JWTBlacklist).where(JWTBlacklist.jti == jti)).first()
        if db_token:
            db_token.exp = int(time.time())  # Invalidate immediately
            session.add(db_token)
            session.commit()
        else:
            # If not found, add to blacklist with immediate expiration
            session.add(JWTBlacklist(jti=jti, iat=payload.get("iat", 0), exp=int(time.time())))
            session.commit()
    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from err


@router.post("/change_password")
def change_password(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    password_data: UserChangePassword,
) -> None:
    # Verify old password
    if not bcrypt.checkpw(
        password_data.old_password.get_secret_value().encode("utf-8"),
        current_user.hashed_password.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid old password",
        )
    if not password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be provided",
        )
    hashed_pw = bcrypt.hashpw(
        password_data.new_password.get_secret_value().encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")
    current_user.hashed_password = hashed_pw
    session.add(current_user)
    session.commit()


@router.patch("/approve_user/{user_id}")
def approve_user(
    user_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can approve users",
        )
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user.is_approved = True
    session.add(user)
    session.commit()
