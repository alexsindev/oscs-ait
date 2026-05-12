import datetime
import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.user import User


class FeedbackBase(SQLModel):
    post_id: uuid.UUID = Field(
        foreign_key="posts.id",
        nullable=False,
    )
    content: str = Field(max_length=1000, nullable=False)
    rating: int = Field(default=5, ge=1, le=5, nullable=False)  # Rating between 1 and 5


class Feedback(FeedbackBase, table=True):
    __tablename__ = "feedbacks"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
    created_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )
    teacher_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
    )
    teacher: "User" = Relationship(back_populates="feedback_given")
    post: "Post" = Relationship(back_populates="feedback_items")


class FeedbackCreate(FeedbackBase):
    pass
