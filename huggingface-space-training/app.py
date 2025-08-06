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
    
    # Always start with synthetic examples as a reliable base
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
        },
        {
            "instruction": "What are the key considerations for designing a fault-tolerant distributed system?",
            "input": "",
            "output": "Key fault-tolerant distributed system considerations: 1) Implement circuit breakers for external dependencies, 2) Use redundancy across multiple availability zones, 3) Design for graceful degradation, 4) Implement proper retry logic with exponential backoff, 5) Use health checks and automatic failover, 6) Ensure data consistency with appropriate patterns (eventual consistency, ACID), 7) Monitor system health and performance metrics, 8) Plan for disaster recovery scenarios."
        },
        {
            "instruction": "How do you optimize Docker container security?",
            "input": "",
            "output": "Docker container security optimization: 1) Use minimal base images (alpine, distroless), 2) Run containers as non-root user, 3) Implement multi-stage builds to reduce attack surface, 4) Scan images for vulnerabilities using tools like Trivy, 5) Use secrets management instead of environment variables, 6) Configure security contexts and pod security policies, 7) Enable runtime security monitoring, 8) Regularly update base images and dependencies."
        }
    ]
    all_examples.extend(synthetic_examples)
    datasets_info.append(f"✅ Synthetic examples: {len(synthetic_examples)} examples")
    
    # Load VERIFIED external DevOps datasets from HuggingFace Hub (YOUR RECOMMENDED APPROACH!)
    print("Loading VERIFIED external datasets - YOUR RECOMMENDED METHOD!")
    
    # 1. CoSQA - 20,000+ Web Queries for Code Search and Question Answering (VERIFIED!)
    try:
        print("Loading gonglinyuan/CoSQA dataset (20k+ web queries)...")
        dataset = load_dataset("gonglinyuan/CoSQA", split="train")
        examples = []
        
        # Debug: Print first item to see actual field names
        print(f"CoSQA sample fields: {list(dataset[0].keys())}")
        
        for item in dataset.select(range(min(500, len(dataset)))):  # Reduced for Space memory
            # CoSQA actual field names (from CodeXGLUE format)
            query = item.get('nl', item.get('query', item.get('question', '')))
            code = item.get('code', item.get('text', ''))
            url = item.get('url', '')
            
            if query and code:
                # Create instruction-response format for code Q&A
                instruction = f"Explain what this code does:\n```\n{code}\n```"
                output = f"This code answers the query: {query}"
                
                examples.append({
                    "instruction": instruction,
                    "input": "",
                    "output": output
                })
                
            elif query:  # If we have query without code, make it a Q&A
                examples.append({
                    "instruction": query,
                    "input": "",
                    "output": f"This is a software engineering question related to: {query}"
                })
                
        all_examples.extend(examples)
        datasets_info.append(f"✅ CoSQA Web Queries: {len(examples)} examples (20k+ total)")
        print(f"Successfully loaded {len(examples)} examples from CoSQA - PREMIUM DATASET!")
    except Exception as e:
        datasets_info.append(f"⚠️ CoSQA failed: {str(e)}")
        print(f"CoSQA dataset error: {str(e)}")
    
    # 2. StackExchange DevOps - YOUR RECOMMENDED DATASET (VERIFIED!)
    try:
        print("Loading mlfoundations-dev/stackexchange_devops dataset...")
        dataset = load_dataset("mlfoundations-dev/stackexchange_devops", split="train")
        examples = []
        for item in dataset.select(range(min(800, len(dataset)))):
            # StackExchange format
            question = item.get('question', item.get('title', ''))
            answer = item.get('answer', item.get('body', ''))
            tags = item.get('tags', '')
            
            if question and answer:
                # Add tags context if available
                full_question = f"[Tags: {tags}] {question}" if tags else question
                examples.append({
                    "instruction": full_question,
                    "input": "",
                    "output": answer
                })
        all_examples.extend(examples)
        datasets_info.append(f"✅ StackExchange DevOps: {len(examples)} examples")
        print(f"Successfully loaded {len(examples)} examples from StackExchange DevOps - YOUR RECOMMENDATION!")
    except Exception as e:
        datasets_info.append(f"⚠️ StackExchange DevOps failed: {str(e)}")
        print(f"StackExchange DevOps dataset error: {str(e)}")
        
    # 3. Kubernetes StackOverflow Questions (VERIFIED!)
    try:
        print("Loading mcipriano/stackoverflow-kubernetes-questions dataset...")
        dataset = load_dataset("mcipriano/stackoverflow-kubernetes-questions", split="train")
        examples = []
        for item in dataset.select(range(min(600, len(dataset)))):
            # Adapt format from StackOverflow
            question = item.get('title', item.get('question', ''))
            body = item.get('body', '')
            answer = item.get('accepted_answer_body', item.get('answer', ''))
            
            if question and answer:
                # Combine question and body for instruction
                full_question = f"{question}\n{body}".strip() if body else question
                examples.append({
                    "instruction": full_question,
                    "input": "",
                    "output": answer
                })
        all_examples.extend(examples)
        datasets_info.append(f"✅ Kubernetes StackOverflow: {len(examples)} examples")
        print(f"Successfully loaded {len(examples)} examples from Kubernetes StackOverflow")
    except Exception as e:
        datasets_info.append(f"⚠️ Kubernetes StackOverflow failed: {str(e)}")
        print(f"Kubernetes StackOverflow dataset error: {str(e)}")
        
    # 4. Docker Commands - Natural Language to Docker (VERIFIED!)
    try:
        print("Loading MattCoddity/dockerNLcommands dataset...")
        dataset = load_dataset("MattCoddity/dockerNLcommands", split="train")
        examples = []
        for item in dataset:
            instruction = item.get('instruction', item.get('natural_language', ''))
            command = item.get('docker_command', item.get('command', ''))
            
            if instruction and command:
                examples.append({
                    "instruction": f"Translate this requirement to a Docker command: {instruction}",
                    "input": "",
                    "output": f"Docker command: {command}"
                })
        all_examples.extend(examples)
        datasets_info.append(f"✅ Docker Commands: {len(examples)} examples")
        print(f"Successfully loaded {len(examples)} examples from Docker Commands")
    except Exception as e:
        datasets_info.append(f"⚠️ Docker Commands failed: {str(e)}")
        print(f"Docker Commands dataset error: {str(e)}")
        
    # 5. Python StackOverflow - Programming Q&A (VERIFIED!)
    try:
        print("Loading koutch/stackoverflow_python dataset...")
        dataset = load_dataset("koutch/stackoverflow_python", split="train")
        examples = []
        # Filter for DevOps/infrastructure related Python questions
        devops_keywords = ['deployment', 'docker', 'kubernetes', 'ci/cd', 'automation', 'infrastructure', 'monitoring', 'logging']
        
        for item in dataset.select(range(min(1000, len(dataset)))):
            question_title = item.get('question_title', '')
            question_body = item.get('question_body', '')
            answer = item.get('answer', '')
            
            # Check if question is DevOps-related
            text_to_check = f"{question_title} {question_body}".lower()
            is_devops_related = any(keyword in text_to_check for keyword in devops_keywords)
            
            if question_title and answer and (is_devops_related or len(examples) < 400):
                # Combine title and body for instruction
                full_question = f"{question_title}\n{question_body}".strip() if question_body else question_title
                examples.append({
                    "instruction": full_question,
                    "input": "",
                    "output": answer
                })
                
                if len(examples) >= 500:  # Limit total examples
                    break
        
        all_examples.extend(examples)
        datasets_info.append(f"✅ Python StackOverflow: {len(examples)} examples")
        print(f"Successfully loaded {len(examples)} examples from Python StackOverflow")
    except Exception as e:
        datasets_info.append(f"⚠️ Python StackOverflow failed: {str(e)}")
        print(f"Python StackOverflow dataset error: {str(e)}")
    
    # 6. Incident Response Playbooks - SRE focused
    try:
        print("Loading agamage/incident-response-playbook-samples dataset...")
        dataset = load_dataset("agamage/incident-response-playbook-samples", split="train")
        examples = []
        for item in dataset:
            playbook = item.get('playbook', item.get('content', ''))
            title = item.get('title', item.get('name', ''))
            description = item.get('description', '')
            
            if playbook and title:
                instruction = f"Create an incident response playbook for: {title}"
                if description:
                    instruction = f"{instruction}\nDescription: {description}"
                examples.append({
                    "instruction": instruction,
                    "input": "",
                    "output": playbook
                })
        all_examples.extend(examples)
        datasets_info.append(f"✅ Incident Response Playbooks: {len(examples)} SRE examples")
        print(f"Successfully loaded {len(examples)} SRE incident response examples")
    except Exception as e:
        datasets_info.append(f"⚠️ Incident Response Playbooks failed: {str(e)}")
        print(f"Incident Response Playbooks dataset error: {str(e)}")
        
    # 7. General Incident Dataset - Q&A format  
    try:
        print("Loading atishayj281/incident-dataset dataset...")
        dataset = load_dataset("atishayj281/incident-dataset", split="train")
        examples = []
        for item in dataset:
            question = item.get('question', item.get('incident_description', ''))
            answer = item.get('answer', item.get('resolution', item.get('response', '')))
            
            if question and answer:
                examples.append({
                    "instruction": f"How to handle this incident: {question}",
                    "input": "",
                    "output": answer
                })
        all_examples.extend(examples)
        datasets_info.append(f"✅ Incident Management: {len(examples)} examples")
        print(f"Successfully loaded {len(examples)} incident management examples")
    except Exception as e:
        datasets_info.append(f"⚠️ Incident Management failed: {str(e)}")
        print(f"Incident Management dataset error: {str(e)}")
        
    # Add fallback synthetic examples if no external datasets loaded
    if len(all_examples) < 20:
        fallback_examples = [
            {
                "instruction": "How do you implement blue-green deployment in Kubernetes?",
                "input": "",
                "output": "Blue-green deployment in Kubernetes: 1) Create two identical environments (blue and green) using different selectors, 2) Deploy new version to inactive environment (green), 3) Test thoroughly with readiness/liveness probes, 4) Switch traffic by updating service selector labels, 5) Monitor metrics and logs post-switch, 6) Rollback by reverting service selector if issues occur, 7) Use tools like Argo Rollouts or Flagger for automation."
            },
            {
                "instruction": "Explain Prometheus monitoring setup for microservices",
                "input": "",
                "output": "Prometheus microservices monitoring: 1) Install Prometheus server via Helm chart, 2) Configure service discovery for automatic target detection, 3) Expose metrics endpoints (/metrics) in each microservice, 4) Set up alerting rules for SLA violations, 5) Configure Grafana dashboards for visualization, 6) Implement distributed tracing with Jaeger, 7) Monitor golden signals: latency, traffic, errors, saturation, 8) Use PushGateway for batch jobs, 9) Set up federation for multi-cluster monitoring."
            }
        ]
        all_examples.extend(fallback_examples)
        datasets_info.append(f"✅ Fallback synthetic examples: {len(fallback_examples)} examples")
    
    return all_examples, datasets_info

