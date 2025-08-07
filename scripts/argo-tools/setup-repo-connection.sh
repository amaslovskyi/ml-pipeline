#!/bin/bash

# Setup Repository Connection to Argo Workflows
# This script connects the ml-pipeline repository to Argo for GitOps-style deployments

set -e

echo "🔗 Setting up Repository Connection to Argo Workflows"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if we can connect to Kubernetes
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster. Please ensure your cluster is running."
    exit 1
fi

# Check if Argo namespace exists
if ! kubectl get namespace argo &> /dev/null; then
    print_error "Argo namespace not found. Please install Argo Workflows first."
    exit 1
fi

print_status "Setting up repository connection..."

# Step 1: Apply ArgoCD configuration
print_status "Applying ArgoCD configuration..."
kubectl apply -f argo-workflows/argocd-config.yaml

# Step 2: Create repository secret (if needed)
print_status "Setting up repository access..."

# Check if we need to create a repository secret
if [ ! -z "$GITHUB_TOKEN" ]; then
    print_status "Creating GitHub token secret..."
    kubectl create secret generic github-token \
        --from-literal=token="$GITHUB_TOKEN" \
        --namespace=argo \
        --dry-run=client -o yaml | kubectl apply -f -
    
    print_success "GitHub token secret created"
else
    print_warning "No GITHUB_TOKEN found. Using public repository access."
fi

# Step 3: Verify ArgoCD installation
print_status "Checking ArgoCD installation..."
if kubectl get pods -n argo -l app=argocd-server --no-headers | grep -q Running; then
    print_success "ArgoCD server is running"
else
    print_warning "ArgoCD server not found. Installing ArgoCD..."
    
    # Install ArgoCD
    kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
    
    print_status "Waiting for ArgoCD to be ready..."
    kubectl wait --for=condition=ready pod -l app=argocd-server -n argocd --timeout=300s
    print_success "ArgoCD installed successfully!"
fi

# Step 4: Create Application
print_status "Creating ArgoCD Application..."
kubectl apply -f argo-workflows/argocd-config.yaml

# Step 5: Wait for application to sync
print_status "Waiting for application to sync..."
sleep 10

# Step 6: Check application status
print_status "Checking application status..."
kubectl get application ml-pipeline-workflows -n argo

print_success "🎉 Repository connection setup complete!"

print_status ""
print_status "📋 Repository Configuration:"
echo "  Repository: https://github.com/amaslovs/ml-pipeline.git"
echo "  Branch: main"
echo "  Path: argo-workflows"
echo "  Namespace: argo"

print_status ""
print_status "🔄 GitOps Features:"
echo "  ✅ Automatic sync from repository"
echo "  ✅ Self-healing (reverts manual changes)"
echo "  ✅ Prune resources (removes deleted files)"
echo "  ✅ Retry on failure (5 attempts)"

print_status ""
print_status "📊 Monitoring:"
echo "  Check application status:"
echo "    kubectl get application ml-pipeline-workflows -n argo"
echo ""
echo "  View sync status:"
echo "    kubectl describe application ml-pipeline-workflows -n argo"
echo ""
echo "  View ArgoCD UI:"
echo "    kubectl port-forward -n argocd svc/argocd-server 8080:80"

print_status ""
print_status "🚀 Next Steps:"
echo "  1. Push changes to your repository"
echo "  2. ArgoCD will automatically sync the workflows"
echo "  3. Monitor sync status in ArgoCD UI"
echo "  4. Workflows will be deployed automatically"

print_status ""
print_status "📚 Documentation:"
echo "  - ArgoCD UI: http://localhost:8080"
echo "  - Repository: https://github.com/amaslovs/ml-pipeline"
echo "  - Workflows: argo-workflows/"

print_success "✅ Repository connection is now active!" 