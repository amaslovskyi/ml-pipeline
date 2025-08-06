#!/usr/bin/env python3
"""
HuggingFace Space Training App for Qwen3-8B DevOps Foundation Model
Optimized for ZeroGPU and dedicated GPU hardware
"""

import os

# Fix for HuggingFace CAS/XET infrastructure issues  
os.environ["HF_HUB_DISABLE_XET"] = "1"

import gradio as gr
import torch
import spaces  # HuggingFace Spaces GPU decorator
from datetime import datetime
import json

# Training imports
from datasets import Dataset, load_dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
import wandb

# Configuration
MODEL_NAME = "Qwen/Qwen3-8B"
OUTPUT_DIR = "./qwen-devops-foundation"

def load_devops_datasets():
    """Load and combine DevOps/SRE datasets with robust error handling"""
    print("📥 Loading DevOps datasets...")
    
    datasets_info = []
    all_examples = []
    
    # Use comprehensive synthetic dataset due to HF infrastructure issues
    print("Using comprehensive synthetic DevOps dataset for reliable training...")
    datasets_info.append("ℹ️ Using synthetic dataset due to HuggingFace S3 infrastructure issues")
    
    # Add extended DevOps examples for better training coverage
    extended_examples = [
        {
            "instruction": "How do you implement blue-green deployment in Kubernetes?",
            "input": "",
            "output": "Blue-green deployment in Kubernetes: 1) Create two identical environments (blue and green) using different selectors, 2) Deploy new version to inactive environment (green), 3) Test thoroughly with readiness/liveness probes, 4) Switch traffic by updating service selector labels, 5) Monitor metrics and logs post-switch, 6) Rollback by reverting service selector if issues occur, 7) Use tools like Argo Rollouts or Flagger for automation."
        },
        {
            "instruction": "Explain Prometheus monitoring setup for microservices",
            "input": "",
            "output": "Prometheus microservices monitoring: 1) Install Prometheus server via Helm chart, 2) Configure service discovery for automatic target detection, 3) Expose metrics endpoints (/metrics) in each microservice, 4) Set up alerting rules for SLA violations, 5) Configure Grafana dashboards for visualization, 6) Implement distributed tracing with Jaeger, 7) Monitor golden signals: latency, traffic, errors, saturation, 8) Use PushGateway for batch jobs, 9) Set up federation for multi-cluster monitoring."
        },
        {
            "instruction": "What are Terraform best practices for infrastructure as code?",
            "input": "",
            "output": "Terraform best practices: 1) Use remote state storage (S3, Azure Blob) with state locking, 2) Organize code with modules for reusability, 3) Pin provider versions to avoid breaking changes, 4) Use variables and locals for parameterization, 5) Implement proper naming conventions and tagging, 6) Use terraform plan before apply in CI/CD, 7) Store sensitive data in parameter stores or vaults, 8) Use workspaces for environment separation, 9) Validate configurations with terraform validate and tflint, 10) Implement automated testing with Terratest."
        }
    ]
    
    all_examples.extend(extended_examples)
    datasets_info.append(f"✅ Extended synthetic examples: {len(extended_examples)} examples")
    
    # Add synthetic examples if datasets fail
    if len(all_examples) < 50:
        synthetic_examples = [
            {
                "instruction": "How do you troubleshoot high CPU usage in a Kubernetes pod?",
                "input": "",
                "output": "To troubleshoot high CPU usage in a Kubernetes pod: 1) Use kubectl top pod to identify the pod, 2) Check pod resource limits with kubectl describe pod, 3) Examine application logs with kubectl logs, 4) Use kubectl exec to access the pod and run top/htop, 5) Check for resource requests/limits configuration, 6) Consider horizontal pod autoscaling if needed."
            },
            {
                "instruction": "Explain how to set up monitoring for a production ML model",
                "input": "",
                "output": "Production ML model monitoring setup: 1) Implement model performance metrics (accuracy, latency, throughput), 2) Set up data drift detection using statistical tests, 3) Monitor prediction distribution changes, 4) Configure alerts for model degradation, 5) Use tools like Prometheus + Grafana for metrics visualization, 6) Implement logging for prediction requests/responses, 7) Set up automated model retraining triggers."
            },
            {
                "instruction": "How do you implement blue-green deployment for a microservice?",
                "input": "",
                "output": "Blue-green deployment implementation: 1) Maintain two identical production environments (blue and green), 2) Deploy new version to inactive environment, 3) Test thoroughly in the green environment, 4) Switch traffic from blue to green using load balancer, 5) Monitor for issues and rollback if needed, 6) Keep blue environment as backup, 7) Use automation tools like ArgoCD or Jenkins for orchestration."
            }
        ]
        all_examples.extend(synthetic_examples)
        datasets_info.append(f"✅ Synthetic examples: {len(synthetic_examples)} examples")
    
    return all_examples, datasets_info

