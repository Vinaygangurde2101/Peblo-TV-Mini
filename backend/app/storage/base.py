from abc import ABC, abstractmethod
from typing import BinaryIO, Optional


class BaseStorageService(ABC):
    """
    Abstract interface for object/file storage services.
    Supports local filesystem dev/Docker environments and extensible cloud backends (Cloudflare R2 / AWS S3).
    """

    @abstractmethod
    def save(self, file_data: BinaryIO, filename: str, subfolder: str = "artwork") -> str:
        """
        Saves binary file data to storage.
        Returns the public URL/relative path of the saved file.
        """
        pass

    @abstractmethod
    def get(self, relative_path: str) -> Optional[bytes]:
        """Retrieves raw bytes of a file by its relative path."""
        pass

    @abstractmethod
    def delete(self, relative_path: str) -> bool:
        """Deletes a file from storage. Returns True if successful."""
        pass

    @abstractmethod
    def exists(self, relative_path: str) -> bool:
        """Checks if a file exists in storage."""
        pass
