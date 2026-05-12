import datetime
import shutil
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from loguru import logger
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_session
from app.models.media import Media
from app.models.post import VISIBILITY_ROLES, Post, PostResponse, PostVisibility
from app.models.user import User

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/")
def list_posts(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Post]:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can list all posts",
        )
    return session.exec(select(Post)).all()


@router.get("/course/{course_id}")
def list_posts_by_course(
    course_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[PostResponse]:
    """Return all posts for students enrolled in a course, filtered by visibility.
    
    - Returns posts from all students enrolled in the course
    - Filtered based on current user's role and visibility permissions
    - Includes media_items and feedback_items for each post
    """
    from app.models.enrollment import Enrollment
    from app.models.course import Course
    
    logger.debug(f"User {current_user.id} ({current_user.role}) requesting posts for course {course_id}")
    
    # Verify course exists
    course = session.get(Course, course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    
    # Get all enrolled students in this course
    enrollments = session.exec(
        select(Enrollment).where(Enrollment.course_id == course_id)
    ).all()
    
    enrolled_user_ids = [e.user_id for e in enrollments]
    
    if not enrolled_user_ids:
        logger.debug(f"No students enrolled in course {course_id}")
        return []
    
    # Get all posts by enrolled students
    all_posts = session.exec(
        select(Post).where(Post.owner_id.in_(enrolled_user_ids))
    ).all()
    
    # Filter posts based on current user's role and visibility
    visible_posts = []
    
    for post in all_posts:
        # Owner always sees their own posts
        if post.owner_id == current_user.id:
            _ = post.media_items  # Eager load
            _ = post.feedback_items
            visible_posts.append(post)
            continue
        
        # Admin sees everything
        if current_user.role == "admin":
            _ = post.media_items
            _ = post.feedback_items
            visible_posts.append(post)
            continue
        
        # Check visibility based on role
        allowed_roles = VISIBILITY_ROLES.get(post.visibility, set())
        if current_user.role in allowed_roles:
            _ = post.media_items
            _ = post.feedback_items
            visible_posts.append(post)
    
    logger.debug(
        f"User {current_user.id} retrieved {len(visible_posts)} out of {len(all_posts)} posts for course {course_id}"
    )
    return visible_posts


@router.get("/user/{user_id}")
def list_posts_by_user(
    user_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[Post]:
    """Return all posts of a given user, filtered by the current user's visibility permissions."""
    logger.debug(f"User {current_user.id} ({current_user.role}) requesting posts of user {user_id}")

    # Admins can see everything
    if current_user.role == "admin":
        posts = session.exec(select(Post).where(Post.owner_id == user_id)).all()
        logger.debug(f"Admin {current_user.id} retrieved all posts for user {user_id}")
        return posts

    # Owners can see all their own posts
    if current_user.id == user_id:
        posts = session.exec(select(Post).where(Post.owner_id == user_id)).all()
        logger.debug(f"Owner {current_user.id} retrieved all their own posts")
        return posts

    # All other roles: filter posts by visibility mapping
    visible_visibilities = [visibility for visibility, roles in VISIBILITY_ROLES.items() if current_user.role in roles]

    posts = session.exec(
        select(Post).where(
            Post.owner_id == user_id,
            Post.visibility.in_(visible_visibilities),
        ),
    ).all()

    logger.debug(f"User {current_user.id} retrieved {len(posts)} posts for user {user_id}")
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post(  # noqa: PLR0913
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    title: Annotated[str, Form(min_length=1)],
    text_content: Annotated[str, Form(min_length=1)],
    visibility: Annotated[PostVisibility, Form()] = PostVisibility.NORMAL,
    latitude: Annotated[float | None, Form()] = None,
    longitude: Annotated[float | None, Form()] = None,
    files: Annotated[list[UploadFile] | None, File()] = None,
) -> PostResponse:
    logger.debug(f"User {current_user.id} with role {current_user.role} creating a post")
    if current_user.role not in {"admin", "student"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and students can create posts",
        )

    # Only admins can create posts with admins_only visibility
    if visibility == PostVisibility.ADMINS_ONLY and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create posts with admins_only visibility",
        )

    post = Post(
        id=uuid.uuid4(),  # Explicitly generate UUID before adding to session
        owner_id=current_user.id,
        title=title,
        text_content=text_content,
        visibility=visibility,
        latitude=latitude,
        longitude=longitude,
        last_updated_by_id=current_user.id,
        # created_at and last_updated_at will be set automatically to current time
    )

    session.add(post)
    session.flush()  # Flush to ensure post is in database before creating media items

    saved_media_items = []
    if files:
        post_upload_dir = f"{settings.UPLOAD_DIRECTORY}/{post.id}"

        # parents=True to create any necessary parent directories until the target directory
        # exist_ok=True to avoid error if the directory already exists
        Path(post_upload_dir).mkdir(parents=True, exist_ok=True)

        for i, upload_file in enumerate(files):
            file_extension = Path(upload_file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = str(Path(post_upload_dir) / unique_filename)

            with Path(file_path).open("wb") as out_file:
                content = upload_file.file.read()
                out_file.write(content)
                logger.debug(f"{i + 1}/{len(files)} Saved uploaded file to {file_path}")

            media_item = Media(
                id=uuid.uuid4(),
                media_url=file_path,
                media_type=upload_file.content_type,
                post_id=post.id,
                # uploaded_at will be set automatically to current time
            )
            session.add(media_item)
            saved_media_items.append(media_item)

    session.commit()
    session.refresh(post)
    post.media_items = saved_media_items
    return post


@router.get("/{post_id}")
def get_post(
    post_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PostResponse:
    """Return a single post if visible to the current user."""
    logger.debug(f"User {current_user.id} ({current_user.role}) requesting post {post_id}")

    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Owner always has access
    if post.owner_id == current_user.id:
        logger.debug(f"Owner {current_user.id} accessing their own post {post_id}")
        _ = post.media_items
        _ = post.feedback_items
        return post

    # Check visibility permissions
    allowed_roles = VISIBILITY_ROLES.get(post.visibility, set())
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this post",
        )

    # Lazy-load related content
    _ = post.media_items
    _ = post.feedback_items
    logger.debug(f"User {current_user.id} authorized to access post {post_id}")
    return post


@router.patch("/{post_id}/visibility", status_code=status.HTTP_200_OK)
def update_post_visibility(
    post_id: uuid.UUID,
    visibility: PostVisibility,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PostResponse:
    """Update the visibility of a post.

    - Admin and Teacher: Can update any post's visibility to anything (except only admin can set admins_only)
    - Student: Can only update their own post's visibility (except admins_only)
    """
    logger.debug(
        f"User {current_user.id} with role {current_user.role} updating visibility of post {post_id} to {visibility}",
    )

    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Check permissions
    if current_user.role not in {"admin", "teacher", "student"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update post visibility",
        )

    # Students can only update their own posts
    if current_user.role == "student" and post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students can only update their own posts",
        )

    # Only admins can set admins_only visibility
    if visibility == PostVisibility.ADMINS_ONLY and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can set admins_only visibility",
        )

    post.visibility = visibility
    post.last_updated_at = datetime.datetime.now(datetime.UTC)
    post.last_updated_by_id = current_user.id
    session.add(post)
    session.commit()
    session.refresh(post)

    logger.debug(f"Post {post_id} visibility updated to {visibility} by user {current_user.id}")
    return post


@router.patch("/{post_id}/content", status_code=status.HTTP_200_OK)
def update_post_content(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    post_id: uuid.UUID,
    title: Annotated[str | None, Form()] = None,
    text_content: Annotated[str | None, Form()] = None,
    files: Annotated[list[UploadFile] | None, File()] = None,
    remove_media_ids: Annotated[str | None, Form()] = None,  # Comma-separated media IDs to remove
) -> PostResponse:
    """Update the title, text content, and/or attachments of a post.

    - Admin and Teacher: Can update any post's content and attachments.
    - Student: Can only update their own post's content and attachments.
    - files: New files to attach to the post
    - remove_media_ids: Comma-separated list of media IDs to remove (e.g., "id1,id2,id3")
    """
    logger.debug(
        f"User {current_user.id} with role {current_user.role} updating content of post {post_id}",
    )

    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Check permissions
    if current_user.role not in {"admin", "teacher", "student"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update post content",
        )

    # Students can only update their own posts
    if current_user.role == "student" and post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students can only update their own posts",
        )

    # Update text content
    if title is not None:
        post.title = title
    if text_content is not None:
        post.text_content = text_content

    # Remove specified media items
    if remove_media_ids:
        media_ids_to_remove = [mid.strip() for mid in remove_media_ids.split(",") if mid.strip()]
        for media_id_str in media_ids_to_remove:
            try:
                media_id = uuid.UUID(media_id_str)
                media = session.get(Media, media_id)
                if media and media.post_id == post_id:
                    # Delete physical file
                    media_file_path = Path(media.media_url)
                    if media_file_path.exists():
                        media_file_path.unlink()
                        logger.debug(f"Deleted media file: {media_file_path}")
                    # Delete from database
                    session.delete(media)
                    logger.debug(f"Removed media {media_id} from post {post_id}")
            except ValueError:
                logger.warning(f"Invalid media ID format: {media_id_str}")
                continue

    # Add new media items
    if files:
        post_upload_dir = f"{settings.UPLOAD_DIRECTORY}/{post.id}"
        Path(post_upload_dir).mkdir(parents=True, exist_ok=True)

        for i, upload_file in enumerate(files):
            file_extension = Path(upload_file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = str(Path(post_upload_dir) / unique_filename)

            with Path(file_path).open("wb") as out_file:
                content = upload_file.file.read()
                out_file.write(content)
                logger.debug(f"{i + 1}/{len(files)} Saved uploaded file to {file_path}")

            media_item = Media(
                id=uuid.uuid4(),
                media_url=file_path,
                media_type=upload_file.content_type,
                post_id=post.id,
            )
            session.add(media_item)
            logger.debug(f"Added new media {media_item.id} to post {post_id}")

    post.last_updated_at = datetime.datetime.now(datetime.UTC)
    post.last_updated_by_id = current_user.id
    session.add(post)
    session.commit()
    session.refresh(post)

    # Ensure media_items are loaded
    _ = post.media_items

    logger.debug(f"Post {post_id} content and attachments updated by user {current_user.id}")
    return post


@router.delete("/{post_id}/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_media(
    post_id: uuid.UUID,
    media_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    logger.debug(f"User {current_user.id} with role {current_user.role} requesting deletion of media ID {media_id}")
    media = session.get(Media, media_id)
    if not media or media.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found for the specified post",
        )

    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if current_user.role not in {"admin", "teacher", "student"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this media",
        )

    if current_user.role == "student" and post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students can only delete media from their own posts",
        )

    # Delete physical media file from filesystem before deleting from database
    media_file_path = Path(media.media_url)
    if media_file_path.exists():
        media_file_path.unlink()
        logger.debug(f"Deleted media file: {media_file_path}")

    post.last_updated_at = datetime.datetime.now(datetime.UTC)
    post.last_updated_by_id = current_user.id
    session.delete(media)
    session.add(post)
    session.commit()
    logger.debug(f"Media {media_id} deleted by user {current_user.id}")


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    logger.debug(f"User {current_user.id} with role {current_user.role} requesting deletion of post ID {post_id}")
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    if current_user.role not in {"admin", "teacher", "student"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )

    if current_user.role == "student" and post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students can only delete their own posts",
        )

    # Delete physical media files from filesystem before deleting from database
    post_upload_dir = Path(f"{settings.UPLOAD_DIRECTORY}/{post_id}")
    if post_upload_dir.exists():
        shutil.rmtree(post_upload_dir)
        logger.debug(f"Deleted media directory: {post_upload_dir}")

    session.delete(post)
    session.commit()
    logger.debug(f"Post {post_id} deleted by user {current_user.id}")


@router.get("/media/{media_id}")
def get_media(
    media_id: uuid.UUID,
    session: Annotated[Session, Depends(get_session)],
) -> FileResponse:
    """Return media file without authentication (public access)."""
    logger.debug(f"Public access request for media {media_id}")

    media = session.get(Media, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    logger.debug(f"Serving media file: {media.media_url}")
    return FileResponse(media.media_url)
