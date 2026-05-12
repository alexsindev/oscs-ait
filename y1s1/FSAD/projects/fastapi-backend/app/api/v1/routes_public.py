from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.user import User, UserRead

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/user-profiles")
def list_public_user_profiles(
    session: Annotated[Session, Depends(get_session)],
) -> list[UserRead]:
    """
    Return all users who have user_profile data filled out.
    This is a public endpoint for the project info page.
    """
    users = session.exec(select(User)).all()
    # Load relationships and filter users with profiles
    users_with_profiles = []
    for user in users:
        _ = user.user_profile  # Load the user profile relationship
        if user.user_profile:
            users_with_profiles.append(user)
    return users_with_profiles
