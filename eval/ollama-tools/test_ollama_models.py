#!/usr/bin/env python3
"""
Test and compare Ollama models: base qwen3:8b vs DevOps-optimized qwen-devops
"""

import subprocess
import time
import json

def test_ollama_model(model_name, question, timeout=120):
    """Test a specific Ollama model with a question"""
    try:
        start_time = time.time()
        result = subprocess.run([
            "ollama", "run", model_name, question
        ], capture_output=True, text=True, timeout=timeout)
        
        generation_time = time.time() - start_time
        
        if result.returncode == 0:
            response = result.stdout.strip()
            return {
                "success": True,
                "response": response,
                "time": generation_time,
                "word_count": len(response.split()),
                "char_count": len(response)
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "time": generation_time
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Timeout",
            "time": timeout
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "time": 0
        }

def analyze_devops_content(response):
    """Analyze how DevOps-focused the response is"""
    devops_keywords = {
        "ci_cd": ["ci/cd", "pipeline", "github actions", "jenkins", "build", "deploy", "workflow"],
        "docker": ["docker", "container", "dockerfile", "image", "registry", "compose"],
        "kubernetes": ["kubernetes", "k8s", "pod", "deployment", "service", "kubectl", "helm"],
        "infrastructure": ["terraform", "ansible", "infrastructure", "iac", "provisioning"],
        "monitoring": ["monitoring", "logs", "metrics", "prometheus", "grafana", "alerts"],
        "security": ["security", "secrets", "rbac", "vulnerability", "scanning", "hardening"]
    }
    
    response_lower = response.lower()
    category_scores = {}
    total_keywords = 0
    
    for category, keywords in devops_keywords.items():
        found = [kw for kw in keywords if kw in response_lower]
        category_scores[category] = {
            "found": found,
            "count": len(found)
        }
        total_keywords += len(found)
    
    # Quality indicators
    has_code_examples = "```" in response or "`" in response
    has_commands = any(cmd in response_lower for cmd in ["kubectl", "docker", "terraform", "ansible"])
    mentions_best_practices = any(phrase in response_lower for phrase in ["best practice", "recommendation", "should", "avoid"])
    provides_steps = any(indicator in response_lower for indicator in ["1.", "2.", "step", "first", "then", "next"])
    
    return {
        "devops_keywords_total": total_keywords,
        "category_breakdown": category_scores,
        "quality_indicators": {
            "has_code_examples": has_code_examples,
            "has_commands": has_commands,
            "mentions_best_practices": mentions_best_practices,
            "provides_steps": provides_steps
        },
        "devops_relevance_score": min(total_keywords / 10 * 10, 10)  # Scale to 0-10
    }

