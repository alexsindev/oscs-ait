import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlmodel import Session, select

from app.core.security import get_current_user
from app.db.session import get_session
from app.models.feedback import Feedback, FeedbackCreate
from app.models.post import VISIBILITY_ROLES, Post
from app.models.user import User

router = APIRouter(prefix="/feedbacks", tags=["feedbacks"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_feedback(
    feedback_data: FeedbackCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Feedback:
    """Create a new feedback entry.
    
    - All authenticated users (admin, teacher, instructor, student, guest) can provide feedback.
    - Post owners CAN provide feedback on their own posts (treated as replies to other feedback).
    """
    logger.debug(f"User {current_user.id} with role {current_user.role} creating feedback")
    
    # Get the post to check visibility
    post = session.get(Post, feedback_data.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    # Check if user can see the post (based on visibility)
    # Post owners always have access
    if post.owner_id != current_user.id:
        allowed_roles = VISIBILITY_ROLES.get(post.visibility, set())
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to provide feedback on this post",
            )

    feedback = Feedback(
        post_id=feedback_data.post_id,
        content=feedback_data.content,
        rating=feedback_data.rating,
        teacher_id=current_user.id,  # Note: field name is teacher_id but stores any user
    )
    session.add(feedback)
    session.commit()
    session.refresh(feedback)
    
    owner_status = "owner replying" if post.owner_id == current_user.id else "external feedback"
    logger.debug(f"Feedback {feedback.id} created by user {current_user.id} for post {feedback_data.post_id} ({owner_status})")
    return feedback


@router.get("/")
def list_all_feedbacks(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Feedback]:
    """Return all feedback entries."""
    logger.debug(f"User {current_user.id} with role {current_user.role} listing all feedbacks")
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can view all feedbacks",
        )
    return session.exec(select(Feedback)).all()


@router.get("/post/{post_id}")
def list_feedbacks_by_post(
    post_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Feedback]:
    """Return feedback entries for a specific post based on post visibility."""
    logger.debug(f"User {current_user.id} with role {current_user.role} listing feedbacks for post {post_id}")
    post = session.exec(select(Post).where(Post.id == post_id)).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if post.owner_id == current_user.id:
        logger.debug(f"Post owner {current_user.id} accessing feedbacks for their own post {post_id}")
        return post.feedback_items

    allowed_roles = VISIBILITY_ROLES.get(post.visibility, [])
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view feedbacks for this post",
        )

    return post.feedback_items


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(
    feedback_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Delete a feedback entry by ID."""
    logger.debug(f"User {current_user.id} with role {current_user.role} deleting feedback ID {feedback_id}")
    if current_user.role not in ("admin", "teacher"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and teachers can delete feedbacks",
        )

    feedback = session.get(Feedback, feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )

    session.delete(feedback)
    session.commit()
