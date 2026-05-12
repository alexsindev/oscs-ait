import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class UserProfileBase(SQLModel):
    """
    Comprehensive user profile model containing personal information,
    goals, technical details, and humanizing information.
    """

    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        unique=True,  # ensures 1-to-1 relationship with User
    )

    # Personal Information
    profile_picture_url: str | None = Field(
        default=None,
        max_length=500,
        nullable=True,
        description="URL or path to the user's profile picture",
    )
    age: int | None = Field(
        default=None,
        ge=0,
        le=150,
        nullable=True,
        description="User's age",
    )
    occupation: str | None = Field(
        default=None,
        max_length=200,
        nullable=True,
        description="User's occupation or job title",
    )
    housing_situation: str | None = Field(
        default=None,
        max_length=200,
        nullable=True,
        description="User's housing situation (e.g., 'Own home', 'Renting', 'Living with family')",
    )
    income_range: str | None = Field(
        default=None,
        max_length=100,
        nullable=True,
        description="User's income range (e.g., '<20k', '20k-50k', '50k-100k', '>100k')",
    )

    # Goals and Questions
    short_term_goals: str | None = Field(
        default=None,
        max_length=1000,
        nullable=True,
        description="User's short-term goals relevant to the online community",
    )
    long_term_goals: str | None = Field(
        default=None,
        max_length=1000,
        nullable=True,
        description="User's long-term goals relevant to the online community",
    )
    immediate_questions: str | None = Field(
        default=None,
        max_length=1000,
        nullable=True,
        description="Immediate questions the user will bring to the site",
    )

    # Technical Information
    computer_equipment: str | None = Field(
        default=None,
        max_length=500,
        nullable=True,
        description="Computer equipment and devices in the user's house",
    )
    internet_connection: str | None = Field(
        default=None,
        max_length=200,
        nullable=True,
        description="Type and speed of internet connection (e.g., 'Fiber 100Mbps', 'DSL 10Mbps', 'Mobile 4G')",
    )

    # Humanizing Information
    bio: str | None = Field(
        default=None,
        max_length=1000,
        nullable=True,
        description="Short biography or about me section",
    )
    hobbies: str | None = Field(
        default=None,
        max_length=500,
        nullable=True,
        description="User's hobbies and recreational activities",
    )
    interests: str | None = Field(
        default=None,
        max_length=500,
        nullable=True,
        description="User's interests and passions",
    )
    additional_info: str | None = Field(
        default=None,
        max_length=1000,
        nullable=True,
        description="Any other information that will help humanize this person",
    )


class UserProfile(UserProfileBase, table=True):
    """User profile database table."""

    __tablename__ = "user_profiles"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    # Relationship back to User
    user: "User" = Relationship(back_populates="user_profile")


class UserProfileCreate(UserProfileBase):
    """Schema for creating a new user profile."""

    pass


class UserProfileRead(UserProfileBase):
    """Schema for reading user profile data."""

    id: uuid.UUID


class UserProfileUpdate(SQLModel):
    """
    Schema for updating user profile.
    All fields are optional to allow partial updates.
    """

    # Personal Information
    profile_picture_url: str | None = Field(default=None, max_length=500)
    age: int | None = Field(default=None, ge=0, le=150)
    occupation: str | None = Field(default=None, max_length=200)
    housing_situation: str | None = Field(default=None, max_length=200)
    income_range: str | None = Field(default=None, max_length=100)

    # Goals and Questions
    short_term_goals: str | None = Field(default=None, max_length=1000)
    long_term_goals: str | None = Field(default=None, max_length=1000)
    immediate_questions: str | None = Field(default=None, max_length=1000)

    # Technical Information
    computer_equipment: str | None = Field(default=None, max_length=500)
    internet_connection: str | None = Field(default=None, max_length=200)

    # Humanizing Information
    bio: str | None = Field(default=None, max_length=1000)
    hobbies: str | None = Field(default=None, max_length=500)
    interests: str | None = Field(default=None, max_length=500)
    additional_info: str | None = Field(default=None, max_length=1000)
