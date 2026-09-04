import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, TYPE_CHECKING

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.publish_run import PublishRun


class UserRole(str, enum.Enum):
    EDITOR = "editor"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.EDITOR, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    publish_runs: Mapped[List["PublishRun"]] = relationship(
        "PublishRun", back_populates="published_by_user"
    )

    def __repr__(self) -> str:
        return f"<User email={self.email} role={self.role}>"
