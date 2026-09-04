import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, Optional, Any

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class PublishStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"


class PublishRun(Base):
    __tablename__ = "publish_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    published_by_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[PublishStatus] = mapped_column(
        Enum(PublishStatus), nullable=False, index=True
    )
    show_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    episode_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    validation_errors: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    snapshot_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    published_by_user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="publish_runs"
    )

    def __repr__(self) -> str:
        return f"<PublishRun status={self.status} shows={self.show_count} episodes={self.episode_count}>"
