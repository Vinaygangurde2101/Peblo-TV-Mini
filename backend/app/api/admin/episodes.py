import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
from typing import Optional

from app.db.session import get_db
from app.auth.dependencies import get_current_editor_or_admin
from app.models.user import User
from app.models.season import Season
from app.models.episode import Episode
from app.models.show import ContentStatus
from app.schemas.episode import EpisodeCreate, EpisodeUpdate, EpisodeResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/admin/episodes", tags=["Admin Episodes"])


@router.get("", response_model=PaginatedResponse[EpisodeResponse])
def list_episodes(
    season_id: Optional[str] = Query(None, description="Filter episodes by season ID"),
    content_group: Optional[str] = Query(None, description="Filter episodes by content_group key"),
    language: Optional[str] = Query(None, description="Filter episodes by language"),
    status_filter: Optional[ContentStatus] = Query(None, alias="status", description="Filter by status"),
    q: Optional[str] = Query(None, description="Search query for episode title or synopsis"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Episode)

    if season_id:
        query = query.filter(Episode.season_id == season_id)

    if content_group:
        query = query.filter(Episode.content_group == content_group)

    if language:
        query = query.filter(Episode.language == language)

    if status_filter:
        query = query.filter(Episode.status == status_filter)

    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            or_(
                Episode.title.ilike(search_pattern),
                Episode.synopsis.ilike(search_pattern)
            )
        )

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    episodes = query.order_by(Episode.episode_number.asc()).offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        items=episodes,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("", response_model=EpisodeResponse, status_code=status.HTTP_201_CREATED)
def create_episode(
    payload: EpisodeCreate,
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    # Verify parent season exists
    season = db.query(Season).filter(Season.id == payload.season_id).first()
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with ID '{payload.season_id}' not found."
        )

    try:
        episode = Episode(**payload.model_dump())
        db.add(episode)
        db.commit()
        db.refresh(episode)
        return episode
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An episode variant for content_group '{payload.content_group}' in language '{payload.language}' already exists."
        )


@router.get("/{episode_id}", response_model=EpisodeResponse)
def get_episode(
    episode_id: str,
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode with ID '{episode_id}' not found."
        )
    return episode


@router.put("/{episode_id}", response_model=EpisodeResponse)
def update_episode(
    episode_id: str,
    payload: EpisodeUpdate,
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode with ID '{episode_id}' not found."
        )

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(episode, key, value)

    try:
        db.commit()
        db.refresh(episode)
        return episode
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict with existing content_group and language unique constraint."
        )


@router.delete("/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_episode(
    episode_id: str,
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    episode = db.query(Episode).filter(Episode.id == episode_id).first()
    if not episode:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode with ID '{episode_id}' not found."
        )

    db.delete(episode)
    db.commit()
    return None
