#!/usr/bin/env python3
"""
Fix system issues with model names and timeouts
"""

from core.project_manager import MultilingualProjectManager
from content.claude_content import ClaudeContentGenerator
import json
import os

def fix_system_issues():
    """Fix common system issues preventing project execution"""
    
    print("🔧 System Issues Diagnostic & Fix")
    print("=" * 50)
    
    # Initialize components
    pm = MultilingualProjectManager()
    claude_gen = ClaudeContentGenerator()
    
    # 1. Check available models
    print("📋 Available Claude Models:")
    for key, value in claude_gen.available_models.items():
        print(f"   ✅ {key} → {value}")
    
    # 2. Check projects with incorrect model names
    print(f"\n🔍 Checking projects for model issues...")
    
    issues_found = []
    for project_id, project in pm.projects.items():
        if project.llm_model not in claude_gen.available_models.values():
            if project.llm_model not in claude_gen.available_models.keys():
                issues_found.append({
                    'project_id': project_id,
                    'project_name': project.name,
                    'current_model': project.llm_model,
                    'language': project.language
                })
    
    if issues_found:
        print(f"\n❌ Found {len(issues_found)} projects with model issues:")
        for issue in issues_found:
            print(f"   Project: {issue['project_name']} ({issue['language']})")
            print(f"   Current Model: {issue['current_model']}")
            print(f"   Project ID: {issue['project_id']}")
        
        # Fix the model names
        print(f"\n🔧 Fixing model names...")
        for issue in issues_found:
            project = pm.projects[issue['project_id']]
            # Use the most stable model
            project.llm_model = "claude-3.5-sonnet"
            print(f"   ✅ Fixed {issue['project_name']} → claude-3.5-sonnet")
        
        # Save the fixes
        pm.save_projects()
        print(f"✅ All model names fixed and saved!")
    else:
        print("✅ No model issues found")
    
    # 3. Test Claude connection with correct model
    print(f"\n🔗 Testing Claude API connection...")
    claude_gen.set_model("claude-3.5-sonnet")
    
    if claude_gen.test_connection():
        print("✅ Claude API connection successful")
    else:
        print("❌ Claude API connection failed")
        print("💡 Suggestions:")
        print("   1. Check ANTHROPIC_API_KEY environment variable")
        print("   2. Verify API key is valid")
        print("   3. Check internet connection")
    
    # 4. Show current projects status
    print(f"\n📊 Current Projects Status:")
    for project_id, project in pm.projects.items():
        status_icon = "✅" if project.status == "active" else "⏸️" if project.status == "paused" else "🔴"
        print(f"   {status_icon} {project.name} ({project.language})")
        print(f"      Progress: {project.completed_count}/{project.target_count}")
        print(f"      Model: {project.llm_model}")
        print(f"      Status: {project.status}")
        print()
    
    return issues_found

def create_test_project():
    """Create a test project to verify system is working"""
    
    print("🧪 Creating Test Project")
    print("-" * 30)
    
    pm = MultilingualProjectManager()
    
    # Create a simple English test project
    project_id = pm.create_project(
        name="System Test Project",
        description="Simple test to verify system is working",
        keywords=["AI technology", "system test"],
        target_count=1,
        content_type="claude",
        language="english",
        llm_model="claude-3.5-sonnet",
        target_audience="Tech professionals",
        content_length="short"
    )
    
    print(f"✅ Test project created: {project_id}")
    
    # Try to generate one piece of content
    print("🤖 Testing content generation...")
    success = pm.generate_content_for_project(project_id, "AI technology test")
    
    if success:
        print("✅ System test PASSED - Content generation working!")
        
        # Clean up test project
        pm.remove_project(project_id)
        print("🧹 Test project cleaned up")
        
        return True
    else:
        print("❌ System test FAILED - Content generation not working")
        return False

if __name__ == "__main__":
    # Fix system issues
    issues = fix_system_issues()
    
    # Run system test if no major issues
    if len(issues) == 0:
        print("\n" + "="*50)
        test_passed = create_test_project()
        
        if test_passed:
            print("\n🎉 System is ready for project creation!")
        else:
            print("\n⚠️ System needs further troubleshooting")
    else:
        print(f"\n⚠️ Fixed {len(issues)} issues. Please restart and test again.") 