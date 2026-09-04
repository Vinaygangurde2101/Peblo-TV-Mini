import io
from PIL import Image
from typing import BinaryIO
from app.schemas.artwork import ArtworkType, ArtworkValidationResult

MAX_FILE_SIZE_BYTES = 200 * 1024  # 200 KB
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


def validate_artwork(file_data: BinaryIO, artwork_type: ArtworkType) -> ArtworkValidationResult:
    """
    Validates uploaded image file binary data against format, file size, dimension, and aspect ratio requirements.
    Returns ArtworkValidationResult with detailed human-readable error messages.
    """
    errors = []

    # 1. File Size Validation
    file_data.seek(0, io.SEEK_END)
    file_size_bytes = file_data.tell()
    file_data.seek(0)
    file_size_kb = round(file_size_bytes / 1024, 1)

    if file_size_bytes > MAX_FILE_SIZE_BYTES:
        errors.append(
            f"File size exceeds the 200 KB limit. Uploaded image is {file_size_kb} KB."
        )

    # 2. Image Decoding & Format Validation
    try:
        img = Image.open(file_data)
        img.verify()
        # PIL verify closes file pointer state, reopen for dimension inspection
        file_data.seek(0)
        img = Image.open(file_data)
    except Exception:
        errors.append("Invalid or corrupt image file. Could not decode image binary.")
        return ArtworkValidationResult(is_valid=False, errors=errors, file_size_kb=file_size_kb)

    img_format = img.format.upper() if img.format else "UNKNOWN"
    if img_format not in ALLOWED_FORMATS:
        errors.append(
            f"Unsupported image format '{img_format}'. Allowed formats are JPEG, PNG, WebP."
        )

    width, height = img.size
    aspect_ratio = width / height if height > 0 else 0.0

    # 3. Dimension & Aspect Ratio Validation
    if artwork_type == ArtworkType.POSTER:
        # Target: ~600x900 (Aspect ratio ~0.667)
        if not (500 <= width <= 750 and 750 <= height <= 1050):
            errors.append(
                f"Poster must be approximately 600×900 pixels. Uploaded image is {width}×{height} pixels."
            )
        elif not (0.60 <= aspect_ratio <= 0.73):
            errors.append(
                f"Poster must have an aspect ratio of approximately 2:3. Uploaded image aspect ratio is {aspect_ratio:.2f}."
            )

    elif artwork_type == ArtworkType.BANNER:
        # Target: 1280x720 (Aspect ratio 16:9 ~1.778)
        if not (1100 <= width <= 1450 and 600 <= height <= 850):
            errors.append(
                f"Banner must be approximately 1280×720 pixels. Uploaded image is {width}×{height} pixels."
            )
        elif not (1.68 <= aspect_ratio <= 1.88):
            errors.append(
                f"Banner must have an aspect ratio of 16:9. Uploaded image aspect ratio is {aspect_ratio:.2f}."
            )

    elif artwork_type == ArtworkType.THUMBNAIL:
        # Target: 640x360 (Aspect ratio 16:9 ~1.778)
        if not (550 <= width <= 750 and 300 <= height <= 420):
            errors.append(
                f"Thumbnail must be approximately 640×360 pixels. Uploaded image is {width}×{height} pixels."
            )
        elif not (1.68 <= aspect_ratio <= 1.88):
            errors.append(
                f"Thumbnail must have an aspect ratio of 16:9. Uploaded image aspect ratio is {aspect_ratio:.2f}."
            )

    is_valid = len(errors) == 0
    return ArtworkValidationResult(
        is_valid=is_valid,
        errors=errors,
        width=width,
        height=height,
        file_size_kb=file_size_kb,
        format=img_format,
    )
