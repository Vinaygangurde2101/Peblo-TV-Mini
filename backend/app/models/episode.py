import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, DateTime, Enum, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.db.base import Base
from app.models.show import ContentStatus

if TYPE_CHECKING:
    from app.models.season import Season


class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    season_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("seasons.id", ondelete="CASCADE"), nullable=False, index=True
    )
    episode_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    synopsis: Mapped[str] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)  # Nullable: triggers publish validation error
    content_group: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(50), nullable=False, default="English", index=True)
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus), default=ContentStatus.DRAFT, nullable=False, index=True
    )
    poster_url: Mapped[str] = mapped_column(String(512), nullable=True)
    banner_url: Mapped[str] = mapped_column(String(512), nullable=True)
    thumbnail_url: Mapped[str] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    season: Mapped["Season"] = relationship("Season", back_populates="episodes")

    __table_args__ = (
        UniqueConstraint("content_group", "language", name="uq_episodes_content_group_language"),
        Index("idx_episodes_group_lang", "content_group", "language"),
    )

    def __repr__(self) -> str:
        return f"<Episode title={self.title} group={self.content_group} lang={self.language}>"
