#!/bin/bash

# Update DVC S3 bucket configuration in Argo workflow
# This script helps update the S3 bucket name when CloudFormation creates a new bucket

set -e

echo "🔧 Updating DVC S3 bucket configuration in Argo workflow"

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

# Check if S3 bucket name is provided
if [ -z "$1" ]; then
    print_error "Usage: $0 <s3-bucket-name>"
    print_error "Example: $0 mlops-data-bucket-1234567890-username"
    exit 1
fi

S3_BUCKET_NAME="$1"
WORKFLOW_FILE="argo-workflows/ml-pipeline.yaml"

# Check if workflow file exists
if [ ! -f "$WORKFLOW_FILE" ]; then
    print_error "Workflow file not found: $WORKFLOW_FILE"
    exit 1
fi

print_status "Updating S3 bucket name to: $S3_BUCKET_NAME"

# Update the S3 bucket name in the workflow file
sed -i.bak "s/value: \"mlops-data-bucket-[0-9]*-[a-zA-Z0-9]*\"/value: \"$S3_BUCKET_NAME\"/g" "$WORKFLOW_FILE"

# Check if the update was successful
if grep -q "value: \"$S3_BUCKET_NAME\"" "$WORKFLOW_FILE"; then
    print_success "S3 bucket name updated successfully!"
    print_status "Updated workflow file: $WORKFLOW_FILE"
    
    # Show the updated configuration
    print_status "Current DVC configuration:"
    grep -A 2 -B 2 "dvc-s3-bucket" "$WORKFLOW_FILE"
    
    print_status "To apply the changes:"
    echo "  argo submit $WORKFLOW_FILE -n argo"
    
else
    print_error "Failed to update S3 bucket name"
    exit 1
fi

print_success "✅ DVC configuration updated successfully!" 