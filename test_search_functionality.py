#!/usr/bin/env python3
"""
Test Search Functionality
-------------------------
This script tests the image search functionality with a sample image.
"""

import requests
import urllib.request

def test_search_functionality():
    """Test the /search endpoint with a sample image"""
    
    print("🔍 Testing Image Search Functionality")
    print("=" * 50)
    
    # Download a test image (smaller size)
    test_image_url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop"
    print(f"📥 Downloading test image from: {test_image_url}")
    
    try:
        # Download image
        urllib.request.urlretrieve(test_image_url, "test_image.jpg")
        print("✅ Test image downloaded successfully")
        
        # Test the search endpoint
        print("\n🔍 Testing /search endpoint...")
        
        with open("test_image.jpg", "rb") as image_file:
            files = {"file": ("test_image.jpg", image_file, "image/jpeg")}
            data = {"top_k": 5}
            
            response = requests.post(
                "http://localhost:8000/search",
                files=files,
                data=data,
                timeout=120
            )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Search completed successfully!")
            print(f"📝 Message: {result.get('message')}")
            print(f"🖼️ Query filename: {result.get('query_filename')}")
            print(f"📊 Total results: {result.get('total_results')}")
            print(f"⏱️ Processing time: {result.get('processing_time', 0):.2f} seconds")
            
            similar_images = result.get('similar_images', [])
            print(f"\n🎯 Found {len(similar_images)} similar images:")
            
            for i, img in enumerate(similar_images[:3], 1):  # Show top 3
                print(f"\n{i}. Image ID: {img.get('image_id')}")
                print(f"   Similarity Score: {img.get('similarity_score', 0):.3f}")
                print(f"   Image URL: {img.get('image_url', 'N/A')}")
                print(f"   Explanation: {img.get('explanation', 'N/A')[:100]}...")
        
        else:
            print(f"❌ Search failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Clean up
    try:
        import os
        os.remove("test_image.jpg")
        print("\n🧹 Cleaned up test image")
    except:
        pass

def test_upload_functionality():
    """Test the /upload endpoint"""
    
    print("\n📤 Testing Image Upload & Search Functionality")
    print("=" * 50)
    
    test_image_url = "https://images.unsplash.com/photo-1472214103451-9374bd1c798e?w=800&h=600&fit=crop"
    print(f"📥 Downloading test image from: {test_image_url}")
    
    try:
        # Download image
        urllib.request.urlretrieve(test_image_url, "test_upload.jpg")
        print("✅ Test image downloaded successfully")
        
        # Test the upload endpoint
        print("\n📤 Testing /upload endpoint...")
        
        with open("test_upload.jpg", "rb") as image_file:
            files = {"file": ("test_upload.jpg", image_file, "image/jpeg")}
            data = {"top_k": 3}
            
            response = requests.post(
                "http://localhost:8000/upload",
                files=files,
                data=data,
                timeout=120
            )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload completed successfully!")
            print(f"📝 Message: {result.get('message')}")
            print(f"📁 File URL: {result.get('file_url')}")
            print(f"📊 Similar images found: {len(result.get('similar_images', []))}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Clean up
    try:
        import os
        os.remove("test_upload.jpg")
        print("🧹 Cleaned up test image")
    except:
        pass

if __name__ == "__main__":
    print("🧪 Azure Image Search - Functionality Tests")
    print("=" * 50)
    
    # Test search functionality
    test_search_functionality()
    
    # Test upload functionality  
    test_upload_functionality()
    
    print("\n🎉 Testing completed!")
    print("Ready for frontend setup! 🚀") 