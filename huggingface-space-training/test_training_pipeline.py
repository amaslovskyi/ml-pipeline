#!/usr/bin/env python3
"""
Test Training Pipeline for GPT-OSS DevOps Training
Uses a small model to verify repository creation and upload process
"""

import os
import json
from datetime import datetime

# Fix for HuggingFace CAS/XET infrastructure issues
os.environ["HF_HUB_DISABLE_XET"] = "1"

import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, TaskType
from huggingface_hub import create_repo

# Test configuration - using small model
TEST_MODEL_NAME = "microsoft/DialoGPT-small"  # Small 117M parameter model
TEST_OUTPUT_DIR = "./test-devops-model"


def create_test_dataset():
    """Create a small test dataset for quick training"""
    print("📝 Creating test dataset...")

    test_examples = [
        {
            "instruction": "What is Docker?",
            "input": "",
            "output": "Docker is a containerization platform that allows developers to package applications and their dependencies into lightweight, portable containers that can run consistently across different environments.",
        },
        {
            "instruction": "How do you check running containers?",
            "input": "",
            "output": "Use the command 'docker ps' to see currently running containers, or 'docker ps -a' to see all containers including stopped ones.",
        },
        {
            "instruction": "What is Kubernetes?",
            "input": "",
            "output": "Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications across clusters of machines.",
        },
        {
            "instruction": "How do you scale a deployment in Kubernetes?",
            "input": "",
            "output": "Use 'kubectl scale deployment <deployment-name> --replicas=<number>' to scale a deployment to the desired number of replicas.",
        },
        {
            "instruction": "What is Infrastructure as Code?",
            "input": "",
            "output": "Infrastructure as Code (IaC) is the practice of managing and provisioning computing infrastructure through machine-readable definition files, rather than manual configuration. Tools like Terraform and Ansible are commonly used for IaC.",
        },
    ]

    return test_examples


def format_test_data(examples, tokenizer, max_length=512):
    """Format test data for training"""
    print("🔄 Formatting test data...")

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

        # Create labels for causal LM
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
        desc="Tokenizing test dataset",
    )

    print(f"✅ Test dataset prepared: {len(tokenized_dataset)} examples")
    return tokenized_dataset


def test_training_pipeline():
    """Test the complete training and upload pipeline"""
    print("🧪 Starting test training pipeline...")

    try:
        # 1. Create test dataset
        examples = create_test_dataset()

        # 2. Load small model and tokenizer
        print("📥 Loading test model and tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(TEST_MODEL_NAME)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            TEST_MODEL_NAME,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else "cpu",
        )

        # 3. Add LoRA for testing
        print("🔧 Adding LoRA configuration...")
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            inference_mode=False,
            r=8,  # Small rank for testing
            lora_alpha=16,
            lora_dropout=0.1,
            target_modules=["c_attn", "c_proj"],  # DialoGPT architecture
        )

        model = get_peft_model(model, lora_config)
        model.print_trainable_parameters()

        # 4. Prepare dataset
        tokenized_dataset = format_test_data(examples, tokenizer)

        # 5. Minimal training configuration
        training_args = TrainingArguments(
            output_dir=TEST_OUTPUT_DIR,
            num_train_epochs=1,  # Just 1 epoch for testing
            per_device_train_batch_size=1,
            gradient_accumulation_steps=2,
            learning_rate=5e-4,
            logging_steps=1,
            save_steps=5,
            save_strategy="steps",
            remove_unused_columns=True,
            dataloader_drop_last=False,
        )

        # 6. Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
        )

        # 7. Initialize trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
            processing_class=tokenizer,
        )

        # 8. Run quick training
        print("🚀 Starting test training (1 epoch)...")
        trainer.train()

        # 9. Save model locally
        print("💾 Saving test model...")
        trainer.save_model(TEST_OUTPUT_DIR)
        tokenizer.save_pretrained(TEST_OUTPUT_DIR)

        # 10. Test repository creation and upload
        print("🧪 Testing repository creation and upload...")
        test_upload_to_hub()

        print("✅ Test pipeline completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Test pipeline failed: {str(e)}")
        return False


