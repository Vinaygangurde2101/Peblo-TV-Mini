import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional

from app.db.session import get_db
from app.auth.dependencies import get_current_editor_or_admin
from app.models.user import User
from app.models.show import Show, ContentStatus
from app.schemas.show import ShowCreate, ShowUpdate, ShowResponse, ShowDetailResponse
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/admin/shows", tags=["Admin Shows"])


@router.get("", response_model=PaginatedResponse[ShowResponse])
def list_shows(
    q: Optional[str] = Query(None, description="Search query for show title or synopsis"),
    category: Optional[str] = Query(None, description="Filter by category"),
    section: Optional[str] = Query(None, description="Filter by section"),
    status_filter: Optional[ContentStatus] = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    query = db.query(Show)

    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            or_(
                Show.title.ilike(search_pattern),
                Show.synopsis.ilike(search_pattern)
            )
        )

    if category:
        query = query.filter(Show.category == category)

    if section:
        query = query.filter(Show.section == section)

    if status_filter:
        query = query.filter(Show.status == status_filter)

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    shows = query.order_by(Show.title.asc()).offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        items=shows,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("", response_model=ShowResponse, status_code=status.HTTP_201_CREATED)
def create_show(
    payload: ShowCreate,
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    show = Show(**payload.model_dump())
    db.add(show)
    db.commit()
    db.refresh(show)
    return show


@router.get("/{show_id}", response_model=ShowDetailResponse)
def get_show_details(
    show_id: str,
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    show = db.query(Show).options(
        joinedload(Show.seasons)
    ).filter(Show.id == show_id).first()

    if not show:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Show with ID '{show_id}' not found."
        )

    return show


@router.put("/{show_id}", response_model=ShowResponse)
def update_show(
    show_id: str,
    payload: ShowUpdate,
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    show = db.query(Show).filter(Show.id == show_id).first()
    if not show:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Show with ID '{show_id}' not found."
        )

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(show, key, value)

    db.commit()
    db.refresh(show)
    return show


@router.delete("/{show_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_show(
    show_id: str,
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    show = db.query(Show).filter(Show.id == show_id).first()
    if not show:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Show with ID '{show_id}' not found."
        )

    db.delete(show)
    db.commit()
    return None
