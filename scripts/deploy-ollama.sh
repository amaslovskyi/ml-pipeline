#!/bin/bash
# Deploy Qwen DevOps Foundation model to Ollama

set -e

echo "🦙 Setting up Qwen DevOps Foundation for Ollama"
echo "=============================================="

# Check if ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed"
    echo "💡 Install from: https://ollama.ai"
    echo "💡 Or run: curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo "✅ Ollama found"

# Check if Python dependencies are available
echo "🔍 Checking Python dependencies..."

python3 -c "import torch, transformers, peft" 2>/dev/null || {
    echo "❌ Missing Python dependencies"
    echo "💡 Install with: pip install torch transformers peft"
    exit 1
}

echo "✅ Python dependencies available"

# Convert model to merged format
echo "🔄 Converting LoRA model to merged format..."

if [ ! -d "qwen-devops-merged" ]; then
    echo "📥 Running conversion script..."
    python3 convert_to_ollama.py
    
    if [ $? -ne 0 ]; then
        echo "❌ Model conversion failed"
        exit 1
    fi
else
    echo "✅ Merged model already exists"
fi

# Check if Modelfile exists
if [ ! -f "Modelfile" ]; then
    echo "❌ Modelfile not found"
    echo "💡 Run convert_to_ollama.py first"
    exit 1
fi

echo "📝 Creating Ollama model..."

# Create the model in Ollama
ollama create qwen-devops -f Modelfile

if [ $? -eq 0 ]; then
    echo "✅ Model created successfully!"
else
    echo "❌ Model creation failed"
    exit 1
fi

# Test the model
echo "🧪 Testing the model..."

TEST_PROMPT="How do I deploy a Kubernetes cluster?"
echo "📝 Test prompt: $TEST_PROMPT"

ollama run qwen-devops "$TEST_PROMPT" --verbose

echo ""
echo "🎉 Qwen DevOps Foundation model is ready in Ollama!"
echo ""
echo "💡 Usage:"
echo "  ollama run qwen-devops"
echo "  ollama run qwen-devops \"Your DevOps question here\""
echo ""
echo "🌐 API usage:"
echo "  curl -X POST http://localhost:11434/api/generate \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{"
echo "      \"model\": \"qwen-devops\","
echo "      \"prompt\": \"How to set up monitoring with Prometheus?\","
echo "      \"stream\": false"
echo "    }'"
echo ""
echo "📚 Available commands:"
echo "  ollama list                    # List all models"
echo "  ollama show qwen-devops        # Show model info"
echo "  ollama rm qwen-devops          # Remove model"
