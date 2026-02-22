"""
Azure Blob Storage service — AES-256 encrypted image persistence (HIPAA §164.312(a)(2)(iv))
Images auto-deleted after 30 days via Azure lifecycle policy.
"""

import logging
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from azure.storage.blob import BlobServiceClient, ContentSettings
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.warning("azure-storage-blob not installed. Using local fallback.")


class StorageService:
    def __init__(self):
        if AZURE_AVAILABLE and settings.AZURE_STORAGE_CONNECTION_STRING:
            self.client = BlobServiceClient.from_connection_string(
                settings.AZURE_STORAGE_CONNECTION_STRING
            )
            self.container = settings.AZURE_CONTAINER_NAME
            self._ensure_container()
            logger.info("✅ Azure Blob Storage connected")
        else:
            self.client = None
            logger.warning("⚠️  Running in local storage mode (development only)")

    def _ensure_container(self):
        try:
            self.client.create_container(self.container)
        except Exception:
            pass  # Container already exists

    async def upload_bytes(
        self,
        data: bytes,
        blob_name: str,
        content_type: str = "application/octet-stream",
    ) -> Optional[str]:
        if not self.client:
            logger.warning(f"Local mode: skipping upload of {blob_name}")
            return f"local://{blob_name}"

        blob_client = self.client.get_blob_client(
            container=self.container, blob=blob_name
        )
        blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
        return blob_client.url

    async def delete_blob(self, blob_name: str) -> bool:
        if not self.client:
            return False
        try:
            blob_client = self.client.get_blob_client(
                container=self.container, blob=blob_name
            )
            blob_client.delete_blob()
            return True
        except Exception as e:
            logger.error(f"Failed to delete blob {blob_name}: {e}")
            return False


_storage_instance = None


def get_storage_service() -> StorageService:
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = StorageService()
    return _storage_instance
