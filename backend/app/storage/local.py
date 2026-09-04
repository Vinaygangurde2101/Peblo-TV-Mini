import os
import shutil
import uuid
from typing import BinaryIO, Optional
from werkzeug.utils import secure_filename

from app.storage.base import BaseStorageService
from app.core.config import settings


class LocalStorageService(BaseStorageService):
    """
    Local disk storage implementation using standard filesystem calls.
    Target directory is configured via settings.STORAGE_PATH.
    """

    def __init__(self, base_path: str = None):
        self.base_path = os.path.abspath(base_path or settings.STORAGE_PATH)
        os.makedirs(self.base_path, exist_ok=True)

    def _get_full_path(self, relative_path: str) -> str:
        # Sanitize path to prevent directory traversal
        clean_path = relative_path.lstrip("/").lstrip("\\")
        if clean_path.startswith("static/") or clean_path.startswith("static\\"):
            clean_path = clean_path[7:]
        full_path = os.path.abspath(os.path.join(self.base_path, clean_path))
        if not full_path.startswith(self.base_path):
            raise ValueError("Attempted path traversal outside storage directory.")
        return full_path

    def save(self, file_data: BinaryIO, filename: str, subfolder: str = "artwork") -> str:
        sanitized_name = secure_filename(filename) or "file"
        ext = os.path.splitext(sanitized_name)[1].lower() or ".jpg"
        unique_filename = f"{uuid.uuid4().hex[:12]}_{sanitized_name}"
        
        target_dir = os.path.join(self.base_path, subfolder)
        os.makedirs(target_dir, exist_ok=True)

        full_path = os.path.join(target_dir, unique_filename)
        file_data.seek(0)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(file_data, f)

        # Return static web URL relative path
        return f"/static/{subfolder}/{unique_filename}"

    def get(self, relative_path: str) -> Optional[bytes]:
        try:
            full_path = self._get_full_path(relative_path)
            if not os.path.exists(full_path):
                return None
            with open(full_path, "rb") as f:
                return f.read()
        except ValueError:
            return None

    def delete(self, relative_path: str) -> bool:
        try:
            full_path = self._get_full_path(relative_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception:
            return False

    def exists(self, relative_path: str) -> bool:
        try:
            full_path = self._get_full_path(relative_path)
            return os.path.exists(full_path)
        except ValueError:
            return False
