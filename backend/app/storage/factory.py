from app.storage.base import BaseStorageService
from app.storage.local import LocalStorageService
from app.core.config import settings


def get_storage_service() -> BaseStorageService:
    """
    Dependency factory providing the configured storage service instance.
    Defaults to LocalStorageService for dev and Docker environments.
    """
    if settings.STORAGE_TYPE == "local":
        return LocalStorageService(settings.STORAGE_PATH)
    else:
        # Fallback to LocalStorageService if custom cloud adapter isn't configured
        return LocalStorageService(settings.STORAGE_PATH)
