#!/bin/bash

# Start Argo Web UI
# This script starts port forwarding for the Argo web interface

set -e

echo "🚀 Starting Argo Web UI"

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

# Check if Argo server is running
if ! kubectl get pods -n argo -l app=argo-workflows-server --no-headers | grep -q Running; then
    print_error "Argo server is not running. Please check the installation."
    exit 1
fi

print_status "Argo Workflows is ready!"

# Start port forwarding
print_status "Starting port forwarding for Argo UI..."
kubectl port-forward -n argo svc/argo-workflows-server 2746:2746 &
ARGO_PID=$!

# Wait a moment for port forwarding to establish
sleep 3

# Check if port forwarding is working
if curl -s -k https://localhost:2746 > /dev/null 2>&1; then
    print_success "Argo UI is accessible!"
else
    print_warning "Port forwarding may still be establishing..."
fi

print_success "🎉 Argo Web UI is now available!"
print_status "Access the UI at: https://localhost:2746"
print_warning "Note: The UI uses HTTPS with a self-signed certificate."
print_status "You may need to click 'Advanced' and 'Proceed to localhost (unsafe)'"

print_status ""
print_status "📋 Next Steps:"
echo "  1. Open your browser and go to: https://localhost:2746"
echo "  2. Click 'SUBMIT NEW WORKFLOW'"
echo "  3. Upload the file: argo-workflows/ml-pipeline.yaml"
echo "  4. Click 'SUBMIT' to run the ML pipeline"
echo "  5. Monitor the workflow execution in real-time"

print_status ""
print_status "To stop the UI:"
echo "  kill $ARGO_PID"

print_status ""
print_status "For detailed instructions, see: argo-workflows/WEB_UI_GUIDE.md"

# Keep the script running to maintain port forwarding
print_status "Port forwarding is active. Press Ctrl+C to stop."
wait $ARGO_PID 