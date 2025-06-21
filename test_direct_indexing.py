#!/usr/bin/env python3
"""
Direct Indexing Test
-------------------
This script tests the core indexing functionality synchronously to identify issues.
"""

import asyncio
import uuid
from datetime import datetime
import httpx
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.azure_openai_service import AzureOpenAIService
from app.services.blob_service import BlobStorageService  
from app.services.search_service import SearchService
from app.utils.image_utils import ImageProcessor

async def test_direct_indexing():
    """Test indexing directly without background tasks"""
    
    test_url = "https://images.unsplash.com/uploads/1413387620228d142bee4/23eceb86"
    
    print(f"🧪 Direct indexing test")
    print(f"📷 Image URL: {test_url}")
    print("-" * 50)
    
    try:
        print("1️⃣ Downloading image...")
        async with httpx.AsyncClient() as client:
            response = await client.get(test_url, timeout=30.0)
            if response.status_code != 200:
                raise Exception(f"Failed to download: {response.status_code}")
            image_data = response.content
        print(f"✅ Downloaded: {len(image_data)} bytes")
        
        print("2️⃣ Processing image...")
        processed_image = ImageProcessor.process_image(image_data)
        print(f"✅ Processed image successfully")
        
        print("3️⃣ Initializing Azure services...")
        async with (
            AzureOpenAIService() as openai_service,
            BlobStorageService() as blob_service,
            SearchService() as search_service
        ):
            print("✅ Services initialized")
            
            print("4️⃣ Generating embedding...")
            embedding = await openai_service.generate_image_embedding(processed_image)
            print(f"✅ Generated embedding: {len(embedding)} dimensions")
            
            print("5️⃣ Uploading to blob storage...")
            image_id = str(uuid.uuid4())
            filename = f"{image_id}.jpg"
            
            blob_url = await blob_service.upload_image(
                filename,
                processed_image,
                metadata={
                    "source_url": test_url,
                    "indexed_at": datetime.utcnow().isoformat()
                }
            )
            print(f"✅ Uploaded to blob: {blob_url}")
            
            print("6️⃣ Indexing in search service...")
            success = await search_service.index_image(
                image_id=image_id,
                image_name=filename,
                image_url=blob_url,
                blob_name=filename,
                embedding=embedding,
                metadata={"source_url": test_url}
            )
            
            if success:
                print("✅ Successfully indexed!")
                
                print("7️⃣ Checking index stats...")
                stats = await search_service.get_index_stats()
                print(f"📊 Index stats: {stats}")
                
            else:
                print("❌ Failed to index image")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔧 Direct Azure Indexing Test")
    print("=" * 50)
    asyncio.run(test_direct_indexing()) 