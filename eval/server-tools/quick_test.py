#!/usr/bin/env python3
"""
Quick test for the inference server
"""

import requests
import time
import json

def test_server():
    """Test if the server is working"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Qwen DevOps Server")
    print("=" * 30)
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get(f"{base_url}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                break
        except:
            time.sleep(1)
            print(f"   Waiting... ({i+1}/30)")
    else:
        print("❌ Server didn't start in time")
        return False
    
    # Test health endpoint
    print("\n🔍 Health check:")
    try:
        health = requests.get(f"{base_url}/health").json()
        print(f"   Status: {health.get('status')}")
        print(f"   Model loaded: {health.get('model_loaded')}")
        print(f"   Device: {health.get('device')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test chat endpoint
    print("\n💬 Testing chat:")
    try:
        test_message = "How do I deploy to Kubernetes?"
        payload = {
            "message": test_message,
            "max_length": 200,
            "temperature": 0.7
        }
        
        print(f"   Question: {test_message}")
        response = requests.post(f"{base_url}/chat", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Response: {result['response'][:100]}...")
            print(f"   📊 {result['tokens_generated']} tokens in {result['generation_time']:.1f}s")
            return True
        else:
            print(f"❌ Chat failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    if success:
        print("\n🎉 Server is working perfectly!")
        print("🔗 Try the interactive client: python3 chat_client.py")
    else:
        print("\n❌ Server test failed")
