#!/usr/bin/env python3
"""
System Organization Maintenance Script

This script helps maintain the organized directory structure and ensures
all components are properly organized according to the system architecture.
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional

class SystemOrganizer:
    """
    Maintains the organized directory structure of the AI content management system
    """
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.structure = {
            "core": {
                "description": "Core system components",
                "files": [
                    "enhanced_research_llm.py",
                    "project_manager.py", 
                    "settings_manager.py",
                    "web_research_content.py",
                    "local_llm_content.py"
                ]
            },
            "dashboards": {
                "description": "User interface applications",
                "files": [
                    "project_dashboard.py",
                    "content_dashboard.py",
                    "settings_dashboard.py"
                ]
            },
            "content": {
                "description": "Content generation and management",
                "files": [
                    "claude_content.py",
                    "auto_content_system.py",
                    "add_images.py",
                    "update_existing_post.py"
                ]
            },
            "publishing": {
                "description": "Publishing and scheduling",
                "files": [
                    "wordpress_publisher.py",
                    "publishing_scheduler.py",
                    "auto_publisher.py",
                    "publishing_queue.json"
                ]
            },
            "seo": {
                "description": "SEO optimization tools",
                "files": [
                    "seo_optimizer.py",
                    "seo_analyzer.py",
                    "seo_comprehensive_report.md"
                ]
            },
            "config": {
                "description": "Configuration files",
                "files": [
                    "config_example.yaml",
                    "settings.json",
                    ".wp_config.json",
                    "requirements.txt"
                ]
            },
            "docs": {
                "description": "Documentation",
                "files": [
                    "README.md",
                    "SYSTEM_ORGANIZATION.md",
                    "PROJECT_MANAGEMENT_GUIDE.md",
                    "MULTILINGUAL_SYSTEM_GUIDE.md",
                    "PUBLISHING_QUEUE_GUIDE.md",
                    "PROJECT_SYSTEM_GUIDE.md",
                    "PERSIAN_FONT_SETUP.md",
                    "WORDPRESS_SETUP.md",
                    "UNSPLASH_SETUP.md",
                    "README_enhanced_research_llm.md"
                ]
            },
            "scripts": {
                "description": "Utility and startup scripts",
                "subdirs": {
                    "startup": ["start_*.bat"],
                    "setup": ["setup_*.py", "setup_*.bat"],
                    "utilities": ["*.sh", "fix_*.py", "create_*.py"]
                }
            },
            "tests": {
                "description": "Test files",
                "files": ["test_*.py"]
            },
            "logs": {
                "description": "System logs",
                "files": ["*.log"]
            }
        }
    
    def check_organization(self) -> Dict[str, List[str]]:
        """
        Check current organization status
        
        Returns:
            Dictionary with organized and misplaced files
        """
        organized = []
        misplaced = []
        
        for directory, info in self.structure.items():
            dir_path = self.base_path / directory
            
            if dir_path.exists():
                organized.append(f"✅ {directory}/ - {info['description']}")
                
                if 'files' in info:
                    for file_pattern in info['files']:
                        matching_files = list(dir_path.glob(file_pattern))
                        if matching_files:
                            organized.extend([f"  ✅ {f.name}" for f in matching_files])
                        else:
                            # Check if file exists in root
                            root_files = list(self.base_path.glob(file_pattern))
                            if root_files:
                                misplaced.extend([f"❌ {f.name} should be in {directory}/" for f in root_files])
            else:
                misplaced.append(f"❌ Missing directory: {directory}/")
        
        return {"organized": organized, "misplaced": misplaced}
    
    def auto_organize(self, dry_run: bool = True) -> List[str]:
        """
        Automatically organize files into correct directories
        
        Args:
            dry_run: If True, only show what would be moved
            
        Returns:
            List of actions taken or planned
        """
        actions = []
        
        for directory, info in self.structure.items():
            target_dir = self.base_path / directory
            
            # Create directory if it doesn't exist
            if not target_dir.exists():
                action = f"CREATE: {directory}/"
                actions.append(action)
                if not dry_run:
                    target_dir.mkdir(parents=True, exist_ok=True)
            
            # Move files to correct location
            if 'files' in info:
                for file_pattern in info['files']:
                    # Find files in root that match pattern
                    root_files = list(self.base_path.glob(file_pattern))
                    for file_path in root_files:
                        if file_path.parent == self.base_path:  # Only move from root
                            target_path = target_dir / file_path.name
                            action = f"MOVE: {file_path.name} → {directory}/"
                            actions.append(action)
                            if not dry_run:
                                shutil.move(str(file_path), str(target_path))
        
        return actions
    
    def create_quick_access_script(self):
        """Create a quick access script for main functions"""
        script_content = """@echo off
