#!/usr/bin/env python3
"""
Reset Search Index Script
-------------------------
This script deletes the existing search index so it can be recreated with proper vector configuration.

Usage:
    python reset_search_index.py
"""

import asyncio
from azure.search.documents.indexes.aio import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def reset_search_index():
    """Delete the existing search index"""
    
    # Get configuration from environment
    api_key = os.getenv("AZURE_SEARCH_API_KEY")
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT") 
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "image-index")
    
    if not api_key or not endpoint:
        print("❌ Missing Azure Search credentials in .env file")
        return
    
    print(f"🔧 Resetting search index: {index_name}")
    print(f"🔗 Endpoint: {endpoint}")
    print("-" * 50)
    
    # Create search index client
    credential = AzureKeyCredential(api_key)
    async with SearchIndexClient(endpoint=endpoint, credential=credential) as client:
        try:
            # Check if index exists
            await client.get_index(index_name)
            print(f"✅ Found existing index: {index_name}")
            
            # Delete the index
            print(f"🗑️ Deleting index: {index_name}")
            await client.delete_index(index_name)
            print(f"✅ Successfully deleted index: {index_name}")
            print("💡 The index will be recreated automatically on next API call")
            
        except ResourceNotFoundError:
            print(f"ℹ️ Index {index_name} does not exist - nothing to delete")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("🔄 Azure Search Index Reset Tool")
    print("=" * 50)
    asyncio.run(reset_search_index())
    print("=" * 50)
    print("✅ Reset complete! Restart your FastAPI server to recreate the index.") 