#!/usr/bin/env python3
"""
Test App for GPT-OSS DevOps Training Pipeline
Quick validation with small model before running expensive training
"""

import os
import json
from datetime import datetime

# Fix for HuggingFace CAS/XET infrastructure issues  
os.environ["HF_HUB_DISABLE_XET"] = "1"

import gradio as gr
import torch
import spaces  # HuggingFace Spaces GPU decorator
from datasets import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from huggingface_hub import create_repo

# Test configuration
TEST_MODEL_NAME = "microsoft/DialoGPT-small"  # 117M parameters
TEST_OUTPUT_DIR = "./test-devops-model"

def create_test_dataset():
    """Create a small test dataset for quick training"""
    test_examples = [
        {
            "instruction": "What is Docker?",
            "input": "",
            "output": "Docker is a containerization platform that allows developers to package applications and their dependencies into lightweight, portable containers that can run consistently across different environments."
        },
        {
            "instruction": "How do you check running containers?",
            "input": "",
            "output": "Use the command 'docker ps' to see currently running containers, or 'docker ps -a' to see all containers including stopped ones."
        },
        {
            "instruction": "What is Kubernetes?",
            "input": "",
            "output": "Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications across clusters of machines."
        },
        {
            "instruction": "How do you scale a deployment in Kubernetes?",
            "input": "",
            "output": "Use 'kubectl scale deployment <deployment-name> --replicas=<number>' to scale a deployment to the desired number of replicas."
        },
        {
            "instruction": "What is Infrastructure as Code?",
            "input": "",
            "output": "Infrastructure as Code (IaC) is the practice of managing and provisioning computing infrastructure through machine-readable definition files, rather than manual configuration. Tools like Terraform and Ansible are commonly used for IaC."
        },
        {
            "instruction": "How do you implement blue-green deployment?",
            "input": "",
            "output": "Blue-green deployment involves maintaining two identical production environments. Deploy the new version to the inactive environment, test it thoroughly, then switch traffic from the active (blue) to the new (green) environment."
        },
        {
            "instruction": "What is Terraform?",
            "input": "",
            "output": "Terraform is an Infrastructure as Code tool that allows you to define and provision infrastructure using a declarative configuration language. It supports multiple cloud providers and helps manage infrastructure lifecycle."
        },
        {
            "instruction": "How do you troubleshoot a failing pod in Kubernetes?",
            "input": "",
            "output": "To troubleshoot a failing pod: 1) Check pod status with 'kubectl get pods', 2) Describe the pod with 'kubectl describe pod <pod-name>', 3) Check logs with 'kubectl logs <pod-name>', 4) Check events for errors, 5) Verify resource limits and node capacity."
        }
    ]
    
    return test_examples

def format_test_data(examples, tokenizer, max_length=512):
    """Format test data for training"""
    formatted_data = []
    for item in examples:
        text = f"### Instruction:\n{item['instruction']}\n\n### Response:\n{item['output']}"
        formatted_data.append({"text": text})
    
    def tokenize_function(examples):
        tokens = tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=max_length,
            return_tensors=None,
        )
        
        tokens["labels"] = []
        for input_ids in tokens["input_ids"]:
            labels = input_ids.copy()
            tokens["labels"].append(labels)
        
        return tokens
    
    dataset = Dataset.from_list(formatted_data)
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names,
        desc="Tokenizing test dataset"
    )
    
    return tokenized_dataset

