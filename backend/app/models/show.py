import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.season import Season


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Show(Base):
    __tablename__ = "shows"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    synopsis: Mapped[str] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    section: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    status: Mapped[ContentStatus] = mapped_column(
        Enum(ContentStatus), default=ContentStatus.DRAFT, nullable=False, index=True
    )
    poster_url: Mapped[str] = mapped_column(String(512), nullable=True)
    banner_url: Mapped[str] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    seasons: Mapped[List["Season"]] = relationship(
        "Season", back_populates="show", cascade="all, delete-orphan", order_by="Season.season_number"
    )

    __table_args__ = (
        Index("idx_shows_section_category", "section", "category"),
    )

    def __repr__(self) -> str:
        return f"<Show title={self.title} status={self.status}>"
