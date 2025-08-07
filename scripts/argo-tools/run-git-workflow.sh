#!/bin/bash

# Run ML Pipeline from Git Repository
# This script runs the ML pipeline workflow that pulls from the Git repository

set -e

echo "🚀 Running ML Pipeline from Git Repository"

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

print_status "Submitting Git-connected ML pipeline workflow..."

# Submit the Git workflow
argo submit argo-workflows/git-repo-workflow.yaml -n argo

WORKFLOW_NAME="ml-pipeline-from-git"

print_success "Workflow submitted: $WORKFLOW_NAME"

# Show workflow status
print_status "Workflow status:"
argo list -n argo

print_status ""
print_status "📋 Workflow Details:"
echo "  Name: $WORKFLOW_NAME"
echo "  Repository: https://github.com/amaslovs/ml-pipeline.git"
echo "  Branch: main"
echo "  Path: argo-workflows"

print_status ""
print_status "🔄 Workflow Steps:"
echo "  1. Clone Git repository"
echo "  2. Data preprocessing with DVC"
echo "  3. Feature engineering with DVC"
echo "  4. Model training with MLflow"
echo "  5. Model evaluation"
echo "  6. Model registration"

print_status ""
print_status "📊 Monitoring Commands:"
echo "  Watch workflow: argo watch $WORKFLOW_NAME -n argo"
echo "  View logs: argo logs $WORKFLOW_NAME -n argo"
echo "  Check status: argo get $WORKFLOW_NAME -n argo"

print_status ""
print_status "🌐 Web UI:"
echo "  Start UI: ./scripts/start-argo-ui.sh"
echo "  Access: https://localhost:2746"

print_success "🎉 Git-connected ML pipeline is running!"
print_status "The workflow will clone your repository and run the ML pipeline with DVC and MLflow integration!" 