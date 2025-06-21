"""
Main FastAPI application for Azure Image Search
"""
import uuid
import asyncio
import time
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import httpx

from .config import get_settings
from .models.schemas import (
    ImageUploadResponse, SimilarImage, IndexImageRequest, IndexImageResponse,
    SearchRequest, SearchResponse, HealthCheckResponse, ErrorResponse
)
from .services.azure_openai_service import AzureOpenAIService
from .services.blob_service import BlobStorageService
from .services.search_service import SearchService
from .utils.image_utils import ImageProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Application lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting up Image Search API...")
    yield
    logger.info("Shutting down Image Search API...")

# Initialize FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp=datetime.utcnow()
        ).dict()
    )

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        services={
            "api": "operational",
            "azure_openai": "operational",
            "blob_storage": "operational",
            "cognitive_search": "operational"
        }
    )

@app.post("/upload", response_model=ImageUploadResponse)
async def upload_image_and_search(
    file: UploadFile = File(...),
    top_k: Optional[int] = 5
):
    """
    Upload an image and find similar images
    
    Args:
        file: Image file to upload
        top_k: Number of similar images to return
        
    Returns:
        Upload response with similar images
    """
    start_time = time.time()
    
    try:
        # Validate the uploaded file
        ImageProcessor.validate_image(file, settings.max_file_size)
        
        # Read and process the image
        image_data = await file.read()
        processed_image = ImageProcessor.process_image(image_data)
        
        # Generate unique filename
        filename = ImageProcessor.generate_filename(file.filename)
        
        # Initialize services
        async with (
            AzureOpenAIService() as openai_service,
            BlobStorageService() as blob_service,
            SearchService() as search_service
        ):
            # Generate embedding for the uploaded image
            logger.info(f"Generating embedding for uploaded image: {filename}")
            query_embedding = await openai_service.generate_image_embedding(processed_image)
            
            # Search for similar images
            logger.info(f"Searching for {top_k} similar images")
            similar_results = await search_service.search_similar_images(
                query_embedding, top_k
            )
            
            # Upload the query image to blob storage
            logger.info(f"Uploading image to blob storage: {filename}")
            blob_url = await blob_service.upload_image(
                filename, 
                processed_image,
                metadata={
                    "original_name": file.filename,
                    "upload_time": datetime.utcnow().isoformat(),
                    "content_type": file.content_type
                }
            )
            
            # Process similar images and generate explanations
            similar_images = []
            for result in similar_results:
                try:
                    # Download the similar image from blob storage
                    similar_image_data = await blob_service.download_image(result["blob_name"])
                    
                    # Generate explanation
                    explanation = await openai_service.generate_similarity_explanation(
                        processed_image, similar_image_data
                    )
                    
                    similar_images.append(SimilarImage(
                        image_id=result["id"],
                        image_url=result["image_url"],
                        similarity_score=result["similarity_score"],
                        explanation=explanation,
                        metadata={"blob_name": result["blob_name"]}
                    ))
                    
                except Exception as e:
                    logger.error(f"Error processing similar image {result['id']}: {str(e)}")
                    # Continue with other images
                    similar_images.append(SimilarImage(
                        image_id=result["id"],
                        image_url=result["image_url"],
                        similarity_score=result["similarity_score"],
                        explanation="Unable to generate explanation for this image.",
                        metadata={"blob_name": result.get("blob_name", "")}
                    ))
            
            processing_time = time.time() - start_time
            logger.info(f"Image processing completed in {processing_time:.2f} seconds")
            
            return ImageUploadResponse(
                message="Image uploaded and similar images found successfully",
                file_url=blob_url,
                file_name=filename,
                similar_images=similar_images
            )
            
    except Exception as e:
        logger.error(f"Error in upload_image_and_search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search_similar_images(
    file: UploadFile = File(...),
    top_k: Optional[int] = 5
):
    """
    Search for similar images without uploading to storage
    
    Args:
        file: Query image file
        top_k: Number of similar images to return
        
    Returns:
        Search results with similar images and explanations
    """
    start_time = time.time()
    
    try:
        # Validate the uploaded file
        ImageProcessor.validate_image(file, settings.max_file_size)
        
        # Read and process the image
        image_data = await file.read()
        processed_image = ImageProcessor.process_image(image_data)
        
        # Initialize services
        async with (
            AzureOpenAIService() as openai_service,
            BlobStorageService() as blob_service,
            SearchService() as search_service
        ):
            # Generate embedding for the query image
            logger.info(f"Generating embedding for search query: {file.filename}")
            query_embedding = await openai_service.generate_image_embedding(processed_image)
            
            # Search for similar images
            logger.info(f"Searching for {top_k} similar images")
            similar_results = await search_service.search_similar_images(
                query_embedding, top_k
            )
            
            # Process similar images and generate explanations
            similar_images = []
            for result in similar_results:
                try:
                    # Download the similar image from blob storage
                    similar_image_data = await blob_service.download_image(result["blob_name"])
                    
                    # Generate explanation
                    explanation = await openai_service.generate_similarity_explanation(
                        processed_image, similar_image_data
                    )
                    
                    similar_images.append(SimilarImage(
                        image_id=result["id"],
                        image_url=result["image_url"],
                        similarity_score=result["similarity_score"],
                        explanation=explanation,
                        metadata={"blob_name": result["blob_name"]}
                    ))
                    
                except Exception as e:
                    logger.error(f"Error processing similar image {result['id']}: {str(e)}")
                    # Continue with other images
                    similar_images.append(SimilarImage(
                        image_id=result["id"],
                        image_url=result["image_url"],
                        similarity_score=result["similarity_score"],
                        explanation="Unable to generate explanation for this image.",
                        metadata={"blob_name": result.get("blob_name", "")}
                    ))
            
            processing_time = time.time() - start_time
            logger.info(f"Search completed in {processing_time:.2f} seconds")
            
            return SearchResponse(
                message="Search completed successfully",
                query_filename=file.filename,
                similar_images=similar_images,
                total_results=len(similar_images),
                processing_time=processing_time
            )
            
    except Exception as e:
        logger.error(f"Error in search_similar_images: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index", response_model=IndexImageResponse)
async def index_images(request: IndexImageRequest, background_tasks: BackgroundTasks):
    """
    Index images from URLs into the search system (Admin endpoint)
    
    Args:
        request: Index request with image URLs
        background_tasks: FastAPI background tasks
        
    Returns:
        Indexing status
    """
    try:
        # Start indexing in background
        background_tasks.add_task(
            index_images_background,
            request.image_urls,
            request.batch_size
        )
        
        return IndexImageResponse(
            message=f"Started indexing {len(request.image_urls)} images in background",
            indexed_count=0,
            failed_count=0,
            failed_urls=[]
        )
        
    except Exception as e:
        logger.error(f"Error starting image indexing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def index_images_background(image_urls: List[str], batch_size: int):
    """Background task for indexing images"""
    indexed_count = 0
    failed_count = 0
    failed_urls = []
    
    logger.info(f"🚀 Background indexing started: {len(image_urls)} images")
    
    try:
        async with (
            AzureOpenAIService() as openai_service,
            BlobStorageService() as blob_service,
            SearchService() as search_service
        ):
            logger.info("✅ Services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {str(e)}")
        return
    
    async with (
        AzureOpenAIService() as openai_service,
        BlobStorageService() as blob_service,
        SearchService() as search_service
    ):
        # Process images in batches
        for i in range(0, len(image_urls), batch_size):
            batch = image_urls[i:i + batch_size]
            
            for url in batch:
                try:
                    logger.info(f"📥 Processing image: {url}")
                    
                    # Download image from URL
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url, timeout=30.0)
                        if response.status_code != 200:
                            raise Exception(f"Failed to download image: {response.status_code}")
                        
                        image_data = response.content
                    logger.info(f"✅ Downloaded image: {len(image_data)} bytes")
                    
                    # Process image
                    processed_image = ImageProcessor.process_image(image_data)
                    logger.info(f"✅ Processed image successfully")
                    
                    # Generate embedding
                    embedding = await openai_service.generate_image_embedding(processed_image)
                    
                    # Generate unique filename and ID
                    image_id = str(uuid.uuid4())
                    filename = f"{image_id}.jpg"
                    
                    # Upload to blob storage
                    blob_url = await blob_service.upload_image(
                        filename,
                        processed_image,
                        metadata={
                            "source_url": url,
                            "indexed_at": datetime.utcnow().isoformat()
                        }
                    )
                    
                    # Index in search service
                    success = await search_service.index_image(
                        image_id=image_id,
                        image_name=filename,
                        image_url=blob_url,
                        blob_name=filename,
                        embedding=embedding,
                        metadata={"source_url": url}
                    )
                    
                    if success:
                        indexed_count += 1
                        logger.info(f"Indexed image {indexed_count}/{len(image_urls)}: {url}")
                    else:
                        failed_count += 1
                        failed_urls.append(url)
                        
                except Exception as e:
                    logger.error(f"Failed to index image {url}: {str(e)}")
                    failed_count += 1
                    failed_urls.append(url)
            
            # Small delay between batches
            await asyncio.sleep(1)
    
    logger.info(f"Indexing completed: {indexed_count} successful, {failed_count} failed")

@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        async with SearchService() as search_service:
            stats = await search_service.get_index_stats()
            return {
                "indexed_images": stats["document_count"],
                "storage_size": stats["storage_size"],
                "status": "operational"
            }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {
            "indexed_images": 0,
            "storage_size": 0,
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)