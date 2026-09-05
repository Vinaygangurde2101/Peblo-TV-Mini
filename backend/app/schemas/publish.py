from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime
from app.models.publish_run import PublishStatus


class PublishResponse(BaseModel):
    publish_run_id: str
    status: PublishStatus
    show_count: int
    episode_count: int
    published_at: datetime
    message: str


class PublishRunResponse(BaseModel):
    id: str
    published_by_user_id: Optional[str] = None
    status: PublishStatus
    show_count: int
    episode_count: int
    validation_errors: Optional[Any] = None
    snapshot_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublishDryRunResponse(BaseModel):
    is_publishable: bool
    added_shows: List[str]
    modified_shows: List[str]
    removed_shows: List[str]
    total_shows_candidate: int
    total_episodes_candidate: int
    validation_blockers_count: int


class RollbackResponse(BaseModel):
    publish_run_id: str
    rolled_back_to_run_id: str
    status: PublishStatus
    show_count: int
    episode_count: int
    message: str
