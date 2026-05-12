import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class StudentProfileBase(SQLModel):
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        unique=True,  # ensures 1-to-1
    )
    demographics: str | None = Field(default=None, min_length=1, max_length=500, nullable=True)
    matthayom_level: int = Field(ge=1, le=6, nullable=False)


class StudentProfile(StudentProfileBase, table=True):
    __tablename__ = "student_profiles"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )

    # Relationship back to User.
    # - Double quotes around "User" to avoid circular import issues.
    # - back_populates to link back to the User from StudentProfile.
    user: "User" = Relationship(back_populates="student_profile")


class StudentProfileCreate(StudentProfileBase):
    pass


class StudentProfileRead(StudentProfileBase):
    id: uuid.UUID


class StudentProfileUpdate(SQLModel):
    demographics: str | None = Field(default=None, min_length=1, max_length=500)
    matthayom_level: int | None = Field(default=None, ge=1, le=6)
