"""
Azure Cognitive Search service for vector operations
"""
import asyncio
from typing import List, Dict, Any, Optional
from azure.search.documents.aio import SearchClient
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType, VectorSearch,
    VectorSearchAlgorithmConfiguration, HnswAlgorithmConfiguration, HnswParameters,
    VectorSearchProfile, SearchField
)
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from ..config import get_settings
import logging

logger = logging.getLogger(__name__)

class SearchService:
    """Service for Azure Cognitive Search operations"""
    
    def __init__(self):
        self.settings = get_settings()
        self.credential = AzureKeyCredential(self.settings.azure_search_api_key)
        self.search_client = None
        self.index_client = None
    
    async def __aenter__(self):
        self.search_client = SearchClient(
            endpoint=self.settings.azure_search_endpoint,
            index_name=self.settings.azure_search_index_name,
            credential=self.credential
        )
        self.index_client = SearchIndexClient(
            endpoint=self.settings.azure_search_endpoint,
            credential=self.credential
        )
        await self._ensure_index_exists()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.search_client:
            await self.search_client.close()
        if self.index_client:
            await self.index_client.close()
    
    async def _ensure_index_exists(self):
        """Ensure the search index exists, create if it doesn't"""
        try:
            await self.index_client.get_index(self.settings.azure_search_index_name)
            logger.info(f"Index {self.settings.azure_search_index_name} exists")
        except ResourceNotFoundError:
            logger.info(f"Creating index: {self.settings.azure_search_index_name}")
            await self._create_index()
    
    async def _create_index(self):
        """Create the search index with vector search configuration"""
        try:
            # Define the index schema
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(name="image_name", type=SearchFieldDataType.String),
                SimpleField(name="image_url", type=SearchFieldDataType.String),
                SimpleField(name="blob_name", type=SearchFieldDataType.String),
                SimpleField(name="metadata", type=SearchFieldDataType.String),
                SimpleField(name="created_at", type=SearchFieldDataType.DateTimeOffset),
                # Vector field for embeddings
                SearchField(
                    name="embedding",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=self.settings.embedding_dimensions,
                    vector_search_profile_name="vector-profile"
                )
            ]
            
            # Configure vector search algorithms
            vector_search = VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(
                        name="hnsw-config",
                        parameters=HnswParameters(
                            metric="cosine",
                            m=4,
                            ef_construction=400,
                            ef_search=500
                        )
                    )
                ],
                profiles=[
                    VectorSearchProfile(
                        name="vector-profile",
                        algorithm_configuration_name="hnsw-config"
                    )
                ]
            )
            
            # Create the index
            index = SearchIndex(
                name=self.settings.azure_search_index_name,
                fields=fields,
                vector_search=vector_search
            )
            
            await self.index_client.create_index(index)
            logger.info(f"Index {self.settings.azure_search_index_name} created successfully")
            
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            raise
    
    async def index_image(self, image_id: str, image_name: str, image_url: str, 
                         blob_name: str, embedding: List[float], 
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Index an image with its embedding
        
        Args:
            image_id: Unique identifier for the image
            image_name: Original image name
            image_url: URL to access the image
            blob_name: Blob storage name
            embedding: Image embedding vector
            metadata: Optional metadata
            
        Returns:
            True if indexed successfully
        """
        try:
            document = {
                "id": image_id,
                "image_name": image_name,
                "image_url": image_url,
                "blob_name": blob_name,
                "embedding": embedding,
                "metadata": str(metadata) if metadata else "",
                "created_at": "2024-01-01T00:00:00Z"  # You can use datetime.utcnow().isoformat() + "Z"
            }
            
            result = await self.search_client.upload_documents([document])
            
            if result[0].succeeded:
                logger.info(f"Successfully indexed image: {image_id}")
                return True
            else:
                logger.error(f"Failed to index image {image_id}: {result[0].error_message}")
                return False
                
        except Exception as e:
            logger.error(f"Error indexing image {image_id}: {str(e)}")
            return False
    
    async def search_similar_images(self, query_embedding: List[float], 
                                   top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar images using vector similarity
        
        Args:
            query_embedding: Query image embedding
            top_k: Number of results to return
            
        Returns:
            List of similar images
        """
        try:
            # Create vectorized query
            vector_query = VectorizedQuery(
                vector=query_embedding,
                k_nearest_neighbors=top_k,
                fields="embedding"
            )
            
            # Perform vector search
            results = await self.search_client.search(
                search_text=None,
                vector_queries=[vector_query],
                select=["id", "image_name", "image_url", "blob_name", "metadata"],
                top=top_k
            )
            
            similar_images = []
            async for result in results:
                similar_images.append({
                    "id": result["id"],
                    "image_name": result["image_name"],
                    "image_url": result["image_url"],
                    "blob_name": result["blob_name"],
                    "metadata": result.get("metadata", ""),
                    "similarity_score": result.get("@search.score", 0.0)
                })
            
            logger.info(f"Found {len(similar_images)} similar images")
            return similar_images
            
        except Exception as e:
            logger.error(f"Error searching similar images: {str(e)}")
            return []
    
    async def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        Get image document by ID
        
        Args:
            image_id: Image identifier
            
        Returns:
            Image document or None
        """
        try:
            result = await self.search_client.get_document(key=image_id)
            return result
        except ResourceNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error getting image {image_id}: {str(e)}")
            return None
    
    async def delete_image(self, image_id: str) -> bool:
        """
        Delete image from search index
        
        Args:
            image_id: Image identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            result = await self.search_client.delete_documents([{"id": image_id}])
            
            if result[0].succeeded:
                logger.info(f"Successfully deleted image from index: {image_id}")
                return True
            else:
                logger.error(f"Failed to delete image {image_id}: {result[0].error_message}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting image {image_id}: {str(e)}")
            return False
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the search index"""
        try:
            stats = await self.index_client.get_index_statistics(self.settings.azure_search_index_name)
            
            # Handle both dict and object responses
            if isinstance(stats, dict):
                return {
                    "document_count": stats.get("document_count", 0),
                    "storage_size": stats.get("storage_size", 0)
                }
            else:
                return {
                    "document_count": getattr(stats, 'document_count', 0),
                    "storage_size": getattr(stats, 'storage_size', 0)
                }
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {"document_count": 0, "storage_size": 0} 