#!/bin/bash
# Deploy Qwen DevOps Foundation model to Kubernetes

set -e

echo "🚀 Deploying Qwen DevOps Foundation to Kubernetes"
echo "=================================================="

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed or not in PATH"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    echo "💡 Make sure kubectl is configured and cluster is accessible"
    exit 1
fi

echo "✅ Kubernetes cluster accessible"

# Set HF_TOKEN
echo "🔑 Setting up HuggingFace token..."
if [ -z "$HF_TOKEN" ]; then
    echo "⚠️  HF_TOKEN environment variable not set"
    echo "💡 Export your token: export HF_TOKEN=your_token_here"
    echo "🔄 Using placeholder token (update the secret manually)"
    HF_TOKEN="your_hf_token_here"
fi

# Encode HF_TOKEN for secret
HF_TOKEN_B64=$(echo -n "$HF_TOKEN" | base64)

# Create temporary deployment file with real token
TEMP_DEPLOY=$(mktemp)
sed "s/eW91cl9oZl90b2tlbl9oZXJl/$HF_TOKEN_B64/g" k8s-deployment.yaml > "$TEMP_DEPLOY"

echo "📦 Applying Kubernetes manifests..."

# Apply the deployment
kubectl apply -f "$TEMP_DEPLOY"

# Clean up temp file
rm "$TEMP_DEPLOY"

echo "⏳ Waiting for deployment to be ready..."

# Wait for deployment to be ready
kubectl wait --for=condition=available --timeout=600s deployment/qwen-devops-model -n qwen-devops

echo "✅ Deployment completed!"

# Show deployment status
echo ""
echo "📊 Deployment Status:"
kubectl get all -n qwen-devops

echo ""
echo "🔍 Pod logs (last 20 lines):"
kubectl logs -n qwen-devops -l app=qwen-devops-model --tail=20

echo ""
echo "🌐 Service endpoints:"
kubectl get svc -n qwen-devops

echo ""
echo "💡 To test the API:"
echo "kubectl port-forward -n qwen-devops svc/qwen-devops-service 8080:80"
echo "curl -X POST http://localhost:8080/generate \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"prompt\": \"How do I deploy a Kubernetes cluster?\", \"max_length\": 200}'"

echo ""
echo "🎉 Qwen DevOps Foundation model deployed successfully!"