echo ==========================================
echo AI Content Management System - Quick Access
echo ==========================================
echo.
echo 1. Start Project Dashboard
echo 2. Start Content Dashboard  
echo 3. Start Settings Dashboard
echo 4. Start Publishing Scheduler
echo 5. View System Organization
echo 6. Exit
echo.
set /p choice="Select option (1-6): "

if "%choice%"=="1" (
    echo Starting Project Dashboard...
    python dashboards/project_dashboard.py
) else if "%choice%"=="2" (
    echo Starting Content Dashboard...
    python dashboards/content_dashboard.py
) else if "%choice%"=="3" (
    echo Starting Settings Dashboard...
    python dashboards/settings_dashboard.py
) else if "%choice%"=="4" (
    echo Starting Publishing Scheduler...
    python publishing/publishing_scheduler.py
) else if "%choice%"=="5" (
    echo Checking System Organization...
    python organize_system.py --check
    pause
    goto start
) else if "%choice%"=="6" (
    echo Goodbye!
    exit
) else (
    echo Invalid choice. Please try again.
    pause
    goto start
)

:start
goto start
"""
        
        with open(self.base_path / "quick_start.bat", "w", encoding="utf-8") as f:
            f.write(script_content)
    
    def generate_report(self) -> str:
        """Generate organization status report"""
        status = self.check_organization()
        
        report = """
# System Organization Report

## ✅ Properly Organized Files
"""
        for item in status["organized"]:
            report += f"{item}\n"
        
        if status["misplaced"]:
            report += """
## ❌ Files Needing Organization
"""
            for item in status["misplaced"]:
                report += f"{item}\n"
        
        report += f"""
## 📊 Summary
- Total organized: {len(status['organized'])}
- Files needing organization: {len(status['misplaced'])}
- Organization status: {'✅ Complete' if not status['misplaced'] else '⚠️ Needs attention'}

## 🚀 Quick Commands
- Check organization: `python organize_system.py --check`
- Auto-organize (dry run): `python organize_system.py --organize --dry-run`
- Auto-organize (execute): `python organize_system.py --organize`
- Generate report: `python organize_system.py --report`
"""
        
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="System Organization Tool")
    parser.add_argument("--check", action="store_true", help="Check organization status")
    parser.add_argument("--organize", action="store_true", help="Auto-organize files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without executing")
    parser.add_argument("--report", action="store_true", help="Generate organization report")
    parser.add_argument("--quick-start", action="store_true", help="Create quick start script")
    
    args = parser.parse_args()
    
    organizer = SystemOrganizer()
    
    if args.check:
        print("🔍 Checking System Organization...")
        status = organizer.check_organization()
        
        print("\n✅ Properly Organized:")
        for item in status["organized"]:
            print(f"  {item}")
        
        if status["misplaced"]:
            print("\n❌ Needs Organization:")
            for item in status["misplaced"]:
                print(f"  {item}")
        else:
            print("\n🎉 All files are properly organized!")
    
    elif args.organize:
        print("🔧 Organizing System Files...")
        actions = organizer.auto_organize(dry_run=args.dry_run)
        
        if args.dry_run:
            print("\n📋 Actions that would be taken:")
        else:
            print("\n✅ Actions completed:")
        
        for action in actions:
            print(f"  {action}")
    
    elif args.report:
        print("📊 Generating Organization Report...")
        report = organizer.generate_report()
        
        with open("organization_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("✅ Report saved to organization_report.md")
        print(report)
    
    elif args.quick_start:
        print("🚀 Creating Quick Start Script...")
        organizer.create_quick_access_script()
        print("✅ Quick start script created: quick_start.bat")
    
    else:
        print("🏗️ AI Content Management System Organizer")
        print("Use --help to see available options")
        
        # Show current status
        status = organizer.check_organization()
        organized_count = len(status["organized"])
        misplaced_count = len(status["misplaced"])
        
        print(f"\n📊 Current Status:")
        print(f"  ✅ Organized: {organized_count}")
        print(f"  ❌ Misplaced: {misplaced_count}")
        
        if misplaced_count > 0:
            print(f"\n💡 Run 'python organize_system.py --organize' to fix organization")

if __name__ == "__main__":
    main() 