def format_training_data(examples, tokenizer, max_length=2048):
    """Format data for instruction following training"""
    # Validate and clean examples
    valid_examples = []
    for i, item in enumerate(examples):
        if (isinstance(item, dict) and 
            'instruction' in item and 'output' in item and
            isinstance(item['instruction'], str) and isinstance(item['output'], str) and
            item['instruction'].strip() and item['output'].strip()):
            valid_examples.append(item)
        else:
            print(f"⚠️ Skipping invalid example {i}: {type(item)} - {list(item.keys()) if isinstance(item, dict) else 'Not a dict'}")
    
    print(f"✅ Valid examples after cleaning: {len(valid_examples)} / {len(examples)}")
    
    formatted_data = []
    
    for item in valid_examples:
        # Create instruction-following format
        input_text = item.get('input', '').strip()
        if input_text:
            text = f"### Instruction:\n{item['instruction']}\n\n### Input:\n{input_text}\n\n### Response:\n{item['output']}"
        else:
            text = f"### Instruction:\n{item['instruction']}\n\n### Response:\n{item['output']}"
        
        formatted_data.append({"text": text})
    
    # Tokenize with proper padding and validation
    def tokenize_function(examples):
        # Ensure all texts are strings and not empty
        texts = []
        for text in examples["text"]:
            if isinstance(text, str) and text.strip():
                texts.append(text.strip())
            else:
                # Fallback for invalid text
                texts.append("### Instruction:\nWhat is DevOps?\n\n### Response:\nDevOps is a set of practices that combines software development and IT operations.")
        
        tokens = tokenizer(
            texts,
            truncation=True,
            padding="max_length",  # Ensure consistent tensor shapes
            max_length=max_length,
            return_overflowing_tokens=False,
            return_tensors=None,  # Return lists, not tensors yet
        )
        
        # Create labels - copy input_ids for causal LM
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
        desc="Tokenizing dataset"
    )
    
    # Validate tokenized dataset
    print(f"📊 Tokenized dataset size: {len(tokenized_dataset)}")
    if len(tokenized_dataset) > 0:
        sample = tokenized_dataset[0]
        print(f"📏 Sample input_ids length: {len(sample['input_ids'])}")
        print(f"📏 Sample labels length: {len(sample['labels'])}")
        print(f"🔢 Input IDs type: {type(sample['input_ids'])}")
        print(f"🔢 Labels type: {type(sample['labels'])}")
    
    return tokenized_dataset

@spaces.GPU(duration=180)  # Request 3 hours for A100 training (much faster than L4)
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
        
        # Load model with aggressive memory optimization for HuggingFace Spaces
        import gc
        import os
        
        # A100 has 80GB VRAM - no aggressive memory optimization needed
        print("🚀 Using A100 GPU with 80GB VRAM - optimized for performance!")
        
        # Load model with LoRA configuration - A100 optimized
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
            gradient_accumulation_steps=2,  # Reduced for A100's larger batches
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
        
        # Data collator with proper padding
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
            pad_to_multiple_of=8,  # Optimize for GPU efficiency
        )
        
        # Initialize trainer (use processing_class for future compatibility)
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
            processing_class=tokenizer,  # Use processing_class instead of tokenizer
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
                    value=4,
                    step=1,
                    label="Batch Size (A100 optimized)"
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