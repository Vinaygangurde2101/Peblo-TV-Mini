from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.show import ContentStatus


class EpisodeBase(BaseModel):
    episode_number: int
    title: str
    synopsis: Optional[str] = None
    duration_seconds: Optional[int] = None
    content_group: str
    language: str = "English"
    status: ContentStatus = ContentStatus.DRAFT
    poster_url: Optional[str] = None
    banner_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class EpisodeCreate(EpisodeBase):
    season_id: str


class EpisodeUpdate(BaseModel):
    episode_number: Optional[int] = None
    title: Optional[str] = None
    synopsis: Optional[str] = None
    duration_seconds: Optional[int] = None
    content_group: Optional[str] = None
    language: Optional[str] = None
    status: Optional[ContentStatus] = None
    poster_url: Optional[str] = None
    banner_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class EpisodeResponse(EpisodeBase):
    id: str
    season_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
