#!/usr/bin/env python3
"""
Local Inference Setup for Qwen DevOps Foundation Model
======================================================

This script sets up local inference on your M4 Pro MacBook for the trained
Qwen foundational model optimized for DevOps/SRE tasks.

Features:
- Downloads and sets up the trained model locally
- Optimizes for Apple Silicon (M4 Pro)
- Provides a simple CLI interface for testing
- Implements proper memory management and quantization
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

def check_dependencies():
    """Check if all required packages are installed."""
    required_packages = [
        'torch',
        'transformers',
        'accelerate',
        'bitsandbytes',
        'peft'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n🔧 Installing missing packages: {', '.join(missing_packages)}")
        
        # Install packages optimized for Apple Silicon
        install_cmd = [
            sys.executable, "-m", "pip", "install",
            "--upgrade"
        ] + missing_packages
        
        # Add Apple Silicon optimizations
        if sys.platform == "darwin":
            install_cmd.extend(["--extra-index-url", "https://download.pytorch.org/whl/cpu"])
        
        try:
            subprocess.run(install_cmd, check=True)
            print("✅ All packages installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            return False
    
    return True

def setup_local_model_directory(model_path: str = "./qwen-devops-local"):
    """Set up local directory for the model."""
    model_dir = Path(model_path)
    model_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (model_dir / "models").mkdir(exist_ok=True)
    (model_dir / "configs").mkdir(exist_ok=True)
    (model_dir / "examples").mkdir(exist_ok=True)
    
    print(f"✅ Created local model directory: {model_dir.absolute()}")
    return model_dir

def create_inference_config(model_dir: Path):
    """Create optimized inference configuration for M4 Pro."""
    config = {
        "model_settings": {
            "torch_dtype": "float16",
            "device_map": "auto",
            "load_in_4bit": True,
            "bnb_4bit_compute_dtype": "float16",
            "bnb_4bit_quant_type": "nf4",
            "bnb_4bit_use_double_quant": True,
            "max_memory": "40GB",  # Leave some memory for system
            "low_cpu_mem_usage": True
        },
        "generation_settings": {
            "max_new_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "pad_token_id": "auto",
            "eos_token_id": "auto"
        },
        "optimization": {
            "use_cache": True,
            "torch_compile": False,  # May not work well on all Mac configurations
            "attention_implementation": "sdpa"  # Scaled dot-product attention
        }
    }
    
    config_path = model_dir / "configs" / "inference_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Created inference config: {config_path}")
    return config

def create_inference_script(model_dir: Path):
    """Create the main inference script."""
    script_content = '''#!/usr/bin/env python3
"""
Qwen DevOps Foundation Model - Local Inference
==============================================

Usage:
    python inference.py "How do I troubleshoot high CPU usage in Kubernetes?"
    python inference.py --interactive  # Start interactive mode
    python inference.py --benchmark    # Run performance benchmark
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Optional

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel

