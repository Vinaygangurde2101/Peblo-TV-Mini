from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from app.auth.dependencies import get_current_editor_or_admin
from app.models.user import User
from app.schemas.artwork import ArtworkType, ArtworkUploadResponse
from app.services.artwork.validator import validate_artwork
from app.storage.factory import get_storage_service
from app.storage.base import BaseStorageService

router = APIRouter(prefix="/admin/artwork", tags=["Admin Artwork"])


@router.post("/upload", response_model=ArtworkUploadResponse)
def upload_artwork(
    artwork_type: ArtworkType = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_editor_or_admin),
    storage: BaseStorageService = Depends(get_storage_service)
):
    """
    Validates and stores uploaded artwork image files.
    Enforces format (JPEG, PNG, WebP), dimensions, aspect ratios, and file size limits.
    Returns 400 Bad Request with human-readable error messages if validation fails.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required for artwork upload."
        )

    validation_result = validate_artwork(file.file, artwork_type)
    if (
        not validation_result.is_valid
        or validation_result.width is None
        or validation_result.height is None
        or validation_result.file_size_kb is None
        or validation_result.format is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Artwork validation failed.",
                "errors": validation_result.errors,
                "width": validation_result.width,
                "height": validation_result.height,
                "file_size_kb": validation_result.file_size_kb,
                "format": validation_result.format
            }
        )

    # Save to storage abstraction
    saved_path = storage.save(file.file, file.filename, subfolder="artwork")

    return ArtworkUploadResponse(
        url=saved_path,
        artwork_type=artwork_type,
        width=validation_result.width,
        height=validation_result.height,
        file_size_kb=validation_result.file_size_kb,
        format=validation_result.format,
        message=f"{artwork_type.value.capitalize()} uploaded and validated successfully."
    )
