#!/usr/bin/env python3
"""
Compare your fine-tuned DevOps model against base Qwen3:8b model
"""

import subprocess
import time
import requests
import json

def test_ollama_model(model_name: str, question: str) -> dict:
    """Test a question with Ollama model"""
    try:
        start_time = time.time()
        result = subprocess.run([
            "ollama", "run", model_name, question
        ], capture_output=True, text=True, timeout=60)
        
        generation_time = time.time() - start_time
        
        if result.returncode == 0:
            return {
                "success": True,
                "response": result.stdout.strip(),
                "time": generation_time,
                "error": None
            }
        else:
            return {
                "success": False,
                "response": "",
                "time": generation_time,
                "error": result.stderr
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "response": "",
            "time": 60,
            "error": "Timeout"
        }
    except Exception as e:
        return {
            "success": False,
            "response": "",
            "time": 0,
            "error": str(e)
        }

def test_api_model(question: str) -> dict:
    """Test a question with your API model"""
    try:
        start_time = time.time()
        payload = {
            "message": question,
            "max_length": 300,
            "temperature": 0.7
        }
        
        response = requests.post(
            "http://localhost:8000/chat",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "response": result['response'],
                "time": result['generation_time'],
                "tokens": result.get('tokens_generated', 0),
                "error": None
            }
        else:
            return {
                "success": False,
                "response": "",
                "time": time.time() - start_time,
                "error": f"HTTP {response.status_code}"
            }
    except Exception as e:
        return {
            "success": False,
            "response": "",
            "time": time.time() - start_time,
            "error": str(e)
        }

def evaluate_devops_relevance(response: str) -> dict:
    """Evaluate how DevOps-relevant a response is"""
    devops_keywords = [
        # Kubernetes
        "kubernetes", "k8s", "pod", "deployment", "service", "ingress", "helm",
        # Docker
        "docker", "container", "dockerfile", "image", "registry",
        # CI/CD
        "ci/cd", "pipeline", "jenkins", "github actions", "gitlab", "build", "deploy",
        # Infrastructure
        "terraform", "ansible", "infrastructure", "cloud", "aws", "azure", "gcp",
        # Monitoring
        "prometheus", "grafana", "monitoring", "logs", "metrics", "alerts",
        # Security
        "security", "secrets", "rbac", "vulnerability", "scan"
    ]
    
    response_lower = response.lower()
    found_keywords = [kw for kw in devops_keywords if kw in response_lower]
    
    # Quality indicators
    has_commands = bool(any(cmd in response_lower for cmd in ["kubectl", "docker", "terraform", "ansible"]))
    has_yaml = "yaml" in response_lower or "yml" in response_lower
    has_code = "```" in response or "`" in response
    mentions_best_practices = "best practice" in response_lower or "recommendation" in response_lower
    
    relevance_score = len(found_keywords) / len(devops_keywords) * 10  # Scale to 0-10
    
    return {
        "relevance_score": min(relevance_score, 10),
        "keywords_found": found_keywords,
        "quality_indicators": {
            "has_commands": has_commands,
            "has_yaml": has_yaml,
            "has_code": has_code,
            "mentions_best_practices": mentions_best_practices
        }
    }

