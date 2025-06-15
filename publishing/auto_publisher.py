#!/usr/bin/env python3
"""
Automated WordPress Publisher for AgenticAI Updates
Automatically publishes new blog posts without user interaction
"""

import os
import json
import base64
import requests
import yaml
import markdown
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class AutoWordPressPublisher:
    def __init__(self):
        # Load site URL from environment or config
        self.site_url = os.getenv("WP_SITE_URL") or self._load_config_value("site_url") or "https://agenticaiupdates.space"
        self.api_url = f"{self.site_url}/wp-json/wp/v2"
        self.config_file = ".wp_config.json"
        self.content_dir = "serie 1"
        self.headers = None
        
        # Initialize content system
        self.content_system = AutoContentSystem()
        
    def _load_config_value(self, key):
        """Load a configuration value from the config file"""
        try:
            if os.path.exists(".wp_config.json"):
                with open(".wp_config.json", 'r') as f:
                    config = json.load(f)
                return config.get(key)
        except Exception as e:
            print(f"Warning: Could not load config value '{key}': {e}")
        return None
    
    def setup_credentials(self, username: str, password: str) -> bool:
        """Setup and save WordPress credentials"""
        try:
            # Create authentication header
            credentials = f"{username}:{password}"
            token = base64.b64encode(credentials.encode()).decode('utf-8')
            
            # Test connection
            test_headers = {
                'Authorization': f'Basic {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{self.api_url}/posts", headers=test_headers, params={'per_page': 1})
            
            if response.status_code == 200:
                # Save credentials to config file
                config = {
                    'username': username,
                    'password': password,
                    'token': token,
                    'setup_date': datetime.now().isoformat()
                }
                
                with open(self.config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                self.headers = test_headers
                print("✅ Credentials saved successfully!")
                return True
            else:
                print(f"❌ Failed to connect: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error setting up credentials: {e}")
            return False
    
    def load_credentials(self) -> bool:
        """Load saved WordPress credentials"""
        try:
            if not os.path.exists(self.config_file):
                return False
                
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            self.headers = {
                'Authorization': f'Basic {config["token"]}',
                'Content-Type': 'application/json'
            }
            
            # Test if credentials still work
            response = requests.get(f"{self.api_url}/posts", headers=self.headers, params={'per_page': 1})
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Error loading credentials: {e}")
            return False
    
    def parse_markdown_post(self, file_path: str) -> Dict:
        """Parse markdown file and extract metadata"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split YAML front matter and content
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                markdown_content = parts[2].strip()
                
                try:
                    metadata = yaml.safe_load(yaml_content)
                except yaml.YAMLError:
                    metadata = {}
            else:
                metadata = {}
                markdown_content = content
        else:
            metadata = {}
            markdown_content = content
        
        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content, extensions=['extra', 'codehilite'])
        
        return {
            'metadata': metadata,
            'content': html_content,
            'raw_content': markdown_content
        }
    
    def create_post(self, post_data: Dict) -> Optional[int]:
        """Create a new WordPress post"""
        try:
            response = requests.post(f"{self.api_url}/posts", 
                                   headers=self.headers, 
                                   json=post_data)
            
            if response.status_code == 201:
                post_id = response.json()['id']
                post_url = response.json().get('link', '')
                print(f"✅ Post published successfully!")
                print(f"📝 Post ID: {post_id}")
                print(f"🌐 URL: {post_url}")
                return post_id
            else:
                print(f"❌ Failed to create post: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating post: {e}")
            return None
    
    def publish_file(self, file_path: str, status: str = 'publish') -> Optional[int]:
        """Publish a specific markdown file"""
        print(f"📝 Publishing: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return None
        
        # Parse the markdown file
        parsed = self.parse_markdown_post(file_path)
        metadata = parsed['metadata']
        content = parsed['content']
        
        # Prepare WordPress post data
        post_data = {
            'title': metadata.get('title', Path(file_path).stem.replace('-', ' ').title()),
            'content': content,
            'status': status,
            'excerpt': metadata.get('description', ''),
        }
        
        # Add categories if specified
        categories = metadata.get('categories', [])
        if categories:
            post_data['categories'] = self._get_category_ids(categories)
        
        # Add tags if specified
        tags = metadata.get('tags', [])
        if tags:
            post_data['tags'] = self._get_tag_ids(tags)
        
        # Add featured image if specified
        featured_image = metadata.get('featured_image')
        if featured_image and isinstance(featured_image, dict):
            featured_media_id = self._upload_featured_image(featured_image)
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
        
        return self.create_post(post_data)
    
    def _get_category_ids(self, categories: List[str]) -> List[int]:
        """Get or create category IDs"""
        category_ids = []
        
        for category_name in categories:
            try:
                # Try to find existing category
                response = requests.get(f"{self.api_url}/categories", 
                                      headers=self.headers,
                                      params={'search': category_name})
                
                if response.status_code == 200:
                    categories_data = response.json()
                    if categories_data:
                        category_ids.append(categories_data[0]['id'])
                    else:
                        # Create new category
                        new_category = {
                            'name': category_name,
                            'slug': category_name.lower().replace(' ', '-')
                        }
                        create_response = requests.post(f"{self.api_url}/categories",
                                                      headers=self.headers,
                                                      json=new_category)
                        if create_response.status_code == 201:
                            category_ids.append(create_response.json()['id'])
            except Exception as e:
                print(f"⚠️  Error handling category '{category_name}': {e}")
        
        return category_ids
    
    def _get_tag_ids(self, tags: List[str]) -> List[int]:
        """Get or create tag IDs"""
        tag_ids = []
        
        for tag_name in tags:
            try:
                # Try to find existing tag
                response = requests.get(f"{self.api_url}/tags", 
                                      headers=self.headers,
                                      params={'search': tag_name})
                
                if response.status_code == 200:
                    tags_data = response.json()
                    if tags_data:
                        tag_ids.append(tags_data[0]['id'])
                    else:
                        # Create new tag
                        new_tag = {
                            'name': tag_name,
                            'slug': tag_name.lower().replace(' ', '-')
                        }
                        create_response = requests.post(f"{self.api_url}/tags",
                                                      headers=self.headers,
                                                      json=new_tag)
                        if create_response.status_code == 201:
                            tag_ids.append(create_response.json()['id'])
            except Exception as e:
                print(f"⚠️  Error handling tag '{tag_name}': {e}")
        
        return tag_ids
    
    def _upload_featured_image(self, featured_image: Dict) -> Optional[int]:
        """Upload featured image to WordPress media library"""
        try:
            # Download image from Unsplash
            image_url = featured_image.get('url')
            if not image_url:
                return None
            
            print(f"📸 Downloading featured image...")
            response = requests.get(image_url, timeout=30)
            if response.status_code != 200:
                print(f"❌ Failed to download image: {response.status_code}")
                return None
            
            # Prepare image data for WordPress
            filename = f"{featured_image.get('filename', 'featured-image')}.jpg"
            
            # Upload to WordPress media library
            files = {
                'file': (filename, response.content, 'image/jpeg')
            }
            
            media_data = {
                'title': featured_image.get('title', 'Featured Image'),
                'alt_text': featured_image.get('alt', 'AI Marketing Featured Image'),
                'caption': featured_image.get('caption', ''),
                'description': featured_image.get('alt', '')
            }
            
            print(f"📤 Uploading featured image to WordPress...")
            upload_response = requests.post(
                f"{self.api_url}/media",
                headers={'Authorization': self.headers['Authorization']},
                files=files,
                data=media_data
            )
            
            if upload_response.status_code == 201:
                media_id = upload_response.json()['id']
                print(f"✅ Featured image uploaded successfully! Media ID: {media_id}")
                return media_id
            else:
                print(f"❌ Failed to upload featured image: {upload_response.status_code}")
                print(f"Response: {upload_response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error uploading featured image: {e}")
            return None

def publish_latest_post():
    """Main function to automatically publish the latest blog post"""
    print("🚀 Auto WordPress Publisher for AgenticAI Updates")
    print("=" * 50)
    
    publisher = AutoWordPressPublisher()
    
    # Try to load existing credentials
    if not publisher.load_credentials():
        print("🔐 Setting up WordPress credentials...")
        
        # Your credentials (replace with actual values)
        username = "adminn"
        password = "Z6Nc T0kt ED5L 2gY0 sNPm nqf4"  # Your application password
        
        if not publisher.setup_credentials(username, password):
            print("❌ Failed to setup credentials. Exiting.")
            return False
    
    print("✅ Connected to WordPress!")
    
    # Find the newest blog post in serie 1 directory
    serie1_dir = Path("serie 1")
    if not serie1_dir.exists():
        print("❌ 'serie 1' directory not found!")
        return False
    
    # Get all markdown files and find the newest one
    md_files = list(serie1_dir.glob("*.md"))
    md_files = [f for f in md_files if not f.name.startswith('.')]
    
    if not md_files:
        print("❌ No markdown files found in 'serie 1' directory!")
        return False
    
    # Sort by modification time (newest first)
    newest_file = max(md_files, key=lambda x: x.stat().st_mtime)
    
    print(f"📄 Latest blog post: {newest_file.name}")
    
    # Publish the file
    post_id = publisher.publish_file(str(newest_file), status='publish')
    
    if post_id:
        print("\n🎉 Published successfully!")
        print(f"�� Check it out at: {publisher.site_url}")
        print("=" * 50)
        return True
    else:
        print("\n❌ Failed to publish the blog post.")
        return False

if __name__ == "__main__":
    publish_latest_post() 