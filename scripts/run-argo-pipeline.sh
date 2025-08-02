#!/bin/bash

# Quick script to run Argo ML Pipeline
# This script checks if Argo is installed and runs the ML pipeline

set -e

echo "🚀 Running Argo ML Pipeline"

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
    print_warning "Argo namespace not found. Installing Argo Workflows..."
    kubectl create namespace argo
    kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v3.4.8/install.yaml
    
    print_status "Waiting for Argo Workflows to be ready..."
    kubectl wait --for=condition=ready pod -l app=workflow-controller -n argo --timeout=300s
    kubectl wait --for=condition=ready pod -l app=argo-server -n argo --timeout=300s
    print_success "Argo Workflows installed!"
else
    print_status "Argo namespace found"
fi

# Check if Argo CLI is available
if ! command -v argo &> /dev/null; then
    print_warning "Argo CLI not found. Installing..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        curl -sLO https://github.com/argoproj/argo-workflows/releases/download/v3.4.8/argo-darwin-amd64.gz
        gunzip argo-darwin-amd64.gz
        chmod +x argo-darwin-amd64
        sudo mv ./argo-darwin-amd64 /usr/local/bin/argo
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -sLO https://github.com/argoproj/argo-workflows/releases/download/v3.4.8/argo-linux-amd64.gz
        gunzip argo-linux-amd64.gz
        chmod +x argo-linux-amd64
        sudo mv ./argo-linux-amd64 /usr/local/bin/argo
    else
        print_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
    
    print_success "Argo CLI installed!"
fi

# Check if Argo server is running
if ! kubectl get pods -n argo -l app=argo-server --no-headers | grep -q Running; then
    print_error "Argo server is not running. Please check the installation."
    exit 1
fi

print_status "Argo Workflows is ready!"

# Start port forwarding for Argo UI
print_status "Starting port forwarding for Argo UI..."
kubectl port-forward -n argo svc/argo-server 2746:2746 &
ARGO_PID=$!

# Wait for port forwarding
sleep 3

print_success "Argo UI available at: https://localhost:2746"

# Submit the simple ML pipeline
print_status "Submitting ML pipeline workflow..."
argo submit argo-workflows/simple-ml-pipeline.yaml -n argo

WORKFLOW_NAME=$(argo list -n argo --no-headers | head -1 | awk '{print $1}')

print_success "Workflow submitted: $WORKFLOW_NAME"

# Show workflow status
print_status "Workflow status:"
argo list -n argo

print_status "To watch the workflow execution:"
echo "  argo watch $WORKFLOW_NAME -n argo"

print_status "To view workflow logs:"
echo "  argo logs $WORKFLOW_NAME -n argo"

print_status "To access Argo UI:"
echo "  https://localhost:2746"

print_status "To stop port forwarding:"
echo "  kill $ARGO_PID"

print_success "🎉 ML Pipeline is running in Argo Workflows!"
print_status "Check the Argo UI to see the workflow execution in real-time!" 