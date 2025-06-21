"""
Image processing utilities
"""
import os
import uuid
from typing import Tuple, Optional
from PIL import Image
import io
import base64
from fastapi import UploadFile, HTTPException

class ImageProcessor:
    """Image processing utilities"""
    
    @staticmethod
    def validate_image(file: UploadFile, max_size: int = 10 * 1024 * 1024) -> None:
        """
        Validate uploaded image file
        
        Args:
            file: FastAPI UploadFile object
            max_size: Maximum file size in bytes
            
        Raises:
            HTTPException: If validation fails
        """
        # Check file extension
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
            
        ext = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
        
        if ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {ext} not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        # Check file size
        if hasattr(file, 'size') and file.size and file.size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size {file.size} exceeds maximum allowed size {max_size}"
            )
    
    @staticmethod
    def process_image(image_data: bytes, target_size: Tuple[int, int] = (800, 800)) -> bytes:
        """
        Process and optimize image
        
        Args:
            image_data: Raw image bytes
            target_size: Target dimensions (maintains aspect ratio)
            
        Returns:
            Processed image bytes
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Resize while maintaining aspect ratio
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            output_buffer = io.BytesIO()
            image.save(output_buffer, format='JPEG', quality=85, optimize=True)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")
    
    @staticmethod
    def image_to_base64(image_data: bytes) -> str:
        """Convert image bytes to base64 string"""
        return base64.b64encode(image_data).decode('utf-8')
    
    @staticmethod
    def base64_to_image(base64_string: str) -> bytes:
        """Convert base64 string to image bytes"""
        try:
            return base64.b64decode(base64_string)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {str(e)}")
    
    @staticmethod
    def generate_filename(original_filename: str) -> str:
        """Generate unique filename while preserving extension"""
        ext = os.path.splitext(original_filename)[1].lower()
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{ext}"
    
    @staticmethod
    def get_image_metadata(image_data: bytes) -> dict:
        """Extract basic metadata from image"""
        try:
            image = Image.open(io.BytesIO(image_data))
            return {
                'width': image.width,
                'height': image.height,
                'format': image.format,
                'mode': image.mode,
                'size_bytes': len(image_data)
            }
        except Exception:
            return {} 