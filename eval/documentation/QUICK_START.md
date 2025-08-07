# 🚀 Quick Start Evaluation Guide

## ⚡ 5-Minute Model Testing

### 1. **Basic Performance Test**
```bash
python3 quick_devops_test.py
```
**Expected Output**: 5 test questions, accuracy scores, timing

### 2. **System Compatibility Check**
```bash
python3 laptop_performance_analysis.py
```
**Expected Output**: RAM analysis, performance predictions

### 3. **Server + API Test**
```bash
# Terminal 1: Start server
./run_direct_server.sh

# Terminal 2: Test API
python3 quick_test.py
```

## 📊 Comprehensive Evaluation (30 minutes)

### 1. **Full DevOps Assessment**
```bash
python3 devops_model_evaluation.py
# Choose option 2 (Load model locally)
```

### 2. **Model Comparison**
```bash
# Make sure qwen3:8b is installed
ollama pull qwen3:8b

# Run comparison
python3 model_comparison.py
```

### 3. **Generate Report**
```bash
python3 performance_report.py
```

## 🎯 Expected Results

### ✅ **Quick Test Results**
- Accuracy: ~0.60 (Good)
- Speed: ~40s per question
- Strong: CI/CD, Docker security
- Weak: Kubernetes, IaC

### 📊 **System Requirements**
- RAM needed: ~21GB
- Your 48GB laptop: ✅ Excellent
- Loading time: ~60s
- Performance: Fast inference

## 🔧 Troubleshooting

### **Model Loading Issues**
```bash
# Check model files
ls ~/Downloads/qwen-devops-model/

# Expected files:
# - adapter_model.safetensors
# - adapter_config.json  
# - tokenizer files
```

### **Server Won't Start**
```bash
# Install dependencies
pip install torch transformers peft fastapi uvicorn

# Check available RAM
python3 -c "import psutil; print(f'Available: {psutil.virtual_memory().available/(1024**3):.1f}GB')"
```

### **Slow Performance**
- Close other applications
- Use CPU-only mode (already configured)
- Reduce max_length in scripts

## 📁 Quick File Reference

| File                             | Purpose              | Runtime   |
| -------------------------------- | -------------------- | --------- |
| `quick_devops_test.py`           | Fast 5-question test | 3-5 min   |
| `laptop_performance_analysis.py` | System check         | 30 sec    |
| `devops_model_evaluation.py`     | Full evaluation      | 20-30 min |
| `model_comparison.py`            | vs Base model        | 15-20 min |
| `performance_report.py`          | Summary report       | 5 sec     |

## 🎯 Success Indicators

✅ **Model Working**: Generates relevant DevOps responses  
✅ **Good Performance**: >0.5 accuracy, <60s response time  
✅ **System Compatible**: Loads without memory errors  
✅ **Production Ready**: >0.6 accuracy, stable responses
