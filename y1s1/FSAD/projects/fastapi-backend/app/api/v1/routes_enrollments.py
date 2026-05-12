import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlmodel import Session, select

from app.core.security import get_current_user
from app.db.session import get_session
from app.models.course import Course
from app.models.enrollment import (
    Enrollment,
    EnrollmentCreate,
    EnrollmentRead,
    EnrollmentReadByCourse,
    EnrollmentReadByUser,
    EnrollmentStatus,
    EnrollmentUpdate,
)
from app.models.user import User

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.get("/")
def list_enrollments(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Enrollment]:
    """Return all enrollments."""
    logger.debug(
        f"User {current_user.id} with role {current_user.role} listing all enrollments"
    )
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can view all enrollments",
        )
    return session.exec(select(Enrollment)).all()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_enrollment(
    enrollment_data: EnrollmentCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Enrollment:
    """Create a new enrollment for a user in a course."""
    logger.debug(
        f"User {current_user.id} with role {current_user.role} creating enrollment"
    )

    if current_user.role not in ("admin", "teacher", "student", "instructor"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins, teachers, students, and instructors can create enrollments",
        )

    if current_user.role in ("student", "instructor") and current_user.id != enrollment_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students and instructors can only create enrollments for themselves",
        )

    # Validate user and course existence
    user = session.get(User, enrollment_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    course = session.get(Course, enrollment_data.course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    # Prevent duplicate enrollment for same user/course
    existing = session.exec(
        select(Enrollment).where(
            Enrollment.user_id == enrollment_data.user_id,
            Enrollment.course_id == enrollment_data.course_id,
        ),
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enrollment already exists for this user and course",
        )

    enrollment = Enrollment(
        user_id=enrollment_data.user_id,
        course_id=enrollment_data.course_id,
        status=EnrollmentStatus.ACTIVE,  # default is also ACTIVE
    )
    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)
    return enrollment


@router.get("/{enrollment_id}")
def get_enrollment(
    enrollment_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> EnrollmentRead:
    """Get an enrollment by ID."""
    logger.debug(
        f"User {current_user.id} with role {current_user.role} retrieving enrollment ID {enrollment_id}"
    )
    if current_user.role == "guest":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guests cannot view enrollments",
        )
    enrollment = session.get(Enrollment, enrollment_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )
    logger.debug({"user": enrollment.user, "course": enrollment.course})
    return enrollment


@router.patch("/{enrollment_id}")
def update_enrollment(
    enrollment_id: uuid.UUID,
    enrollment_data: EnrollmentUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> EnrollmentRead:
    """Update an enrollment (currently only status)."""
    logger.debug(
        f"User {current_user.id} with role {current_user.role} updating enrollment ID {enrollment_id}"
    )
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can update enrollments status",
        )
    enrollment = session.get(Enrollment, enrollment_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )

    enrollment.status = enrollment_data.status

    session.add(enrollment)
    session.commit()
    session.refresh(enrollment)
    return enrollment


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(
    enrollment_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete an enrollment by ID."""
    logger.debug(
        f"User {current_user.id} with role {current_user.role} deleting enrollment ID {enrollment_id}"
    )
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can delete enrollments",
        )
    enrollment = session.get(Enrollment, enrollment_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found"
        )
    session.delete(enrollment)
    session.commit()


@router.get("/user/{user_id}")
def list_enrollments_by_user(
    user_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[EnrollmentReadByUser]:
    """List all enrollments for a specific user."""
    logger.debug(
        f"User {current_user.id} with role {current_user.role} listing enrollments for user ID {user_id}"
    )
    if current_user.role == "guest":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guests cannot view user enrollments",
        )
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Admin and teachers can view any user's enrollments
    # Other users can only view student enrollments (including their own)
    if current_user.role not in {"admin", "teacher"}:
        if user.role != "student":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enrollments can only be listed for student users",
            )

    return user.enrollments


@router.get("/course/{course_id}")
def list_enrollments_by_course(
    course_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[EnrollmentReadByCourse]:
    """List all enrollments for a specific course."""
    logger.debug(
        f"User {current_user.id} with role {current_user.role} listing enrollments for course ID {course_id}"
    )
    if current_user.role == "guest":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Guests cannot view course enrollments",
        )

    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course not found"
        )

    return course.enrollments
