"""
Configuration module for Azure Image Search Application
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Azure OpenAI Configuration
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str = "gpt-4o"
    azure_openai_embedding_deployment_name: str = "text-embedding-ada-002"
    azure_openai_api_version: str = "2024-10-01-preview"
    
    # Azure Blob Storage Configuration
    azure_storage_connection_string: str
    azure_storage_container: str = "images"
    
    # Azure Cognitive Search Configuration
    azure_search_api_key: str
    azure_search_endpoint: str
    azure_search_index_name: str = "image-index"
    
    # Application Configuration
    max_file_size: int = 20 * 1024 * 1024  # 20MB
    allowed_extensions: list = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]
    embedding_dimensions: int = 1536  # OpenAI CLIP embedding dimensions
    search_top_k: int = 5
    
    # API Configuration
    api_title: str = "Azure Image Search API"
    api_description: str = "Enterprise-grade visual search system with AI-powered explanations"
    api_version: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings 