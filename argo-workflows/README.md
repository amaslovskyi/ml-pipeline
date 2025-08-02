# Argo Workflows ML Pipeline

This directory contains Argo Workflows configurations for orchestrating machine learning pipelines in Kubernetes.

## 📁 Directory Structure

```
argo-workflows/
├── README.md                    # This file
├── ml-pipeline.yaml             # Complete ML pipeline workflow
├── git-repo-workflow.yaml       # Git-connected ML pipeline workflow
├── argocd-config.yaml           # ArgoCD configuration for GitOps
└── rbac-config.yaml             # RBAC permissions for Argo workflows
```

## 🚀 Quick Start

### Prerequisites
- Kubernetes cluster (Docker Desktop, Minikube, or cloud)
- `kubectl` configured and connected
- Argo Workflows installed in the `argo` namespace

### 1. Apply RBAC Configuration
```bash
kubectl apply -f rbac-config.yaml
```

### 2. Submit the ML Pipeline

**Option A: Direct workflow submission**
```bash
argo submit ml-pipeline.yaml -n argo
```

**Option B: Git-connected workflow (recommended)**
```bash
./scripts/run-git-workflow.sh
```

### 3. Monitor the Pipeline
```bash
# Watch workflow execution
argo watch ml-training-pipeline -n argo

# View logs
argo logs ml-training-pipeline -n argo

# List workflows
argo list -n argo
```

## 🔧 ML Pipeline Overview

### **Local Workflow** (`ml-pipeline.yaml`)
The `ml-pipeline.yaml` defines a comprehensive 5-step ML pipeline:

### **Git-Connected Workflow** (`git-repo-workflow.yaml`)
The `git-repo-workflow.yaml` provides GitOps-style deployment that:
- **Clones your repository** from GitHub
- **Runs the ML pipeline** with the latest code
- **Integrates with DVC** for data versioning
- **Connects to MLflow** for experiment tracking
- **Supports parameter customization** via workflow parameters

### 📊 Pipeline Steps

1. **Data Preprocessing** (`data-prep`)
   - Creates sample text classification dataset with 100 balanced records
   - **DVC integration** for data versioning and S3 storage
   - Generates versioned data files with sentiment analysis labels
   - Installs required Python packages (pandas, numpy, scikit-learn, dvc, boto3)

2. **Feature Engineering** (`feature-eng`)
   - **DVC data loading** from versioned raw data
   - Performs TF-IDF vectorization with 100 features
   - Saves processed features, labels, and vectorizer to DVC
   - Prepares features for model training with versioning

3. **Model Training** (`train-model`)
   - Trains LogisticRegression classifier
   - **Uses DVC-processed data** with 100 samples and 100 TF-IDF features
   - **Real MLflow integration** with our cluster's MLflow server
   - Logs parameters, metrics, and model artifacts
   - Saves trained model and vectorizer for versioning
   - Reports comprehensive training metrics

4. **Model Evaluation** (`evaluate-model`)
   - Calculates comprehensive metrics:
     - Accuracy, Precision, Recall, F1-Score
   - Simulates model performance assessment

5. **Model Registration** (`register-model`)
   - **Real MLflow model registration** with our cluster's MLflow server
   - **Loads trained model from DVC-processed artifacts**
   - Registers model in MLflow Model Registry
   - Logs model artifacts and vectorizer
   - Prepares model for deployment with versioning

### ⚙️ Configuration Parameters

The pipeline accepts the following parameters:

| Parameter       | Default                                 | Description                |
| --------------- | --------------------------------------- | -------------------------- |
| `model-name`    | `bert-classifier`                       | Name of the model to train |
| `data-version`  | `v1.0`                                  | Version of the dataset     |
| `epochs`        | `3`                                     | Number of training epochs  |
| `batch-size`    | `16`                                    | Training batch size        |
| `dvc-s3-bucket` | `mlops-data-bucket-1754148674-amaslovs` | S3 bucket for DVC storage  |
| `dvc-s3-region` | `us-east-1`                             | AWS region for S3 bucket   |

### 📈 Resource Requirements

Each step has defined resource limits:

| Step           | CPU Request | CPU Limit | Memory Request | Memory Limit |
| -------------- | ----------- | --------- | -------------- | ------------ |
| Data Prep      | 250m        | 500m      | 512Mi          | 1Gi          |
| Feature Eng    | 500m        | 1000m     | 1Gi            | 2Gi          |
| Model Training | 1000m       | 2000m     | 2Gi            | 4Gi          |
| Model Eval     | 500m        | 1000m     | 1Gi            | 2Gi          |
| Model Reg      | 250m        | 500m      | 512Mi          | 1Gi          |

## 📊 Data Version Control (DVC) Integration

### DVC Configuration
The pipeline uses DVC for data versioning with S3 storage:

- **S3 Remote**: Configurable via parameters (`dvc-s3-bucket` and `dvc-s3-region`)
- **Default S3 Bucket**: `mlops-data-bucket-1754148674-amaslovs`
- **Default Region**: `us-east-1`
- **Data Versioning**: All data artifacts are versioned and stored in S3

### Updating S3 Bucket Configuration
When CloudFormation creates a new S3 bucket, update the configuration:

```bash
# Update S3 bucket name in workflow
./scripts/update-dvc-config.sh mlops-data-bucket-NEW-ID-username

# Submit workflow with custom parameters
argo submit ml-pipeline.yaml \
  --parameter dvc-s3-bucket=mlops-data-bucket-NEW-ID-username \
  --parameter dvc-s3-region=us-east-1 \
  -n argo
```

### Data Flow with DVC
1. **Raw Data**: Generated and versioned in `data/raw/`
2. **Processed Data**: Features, labels, and vectorizers in `data/processed/`
3. **Model Artifacts**: Trained models and vectorizers in `models/`
4. **S3 Storage**: All artifacts pushed to S3 for persistence

### DVC Commands Used
```bash
# Add data to DVC
dvc add data/raw/sample_data_v1.0.csv
dvc add data/processed/features_v1.0.pkl

# Push to S3
dvc push

# Pull from S3
dvc pull data/raw/sample_data_v1.0.csv.dvc
```

## 🔐 Security & Permissions

### RBAC Configuration

The `rbac-config.yaml` file creates:

1. **Service Account**: `argo-workflow-sa`
   - Dedicated service account for workflow execution

2. **Role**: `argo-workflow-role`
   - Pod management permissions
   - ConfigMap and Secret access
   - PersistentVolumeClaim management
   - Argo Workflows resource permissions

3. **RoleBinding**: `argo-workflow-rolebinding`
   - Binds the role to the service account

### Security Features
- **Least Privilege**: Minimal required permissions
- **Namespace Isolation**: All resources in `argo` namespace
- **Service Account**: Dedicated identity for workflows
- **Resource Limits**: Prevents resource exhaustion

## 🛠️ Customization

### Modifying the Pipeline

1. **Add New Steps**:
   ```yaml
   - name: new-step
     template: new-template
     dependencies: [previous-step]
   ```

2. **Change Parameters**:
   ```bash
   argo submit ml-pipeline.yaml \
     --parameter model-name=custom-model \
     --parameter epochs=10 \
     -n argo
   ```

3. **Modify Resources**:
   ```yaml
   resources:
     requests:
       memory: "1Gi"
       cpu: "500m"
     limits:
       memory: "2Gi"
       cpu: "1000m"
   ```

### Adding New Templates

Create new container templates for custom processing:

```yaml
- name: custom-template
  inputs:
    parameters:
    - name: param-name
  container:
    image: python:3.9-slim
    command: [bash]
    args:
    - -c
    - |
      echo "Custom processing"
      # Your custom logic here
```

## 📊 Monitoring & Debugging

### Workflow Status Commands

```bash
# List all workflows
argo list -n argo

# Get workflow details
argo get ml-training-pipeline -n argo

# Watch workflow execution
argo watch ml-training-pipeline -n argo

# View workflow logs
argo logs ml-training-pipeline -n argo

# View specific step logs
argo logs ml-training-pipeline -n argo --step-name model-training
```

### Common Issues & Solutions

1. **Permission Denied**:
   ```bash
   # Reapply RBAC configuration
   kubectl apply -f rbac-config.yaml
   ```

2. **Workflow Stuck**:
   ```bash
   # Check pod status
   kubectl get pods -n argo
   
   # Check workflow controller logs
   kubectl logs -n argo -l app=workflow-controller
   ```

3. **Resource Issues**:
   ```bash
   # Check cluster resources
   kubectl top nodes
   kubectl top pods -n argo
   ```

## 🔄 Workflow Lifecycle

### Execution Flow

1. **Submission**: `argo submit ml-pipeline.yaml -n argo`
2. **Scheduling**: Argo controller schedules pods
3. **Execution**: Each step runs in sequence
4. **Completion**: Workflow reaches final state
5. **Cleanup**: Pods are terminated automatically

### Workflow States

- `Pending`: Waiting for resources
- `Running`: Currently executing
- `Succeeded`: All steps completed successfully
- `Failed`: One or more steps failed
- `Error`: Workflow-level error

## 🚀 Production Considerations

### Scalability
- **Horizontal Scaling**: Multiple workflow controllers
- **Resource Optimization**: Adjust limits based on workload
- **Auto-scaling**: Use HPA for workflow controller

### Reliability
- **Retry Logic**: Configure retry policies for failed steps
- **Timeout Handling**: Set appropriate timeouts
- **Error Handling**: Implement graceful degradation

### Monitoring
- **Metrics**: Prometheus metrics for Argo Workflows
- **Logging**: Structured logging for all steps
- **Alerting**: Set up alerts for workflow failures

## 📚 Related Resources

- [Argo Workflows Documentation](https://argoproj.github.io/argo-workflows/)
- [Kubernetes RBAC](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Scikit-learn Documentation](https://scikit-learn.org/)

## 🤝 Contributing

When modifying the pipeline:

1. **Test Locally**: Run with small datasets first
2. **Update Documentation**: Keep this README current
3. **Follow Conventions**: Use consistent naming and structure
4. **Security Review**: Ensure RBAC permissions are minimal

## 📝 License

This project is part of the MLOps interview preparation guide. 