class QwenDevOpsInference:
    def __init__(self, model_path: str, config_path: Optional[str] = None):
        self.model_path = model_path
        self.config_path = config_path or "configs/inference_config.json"
        self.config = self.load_config()
        self.tokenizer = None
        self.model = None
        
    def load_config(self) -> dict:
        """Load inference configuration."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Config file not found: {self.config_path}")
            return self.get_default_config()
    
    def get_default_config(self) -> dict:
        """Get default configuration for M4 Pro."""
        return {
            "model_settings": {
                "torch_dtype": "float16",
                "device_map": "auto",
                "load_in_4bit": True,
                "max_memory": "40GB"
            },
            "generation_settings": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True
            }
        }
    
    def load_model(self):
        """Load the model and tokenizer with optimizations."""
        print(f"🚀 Loading model from: {self.model_path}")
        
        # Configure quantization for memory efficiency
        model_settings = self.config["model_settings"]
        
        if model_settings.get("load_in_4bit", False):
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type=model_settings.get("bnb_4bit_quant_type", "nf4"),
                bnb_4bit_compute_dtype=getattr(torch, model_settings.get("bnb_4bit_compute_dtype", "float16")),
                bnb_4bit_use_double_quant=model_settings.get("bnb_4bit_use_double_quant", True),
            )
        else:
            bnb_config = None
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                quantization_config=bnb_config,
                torch_dtype=getattr(torch, model_settings.get("torch_dtype", "float16")),
                device_map=model_settings.get("device_map", "auto"),
                low_cpu_mem_usage=model_settings.get("low_cpu_mem_usage", True),
                trust_remote_code=True
            )
            
            # Check if this is a PEFT model
            adapter_config_path = Path(self.model_path) / "adapter_config.json"
            if adapter_config_path.exists():
                print("🔧 Loading PEFT adapter...")
                self.model = PeftModel.from_pretrained(self.model, self.model_path)
            
            print("✅ Model loaded successfully!")
            self.print_model_info()
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            sys.exit(1)
    
    def print_model_info(self):
        """Print model information and memory usage."""
        if torch.cuda.is_available():
            print(f"🎯 Device: {torch.cuda.get_device_name()}")
            print(f"💾 GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("🎯 Device: Apple Silicon (MPS)")
            print("💾 Using unified memory architecture")
        else:
            print("🎯 Device: CPU")
        
        # Count parameters
        if hasattr(self.model, 'num_parameters'):
            params = self.model.num_parameters()
        else:
            params = sum(p.numel() for p in self.model.parameters())
        
        print(f"🧠 Model parameters: {params / 1e9:.2f}B")
        print(f"📏 Max sequence length: {self.tokenizer.model_max_length}")
    
    def format_prompt(self, instruction: str, input_text: str = "") -> str:
        """Format prompt in the training format."""
        if input_text:
            return f"### Instruction:\\n{instruction}\\n\\n### Input:\\n{input_text}\\n\\n### Response:\\n"
        else:
            return f"### Instruction:\\n{instruction}\\n\\n### Response:\\n"
    
    def generate_response(self, prompt: str) -> str:
        """Generate response for a given prompt."""
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Format the prompt
        formatted_prompt = self.format_prompt(prompt)
        
        # Tokenize input
        inputs = self.tokenizer(
            formatted_prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048  # Leave room for generation
        )
        
        # Move to appropriate device
        if hasattr(self.model, 'device'):
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Generation settings
        gen_settings = self.config["generation_settings"]
        
        start_time = time.time()
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=gen_settings.get("max_new_tokens", 512),
                temperature=gen_settings.get("temperature", 0.7),
                top_p=gen_settings.get("top_p", 0.9),
                do_sample=gen_settings.get("do_sample", True),
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                use_cache=True
            )
        
        generation_time = time.time() - start_time
        
        # Decode response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract just the response part
        if "### Response:" in response:
            response = response.split("### Response:")[-1].strip()
        
        # Calculate tokens per second
        new_tokens = len(outputs[0]) - len(inputs["input_ids"][0])
        tokens_per_second = new_tokens / generation_time if generation_time > 0 else 0
        
        print(f"⚡ Generated {new_tokens} tokens in {generation_time:.2f}s ({tokens_per_second:.1f} tokens/s)")
        
        return response
    
    def interactive_mode(self):
        """Start interactive chat mode."""
        print("🤖 Qwen DevOps Assistant - Interactive Mode")
        print("=" * 50)
        print("Ask me anything about DevOps, SRE, or infrastructure!")
        print("Type 'quit', 'exit', or 'q' to stop.")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                print("\\n🤖 Assistant: ", end="", flush=True)
                response = self.generate_response(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\\n\\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\\n❌ Error: {e}")
    
    def benchmark(self):
        """Run performance benchmark."""
        print("🏃 Running performance benchmark...")
        
        test_prompts = [
            "How do you troubleshoot high CPU usage in Kubernetes?",
            "Explain blue-green deployment strategy",
            "What are the best practices for monitoring microservices?",
            "How do you implement Infrastructure as Code with Terraform?"
        ]
        
        total_time = 0
        total_tokens = 0
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\\n📝 Test {i}/{len(test_prompts)}: {prompt[:50]}...")
            
            start_time = time.time()
            response = self.generate_response(prompt)
            end_time = time.time()
            
            prompt_time = end_time - start_time
            response_tokens = len(self.tokenizer.encode(response))
            
            total_time += prompt_time
            total_tokens += response_tokens
            
            print(f"   ⏱️  Time: {prompt_time:.2f}s, Tokens: {response_tokens}")
        
        avg_time = total_time / len(test_prompts)
        avg_tokens_per_sec = total_tokens / total_time
        
        print(f"\\n📊 Benchmark Results:")
        print(f"   Average time per prompt: {avg_time:.2f}s")
        print(f"   Average tokens per second: {avg_tokens_per_sec:.1f}")
        print(f"   Total tokens generated: {total_tokens}")

def main():
    parser = argparse.ArgumentParser(description="Qwen DevOps Foundation Model Inference")
    parser.add_argument("prompt", nargs="?", help="Prompt to process")
    parser.add_argument("--model-path", default="./qwen-devops-foundation", help="Path to model directory")
    parser.add_argument("--config", help="Path to inference config file")
    parser.add_argument("--interactive", action="store_true", help="Start interactive mode")
    parser.add_argument("--benchmark", action="store_true", help="Run performance benchmark")
    
    args = parser.parse_args()
    
    # Initialize inference engine
    inference = QwenDevOpsInference(args.model_path, args.config)
    inference.load_model()
    
    if args.benchmark:
        inference.benchmark()
    elif args.interactive:
        inference.interactive_mode()
    elif args.prompt:
        print(f"👤 Question: {args.prompt}")
        print(f"🤖 Response: {inference.generate_response(args.prompt)}")
    else:
        # Default to interactive mode if no prompt provided
        inference.interactive_mode()

if __name__ == "__main__":
    main()
'''
    
    script_path = model_dir / "inference.py"
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_path, 0o755)
    
    print(f"✅ Created inference script: {script_path}")
    return script_path

def create_example_usage(model_dir: Path):
    """Create example usage and test scripts."""
    examples = {
        "basic_usage.py": '''#!/usr/bin/env python3
"""Basic usage example for Qwen DevOps model."""

from inference import QwenDevOpsInference

def main():
    # Initialize the model
    inference = QwenDevOpsInference("./qwen-devops-foundation")
    inference.load_model()
    
    # Example DevOps questions
    questions = [
        "How do I troubleshoot a failed Kubernetes deployment?",
        "What are the best practices for implementing CI/CD pipelines?",
        "How do you monitor microservices effectively?",
        "Explain the difference between blue-green and canary deployments"
    ]
    
    print("🚀 Testing Qwen DevOps Foundation Model\\n")
    
    for i, question in enumerate(questions, 1):
        print(f"Question {i}: {question}")
        response = inference.generate_response(question)
        print(f"Response: {response[:200]}...\\n")

if __name__ == "__main__":
    main()
''',
        "test_performance.py": '''#!/usr/bin/env python3
"""Performance testing for local inference."""

import time
import psutil
import threading
from inference import QwenDevOpsInference

def monitor_resources():
    """Monitor CPU and memory usage during inference."""
    while monitoring:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        print(f"📊 CPU: {cpu_percent:.1f}%, Memory: {memory_info.percent:.1f}%")

def main():
    global monitoring
    monitoring = True
    
    # Start resource monitoring
    monitor_thread = threading.Thread(target=monitor_resources)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Initialize inference
    inference = QwenDevOpsInference("./qwen-devops-foundation")
    inference.load_model()
    
    # Run benchmark
    inference.benchmark()
    
    monitoring = False
    print("✅ Performance test completed")

if __name__ == "__main__":
    main()
'''
    }
    
    for filename, content in examples.items():
        example_path = model_dir / "examples" / filename
        with open(example_path, 'w') as f:
            f.write(content)
        os.chmod(example_path, 0o755)
        print(f"✅ Created example: {example_path}")

def create_download_script(model_dir: Path):
    """Create script to download trained model from S3/DVC."""
    download_script = '''#!/bin/bash

# Download trained model from cloud storage
# This script downloads the model artifacts from S3 via DVC

set -e

echo "📥 Downloading Qwen DevOps Foundation Model"
echo "==========================================="

# Check if DVC is installed
if ! command -v dvc &> /dev/null; then
    echo "❌ DVC is not installed. Installing..."
    pip install dvc[s3]
fi

# Initialize DVC if not already done
if [ ! -d ".dvc" ]; then
    echo "🔧 Initializing DVC..."
    dvc init --no-scm
fi

# Configure S3 remote
echo "🔗 Configuring S3 remote..."
dvc remote add s3 s3://mlops-data-bucket-1754159204/dvc --force
dvc remote modify s3 region us-east-1
dvc remote default s3

# Download model artifacts
echo "📦 Downloading model artifacts..."
if [ -f "qwen-devops-foundation-model.tar.gz.dvc" ]; then
    dvc pull qwen-devops-foundation-model.tar.gz
    
    # Extract model
    echo "📂 Extracting model..."
    tar -xzf qwen-devops-foundation-model.tar.gz
    
    echo "✅ Model downloaded and extracted successfully!"
    echo "🚀 You can now run: python inference.py --interactive"
else
    echo "❌ Model DVC file not found. Make sure training is completed."
    echo "💡 Check the training pipeline status in Argo Workflows"
    exit 1
fi
'''
    
    download_path = model_dir / "download_model.sh"
    with open(download_path, 'w') as f:
        f.write(download_script)
    os.chmod(download_path, 0o755)
    
    print(f"✅ Created download script: {download_path}")

def main():
    parser = argparse.ArgumentParser(description="Setup local inference for Qwen DevOps model")
    parser.add_argument("--model-path", default="./qwen-devops-local", help="Local model directory path")
    parser.add_argument("--check-deps", action="store_true", help="Only check dependencies")
    
    args = parser.parse_args()
    
    print("🚀 Setting up Qwen DevOps Foundation Model for local inference")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Please fix and try again.")
        return 1
    
    if args.check_deps:
        print("✅ All dependencies are satisfied!")
        return 0
    
    # Set up local environment
    model_dir = setup_local_model_directory(args.model_path)
    
    # Create configuration and scripts
    create_inference_config(model_dir)
    create_inference_script(model_dir)
    create_example_usage(model_dir)
    create_download_script(model_dir)
    
    print("\\n🎉 Local inference setup completed!")
    print("=" * 40)
    print("\\n📋 Next steps:")
    print(f"1. cd {model_dir}")
    print("2. ./download_model.sh  # Download trained model")
    print("3. python inference.py --interactive  # Start chatting!")
    print("\\n💡 Or test with a single question:")
    print('   python inference.py "How do I troubleshoot Kubernetes pods?"')
    print("\\n🏃 Run performance benchmark:")
    print("   python inference.py --benchmark")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())