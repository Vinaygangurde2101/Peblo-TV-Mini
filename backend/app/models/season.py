import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from app.db.base import Base
from app.models.show import ContentStatus

if TYPE_CHECKING:
    from app.models.show import Show
    from app.models.episode import Episode


class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    show_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("shows.id", ondelete="CASCADE"), nullable=False, index=True
    )
    season_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus), default=ContentStatus.DRAFT, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    show: Mapped["Show"] = relationship("Show", back_populates="seasons")
    episodes: Mapped[List["Episode"]] = relationship(
        "Episode", back_populates="season", cascade="all, delete-orphan", order_by="Episode.episode_number"
    )

    __table_args__ = (
        UniqueConstraint("show_id", "season_number", name="uq_seasons_show_season_number"),
    )

    def __repr__(self) -> str:
        return f"<Season show_id={self.show_id} season_number={self.season_number}>"
