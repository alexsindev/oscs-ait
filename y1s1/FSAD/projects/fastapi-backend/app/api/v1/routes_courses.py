import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlmodel import Session, select

from app.core.security import get_current_user
from app.db.session import get_session
from app.models.course import Course, CourseCreate, CourseRead, CourseUpdate
from app.models.course_group import CourseGroup, CourseGroupCreate, CourseGroupRead, CourseGroupUpdate
from app.models.user import User

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/")
def list_courses(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Course]:
    """Return all courses."""
    logger.debug(f"User {current_user.id} with role {current_user.role} requesting list of all courses")
    # Anyone logged in can view the list of courses
    return session.exec(select(Course)).all()


@router.get("/teacher/me")
def list_my_courses_as_teacher(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Course]:
    """Return courses created by the current teacher."""
    logger.debug(f"User {current_user.id} with role {current_user.role} requesting their own courses")
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can access this endpoint",
        )
    
    courses = session.exec(select(Course).where(Course.teacher_id == current_user.id)).all()
    logger.debug(f"Found {len(courses)} courses for teacher {current_user.id}")
    return courses


@router.get("/groups")
def list_course_groups(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[CourseGroup]:
    """Return all course groups."""
    logger.debug(f"User {current_user.id} with role {current_user.role} requesting list of all course groups")
    # Anyone logged in can view the list of course groups
    return session.exec(select(CourseGroup)).all()


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Course:
    """Create a new course and automatically enroll the creating teacher."""
    from app.models.enrollment import Enrollment, EnrollmentStatus
    
    logger.debug(f"User {current_user.id} with role {current_user.role} creating a new course")
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can create courses",
        )

    db_course = session.exec(select(Course).where(Course.name == course_data.name)).first()
    if db_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course with this name already exists",
        )

    # Verify course group exists
    course_group = session.get(CourseGroup, course_data.course_group_id)
    if not course_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course group not found",
        )

    # Verify teacher exists
    teacher = session.get(User, course_data.teacher_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found",
        )

    # Create course
    course = Course(
        name=course_data.name,
        description=course_data.description,
        teacher_id=course_data.teacher_id,
        course_group_id=course_data.course_group_id,
    )
    session.add(course)
    session.flush()  # Flush to get course.id for enrollment
    
    # Automatically enroll the teacher in their own course
    enrollment = Enrollment(
        user_id=course_data.teacher_id,
        course_id=course.id,
        status=EnrollmentStatus.ACTIVE,
    )
    session.add(enrollment)
    logger.debug(f"Auto-enrolled teacher {course_data.teacher_id} in course {course.id}")
    
    session.commit()
    session.refresh(course)
    return course


@router.post("/groups", status_code=status.HTTP_201_CREATED)
def create_course_group(
    course_group_data: CourseGroupCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CourseGroup:
    """Create a new course group."""
    logger.debug(f"User {current_user.id} with role {current_user.role} creating a new course group")
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can create course groups",
        )

    db_course_group = session.exec(select(CourseGroup).where(CourseGroup.name == course_group_data.name)).first()
    if db_course_group:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course group with this name already exists",
        )
    course_group = CourseGroup(
        name=course_group_data.name,
        description=course_group_data.description,
    )
    session.add(course_group)
    session.commit()
    session.refresh(course_group)
    return course_group


@router.get("/{course_id}")
def get_course(
    course_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CourseRead:
    """Get a course by ID."""
    logger.debug(f"User {current_user.id} with role {current_user.role} requesting course ID {course_id}")
    # Anyone logged in can view course details
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    return course


@router.get("/groups/{course_group_id}")
def get_course_group(
    course_group_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CourseGroupRead:
    """Get a course group by ID."""
    logger.debug(f"User {current_user.id} with role {current_user.role} requesting course group ID {course_group_id}")
    # Anyone logged in can view course group details
    course_group = session.get(CourseGroup, course_group_id)
    if not course_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course group not found",
        )
    return course_group


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a course by ID. Teachers can only delete their own courses, admins can delete any."""
    logger.debug(f"User {current_user.id} with role {current_user.role} deleting course ID {course_id}")
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can delete courses",
        )
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    
    # Teachers can only delete their own courses
    if current_user.role == "teacher" and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teachers can only delete courses they created",
        )
    
    session.delete(course)
    session.commit()


@router.delete("/groups/{course_group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course_group(
    course_group_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a course group by ID."""
    logger.debug(f"User {current_user.id} with role {current_user.role} deleting course group ID {course_group_id}")
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can delete course groups",
        )

    course_group = session.get(CourseGroup, course_group_id)
    if not course_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course group not found",
        )

    # Check if course group has courses - cannot delete if it does
    if course_group.courses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete course group that still has courses assigned to it",
        )

    session.delete(course_group)
    session.commit()


@router.get("/groups/{course_group_id}/courses")
def list_courses_in_group(
    course_group_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[CourseRead]:
    """Return all courses in a specific course group."""
    logger.debug(
        f"User {current_user.id} with role {current_user.role} requesting courses in group ID {course_group_id}",
    )
    # Anyone logged in can view the courses in a course group

    course_group = session.get(CourseGroup, course_group_id)
    if not course_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course group not found",
        )
    return course_group.courses


@router.patch("/{course_id}")
def update_course(
    course_id: uuid.UUID,
    course_data: CourseUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CourseRead:
    """Update a course by ID. Teachers can only update their own courses, admins can update any."""
    logger.debug(f"User {current_user.id} with role {current_user.role} updating course ID {course_id}")
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can update courses",
        )

    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    
    # Teachers can only update their own courses
    if current_user.role == "teacher" and course.teacher_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teachers can only update courses they created",
        )
    
    if course_data.name is not None:
        course.name = course_data.name
    if course_data.description is not None:
        course.description = course_data.description
    if course_data.course_group_id is not None:
        course.course_group_id = course_data.course_group_id
    session.add(course)
    session.commit()
    session.refresh(course)
    return course


@router.patch("/groups/{course_group_id}")
def update_course_group(
    course_group_id: uuid.UUID,
    course_group_data: CourseGroupUpdate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CourseGroupRead:
    """Update a course group by ID."""
    logger.debug(f"User {current_user.id} with role {current_user.role} updating course group ID {course_group_id}")
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can update course groups",
        )

    course_group = session.get(CourseGroup, course_group_id)
    if not course_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course group not found",
        )
    if course_group_data.name is not None:
        course_group.name = course_group_data.name
    if course_group_data.description is not None:
        course_group.description = course_group_data.description
    session.add(course_group)
    session.commit()
    session.refresh(course_group)
    return course_group
