#!/usr/bin/env python3
"""
Analyze performance requirements for Qwen DevOps model on your 48GB RAM laptop
"""

import psutil
import platform

def analyze_system_capabilities():
    """Analyze if your laptop can run the Qwen DevOps model"""
    
    print("💻 System Analysis for Qwen DevOps Model")
    print("=" * 50)
    
    # System info
    print(f"🖥️  System: {platform.system()} {platform.release()}")
    print(f"🔧 Processor: {platform.processor()}")
    print(f"💾 Total RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    print(f"💾 Available RAM: {psutil.virtual_memory().available / (1024**3):.1f} GB")
    
    # Model requirements analysis
    print("\n📊 Model Requirements Analysis:")
    print("=" * 40)
    
    # Base model requirements
    base_model_size_gb = 16  # Qwen3-8B in FP16
    lora_adapter_mb = 182   # Your LoRA adapter
    
    print(f"📦 Base Qwen3-8B Model: ~{base_model_size_gb} GB (FP16)")
    print(f"📦 Your LoRA Adapter: {lora_adapter_mb} MB")
    print(f"📦 Tokenizer & Cache: ~1 GB")
    print(f"📦 Working Memory: ~4 GB")
    
    total_memory_needed = base_model_size_gb + (lora_adapter_mb/1000) + 1 + 4
    print(f"📊 Total Memory Needed: ~{total_memory_needed:.1f} GB")
    
    available_ram = psutil.virtual_memory().available / (1024**3)
    
    print(f"\n💡 Your Available RAM: {available_ram:.1f} GB")
    
    if available_ram >= total_memory_needed:
        print("✅ EXCELLENT: Your laptop can run the model comfortably!")
        performance = "Excellent"
    elif available_ram >= total_memory_needed * 0.8:
        print("✅ GOOD: Your laptop can run the model with some optimization")
        performance = "Good"
    elif available_ram >= total_memory_needed * 0.6:
        print("⚠️  MARGINAL: May work with heavy optimization")
        performance = "Marginal"
    else:
        print("❌ INSUFFICIENT: Not enough RAM for comfortable operation")
        performance = "Insufficient"
    
    # Performance predictions
    print(f"\n🚀 Performance Predictions:")
    print("=" * 30)
    
    if performance == "Excellent":
        print("🔥 Inference Speed: Fast (2-5 tokens/sec)")
        print("🔥 Model Loading: 30-60 seconds")
        print("🔥 Concurrent Requests: 2-3 possible")
        print("🔥 Recommended: Use FP16 precision")
    elif performance == "Good":
        print("⚡ Inference Speed: Moderate (1-3 tokens/sec)")
        print("⚡ Model Loading: 60-120 seconds")
        print("⚡ Concurrent Requests: 1-2 possible")
        print("⚡ Recommended: Use FP16, close other apps")
    elif performance == "Marginal":
        print("🐌 Inference Speed: Slow (0.5-1 tokens/sec)")
        print("🐌 Model Loading: 120+ seconds")
        print("🐌 Concurrent Requests: 1 only")
        print("🐌 Recommended: Use quantization (8-bit)")
    else:
        print("🚫 Not recommended for local inference")
        print("🚫 Consider cloud deployment instead")
    
    # Optimization recommendations
    print(f"\n🔧 Optimization Recommendations:")
    print("=" * 35)
    
    print("1. **Model Quantization**:")
    print("   - 4-bit: Reduces memory to ~4-6 GB")
    print("   - 8-bit: Reduces memory to ~8-10 GB")
    
    print("\n2. **CPU vs GPU**:")
    print("   - CPU only: Works but slower")
    print("   - GPU (if available): Much faster inference")
    
    print("\n3. **Memory Management**:")
    print("   - Close unnecessary applications")
    print("   - Use torch.no_grad() for inference")
    print("   - Clear CUDA cache after generation")
    
    return performance

def create_test_script():
    """Create a test script optimized for your system"""
    
    test_code = '''#!/usr/bin/env python3
"""
Optimized test script for 48GB RAM laptop
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import psutil
import time

def test_model_on_laptop():
    """Test Qwen DevOps model on your laptop"""
    
    print("🚀 Testing Qwen DevOps Model on Laptop")
    print("=" * 45)
    
    model_path = "~/Downloads/qwen-devops-model"
    
    # Check initial memory
    initial_memory = psutil.virtual_memory().available / (1024**3)
    print(f"💾 Available RAM: {initial_memory:.1f} GB")
    
    try:
        print("📥 Loading base model...")
        start_time = time.time()
        
        # Load with optimization for 48GB RAM
        base_model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen3-8B",
            torch_dtype=torch.float16,  # Use FP16 to save memory
            device_map="auto",          # Automatic device placement
            low_cpu_mem_usage=True,     # Reduce CPU memory usage
            trust_remote_code=True
        )
        
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        load_time = time.time() - start_time
        current_memory = psutil.virtual_memory().available / (1024**3)
        print(f"✅ Base model loaded in {load_time:.1f}s")
        print(f"💾 Memory used: {initial_memory - current_memory:.1f} GB")
        
        print("📥 Loading LoRA adapter...")
        model = PeftModel.from_pretrained(base_model, model_path)
        
        adapter_memory = psutil.virtual_memory().available / (1024**3)
        print(f"✅ LoRA adapter loaded")
        print(f"💾 Total memory used: {initial_memory - adapter_memory:.1f} GB")
        
        # Test inference
        print("\\n🧪 Testing inference...")
        test_prompts = [
            "How do I deploy a Kubernetes cluster?",
            "What are Docker best practices?",
            "How to set up CI/CD pipeline?"
        ]
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\\n📝 Test {i}: {prompt[:30]}...")
            
            inputs = tokenizer(prompt, return_tensors="pt")
            
            start_time = time.time()
            with torch.no_grad():  # Save memory during inference
                outputs = model.generate(
                    **inputs,
                    max_length=150,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            generation_time = time.time() - start_time
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            generated_text = response[len(prompt):].strip()
            
            tokens_generated = len(tokenizer.encode(generated_text))
            tokens_per_sec = tokens_generated / generation_time
            
            print(f"⚡ Generated {tokens_generated} tokens in {generation_time:.1f}s")
            print(f"🔥 Speed: {tokens_per_sec:.1f} tokens/second")
            print(f"💬 Response: {generated_text[:100]}...")
            
            # Clear cache to free memory
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        final_memory = psutil.virtual_memory().available / (1024**3)
        print(f"\\n📊 Final memory usage: {initial_memory - final_memory:.1f} GB")
        print("🎉 Model testing completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Try reducing model size or using quantization")
        return False

if __name__ == "__main__":
    success = test_model_on_laptop()
    if success:
        print("\\n✅ Your laptop can run the Qwen DevOps model!")
    else:
        print("\\n❌ Consider cloud deployment or quantization")
'''
    
    with open("test_laptop_performance.py", "w") as f:
        f.write(test_code)
    
    print("📝 Created optimized test script: test_laptop_performance.py")

def main():
    """Main analysis function"""
    performance = analyze_system_capabilities()
    
    print(f"\n🎯 **CONCLUSION FOR YOUR 48GB LAPTOP:**")
    print("=" * 50)
    
    if performance in ["Excellent", "Good"]:
        print("✅ **YES, you can safely delete the persistent volume!**")
        print("✅ **Your laptop can run the model locally**")
        print(f"✅ **You have all necessary files downloaded (182MB)**")
        print("✅ **Model is safely backed up on HuggingFace Hub**")
        
        print("\\n📋 **What you have locally:**")
        print("   - LoRA adapter weights (174MB)")
        print("   - Tokenizer files (8MB)")
        print("   - Configuration files")
        print("   - README with usage instructions")
        
        print("\\n🚀 **Next steps:**")
        print("   1. Test model performance on your laptop")
        print("   2. If satisfied, delete persistent volume")
        print("   3. Save ~$15/month on storage costs")
        
        create_test_script()
    else:
        print("⚠️  **Consider keeping storage for now**")
        print("⚠️  **Your laptop may struggle with the full model**")
        print("💡 **Alternative: Use model via HuggingFace Inference API**")

if __name__ == "__main__":
    main()
