# OneDrive DVC Configuration - Complete Setup

## ✅ Configuration Summary

Your DVC is now successfully configured to use **SoftServe OneDrive** instead of AWS S3:

### DVC Remote Configuration
```
Remote: onedrive (default)
URL: /Users/amaslovs/Library/CloudStorage/OneDrive-SoftServe,Inc/MLOps-DVC-Storage
Type: Local directory (synced to OneDrive cloud)
```

### What was Changed
- ✅ DVC configuration updated to use OneDrive local storage
- ✅ All pipeline files updated (qwen-foundational-pipeline.yaml, ml-pipeline.yaml, git-repo-workflow.yaml)
- ✅ Backup files created (.backup extension)
- ✅ OneDrive storage directory created and tested

## 🚀 Benefits of OneDrive Setup

### 1. **Cost Savings**
- No AWS S3 storage costs
- No data transfer charges
- Uses existing OneDrive storage

### 2. **Performance**
- Local file access (faster than cloud)
- Works offline when OneDrive is synced
- No network latency for model training

### 3. **Simplicity**
- No AWS credentials needed for DVC
- Automatic cloud backup via OneDrive sync
- Simple file management

### 4. **Security**
- Data stays within SoftServe environment
- OneDrive enterprise security
- No external cloud storage exposure

## 📁 Directory Structure

```
OneDrive-SoftServe,Inc/
└── MLOps-DVC-Storage/
    └── files/
        └── md5/
            └── [DVC hash directories]
```

## 🛠️ Usage Commands

### Basic DVC Operations
```bash
# Add file to DVC
dvc add myfile.txt

# Push to OneDrive storage
dvc push

# Pull from OneDrive storage
dvc pull

# Check status
dvc status

# List remotes
dvc remote list
```

### Verify OneDrive Sync
```bash
# Check if OneDrive is syncing
ls -la "/Users/amaslovs/Library/CloudStorage/OneDrive-SoftServe,Inc/MLOps-DVC-Storage/"

# Find DVC files in OneDrive
find "/Users/amaslovs/Library/CloudStorage/OneDrive-SoftServe,Inc/MLOps-DVC-Storage/" -type f
```

## 🔄 Training Pipeline Changes

All pipeline files have been updated to use OneDrive:

### Before (S3):
```bash
dvc remote add s3 s3://bucket/dvc --force
dvc remote modify s3 region us-east-1
dvc remote default s3
```

### After (OneDrive):
```bash
dvc remote add -d onedrive /Users/amaslovs/Library/CloudStorage/OneDrive-SoftServe,Inc/MLOps-DVC-Storage
```

## 🚀 Next Steps

### 1. Deploy Updated Pipeline
```bash
kubectl apply -f argo-workflows/qwen-foundational-pipeline.yaml
```

### 2. Start Training
```bash
argo submit argo-workflows/qwen-foundational-pipeline.yaml \
  --parameter model-base="Qwen/Qwen2.5-8B" \
  --parameter training-approach="qlora" \
  --parameter epochs="3"
```

### 3. Monitor Training
```bash
argo logs -f @latest
```

## ⚠️ Important Notes

### OneDrive Sync Requirements
- Keep OneDrive app running during training
- Ensure sufficient OneDrive storage space
- Monitor sync status for large model files
- Large files may take time to sync to cloud

### Troubleshooting
```bash
# If DVC operations fail, check OneDrive sync
open "/Users/amaslovs/Library/CloudStorage/OneDrive-SoftServe,Inc/"

# Verify DVC configuration
dvc remote list
cat .dvc/config

# Test DVC operations
echo "test" > test.txt
dvc add test.txt
dvc push
rm test.txt
dvc pull
```

## 📊 Storage Monitoring

### Check OneDrive Usage
```bash
# Directory size
du -sh "/Users/amaslovs/Library/CloudStorage/OneDrive-SoftServe,Inc/MLOps-DVC-Storage/"

# File count
find "/Users/amaslovs/Library/CloudStorage/OneDrive-SoftServe,Inc/MLOps-DVC-Storage/" -type f | wc -l
```

### Estimate Model Storage Needs
- **Qwen3-8B (FP16)**: ~16GB
- **Training artifacts**: ~5-10GB
- **Dataset**: ~1-5GB
- **Total estimated**: ~25-30GB

## 🔐 Security Considerations

- Data stored locally and synced to SoftServe OneDrive
- No external cloud storage exposure
- Enterprise-grade security through OneDrive
- Access controlled by SoftServe policies

## 📞 Support

If you encounter issues:
1. Check OneDrive sync status
2. Verify sufficient storage space
3. Test DVC operations with small files first
4. Review pipeline logs for specific errors

---

**Status**: ✅ OneDrive DVC configuration completed successfully!  
**Ready for**: Qwen foundational model training with local storage backup