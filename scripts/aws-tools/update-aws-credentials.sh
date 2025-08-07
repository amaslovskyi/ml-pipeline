#!/bin/bash
# Update AWS credentials for Argo Workflows
# This script creates/updates the AWS credentials secret in the argo namespace

set -e

echo "🔐 Updating AWS Credentials for Argo Workflows"

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

# Check if AWS credentials are available
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    print_error "AWS credentials not found in environment variables"
    print_error "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
    print_error ""
    print_error "Example:"
    print_error "  export AWS_ACCESS_KEY_ID='your-access-key'"
    print_error "  export AWS_SECRET_ACCESS_KEY='your-secret-key'"
    print_error "  export AWS_DEFAULT_REGION='us-east-1'"
    exit 1
fi

# Check if argo namespace exists
if ! kubectl get namespace argo &> /dev/null; then
    print_error "Argo namespace not found. Please install Argo Workflows first."
    exit 1
fi

print_status "Current AWS credentials:"
print_status "  AWS_ACCESS_KEY_ID: ${AWS_ACCESS_KEY_ID:0:8}..."
print_status "  AWS_DEFAULT_REGION: ${AWS_DEFAULT_REGION:-us-east-1}"

# Delete existing secret if it exists
print_status "Removing existing AWS credentials secret..."
kubectl delete secret aws-credentials -n argo --ignore-not-found=true

# Create new secret with current AWS credentials
print_status "Creating new AWS credentials secret..."
kubectl create secret generic aws-credentials -n argo \
    --from-literal=AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    --from-literal=AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    --from-literal=AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}"

if [ $? -eq 0 ]; then
    print_success "✅ AWS credentials secret updated successfully!"
    print_status "The secret is available for all workflows in the argo namespace"
    print_status ""
    print_status "To verify the secret:"
    print_status "  kubectl get secret aws-credentials -n argo"
else
    print_error "❌ Failed to update AWS credentials secret"
    exit 1
fi

print_success "🎉 AWS credentials are ready for Argo Workflows!"