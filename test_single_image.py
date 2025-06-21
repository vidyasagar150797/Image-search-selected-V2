#!/usr/bin/env python3
"""
Test Single Image Indexing
--------------------------
This script tests indexing a single image to debug issues.
"""

import requests
import json

def test_single_image():
    """Test indexing a single image"""
    
    # Use the first image from your CSV
    test_url = "https://images.unsplash.com/uploads/1413387620228d142bee4/23eceb86"
    
    payload = {
        "image_urls": [test_url],
        "batch_size": 1
    }
    
    print(f"🧪 Testing single image indexing...")
    print(f"📷 Image URL: {test_url}")
    print("-" * 50)
    
    try:
        response = requests.post(
            "http://localhost:8000/index",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutes timeout
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📝 Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Request submitted successfully")
            print("⏳ Wait 30 seconds for background processing...")
            
            # Wait and check stats
            import time
            time.sleep(30)
            
            stats_response = requests.get("http://localhost:8000/stats")
            print(f"📈 Stats after processing: {stats_response.text}")
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_single_image() 