"""
Pydantic models for API schemas
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ImageUploadResponse(BaseModel):
    """Response model for image upload"""
    message: str
    file_url: str
    file_name: str
    similar_images: List['SimilarImage']

class SimilarImage(BaseModel):
    """Model for similar image result"""
    image_id: str
    image_url: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    explanation: str
    metadata: Optional[Dict[str, Any]] = None

class IndexImageRequest(BaseModel):
    """Request model for indexing images"""
    image_urls: List[str]
    batch_size: Optional[int] = Field(default=10, ge=1, le=100)

class IndexImageResponse(BaseModel):
    """Response model for image indexing"""
    message: str
    indexed_count: int
    failed_count: int
    failed_urls: List[str] = []

class SearchRequest(BaseModel):
    """Request model for text-based search"""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: Optional[int] = Field(default=5, ge=1, le=20)

class SearchResponse(BaseModel):
    """Response model for search results"""
    message: str
    query_filename: str
    similar_images: List[SimilarImage]
    total_results: int
    processing_time: float

class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    services: Dict[str, str]

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime

class TextSearchRequest(BaseModel):
    """Request model for text-based image search"""
    query: str = Field(..., min_length=1, max_length=500, description="Text query to search for similar images")
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Number of results to return")

class TextSearchResponse(BaseModel):
    """Response model for text-based image search"""
    message: str
    query: str
    similar_images: List[SimilarImage]
    search_time: Optional[float] = None

class BulkUploadResponse(BaseModel):
    """Response model for bulk image upload"""
    message: str
    total_urls: int
    successful_indexes: int
    failed_urls: List[str] = []
    processing_time: Optional[float] = None

class IndexingProgress(BaseModel):
    """Model for indexing progress updates"""
    current: int
    total: int
    status: str
    current_url: Optional[str] = None
    errors: List[str] = []

# Update forward references
ImageUploadResponse.model_rebuild()
SearchResponse.model_rebuild() 