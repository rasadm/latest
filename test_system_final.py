#!/usr/bin/env python3
"""
Final System Test for AI Content Management System v0.1.1
Tests all critical components after Claude Sonnet 4 upgrade
"""

import sys
import os
import json
from pathlib import Path

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing imports...")
    try:
        from core.project_manager import MultilingualProjectManager, ContentProject
        from core.enhanced_research_llm import EnhancedResearchLLM
        from content.claude_content import ClaudeContentGenerator
        from content.auto_content_system import AutoContentSystem
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_settings_file():
    """Test settings file exists and is valid"""
    print("🔍 Testing settings file...")
    settings_path = Path("config/settings.json")
    if not settings_path.exists():
        print("❌ Settings file not found")
        return False
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        # Check for required sections
        required_sections = ['anthropic', 'wordpress_websites', 'supported_languages']
        for section in required_sections:
            if section not in settings:
                print(f"❌ Missing section: {section}")
                return False
        
        # Check Claude model
        if settings.get('anthropic', {}).get('model') == 'claude-sonnet-4-20250514':
            print("✅ Claude Sonnet 4 model configured correctly")
        else:
            print(f"⚠️ Model: {settings.get('anthropic', {}).get('model')}")
        
        print("✅ Settings file valid")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Settings file JSON error: {e}")
        return False

def test_projects_file():
    """Test projects.json file"""
    print("🔍 Testing projects file...")
    projects_path = Path("projects.json")
    if not projects_path.exists():
        print("❌ Projects file not found")
        return False
    
    try:
        with open(projects_path, 'r', encoding='utf-8') as f:
            projects = json.load(f)
        
        # Check if projects use Claude Sonnet 4
        sonnet4_count = 0
        for project_id, project in projects.items():
            if project.get('llm_model') == 'claude-sonnet-4-20250514':
                sonnet4_count += 1
        
        print(f"✅ {sonnet4_count}/{len(projects)} projects using Claude Sonnet 4")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Projects file JSON error: {e}")
        return False

def test_directory_structure():
    """Test directory structure"""
    print("🔍 Testing directory structure...")
    required_dirs = ['core', 'content', 'dashboards', 'config', 'projects']
    missing_dirs = []
    
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ Directory structure complete")
    return True

def test_environment_setup():
    """Test environment setup"""
    print("🔍 Testing environment setup...")
    
    # Check for .env.example
    if Path(".env.example").exists():
        print("✅ .env.example file exists")
    else:
        print("⚠️ .env.example file missing")
    
    # Check for .gitignore
    if Path(".gitignore").exists():
        print("✅ .gitignore file exists")
    else:
        print("⚠️ .gitignore file missing")
    
    return True

def main():
    """Run all tests"""
    print("🚀 AI Content Management System v0.1.1 - Final System Test")
    print("=" * 60)
    
    tests = [
        test_directory_structure,
        test_imports,
        test_settings_file,
        test_projects_file,
        test_environment_setup
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for production.")
        print("\n📋 Next Steps:")
        print("1. Copy .env.example to .env and add your API keys")
        print("2. Run: ./start_app.bat")
        print("3. Visit GitHub to create pull request:")
        print("   https://github.com/rasadm/latest/pull/new/v0.1.1-release")
        return True
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 