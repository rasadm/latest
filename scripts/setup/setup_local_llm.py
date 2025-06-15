#!/usr/bin/env python3
"""
Local LLM Setup Script
Helps users install and configure Ollama with DeepSeek for local content generation
"""

import os
import sys
import subprocess
import requests
import time
from pathlib import Path

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        return response.status_code == 200
    except:
        return False

def start_ollama_service():
    """Start Ollama service"""
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen(['ollama', 'serve'], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Linux/Mac
            subprocess.Popen(['ollama', 'serve'])
        
        print("⏳ Starting Ollama service...")
        time.sleep(5)
        return check_ollama_running()
    except Exception as e:
        print(f"❌ Error starting Ollama: {e}")
        return False

def list_available_models():
    """List available models in Ollama"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=10)
        if response.status_code == 200:
            models = response.json().get('models', [])
            return [model['name'] for model in models]
        return []
    except:
        return []

def pull_model(model_name):
    """Pull a model using Ollama"""
    try:
        print(f"📥 Downloading {model_name}... (This may take several minutes)")
        result = subprocess.run(['ollama', 'pull', model_name], 
                              capture_output=True, text=True, timeout=1800)  # 30 min timeout
        
        if result.returncode == 0:
            print(f"✅ Successfully downloaded {model_name}")
            return True
        else:
            print(f"❌ Failed to download {model_name}: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout downloading {model_name}")
        return False
    except Exception as e:
        print(f"❌ Error downloading {model_name}: {e}")
        return False

def test_model(model_name):
    """Test a model with a simple prompt"""
    try:
        print(f"🧪 Testing {model_name}...")
        
        response = requests.post('http://localhost:11434/api/generate',
                               json={
                                   'model': model_name,
                                   'prompt': 'Write a brief introduction about AI marketing.',
                                   'stream': False
                               },
                               timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('response', '')
            if content and len(content) > 50:
                print(f"✅ {model_name} is working correctly!")
                print(f"📝 Sample output: {content[:100]}...")
                return True
            else:
                print(f"❌ {model_name} returned empty or short response")
                return False
        else:
            print(f"❌ {model_name} test failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing {model_name}: {e}")
        return False

def main():
    """Main setup function"""
    
    print("🚀 Local LLM Setup for Content Generation")
    print("=" * 50)
    
    # Step 1: Check Ollama installation
    print("\n1️⃣ Checking Ollama installation...")
    
    if not check_ollama_installed():
        print("❌ Ollama is not installed")
        print("\n📋 Installation Instructions:")
        print("1. Visit: https://ollama.ai")
        print("2. Download Ollama for your operating system")
        print("3. Install and restart this script")
        return False
    
    print("✅ Ollama is installed")
    
    # Step 2: Check if Ollama is running
    print("\n2️⃣ Checking Ollama service...")
    
    if not check_ollama_running():
        print("⚠️ Ollama service is not running")
        if start_ollama_service():
            print("✅ Ollama service started")
        else:
            print("❌ Failed to start Ollama service")
            print("💡 Try running 'ollama serve' manually in another terminal")
            return False
    else:
        print("✅ Ollama service is running")
    
    # Step 3: Check available models
    print("\n3️⃣ Checking available models...")
    
    available_models = list_available_models()
    print(f"📦 Currently installed models: {len(available_models)}")
    
    for model in available_models:
        print(f"  - {model}")
    
    # Step 4: Recommend and install models
    print("\n4️⃣ Recommended models for content generation:")
    
    recommended_models = [
        {
            "name": "deepseek-coder:6.7b",
            "description": "DeepSeek Coder - Excellent for structured content",
            "size": "~4GB"
        },
        {
            "name": "llama2:7b",
            "description": "Llama 2 - General purpose, reliable",
            "size": "~4GB"
        },
        {
            "name": "mistral:7b",
            "description": "Mistral - Fast and efficient",
            "size": "~4GB"
        }
    ]
    
    for i, model in enumerate(recommended_models, 1):
        status = "✅ Installed" if model["name"] in available_models else "❌ Not installed"
        print(f"{i}. {model['name']} - {model['description']} ({model['size']}) - {status}")
    
    # Step 5: Install missing models
    print("\n5️⃣ Model installation:")
    
    missing_models = [m for m in recommended_models if m["name"] not in available_models]
    
    if not missing_models:
        print("✅ All recommended models are already installed!")
    else:
        print(f"📥 {len(missing_models)} models need to be installed")
        
        install_choice = input("\nInstall missing models? (y/n): ").lower().strip()
        
        if install_choice == 'y':
            for model in missing_models:
                if pull_model(model["name"]):
                    available_models.append(model["name"])
        else:
            print("⏭️ Skipping model installation")
    
    # Step 6: Test models
    print("\n6️⃣ Testing installed models...")
    
    working_models = []
    for model_name in available_models:
        if test_model(model_name):
            working_models.append(model_name)
    
    # Step 7: Summary and next steps
    print("\n🎉 Setup Summary:")
    print(f"✅ Ollama installed and running")
    print(f"📦 {len(available_models)} models installed")
    print(f"🧪 {len(working_models)} models tested successfully")
    
    if working_models:
        print(f"\n🚀 Ready to use local LLM content generation!")
        print(f"💡 Recommended model: {working_models[0]}")
        print(f"\n📋 Next steps:")
        print(f"1. Run the content dashboard: python content_dashboard.py")
        print(f"2. Select 'Local LLM' as generation method")
        print(f"3. Click 'Test Local LLM' to verify connection")
        print(f"4. Start creating content with $0.00 cost!")
        
        # Test the local LLM content generator
        print(f"\n🧪 Testing local LLM content generator...")
        try:
            from core.local_llm_content import MultilingualLocalLLMContentGenerator
            
            generator = MultilingualLocalLLMContentGenerator()
            generator.set_provider("deepseek" if "deepseek-coder:6.7b" in working_models else "ollama")
            
            if generator.test_connection():
                print(f"✅ Local LLM content generator is ready!")
            else:
                print(f"⚠️ Local LLM content generator needs configuration")
                
        except ImportError:
            print(f"⚠️ local_llm_content.py not found in current directory")
        except Exception as e:
            print(f"⚠️ Error testing content generator: {e}")
    else:
        print(f"\n❌ No working models found")
        print(f"💡 Try installing models manually: ollama pull llama2:7b")
    
    return len(working_models) > 0

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🎊 Local LLM setup completed successfully!")
    else:
        print(f"\n❌ Setup incomplete. Please check the instructions above.")
    
    input(f"\nPress Enter to exit...") 