def compare_models():
    """Compare your fine-tuned model against base Qwen3"""
    
    print("🔍 DevOps Model Comparison Test")
    print("=" * 40)
    
    # Test questions
    test_questions = [
        "How do I deploy a web application to Kubernetes?",
        "What are Docker security best practices?",
        "How to set up a CI/CD pipeline?",
        "How do I troubleshoot pod failures?",
        "What is Infrastructure as Code?"
    ]
    
    # Check available models
    print("🔍 Checking available models...")
    
    # Check Ollama models
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        ollama_available = "qwen3:8b" in result.stdout
        print(f"📦 Ollama qwen3:8b: {'✅ Available' if ollama_available else '❌ Not available'}")
    except:
        ollama_available = False
        print("📦 Ollama qwen3:8b: ❌ Ollama not available")
    
    # Check API model
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        api_available = response.status_code == 200
        print(f"🔗 Your fine-tuned model API: {'✅ Available' if api_available else '❌ Not available'}")
    except:
        api_available = False
        print("🔗 Your fine-tuned model API: ❌ Not available")
    
    if not (ollama_available or api_available):
        print("❌ No models available for testing")
        return
    
    # Run comparison tests
    results = []
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*50}")
        print(f"🧪 Test {i}/{len(test_questions)}")
        print(f"❓ Question: {question}")
        print("="*50)
        
        test_result = {"question": question}
        
        # Test base Qwen3:8b
        if ollama_available:
            print("\n🤖 Testing Base Qwen3:8b...")
            base_result = test_ollama_model("qwen3:8b", f"As a DevOps expert, {question}")
            
            if base_result["success"]:
                base_eval = evaluate_devops_relevance(base_result["response"])
                test_result["base_model"] = {
                    "response": base_result["response"],
                    "time": base_result["time"],
                    "evaluation": base_eval
                }
                
                print(f"⏱️  Time: {base_result['time']:.1f}s")
                print(f"🎯 DevOps Relevance: {base_eval['relevance_score']:.1f}/10")
                print(f"💬 Response: {base_result['response'][:100]}...")
            else:
                print(f"❌ Error: {base_result['error']}")
                test_result["base_model"] = {"error": base_result["error"]}
        
        # Test your fine-tuned model
        if api_available:
            print("\n🔧 Testing Your Fine-tuned Model...")
            api_result = test_api_model(question)
            
            if api_result["success"]:
                api_eval = evaluate_devops_relevance(api_result["response"])
                test_result["fine_tuned_model"] = {
                    "response": api_result["response"],
                    "time": api_result["time"],
                    "tokens": api_result.get("tokens", 0),
                    "evaluation": api_eval
                }
                
                print(f"⏱️  Time: {api_result['time']:.1f}s")
                print(f"🎯 DevOps Relevance: {api_eval['relevance_score']:.1f}/10")
                print(f"💬 Response: {api_result['response'][:100]}...")
            else:
                print(f"❌ Error: {api_result['error']}")
                test_result["fine_tuned_model"] = {"error": api_result["error"]}
        
        results.append(test_result)
    
    # Summary comparison
    print(f"\n{'='*60}")
    print("📊 COMPARISON SUMMARY")
    print("="*60)
    
    base_scores = []
    fine_tuned_scores = []
    base_times = []
    fine_tuned_times = []
    
    for result in results:
        if "base_model" in result and "evaluation" in result["base_model"]:
            base_scores.append(result["base_model"]["evaluation"]["relevance_score"])
            base_times.append(result["base_model"]["time"])
        
        if "fine_tuned_model" in result and "evaluation" in result["fine_tuned_model"]:
            fine_tuned_scores.append(result["fine_tuned_model"]["evaluation"]["relevance_score"])
            fine_tuned_times.append(result["fine_tuned_model"]["time"])
    
    if base_scores:
        avg_base_score = sum(base_scores) / len(base_scores)
        avg_base_time = sum(base_times) / len(base_times)
        print(f"🤖 Base Qwen3:8b - Avg Relevance: {avg_base_score:.1f}/10, Avg Time: {avg_base_time:.1f}s")
    
    if fine_tuned_scores:
        avg_fine_tuned_score = sum(fine_tuned_scores) / len(fine_tuned_scores)
        avg_fine_tuned_time = sum(fine_tuned_times) / len(fine_tuned_times)
        print(f"🔧 Your Fine-tuned Model - Avg Relevance: {avg_fine_tuned_score:.1f}/10, Avg Time: {avg_fine_tuned_time:.1f}s")
        
        if base_scores:
            improvement = avg_fine_tuned_score - avg_base_score
            if improvement > 1:
                print(f"🏆 EXCELLENT: Your model shows significant improvement (+{improvement:.1f} points)!")
            elif improvement > 0.5:
                print(f"✅ GOOD: Your model shows solid improvement (+{improvement:.1f} points)")
            elif improvement > 0:
                print(f"📈 SLIGHT: Your model shows minor improvement (+{improvement:.1f} points)")
            else:
                print(f"📊 Your model performs similarly to base model ({improvement:+.1f} points)")
    
    # Save detailed results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"model_comparison_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Detailed results saved to: {filename}")

if __name__ == "__main__":
    compare_models()
