#!/usr/bin/env python3
"""
Direct inference server for Qwen DevOps model (bypassing Ollama)
Works with any architecture including Qwen3
"""

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import json
from typing import Optional

# Initialize FastAPI app
app = FastAPI(title="Qwen DevOps Foundation API", version="1.0.0")

# Global model variables
model = None
tokenizer = None

class ChatRequest(BaseModel):
    message: str
    max_length: Optional[int] = 512
    temperature: Optional[float] = 0.7
    system_prompt: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    tokens_generated: int
    generation_time: float

def load_model():
    """Load the model and tokenizer"""
    global model, tokenizer
    
    print("🚀 Loading Qwen DevOps Foundation Model...")
    
    try:
        # Check if we have local model files
        local_model_path = os.path.expanduser("~/Downloads/qwen-devops-model")
        
        if os.path.exists(local_model_path):
            print(f"📁 Found local model at: {local_model_path}")
            
            # Load base model
            print("📥 Loading base model...")
            base_model = AutoModelForCausalLM.from_pretrained(
                "Qwen/Qwen3-8B",
                torch_dtype=torch.float16,
                device_map="cpu",  # Use CPU to avoid MPS issues
                trust_remote_code=True
            )
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load LoRA adapter
            print("📥 Loading LoRA adapter...")
            model = PeftModel.from_pretrained(base_model, local_model_path)
            
            print("✅ Model loaded successfully!")
            
        else:
            print("📥 Loading from HuggingFace Hub...")
            
            # Load base model
            base_model = AutoModelForCausalLM.from_pretrained(
                "Qwen/Qwen3-8B",
                torch_dtype=torch.float16,
                device_map="cpu",  # Use CPU to avoid MPS issues
                trust_remote_code=True
            )
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Load LoRA from Hub
            model = PeftModel.from_pretrained(
                base_model, 
                "AMaslovskyi/qwen-devops-foundation-lora"
            )
            
            print("✅ Model loaded from HuggingFace Hub!")
            
    except Exception as e:
        print(f"❌ Failed to load model: {str(e)}")
        raise e

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    load_model()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "model": "Qwen DevOps Foundation"}

@app.get("/health")
async def health():
    """Detailed health check"""
    global model, tokenizer
    
    return {
        "status": "healthy" if model is not None else "loading",
        "model_loaded": model is not None,
        "tokenizer_loaded": tokenizer is not None,
        "device": str(next(model.parameters()).device) if model else "unknown"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Generate response to user message"""
    global model, tokenizer
    
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        import time
        start_time = time.time()
        
        # Prepare system prompt
        system_prompt = request.system_prompt or """You are a DevOps expert assistant specializing in:
- Kubernetes deployments and troubleshooting
- Docker containerization best practices  
- CI/CD pipeline setup and optimization
- Infrastructure as Code (Terraform, Ansible)
- Site Reliability Engineering (SRE) practices
- Cloud platform management (AWS, GCP, Azure)
- Monitoring and observability setup

Provide practical, actionable advice with code examples when applicable."""
        
        # Format prompt
        formatted_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{request.message}<|im_end|>\n<|im_start|>assistant\n"
        
        # Tokenize
        inputs = tokenizer(formatted_prompt, return_tensors="pt")
        input_length = inputs.input_ids.shape[1]
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=min(request.max_length + input_length, 2048),
                temperature=request.temperature,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.05
            )
        
        # Decode response
        full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        response_text = full_response[len(formatted_prompt):].strip()
        
        # Clean up response
        if response_text.endswith("<|im_end|>"):
            response_text = response_text[:-10].strip()
        
        generation_time = time.time() - start_time
        tokens_generated = outputs[0].shape[0] - input_length
        
        # Clear cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        return ChatResponse(
            response=response_text,
            tokens_generated=tokens_generated,
            generation_time=generation_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/generate")
async def generate(request: ChatRequest):
    """Alternative endpoint for compatibility"""
    return await chat(request)

def main():
    """Run the server"""
    print("🚀 Starting Qwen DevOps Foundation Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
