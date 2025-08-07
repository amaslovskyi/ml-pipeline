#!/usr/bin/env python3
"""
Quick DevOps Model Performance Test
Fast evaluation with essential DevOps questions
"""

import os
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

def quick_devops_test():
    """Quick test of DevOps model performance"""
    
    print("🚀 Quick DevOps Model Test")
    print("=" * 30)
    
    # Test questions
    test_questions = [
        "How do I deploy a simple web app to Kubernetes?",
        "What are Docker best practices for production?",
        "How to set up a CI/CD pipeline with GitHub Actions?",
        "How do I troubleshoot a failing Kubernetes pod?",
        "What is Infrastructure as Code and why use it?"
    ]
    
    expected_answers = [
        ["deployment", "service", "kubectl", "replicas"],
        ["security", "minimal", "non-root", "scan"],
        ["workflow", "build", "test", "deploy"],
        ["logs", "describe", "events", "status"],
        ["terraform", "version control", "automation", "reproducible"]
    ]
    
    # Load model
    print("📥 Loading model...")
    local_model_path = os.path.expanduser("~/Downloads/qwen-devops-model")
    
    try:
        # Load base model on CPU
        base_model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen3-8B",
            torch_dtype=torch.float16,
            device_map="cpu",
            trust_remote_code=True
        )
        
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load LoRA adapter
        model = PeftModel.from_pretrained(base_model, local_model_path)
        print("✅ Model loaded successfully!")
        
    except Exception as e:
        print(f"❌ Failed to load model: {str(e)}")
        return
    
    # Test each question
    total_score = 0
    total_time = 0
    
    for i, (question, expected) in enumerate(zip(test_questions, expected_answers), 1):
        print(f"\n🔍 Test {i}/5: {question}")
        
        # Format prompt
        formatted_prompt = f"<|im_start|>system\nYou are a DevOps expert. Provide practical advice with examples.<|im_end|>\n<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant\n"
        
        # Generate response
        start_time = time.time()
        inputs = tokenizer(formatted_prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=300,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        generation_time = time.time() - start_time
        total_time += generation_time
        
        # Decode response
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response = full_response[len(formatted_prompt):].strip()
        
        if response.endswith("<|im_end|>"):
            response = response[:-10].strip()
        
        # Check accuracy
        response_lower = response.lower()
        keywords_found = [kw for kw in expected if kw.lower() in response_lower]
        accuracy = len(keywords_found) / len(expected)
        total_score += accuracy
        
        # Display results
        print(f"⏱️  Generation time: {generation_time:.1f}s")
        print(f"🎯 Keywords found: {keywords_found}")
        print(f"📊 Accuracy: {accuracy:.2f}")
        print(f"💬 Response: {response[:150]}...")
        
        # Score indicator
        if accuracy >= 0.8:
            print("🏆 Excellent!")
        elif accuracy >= 0.6:
            print("✅ Good!")
        elif accuracy >= 0.4:
            print("⚠️  Fair")
        else:
            print("❌ Needs improvement")
    
    # Final results
    avg_score = total_score / len(test_questions)
    avg_time = total_time / len(test_questions)
    
    print(f"\n" + "=" * 40)
    print("🎯 QUICK TEST RESULTS")
    print("=" * 40)
    print(f"📊 Average Accuracy: {avg_score:.2f}")
    print(f"⏱️  Average Time: {avg_time:.1f}s per question")
    print(f"🔥 Total Time: {total_time:.1f}s")
    
    if avg_score >= 0.8:
        print("🏆 EXCELLENT: Your model performs very well on DevOps tasks!")
    elif avg_score >= 0.6:
        print("✅ GOOD: Your model shows solid DevOps knowledge!")
    elif avg_score >= 0.4:
        print("⚠️  FAIR: Your model has basic DevOps understanding")
    else:
        print("❌ NEEDS WORK: Consider additional training")
    
    # Performance assessment
    if avg_time <= 5:
        print("⚡ FAST: Great inference speed!")
    elif avg_time <= 10:
        print("🚀 MODERATE: Reasonable inference speed")
    else:
        print("🐌 SLOW: Consider optimization")

if __name__ == "__main__":
    quick_devops_test()
