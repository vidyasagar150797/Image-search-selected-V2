#!/usr/bin/env python3
"""
Image Indexing Script for Azure Search
-------------------------------------
This script reads URLs from photos_url.csv and indexes them using the FastAPI /index endpoint.
The endpoint handles: download, embedding generation, blob upload, and search indexing.

Usage:
    python index_images.py
"""

import pandas as pd
import requests
import json
import time
from datetime import datetime

def index_images_batch(num_images=250, api_url="http://localhost:8000", batch_size=10):
    """
    Index images using the FastAPI /index endpoint
    
    Args:
        num_images: Number of images to index (default: 250)
        api_url: FastAPI server URL (default: http://localhost:8000)
        batch_size: Images per batch request (default: 10)
    """
    print(f"🚀 Starting image indexing process...")
    print(f"📊 Target: {num_images} images")
    print(f"🔗 API URL: {api_url}")
    print(f"📦 Batch size: {batch_size}")
    print("-" * 50)
    
    # Read CSV file
    try:
        df = pd.read_csv("photos_url.csv")
        print(f"✅ Loaded CSV with {len(df)} total images")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return
    
    # Take first N images
    if num_images:
        df = df.head(num_images)
    
    # Get image URLs
    image_urls = df['photo_image_url'].tolist()
    print(f"📋 Selected {len(image_urls)} images for indexing")
    
    # Test API health first
    try:
        response = requests.get(f"{api_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API is healthy and ready")
        else:
            print(f"⚠️ API health check returned: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    # Process images in batches
    total_batches = (len(image_urls) + batch_size - 1) // batch_size
    start_time = time.time()
    
    for batch_num in range(total_batches):
        batch_start = batch_num * batch_size
        batch_end = min(batch_start + batch_size, len(image_urls))
        batch_urls = image_urls[batch_start:batch_end]
        
        print(f"\n📦 Processing batch {batch_num + 1}/{total_batches}")
        print(f"   Images {batch_start + 1}-{batch_end} of {len(image_urls)}")
        
        # Prepare request payload
        payload = {
            "image_urls": batch_urls,
            "batch_size": batch_size
        }
        
        try:
            # Send indexing request
            batch_start_time = time.time()
            response = requests.post(
                f"{api_url}/index", 
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=300  # 5 minutes timeout per batch
            )
            
            batch_time = time.time() - batch_start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Batch submitted successfully")
                print(f"   📝 Message: {result.get('message', 'N/A')}")
                print(f"   ⏱️ Batch time: {batch_time:.2f} seconds")
            else:
                print(f"   ❌ Batch failed: {response.status_code}")
                print(f"   📝 Response: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Batch timed out (this is normal for large batches)")
            print(f"   🔄 Processing continues in background")
        except Exception as e:
            print(f"   ❌ Batch error: {e}")
        
        # Wait between batches to respect Azure OpenAI rate limits
        if batch_num < total_batches - 1:
            print(f"   ⏳ Waiting 20 seconds before next batch (rate limit protection)...")
            time.sleep(20)
    
    total_time = time.time() - start_time
    print("\n" + "=" * 50)
    print("🎉 Indexing process completed!")
    print(f"⏱️ Total time: {total_time/60:.2f} minutes")
    print(f"📊 Processed: {len(image_urls)} images")
    print(f"💡 Note: Indexing continues in background")
    print("💡 Use GET /stats to check indexing progress")
    print("=" * 50)

def check_indexing_stats(api_url="http://localhost:8000"):
    """Check current indexing statistics"""
    try:
        response = requests.get(f"{api_url}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print("\n📊 Current Index Statistics:")
            print(f"   📸 Indexed images: {stats.get('indexed_images', 0)}")
            print(f"   💾 Storage size: {stats.get('storage_size', 0)}")
            print(f"   🔴 Status: {stats.get('status', 'unknown')}")
        else:
            print(f"❌ Stats request failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting stats: {e}")

if __name__ == "__main__":
    print("🖼️ Azure Image Search - Batch Indexing Tool")
    print("=" * 50)
    
    # Check current stats first
    check_indexing_stats()
    
    # Start indexing  
    index_images_batch(num_images=100, batch_size=3)  # 100 images, smaller batches for rate limits
    
    # Check stats after
    print("\n🔍 Checking final statistics...")
    time.sleep(5)  # Wait a bit for processing
    check_indexing_stats() 