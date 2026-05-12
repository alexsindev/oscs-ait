import uuid
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel

from app.models.course import Course
from app.models.user import User


class EnrollmentStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"


class EnrollmentBase(SQLModel):
    status: EnrollmentStatus = Field(default=EnrollmentStatus.ACTIVE, nullable=False)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    course_id: uuid.UUID = Field(foreign_key="courses.id", nullable=False)


class Enrollment(EnrollmentBase, table=True):
    __tablename__ = "enrollments"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    user: "User" = Relationship(back_populates="enrollments")
    course: "Course" = Relationship(back_populates="enrollments")


class EnrollmentCreate(SQLModel):
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    course_id: uuid.UUID = Field(foreign_key="courses.id", nullable=False)


class EnrollmentRead(EnrollmentBase):
    id: uuid.UUID
    user: "User"
    course: "Course"


EnrollmentRead.model_rebuild()


class EnrollmentReadByUser(EnrollmentBase):
    id: uuid.UUID
    course: "Course"


EnrollmentReadByUser.model_rebuild()


class EnrollmentReadByCourse(EnrollmentBase):
    id: uuid.UUID
    user: "User"


EnrollmentReadByCourse.model_rebuild()


class EnrollmentUpdate(SQLModel):
    status: EnrollmentStatus
