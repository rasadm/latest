#!/usr/bin/env python3
"""
WordPress Auto Publisher for AgenticAI Updates
Automatically publishes markdown blog posts to WordPress site
"""

import os
import re
import json
import requests
import base64
from datetime import datetime
from pathlib import Path
import yaml
import markdown
from typing import Dict, List, Optional

class WordPressPublisher:
    def __init__(self, site_url: str, username: str, password: str):
        """
        Initialize WordPress publisher
        
        Args:
            site_url: WordPress site URL (e.g., 'https://agenticaiupdates.space')
            username: WordPress username or email
            password: WordPress application password
        """
        self.site_url = site_url.rstrip('/')
        self.api_url = f"{self.site_url}/wp-json/wp/v2"
        self.username = username
        self.password = password
        
        # Create authentication header
        credentials = f"{username}:{password}"
        token = base64.b64encode(credentials.encode()).decode('utf-8')
        self.headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json',
            'User-Agent': 'WordPress-Publisher/1.0'
        }
        
        print(f"🔐 WordPress Publisher initialized for: {self.site_url}")
        print(f"👤 Username/Email: {username}")
        print(f"🔑 Using application password: {'*' * (len(password) - 4)}{password[-4:]}")
    
    def test_connection(self) -> bool:
        """Test WordPress API connection with detailed debugging"""
        print(f"🔍 Testing connection to: {self.api_url}")
        
        try:
            # First, test if the API is accessible
            response = requests.get(f"{self.site_url}/wp-json/", timeout=30)
            if response.status_code != 200:
                print(f"❌ WordPress API not accessible: {response.status_code}")
                return False
            
            print("✅ WordPress API is accessible")
            
            # Test authentication with a simple GET request
            auth_response = requests.get(
                f"{self.api_url}/users/me", 
                headers=self.headers, 
                timeout=30
            )
            
            if auth_response.status_code == 200:
                user_data = auth_response.json()
                print(f"✅ Authentication successful!")
                print(f"👤 Logged in as: {user_data.get('name', 'Unknown')}")
                print(f"🔐 User ID: {user_data.get('id', 'Unknown')}")
                print(f"📧 Email: {user_data.get('email', 'Unknown')}")
                
                # Check user capabilities
                capabilities = user_data.get('capabilities', {})
                can_publish = capabilities.get('publish_posts', False)
                can_edit = capabilities.get('edit_posts', False)
                
                print(f"📝 Can edit posts: {can_edit}")
                print(f"📤 Can publish posts: {can_publish}")
                
                if not can_publish:
                    print("⚠️ Warning: User doesn't have publish_posts capability")
                    print("💡 Try changing post status to 'draft' instead of 'publish'")
                
                return True
            else:
                print(f"❌ Authentication failed: {auth_response.status_code}")
                print(f"Response: {auth_response.text}")
                
                if auth_response.status_code == 401:
                    print("💡 Troubleshooting tips:")
                    print("   1. Verify your application password is correct")
                    print("   2. Make sure you're using username OR email (not both)")
                    print("   3. Check if 2FA is interfering with app passwords")
                    print("   4. Verify the user has proper permissions")
                
                return False
                
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def parse_markdown_post(self, file_path: str) -> Dict:
        """Parse markdown file and extract metadata with content cleaning"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split YAML front matter and content
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                markdown_content = parts[2].strip()
                
                # Parse YAML metadata
                try:
                    metadata = yaml.safe_load(yaml_content)
                    # Remove internal metadata that shouldn't be published
                    if '_internal' in metadata:
                        del metadata['_internal']
                except yaml.YAMLError:
                    metadata = {}
            else:
                metadata = {}
                markdown_content = content
        else:
            metadata = {}
            markdown_content = content
        
        # Clean markdown content - remove any metadata headers that might still exist
        lines = markdown_content.split('\n')
        cleaned_lines = []
        skip_metadata = False
        
        for line in lines:
            # Skip lines that look like metadata headers
            if line.startswith('**Project:**') or line.startswith('**Keyword:**') or \
               line.startswith('**Generated:**') or line.startswith('**Generation Method:**') or \
               line.startswith('**Word Count:**'):
                skip_metadata = True
                continue
            elif line.startswith('## SEO Information') or (skip_metadata and line.startswith('- **')):
                continue
            elif line.strip() == '---' and skip_metadata:
                skip_metadata = False
                continue
            elif not skip_metadata:
                cleaned_lines.append(line)
        
        cleaned_markdown = '\n'.join(cleaned_lines).strip()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(cleaned_markdown, extensions=['extra', 'codehilite'])
        
        return {
            'metadata': metadata,
            'content': html_content,
            'raw_content': cleaned_markdown
        }
    
    def create_post(self, post_data: Dict) -> Optional[int]:
        """Create a new WordPress post with enhanced error handling"""
        try:
            print(f"📝 Creating post: {post_data.get('title', 'Untitled')}")
            print(f"📊 Post status: {post_data.get('status', 'draft')}")
            
            response = requests.post(f"{self.api_url}/posts", 
                                   headers=self.headers, 
                                   json=post_data,
                                   timeout=60)
            
            if response.status_code == 201:
                post_data_response = response.json()
                post_id = post_data_response['id']
                post_url = post_data_response.get('link', 'N/A')
                print(f"✅ Post created successfully!")
                print(f"🆔 Post ID: {post_id}")
                print(f"🔗 Post URL: {post_url}")
                return post_id
            else:
                print(f"❌ Failed to create post: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
                # Provide specific error guidance
                if response.status_code == 401:
                    print("🔐 Authentication Error - Check your credentials")
                elif response.status_code == 403:
                    print("🚫 Permission Error - User lacks posting permissions")
                    print("💡 Try setting post status to 'draft' instead of 'publish'")
                elif response.status_code == 400:
                    print("📝 Bad Request - Check post data format")
                
                return None
                
        except Exception as e:
            print(f"❌ Error creating post: {e}")
            return None
    
    def publish_markdown_file(self, file_path: str, status: str = 'draft') -> Optional[int]:
        """Publish a markdown file to WordPress"""
        print(f"📝 Processing: {file_path}")
        
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
            'categories': self._get_category_ids(metadata.get('categories', [])),
            'tags': self._get_tag_ids(metadata.get('tags', [])),
        }
        
        # Add featured image if specified
        featured_image = metadata.get('featured_image')
        if featured_image:
            if isinstance(featured_image, dict):
                # New SEO-optimized featured image format
                featured_media_id = self._upload_featured_image(featured_image)
                if featured_media_id:
                    post_data['featured_media'] = featured_media_id
            else:
                # Legacy format - direct media ID
                post_data['featured_media'] = featured_image
        
        # Set publish date if specified
        if 'date' in metadata:
            post_data['date'] = metadata['date']
        
        return self.create_post(post_data)
    
    def _get_category_ids(self, categories: List[str]) -> List[int]:
        """Get or create category IDs"""
        category_ids = []
        
        for category_name in categories:
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
        
        return category_ids
    
    def _get_tag_ids(self, tags: List[str]) -> List[int]:
        """Get or create tag IDs"""
        tag_ids = []
        
        for tag_name in tags:
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
    
    def publish_directory(self, directory_path: str, status: str = 'draft') -> List[int]:
        """Publish all markdown files in a directory"""
        published_ids = []
        
        directory = Path(directory_path)
        if not directory.exists():
            print(f"❌ Directory not found: {directory_path}")
            return published_ids
        
        # Find all markdown files
        md_files = list(directory.glob('*.md'))
        
        print(f"📁 Found {len(md_files)} markdown files in {directory_path}")
        
        for md_file in md_files:
            if md_file.name.startswith('.'):
                continue  # Skip hidden files
                
            post_id = self.publish_markdown_file(str(md_file), status)
            if post_id:
                published_ids.append(post_id)
        
        return published_ids


def main():
    """Test the WordPress publisher"""
    # Load site URL from environment or config
    SITE_URL = os.getenv("WP_SITE_URL") or "https://agenticaiupdates.space"
    
    # Get credentials from user
    print("Please provide your WordPress credentials:")
    username = input("WordPress Username or Email: ").strip()
    password = input("WordPress Application Password: ").strip()
    
    if not username or not password:
        print("❌ Username and password are required!")
        return
    
    publisher = WordPressPublisher(SITE_URL, username, password)
    
    if not publisher.test_connection():
        print("❌ Failed to connect to WordPress. Please check your credentials and site URL.")
        return
    
    print("✅ Successfully connected to WordPress!")
    
    # Menu options
    while True:
        print("\n📋 What would you like to do?")
        print("1. Publish all posts from 'serie 1' directory (as drafts)")
        print("2. Publish all posts from 'serie 1' directory (publish immediately)")
        print("3. Publish a specific file")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            print("\n📤 Publishing posts as drafts...")
            published = publisher.publish_directory('serie 1', 'draft')
            print(f"\n✅ Published {len(published)} posts as drafts!")
            
        elif choice == '2':
            confirm = input("\n⚠️  This will publish posts immediately. Are you sure? (y/N): ")
            if confirm.lower() == 'y':
                print("\n📤 Publishing posts immediately...")
                published = publisher.publish_directory('serie 1', 'publish')
                print(f"\n✅ Published {len(published)} posts!")
            else:
                print("❌ Cancelled.")
                
        elif choice == '3':
            file_path = input("Enter the path to the markdown file: ").strip()
            if os.path.exists(file_path):
                status = input("Publish as draft or immediately? (draft/publish): ").strip().lower()
                if status not in ['draft', 'publish']:
                    status = 'draft'
                
                post_id = publisher.publish_markdown_file(file_path, status)
                if post_id:
                    print(f"✅ Post published successfully!")
            else:
                print("❌ File not found!")
                
        elif choice == '4':
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main() 