from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.show import ContentStatus


class SeasonBase(BaseModel):
    season_number: int
    title: Optional[str] = None
    status: ContentStatus = ContentStatus.DRAFT


class SeasonCreate(SeasonBase):
    show_id: str


class SeasonUpdate(BaseModel):
    season_number: Optional[int] = None
    title: Optional[str] = None
    status: Optional[ContentStatus] = None


class SeasonResponse(SeasonBase):
    id: str
    show_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
