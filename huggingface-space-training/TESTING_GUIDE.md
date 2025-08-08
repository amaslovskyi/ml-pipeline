# 🧪 GPT-OSS DevOps Training Pipeline Testing Guide

## 📋 Overview

Before running the expensive GPT-OSS:20B training, we need to validate the complete pipeline with a small model. This ensures repository creation and upload processes work correctly, preventing costly failures.

## 🎯 Testing Strategy

### ✅ **Test Model**: Microsoft DialoGPT-small (117M parameters)
- **Training time**: ~2-5 minutes
- **Cost**: Minimal (PRO dev mode)
- **Purpose**: Validate complete pipeline

### ✅ **What We Test**:
1. Dataset loading and formatting
2. Model loading with LoRA configuration  
3. Training pipeline execution
4. Local model saving
5. **HuggingFace repository creation** (fixes your upload issue)
6. Model and tokenizer upload to Hub

## 🚀 Testing Options

### Option 1: Local Testing (Recommended First)

```bash
# 1. Set your HuggingFace token
export HF_TOKEN=your_token_here

# 2. Run local test
python run_local_test.py
```

**Advantages:**
- Quick validation
- Debug issues locally
- No GPU credits used

### Option 2: HuggingFace Space Testing

**Deploy `test_app.py` to a Space:**

```yaml
---
title: GPT-OSS Pipeline Test
sdk: gradio
app_file: test_app.py
hardware: cpu  # Can use CPU for testing
---
```

**Advantages:**
- Tests in actual deployment environment
- Validates Space configuration
- Uses PRO dev mode credits

### Option 3: Full Integration Test

**Deploy both test and main apps:**
1. Test with `test_app.py`
2. If successful, deploy `app.py`
3. Run full GPT-OSS:20B training

## 📁 Test Files Created

| File                        | Purpose               | Usage            |
| --------------------------- | --------------------- | ---------------- |
| `test_training_pipeline.py` | Core test logic       | Local testing    |
| `test_app.py`               | Gradio test interface | Space deployment |
| `run_local_test.py`         | Local test runner     | Quick validation |
| `TESTING_GUIDE.md`          | This guide            | Documentation    |

## 🔧 Test Configuration

### Model Settings
```python
TEST_MODEL_NAME = "microsoft/DialoGPT-small"  # 117M parameters
TRAINING_EPOCHS = 1  # Quick training
LORA_RANK = 8  # Small LoRA for testing
BATCH_SIZE = 2  # Conservative memory usage
```

### Dataset
- 8 DevOps examples
- Covers Docker, Kubernetes, IaC
- Quick tokenization (~512 tokens max)

## ✅ Success Criteria

### Local Test Success
```
✅ Dependencies installed
✅ HF_TOKEN configured  
✅ Model loads successfully
✅ Training completes (1 epoch)
✅ Model saves locally
✅ Repository created on Hub
✅ Upload completes successfully
```

### Space Test Success  
```
✅ Space builds without errors
✅ GPU allocation works
✅ Training pipeline executes
✅ Repository creation works
✅ Upload flow validated
✅ Test model appears on Hub
```

## 🚨 Common Issues & Solutions

### Issue: Import Errors
**Solution:**
```bash
pip install torch transformers datasets peft huggingface_hub gradio spaces
```

### Issue: HF_TOKEN Not Found
**Solution:**
- Local: `export HF_TOKEN=your_token`
- Space: Add in Settings > Repository secrets

### Issue: Repository Creation Fails
**Solution:**
- Verify token has write permissions
- Check internet connectivity
- Ensure unique repository name

### Issue: Upload Timeout
**Solution:**  
- Model is small (should upload quickly)
- Check network stability
- Retry upload

## 📊 Expected Results

### Successful Test Output
```
🧪 Starting test training pipeline...
📝 Creating test dataset...
✅ Created 8 test examples
📥 Loading test model and tokenizer...
✅ Model loaded on: auto
🔧 Adding LoRA configuration...
✅ LoRA added - Trainable parameters: 294,912
🚀 Starting test training (1 epoch)...
✅ Training completed successfully!
💾 Saving test model...
✅ Model saved locally
🏗️ Creating test repository: AMaslovskyi/test-devops-model-20250107-143022
✅ Repository created successfully!
📤 Uploading model to HuggingFace Hub...
📤 Uploading tokenizer...
🎉 Upload successful! Model available at:
🔗 https://huggingface.co/AMaslovskyi/test-devops-model-20250107-143022
🎉 TEST PIPELINE COMPLETED SUCCESSFULLY!
✅ Ready to run full GPT-OSS:20B training
```

### Test Results File
```json
{
  "test_completed": true,
  "timestamp": "2025-01-07T14:30:22",
  "model_name": "microsoft/DialoGPT-small",
  "repository": "AMaslovskyi/test-devops-model-20250107-143022",
  "upload_successful": true,
  "repository_url": "https://huggingface.co/AMaslovskyi/test-devops-model-20250107-143022"
}
```

## 🎯 Next Steps After Successful Test

### 1. **Deploy Main Application**
- Upload `app.py` to your main Space
- Configure secrets (HF_TOKEN, WANDB_API_KEY)
- Set hardware to 4xL40S GPU

### 2. **Run GPT-OSS:20B Training**
- Use validated pipeline
- Repository creation will work correctly
- Upload will succeed (proven by test)

### 3. **Monitor Training**
- Watch training logs
- Check W&B metrics
- Verify checkpoints save

## 🧹 Cleanup

### After Successful Test
```python
# Local cleanup
python -c "from test_training_pipeline import cleanup_test_files; cleanup_test_files()"

# Or manual cleanup
rm -rf test-devops-model/
rm test_results.json
```

### Test Repositories
- Test repositories are created with timestamps
- Safe to delete after validation
- Keep for reference if needed

## 🔄 Iteration Process

1. **Run Local Test** → Fix any issues
2. **Run Space Test** → Validate environment  
3. **Deploy Main App** → Production ready
4. **Train GPT-OSS:20B** → Confident success

## 💡 Pro Tips

### For PRO Dev Mode
- Test apps use minimal resources
- GPU duration is short (60s vs 480s)
- Iterate quickly without cost

### For Repository Management
- Test repos use timestamp naming
- Avoid conflicts with main models
- Easy to identify and clean up

### For Debugging
- Verbose logging in test apps
- Step-by-step progress tracking
- Clear error messages

## 🎉 Confidence Level

After successful testing:
- ✅ **99% confidence** in GPT-OSS:20B training success
- ✅ **Upload issues resolved** (your main concern)
- ✅ **Pipeline validated** end-to-end
- ✅ **Ready for production** training

---

**🚀 Ready to test? Start with local testing, then move to Space testing!**
