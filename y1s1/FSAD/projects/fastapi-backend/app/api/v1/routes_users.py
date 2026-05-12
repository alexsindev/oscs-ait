import os
import shutil
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from loguru import logger
from sqlmodel import Session, select

from app.core.security import get_current_user
from app.db.session import get_session
from app.models.student_profile import (
    StudentProfile,
    StudentProfileCreate,
    StudentProfileRead,
    StudentProfileUpdate,
)
from app.models.user import User, UserRead, UserUpdate
from app.models.user_profile import (
    UserProfile,
    UserProfileCreate,
    UserProfileRead,
    UserProfileUpdate,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def list_users(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[UserRead]:
    """Return all users."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested list of all users"
    )
    # if current_user.role not in {"admin", "teacher"}:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not authorized to view all users",
    #     )
    users = session.exec(select(User)).all()
    for user in users:
        _ = user.student_profile  # Load the student profile relationship
        _ = user.user_profile  # Load the user profile relationship
    return users


@router.get("/me")
def read_current_user(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    """Get the currently authenticated user."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested their own details"
    )
    user = session.get(User, current_user.id)
    _ = user.student_profile  # Load the student profile relationship
    _ = user.user_profile  # Load the user profile relationship
    return user


@router.get("/student_profiles")
def list_student_profiles(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[StudentProfile]:
    """Return all student profiles."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested list of all student profiles"
    )
    if current_user.role not in {"admin", "teacher"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view all student profiles",
        )
    return session.exec(select(StudentProfile)).all()


@router.get("/{user_id}")
def get_user(
    user_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    """Get a user by ID."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested details for user ID {user_id}"
    )
    # Everyone can get user details of other users except Guests can only get their own details
    if current_user.role == "guest" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guests can only view their own user details",
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    _ = user.student_profile  # Load the student profile relationship
    _ = user.user_profile  # Load the user profile relationship

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a user by ID."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested deletion of user ID {user_id}"
    )
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete users",
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    session.delete(user)
    session.commit()


@router.post("/student_profiles", status_code=status.HTTP_201_CREATED)
def create_student_profile(
    profile_data: StudentProfileCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> StudentProfile:
    """Create a new student profile."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested creation of a student profile"
    )
    if current_user.role not in {"admin", "teacher", "student"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins, teachers, or students can create student profiles",
        )

    if current_user.role == "student" and current_user.id != profile_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students can only create their own student profiles",
        )

    db_profile = session.exec(
        select(StudentProfile).where(StudentProfile.user_id == profile_data.user_id)
    ).first()
    if db_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student profile already exists for this user",
        )

    target_user = session.get(User, profile_data.user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found for the given user_id",
        )

    profile = StudentProfile(
        user_id=target_user.id,
        demographics=profile_data.demographics,
        matthayom_level=profile_data.matthayom_level,
    )
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@router.get("/student_profiles/{profile_id}")
def get_student_profile(
    profile_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> StudentProfile:
    """Get a student profile by ID."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested student profile ID {profile_id}"
    )
    if current_user.role not in {"admin", "teacher", "student"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins, teachers, and students can view student profiles",
        )

    profile = session.get(StudentProfile, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    if current_user.role == "student" and profile.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students can only view their own student profiles",
        )

    return profile


