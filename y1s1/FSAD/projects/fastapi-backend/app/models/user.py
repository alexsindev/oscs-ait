import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import EmailStr, SecretStr
from sqlmodel import Field, Relationship, SQLModel

from app.models.student_profile import StudentProfile
from app.models.user_profile import UserProfile

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.enrollment import Enrollment
    from app.models.feedback import Feedback
    from app.models.post import Post


class UserRole(str, Enum):
    admin = "admin"  # Admin is the highest role, only assigned school staff
    teacher = "teacher"  # Teachers of the school
    student = "student"  # Students of the school
    instructor = "instructor"  # External instructors for extracurriculars
    guest = "guest"  # Limited access users, e.g., parents, locals, auditors


class UserBase(SQLModel):
    # All nullable=False to enforce NOT NULL constraints in the DB.

    # Basic name fields with length limits.
    # - min_length was REMOVED because SQLAlchemy (via SQLModel.Field) does not enforce it.
    #   Validation of non-empty values is handled at the Pydantic request schema level instead.
    # - max_length remains to generate a VARCHAR(100) constraint in the database.
    first_name: str = Field(min_length=1, max_length=100, nullable=False)
    last_name: str = Field(min_length=1, max_length=100, nullable=False)

    # Email field.
    # - 'unique=True' already creates a unique index in PostgreSQL.
    #   The earlier 'index=True' was REMOVED because it would create a second, redundant index.
    # - max_length keeps VARCHAR(100) constraint.
    email: EmailStr = Field(min_length=1, max_length=100, nullable=False)

    # Role field.
    # - Uses Enum instead of Literal so PostgreSQL can enforce valid values.
    # - Default role is 'guest' for new users.
    role: UserRole = Field(default=UserRole.guest, nullable=False)


class User(UserBase, table=True):
    __tablename__ = "users"
    # Primary key field.
    # - Uses Python uuid.UUID type for type safety and Pydantic validation.
    # - default_factory=uuid.uuid4 ensures a new UUID is generated automatically in Python.
    # - 'index=True' was REMOVED because primary keys are automatically indexed by PostgreSQL.
    # - nullable=False is implicit for primary keys.
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    # Hashed password field.
    # - Length 255 allows for bcrypt or Argon2 hash strings safely.
    # - The plain-text password field was intentionally removed; only store hashed passwords.
    hashed_password: str = Field(max_length=255, nullable=False)

    # Approved field.
    # - Indicates if the user account is approved by an admin to prevent misuse.
    # - Default is False for new registrations.
    is_approved: bool = Field(default=False, nullable=False)

    # Created at timestamp.
    # - Records when the user account was created.
    # - Uses UTC timezone for consistency.
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationship to StudentProfile.
    # - Double quotes around "StudentProfile" to avoid circular import issues.
    # - Optional relationship; not all users have a student profile.
    # - back_populates to link back to the User from StudentProfile.
    # - uselist=False indicates a one-to-one relationship.
    student_profile: Optional["StudentProfile"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    # Relationship to UserProfile.
    # - Optional relationship; not all users have a comprehensive profile.
    # - One-to-one relationship with cascade delete.
    user_profile: Optional["UserProfile"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    posts: list["Post"] = Relationship(
        back_populates="owner",
        sa_relationship_kwargs={"foreign_keys": "Post.owner_id"},
    )
    posts_updated: list["Post"] = Relationship(
        back_populates="last_updated_by_user",
        sa_relationship_kwargs={"foreign_keys": "Post.last_updated_by_id"},
    )
    feedback_given: list["Feedback"] = Relationship(back_populates="teacher")
    courses_taught: list["Course"] = Relationship(back_populates="teacher")
    enrollments: list["Enrollment"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    # Plain-text password for user creation only.
    password: SecretStr = Field(min_length=8, max_length=100)


class UserRead(UserBase):
    id: uuid.UUID
    student_profile: Optional["StudentProfile"] = None
    user_profile: Optional["UserProfile"] = None
    is_approved: bool
    created_at: datetime
    # Exclude hashed_password from read model for security.


UserRead.model_rebuild()


class UserUpdate(SQLModel):
    # In Pydantic v2, Optional and default=None are required to make fields optional.
    # This allows partial updates where only some fields are provided.
    # https://docs.pydantic.dev/2.0/migration/#required-optional-and-nullable-fields
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, min_length=1, max_length=100)


class UserChangePassword(SQLModel):
    old_password: SecretStr = Field(min_length=8, max_length=100)
    new_password: SecretStr = Field(min_length=8, max_length=100)
