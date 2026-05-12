import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.course import Course


class CourseGroupBase(SQLModel):
    name: str = Field(min_length=1, max_length=100, nullable=False)
    description: str | None = Field(default=None, min_length=1, max_length=500, nullable=True)


class CourseGroup(CourseGroupBase, table=True):
    __tablename__ = "coursegroups"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
    courses: list["Course"] = Relationship(back_populates="course_group")


class CourseGroupCreate(CourseGroupBase):
    pass


class CourseGroupRead(CourseGroupBase):
    id: uuid.UUID


class CourseGroupUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=100, nullable=True)
    description: str | None = Field(default=None, max_length=500, nullable=True)
