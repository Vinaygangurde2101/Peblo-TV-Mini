from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from app.db.session import get_db
from app.auth.dependencies import get_current_editor_or_admin
from app.models.user import User
from app.models.show import Show
from app.models.season import Season
from app.schemas.season import SeasonCreate, SeasonUpdate, SeasonResponse

router = APIRouter(prefix="/admin/seasons", tags=["Admin Seasons"])


@router.get("", response_model=List[SeasonResponse])
def list_seasons(
    show_id: Optional[str] = Query(None, description="Filter seasons by show ID"),
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Season)
    if show_id:
        query = query.filter(Season.show_id == show_id)

    return query.order_by(Season.season_number.asc()).all()


@router.post("", response_model=SeasonResponse, status_code=status.HTTP_201_CREATED)
def create_season(
    payload: SeasonCreate,
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    # Verify parent show exists
    show = db.query(Show).filter(Show.id == payload.show_id).first()
    if not show:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Show with ID '{payload.show_id}' not found."
        )

    try:
        season = Season(**payload.model_dump())
        db.add(season)
        db.commit()
        db.refresh(season)
        return season
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Season number {payload.season_number} already exists for this show."
        )


@router.put("/{season_id}", response_model=SeasonResponse)
def update_season(
    season_id: str,
    payload: SeasonUpdate,
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    season = db.query(Season).filter(Season.id == season_id).first()
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with ID '{season_id}' not found."
        )

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(season, key, value)

    try:
        db.commit()
        db.refresh(season)
        return season
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflict with existing season number for this show."
        )


@router.delete("/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_season(
    season_id: str,
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    season = db.query(Season).filter(Season.id == season_id).first()
    if not season:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Season with ID '{season_id}' not found."
        )

    db.delete(season)
    db.commit()
    return None
