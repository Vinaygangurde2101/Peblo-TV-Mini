from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.dependencies import get_current_editor_or_admin
from app.models.user import User
from app.schemas.validation import ValidationReportResponse
from app.services.validation.report import generate_validation_report
from app.storage.factory import get_storage_service
from app.storage.base import BaseStorageService

router = APIRouter(prefix="/admin", tags=["Admin Validation"])


@router.get("/validation-report", response_model=ValidationReportResponse)
def get_validation_report(
    current_user: User = Depends(get_current_editor_or_admin),
    db: Session = Depends(get_db),
    storage: BaseStorageService = Depends(get_storage_service)
):
    """
    Performs a live readiness audit of editorial database state.
    Returns publish blockers grouped by show and episode.
    """
    return generate_validation_report(db, storage)