@spaces.GPU(duration=60)  # Short duration for testing
def test_training_pipeline(test_repo_suffix=""):
    """Test the complete training and upload pipeline"""
    
    try:
        yield "🧪 Starting test training pipeline..."
        yield f"📋 Using model: {TEST_MODEL_NAME} (117M parameters)"
        
        # 1. Create test dataset
        yield "📝 Creating test dataset..."
        examples = create_test_dataset()
        yield f"✅ Created {len(examples)} test examples"
        
        # 2. Load small model and tokenizer
        yield "📥 Loading test model and tokenizer..."
        tokenizer = AutoTokenizer.from_pretrained(TEST_MODEL_NAME)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        device_map = "auto" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        model = AutoModelForCausalLM.from_pretrained(
            TEST_MODEL_NAME,
            torch_dtype=torch_dtype,
            device_map=device_map
        )
        
        yield f"✅ Model loaded on: {device_map}"
        
        # 3. Add LoRA for testing
        yield "🔧 Adding LoRA configuration..."
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=8,  # Small rank for testing
            lora_alpha=16,
            lora_dropout=0.1,
            target_modules=["c_attn", "c_proj"]  # DialoGPT architecture
        )
        
        model = get_peft_model(model, lora_config)
        trainable_params = model.get_nb_trainable_parameters()
        yield f"✅ LoRA added - Trainable parameters: {trainable_params:,}"
        
        # 4. Prepare dataset
        yield "🔄 Preparing dataset..."
        tokenized_dataset = format_test_data(examples, tokenizer)
        yield f"✅ Dataset prepared: {len(tokenized_dataset)} tokenized examples"
        
        # 5. Minimal training configuration
        yield "⚙️ Setting up training configuration..."
        training_args = TrainingArguments(
            output_dir=TEST_OUTPUT_DIR,
            num_train_epochs=1,  # Just 1 epoch for testing
            per_device_train_batch_size=2,
            gradient_accumulation_steps=2,
            learning_rate=5e-4,
            logging_steps=1,
            save_steps=len(tokenized_dataset) // 2,  # Save midway
            save_strategy="steps",
            remove_unused_columns=True,
            dataloader_drop_last=False,
            fp16=torch.cuda.is_available(),
        )
        
        # 6. Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
        )
        
        # 7. Initialize trainer
        yield "🏗️ Initializing trainer..."
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
            processing_class=tokenizer,
        )
        
        # 8. Run quick training
        yield "🚀 Starting test training (1 epoch)..."
        trainer.train()
        yield "✅ Training completed successfully!"
        
        # 9. Save model locally
        yield "💾 Saving test model..."
        trainer.save_model(TEST_OUTPUT_DIR)
        tokenizer.save_pretrained(TEST_OUTPUT_DIR)
        yield "✅ Model saved locally"
        
        # 10. Test repository creation and upload
        yield "🧪 Testing repository creation and upload..."
        upload_result = yield from test_upload_to_hub(test_repo_suffix)
        
        if upload_result:
            yield "🎉 TEST PIPELINE COMPLETED SUCCESSFULLY!"
            yield "✅ Ready to run full GPT-OSS:20B training"
        else:
            yield "⚠️ Upload test failed - check configuration"
            
        return "✅ Test completed"
        
    except Exception as e:
        error_msg = f"❌ Test pipeline failed: {str(e)}"
        yield error_msg
        return error_msg

