import enum
from pydantic import BaseModel
from typing import Optional, List


class ArtworkType(str, enum.Enum):
    POSTER = "poster"
    BANNER = "banner"
    THUMBNAIL = "thumbnail"


class ArtworkUploadResponse(BaseModel):
    url: str
    artwork_type: ArtworkType
    width: int
    height: int
    file_size_kb: float
    format: str
    message: str = "Artwork uploaded successfully."


class ArtworkValidationResult(BaseModel):
    is_valid: bool
    errors: List[str]
    width: Optional[int] = None
    height: Optional[int] = None
    file_size_kb: Optional[float] = None
    format: Optional[str] = None
