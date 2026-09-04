from pydantic import BaseModel
from typing import List, Optional, Any


class CatalogueEpisodeVariant(BaseModel):
    language: str
    title: str
    duration_seconds: Optional[int] = None
    thumbnail_url: Optional[str] = None


class CatalogueEpisode(BaseModel):
    content_group: str
    episode_number: int
    title: str
    synopsis: Optional[str] = None
    duration_seconds: Optional[int] = None
    poster_url: Optional[str] = None
    banner_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    languages: List[str]
    variants: List[CatalogueEpisodeVariant] = []


class CatalogueSeason(BaseModel):
    id: str
    season_number: int
    title: str
    episodes: List[CatalogueEpisode] = []


class CatalogueShow(BaseModel):
    id: str
    title: str
    synopsis: Optional[str] = None
    category: Optional[str] = None
    section: Optional[str] = None
    poster_url: Optional[str] = None
    banner_url: Optional[str] = None
    seasons: List[CatalogueSeason] = []
    trailers: List[CatalogueEpisode] = []


class SectionGroup(BaseModel):
    name: str
    shows: List[CatalogueShow] = []


class CatalogueResponse(BaseModel):
    version: str
    generated_at: str
    total_shows: int
    total_episodes: int
    sections: List[SectionGroup] = []
    shows: List[CatalogueShow] = []
