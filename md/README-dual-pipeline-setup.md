# Dual Pipeline Setup: Local K8s vs HuggingFace Training

> **🚀 Now Using Latest Qwen3**: Both pipelines updated to use [Qwen3-8B](https://huggingface.co/collections/Qwen/qwen3-67dd247413f0e2e4f653967f) - the most recent and capable model in the Qwen family with 4.25M+ downloads.

## 🏗️ Overview

You now have **two distinct training pipelines** for your Qwen3-8B foundational model:

### 1. **Local Kubernetes Pipeline** 
`qwen-foundational-training-pipeline-locally.yaml`
- **Infrastructure**: Your Kubernetes cluster with GPU nodes
- **Storage**: OneDrive local sync
- **Control**: Full infrastructure control

### 2. **HuggingFace Cloud Pipeline**
`qwen-foundational-training-pipeline-huggingface.yaml`  
- **Infrastructure**: HuggingFace Spaces with GPU
- **Storage**: HuggingFace Hub + OneDrive sync
- **Control**: Managed service with web interface

## 🚀 Quick Start Guide

### Option A: Local Kubernetes Training

```bash
# Deploy the local K8s pipeline
kubectl apply -f argo-workflows/qwen-foundational-training-pipeline-locally.yaml

# Start training
argo submit argo-workflows/qwen-foundational-training-pipeline-locally.yaml \
  --parameter model-base="Qwen/Qwen3-8B" \
  --parameter training-approach="qlora" \
  --parameter epochs="3"

# Monitor progress
argo logs -f @latest
```

### Option B: HuggingFace Cloud Training

```bash
# Deploy the HF pipeline
kubectl apply -f argo-workflows/qwen-foundational-training-pipeline-huggingface.yaml

# Start training (creates HF Space)
argo submit argo-workflows/qwen-foundational-training-pipeline-huggingface.yaml \
  --parameter model-base="Qwen/Qwen3-8B" \
  --parameter training-approach="qlora" \
  --parameter hf-organization="your-hf-username"

# Monitor via web interface
# The pipeline will output the HF Space URL
```

## 📊 Comparison Matrix

| Feature              | Local K8s Pipeline    | HuggingFace Pipeline      |
| -------------------- | --------------------- | ------------------------- |
| **Infrastructure**   | Your K8s cluster      | HuggingFace Spaces        |
| **GPU Requirements** | Need GPU nodes        | Managed GPU access        |
| **Setup Complexity** | High (K8s management) | Low (managed service)     |
| **Cost Control**     | Direct GPU costs      | HF compute credits        |
| **Customization**    | Full control          | Limited to HF environment |
| **Monitoring**       | Argo UI + kubectl     | Web interface + W&B       |
| **Model Storage**    | OneDrive only         | HF Hub + OneDrive         |
| **Training Time**    | 4-8 hours             | 4-8 hours                 |
| **Failure Recovery** | Manual intervention   | Automatic retry           |
| **Collaboration**    | K8s access needed     | Web-based sharing         |

## 🏗️ Architecture Diagrams

### Local K8s Architecture
```
Argo Workflows → K8s GPU Pods → HuggingFace Containers → OneDrive Storage
     ↓               ↓                    ↓                     ↓
  Orchestration   Compute Resources   Training Runtime    Data Versioning
```

### HuggingFace Architecture  
```
Argo Orchestrator → HF Space Creation → Gradio Interface → Model Training
         ↓                ↓                    ↓               ↓
    Deployment        Managed GPU         Web Monitoring    HF Hub + OneDrive
```

## 🔧 Pipeline Details

### Local Kubernetes Pipeline Features
- **Container Runtime**: `huggingface/transformers-pytorch-gpu:4.35.0`
- **Resource Requests**: 16-32GB memory, 1 GPU per pod
- **Data Flow**: OneDrive ↔ DVC ↔ Training pods
- **Monitoring**: Argo UI, kubectl logs, W&B
- **Model Output**: Saved to OneDrive via DVC

### HuggingFace Pipeline Features
- **Runtime**: HuggingFace Spaces with Gradio interface
- **GPU Access**: Automatic GPU allocation
- **Data Flow**: Local dataset → HF Hub → Training → OneDrive sync
- **Monitoring**: Web interface with real-time logs
- **Model Output**: HF Hub + OneDrive backup

## 🎯 When to Use Which Pipeline

### Choose **Local K8s Pipeline** when:
- ✅ You have K8s cluster with GPU support
- ✅ Need full control over training environment
- ✅ Want to minimize external dependencies
- ✅ Have enterprise security requirements
- ✅ Plan multiple training experiments
- ✅ Team familiar with K8s operations

### Choose **HuggingFace Pipeline** when:
- ✅ Want zero infrastructure management
- ✅ Need easy sharing and collaboration
- ✅ Prefer web-based monitoring
- ✅ Want automatic model hosting
- ✅ Occasional training needs
- ✅ Want to leverage HF ecosystem

## 🚀 Deployment Instructions

### Prerequisites for Both Pipelines
```bash
# Ensure credentials are set up
./scripts/setup-credentials.sh

# Verify OneDrive DVC configuration
dvc remote list
```

### Local K8s Pipeline Deployment
```bash
# Check K8s cluster has GPU nodes
kubectl get nodes -l accelerator=nvidia-tesla-k80

# Deploy pipeline
kubectl apply -f argo-workflows/qwen-foundational-training-pipeline-locally.yaml

# Submit training job
argo submit argo-workflows/qwen-foundational-training-pipeline-locally.yaml \
  --parameter training-approach="qlora" \
  --parameter epochs="3" \
  --parameter batch-size="4"
```

### HuggingFace Pipeline Deployment
```bash
# Update HF organization parameter
# Edit the pipeline file and set your HF username

# Deploy pipeline
kubectl apply -f argo-workflows/qwen-foundational-training-pipeline-huggingface.yaml

# Submit training job
argo submit argo-workflows/qwen-foundational-training-pipeline-huggingface.yaml \
  --parameter hf-organization="your-hf-username" \
  --parameter hf-space-name="qwen-devops-training"
```

## 📊 Monitoring & Troubleshooting

### Local K8s Monitoring
```bash
# Check workflow status
argo list

# View logs
argo logs -f qwen-foundational-training-pipeline-locally-xxxxx

# Check pod status
kubectl get pods -n argo

# Debug GPU allocation
kubectl describe pod training-pod-name
```

### HuggingFace Monitoring
```bash
# Check workflow status
argo list

# View space creation logs
argo logs -f qwen-foundational-training-pipeline-huggingface-xxxxx

# Access web interface (URL provided in logs)
# Format: https://huggingface.co/spaces/{org}/{space-name}
```

## 💾 Model Retrieval

### From Local K8s Training
```bash
# Models automatically saved to OneDrive
ls -la "/Users/amaslovs/Library/CloudStorage/OneDrive-SoftServe,Inc/MLOps-DVC-Storage/"

# Pull from OneDrive if needed
dvc pull qwen-devops-foundation-model.tar.gz
tar -xzf qwen-devops-foundation-model.tar.gz
```

### From HuggingFace Training
```bash
# Models available in multiple locations:
# 1. HuggingFace Hub: https://huggingface.co/{org}/qwen-devops-foundation
# 2. OneDrive backup (automatically synced)

# Download from HF Hub
python -c "
from huggingface_hub import snapshot_download
snapshot_download(repo_id='your-org/qwen-devops-foundation', local_dir='./model')
"

# Or pull from OneDrive backup
dvc pull qwen-devops-foundation-hf.tar.gz
```

## 🔄 Next Steps

1. **Choose your preferred pipeline** based on your infrastructure and requirements
2. **Update parameters** in the chosen pipeline file
3. **Deploy and test** with a small training run
4. **Scale up** for full model training
5. **Set up local inference** on your M4 Pro using the trained model

## 📞 Support

### Local K8s Issues
- Check GPU node availability
- Verify resource requests/limits
- Review Argo workflow logs
- Ensure DVC OneDrive connectivity

### HuggingFace Issues  
- Verify HF token permissions
- Check HF organization access
- Review Space creation logs
- Ensure sufficient HF compute credits

---

**Status**: ✅ **Dual pipeline setup completed!**  
**Ready for**: Choose your preferred training approach and deploy!