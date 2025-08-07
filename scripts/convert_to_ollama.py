#!/usr/bin/env python3
"""
Convert Qwen DevOps Foundation LoRA model to Ollama-compatible format
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

def convert_to_merged_model():
    """Convert LoRA adapter to merged model for Ollama"""
    
    print("🦙 Converting Qwen DevOps LoRA to Ollama Format")
    print("=" * 50)
    
    try:
        print("📥 Loading base model and LoRA adapter...")
        
        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen3-8B",
            torch_dtype=torch.float16,
            device_map="cpu",  # Use CPU for conversion
            trust_remote_code=True
        )
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
        
        # Load LoRA adapter
        model = PeftModel.from_pretrained(
            base_model, 
            "AMaslovskyi/qwen-devops-foundation-lora"
        )
        
        print("🔄 Merging LoRA adapter with base model...")
        
        # Merge and unload LoRA
        merged_model = model.merge_and_unload()
        
        # Save merged model
        output_dir = "./qwen-devops-merged"
        print(f"💾 Saving merged model to: {output_dir}")
        
        merged_model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        print("✅ Merged model saved successfully!")
        print(f"📁 Location: {output_dir}")
        
        # Create Ollama Modelfile
        create_ollama_modelfile(output_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ Conversion failed: {str(e)}")
        return False

def create_ollama_modelfile(model_dir):
    """Create Ollama Modelfile for the converted model"""
    
    modelfile_content = f"""FROM {model_dir}

TEMPLATE \"\"\"{{{{ if .System }}}}<|im_start|>system
{{{{ .System }}}}<|im_end|>
{{{{ end }}}}{{{{ if .Prompt }}}}<|im_start|>user
{{{{ .Prompt }}}}<|im_end|>
<|im_start|>assistant
{{{{ end }}}}{{{{ .Response }}}}<|im_end|>
\"\"\"

PARAMETER stop <|im_start|>
PARAMETER stop <|im_end|>
PARAMETER temperature 0.7
PARAMETER top_p 0.8
PARAMETER repeat_penalty 1.05

SYSTEM \"\"\"You are a DevOps expert assistant specializing in:
- Kubernetes deployments and troubleshooting
- Docker containerization best practices  
- CI/CD pipeline setup and optimization
- Infrastructure as Code (Terraform, Ansible)
- Site Reliability Engineering (SRE) practices
- Cloud platform management (AWS, GCP, Azure)
- Monitoring and observability setup

Provide practical, actionable advice with code examples when applicable.\"\"\"
"""

    with open("Modelfile", "w") as f:
        f.write(modelfile_content)
    
    print("📝 Created Ollama Modelfile")
    print("\n🦙 To use with Ollama:")
    print("1. ollama create qwen-devops -f Modelfile")
    print("2. ollama run qwen-devops")

if __name__ == "__main__":
    success = convert_to_merged_model()
    if success:
        print("\n🎉 Ready for Ollama! Use the Modelfile to create your model.")
    else:
        print("\n❌ Conversion failed. Check the error messages above.")
