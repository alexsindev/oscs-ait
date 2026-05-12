import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.course_group import CourseGroup
    from app.models.enrollment import Enrollment
    from app.models.user import User


class CourseBase(SQLModel):
    name: str = Field(max_length=200, nullable=False)
    description: str | None = Field(
        default=None, min_length=1, max_length=1000, nullable=True
    )
    teacher_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    course_group_id: uuid.UUID = Field(foreign_key="coursegroups.id", nullable=False)


class Course(CourseBase, table=True):
    __tablename__ = "courses"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    teacher: "User" = Relationship(back_populates="courses_taught")
    course_group: "CourseGroup" = Relationship(back_populates="courses")
    enrollments: list["Enrollment"] = Relationship(
        back_populates="course",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class CourseCreate(CourseBase):
    pass


class CourseRead(CourseBase):
    id: uuid.UUID


class CourseUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=200, nullable=True)
    description: str | None = Field(default=None, max_length=1000, nullable=True)
    course_group_id: uuid.UUID | None = Field(default=None, nullable=True)