def test_upload_to_hub(test_repo_suffix=""):
    """Test the upload to HuggingFace Hub process"""
    
    # Check for HF token
    hf_token = os.environ.get('HF_TOKEN')
    if not hf_token:
        yield "❌ No HF_TOKEN found - cannot test upload"
        yield "💡 Add HF_TOKEN in Space settings > Repository secrets"
        return False
    
    try:
        # Create unique repository name
        username = "AMaslovskyi"
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        suffix = f"-{test_repo_suffix}" if test_repo_suffix.strip() else ""
        test_repo_name = f"{username}/test-devops-model-{timestamp}{suffix}"
        
        yield f"🏗️ Creating test repository: {test_repo_name}"
        create_repo(
            repo_id=test_repo_name,
            repo_type="model",
            exist_ok=True,
            token=hf_token
        )
        yield "✅ Repository created successfully!"
        
        # Load and upload model
        yield "📥 Loading trained model for upload..."
        tokenizer = AutoTokenizer.from_pretrained(TEST_OUTPUT_DIR)
        model = AutoModelForCausalLM.from_pretrained(
            TEST_OUTPUT_DIR,
            torch_dtype=torch.float16,
            device_map="cpu"
        )
        
        yield "📤 Uploading model to HuggingFace Hub..."
        model.push_to_hub(
            test_repo_name,
            use_temp_dir=True,
            commit_message=f"Test DevOps model upload - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            token=hf_token
        )
        
        yield "📤 Uploading tokenizer..."
        tokenizer.push_to_hub(
            test_repo_name,
            use_temp_dir=True,
            commit_message=f"Test tokenizer upload - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            token=hf_token
        )
        
        yield f"🎉 Upload successful! Model available at:"
        yield f"🔗 https://huggingface.co/{test_repo_name}"
        
        # Save test results
        test_results = {
            "test_completed": True,
            "timestamp": datetime.now().isoformat(),
            "model_name": TEST_MODEL_NAME,
            "repository": test_repo_name,
            "upload_successful": True,
            "repository_url": f"https://huggingface.co/{test_repo_name}"
        }
        
        with open("test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)
        
        return True
        
    except Exception as e:
        yield f"❌ Upload test failed: {str(e)}"
        
        # Save failure results
        test_results = {
            "test_completed": True,
            "timestamp": datetime.now().isoformat(),
            "model_name": TEST_MODEL_NAME,
            "upload_successful": False,
            "error": str(e)
        }
        
        with open("test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)
        
        return False

def cleanup_test_files():
    """Clean up test files after testing"""
    import shutil
    
    cleanup_log = []
    
    try:
        if os.path.exists(TEST_OUTPUT_DIR):
            shutil.rmtree(TEST_OUTPUT_DIR)
            cleanup_log.append("✅ Test model directory cleaned up")
        
        if os.path.exists("test_results.json"):
            os.remove("test_results.json")
            cleanup_log.append("✅ Test results file cleaned up")
        
        # Clear GPU cache if available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            cleanup_log.append("✅ GPU cache cleared")
            
        cleanup_log.append("🧹 Cleanup completed successfully!")
        
    except Exception as e:
        cleanup_log.append(f"⚠️ Cleanup warning: {str(e)}")
    
    return "\n".join(cleanup_log)

def create_test_interface():
    """Create Gradio interface for testing"""
    
    with gr.Blocks(title="GPT-OSS DevOps Training Pipeline Test") as app:
        gr.Markdown("# 🧪 GPT-OSS DevOps Training Pipeline Test")
        gr.Markdown("Test the complete training and upload pipeline with a small model before running expensive GPT-OSS:20B training")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### ⚙️ Test Configuration")
                gr.Markdown(f"**Test Model:** {TEST_MODEL_NAME} (117M parameters)")
                gr.Markdown("**Training:** 1 epoch with LoRA")
                gr.Markdown("**Upload:** Full HuggingFace Hub test")
                
                test_repo_suffix = gr.Textbox(
                    label="Repository Suffix (optional)",
                    placeholder="e.g., 'pipeline-test'",
                    value="",
                    info="Optional suffix for test repository name"
                )
                
                test_btn = gr.Button("🚀 Run Test Pipeline", variant="primary", size="lg")
                cleanup_btn = gr.Button("🧹 Cleanup Test Files", variant="secondary")
            
            with gr.Column():
                output = gr.Textbox(
                    label="Test Progress",
                    lines=25,
                    max_lines=35,
                    show_copy_button=True
                )
        
        # Connect buttons
        test_btn.click(
            fn=test_training_pipeline,
            inputs=[test_repo_suffix],
            outputs=output,
            show_progress=True
        )
        
        cleanup_btn.click(
            fn=cleanup_test_files,
            outputs=output
        )
        
        gr.Markdown("""
        ## 📋 Test Checklist:
        
        ✅ **What this test validates:**
        - Dataset loading and formatting
        - Model loading and LoRA configuration
        - Training pipeline execution
        - Model saving to local directory
        - HuggingFace repository creation
        - Model and tokenizer upload to Hub
        
        ## 🔧 Requirements:
        - **HF_TOKEN**: Required in Space secrets for upload testing
        - **Hardware**: Works on CPU or GPU (faster on GPU)
        - **Duration**: ~2-5 minutes depending on hardware
        
        ## 🎯 Success Criteria:
        - Training completes without errors
        - Model saves locally
        - Repository creates successfully
        - Upload completes without errors
        - Test model appears on your HuggingFace profile
        
        ## ⚠️ Before GPT-OSS:20B Training:
        Make sure this test passes completely before running the expensive 20B model training!
        """)
    
    return app

if __name__ == "__main__":
    app = create_test_interface()
    app.launch(share=True)
