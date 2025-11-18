"""
Image storage service for food image recognition.

Handles:
- Image file validation (type, size, dimensions)
- Local file storage with organized structure
- Image URL generation
- Image cleanup
"""

import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ImageStorageError(Exception):
    """Custom exception for image storage errors."""

    pass


class ImageStorageService:
    """
    Service for managing food image uploads and storage.

    Features:
    - File type validation (jpg, png, webp)
    - File size validation (max 5MB)
    - Image dimension validation
    - Organized storage: uploads/images/{user_id}/{timestamp}_{filename}
    - Image URL generation for API responses
    """

    # Storage configuration
    UPLOAD_DIR = Path("backend/uploads/images")
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
    ALLOWED_MIME_TYPES = {
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
    }
    MIN_DIMENSION = 100  # Minimum width/height in pixels
    MAX_DIMENSION = 4096  # Maximum width/height in pixels

    def __init__(self):
        """Initialize image storage service."""
        self._ensure_upload_directory()

    def _ensure_upload_directory(self) -> None:
        """Ensure upload directory exists."""
        try:
            self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"Upload directory ready: {self.UPLOAD_DIR}")
        except Exception as e:
            logger.error(f"Failed to create upload directory: {e}")
            raise ImageStorageError(f"Failed to initialize storage: {e}")

    def validate_file_type(
        self, filename: str, content_type: Optional[str] = None
    ) -> str:
        """
        Validate file type by extension and content type.

        Args:
            filename: Original filename
            content_type: MIME content type

        Returns:
            Validated file extension (jpg, png, webp)

        Raises:
            ImageStorageError: If file type is invalid
        """
        # Extract extension from filename
        if not filename:
            raise ImageStorageError("Filename is required")

        file_ext = filename.lower().split(".")[-1] if "." in filename else ""

        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise ImageStorageError(
                f"Invalid file extension. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        # Validate content type if provided
        if content_type and content_type.lower() not in self.ALLOWED_MIME_TYPES:
            raise ImageStorageError(
                f"Invalid content type: {content_type}. "
                f"Allowed: {', '.join(self.ALLOWED_MIME_TYPES)}"
            )

        # Normalize extension
        if file_ext == "jpeg":
            file_ext = "jpg"

        return file_ext

    def validate_file_size(self, file_size: int) -> None:
        """
        Validate file size.

        Args:
            file_size: File size in bytes

        Raises:
            ImageStorageError: If file size exceeds limit
        """
        if file_size > self.MAX_FILE_SIZE:
            max_mb = self.MAX_FILE_SIZE / (1024 * 1024)
            raise ImageStorageError(
                f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds "
                f"maximum allowed size ({max_mb}MB)"
            )

        if file_size == 0:
            raise ImageStorageError("File is empty")

    def validate_image_dimensions(self, image_bytes: bytes) -> Tuple[int, int]:
        """
        Validate image dimensions and return (width, height).

        Args:
            image_bytes: Raw image bytes

        Returns:
            Tuple of (width, height)

        Raises:
            ImageStorageError: If image is invalid or dimensions are out of bounds
        """
        try:
            import io

            image = Image.open(io.BytesIO(image_bytes))
            width, height = image.size

            if width < self.MIN_DIMENSION or height < self.MIN_DIMENSION:
                raise ImageStorageError(
                    f"Image dimensions too small. Minimum: {self.MIN_DIMENSION}x{self.MIN_DIMENSION}px"
                )

            if width > self.MAX_DIMENSION or height > self.MAX_DIMENSION:
                raise ImageStorageError(
                    f"Image dimensions too large. Maximum: {self.MAX_DIMENSION}x{self.MAX_DIMENSION}px"
                )

            logger.info(f"Image dimensions validated: {width}x{height}px")
            return width, height

        except ImageStorageError:
            raise
        except Exception as e:
            raise ImageStorageError(f"Failed to validate image: {e}")

    def save_image(
        self,
        image_bytes: bytes,
        user_id: int,
        filename: str,
        content_type: Optional[str] = None,
    ) -> dict:
        """
        Save image to local storage.

        Args:
            image_bytes: Raw image bytes
            user_id: User ID for organization
            filename: Original filename
            content_type: MIME content type

        Returns:
            Dictionary with file_path, url, width, height, size

        Raises:
            ImageStorageError: If validation or save fails
        """
        # Validate file type
        file_ext = self.validate_file_type(filename, content_type)

        # Validate file size
        file_size = len(image_bytes)
        self.validate_file_size(file_size)

        # Validate dimensions
        width, height = self.validate_image_dimensions(image_bytes)

        # Create user directory
        user_dir = self.UPLOAD_DIR / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename with timestamp
        timestamp = int(time.time() * 1000)  # milliseconds
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        new_filename = f"{timestamp}_{safe_filename}"

        # Ensure extension is correct
        if not new_filename.endswith(f".{file_ext}"):
            new_filename = f"{new_filename}.{file_ext}"

        file_path = user_dir / new_filename

        # Save file
        try:
            with open(file_path, "wb") as f:
                f.write(image_bytes)

            logger.info(f"Image saved: {file_path} ({file_size} bytes)")

            # Generate URL (relative path from backend root)
            relative_path = file_path.relative_to(Path("backend"))
            url = f"/uploads/images/{user_id}/{new_filename}"

            return {
                "file_path": str(file_path),
                "url": url,
                "width": width,
                "height": height,
                "size": file_size,
                "format": file_ext,
            }

        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise ImageStorageError(f"Failed to save image: {e}")

    def delete_image(self, file_path: str) -> bool:
        """
        Delete image from storage.

        Args:
            file_path: Path to image file

        Returns:
            True if deleted, False if file not found
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                logger.info(f"Image deleted: {file_path}")
                return True
            else:
                logger.warning(f"Image not found for deletion: {file_path}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete image: {e}")
            return False

    def get_user_images(self, user_id: int) -> list:
        """
        Get all image files for a user.

        Args:
            user_id: User ID

        Returns:
            List of image file paths
        """
        user_dir = self.UPLOAD_DIR / str(user_id)

        if not user_dir.exists():
            return []

        try:
            images = []
            for ext in self.ALLOWED_EXTENSIONS:
                images.extend(user_dir.glob(f"*.{ext}"))

            return sorted([str(img) for img in images], reverse=True)

        except Exception as e:
            logger.error(f"Failed to list user images: {e}")
            return []

    def cleanup_old_images(self, user_id: int, days: int = 30) -> int:
        """
        Delete images older than specified days for a user.

        Args:
            user_id: User ID
            days: Number of days threshold

        Returns:
            Number of images deleted
        """
        user_dir = self.UPLOAD_DIR / str(user_id)

        if not user_dir.exists():
            return 0

        try:
            deleted_count = 0
            current_time = time.time()
            max_age_seconds = days * 24 * 60 * 60

            for image_path in user_dir.iterdir():
                if image_path.is_file():
                    file_age = current_time - image_path.stat().st_mtime

                    if file_age > max_age_seconds:
                        image_path.unlink()
                        deleted_count += 1

            logger.info(
                f"Cleaned up {deleted_count} old images for user {user_id}"
            )
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup old images: {e}")
            return 0


# Create singleton instance
image_storage_service = ImageStorageService()
