# 🦙 Ollama DevOps Model Usage Guide

## ✅ **Successfully Created: `qwen-devops`**

DevOps-optimized Ollama model is ready! Here's how to use it:

---

## 🚀 **Basic Usage**

### **Start Interactive Chat**
```bash
ollama run qwen-devops
```

### **Single Question**
```bash
ollama run qwen-devops "How do I set up a CI/CD pipeline?"
```

### **With Specific Context**
```bash
ollama run qwen-devops "I have a Node.js app. How do I create a Dockerfile for production?"
```

---

## 🎯 **What Makes This Model Special**

### **🔧 Enhanced DevOps System Prompt**
- Senior DevOps Engineer with 10+ years experience
- Specialized knowledge in CI/CD, Docker, Kubernetes, IaC
- Security-focused recommendations
- Practical, actionable solutions

### **⚙️ Optimized Parameters**
- **Temperature**: 0.7 (balanced creativity/accuracy)
- **Top-p**: 0.8 (focused responses)
- **Context**: 4096 tokens (handles complex scenarios)
- **Repeat penalty**: 1.05 (reduces repetition)

---

## 💡 **Example Conversations**

### **CI/CD Pipeline Setup**
```bash
ollama run qwen-devops "How do I create a GitHub Actions workflow for a Python web app?"
```
**Expected response**: Step-by-step workflow with YAML examples, testing stages, deployment strategies

### **Docker Security**
```bash
ollama run qwen-devops "What are the most important Docker security practices?"
```
**Expected response**: Non-root users, image scanning, minimal base images, secrets management

### **Kubernetes Troubleshooting**
```bash
ollama run qwen-devops "My pod is stuck in CrashLoopBackOff. How do I debug this?"
```
**Expected response**: Systematic debugging with kubectl commands, log analysis

### **Infrastructure as Code**
```bash
ollama run qwen-devops "How do I manage Terraform state securely?"
```
**Expected response**: Remote backends, state locking, encryption, best practices

---

## 📊 **Performance Characteristics**

| **Aspect**         | **Details**                           |
| ------------------ | ------------------------------------- |
| **Response Time**  | 30-90 seconds (depends on complexity) |
| **Base Model**     | qwen3:8b (5.2GB)                      |
| **Specialization** | High DevOps focus                     |
| **Code Examples**  | Includes practical examples           |
| **Best Practices** | Security and production focus         |

---

## 🔧 **Troubleshooting**

### **Model Takes Long to Respond**
- **Normal**: First response is slower (model loading)
- **Solution**: Subsequent responses are faster
- **Alternative**: Use shorter, more specific questions

### **Generic Responses**
- **Cause**: Question might be too broad
- **Solution**: Be more specific about your environment/tools
- **Example**: Instead of "How to deploy?" use "How to deploy Node.js to Kubernetes with Docker?"

### **Missing DevOps Context**
- **Cause**: Model might revert to general knowledge
- **Solution**: Emphasize DevOps context in your question
- **Example**: "As a DevOps engineer, how should I..."

---

## 🎯 **Best Practices for Questions**

### **✅ Good Questions**
- "How do I set up monitoring for a Kubernetes cluster with Prometheus?"
- "What's the best way to handle secrets in a Docker production environment?"
- "How do I implement blue-green deployment with GitHub Actions?"

### **❌ Avoid These**
- "How do I code?" (too general)
- "What is programming?" (not DevOps-focused)
- "Tell me about cats" (completely off-topic)

---

## 🚀 **Advanced Usage**

### **Custom System Prompts**
You can override the system prompt for specific use cases:

```bash
ollama run qwen-devops "You are a Kubernetes expert. Focus only on K8s solutions. How do I debug pod networking issues?"
```

### **Chaining Questions**
For complex scenarios, break into steps:

1. "What are the components of a complete CI/CD pipeline?"
2. "How do I implement the build stage you mentioned?"
3. "What security checks should I add to this pipeline?"

---

## 📋 **Available Models**

| **Model**     | **Purpose**             | **Command**              |
| ------------- | ----------------------- | ------------------------ |
| `qwen-devops` | General DevOps expert   | `ollama run qwen-devops` |
| `qwen3:8b`    | Base model (comparison) | `ollama run qwen3:8b`    |

---

## 🔍 **Model Comparison**

### **qwen-devops vs qwen3:8b**

| **Aspect**         | **qwen-devops** | **qwen3:8b** |
| ------------------ | --------------- | ------------ |
| **DevOps Focus**   | ✅ High          | ⚠️ General    |
| **Code Examples**  | ✅ Practical     | ⚠️ Generic    |
| **Security Focus** | ✅ Built-in      | ❌ Limited    |
| **Best Practices** | ✅ Emphasized    | ⚠️ Occasional |
| **Response Style** | 🎯 Structured    | 📝 Verbose    |

---

## 💾 **Model Management**

### **Check Available Models**
```bash
ollama list
```

### **Remove Model (if needed)**
```bash
ollama rm qwen-devops
```

### **Recreate Model**
```bash
python3 create_ollama_devops_model.py
```

---

## 🎉 **Success! Your DevOps Ollama Model is Ready**

**🚀 Start using it now:**
```bash
ollama run qwen-devops "How do I get started with Infrastructure as Code?"
```

**📊 Perfect for:**
- DevOps team guidance
- CI/CD pipeline assistance  
- Docker and Kubernetes help
- Infrastructure automation
- Security best practices
- Troubleshooting support

**🔧 Remember:** This model complements your fine-tuned LoRA model and provides another deployment option for DevOps assistance!
