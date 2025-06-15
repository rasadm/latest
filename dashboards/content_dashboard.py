#!/usr/bin/env python3
"""
Content Management Dashboard
Windows GUI for managing automated content creation and publishing
"""

import sys
import os
# Add the parent directory to Python path to find our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import json
import os
from datetime import datetime
import requests
from content.auto_content_system import AutoContentSystem

class ContentDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("AgenticAI Content Management Dashboard")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize content system
        self.content_system = AutoContentSystem()
        self.is_running = False
        self.publishing_thread = None
        
        # Create GUI elements
        self.create_widgets()
        self.load_stats()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', padx=0, pady=0)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🚀 AgenticAI Content Management Dashboard", 
                              font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(title_frame, text="Automated AI Marketing Content Creation & Publishing", 
                                 font=('Arial', 10), fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left panel - Controls
        left_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=1)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # Control buttons
        control_label = tk.Label(left_frame, text="📋 Content Controls", 
                                font=('Arial', 12, 'bold'), bg='white')
        control_label.pack(pady=10)
        
        # Custom topic input section
        custom_topic_label = tk.Label(left_frame, text="💡 Custom Topic (Optional)", 
                                     font=('Arial', 10, 'bold'), bg='white')
        custom_topic_label.pack(pady=(5, 0), padx=10)
        
        # Topic input field
        self.custom_topic_var = tk.StringVar()
        topic_entry = tk.Entry(left_frame, textvariable=self.custom_topic_var, 
                              width=30, font=('Arial', 9))
        topic_entry.pack(pady=(5, 0), padx=10)
        
        # Topic help text
        topic_help = tk.Label(left_frame, text="Leave empty for random topic", 
                             font=('Arial', 7), bg='white', fg='gray')
        topic_help.pack(pady=(0, 5), padx=10)
        
        # Create single post button
        self.create_post_btn = tk.Button(left_frame, text="✨ Create & Publish One Post", 
                                        command=self.create_single_post,
                                        bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                                        width=25, height=2)
        self.create_post_btn.pack(pady=5, padx=10)
        
        # Start continuous publishing button
        self.start_btn = tk.Button(left_frame, text="🤖 Start Auto Publishing", 
                                  command=self.start_continuous,
                                  bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
                                  width=25, height=2)
        self.start_btn.pack(pady=5, padx=10)
        
        # Stop continuous publishing button
        self.stop_btn = tk.Button(left_frame, text="⏹️ Stop Auto Publishing", 
                                 command=self.stop_continuous,
                                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                                 width=25, height=2, state='disabled')
        self.stop_btn.pack(pady=5, padx=10)
        
        # Settings section
        settings_label = tk.Label(left_frame, text="⚙️ Settings", 
                                 font=('Arial', 12, 'bold'), bg='white')
        settings_label.pack(pady=(20, 10))
        
        # Publishing interval
        interval_label = tk.Label(left_frame, text="Publishing Interval (minutes):", 
                                 font=('Arial', 9), bg='white')
        interval_label.pack(pady=(5, 0), padx=10)
        
        self.interval_var = tk.StringVar(value="5")
        interval_entry = tk.Entry(left_frame, textvariable=self.interval_var, width=10)
        interval_entry.pack(pady=(0, 5), padx=10)
        
        # Content generation method
        method_label = tk.Label(left_frame, text="Content Generation:", 
                               font=('Arial', 9), bg='white')
        method_label.pack(pady=(10, 0), padx=10)
        
        self.generation_method = tk.StringVar(value="template")
        method_frame = tk.Frame(left_frame, bg='white')
        method_frame.pack(pady=(0, 5), padx=10)
        
        template_radio = tk.Radiobutton(method_frame, text="Template", 
                                       variable=self.generation_method, value="template",
                                       bg='white', font=('Arial', 7))
        template_radio.pack(side='left')
        
        llm_radio = tk.Radiobutton(method_frame, text="Local LLM", 
                                  variable=self.generation_method, value="local_llm",
                                  bg='white', font=('Arial', 7))
        llm_radio.pack(side='left')
        
        research_radio = tk.Radiobutton(method_frame, text="Research+LLM", 
                                       variable=self.generation_method, value="research_llm",
                                       bg='white', font=('Arial', 7))
        research_radio.pack(side='left')
        
        # LLM Model selection
        model_label = tk.Label(left_frame, text="DeepSeek Model:", 
                              font=('Arial', 9), bg='white')
        model_label.pack(pady=(5, 0), padx=10)
        
        self.llm_model = tk.StringVar(value="deepseek")
        model_combo = tk.ttk.Combobox(left_frame, textvariable=self.llm_model,
                                     values=["deepseek", "deepseek-32b", "deepseek-14b"],
                                     state="readonly", width=22)
        model_combo.pack(pady=(0, 5), padx=10)
        
        # Test LLM button
        test_llm_btn = tk.Button(left_frame, text="🧪 Test Local LLM", 
                                command=self.test_local_llm,
                                bg='#9b59b6', fg='white', font=('Arial', 9),
                                width=25)
        test_llm_btn.pack(pady=5, padx=10)
        
        # Website status
        status_label = tk.Label(left_frame, text="🌐 Website Status", 
                               font=('Arial', 12, 'bold'), bg='white')
        status_label.pack(pady=(20, 10))
        
        self.status_text = tk.Label(left_frame, text="Checking...", 
                                   font=('Arial', 9), bg='white', fg='orange')
        self.status_text.pack(pady=5, padx=10)
        
        # Check status button
        check_btn = tk.Button(left_frame, text="🔄 Check Website Status", 
                             command=self.check_website_status,
                             bg='#f39c12', fg='white', font=('Arial', 9),
                             width=25)
        check_btn.pack(pady=5, padx=10)
        
        # Right panel - Logs and Stats
        right_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=1)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Stats section
        stats_label = tk.Label(right_frame, text="📊 Publishing Statistics", 
                              font=('Arial', 12, 'bold'), bg='white')
        stats_label.pack(pady=10)
        
        # Stats frame
        stats_frame = tk.Frame(right_frame, bg='white')
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        # Stats labels
        self.total_posts_label = tk.Label(stats_frame, text="Total Posts: 0", 
                                         font=('Arial', 10), bg='white')
        self.total_posts_label.pack(side='left', padx=10)
        
        self.today_posts_label = tk.Label(stats_frame, text="Today: 0", 
                                         font=('Arial', 10), bg='white')
        self.today_posts_label.pack(side='left', padx=10)
        
        self.last_post_label = tk.Label(stats_frame, text="Last Post: Never", 
                                       font=('Arial', 10), bg='white')
        self.last_post_label.pack(side='left', padx=10)
        
        # Activity log
        log_label = tk.Label(right_frame, text="📝 Activity Log", 
                            font=('Arial', 12, 'bold'), bg='white')
        log_label.pack(pady=(20, 10))
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(right_frame, height=20, width=60,
                                                 font=('Consolas', 9))
        self.log_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Status bar
        status_frame = tk.Frame(self.root, bg='#34495e', height=30)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.status_bar = tk.Label(status_frame, text="Ready", 
                                  font=('Arial', 9), fg='white', bg='#34495e')
        self.status_bar.pack(side='left', padx=10, pady=5)
        
        # Initialize with welcome message
        self.log_message("🚀 Content Management Dashboard Started")
        self.log_message("📁 Content Directory: serie 1/")
        
        # Load site URL from environment or config
        site_url = os.getenv("WP_SITE_URL") or "https://agenticaiupdates.space"
        self.log_message(f"🌐 Target Website: {site_url}")
        
        # Test connection to WordPress
        try:
            response = requests.get(site_url, timeout=10)
            if response.status_code == 200:
                self.log_message("✅ WordPress site is accessible")
            else:
                self.log_message(f"⚠️ WordPress site returned status: {response.status_code}")
        except Exception as e:
            self.log_message(f"❌ Cannot reach WordPress site: {e}")
        
        # Test WordPress API
        try:
            api_url = f"{site_url}/wp-json/wp/v2"
            response = requests.get(api_url, timeout=10)
        except Exception as e:
            self.log_message(f"❌ Cannot reach WordPress API: {e}")
        
        # Check website status on startup
        self.check_website_status()
    
    def log_message(self, message):
        """Add message to activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update()
    
    def update_status_bar(self, message):
        """Update status bar message"""
        self.status_bar.config(text=message)
        self.root.update()
    
    def test_local_llm(self):
        """Test local LLM connection"""
        try:
            selected_model = self.llm_model.get()
            self.log_message(f"🧪 Testing {selected_model} connection...")
            
            if self.content_system.local_llm.test_connection(selected_model):
                model_name = self.content_system.local_llm.providers[selected_model]["model"]
                self.log_message(f"✅ {selected_model} ({model_name}): Connected and ready!")
                self.log_message(f"💰 Cost per post: $0.00 (Local Generation)")
            else:
                self.log_message(f"❌ {selected_model}: Not available")
                self.log_message("💡 Make sure Ollama is running: ollama serve")
                
        except Exception as e:
            self.log_message(f"❌ Error testing local LLM: {e}")
    
    def create_single_post(self):
        """Create and publish a single post"""
        custom_topic = self.custom_topic_var.get().strip()
        
        if custom_topic:
            self.log_message(f"🎯 Creating blog post with custom topic: {custom_topic}")
        else:
            self.log_message("🎯 Creating blog post with random topic...")
        
        self.update_status_bar("Creating content...")
        self.create_post_btn.config(state='disabled')
        
        def create_post_thread():
            try:
                # Set generation method
                if self.generation_method.get() == "research_llm":
                    selected_model = self.llm_model.get()
                    if self.content_system.enable_research_llm(selected_model):
                        model_name = self.content_system.enhanced_research.local_llm.providers[selected_model]["model"]
                        self.log_message(f"🌐🤖 Using Research+{model_name} for content generation...")
                    else:
                        self.log_message("❌ Research LLM not available, using template generation")
                        self.content_system.disable_research_llm()
                elif self.generation_method.get() == "local_llm":
                    selected_model = self.llm_model.get()
                    if self.content_system.enable_local_llm(selected_model):
                        model_name = self.content_system.local_llm.providers[selected_model]["model"]
                        self.log_message(f"🤖 Using {model_name} for content generation...")
                    else:
                        self.log_message("❌ Local LLM not available, using template generation")
                        self.content_system.disable_local_llm()
                else:
                    self.content_system.disable_local_llm()
                    self.content_system.disable_research_llm()
                    self.log_message("📝 Using template-based content generation...")
                
                # Create post with custom topic if provided
                if custom_topic:
                    success = self.content_system.create_and_publish_custom_post(custom_topic)
                else:
                    success = self.content_system.create_and_publish_post()
                
                if success:
                    self.log_message("✅ Post created and published successfully!")
                    self.update_status_bar("Post published successfully")
                    self.load_stats()
                    # Clear custom topic after successful creation
                    self.custom_topic_var.set("")
                else:
                    self.log_message("❌ Failed to create/publish post")
                    self.update_status_bar("Failed to publish post")
            except Exception as e:
                self.log_message(f"❌ Error: {str(e)}")
                self.update_status_bar("Error occurred")
            finally:
                self.create_post_btn.config(state='normal')
        
        thread = threading.Thread(target=create_post_thread)
        thread.daemon = True
        thread.start()
    
    def start_continuous(self):
        """Start continuous publishing"""
        if self.is_running:
            return
        
        self.is_running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        interval_minutes = float(self.interval_var.get())
        self.log_message(f"🤖 Starting continuous publishing (every {interval_minutes} minutes)")
        self.update_status_bar("Auto publishing active")
        
        def publishing_loop():
            while self.is_running:
                try:
                    # Set generation method
                    if self.generation_method.get() == "research_llm":
                        selected_model = self.llm_model.get()
                        if self.content_system.enable_research_llm(selected_model):
                            model_name = self.content_system.enhanced_research.local_llm.providers[selected_model]["model"]
                            self.log_message(f"🌐🤖 Auto-creating with Research+{model_name}...")
                        else:
                            self.log_message("❌ Research LLM not available, using template generation")
                            self.content_system.disable_research_llm()
                    elif self.generation_method.get() == "local_llm":
                        selected_model = self.llm_model.get()
                        if self.content_system.enable_local_llm(selected_model):
                            model_name = self.content_system.local_llm.providers[selected_model]["model"]
                            self.log_message(f"🤖 Auto-creating with {model_name}...")
                        else:
                            self.log_message("❌ Local LLM not available, using template generation")
                            self.content_system.disable_local_llm()
                    else:
                        self.content_system.disable_local_llm()
                        self.content_system.disable_research_llm()
                        self.log_message("📝 Auto-creating with template generation...")
                    
                    # Create and publish post
                    self.log_message("🚀 Auto-creating new blog post...")
                    success = self.content_system.create_and_publish_post()
                    
                    if success:
                        self.log_message("✅ Auto-post published successfully!")
                        self.load_stats()
                    else:
                        self.log_message("❌ Auto-post failed")
                    
                    # Wait for next interval
                    if self.is_running:
                        wait_seconds = interval_minutes * 60
                        self.log_message(f"⏰ Next post in {interval_minutes} minutes...")
                        
                        # Wait in small increments to allow stopping
                        for i in range(int(wait_seconds)):
                            if not self.is_running:
                                break
                            time.sleep(1)
                
                except Exception as e:
                    self.log_message(f"❌ Auto-publishing error: {str(e)}")
                    time.sleep(60)  # Wait 1 minute before retrying
        
        self.publishing_thread = threading.Thread(target=publishing_loop)
        self.publishing_thread.daemon = True
        self.publishing_thread.start()
    
    def stop_continuous(self):
        """Stop continuous publishing"""
        self.is_running = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        self.log_message("⏹️ Stopping continuous publishing...")
        self.update_status_bar("Auto publishing stopped")
    
    def check_website_status(self):
        """Check if website is accessible"""
        def check_status_thread():
            try:
                response = requests.get("https://agenticaiupdates.space", timeout=10)
                if response.status_code == 200:
                    self.status_text.config(text="✅ Website Online", fg='green')
                    self.log_message("🌐 Website status: Online")
                else:
                    self.status_text.config(text="⚠️ Website Issues", fg='orange')
                    self.log_message(f"🌐 Website status: HTTP {response.status_code}")
            except Exception as e:
                self.status_text.config(text="❌ Website Offline", fg='red')
                self.log_message(f"🌐 Website status: Offline ({str(e)})")
        
        thread = threading.Thread(target=check_status_thread)
        thread.daemon = True
        thread.start()
    
    def load_stats(self):
        """Load and display publishing statistics"""
        try:
            # Count total posts in serie 1 directory
            content_dir = "serie 1"
            if os.path.exists(content_dir):
                md_files = [f for f in os.listdir(content_dir) if f.endswith('.md')]
                total_posts = len(md_files)
                
                # Count today's posts
                today = datetime.now().strftime("%Y-%m-%d")
                today_posts = len([f for f in md_files if today in f])
                
                # Find last post
                if md_files:
                    md_files.sort(key=lambda x: os.path.getmtime(os.path.join(content_dir, x)), reverse=True)
                    last_post_time = os.path.getmtime(os.path.join(content_dir, md_files[0]))
                    last_post = datetime.fromtimestamp(last_post_time).strftime("%Y-%m-%d %H:%M")
                else:
                    last_post = "Never"
                
                # Update labels
                self.total_posts_label.config(text=f"Total Posts: {total_posts}")
                self.today_posts_label.config(text=f"Today: {today_posts}")
                self.last_post_label.config(text=f"Last Post: {last_post}")
                
        except Exception as e:
            self.log_message(f"⚠️ Error loading stats: {str(e)}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.is_running:
            if messagebox.askokcancel("Quit", "Auto publishing is running. Stop and quit?"):
                self.stop_continuous()
                time.sleep(1)  # Give time to stop
                self.root.destroy()
        else:
            self.root.destroy()

def main():
    """Main function to run the dashboard"""
    root = tk.Tk()
    
    # Set window icon (if available)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = ContentDashboard(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    main() 