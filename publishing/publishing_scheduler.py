#!/usr/bin/env python3
"""
Publishing Scheduler
Automatically publishes content from the queue at scheduled times
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import schedule

from core.project_manager import MultilingualProjectManager
from publishing.wordpress_publisher import WordPressPublisher
from core.settings_manager import SettingsManager

class PublishingScheduler:
    def __init__(self):
        self.project_manager = MultilingualProjectManager()
        self.settings_manager = SettingsManager()
        self.wordpress_publisher = None  # Initialize later when needed
        self.is_running = False
        self.scheduler_thread = None
        
        print("📅 Publishing Scheduler initialized")
    
    def start_scheduler(self):
        """Start the publishing scheduler"""
        if self.is_running:
            print("⚠️ Scheduler is already running")
            return
        
        self.is_running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        print("🚀 Publishing scheduler started")
    
    def stop_scheduler(self):
        """Stop the publishing scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        print("⏹️ Publishing scheduler stopped")
    
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                self.check_and_publish_due_content()
                time.sleep(60)  # Check every minute
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                time.sleep(60)
    
    def check_and_publish_due_content(self):
        """Check for content that's due for publishing and publish it"""
        queue = self.project_manager.get_publishing_queue()
        current_time = datetime.now()
        
        for item in queue:
            if item['status'] == 'queued' and item['scheduled_time'] <= current_time:
                self.publish_content_item(item)
    
    def publish_content_item(self, queue_item: Dict):
        """Publish a single content item from the queue"""
        try:
            project_id = queue_item['project_id']
            content_index = queue_item['content_index']
            
            print(f"📤 Publishing content {content_index} for project {project_id}")
            
            # Get project details
            project = self.project_manager.get_project(project_id)
            if not project:
                print(f"❌ Project {project_id} not found")
                self.project_manager.update_queue_item_status(project_id, content_index, 'error')
                return
            
            # Find the content file to publish
            content_file = self.find_content_file(project, content_index)
            if not content_file:
                print(f"❌ Content file not found for project {project_id}, content {content_index}")
                self.project_manager.update_queue_item_status(project_id, content_index, 'error')
                return
            
            # Get WordPress website details
            website = self.project_manager.get_website_by_id(project.website_id)
            if not website:
                print(f"❌ WordPress website not found for project {project_id}")
                self.project_manager.update_queue_item_status(project_id, content_index, 'error')
                return
            
            # Initialize WordPress publisher if needed
            if not self.wordpress_publisher:
                from publishing.wordpress_publisher import WordPressPublisher
                self.wordpress_publisher = WordPressPublisher(
                    site_url=website.url,
                    username=website.username,
                    password=website.password
                )
            
            # Publish to WordPress
            success = self.wordpress_publisher.publish_markdown_file(content_file, status='draft')
            
            if success:
                print(f"✅ Successfully published content {content_index} for project {project.name}")
                self.project_manager.update_queue_item_status(project_id, content_index, 'published')
            else:
                print(f"❌ Failed to publish content {content_index} for project {project.name}")
                self.project_manager.update_queue_item_status(project_id, content_index, 'failed')
                
        except Exception as e:
            print(f"❌ Error publishing content: {e}")
            self.project_manager.update_queue_item_status(
                queue_item['project_id'], 
                queue_item['content_index'], 
                'error'
            )
    
    def find_content_file(self, project, content_index: int) -> Optional[str]:
        """Find the content file for a specific project and content index"""
        try:
            project_dir = Path(project.output_directory)
            if not project_dir.exists():
                return None
            
            # Look for markdown files in the project directory
            md_files = list(project_dir.glob("*.md"))
            
            # Sort by creation time to match the content index
            md_files.sort(key=lambda x: x.stat().st_ctime)
            
            if content_index < len(md_files):
                return str(md_files[content_index])
            
            return None
            
        except Exception as e:
            print(f"❌ Error finding content file: {e}")
            return None
    
    def get_queue_status(self) -> Dict:
        """Get current queue status"""
        queue = self.project_manager.get_publishing_queue()
        
        status = {
            'total_items': len(queue),
            'queued': 0,
            'published': 0,
            'failed': 0,
            'error': 0,
            'next_publish_time': None
        }
        
        current_time = datetime.now()
        next_times = []
        
        for item in queue:
            status[item['status']] += 1
            
            if item['status'] == 'queued' and item['scheduled_time'] > current_time:
                next_times.append(item['scheduled_time'])
        
        if next_times:
            status['next_publish_time'] = min(next_times)
        
        return status
    
    def reschedule_failed_content(self, project_id: str, content_index: int, delay_minutes: int = 30):
        """Reschedule failed content for later publishing"""
        queue = self.project_manager.get_publishing_queue()
        
        for item in queue:
            if (item['project_id'] == project_id and 
                item['content_index'] == content_index and 
                item['status'] in ['failed', 'error']):
                
                # Reschedule for later
                new_time = datetime.now() + timedelta(minutes=delay_minutes)
                item['scheduled_time'] = new_time
                item['status'] = 'queued'
                
                # Save updated queue
                self.project_manager.save_publishing_queue([])  # This will reload and save
                print(f"🔄 Rescheduled content {content_index} for {new_time.strftime('%Y-%m-%d %H:%M:%S')}")
                break
    
    def clear_completed_items(self):
        """Remove published items from the queue"""
        queue = self.project_manager.get_publishing_queue()
        
        # Keep only non-published items
        active_queue = [item for item in queue if item['status'] != 'published']
        
        # Save cleaned queue
        queue_file = "publishing_queue.json"
        try:
            # Convert datetime objects to strings for JSON
            queue_for_json = []
            for item in active_queue:
                item_copy = item.copy()
                if isinstance(item_copy['scheduled_time'], datetime):
                    item_copy['scheduled_time'] = item_copy['scheduled_time'].isoformat()
                queue_for_json.append(item_copy)
            
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(queue_for_json, f, indent=2, ensure_ascii=False)
            
            removed_count = len(queue) - len(active_queue)
            print(f"🧹 Removed {removed_count} completed items from queue")
            
        except Exception as e:
            print(f"❌ Error cleaning queue: {e}")

def main():
    """Main function for testing the scheduler"""
    scheduler = PublishingScheduler()
    
    print("🚀 Starting publishing scheduler...")
    scheduler.start_scheduler()
    
    try:
        # Keep the scheduler running
        while True:
            status = scheduler.get_queue_status()
            print(f"📊 Queue Status: {status['queued']} queued, {status['published']} published, {status['failed']} failed")
            
            if status['next_publish_time']:
                print(f"⏰ Next publish: {status['next_publish_time'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            time.sleep(300)  # Print status every 5 minutes
            
    except KeyboardInterrupt:
        print("\n⏹️ Stopping scheduler...")
        scheduler.stop_scheduler()

if __name__ == "__main__":
    main() 