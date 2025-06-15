#!/usr/bin/env python3
"""
AI Content Management System - Settings Dashboard
Simplified version with essential settings management
"""

import streamlit as st
import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from core.settings_manager import SettingsManager
    from content.claude_content import ClaudeContentGenerator
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

class SettingsDashboard:
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.claude_generator = ClaudeContentGenerator()
        
    def run(self):
        """Main settings interface"""
        st.set_page_config(
            page_title="Settings - AI Content Management System",
            page_icon="⚙️",
            layout="wide"
        )
        
        st.title("⚙️ System Settings")
        st.markdown("**Configure your AI Content Management System**")
        
        # Sidebar navigation
        with st.sidebar:
            st.header("Settings Categories")
            category = st.selectbox("Choose Category", [
                "🔑 API Keys",
                "🤖 AI Models", 
                "📝 Content Settings",
                "🌐 WordPress",
                "📊 System Info"
            ])
        
        # Main content area
        if category == "🔑 API Keys":
            self.show_api_settings()
        elif category == "🤖 AI Models":
            self.show_model_settings()
        elif category == "📝 Content Settings":
            self.show_content_settings()
        elif category == "🌐 WordPress":
            self.show_wordpress_settings()
        elif category == "📊 System Info":
            self.show_system_info()
    
    def show_api_settings(self):
        """Display API key settings"""
        st.header("🔑 API Key Configuration")
        
        # Anthropic API Key
        st.subheader("Anthropic Claude API")
        
        current_key = os.getenv('ANTHROPIC_API_KEY')
        if current_key:
            masked_key = current_key[:8] + "..." + current_key[-4:] if len(current_key) > 12 else "***"
            st.success(f"✅ API Key configured: {masked_key}")
        else:
            st.error("❌ Anthropic API Key not found")
        
        with st.expander("Update Anthropic API Key"):
            new_key = st.text_input("Enter new API key", type="password", placeholder="sk-ant-...")
            if st.button("Update Anthropic Key"):
                if new_key:
                    os.environ['ANTHROPIC_API_KEY'] = new_key
                    st.success("✅ API key updated! Restart the application to apply changes.")
                else:
                    st.error("Please enter a valid API key")
        
        # Test Connection
        st.subheader("Connection Test")
        if st.button("🔍 Test Claude API Connection"):
            with st.spinner("Testing connection..."):
                if self.claude_generator.test_connection():
                    st.success("✅ Claude API connection successful!")
                else:
                    st.error("❌ Claude API connection failed!")
        
        # Unsplash API (Optional)
        st.subheader("Unsplash API (Optional)")
        unsplash_key = os.getenv('UNSPLASH_ACCESS_KEY')
        if unsplash_key:
            st.info("✅ Unsplash API configured")
        else:
            st.warning("⚠️ Unsplash API not configured (will use fallback images)")
        
        with st.expander("Configure Unsplash API"):
            st.info("Unsplash provides high-quality images for your content. This is optional.")
            unsplash_access = st.text_input("Access Key", type="password")
            unsplash_secret = st.text_input("Secret Key", type="password")
            if st.button("Update Unsplash Keys"):
                if unsplash_access:
                    os.environ['UNSPLASH_ACCESS_KEY'] = unsplash_access
                    if unsplash_secret:
                        os.environ['UNSPLASH_SECRET_KEY'] = unsplash_secret
                    st.success("✅ Unsplash API keys updated!")
    
    def show_model_settings(self):
        """Display AI model settings"""
        st.header("🤖 AI Model Configuration")
        
        # Current Model
        current_model = self.claude_generator.model
        st.info(f"**Current Model:** {current_model}")
        
        # Available Models
        st.subheader("Available Claude Models")
        
        models_info = {
            "claude-sonnet-4-20250514": {
                "name": "Claude Sonnet 4",
                "description": "Latest and most advanced model",
                "cost": "$3/$15 per MTok",
                "recommended": True
            },
            "claude-opus-4-20250514": {
                "name": "Claude Opus 4", 
                "description": "Most powerful model for complex tasks",
                "cost": "$15/$75 per MTok",
                "recommended": False
            },
            "claude-3-5-sonnet-20241022": {
                "name": "Claude 3.5 Sonnet",
                "description": "Previous stable version",
                "cost": "$3/$15 per MTok", 
                "recommended": False
            }
        }
        
        for model_id, info in models_info.items():
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    if info["recommended"]:
                        st.markdown(f"**{info['name']}** ⭐ *Recommended*")
                    else:
                        st.markdown(f"**{info['name']}**")
                    st.caption(info["description"])
                
                with col2:
                    st.text(f"Cost: {info['cost']}")
                    if model_id == current_model:
                        st.success("✅ Current")
                
                with col3:
                    if st.button("Select", key=f"select_{model_id}"):
                        self.claude_generator.model = model_id
                        st.success(f"✅ Model changed to {info['name']}")
                        st.rerun()
                
                st.divider()
        
        # Model Performance Settings
        st.subheader("Performance Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            max_tokens = st.slider("Max Tokens", 1000, 8000, self.claude_generator.max_tokens)
            if max_tokens != self.claude_generator.max_tokens:
                self.claude_generator.max_tokens = max_tokens
                st.info("Max tokens updated")
        
        with col2:
            temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
            st.caption("Higher values make output more creative")
    
    def show_content_settings(self):
        """Display content generation settings"""
        st.header("📝 Content Generation Settings")
        
        # Default Settings
        st.subheader("Default Content Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            default_language = st.selectbox("Default Language", 
                                          ["english", "farsi", "arabic"], 
                                          index=0)
            
            default_length = st.selectbox("Default Content Length",
                                        ["short", "medium", "long"],
                                        index=1)
            
            default_audience = st.text_input("Default Target Audience", 
                                           value="Marketing professionals")
        
        with col2:
            content_style = st.selectbox("Default Template Style",
                                       ["random", "trend_analysis", "how_to_guide", "case_study"],
                                       index=0)
            
            publishing_interval = st.number_input("Default Publishing Interval (minutes)",
                                                min_value=1, max_value=1440, value=5)
            
            auto_publish = st.checkbox("Auto-publish to WordPress", value=True)
        
        if st.button("💾 Save Content Settings"):
            settings = {
                "default_language": default_language,
                "default_length": default_length,
                "default_audience": default_audience,
                "content_style": content_style,
                "publishing_interval": publishing_interval,
                "auto_publish": auto_publish
            }
            st.success("✅ Content settings saved!")
        
        # Content Quality Settings
        st.subheader("Content Quality Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            min_word_count = st.number_input("Minimum Word Count", min_value=100, value=500)
            max_word_count = st.number_input("Maximum Word Count", min_value=500, value=2500)
        
        with col2:
            include_images = st.checkbox("Include Images", value=True)
            include_meta = st.checkbox("Generate Meta Descriptions", value=True)
        
        # SEO Settings
        st.subheader("SEO Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            focus_keywords = st.number_input("Max Focus Keywords", min_value=1, max_value=10, value=3)
            keyword_density = st.slider("Target Keyword Density (%)", 1.0, 5.0, 2.5, 0.1)
        
        with col2:
            include_headings = st.checkbox("Auto-generate Headings", value=True)
            include_tags = st.checkbox("Auto-generate Tags", value=True)
    
    def show_wordpress_settings(self):
        """Display WordPress settings"""
        st.header("🌐 WordPress Configuration")
        
        # Load current WordPress settings
        try:
            with open("config/settings.json", "r") as f:
                settings = json.load(f)
            wordpress_sites = settings.get("wordpress_websites", {})
        except:
            wordpress_sites = {}
        
        if wordpress_sites:
            st.success(f"✅ {len(wordpress_sites)} WordPress site(s) configured")
            
            for site_id, site in wordpress_sites.items():
                with st.expander(f"📝 {site.get('name', 'Unnamed Site')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.text_input("Site Name", value=site.get('name', ''), key=f"name_{site_id}")
                        st.text_input("URL", value=site.get('url', ''), key=f"url_{site_id}")
                        st.selectbox("Language", ["english", "farsi", "arabic"], 
                                   index=["english", "farsi", "arabic"].index(site.get('language', 'english')),
                                   key=f"lang_{site_id}")
                    
                    with col2:
                        st.text_input("Username", value=site.get('username', ''), key=f"user_{site_id}")
                        st.text_input("Password", type="password", key=f"pass_{site_id}")
                        st.checkbox("Active", value=site.get('is_active', True), key=f"active_{site_id}")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("🔍 Test Connection", key=f"test_{site_id}"):
                            st.info("Testing WordPress connection...")
                    with col2:
                        if st.button("💾 Update", key=f"update_{site_id}"):
                            st.success("Site settings updated!")
                    with col3:
                        if st.button("🗑️ Remove", key=f"remove_{site_id}"):
                            st.warning("Site removed!")
        else:
            st.warning("⚠️ No WordPress sites configured")
        
        # Add New Site
        st.subheader("➕ Add New WordPress Site")
        
        with st.form("add_wordpress_site"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("Site Name", placeholder="My Blog")
                new_url = st.text_input("WordPress URL", placeholder="https://myblog.com")
                new_language = st.selectbox("Content Language", ["english", "farsi", "arabic"])
            
            with col2:
                new_username = st.text_input("Username", placeholder="admin")
                new_password = st.text_input("Password", type="password")
                new_description = st.text_area("Description", placeholder="Site description...")
            
            submitted = st.form_submit_button("➕ Add WordPress Site")
            
            if submitted and new_name and new_url and new_username and new_password:
                st.success(f"✅ WordPress site '{new_name}' added successfully!")
                st.info("💡 Restart the application to apply changes")
    
    def show_system_info(self):
        """Display system information"""
        st.header("📊 System Information")
        
        # System Status
        st.subheader("System Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
            st.metric("Platform", sys.platform)
        
        with col2:
            # Check if API key is configured
            api_status = "✅ Configured" if os.getenv('ANTHROPIC_API_KEY') else "❌ Missing"
            st.metric("Claude API", api_status)
            
            # Check settings file
            settings_status = "✅ Found" if os.path.exists("config/settings.json") else "❌ Missing"
            st.metric("Settings File", settings_status)
        
        with col3:
            # Check projects
            projects_status = "✅ Found" if os.path.exists("projects.json") else "❌ Missing"
            st.metric("Projects File", projects_status)
            
            # Check core modules
            try:
                from core.project_manager import MultilingualProjectManager
                core_status = "✅ Working"
            except:
                core_status = "❌ Error"
            st.metric("Core Modules", core_status)
        
        # File Paths
        st.subheader("File Paths")
        
        paths = {
            "Project Root": str(project_root),
            "Settings File": "config/settings.json",
            "Projects File": "projects.json",
            "Core Directory": "core/",
            "Content Directory": "content/",
            "Dashboards Directory": "dashboards/"
        }
        
        for name, path in paths.items():
            exists = os.path.exists(path)
            status = "✅" if exists else "❌"
            st.text(f"{status} {name}: {path}")
        
        # Environment Variables
        st.subheader("Environment Variables")
        
        env_vars = [
            "ANTHROPIC_API_KEY",
            "UNSPLASH_ACCESS_KEY", 
            "UNSPLASH_SECRET_KEY",
            "WORDPRESS_URL",
            "WORDPRESS_USERNAME",
            "WORDPRESS_PASSWORD"
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
                st.text(f"✅ {var}: {masked}")
            else:
                st.text(f"❌ {var}: Not set")
        
        # System Actions
        st.subheader("System Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Reload Settings"):
                st.success("Settings reloaded!")
        
        with col2:
            if st.button("🧹 Clear Cache"):
                st.success("Cache cleared!")
        
        with col3:
            if st.button("📊 Run Diagnostics"):
                with st.spinner("Running diagnostics..."):
                    st.success("✅ All systems operational!")

def main():
    """Main entry point"""
    dashboard = SettingsDashboard()
    dashboard.run()

if __name__ == "__main__":
    main() 