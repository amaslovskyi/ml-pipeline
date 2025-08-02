# Argo Workflows Web UI Guide

This guide shows you how to run the ML pipeline workflow from the Argo web UI.

## 🚀 Accessing the Argo Web UI

### 1. Start Port Forwarding
```bash
# Start port forwarding for Argo UI
kubectl port-forward -n argo svc/argo-workflows-server 2746:2746
```

### 2. Access the Web UI
Open your browser and navigate to:
```
https://localhost:2746
```

**Note**: The UI uses HTTPS with a self-signed certificate. You may need to:
- Click "Advanced" and "Proceed to localhost (unsafe)"
- Or add a security exception for the certificate

## 📋 Running the ML Pipeline from Web UI

### Step 1: Navigate to Workflows
1. Open the Argo web UI
2. Click on **"Workflows"** in the left sidebar
3. You'll see a list of existing workflows (if any)

### Step 2: Submit New Workflow
1. Click the **"SUBMIT NEW WORKFLOW"** button
2. You'll see a form with several options:
   - **Namespace**: Select `argo`
   - **Workflow YAML**: You can paste the YAML content
   - **File Upload**: Or upload the workflow file

### Step 3: Upload Workflow File
**Option A: Upload File**
1. Click **"Choose File"**
2. Select `ml-pipeline/argo-workflows/ml-pipeline.yaml`
3. Click **"SUBMIT"**

**Option B: Paste YAML**
1. Click **"Edit YAML"**
2. Copy and paste the content of `ml-pipeline.yaml`
3. Click **"SUBMIT"**

### Step 4: Configure Parameters (Optional)
Before submitting, you can modify the parameters:

```yaml
arguments:
  parameters:
    - name: model-name
      value: "bert-classifier"        # Change model name
    - name: data-version
      value: "v1.0"                  # Change data version
    - name: epochs
      value: "3"                      # Change training epochs
    - name: batch-size
      value: "16"                     # Change batch size
    - name: dvc-s3-bucket
      value: "mlops-data-bucket-1754148674-amaslovs"  # Your S3 bucket
    - name: dvc-s3-region
      value: "us-east-1"              # Your AWS region
```

## 📊 Monitoring Workflow Execution

### Real-time Monitoring
1. **Workflow List**: See all workflows and their status
2. **Workflow Details**: Click on a workflow to see detailed view
3. **Step-by-step Progress**: Watch each step execute in real-time
4. **Logs**: Click on any step to view its logs

### Workflow Status Indicators
- 🟡 **Pending**: Waiting for resources
- 🔵 **Running**: Currently executing
- 🟢 **Succeeded**: Completed successfully
- 🔴 **Failed**: One or more steps failed
- ⚫ **Error**: Workflow-level error

## 🔍 Viewing Workflow Details

### Workflow Overview
- **Name**: `ml-training-pipeline`
- **Namespace**: `argo`
- **Status**: Current execution status
- **Duration**: Total execution time
- **Parameters**: All input parameters

### Step-by-step Monitoring
1. **Data Preprocessing**: Creates and versions data
2. **Feature Engineering**: Processes features with DVC
3. **Model Training**: Trains model with MLflow tracking
4. **Model Evaluation**: Calculates metrics
5. **Model Registration**: Registers model in MLflow

### Viewing Logs
1. Click on any step in the workflow
2. Click **"Logs"** tab
3. See real-time execution logs
4. Monitor progress and errors

## 🛠️ Troubleshooting Web UI

### Common Issues

**1. Port Forwarding Fails**
```bash
# Check if Argo server is running
kubectl get pods -n argo -l app=argo-workflows-server

# Restart port forwarding
kubectl port-forward -n argo svc/argo-workflows-server 2746:2746
```

**2. Certificate Warning**
- Click "Advanced" → "Proceed to localhost (unsafe)"
- Or use HTTP instead: `http://localhost:2746`

**3. Workflow Submission Fails**
- Check YAML syntax
- Verify namespace is `argo`
- Ensure RBAC is applied: `kubectl apply -f rbac-config.yaml`

**4. Workflow Stuck**
- Check pod status: `kubectl get pods -n argo`
- View workflow controller logs: `kubectl logs -n argo -l app=workflow-controller`

## 📈 Advanced Web UI Features

### 1. Workflow Templates
- Create reusable workflow templates
- Save common configurations
- Share templates across team

### 2. Workflow Archives
- View completed workflows
- Compare different runs
- Analyze performance trends

### 3. Real-time Metrics
- Monitor resource usage
- Track execution times
- View step dependencies

### 4. Workflow Visualization
- See DAG (Directed Acyclic Graph) visualization
- Understand step dependencies
- Monitor parallel execution

## 🔧 Customizing Workflow Parameters

### Modifying Parameters in Web UI
1. Click **"Edit YAML"** before submitting
2. Modify the `arguments.parameters` section
3. Update values as needed
4. Click **"SUBMIT"**

### Example Parameter Changes
```yaml
# Change model name
- name: model-name
  value: "custom-sentiment-model"

# Change data version
- name: data-version
  value: "v2.0"

# Change training parameters
- name: epochs
  value: "10"
- name: batch-size
  value: "32"

# Change DVC configuration
- name: dvc-s3-bucket
  value: "your-new-bucket-name"
```

## 📱 Mobile-Friendly Features
- Responsive design works on tablets
- Touch-friendly interface
- Swipe gestures for navigation

## 🔐 Security Considerations
- HTTPS by default
- Self-signed certificates for local development
- RBAC controls access
- Namespace isolation

## 🎯 Best Practices

### 1. Before Running
- ✅ Verify Argo server is running
- ✅ Apply RBAC configuration
- ✅ Check S3 bucket configuration
- ✅ Ensure MLflow server is accessible

### 2. During Execution
- 📊 Monitor real-time logs
- 🔍 Watch step-by-step progress
- ⚠️ Check for errors early
- 📈 Track resource usage

### 3. After Completion
- 📋 Review all step logs
- 📊 Check MLflow for metrics
- 💾 Verify DVC data versioning
- 🔄 Plan next iteration

## 🚀 Quick Start Commands

```bash
# 1. Start port forwarding
kubectl port-forward -n argo svc/argo-workflows-server 2746:2746

# 2. Open browser
open https://localhost:2746

# 3. Submit workflow from UI
# - Click "SUBMIT NEW WORKFLOW"
# - Upload ml-pipeline.yaml
# - Click "SUBMIT"

# 4. Monitor execution
# - Watch real-time progress
# - Check logs for each step
# - Verify completion status
```

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Argo documentation: https://argoproj.github.io/argo-workflows/
3. Check Kubernetes logs for detailed error messages
4. Verify all prerequisites are met

---

**Happy Workflow Orchestration! 🎉** 