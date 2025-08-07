#!/bin/bash

# Setup Argo Workflows and run ML Pipeline
# This script installs Argo Workflows and runs the ML pipeline

set -e

echo "🚀 Setting up Argo Workflows for ML Pipeline"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

print_status "Checking Kubernetes cluster..."
kubectl cluster-info

# Step 1: Create Argo namespace
print_status "Creating Argo namespace..."
kubectl create namespace argo --dry-run=client -o yaml | kubectl apply -f -

# Step 2: Install Argo Workflows
print_status "Installing Argo Workflows..."
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v3.4.8/install.yaml

# Wait for Argo Workflows to be ready
print_status "Waiting for Argo Workflows to be ready..."
kubectl wait --for=condition=ready pod -l app=workflow-controller -n argo --timeout=300s
kubectl wait --for=condition=ready pod -l app=argo-server -n argo --timeout=300s

print_success "Argo Workflows installed successfully!"

# Step 3: Install Argo CLI if not present
if ! command -v argo &> /dev/null; then
    print_status "Installing Argo CLI..."
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -sLO https://github.com/argoproj/argo-workflows/releases/download/v3.4.8/argo-linux-amd64.gz
        gunzip argo-linux-amd64.gz
        chmod +x argo-linux-amd64
        sudo mv ./argo-linux-amd64 /usr/local/bin/argo
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        curl -sLO https://github.com/argoproj/argo-workflows/releases/download/v3.4.8/argo-darwin-amd64.gz
        gunzip argo-darwin-amd64.gz
        chmod +x argo-darwin-amd64
        sudo mv ./argo-darwin-amd64 /usr/local/bin/argo
    else
        print_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
    
    print_success "Argo CLI installed successfully!"
else
    print_status "Argo CLI already installed"
fi

# Step 4: Port forward Argo server
print_status "Setting up port forwarding for Argo UI..."
kubectl port-forward -n argo svc/argo-server 2746:2746 &
ARGO_PID=$!

# Wait a moment for port forwarding to establish
sleep 5

print_success "Argo UI available at: https://localhost:2746"
print_warning "Note: The UI uses HTTPS with a self-signed certificate. You may need to accept the certificate warning."

# Step 5: Submit the ML pipeline workflow
print_status "Submitting ML pipeline workflow..."
argo submit argo-workflows/ml-pipeline.yaml -n argo

print_success "ML pipeline workflow submitted successfully!"

# Step 6: Show workflow status
print_status "Workflow status:"
argo list -n argo

print_status "To watch the workflow execution:"
echo "  argo watch @latest -n argo"

print_status "To view workflow logs:"
echo "  argo logs @latest -n argo"

print_status "To access Argo UI:"
echo "  https://localhost:2746"

print_status "To stop port forwarding:"
echo "  kill $ARGO_PID"

print_success "🎉 Argo Workflows setup complete!"
print_status "Your ML pipeline is now running in Argo Workflows!" 