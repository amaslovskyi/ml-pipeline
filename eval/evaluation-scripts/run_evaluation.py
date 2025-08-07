#!/usr/bin/env python3
"""
Simple evaluation runner - runs all tests and generates final report
"""

import os
import sys
import subprocess
import time
from datetime import datetime

def run_command(command, description, timeout=300):
    """Run a command with timeout and error handling"""
    print(f"\n🔄 {description}")
    print(f"💻 Running: {command}")
    print("-" * 50)
    
    try:
        start_time = time.time()
        result = subprocess.run(
            command.split(), 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(result.stdout)
            print(f"✅ Completed in {duration:.1f}s")
            return True, result.stdout
        else:
            print(f"❌ Error: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout after {timeout}s")
        return False, "Timeout"
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False, str(e)

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking Requirements")
    print("=" * 30)
    
    # Check model files
    model_path = os.path.expanduser("~/Downloads/qwen-devops-model")
    if os.path.exists(model_path):
        print("✅ Model files found")
    else:
        print("❌ Model files not found at ~/Downloads/qwen-devops-model")
        return False
    
    # Check Python packages
    try:
        import torch
        import transformers
        import peft
        print("✅ Python packages available")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False
    
    # Check system resources
    try:
        import psutil
        available_gb = psutil.virtual_memory().available / (1024**3)
        if available_gb >= 20:
            print(f"✅ Sufficient RAM: {available_gb:.1f}GB")
        else:
            print(f"⚠️ Low RAM: {available_gb:.1f}GB (need 20GB+)")
    except:
        print("⚠️ Cannot check RAM")
    
    return True

def run_full_evaluation():
    """Run complete evaluation suite"""
    
    print("🔬 DevOps Model Evaluation Suite")
    print("=" * 40)
    print(f"🕒 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not check_requirements():
        print("❌ Requirements not met. Exiting.")
        return
    
    results = {}
    
    # 1. System Analysis
    success, output = run_command(
        "python3 laptop_performance_analysis.py",
        "System Compatibility Analysis",
        timeout=60
    )
    results["system_analysis"] = success
    
    # 2. Quick Performance Test
    success, output = run_command(
        "python3 quick_devops_test.py", 
        "Quick DevOps Performance Test",
        timeout=600
    )
    results["quick_test"] = success
    if success and "Average Accuracy:" in output:
        # Extract accuracy score
        try:
            accuracy_line = [line for line in output.split('\n') if 'Average Accuracy:' in line][0]
            accuracy = float(accuracy_line.split(':')[1].strip())
            results["accuracy"] = accuracy
        except:
            results["accuracy"] = None
    
    # 3. Model Comparison (if Ollama available)
    print("\n🔍 Checking for Ollama and base model...")
    try:
        ollama_check = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if ollama_check.returncode == 0 and "qwen3:8b" in ollama_check.stdout:
            print("✅ Ollama and qwen3:8b found")
            success, output = run_command(
                "python3 model_comparison.py",
                "Model Comparison vs Base Qwen3",
                timeout=900
            )
            results["comparison"] = success
        else:
            print("⚠️ Ollama or qwen3:8b not available, skipping comparison")
            results["comparison"] = "skipped"
    except:
        print("⚠️ Ollama not available, skipping comparison")
        results["comparison"] = "skipped"
    
    # 4. Generate Final Report
    success, output = run_command(
        "python3 performance_report.py",
        "Generate Performance Report",
        timeout=60
    )
    results["report"] = success
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 EVALUATION SUMMARY")
    print("=" * 50)
    
    total_tests = sum(1 for v in results.values() if v is True)
    print(f"✅ Tests Completed: {total_tests}")
    
    if results.get("system_analysis"):
        print("✅ System analysis completed")
    
    if results.get("quick_test"):
        accuracy = results.get("accuracy")
        if accuracy:
            if accuracy >= 0.7:
                rating = "🏆 Excellent"
            elif accuracy >= 0.6:
                rating = "✅ Good"
            elif accuracy >= 0.5:
                rating = "⚠️ Fair"
            else:
                rating = "❌ Needs Work"
            print(f"✅ Quick test: {accuracy:.2f} accuracy ({rating})")
        else:
            print("✅ Quick test completed")
    
    if results.get("comparison") == True:
        print("✅ Model comparison completed")
    elif results.get("comparison") == "skipped":
        print("⚠️ Model comparison skipped (Ollama unavailable)")
    
    if results.get("report"):
        print("✅ Performance report generated")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 20)
    
    if results.get("accuracy"):
        accuracy = results["accuracy"]
        if accuracy >= 0.7:
            print("🎉 Excellent performance! Ready for production use.")
        elif accuracy >= 0.6:
            print("✅ Good performance! Ready for internal team use.")
            print("🎯 Consider additional training for weak areas.")
        elif accuracy >= 0.5:
            print("⚠️ Fair performance. Good for basic DevOps assistance.")
            print("📚 Recommend additional training data.")
        else:
            print("❌ Performance needs improvement.")
            print("🔧 Consider retraining with more diverse data.")
    
    print(f"\n📁 Check generated files:")
    print("   - Performance report JSON")
    print("   - Comparison results (if available)")
    print("   - Individual test outputs")
    
    print(f"\n🕒 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    run_full_evaluation()
