#!/usr/bin/env python3
"""
Local Test Script for GPT-OSS DevOps Training Pipeline
Run this locally to validate the pipeline before HuggingFace Space deployment
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        "torch",
        "transformers",
        "datasets", 
        "peft",
        "huggingface_hub"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment():
    """Check environment configuration"""
    print("🔍 Checking environment...")
    
    # Check HF_TOKEN
    hf_token = os.environ.get('HF_TOKEN')
    if hf_token:
        print("✅ HF_TOKEN found")
    else:
        print("❌ HF_TOKEN not found")
        print("💡 Set HF_TOKEN environment variable:")
        print("   export HF_TOKEN=your_token_here")
        return False
    
    # Check Python version
    if sys.version_info >= (3, 8):
        print(f"✅ Python {sys.version.split()[0]}")
    else:
        print(f"❌ Python {sys.version.split()[0]} (requires 3.8+)")
        return False
    
    return True

def run_test():
    """Run the test pipeline"""
    print("\n🚀 Running test pipeline...")
    
    try:
        # Import and run test
        from test_training_pipeline import test_training_pipeline
        
        success = test_training_pipeline()
        
        if success:
            print("\n🎉 TEST PIPELINE SUCCESSFUL!")
            print("✅ Ready for HuggingFace Space deployment")
            return True
        else:
            print("\n❌ TEST PIPELINE FAILED!")
            print("🔧 Fix issues before deploying to HuggingFace Space")
            return False
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        return False

def main():
    """Main function"""
    print("🧪 GPT-OSS DevOps Training Pipeline - Local Test")
    print("=" * 60)
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first")
        return
    
    # Check environment
    if not check_environment():
        print("\n❌ Please configure environment first")
        return
    
    print("\n✅ All checks passed!")
    
    # Ask user if they want to proceed
    proceed = input("\n🚀 Run test pipeline? (y/n): ").lower().strip()
    if proceed != 'y':
        print("👋 Test cancelled")
        return
    
    # Run test
    success = run_test()
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Deploy test_app.py to HuggingFace Space")
        print("2. Run test in Space environment") 
        print("3. If successful, deploy main app.py")
        print("4. Run full GPT-OSS:20B training")
    else:
        print("\n🔧 Fix Issues:")
        print("1. Check error messages above")
        print("2. Verify HF_TOKEN has write permissions")
        print("3. Ensure stable internet connection")
        print("4. Try running test again")

if __name__ == "__main__":
    main()
