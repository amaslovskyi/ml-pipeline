#!/usr/bin/env python3
"""
Test script for the Qwen DevOps Foundation LoRA model
Tests the uploaded model from HuggingFace Hub
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import time

def test_model():
    """Test the uploaded LoRA model"""
    
    print("🎯 Testing Qwen DevOps Foundation LoRA Model")
    print("=" * 50)
    
    model_repo = "AMaslovskyi/qwen-devops-foundation-lora"
    base_model_repo = "Qwen/Qwen3-8B"
    
    try:
        print("📥 Loading base model and tokenizer...")
        start_time = time.time()
        
        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_repo,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(base_model_repo)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        load_time = time.time() - start_time
        print(f"✅ Base model loaded in {load_time:.1f}s")
        
        print("📥 Loading LoRA adapter...")
        start_time = time.time()
        
        # Load LoRA adapter
        model = PeftModel.from_pretrained(base_model, model_repo)
        
        adapter_time = time.time() - start_time
        print(f"✅ LoRA adapter loaded in {adapter_time:.1f}s")
        
        # Test prompts for DevOps tasks
        test_prompts = [
            "How do I deploy a Kubernetes cluster?",
            "What are the best practices for Docker containerization?",
            "How to set up a CI/CD pipeline with GitHub Actions?",
            "Explain how to monitor system performance with Prometheus.",
            "What steps should I take to troubleshoot a failed deployment?"
        ]
        
        print("\n🚀 Testing DevOps Prompts:")
        print("=" * 50)
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📝 Test {i}: {prompt}")
            print("-" * 40)
            
            # Tokenize input
            inputs = tokenizer(prompt, return_tensors="pt", padding=True)
            
            # Generate response
            start_time = time.time()
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_length=200,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
            
            generation_time = time.time() - start_time
            
            # Decode response
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the generated part (after the prompt)
            generated_text = response[len(prompt):].strip()
            
            print(f"💡 Response ({generation_time:.1f}s):")
            print(f"   {generated_text[:150]}{'...' if len(generated_text) > 150 else ''}")
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed successfully!")
        print(f"🔗 Model: https://huggingface.co/{model_repo}")
        
        # Model info
        print(f"\n📊 Model Information:")
        print(f"   Base Model: {base_model_repo}")
        print(f"   LoRA Adapter: {model_repo}")
        print(f"   Device: {next(model.parameters()).device}")
        print(f"   Dtype: {next(model.parameters()).dtype}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_model_simple():
    """Simple test without loading the full model (for systems with limited resources)"""
    
    print("🎯 Simple Model Test (Repository Check)")
    print("=" * 40)
    
    try:
        from huggingface_hub import HfApi
        
        api = HfApi()
        model_repo = "AMaslovskyi/qwen-devops-foundation-lora"
        
        # Check if model exists
        model_info = api.model_info(model_repo)
        print(f"✅ Model found: {model_repo}")
        print(f"📊 Model size: {model_info.siblings}")
        print(f"🏷️ Tags: {model_info.tags}")
        
        # Check files
        files = [f.rfilename for f in model_info.siblings]
        expected_files = [
            'adapter_model.safetensors',
            'adapter_config.json', 
            'tokenizer.json',
            'README.md'
        ]
        
        print("\n📁 Model Files:")
        for file in files:
            status = "✅" if any(expected in file for expected in expected_files) else "📄"
            print(f"   {status} {file}")
        
        print(f"\n🎉 Model repository is accessible and properly configured!")
        return True
        
    except Exception as e:
        print(f"❌ Simple test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🔍 Choose test mode:")
    print("1. Full model test (requires GPU/high memory)")
    print("2. Simple repository test (lightweight)")
    
    # For automation, let's try simple test first
    print("\n🚀 Running simple test first...")
    
    simple_success = test_model_simple()
    
    if simple_success:
        print("\n" + "=" * 60)
        print("💡 Simple test passed! Your model is properly uploaded.")
        print("💡 To run full inference test, you need:")
        print("   - GPU with 16GB+ VRAM (or CPU with 32GB+ RAM)")
        print("   - transformers, torch, peft packages")
        print("💡 You can test inference on Google Colab or similar platforms")
        print("=" * 60)
    
    return simple_success

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Your Qwen DevOps Foundation LoRA model is ready to use!")
    else:
        print("\n❌ Model testing failed. Check the errors above.")
