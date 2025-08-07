# 📁 Scripts Directory Structure

This document outlines the organized structure of the scripts directory for better maintainability and clear separation of concerns.

## 📂 Directory Overview

```
scripts/
├── aws-tools/           # AWS infrastructure and credential management
├── argo-tools/         # Argo Workflows and GitOps tools
├── data-tools/         # Data processing and DVC management
├── deployment/         # Container and Kubernetes deployment files
├── evaluation-legacy/  # Legacy evaluation scripts (moved to eval/)
├── inference-legacy/   # Legacy inference tools (deprecated)
└── ollama-legacy/     # Legacy Ollama conversion attempts
```

## ☁️ aws-tools/

**Purpose**: AWS infrastructure setup and credential management

| **File**                    | **Purpose**                             | **Usage**                     |
| --------------------------- | --------------------------------------- | ----------------------------- |
| `deploy-s3-bucket.sh`       | Deploy S3 bucket for MLOps data storage | `./deploy-s3-bucket.sh`       |
| `update-aws-credentials.sh` | Update AWS credentials configuration    | `./update-aws-credentials.sh` |
| `setup-credentials.sh`      | Initial AWS credentials setup           | `./setup-credentials.sh`      |

## 🔄 argo-tools/

**Purpose**: Argo Workflows and GitOps pipeline management

| **File**                           | **Purpose**                           | **Usage**                            |
| ---------------------------------- | ------------------------------------- | ------------------------------------ |
| `setup-argo.sh`                    | Install and configure Argo Workflows  | `./setup-argo.sh`                    |
| `start-argo-ui.sh`                 | Start Argo UI for workflow monitoring | `./start-argo-ui.sh`                 |
| `run-argo-pipeline.sh`             | Execute ML training pipeline          | `./run-argo-pipeline.sh`             |
| `run-git-workflow.sh`              | Run Git-based workflow                | `./run-git-workflow.sh`              |
| `setup-repo-connection.sh`         | Configure repository connections      | `./setup-repo-connection.sh`         |
| `validate-deployment-readiness.sh` | Check deployment prerequisites        | `./validate-deployment-readiness.sh` |

## 📊 data-tools/

**Purpose**: Data processing, versioning, and DVC management

| **File**                             | **Purpose**                             | **Usage**                                   |
| ------------------------------------ | --------------------------------------- | ------------------------------------------- |
| `prepare-enhanced-devops-dataset.py` | Create enhanced DevOps training dataset | `python prepare-enhanced-devops-dataset.py` |
| `test-enhanced-dataset.py`           | Validate enhanced dataset quality       | `python test-enhanced-dataset.py`           |
| `update-dvc-config.sh`               | Update DVC configuration                | `./update-dvc-config.sh`                    |
| `update-dvc-to-onedrive.sh`          | Configure DVC for OneDrive storage      | `./update-dvc-to-onedrive.sh`               |

## 🚀 deployment/

**Purpose**: Container and Kubernetes deployment configurations

| **File**                     | **Purpose**                         | **Usage**                                   |
| ---------------------------- | ----------------------------------- | ------------------------------------------- |
| `Dockerfile`                 | Container image for model inference | `docker build -f Dockerfile .`              |
| `k8s-deployment.yaml`        | Kubernetes deployment manifest      | `kubectl apply -f k8s-deployment.yaml`      |
| `deploy-k8s.sh`              | Deploy to Kubernetes cluster        | `./deploy-k8s.sh`                           |
| `deploy-ollama.sh`           | Deploy Ollama model locally         | `./deploy-ollama.sh`                        |
| `requirements-inference.txt` | Python dependencies for inference   | `pip install -r requirements-inference.txt` |

## ✅ **Clean Structure** 

All legacy directories have been removed:
- ❌ `evaluation-legacy/` - Duplicates moved to `../eval/evaluation-scripts/`
- ❌ `inference-legacy/` - Superseded by `../eval/server-tools/`  
- ❌ `ollama-legacy/` - Failed attempts, working solution in `../eval/ollama-tools/`

## 🚀 Quick Start Commands

### Setup AWS Infrastructure
```bash
cd aws-tools/
./setup-credentials.sh
./deploy-s3-bucket.sh
```

### Setup Argo Workflows
```bash
cd argo-tools/
./setup-argo.sh
./start-argo-ui.sh
```

### Prepare Training Data
```bash
cd data-tools/
python prepare-enhanced-devops-dataset.py
python test-enhanced-dataset.py
```

### Deploy Model
```bash
cd deployment/
./deploy-k8s.sh
# OR for local Ollama deployment
./deploy-ollama.sh
```

## 🔧 Dependencies

- **aws-tools/**: AWS CLI, proper AWS credentials
- **argo-tools/**: kubectl, Argo Workflows CLI
- **data-tools/**: Python 3.8+, DVC, pandas, datasets
- **deployment/**: Docker, kubectl (for K8s), ollama (for local)

## 📝 Migration Notes

- **Evaluation scripts**: Moved to `../eval/evaluation-scripts/`
- **Server tools**: Moved to `../eval/server-tools/`
- **Ollama tools**: Working versions moved to `../eval/ollama-tools/`

## 💾 **Space Saved**

Cleanup results:
- **~15GB freed** by removing duplicate model files
- **Reduced complexity** with clear, focused directory structure
- **No functionality lost** - all working tools preserved in `../eval/`

---

**🎯 Remember**: This organized structure separates production tools from legacy code and groups related functionality for better maintainability.
