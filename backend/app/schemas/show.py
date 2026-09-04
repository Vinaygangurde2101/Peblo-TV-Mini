from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.show import ContentStatus
from app.schemas.season import SeasonResponse
from app.schemas.episode import EpisodeResponse


class ShowBase(BaseModel):
    title: str
    synopsis: Optional[str] = None
    category: Optional[str] = None
    section: Optional[str] = None
    status: ContentStatus = ContentStatus.DRAFT
    poster_url: Optional[str] = None
    banner_url: Optional[str] = None


class ShowCreate(ShowBase):
    pass


class ShowUpdate(BaseModel):
    title: Optional[str] = None
    synopsis: Optional[str] = None
    category: Optional[str] = None
    section: Optional[str] = None
    status: Optional[ContentStatus] = None
    poster_url: Optional[str] = None
    banner_url: Optional[str] = None


class ShowResponse(ShowBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SeasonWithEpisodesResponse(SeasonResponse):
    episodes: List[EpisodeResponse] = []


class ShowDetailResponse(ShowResponse):
    seasons: List[SeasonWithEpisodesResponse] = []
