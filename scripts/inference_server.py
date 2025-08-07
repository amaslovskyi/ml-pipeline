#!/usr/bin/env python3
"""
FastAPI inference server for Qwen DevOps Foundation LoRA model
Designed for Kubernetes deployment
"""

import os
import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import logging
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model variables
model = None
tokenizer = None

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Input prompt for generation")
    max_length: Optional[int] = Field(512, ge=1, le=2048)
    temperature: Optional[float] = Field(0.7, ge=0.1, le=2.0)
    top_p: Optional[float] = Field(0.9, ge=0.1, le=1.0)
    do_sample: Optional[bool] = Field(True)
    repetition_penalty: Optional[float] = Field(1.05, ge=1.0, le=2.0)

class GenerateResponse(BaseModel):
    generated_text: str
    prompt: str
    model_info: dict

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup, cleanup on shutdown"""
    global model, tokenizer
    
    logger.info("🚀 Loading Qwen DevOps Foundation model...")
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        from peft import PeftModel
        
        # Get configuration from environment
        model_repo = os.getenv("MODEL_REPO", "AMaslovskyi/qwen-devops-foundation-lora")
        base_model_repo = os.getenv("BASE_MODEL", "Qwen/Qwen3-8B")
        hf_token = os.getenv("HF_TOKEN")
        
        logger.info(f"📥 Loading base model: {base_model_repo}")
        
        # Load base model
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model_repo,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
            token=hf_token
        )
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            base_model_repo,
            trust_remote_code=True,
            token=hf_token
        )
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        logger.info(f"📥 Loading LoRA adapter: {model_repo}")
        
        # Load LoRA adapter
        model = PeftModel.from_pretrained(
            base_model,
            model_repo,
            token=hf_token
        )
        
        logger.info("✅ Model loaded successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        raise
    
    yield
    
    # Cleanup
    logger.info("🧹 Cleaning up resources...")
    if model:
        del model
    if tokenizer:
        del tokenizer
    torch.cuda.empty_cache()

# Create FastAPI app
app = FastAPI(
    title="Qwen DevOps Foundation API",
    description="Inference API for Qwen DevOps Foundation LoRA model",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "status": "healthy",
        "model_loaded": True,
        "cuda_available": torch.cuda.is_available(),
        "gpu_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
    }

@app.get("/")
async def root():
    """Root endpoint with model information"""
    return {
        "message": "Qwen DevOps Foundation API",
        "model": "AMaslovskyi/qwen-devops-foundation-lora",
        "base_model": "Qwen/Qwen3-8B",
        "endpoints": ["/generate", "/health", "/docs"]
    }

@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """Generate text using the Qwen DevOps model"""
    
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        logger.info(f"📝 Generating text for prompt: {request.prompt[:50]}...")
        
        # Tokenize input
        inputs = tokenizer(
            request.prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=2048
        )
        
        # Move to GPU if available
        if torch.cuda.is_available():
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=request.max_length,
                temperature=request.temperature,
                top_p=request.top_p,
                do_sample=request.do_sample,
                repetition_penalty=request.repetition_penalty,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                early_stopping=True
            )
        
        # Decode response
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the generated part
        response_text = generated_text[len(request.prompt):].strip()
        
        logger.info(f"✅ Generated {len(response_text)} characters")
        
        return GenerateResponse(
            generated_text=response_text,
            prompt=request.prompt,
            model_info={
                "model": "AMaslovskyi/qwen-devops-foundation-lora",
                "base_model": "Qwen/Qwen3-8B",
                "device": str(model.device),
                "parameters": request.dict()
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.get("/models")
async def get_model_info():
    """Get detailed model information"""
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "model_repo": "AMaslovskyi/qwen-devops-foundation-lora",
        "base_model": "Qwen/Qwen3-8B",
        "model_type": "LoRA Adapter",
        "training_hardware": "4x NVIDIA L40S",
        "training_date": "2025-08-07",
        "specialization": "DevOps, Kubernetes, Docker, SRE",
        "device": str(model.device) if hasattr(model, 'device') else "unknown",
        "torch_dtype": str(next(model.parameters()).dtype) if model else "unknown"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
