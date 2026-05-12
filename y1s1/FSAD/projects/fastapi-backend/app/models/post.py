import datetime
import uuid
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from app.models.feedback import Feedback
from app.models.media import Media
from app.models.user import UserRole

if TYPE_CHECKING:
    from app.models.user import User


class PostVisibility(str, Enum):
    # Business logic for post visibility
    # - Only students can create posts
    # - Admins can see all posts, regardless of visibility
    # - Teachers can see all posts except those marked ADMINS_ONLY
    # - Instructors can see posts marked TEACHERS_AND_INSTRUCTORS and below
    # - Students can see posts marked STUDENTS and PUBLIC

    # For hiding posts from everyone except admins
    # - Admin: True
    # - Everyone else: False
    ADMINS_ONLY = "admins_only"

    # - Admins: True
    # - Teachers: True
    # - Instructors: False
    # - Students: False
    # - Guests: False
    TEACHERS = "teachers"

    # - Admins: True
    # - Teachers: True
    # - Students: True
    # - Instructors: False
    # - Guests: False
    TEACHERS_AND_STUDENTS = "teachers_and_students"

    # For hiding posts from students and guests, might be useful for some cases
    # e.g. For auditing some posts that school staff might not want students to see
    # - Admins: True
    # - Teachers: True
    # - Students: False
    # - Instructors: True
    # - Guests: False
    TEACHERS_AND_INSTRUCTORS = "teachers_and_instructors"

    # Normal visibility for posts meant for all roles except guests
    # - Admins: True
    # - Teachers: True
    # - Students: True
    # - Instructors: True
    # - Guests: False
    NORMAL = "normal"

    # For posts visible to everyone, including guests
    GUEST = "guest"


VISIBILITY_ROLES = {
    PostVisibility.ADMINS_ONLY: {UserRole.admin},
    PostVisibility.TEACHERS: {UserRole.admin, UserRole.teacher},
    PostVisibility.TEACHERS_AND_INSTRUCTORS: {UserRole.admin, UserRole.teacher, UserRole.instructor},
    PostVisibility.TEACHERS_AND_STUDENTS: {UserRole.admin, UserRole.teacher, UserRole.student},
    PostVisibility.NORMAL: {UserRole.admin, UserRole.teacher, UserRole.student, UserRole.instructor},
    PostVisibility.GUEST: {UserRole.admin, UserRole.teacher, UserRole.student, UserRole.instructor, UserRole.guest},
}


class PostBase(SQLModel):
    title: str = Field(min_length=1, max_length=200, nullable=False)
    text_content: str = Field(min_length=1, max_length=500, nullable=False)
    visibility: PostVisibility = Field(default=PostVisibility.NORMAL, nullable=False)
    latitude: float | None = Field(default=None, nullable=True)
    longitude: float | None = Field(default=None, nullable=True)


class Post(PostBase, table=True):
    __tablename__ = "posts"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
    owner_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
    )
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )
    last_updated_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )
    last_updated_by_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
    )

    owner: "User" = Relationship(
        back_populates="posts",
        sa_relationship_kwargs={"foreign_keys": "Post.owner_id"},
    )
    last_updated_by_user: "User" = Relationship(
        back_populates="posts_updated",
        sa_relationship_kwargs={"foreign_keys": "Post.last_updated_by_id"},
    )
    media_items: list["Media"] = Relationship(
        back_populates="post",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    feedback_items: list["Feedback"] = Relationship(
        back_populates="post",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class PostResponse(PostBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime.datetime
    last_updated_at: datetime.datetime
    media_items: list["Media"] = []
    feedback_items: list["Feedback"] = []


PostResponse.model_rebuild()
