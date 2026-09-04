import io
import pytest
from PIL import Image
from app.services.artwork.validator import validate_artwork
from app.schemas.artwork import ArtworkType
from app.storage.local import LocalStorageService


def create_test_image(width: int, height: int, fmt: str = "JPEG", size_padding: int = 0) -> io.BytesIO:
    """Helper function creating an in-memory image for validation testing."""
    buf = io.BytesIO()
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    img.save(buf, format=fmt)
    if size_padding > 0:
        buf.write(b"0" * size_padding)
    buf.seek(0)
    return buf


def test_valid_poster_validation():
    file_data = create_test_image(600, 900, "JPEG")
    res = validate_artwork(file_data, ArtworkType.POSTER)
    assert res.is_valid is True
    assert len(res.errors) == 0
    assert res.width == 600
    assert res.height == 900


def test_invalid_poster_dimensions():
    # 400x400 is not approximately 600x900
    file_data = create_test_image(400, 400, "JPEG")
    res = validate_artwork(file_data, ArtworkType.POSTER)
    assert res.is_valid is False
    assert any("Poster must be approximately 600×900" in err for err in res.errors)


def test_invalid_banner_aspect_ratio():
    # 1280x720 is 16:9, but 1280x1000 is ~1.28
    file_data = create_test_image(1280, 720, "JPEG")
    res_valid = validate_artwork(file_data, ArtworkType.BANNER)
    assert res_valid.is_valid is True

    file_data_bad = create_test_image(1280, 1000, "JPEG")
    res_bad = validate_artwork(file_data_bad, ArtworkType.BANNER)
    assert res_bad.is_valid is False


def test_file_size_exceeded():
    # Create image exceeding 200 KB
    file_data = create_test_image(600, 900, "JPEG", size_padding=250 * 1024)
    res = validate_artwork(file_data, ArtworkType.POSTER)
    assert res.is_valid is False
    assert any("File size exceeds the 200 KB limit" in err for err in res.errors)


def test_storage_path_traversal_prevention(tmp_path):
    storage = LocalStorageService(base_path=str(tmp_path))
    with pytest.raises(ValueError, match="Attempted path traversal"):
        storage._get_full_path("../../../etc/passwd")