def compare_models():
    """Compare base qwen3:8b with DevOps-optimized qwen-devops"""
    
    print("🔍 Ollama Models Comparison: Base vs DevOps-Optimized")
    print("=" * 60)
    
    # Test questions
    test_questions = [
        "How do I deploy a web application to Kubernetes?",
        "What are Docker security best practices for production?",
        "How to set up a CI/CD pipeline with GitHub Actions?",
        "How do I troubleshoot a failing Kubernetes pod?",
        "What is Infrastructure as Code and how to implement it?"
    ]
    
    models = ["qwen3:8b", "qwen-devops"]
    results = {model: [] for model in models}
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"🧪 Test Question {i}/{len(test_questions)}")
        print(f"❓ {question}")
        print("="*60)
        
        for model in models:
            print(f"\n🤖 Testing {model}...")
            
            result = test_ollama_model(model, question, timeout=90)
            
            if result["success"]:
                analysis = analyze_devops_content(result["response"])
                result["analysis"] = analysis
                
                print(f"✅ Response generated in {result['time']:.1f}s")
                print(f"📊 DevOps Relevance: {analysis['devops_relevance_score']:.1f}/10")
                print(f"🔤 Response length: {result['word_count']} words")
                print(f"🎯 DevOps keywords: {analysis['devops_keywords_total']}")
                print(f"💬 Preview: {result['response'][:150]}...")
                
                # Quality indicators
                quality = analysis['quality_indicators']
                indicators = []
                if quality['has_code_examples']: indicators.append("📝 Code")
                if quality['has_commands']: indicators.append("💻 Commands")
                if quality['mentions_best_practices']: indicators.append("🏆 Best Practices")
                if quality['provides_steps']: indicators.append("📋 Step-by-step")
                
                if indicators:
                    print(f"✨ Quality: {', '.join(indicators)}")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                result["analysis"] = None
            
            results[model].append(result)
    
    # Generate comparison summary
    print(f"\n{'='*60}")
    print("📊 COMPARISON SUMMARY")
    print("="*60)
    
    for model in models:
        successful_tests = [r for r in results[model] if r["success"]]
        
        if successful_tests:
            avg_time = sum(r["time"] for r in successful_tests) / len(successful_tests)
            avg_relevance = sum(r["analysis"]["devops_relevance_score"] for r in successful_tests) / len(successful_tests)
            avg_keywords = sum(r["analysis"]["devops_keywords_total"] for r in successful_tests) / len(successful_tests)
            
            print(f"\n🤖 {model}")
            print(f"   ✅ Success rate: {len(successful_tests)}/{len(test_questions)}")
            print(f"   ⏱️ Avg response time: {avg_time:.1f}s")
            print(f"   📊 Avg DevOps relevance: {avg_relevance:.1f}/10")
            print(f"   🎯 Avg DevOps keywords: {avg_keywords:.1f}")
            
            # Quality analysis
            quality_stats = {
                "code_examples": sum(1 for r in successful_tests if r["analysis"]["quality_indicators"]["has_code_examples"]),
                "commands": sum(1 for r in successful_tests if r["analysis"]["quality_indicators"]["has_commands"]),
                "best_practices": sum(1 for r in successful_tests if r["analysis"]["quality_indicators"]["mentions_best_practices"]),
                "step_by_step": sum(1 for r in successful_tests if r["analysis"]["quality_indicators"]["provides_steps"])
            }
            
            print(f"   ✨ Quality indicators:")
            for indicator, count in quality_stats.items():
                percentage = (count / len(successful_tests)) * 100
                print(f"      {indicator.replace('_', ' ').title()}: {count}/{len(successful_tests)} ({percentage:.0f}%)")
        else:
            print(f"\n🤖 {model}")
            print("   ❌ No successful tests")
    
    # Determine winner
    if len(models) == 2:
        base_results = [r for r in results[models[0]] if r["success"]]
        devops_results = [r for r in results[models[1]] if r["success"]]
        
        if base_results and devops_results:
            base_avg_relevance = sum(r["analysis"]["devops_relevance_score"] for r in base_results) / len(base_results)
            devops_avg_relevance = sum(r["analysis"]["devops_relevance_score"] for r in devops_results) / len(devops_results)
            
            print(f"\n🏆 WINNER ANALYSIS:")
            improvement = devops_avg_relevance - base_avg_relevance
            
            if improvement > 1:
                print(f"🥇 {models[1]} wins with +{improvement:.1f} points improvement!")
                print("   🎉 DevOps optimization was highly successful!")
            elif improvement > 0.5:
                print(f"🥈 {models[1]} wins with +{improvement:.1f} points improvement")
                print("   ✅ DevOps optimization shows good results")
            elif improvement > 0:
                print(f"📈 {models[1]} slightly better (+{improvement:.1f} points)")
                print("   🔧 Minor improvement from DevOps optimization")
            else:
                print(f"📊 Models perform similarly (difference: {improvement:+.1f})")
                print("   🤔 DevOps optimization may need refinement")
    
    # Save detailed results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"ollama_comparison_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {filename}")

def quick_demo():
    """Quick demonstration of both models"""
    print("🚀 Quick Demo: DevOps Question")
    print("=" * 35)
    
    question = "How do I deploy to Kubernetes?"
    
    print(f"❓ Question: {question}")
    print(f"🤖 Testing qwen-devops...")
    
    result = test_ollama_model("qwen-devops", question, timeout=60)
    
    if result["success"]:
        analysis = analyze_devops_content(result["response"])
        print(f"✅ Generated in {result['time']:.1f}s")
        print(f"📊 DevOps relevance: {analysis['devops_relevance_score']:.1f}/10")
        print(f"💬 Response preview:")
        print("-" * 40)
        print(result["response"][:300] + "...")
        print("-" * 40)
    else:
        print(f"❌ Failed: {result.get('error')}")

def main():
    """Main function"""
    print("🦙 Ollama DevOps Model Testing Suite")
    print("=" * 40)
    
    # Check available models
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        available_models = result.stdout
        
        has_base = "qwen3:8b" in available_models
        has_devops = "qwen-devops" in available_models
        
        print(f"📦 qwen3:8b (base): {'✅' if has_base else '❌'}")
        print(f"🔧 qwen-devops: {'✅' if has_devops else '❌'}")
        
        if not has_devops:
            print("\n❌ qwen-devops model not found!")
            print("💡 Run: python3 create_ollama_devops_model.py")
            return
        
        print("\nChoose test mode:")
        print("1. Quick demo (1 question)")
        print("2. Full comparison (5 questions)")
        
        try:
            choice = input("\nSelect option (1-2): ").strip()
            
            if choice == "1":
                quick_demo()
            elif choice == "2":
                compare_models()
            else:
                print("❌ Invalid choice")
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
