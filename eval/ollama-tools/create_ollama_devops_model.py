#!/usr/bin/env python3
"""
Create DevOps-optimized Ollama model from base Qwen3:8b
This approach works by creating a specialized Modelfile with DevOps-focused prompts
"""

import subprocess
import os
import tempfile

def create_devops_ollama_model():
    """Create DevOps-optimized Ollama model"""
    
    print("🦙 Creating DevOps-Optimized Ollama Model")
    print("=" * 45)
    
    # Enhanced DevOps Modelfile with specialized system prompt
    modelfile_content = """FROM qwen3:8b

# DevOps Expert System Prompt
SYSTEM \"\"\"You are a Senior DevOps Engineer and Site Reliability Expert with 10+ years of experience. You specialize in:

🚀 **CI/CD & Build Automation**
- GitHub Actions, Jenkins, GitLab CI workflows
- Build optimization and dependency management
- Automated testing and quality gates
- Deployment strategies (blue-green, canary, rolling)

🐳 **Containerization & Orchestration**
- Docker production best practices and security
- Kubernetes deployment, scaling, and troubleshooting
- Helm charts and package management
- Container registry and image optimization

🏗️ **Infrastructure as Code**
- Terraform modules and state management
- Ansible playbooks and automation
- AWS/GCP/Azure resource provisioning
- Infrastructure monitoring and compliance

🔧 **Troubleshooting & Monitoring**
- Systematic debugging methodologies
- Log analysis and distributed tracing
- Performance optimization and capacity planning
- Incident response and post-mortem analysis

🔒 **Security & Compliance**
- Container security scanning and hardening
- Secrets management and RBAC
- Vulnerability assessment and remediation
- SOC2, PCI-DSS compliance frameworks

Always provide:
1. **Practical, actionable solutions** with concrete steps
2. **Code examples** with proper syntax and error handling
3. **Best practices** for production environments
4. **Security considerations** for all recommendations
5. **Troubleshooting steps** when things go wrong

Format responses with clear structure, use bullet points, and include relevant commands or configuration examples.\"\"\"

# Optimized parameters for DevOps responses
PARAMETER temperature 0.7
PARAMETER top_p 0.8
PARAMETER top_k 20
PARAMETER repeat_penalty 1.05
PARAMETER num_ctx 4096

# Stop tokens
PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
"""

    # Create temporary Modelfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.modelfile', delete=False) as f:
        f.write(modelfile_content)
        modelfile_path = f.name
    
    try:
        print("📝 Created enhanced DevOps Modelfile")
        print("🔄 Creating Ollama model...")
        
        # Create the model
        result = subprocess.run([
            "ollama", "create", "qwen-devops", "-f", modelfile_path
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ DevOps model created successfully!")
            print("\n🎉 Model: qwen-devops")
            print("📖 Based on: qwen3:8b with DevOps specialization")
            
            # Test the model
            print("\n🧪 Testing the model...")
            test_model()
            
            print("\n🚀 Usage:")
            print("   ollama run qwen-devops")
            print("\n💬 Example:")
            print('   ollama run qwen-devops "How do I set up a CI/CD pipeline?"')
            
            return True
        else:
            print(f"❌ Model creation failed: {result.stderr}")
            return False
            
    finally:
        # Clean up temporary file
        os.unlink(modelfile_path)

def test_model():
    """Test the created DevOps model"""
    test_questions = [
        "How do I deploy to Kubernetes?",
        "What are Docker best practices?",
        "How to troubleshoot a failing pod?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 Test {i}: {question}")
        
        try:
            result = subprocess.run([
                "ollama", "run", "qwen-devops", question
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                response = result.stdout.strip()
                print(f"✅ Response: {response[:100]}...")
                
                # Check for DevOps keywords
                devops_keywords = ["deployment", "docker", "kubernetes", "pipeline", "security"]
                found_keywords = [kw for kw in devops_keywords if kw.lower() in response.lower()]
                
                if found_keywords:
                    print(f"🎯 DevOps keywords found: {found_keywords}")
                else:
                    print("⚠️ Limited DevOps context in response")
            else:
                print(f"❌ Test failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⏱️ Test timed out")
        except Exception as e:
            print(f"❌ Test error: {str(e)}")

def create_devops_shortcuts():
    """Create convenient DevOps-specific model shortcuts"""
    
    shortcuts = {
        "qwen-docker": {
            "base": "qwen-devops",
            "system": "You are a Docker expert. Focus on containerization, security, and optimization. Always include practical examples with Dockerfile snippets."
        },
        "qwen-k8s": {
            "base": "qwen-devops", 
            "system": "You are a Kubernetes expert. Focus on deployments, troubleshooting, and best practices. Always provide kubectl commands and YAML examples."
        },
        "qwen-cicd": {
            "base": "qwen-devops",
            "system": "You are a CI/CD expert. Focus on GitHub Actions, Jenkins, and deployment automation. Always provide workflow examples and best practices."
        }
    }
    
    print("\n🔧 Creating specialized DevOps shortcuts...")
    
    for model_name, config in shortcuts.items():
        modelfile_content = f"""FROM {config["base"]}

SYSTEM \"\"\"{config["system"]}\"\"\"

PARAMETER temperature 0.7
PARAMETER top_p 0.8
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.modelfile', delete=False) as f:
            f.write(modelfile_content)
            modelfile_path = f.name
        
        try:
            result = subprocess.run([
                "ollama", "create", model_name, "-f", modelfile_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Created {model_name}")
            else:
                print(f"⚠️ Failed to create {model_name}: {result.stderr}")
                
        finally:
            os.unlink(modelfile_path)

def main():
    """Main function"""
    print("🦙 Ollama DevOps Model Creator")
    print("=" * 35)
    
    # Check if base model exists
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if "qwen3:8b" not in result.stdout:
            print("❌ Base model qwen3:8b not found")
            print("💡 Run: ollama pull qwen3:8b")
            return
    except:
        print("❌ Ollama not available")
        return
    
    # Create main DevOps model
    success = create_devops_ollama_model()
    
    if success:
        # Ask user if they want shortcuts
        try:
            create_shortcuts = input("\n🔧 Create specialized shortcuts (docker, k8s, ci-cd)? (y/n): ").strip().lower()
            if create_shortcuts in ['y', 'yes']:
                create_devops_shortcuts()
        except KeyboardInterrupt:
            print("\n👋 Skipping shortcuts")
        
        print(f"\n🎉 DevOps Ollama models ready!")
        print(f"📋 Available models:")
        print(f"   • qwen-devops (main DevOps expert)")
        
        # Check what was actually created
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            created_models = [line.split()[0] for line in result.stdout.split('\n')[1:] if 'qwen-' in line]
            for model in created_models:
                if model.startswith('qwen-') and model != 'qwen3:8b':
                    print(f"   • {model}")
        except:
            pass
    else:
        print("❌ DevOps model creation failed")

if __name__ == "__main__":
    main()
