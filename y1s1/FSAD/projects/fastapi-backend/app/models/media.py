import datetime
import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.post import Post


class MediaBase(SQLModel):
    media_url: str = Field(min_length=1, max_length=255, nullable=False)
    media_type: str = Field(min_length=1, max_length=50, nullable=False)  # e.g., 'image', 'video'
    uploaded_at: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False,
    )
    post_id: uuid.UUID = Field(
        foreign_key="posts.id",
        nullable=False,
    )


class Media(MediaBase, table=True):
    __tablename__ = "media"
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
    )
    post: "Post" = Relationship(back_populates="media_items")
