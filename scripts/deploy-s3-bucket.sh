#!/bin/bash

# Deploy S3 MLOps Data Bucket using CloudFormation
# Usage: ./deploy-s3-bucket.sh [environment] [bucket-name]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_blue() {
    echo -e "${BLUE}[DEPLOY]${NC} $1"
}

# Default values
ENVIRONMENT=${1:-development}
BUCKET_NAME=${2:-mlops-data-bucket}
STACK_NAME="mlops-s3-bucket-${ENVIRONMENT}"
TEMPLATE_FILE="cloudformation/s3-mlops-data-bucket.yaml"
REGION="us-east-1"

echo "🚀 MLOps S3 Bucket CloudFormation Deployment"
echo "=============================================="
echo ""

# Validate prerequisites
log_info "Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    log_error "AWS CLI is not installed. Please install AWS CLI first."
    exit 1
fi

if [ ! -f "$TEMPLATE_FILE" ]; then
    log_error "CloudFormation template not found: $TEMPLATE_FILE"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    log_error "AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

log_info "Prerequisites check passed ✅"

# Display deployment information
echo ""
log_blue "Deployment Configuration:"
echo "  Stack Name: $STACK_NAME"
echo "  Bucket Name: $BUCKET_NAME"
echo "  Environment: $ENVIRONMENT"
echo "  Region: $REGION"
echo "  Template: $TEMPLATE_FILE"
echo ""

# Validate CloudFormation template
log_info "Validating CloudFormation template..."
aws cloudformation validate-template \
    --template-body file://$TEMPLATE_FILE \
    --region $REGION > /dev/null

log_info "Template validation passed ✅"

# Check if stack already exists
STACK_EXISTS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].StackStatus' \
    --output text 2>/dev/null || echo "DOES_NOT_EXIST")

if [ "$STACK_EXISTS" != "DOES_NOT_EXIST" ]; then
    log_warn "Stack $STACK_NAME already exists with status: $STACK_EXISTS"
    echo ""
    read -p "Do you want to update the existing stack? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled by user."
        exit 0
    fi
    ACTION="update"
else
    ACTION="create"
fi

# Deploy the stack
echo ""
log_blue "Deploying CloudFormation stack..."

if [ "$ACTION" == "create" ]; then
    aws cloudformation create-stack \
        --stack-name $STACK_NAME \
        --template-body file://$TEMPLATE_FILE \
        --parameters \
            ParameterKey=BucketName,ParameterValue=$BUCKET_NAME \
            ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
            ParameterKey=EnableVersioning,ParameterValue=true \
            ParameterKey=EnableEncryption,ParameterValue=true \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION \
        --tags \
            Key=Environment,Value=$ENVIRONMENT \
            Key=Purpose,Value=MLOps-DataStorage \
            Key=ManagedBy,Value=CloudFormation \
            Key=DeployedBy,Value="$(whoami)" \
            Key=DeployedAt,Value="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
else
    aws cloudformation update-stack \
        --stack-name $STACK_NAME \
        --template-body file://$TEMPLATE_FILE \
        --parameters \
            ParameterKey=BucketName,ParameterValue=$BUCKET_NAME \
            ParameterKey=Environment,ParameterValue=$ENVIRONMENT \
            ParameterKey=EnableVersioning,ParameterValue=true \
            ParameterKey=EnableEncryption,ParameterValue=true \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $REGION
fi

log_info "Stack deployment initiated ✅"

# Wait for stack deployment to complete
echo ""
log_blue "Waiting for stack deployment to complete..."
aws cloudformation wait stack-${ACTION}-complete \
    --stack-name $STACK_NAME \
    --region $REGION

# Check final status
FINAL_STATUS=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].StackStatus' \
    --output text)

if [[ "$FINAL_STATUS" == *"COMPLETE"* ]]; then
    log_info "Stack deployment completed successfully! ✅"
else
    log_error "Stack deployment failed with status: $FINAL_STATUS"
    exit 1
fi

# Get stack outputs
echo ""
log_blue "Stack Outputs:"
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue,Description]' \
    --output table

# Get the created bucket name and access credentials
CREATED_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`BucketName`].OutputValue' \
    --output text)

ACCESS_KEY_ID=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`CIUserAccessKeyId`].OutputValue' \
    --output text)

# Update DVC configuration with the new bucket
echo ""
log_blue "🔧 Updating DVC configuration..."
DVC_CONFIG_FILE=".dvc/config"

if [ -f "$DVC_CONFIG_FILE" ]; then
    # Backup the original config
    cp "$DVC_CONFIG_FILE" "${DVC_CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    log_info "Backed up original DVC config to ${DVC_CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Update the S3 URL in the DVC config
    sed -i.bak "s|url = s3://[^/]*/dvc|url = s3://$CREATED_BUCKET/dvc|" "$DVC_CONFIG_FILE"
    
    if [ $? -eq 0 ]; then
        log_info "✅ Updated DVC config with new bucket: s3://$CREATED_BUCKET/dvc"
        echo "   Updated: $DVC_CONFIG_FILE"
    else
        log_warn "⚠️  Failed to update DVC config automatically"
        echo "   Please manually update: $DVC_CONFIG_FILE"
    fi
else
    log_warn "⚠️  DVC config file not found: $DVC_CONFIG_FILE"
    echo "   Creating new DVC remote configuration..."
    mkdir -p .dvc
    cat > "$DVC_CONFIG_FILE" << EOF
[core]
    remote = s3
['remote "s3"']
    url = s3://$CREATED_BUCKET/dvc
    region = $REGION
EOF
    log_info "✅ Created new DVC config with bucket: s3://$CREATED_BUCKET/dvc"
fi

# Note: Secret access key would need to be retrieved separately due to NoEcho
echo ""
log_blue "📋 Next Steps:"
echo ""
echo "1. ✅ DVC configuration updated automatically:"
echo "   - Bucket URL: s3://$CREATED_BUCKET/dvc"
echo "   - Region: $REGION"
echo "   - Config file: .dvc/config"
echo ""
echo "2. 🔑 Configure AWS credentials for DVC:"
echo "   # For local development (if using IAM user):"
echo "   aws configure set aws_access_key_id $ACCESS_KEY_ID"
echo "   aws configure set aws_secret_access_key <SECRET_KEY_FROM_OUTPUTS>"
echo "   aws configure set default.region $REGION"
echo ""
echo "   # For EC2 instances, attach the IAM role:"
echo "   # Role ARN available in stack outputs"
echo ""
echo "3. 🧪 Test DVC connection:"
echo "   dvc remote list"
echo "   dvc push  # Push local data to S3"
echo "   dvc pull  # Pull data from S3"
echo ""
echo "4. 📊 Monitor bucket usage:"
echo "   aws s3 ls s3://$CREATED_BUCKET --recursive --human-readable --summarize"
echo ""
echo "5. 💰 Cost optimization:"
echo "   # Review lifecycle policies in the CloudFormation template"
echo "   # Monitor S3 costs in AWS Cost Explorer"
echo ""

# Security recommendations
echo ""
log_blue "🔒 Security Recommendations:"
echo ""
echo "• Store the secret access key securely (e.g., AWS Secrets Manager, CI/CD secrets)"
echo "• Use IAM roles instead of access keys when possible (recommended for EC2/EKS)"
echo "• Regularly rotate access keys"
echo "• Monitor S3 access logs in CloudWatch"
echo "• Review bucket policies and ACLs regularly"
echo ""

# Cleanup reminder
echo ""
log_blue "🧹 Cleanup (when no longer needed):"
echo "aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION"
echo ""

log_info "Deployment completed successfully! 🎉"