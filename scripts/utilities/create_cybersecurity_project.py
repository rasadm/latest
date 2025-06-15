#!/usr/bin/env python3
"""
Create a cyber security project for UCLan graduates
"""

from core.project_manager import MultilingualProjectManager

def create_cybersecurity_project():
    """Create a cyber security focused project"""
    
    print("🔒 Creating Cyber Security Project for UCLan Graduates")
    print("=" * 60)
    
    pm = MultilingualProjectManager()
    
    # Create a cyber security project
    project_id = pm.create_project(
        name="Cyber Security for UCLan Graduates",
        description="Professional cyber security content for Computer Engineering MSc graduates from UCLan UK specializing in cyber security management",
        keywords=[
            "cyber security management",
            "cybersecurity for engineers", 
            "information security",
            "UCLan cyber security",
            "cyber security careers",
            "security management"
        ],
        target_count=3,
        content_type="claude",
        language="english",
        llm_model="claude-3.5-sonnet",
        target_audience="Computer Engineer MSc Cyber Security Management graduates from UCLan UK",
        content_length="medium",
        seo_focus=[
            "cyber security management",
            "UCLan graduates",
            "cyber security careers",
            "information security"
        ]
    )
    
    print(f"✅ Project created with ID: {project_id}")
    
    # Get the project to show details
    project = pm.get_project(project_id)
    
    print(f"\n📋 Project Details:")
    print(f"   Name: {project.name}")
    print(f"   Language: {project.language}")
    print(f"   Target Audience: {project.target_audience}")
    print(f"   Keywords: {project.keywords}")
    print(f"   SEO Focus: {project.seo_focus}")
    print(f"   Target Count: {project.target_count}")
    print(f"   Model: {project.llm_model}")
    
    print(f"\n🎯 Ready to generate content about:")
    for i, keyword in enumerate(project.keywords, 1):
        print(f"   {i}. {keyword}")
    
    # Test generation of first content
    print(f"\n🤖 Would you like to generate the first piece of content?")
    print(f"   Topic: {project.keywords[0]}")
    
    # You can uncomment the following lines to auto-generate:
    # print(f"\n🚀 Generating first content piece...")
    # success = pm.generate_content_for_project(project_id, project.keywords[0])
    # if success:
    #     print(f"✅ Content generated successfully!")
    # else:
    #     print(f"❌ Content generation failed")
    
    return project_id

def show_usage_instructions():
    """Show how to use the project"""
    
    print(f"\n📖 Usage Instructions:")
    print(f"1. Open the project dashboard: python project_dashboard.py")
    print(f"2. Find your 'Cyber Security for UCLan Graduates' project")
    print(f"3. Click 'Start Project' to generate all content")
    print(f"4. Or generate individual content pieces manually")
    
    print(f"\n💡 Your content will focus on:")
    print(f"   • Cyber security management strategies")
    print(f"   • Career guidance for UCLan graduates")
    print(f"   • Industry best practices")
    print(f"   • Technical security topics")
    print(f"   • Professional development in cybersecurity")

if __name__ == "__main__":
    project_id = create_cybersecurity_project()
    show_usage_instructions()
    
    print(f"\n🎉 Your cyber security project is ready!")
    print(f"   Project ID: {project_id}")
    print(f"   Use the project dashboard to start content generation.") 