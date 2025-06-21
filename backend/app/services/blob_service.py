"""
Azure Blob Storage service for image management
"""
import asyncio
from typing import Optional, List, Dict, Any
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import BlobSasPermissions, generate_blob_sas
from azure.core.exceptions import ResourceNotFoundError
from datetime import datetime, timedelta
from ..config import get_settings
import logging

logger = logging.getLogger(__name__)

class BlobStorageService:
    """Service for Azure Blob Storage operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.blob_service_client = None
        self.container_name = self.settings.azure_storage_container
    
    async def __aenter__(self):
        self.blob_service_client = BlobServiceClient.from_connection_string(
            self.settings.azure_storage_connection_string
        )
        await self._ensure_container_exists()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.blob_service_client:
            await self.blob_service_client.close()
    
    async def _ensure_container_exists(self):
        """Ensure the container exists, create if it doesn't"""
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            await container_client.get_container_properties()
            logger.info(f"Container {self.container_name} exists")
        except ResourceNotFoundError:
            logger.info(f"Creating public container: {self.container_name}")
            from azure.storage.blob import PublicAccess
            await self.blob_service_client.create_container(
                self.container_name,
                public_access=PublicAccess.Blob
            )
    
    async def upload_image(self, file_name: str, image_data: bytes, metadata: Optional[Dict[str, str]] = None) -> str:
        """
        Upload image to blob storage
        
        Args:
            file_name: Name of the file
            image_data: Image bytes
            metadata: Optional metadata
            
        Returns:
            Public blob URL
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=file_name
            )
            
            # Upload the image
            await blob_client.upload_blob(
                image_data,
                blob_type="BlockBlob",
                content_type="image/jpeg",
                metadata=metadata,
                overwrite=True
            )
            
            # Return the public blob URL
            return blob_client.url
            
        except Exception as e:
            logger.error(f"Error uploading image {file_name}: {str(e)}")
            raise
    
    async def download_image(self, file_name: str) -> bytes:
        """
        Download image from blob storage
        
        Args:
            file_name: Name of the file
            
        Returns:
            Image bytes
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=file_name
            )
            
            download_stream = await blob_client.download_blob()
            return await download_stream.readall()
            
        except ResourceNotFoundError:
            logger.error(f"Image {file_name} not found")
            raise
        except Exception as e:
            logger.error(f"Error downloading image {file_name}: {str(e)}")
            raise
    
    async def get_image_url(self, file_name: str, expires_in_hours: int = 24) -> str:
        """
        Get a SAS URL for the image
        
        Args:
            file_name: Name of the file
            expires_in_hours: Expiration time in hours
            
        Returns:
            SAS URL
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=file_name
            )
            
            # Get the account key from the connection string
            from azure.storage.blob import BlobServiceClient
            
            # Create a sync client to get the account key
            sync_client = BlobServiceClient.from_connection_string(
                self.settings.azure_storage_connection_string
            )
            
            # Generate SAS token
            sas_token = generate_blob_sas(
                account_name=sync_client.account_name,
                container_name=self.container_name,
                blob_name=file_name,
                account_key=sync_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=expires_in_hours)
            )
            
            base_url = blob_client.url.split('?')[0]  # Remove any existing query params
            return f"{base_url}?{sas_token}"
            
        except Exception as e:
            logger.error(f"Error generating SAS URL for {file_name}: {str(e)}")
            # Return direct URL as fallback
            return blob_client.url
    
    async def list_images(self, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List images in the container
        
        Args:
            prefix: Optional prefix to filter blobs
            
        Returns:
            List of blob information
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blobs = []
            
            async for blob in container_client.list_blobs(name_starts_with=prefix):
                blobs.append({
                    'name': blob.name,
                    'url': f"{container_client.url}/{blob.name}",
                    'size': blob.size,
                    'last_modified': blob.last_modified,
                    'metadata': blob.metadata or {}
                })
            
            return blobs
            
        except Exception as e:
            logger.error(f"Error listing images: {str(e)}")
            raise
    
    async def delete_image(self, file_name: str) -> bool:
        """
        Delete image from blob storage
        
        Args:
            file_name: Name of the file
            
        Returns:
            True if deleted successfully
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=file_name
            )
            
            await blob_client.delete_blob()
            return True
            
        except ResourceNotFoundError:
            logger.warning(f"Image {file_name} not found for deletion")
            return False
        except Exception as e:
            logger.error(f"Error deleting image {file_name}: {str(e)}")
            raise 