@router.delete("/student_profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student_profile(
    profile_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a student profile by ID."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested deletion of studentprofile ID {profile_id}",
    )
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete student profiles",
        )

    profile = session.get(StudentProfile, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    session.delete(profile)
    session.commit()


@router.patch("/{user_id}")
def update_user(
    user_id: uuid.UUID,
    updated_data: UserUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    """Update a user's information."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested update of user ID {user_id}"
    )
    # Only admin can update other users; users can update themselves
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update other users",
        )
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user.first_name = updated_data.first_name or user.first_name
    user.last_name = updated_data.last_name or user.last_name
    user.email = updated_data.email or user.email
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.patch("/student_profiles/{profile_id}")
def update_student_profile(
    profile_id: uuid.UUID,
    updated_data: StudentProfileUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> StudentProfileRead:
    """Update a student profile's information."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested update of student profile ID {profile_id}",
    )
    # Only admins, teachers can update any profile; students can update their own profile
    if current_user.role not in {"admin", "teacher", "student"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins, teachers, or students can update student profiles",
        )
    if current_user.role == "student":
        profile = session.get(StudentProfile, profile_id)
        if not profile or profile.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students can only update their own student profiles",
            )

    profile = session.get(StudentProfile, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    profile.demographics = updated_data.demographics or profile.demographics
    profile.matthayom_level = updated_data.matthayom_level or profile.matthayom_level

    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


# ========== User Profile Endpoints ==========


@router.get("/user_profiles")
def list_user_profiles(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[UserProfile]:
    """Return all user profiles."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested list of all user profiles"
    )
    if current_user.role not in {"admin", "teacher"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view all user profiles",
        )
    return session.exec(select(UserProfile)).all()


@router.post("/user_profiles", status_code=status.HTTP_201_CREATED)
def create_user_profile(
    profile_data: UserProfileCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserProfile:
    """Create a new user profile."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested creation of a user profile"
    )

    # Users can create their own profiles; admins and teachers can create any profile
    if (
        current_user.role not in {"admin", "teacher"}
        and current_user.id != profile_data.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create your own user profile",
        )

    # Check if profile already exists
    db_profile = session.exec(
        select(UserProfile).where(UserProfile.user_id == profile_data.user_id)
    ).first()
    if db_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User profile already exists for this user",
        )

    # Verify the target user exists
    target_user = session.get(User, profile_data.user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found for the given user_id",
        )

    # Create the profile
    profile = UserProfile(**profile_data.model_dump())
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@router.get("/user_profiles/{profile_id}")
def get_user_profile(
    profile_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserProfile:
    """Get a user profile by ID."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested user profile ID {profile_id}"
    )

    profile = session.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    # Users can view their own profiles; admins and teachers can view any profile
    if (
        current_user.role not in {"admin", "teacher"}
        and profile.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own user profile",
        )

    return profile


@router.patch("/user_profiles/{profile_id}")
def update_user_profile(
    profile_id: uuid.UUID,
    updated_data: UserProfileUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserProfileRead:
    """Update a user profile's information."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested update of user profile ID {profile_id}",
    )

    profile = session.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    # Users can update their own profiles; admins and teachers can update any profile
    if (
        current_user.role not in {"admin", "teacher"}
        and profile.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own user profile",
        )

    # Update only the fields that were provided
    update_dict = updated_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(profile, field, value)

    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


@router.delete("/user_profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_profile(
    profile_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a user profile by ID."""
    logger.debug(
        f"User {current_user.email} with role {current_user.role} requested deletion of user profile ID {profile_id}",
    )
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete user profiles",
        )

    profile = session.get(UserProfile, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )
    session.delete(profile)
    session.commit()


# Profile Picture Upload
UPLOAD_DIR = Path("uploads/profile_pictures")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/profile-picture/upload")
async def upload_profile_picture(
    file: Annotated[UploadFile, File(...)],
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Upload a profile picture for the current user."""
    logger.debug(f"User {current_user.email} uploading profile picture")

    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read file content
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB",
        )

    # Generate unique filename
    unique_filename = f"{current_user.id}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    # Delete old profile picture if exists
    if file_path.exists():
        file_path.unlink()

    # Save the file
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    # Update user profile with the new picture URL
    profile_url = f"/api/v1/users/profile-pictures/{unique_filename}"

    # Get or create user profile
    user_profile = session.exec(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    ).first()

    if user_profile:
        user_profile.profile_picture_url = profile_url
        session.add(user_profile)
    else:
        # Create a new profile with just the picture URL
        new_profile = UserProfile(
            user_id=current_user.id,
            profile_picture_url=profile_url,
        )
        session.add(new_profile)

    session.commit()

    logger.info(
        f"Profile picture uploaded for user {current_user.email}: {unique_filename}"
    )
    return {
        "message": "Profile picture uploaded successfully",
        "url": profile_url,
        "filename": unique_filename,
    }


@router.get("/profile-pictures/{filename}")
async def get_profile_picture(filename: str) -> FileResponse:
    """Serve a profile picture."""
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile picture not found",
        )

    return FileResponse(file_path)


@router.delete("/profile-picture")
async def delete_profile_picture(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Delete the current user's profile picture."""
    logger.debug(f"User {current_user.email} deleting profile picture")

    # Get user profile
    user_profile = session.exec(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    ).first()

    if not user_profile or not user_profile.profile_picture_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profile picture found",
        )

    # Delete the file
    unique_filename = (
        f"{current_user.id}" + Path(user_profile.profile_picture_url).suffix
    )
    file_path = UPLOAD_DIR / unique_filename
    if file_path.exists():
        file_path.unlink()

    # Remove URL from profile
    user_profile.profile_picture_url = None
    session.add(user_profile)
    session.commit()

    logger.info(f"Profile picture deleted for user {current_user.email}")
    return {"message": "Profile picture deleted successfully"}
