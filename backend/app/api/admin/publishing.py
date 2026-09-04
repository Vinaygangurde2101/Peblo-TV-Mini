from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.auth.dependencies import get_current_admin, get_current_editor_or_admin
from app.models.user import User
from app.models.publish_run import PublishRun
from app.schemas.publish import PublishResponse, PublishRunResponse
from app.services.publishing.engine import execute_catalogue_publish, PublishValidationError

router = APIRouter(prefix="/admin", tags=["Admin Publishing"])


@router.post("/catalog/publish", response_model=PublishResponse)
def publish_catalog(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Executes atomic catalogue publishing pipeline.
    RESTRICTED TO ADMIN ROLE ONLY. Returns 403 Forbidden if invoked by Editor.
    Returns 400 Bad Request with validation report if database state is invalid.
    """
    try:
        run_record = execute_catalogue_publish(db, current_user.id)
        return PublishResponse(
            publish_run_id=run_record.id,
            status=run_record.status,
            show_count=run_record.show_count,
            episode_count=run_record.episode_count,
            published_at=run_record.created_at,
            message="Catalogue published successfully."
        )
    except PublishValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Publishing blocked by validation errors.",
                "report": e.validation_report.model_dump()
            }
        )


@router.get("/publish-runs", response_model=List[PublishRunResponse])
def get_publish_history(
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db)
):
    """
    Returns audit history of past publish executions.
    """
    return db.query(PublishRun).order_by(PublishRun.created_at.desc()).all()