def validate_hf_token():
    """Validate HuggingFace token permissions"""
    from huggingface_hub import HfApi, whoami

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("❌ No HF_TOKEN found")
        print("💡 Get token from: https://huggingface.co/settings/tokens")
        return False, None

    try:
        # Test token validity
        api = HfApi()
        user_info = whoami(token=hf_token)
        username = user_info["name"]

        print(f"✅ Token valid for user: {username}")

        # Check if token has write permissions by trying to list user repos
        try:
            list(api.list_models(author=username, limit=1, token=hf_token))
            print("✅ Token has read permissions")
            return True, username
        except Exception as e:
            print(f"⚠️ Token permission check failed: {str(e)}")
            print("💡 Make sure your token has 'Write' permissions")
            print("🔗 Update at: https://huggingface.co/settings/tokens")
            return False, username

    except Exception as e:
        print(f"❌ Token validation failed: {str(e)}")
        print("💡 Check token validity at: https://huggingface.co/settings/tokens")
        return False, None


def test_upload_to_hub():
    """Test the upload to HuggingFace Hub process"""
    print("📤 Testing upload to HuggingFace Hub...")

    # Validate token first
    token_valid, username = validate_hf_token()
    if not token_valid:
        return False

    hf_token = os.environ.get("HF_TOKEN")

    try:
        # Test repository creation using validated username
        test_repo_name = (
            f"{username}/test-devops-model-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )

        print(f"🏗️ Creating test repository: {test_repo_name}")
        create_repo(
            repo_id=test_repo_name, repo_type="model", exist_ok=True, token=hf_token
        )
        print("✅ Repository created successfully!")

        # Load and upload model
        print("📥 Loading trained model for upload...")
        tokenizer = AutoTokenizer.from_pretrained(TEST_OUTPUT_DIR)
        model = AutoModelForCausalLM.from_pretrained(
            TEST_OUTPUT_DIR, torch_dtype=torch.float16, device_map="cpu"
        )

        print("📤 Uploading model...")
        model.push_to_hub(
            test_repo_name,
            use_temp_dir=True,
            commit_message=f"Test DevOps model upload - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            token=hf_token,
        )

        print("📤 Uploading tokenizer...")
        tokenizer.push_to_hub(
            test_repo_name,
            use_temp_dir=True,
            commit_message=f"Test tokenizer upload - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            token=hf_token,
        )

        print(
            f"🎉 Upload successful! Model available at: https://huggingface.co/{test_repo_name}"
        )

        # Save test results
        test_results = {
            "test_completed": True,
            "timestamp": datetime.now().isoformat(),
            "model_name": TEST_MODEL_NAME,
            "repository": test_repo_name,
            "upload_successful": True,
        }

        with open("test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)

        return True

    except Exception as e:
        print(f"❌ Upload test failed: {str(e)}")

        # Save failure results
        test_results = {
            "test_completed": True,
            "timestamp": datetime.now().isoformat(),
            "model_name": TEST_MODEL_NAME,
            "upload_successful": False,
            "error": str(e),
        }

        with open("test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)

        return False


def cleanup_test_files():
    """Clean up test files after testing"""
    import shutil

    print("🧹 Cleaning up test files...")
    try:
        if os.path.exists(TEST_OUTPUT_DIR):
            shutil.rmtree(TEST_OUTPUT_DIR)
            print("✅ Test model directory cleaned up")

        if os.path.exists("test_results.json"):
            os.remove("test_results.json")
            print("✅ Test results file cleaned up")

    except Exception as e:
        print(f"⚠️ Cleanup warning: {str(e)}")


if __name__ == "__main__":
    print("🧪 GPT-OSS DevOps Training Pipeline Test")
    print("=" * 50)

    # Run the test
    success = test_training_pipeline()

    if success:
        print("\n✅ ALL TESTS PASSED!")
        print("🚀 Ready to run full GPT-OSS:20B training")

        # Ask about cleanup
        cleanup_choice = input("\n🧹 Clean up test files? (y/n): ").lower().strip()
        if cleanup_choice == "y":
            cleanup_test_files()
    else:
        print("\n❌ TESTS FAILED!")
        print("🔧 Please fix issues before running full training")

    print("\n🏁 Test completed!")