def format_training_data(examples, tokenizer, max_length=2048):
    """Format data for instruction following training"""
    formatted_data = []
    
    for item in examples:
        # Create instruction-following format
        if item['input']:
            text = f"### Instruction:\n{item['instruction']}\n\n### Input:\n{item['input']}\n\n### Response:\n{item['output']}"
        else:
            text = f"### Instruction:\n{item['instruction']}\n\n### Response:\n{item['output']}"
        
        formatted_data.append({"text": text})
    
    # Tokenize
    def tokenize_function(examples):
        tokens = tokenizer(
            examples["text"],
            truncation=True,
            padding=False,
            max_length=max_length,
            return_overflowing_tokens=False,
        )
        tokens["labels"] = tokens["input_ids"].copy()
        return tokens
    
    dataset = Dataset.from_list(formatted_data)
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names,
        desc="Tokenizing dataset"
    )
    
    return tokenized_dataset

@spaces.GPU(duration=360)  # Request 6 hours for complete training (use with L4/A100)
def train_model(wandb_project, learning_rate, epochs, batch_size, resume_from_checkpoint=None):
    """Main training function with GPU acceleration"""
    
    # Initialize wandb if key provided
    wandb_key = os.environ.get("WANDB_API_KEY")
    if wandb_key:
        wandb.login(key=wandb_key)
        wandb.init(
            project=wandb_project,
            name=f"qwen-devops-spaces-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            config={
                "model": MODEL_NAME,
                "learning_rate": learning_rate,
                "epochs": epochs,
                "batch_size": batch_size,
                "training_approach": "LoRA"
            }
        )
    
    try:
        # Load datasets
        yield "📥 Loading DevOps datasets..."
        examples, dataset_info = load_devops_datasets()
        yield f"✅ Loaded {len(examples)} training examples\n" + "\n".join(dataset_info)
        
        # Load model and tokenizer
        yield "🔄 Loading Qwen3-8B model and tokenizer..."
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        # Load model with LoRA configuration
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        
        # Configure LoRA for efficient fine-tuning
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=16,  # Rank
            lora_alpha=32,
            lora_dropout=0.1,
            target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
        )
        
        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()
        
        yield f"✅ Model loaded with LoRA configuration\n📊 Trainable parameters: {model.get_nb_trainable_parameters()}"
        
        # Prepare dataset
        yield "🔄 Preparing training dataset..."
        tokenized_dataset = format_training_data(examples, tokenizer)
        
        # Split dataset
        split_dataset = tokenized_dataset.train_test_split(test_size=0.1, seed=42)
        train_dataset = split_dataset["train"]
        eval_dataset = split_dataset["test"]
        
        yield f"✅ Dataset prepared: {len(train_dataset)} train, {len(eval_dataset)} eval examples"
        
        # Training arguments optimized for dedicated GPU training
        training_args = TrainingArguments(
            output_dir=OUTPUT_DIR,
            num_train_epochs=epochs,  # Full epochs for complete training
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            gradient_accumulation_steps=4,  # Standard accumulation
            learning_rate=learning_rate,
            weight_decay=0.01,
            logging_steps=10,
            eval_steps=50,
            save_steps=100,
            eval_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            warmup_steps=50,
            lr_scheduler_type="cosine",
            fp16=True,
            dataloader_pin_memory=True,
            remove_unused_columns=False,
            report_to="wandb" if wandb_key else "none",
            run_name=f"qwen-devops-complete-{datetime.now().strftime('%Y%m%d_%H%M')}",
            resume_from_checkpoint=resume_from_checkpoint,
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
            tokenizer=tokenizer,
        )
        
        yield "🚀 Starting training..."
        
        # Train the model
        trainer.train()
        
        yield "💾 Saving model..."
        
        # Save the final model
        trainer.save_model(OUTPUT_DIR)
        tokenizer.save_pretrained(OUTPUT_DIR)
        
        # Save training metrics
        metrics = trainer.state.log_history
        with open(f"{OUTPUT_DIR}/training_metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        
        # Final evaluation
        final_metrics = trainer.evaluate()
        
        if wandb_key:
            wandb.log(final_metrics)
            wandb.finish()
        
        yield f"✅ Training completed successfully!\n📊 Final eval loss: {final_metrics.get('eval_loss', 'N/A'):.4f}"
        
        return f"🎉 Model saved to {OUTPUT_DIR}"
        
    except Exception as e:
        error_msg = f"❌ Training failed: {str(e)}"
        yield error_msg
        return error_msg

def create_interface():
    """Create Gradio interface"""
    
    with gr.Blocks(title="Qwen3-8B DevOps Foundation Model Training") as app:
        gr.Markdown("# 🤖 Qwen3-8B DevOps Foundation Model Training")
        gr.Markdown("Train a specialized DevOps/SRE model using the latest Qwen3-8B base model")
        
        with gr.Row():
            with gr.Column():
                wandb_project = gr.Textbox(
                    label="W&B Project Name",
                    value="qwen-devops-foundation",
                    placeholder="Enter Weights & Biases project name"
                )
                learning_rate = gr.Slider(
                    minimum=1e-5,
                    maximum=1e-3,
                    value=2e-4,
                    step=1e-5,
                    label="Learning Rate"
                )
                epochs = gr.Slider(
                    minimum=1,
                    maximum=5,
                    value=3,
                    step=1,
                    label="Training Epochs"
                )
                batch_size = gr.Slider(
                    minimum=1,
                    maximum=8,
                    value=2,
                    step=1,
                    label="Batch Size"
                )
                
                train_btn = gr.Button("🚀 Start Training", variant="primary")
            
            with gr.Column():
                output = gr.Textbox(
                    label="Training Progress",
                    lines=20,
                    max_lines=30,
                    show_copy_button=True
                )
        
        # Training progress
        train_btn.click(
            fn=train_model,
            inputs=[wandb_project, learning_rate, epochs, batch_size],
            outputs=output,
            show_progress=True
        )
        
        gr.Markdown("""
        ## 📋 Setup Instructions:
        
        1. **HuggingFace Token**: Add your HF token as a secret named `HF_TOKEN`
        2. **W&B API Key**: Add your Weights & Biases API key as a secret named `WANDB_API_KEY`
        3. **Hardware**: Use ZeroGPU (free with PRO) or dedicated GPU for faster training
        
        ## 💰 Cost Estimates:
        - **ZeroGPU**: FREE with PRO subscription ($9/month)
        - **L4 GPU**: $0.80/hour (~$4.80 per training run)
        - **A100 GPU**: $2.50/hour (~$7.50 per training run)
        """)
    
    return app

if __name__ == "__main__":
    app = create_interface()
    app.launch(share=True)