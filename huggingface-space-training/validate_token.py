#!/usr/bin/env python3
"""
HuggingFace Token Validation Script
Check if your token has the correct permissions for model uploads
"""

import os
from huggingface_hub import HfApi, whoami


def validate_token():
    """Validate HuggingFace token and permissions"""
    print("🔐 HuggingFace Token Validation")
    print("=" * 40)

    # Check if token exists
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("❌ No HF_TOKEN found in environment")
        print("\n💡 How to fix:")
        print("1. Go to: https://huggingface.co/settings/tokens")
        print("2. Create a new token with 'Write' permissions")
        print("3. Set environment variable:")
        print("   export HF_TOKEN=your_new_token_here")
        return False

    print(f"✅ HF_TOKEN found (length: {len(hf_token)} chars)")

    try:
        # Test token validity and get user info
        print("\n🔍 Validating token...")
        api = HfApi()
        user_info = whoami(token=hf_token)
        username = user_info["name"]

        print(f"✅ Token is valid")
        print(f"👤 Username: {username}")
        print(f"📧 Email: {user_info.get('email', 'N/A')}")

        # Check token permissions
        print("\n🔍 Checking permissions...")

        # Test if we can list user's repositories (read permission)
        try:
            repos = list(api.list_models(author=username, limit=1, token=hf_token))
            print("✅ Read permissions: OK")
        except Exception as e:
            print(f"❌ Read permissions: FAILED - {str(e)}")
            return False

        # Test if we can create a repository (write permission)
        # We'll use a test repo name that we can safely create/delete
        test_repo_name = f"{username}/hf-token-test-repo"

        try:
            print(f"🧪 Testing write permissions with: {test_repo_name}")

            # Try to create a test repository
            from huggingface_hub import create_repo, delete_repo

            create_repo(
                repo_id=test_repo_name, repo_type="model", exist_ok=True, token=hf_token
            )
            print("✅ Write permissions: OK (repository creation successful)")

            # Clean up test repository
            try:
                delete_repo(repo_id=test_repo_name, token=hf_token)
                print("🧹 Test repository cleaned up")
            except:
                print("⚠️ Test repository not cleaned up (may already exist)")

            return True

        except Exception as e:
            print(f"❌ Write permissions: FAILED - {str(e)}")

            if "403" in str(e) or "Forbidden" in str(e):
                print("\n💡 How to fix 403 Forbidden error:")
                print("1. Go to: https://huggingface.co/settings/tokens")
                print("2. Find your current token")
                print("3. Edit the token and change permissions to 'Write'")
                print("4. Or create a new token with 'Write' permissions")
                print("5. Update your environment variable")

            return False

    except Exception as e:
        print(f"❌ Token validation failed: {str(e)}")
        print("\n💡 Possible issues:")
        print("- Token is invalid or expired")
        print("- Network connectivity issues")
        print("- HuggingFace API is down")
        return False


def show_token_setup_guide():
    """Show detailed guide for setting up HuggingFace token"""
    print("\n📚 Complete Token Setup Guide")
    print("=" * 40)

    print("\n1. 🌐 Go to HuggingFace Settings:")
    print("   https://huggingface.co/settings/tokens")

    print("\n2. 🔧 Create/Edit Token:")
    print("   - Click 'New token' or edit existing")
    print("   - Name: 'DevOps Training Token'")
    print("   - Type: 'Write' (not just 'Read')")
    print("   - Repository types: 'All'")

    print("\n3. 💾 Copy Token:")
    print("   - Copy the generated token")
    print("   - Keep it secure!")

    print("\n4. 🔧 Set Environment Variable:")
    print("   # On macOS/Linux:")
    print("   export HF_TOKEN=hf_xxxxxxxxxxxxxxxx")
    print("   echo 'export HF_TOKEN=hf_xxxxxxxxxxxxxxxx' >> ~/.bashrc")
    print("   ")
    print("   # On Windows:")
    print("   set HF_TOKEN=hf_xxxxxxxxxxxxxxxx")

    print("\n5. ✅ Verify Setup:")
    print("   python validate_token.py")


if __name__ == "__main__":
    success = validate_token()

    if success:
        print("\n🎉 TOKEN VALIDATION SUCCESSFUL!")
        print("✅ Your token has all required permissions")
        print("🚀 Ready to run training pipeline")
    else:
        print("\n❌ TOKEN VALIDATION FAILED!")
        print("🔧 Please fix token permissions before proceeding")

        show_help = input("\n📚 Show detailed setup guide? (y/n): ").lower().strip()
        if show_help == "y":
            show_token_setup_guide()

    print("\n🏁 Validation completed!")
