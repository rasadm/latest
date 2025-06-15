#!/usr/bin/env python3
"""
Test and Fix Claude API Connection
"""

import sys
import os
# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from content.claude_content import ClaudeContentGenerator
from core.settings_manager import SettingsManager

def test_claude_connection():
    """Test Claude API connection and fix issues"""
    
    print("🔍 Testing Claude API Connection...")
    print("=" * 50)
    
    # 1. Load settings and API key
    print("1. Loading settings...")
    settings_manager = SettingsManager()
    
    # Check if API key is in settings
    claude_key = settings_manager.settings.get("claude_api_key")
    if claude_key:
        print(f"✅ Found Claude API key in settings: {claude_key[:10]}...")
        os.environ["ANTHROPIC_API_KEY"] = claude_key
    else:
        print("❌ No Claude API key found in settings")
        return False
    
    # 2. Initialize Claude generator
    print("\n2. Initializing Claude generator...")
    claude = ClaudeContentGenerator()
    
    print(f"   Model: {claude.model}")
    print(f"   API Key: {'✅ Set' if claude.api_key else '❌ Missing'}")
    
    # 3. Test connection
    print("\n3. Testing API connection...")
    if claude.test_connection():
        print("✅ Claude API connection successful!")
        
        # 4. Test content generation
        print("\n4. Testing content generation...")
        try:
            test_content = claude.generate_content_with_claude(
                topic="AI Marketing Test",
                keyword="test keyword"
            )
            
            if test_content:
                print("✅ Content generation successful!")
                print(f"   Generated {len(test_content)} characters")
                print(f"   Preview: {test_content[:100]}...")
                return True
            else:
                print("❌ Content generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Content generation error: {e}")
            return False
    else:
        print("❌ Claude API connection failed")
        
        # Try to diagnose the issue
        print("\n🔧 Diagnosing issues...")
        
        # Check API key format
        if claude.api_key:
            if claude.api_key.startswith("sk-ant-"):
                print("✅ API key format looks correct")
            else:
                print("❌ API key format looks incorrect (should start with 'sk-ant-')")
        
        # Check model name
        print(f"   Current model: {claude.model}")
        print(f"   Available models: {list(claude.available_models.keys())}")
        
        return False

def fix_claude_issues():
    """Fix common Claude API issues"""
    
    print("\n🔧 Fixing Claude API Issues...")
    print("=" * 50)
    
    # Load settings
    settings_manager = SettingsManager()
    
    # Fix model names in projects
    print("1. Checking project model names...")
    
    try:
        with open("projects.json", "r", encoding="utf-8") as f:
            projects_data = json.load(f)
        
        fixed_count = 0
        for project_id, project in projects_data.items():
            if project.get("llm_model", "").startswith("claude-"):
                old_model = project["llm_model"]
                # Fix to use correct model name
                if "4-sonnet" in old_model or "sonnet-4" in old_model:
                    project["llm_model"] = "claude-3.5-sonnet"
                    print(f"   ✅ Fixed {project['name']}: {old_model} → claude-3.5-sonnet")
                    fixed_count += 1
                elif "3.7-sonnet" in old_model:
                    project["llm_model"] = "claude-3.5-sonnet"
                    print(f"   ✅ Fixed {project['name']}: {old_model} → claude-3.5-sonnet")
                    fixed_count += 1
        
        if fixed_count > 0:
            # Save fixed projects
            with open("projects.json", "w", encoding="utf-8") as f:
                json.dump(projects_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Fixed {fixed_count} project model names")
        else:
            print("✅ No model names needed fixing")
            
    except Exception as e:
        print(f"❌ Error fixing projects: {e}")
    
    # Test again
    print("\n2. Testing connection after fixes...")
    return test_claude_connection()

def main():
    """Main function"""
    print("🤖 Claude API Test & Fix Tool")
    print("=" * 50)
    
    # First test
    if test_claude_connection():
        print("\n🎉 All tests passed! Claude API is working correctly.")
    else:
        print("\n🔧 Issues found. Attempting to fix...")
        if fix_claude_issues():
            print("\n🎉 Issues fixed! Claude API is now working.")
        else:
            print("\n❌ Could not fix all issues. Manual intervention needed.")
            print("\n💡 Troubleshooting steps:")
            print("1. Check your Claude API key at: https://console.anthropic.com/")
            print("2. Ensure you have billing set up")
            print("3. Verify your internet connection")
            print("4. Check if the API key is correctly set in config/settings.json")

if __name__ == "__main__":
    main() 