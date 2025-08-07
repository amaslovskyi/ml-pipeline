#!/usr/bin/env python3
"""
Simple chat client for the Qwen DevOps Foundation Server
"""

import requests
import json
import time
from typing import Optional

class QwenDevOpsClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        
    def health_check(self) -> dict:
        """Check if the server is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status": "unavailable"}
    
    def chat(self, message: str, max_length: int = 512, temperature: float = 0.7, system_prompt: Optional[str] = None) -> dict:
        """Send a chat message to the model"""
        payload = {
            "message": message,
            "max_length": max_length,
            "temperature": temperature
        }
        
        if system_prompt:
            payload["system_prompt"] = system_prompt
        
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
                
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

def interactive_chat():
    """Run interactive chat session"""
    client = QwenDevOpsClient()
    
    print("🤖 Qwen DevOps Foundation - Interactive Chat")
    print("=" * 45)
    
    # Check server health
    print("🔍 Checking server health...")
    health = client.health_check()
    
    if "error" in health:
        print(f"❌ Server not available: {health['error']}")
        print("💡 Make sure to run: ./run_direct_server.sh")
        return
    
    print(f"✅ Server status: {health.get('status', 'unknown')}")
    print(f"📊 Model loaded: {health.get('model_loaded', False)}")
    print(f"🖥️  Device: {health.get('device', 'unknown')}")
    print()
    
    print("💬 Chat started! Type 'quit' to exit")
    print("🔧 Commands: 'quit', 'help', 'settings'")
    print("-" * 45)
    
    # Default settings
    max_length = 512
    temperature = 0.7
    
    while True:
        try:
            user_input = input("\n🧑 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            elif user_input.lower() == 'help':
                print("\n🔧 Available commands:")
                print("  quit/exit/q - Exit chat")
                print("  help - Show this help")
                print("  settings - Adjust generation settings")
                print("  health - Check server health")
                continue
            
            elif user_input.lower() == 'settings':
                print(f"\n⚙️  Current settings:")
                print(f"   Max length: {max_length}")
                print(f"   Temperature: {temperature}")
                
                try:
                    new_length = input(f"New max length ({max_length}): ").strip()
                    if new_length:
                        max_length = int(new_length)
                    
                    new_temp = input(f"New temperature ({temperature}): ").strip()
                    if new_temp:
                        temperature = float(new_temp)
                    
                    print("✅ Settings updated!")
                except ValueError:
                    print("❌ Invalid input, keeping current settings")
                continue
            
            elif user_input.lower() == 'health':
                health = client.health_check()
                print(f"\n📊 Server health: {json.dumps(health, indent=2)}")
                continue
            
            elif not user_input:
                continue
            
            # Send chat message
            print("🤖 Assistant: ", end="", flush=True)
            start_time = time.time()
            
            result = client.chat(
                message=user_input,
                max_length=max_length,
                temperature=temperature
            )
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                response_time = time.time() - start_time
                response = result.get('response', 'No response')
                tokens = result.get('tokens_generated', 0)
                gen_time = result.get('generation_time', 0)
                
                print(response)
                print(f"\n📊 Stats: {tokens} tokens, {gen_time:.1f}s generation, {response_time:.1f}s total")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")

def test_devops_questions():
    """Test with common DevOps questions"""
    client = QwenDevOpsClient()
    
    print("🧪 Testing Qwen DevOps Foundation")
    print("=" * 35)
    
    # Check health first
    health = client.health_check()
    if "error" in health:
        print(f"❌ Server not available: {health['error']}")
        return
    
    test_questions = [
        "How do I deploy a simple web app to Kubernetes?",
        "What are Docker best practices for production?",
        "How to set up a CI/CD pipeline with GitHub Actions?",
        "Explain blue-green deployment strategy",
        "How to monitor Kubernetes cluster health?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Test {i}: {question}")
        print("-" * 50)
        
        result = client.chat(question, max_length=300, temperature=0.7)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            response = result.get('response', 'No response')
            tokens = result.get('tokens_generated', 0)
            gen_time = result.get('generation_time', 0)
            
            print(f"🤖 Response: {response}")
            print(f"📊 {tokens} tokens in {gen_time:.1f}s")

def main():
    """Main function"""
    print("🚀 Qwen DevOps Foundation Client")
    print("=" * 35)
    print("1. Interactive chat")
    print("2. Run test questions")
    print("3. Check server health")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        interactive_chat()
    elif choice == "2":
        test_devops_questions()
    elif choice == "3":
        client = QwenDevOpsClient()
        health = client.health_check()
        print(f"\n📊 Server health:\n{json.dumps(health, indent=2)}")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
