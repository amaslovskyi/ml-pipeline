#!/bin/bash

# Setup script for Qwen foundational model training credentials
# This script helps you set up all required credentials for the training pipeline

set -e

echo "🚀 Setting up credentials for Qwen foundational model training"
echo "============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl is not installed or not in PATH${NC}"
        echo "Please install kubectl first: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi
    
    # Check if we can connect to cluster
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}❌ Cannot connect to Kubernetes cluster${NC}"
        echo "Please ensure your kubeconfig is properly configured"
        exit 1
    fi
    
    echo -e "${GREEN}✅ kubectl is working and connected to cluster${NC}"
}

# Function to check if argo namespace exists
check_argo_namespace() {
    if ! kubectl get namespace argo &> /dev/null; then
        echo -e "${YELLOW}⚠️  Argo namespace doesn't exist, creating it...${NC}"
        kubectl create namespace argo
        echo -e "${GREEN}✅ Created argo namespace${NC}"
    else
        echo -e "${GREEN}✅ Argo namespace exists${NC}"
    fi
}

# Function to set up HuggingFace credentials
setup_huggingface() {
    echo ""
    echo "🤗 Setting up HuggingFace credentials"
    echo "-----------------------------------"
    
    # Check if secret already exists
    if kubectl get secret huggingface-credentials -n argo &> /dev/null; then
        echo -e "${YELLOW}⚠️  HuggingFace credentials already exist${NC}"
        read -p "Do you want to update them? (y/N): " update_hf
        if [[ ! $update_hf =~ ^[Yy]$ ]]; then
            echo "Skipping HuggingFace credentials setup"
            return
        fi
        kubectl delete secret huggingface-credentials -n argo
    fi
    
    echo "You need a HuggingFace token with read access to Qwen models."
    echo "Get your token from: https://huggingface.co/settings/tokens"
    echo ""
    
    read -s -p "Enter your HuggingFace token: " HF_TOKEN
    echo ""
    
    if [[ -z "$HF_TOKEN" ]]; then
        echo -e "${RED}❌ HuggingFace token cannot be empty${NC}"
        return 1
    fi
    
    # Validate token format (basic check)
    if [[ ! $HF_TOKEN =~ ^hf_[a-zA-Z0-9]{34}$ ]]; then
        echo -e "${YELLOW}⚠️  Token format looks unusual. Make sure it's correct.${NC}"
    fi
    
    kubectl create secret generic huggingface-credentials \
        --from-literal=HF_TOKEN="$HF_TOKEN" \
        -n argo
    
    echo -e "${GREEN}✅ HuggingFace credentials created successfully${NC}"
}

# Function to set up Weights & Biases credentials
setup_wandb() {
    echo ""
    echo "📊 Setting up Weights & Biases credentials"
    echo "----------------------------------------"
    
    # Check if secret already exists
    if kubectl get secret wandb-credentials -n argo &> /dev/null; then
        echo -e "${YELLOW}⚠️  W&B credentials already exist${NC}"
        read -p "Do you want to update them? (y/N): " update_wandb
        if [[ ! $update_wandb =~ ^[Yy]$ ]]; then
            echo "Skipping W&B credentials setup"
            return
        fi
        kubectl delete secret wandb-credentials -n argo
    fi
    
    echo "Weights & Biases is used for experiment tracking (optional but recommended)."
    echo "Get your API key from: https://wandb.ai/settings"
    echo ""
    
    read -p "Do you want to set up W&B tracking? (y/N): " setup_wandb_prompt
    if [[ ! $setup_wandb_prompt =~ ^[Yy]$ ]]; then
        # Create empty secret so pipeline doesn't fail
        kubectl create secret generic wandb-credentials \
            --from-literal=WANDB_API_KEY="" \
            -n argo
        echo -e "${YELLOW}⚠️  Created empty W&B credentials (tracking disabled)${NC}"
        return
    fi
    
    read -s -p "Enter your W&B API key: " WANDB_KEY
    echo ""
    
    if [[ -z "$WANDB_KEY" ]]; then
        echo -e "${RED}❌ W&B API key cannot be empty${NC}"
        return 1
    fi
    
    kubectl create secret generic wandb-credentials \
        --from-literal=WANDB_API_KEY="$WANDB_KEY" \
        -n argo
    
    echo -e "${GREEN}✅ W&B credentials created successfully${NC}"
}

