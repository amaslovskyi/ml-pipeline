#!/usr/bin/env python3
"""
Test the enhanced DevOps dataset preparation script
"""

import os
import sys

# Set up environment
os.environ['HUGGINGFACE_HUB_TOKEN'] = 'test_token'

# Import our script
sys.path.append('.')
from scripts.prepare_enhanced_devops_dataset import DevOpsDatasetBuilder

def test_dataset_creation():
    """Test dataset creation without actual HF token."""
    print("🧪 Testing enhanced DevOps dataset creation...")
    
    # Create builder (will skip HF login with invalid token)
    builder = DevOpsDatasetBuilder()
    
    # Test synthetic examples creation
    synthetic = builder.create_synthetic_devops_examples()
    print(f"✅ Created {len(synthetic)} synthetic examples")
    
    # Test troubleshooting scenarios
    troubleshooting = builder.create_troubleshooting_scenarios()
    print(f"✅ Created {len(troubleshooting)} troubleshooting scenarios")
    
    # Test formatting
    formatted = builder.format_for_qwen3_training(synthetic[:2])
    print(f"✅ Formatted {len(formatted)} examples for Qwen3")
    
    # Show sample
    print("\n📋 Sample formatted example:")
    print("=" * 50)
    print(formatted[0]['text'])
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    test_dataset_creation()
    print("✅ Enhanced dataset test completed successfully!")