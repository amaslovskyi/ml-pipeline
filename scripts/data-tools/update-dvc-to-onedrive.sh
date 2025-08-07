#!/bin/bash

# Update DVC configuration from S3 to OneDrive in all pipeline files
# This script replaces S3 DVC configuration with OneDrive configuration

set -e

echo "🔄 Updating DVC configuration from S3 to OneDrive"
echo "================================================="

ONEDRIVE_PATH="/Users/amaslovs/Library/CloudStorage/OneDrive-SoftServe,Inc/MLOps-DVC-Storage"

# Find all YAML files with DVC S3 configuration
echo "📁 Finding pipeline files to update..."
files_to_update=(
    "argo-workflows/qwen-foundational-pipeline.yaml"
    "argo-workflows/ml-pipeline.yaml"
    "argo-workflows/git-repo-workflow.yaml"
)

for file in "${files_to_update[@]}"; do
    if [[ -f "$file" ]]; then
        echo "📝 Updating: $file"
        
        # Create backup
        cp "$file" "$file.backup"
        
        # Replace S3 DVC configuration with OneDrive
        sed -i.tmp "s|dvc remote add s3 s3://.*|dvc remote add -d onedrive $ONEDRIVE_PATH|g" "$file"
        sed -i.tmp "/dvc remote modify s3 region/d" "$file"
        sed -i.tmp "/dvc remote default s3/d" "$file"
        
        # Clean up temporary files
        rm -f "$file.tmp"
        
        echo "✅ Updated: $file (backup: $file.backup)"
    else
        echo "⚠️  File not found: $file"
    fi
done

echo ""
echo "🎉 DVC configuration updated successfully!"
echo "📋 Summary:"
echo "   • Replaced S3 remotes with OneDrive local storage"
echo "   • OneDrive path: $ONEDRIVE_PATH"
echo "   • Backup files created with .backup extension"
echo ""
echo "💡 Next steps:"
echo "   1. Verify the configuration: dvc remote list"
echo "   2. Test DVC operations: dvc push && dvc pull"
echo "   3. Deploy updated pipeline: kubectl apply -f argo-workflows/qwen-foundational-pipeline.yaml"