# Function to check AWS credentials
check_aws_credentials() {
    echo ""
    echo "☁️  Checking AWS credentials"
    echo "----------------------------"
    
    if kubectl get secret aws-credentials -n argo &> /dev/null; then
        echo -e "${GREEN}✅ AWS credentials already exist${NC}"
        
        # Test if credentials work
        echo "Testing AWS credentials..."
        if kubectl run test-aws --rm -i --restart=Never --image=amazon/aws-cli:latest \
           --env="AWS_ACCESS_KEY_ID=$(kubectl get secret aws-credentials -n argo -o jsonpath='{.data.AWS_ACCESS_KEY_ID}' | base64 -d)" \
           --env="AWS_SECRET_ACCESS_KEY=$(kubectl get secret aws-credentials -n argo -o jsonpath='{.data.AWS_SECRET_ACCESS_KEY}' | base64 -d)" \
           --env="AWS_DEFAULT_REGION=$(kubectl get secret aws-credentials -n argo -o jsonpath='{.data.AWS_DEFAULT_REGION}' | base64 -d)" \
           -- aws sts get-caller-identity &> /dev/null; then
            echo -e "${GREEN}✅ AWS credentials are valid${NC}"
        else
            echo -e "${YELLOW}⚠️  Could not validate AWS credentials${NC}"
        fi
    else
        echo -e "${RED}❌ AWS credentials not found${NC}"
        echo "Please set up AWS credentials first using:"
        echo "kubectl create secret generic aws-credentials \\"
        echo "  --from-literal=AWS_ACCESS_KEY_ID=\"your_key\" \\"
        echo "  --from-literal=AWS_SECRET_ACCESS_KEY=\"your_secret\" \\"
        echo "  --from-literal=AWS_DEFAULT_REGION=\"us-east-1\" \\"
        echo "  -n argo"
        return 1
    fi
}

# Function to verify all credentials
verify_credentials() {
    echo ""
    echo "🔍 Verifying all credentials"
    echo "----------------------------"
    
    local all_good=true
    
    # Check HuggingFace
    if kubectl get secret huggingface-credentials -n argo &> /dev/null; then
        echo -e "${GREEN}✅ HuggingFace credentials exist${NC}"
    else
        echo -e "${RED}❌ HuggingFace credentials missing${NC}"
        all_good=false
    fi
    
    # Check W&B
    if kubectl get secret wandb-credentials -n argo &> /dev/null; then
        echo -e "${GREEN}✅ W&B credentials exist${NC}"
    else
        echo -e "${RED}❌ W&B credentials missing${NC}"
        all_good=false
    fi
    
    # Check AWS
    if kubectl get secret aws-credentials -n argo &> /dev/null; then
        echo -e "${GREEN}✅ AWS credentials exist${NC}"
    else
        echo -e "${RED}❌ AWS credentials missing${NC}"
        all_good=false
    fi
    
    if $all_good; then
        echo ""
        echo -e "${GREEN}🎉 All credentials are set up correctly!${NC}"
        echo -e "${GREEN}You can now deploy the training pipeline.${NC}"
        return 0
    else
        echo ""
        echo -e "${RED}❌ Some credentials are missing. Please fix them before proceeding.${NC}"
        return 1
    fi
}

# Function to show next steps
show_next_steps() {
    echo ""
    echo "🚀 Next Steps"
    echo "============"
    echo ""
    echo "1. Deploy the training pipeline:"
    echo "   kubectl apply -f ml-pipeline/argo-workflows/qwen-foundational-pipeline.yaml"
    echo ""
    echo "2. Start a training run:"
    echo "   argo submit ml-pipeline/argo-workflows/qwen-foundational-pipeline.yaml \\"
    echo "     --parameter model-base=\"Qwen/Qwen2.5-8B\" \\"
    echo "     --parameter training-approach=\"qlora\" \\"
    echo "     --parameter epochs=\"3\""
    echo ""
    echo "3. Monitor the training:"
    echo "   argo logs -f @latest"
    echo ""
    echo "4. Access Argo UI (if available):"
    echo "   kubectl port-forward svc/argo-server 2746:2746 -n argo"
    echo "   # Then open: https://localhost:2746"
    echo ""
}

# Main execution
main() {
    echo "Starting credential setup for Qwen foundational model training..."
    echo ""
    
    # Check prerequisites
    check_kubectl
    check_argo_namespace
    
    # Set up credentials
    setup_huggingface
    setup_wandb
    check_aws_credentials
    
    # Verify everything
    if verify_credentials; then
        show_next_steps
    else
        echo ""
        echo -e "${RED}Please fix the missing credentials and run this script again.${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}✅ Credential setup completed successfully!${NC}"
}

# Run main function
main "$@"