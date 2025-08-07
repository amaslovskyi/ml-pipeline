#!/bin/bash

# Direct inference server launcher (bypasses Ollama compatibility issues)

echo "🚀 Starting Qwen DevOps Foundation Server"
echo "=========================================="

# Check if we're in the right directory
if [[ ! -f "direct_inference_server.py" ]]; then
    echo "❌ direct_inference_server.py not found!"
    echo "💡 Make sure you're in the ml-pipeline/scripts directory"
    exit 1
fi

# Check Python dependencies
echo "🔍 Checking Python dependencies..."
python3 -c "
import sys
missing = []
try:
    import torch
    import transformers
    import peft
    import fastapi
    import uvicorn
    import pydantic
except ImportError as e:
    missing.append(str(e).split()[-1])

if missing:
    print(f'❌ Missing dependencies: {missing}')
    print('💡 Install with: pip install torch transformers peft fastapi uvicorn pydantic')
    sys.exit(1)
else:
    print('✅ All dependencies found')
"

if [[ $? -ne 0 ]]; then
    echo "📦 Installing missing dependencies..."
    pip install torch transformers peft fastapi uvicorn pydantic
fi

# Check for model files
echo "🔍 Checking for model files..."
if [[ -d "$HOME/Downloads/qwen-devops-model" ]]; then
    echo "✅ Local model found at ~/Downloads/qwen-devops-model"
    LOCAL_MODEL=true
else
    echo "⚠️  Local model not found, will use HuggingFace Hub"
    LOCAL_MODEL=false
fi

# Check system resources
echo "💾 Checking system resources..."
python3 -c "
import psutil
ram_gb = psutil.virtual_memory().total / (1024**3)
available_gb = psutil.virtual_memory().available / (1024**3)
print(f'💾 Total RAM: {ram_gb:.1f} GB')
print(f'💾 Available RAM: {available_gb:.1f} GB')

if available_gb < 20:
    print('⚠️  WARNING: Less than 20GB RAM available')
    print('💡 Close other applications for better performance')
else:
    print('✅ Sufficient RAM for model loading')
"

# Set environment variables
export PYTORCH_ENABLE_MPS_FALLBACK=1
export TOKENIZERS_PARALLELISM=false

echo ""
echo "🎯 Server Configuration:"
echo "------------------------"
echo "📍 URL: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🔧 Interactive API: http://localhost:8000/redoc"
echo ""

# Test endpoints that will be available
echo "🧪 Example API calls:"
echo "---------------------"
echo "Health check:"
echo "  curl http://localhost:8000/health"
echo ""
echo "Chat request:"
echo "  curl -X POST http://localhost:8000/chat \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"message\": \"How do I deploy to Kubernetes?\"}'"
echo ""

# Start the server
echo "🚀 Starting server..."
echo "Press Ctrl+C to stop"
echo ""

python3 direct_inference_server.py
