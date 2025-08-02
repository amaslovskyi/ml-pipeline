# ML Pipeline with Argo Workflows and DVC

This project demonstrates a complete MLOps pipeline using **Argo Workflows** for orchestration and **DVC** for data versioning.

## 🎯 Overview

This project implements **Step 4** of the MLOps interview preparation guide, focusing on:
- **Argo Workflows** for ML pipeline orchestration
- **DVC** for data versioning and artifact management
- **Kubernetes-native** ML workflows
- **Production-ready** pipeline patterns

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ML Pipeline Architecture              │
├─────────────────────────────────────────────────────────┤
│  Argo Workflows (Orchestration)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │   Data      │ │   Feature   │ │   Model     │      │
│  │   Prep      │ │   Engineering│ │   Training  │      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
├─────────────────────────────────────────────────────────┤
│  DVC (Data Versioning)                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │   Raw       │ │   Processed │ │   Models    │      │
│  │   Data      │ │   Data      │ │   Artifacts │      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
├─────────────────────────────────────────────────────────┤
│  S3 Storage (Remote Artifacts)                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │   DVC       │ │   MLflow    │ │   Model     │      │
│  │   Cache     │ │   Artifacts │ │   Registry  │      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Kubernetes cluster** (Docker Desktop, Minikube, or cloud)
- **kubectl** configured
- **DVC** installed (`pip install dvc[s3]`)

### Option 1: Quick Run (Recommended)

```bash
# Navigate to the project
cd /Users/amaslovs/Edu/LLM/ml-pipeline

# Run the Argo ML pipeline
./scripts/run-argo-pipeline.sh
```

This script will:
- ✅ Install Argo Workflows if not present
- ✅ Install Argo CLI if needed
- ✅ Start port forwarding for Argo UI
- ✅ Submit the ML pipeline workflow
- ✅ Show workflow status and logs

### Option 2: Manual Setup

```bash
# 1. Install Argo Workflows
kubectl create namespace argo
kubectl apply -n argo -f https://github.com/argoproj/argo-workflows/releases/download/v3.4.8/install.yaml

# 2. Install Argo CLI
curl -sLO https://github.com/argoproj/argo-workflows/releases/download/v3.4.8/argo-darwin-amd64.gz
gunzip argo-darwin-amd64.gz
chmod +x argo-darwin-amd64
sudo mv ./argo-darwin-amd64 /usr/local/bin/argo

# 3. Submit workflow
argo submit argo-workflows/simple-ml-pipeline.yaml -n argo

# 4. Access Argo UI
kubectl port-forward -n argo svc/argo-server 2746:2746
```

## 📁 Project Structure

```
ml-pipeline/
├── argo-workflows/           # Argo workflow definitions
│   ├── ml-pipeline.yaml     # Full ML pipeline workflow
│   └── simple-ml-pipeline.yaml # Simple test workflow
├── scripts/                  # Automation scripts
│   ├── setup-argo.sh        # Complete Argo setup
│   ├── run-argo-pipeline.sh # Quick run script
│   └── deploy-s3-bucket.sh  # S3 bucket deployment
├── cloudformation/           # AWS infrastructure
│   ├── s3-mlops-data-bucket.yaml # S3 bucket template
│   └── README.md            # CloudFormation docs
├── data/                     # Data directory (DVC tracked)
│   ├── raw/                 # Raw data files
│   ├── processed/           # Processed data
│   └── interim/             # Intermediate data
├── src/                      # Source code
├── tests/                    # Test files
├── models/                   # Model artifacts
├── .dvc/                     # DVC configuration
├── .github/                  # GitHub Actions
└── terraform/                # Terraform configurations
```

## 🔧 Workflow Details

### Simple ML Pipeline

The `simple-ml-pipeline.yaml` contains:

1. **Data Preparation**: Creates sample text classification data
2. **Model Training**: Trains a LogisticRegression model with TF-IDF features
3. **Model Evaluation**: Calculates accuracy, precision, recall, and F1-score

### Full ML Pipeline

The `ml-pipeline.yaml` contains:

1. **Data Preprocessing**: Data cleaning and preparation
2. **Feature Engineering**: Feature extraction and transformation
3. **Model Training**: ML model training with hyperparameters
4. **Model Evaluation**: Comprehensive model evaluation
5. **Model Registration**: Model artifact registration

## 📊 Monitoring & Access

### Argo UI Access

```bash
# Port forward Argo UI
kubectl port-forward -n argo svc/argo-server 2746:2746

# Access UI
open https://localhost:2746
```

### Workflow Commands

```bash
# List workflows
argo list -n argo

# Watch workflow execution
argo watch @latest -n argo

# View workflow logs
argo logs @latest -n argo

# Get workflow details
argo get @latest -n argo
```

## 🔄 DVC Integration

### DVC Setup

```bash
# Initialize DVC (already done)
dvc init

# Add data directories
dvc add data/raw/
dvc add data/processed/
dvc add models/

# Push to S3
dvc push

# Pull from S3
dvc pull
```

### DVC Configuration

The project is configured to use S3 for DVC storage:

```ini
[core]
    remote = s3
['remote "s3"']
    url = s3://mlops-data-bucket-1754148674-amaslovs/dvc
    region = us-east-1
```

## 🛠️ Customization

### Modify Workflow Parameters

Edit the workflow YAML files to customize:

```yaml
arguments:
  parameters:
  - name: model-name
    value: "your-model-name"
  - name: epochs
    value: "5"
  - name: batch-size
    value: "32"
```

### Add New Steps

Add new templates to the workflow:

```yaml
- name: your-step
  container:
    image: python:3.9-slim
    command: [python]
    args: ["your-script.py"]
```

## 🔍 Troubleshooting

### Common Issues

1. **Argo not installed**
   ```bash
   ./scripts/setup-argo.sh
   ```

2. **Workflow fails**
   ```bash
   argo logs @latest -n argo
   kubectl get pods -n argo
   ```

3. **Port forwarding issues**
   ```bash
   # Kill existing port forward
   pkill -f "port-forward.*argo-server"
   
   # Start new port forward
   kubectl port-forward -n argo svc/argo-server 2746:2746
   ```

4. **DVC issues**
   ```bash
   # Check DVC status
   dvc status
   
   # Reconfigure DVC
   dvc remote modify s3 region us-east-1
   ```

### Debug Commands

```bash
# Check Argo pods
kubectl get pods -n argo

# Check workflow status
argo list -n argo

# View workflow details
argo get @latest -n argo -o yaml

# Check DVC status
dvc status
```

## 📈 Performance

### Resource Requirements

- **Memory**: 2-4GB for workflow execution
- **CPU**: 2-4 cores for parallel tasks
- **Storage**: 10-20GB for data and models

### Optimization Tips

1. **Use smaller images** for faster startup
2. **Implement caching** for repeated steps
3. **Use resource limits** to prevent OOM
4. **Parallel execution** for independent tasks

## 🔗 Related Resources

- [Argo Workflows Documentation](https://argoproj.github.io/argo-workflows/)
- [DVC Documentation](https://dvc.org/doc)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [MLOps Best Practices](https://mlops.community/)

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

**🎯 Ready for MLOps Interviews**: This setup demonstrates production-ready ML pipeline orchestration with Argo Workflows and proper data versioning with DVC. 