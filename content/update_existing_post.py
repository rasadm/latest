#!/usr/bin/env python3
"""
Update Existing WordPress Post
Fixes broken images and missing internal links for published posts
"""

import os
import json
import requests
import base64
import yaml
from pathlib import Path
from publishing.wordpress_publisher import WordPressPublisher

def update_post_with_fixes():
    """Update the specific post with broken image and missing links"""
    
    # Load WordPress credentials
    config_file = ".wp_config.json"
    if not os.path.exists(config_file):
        print("❌ WordPress config file not found")
        return False
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Load site URL from environment or config
    site_url = os.getenv("WP_SITE_URL") or config.get("site_url") or "https://agenticaiupdates.space"
    
    # Initialize publisher
    publisher = WordPressPublisher(
        site_url=site_url,
        username=config["username"],
        password=config["password"]
    )
    
    # Test connection
    if not publisher.test_connection():
        print("❌ Cannot connect to WordPress")
        return False
    
    print("✅ Connected to WordPress")
    
    # Post ID 40 - the broken post
    post_id = 40
    
    # Read the updated markdown file
    file_path = "serie 1/how-leading-companies-are-using-machine-learning-in-customer-experience-to-transform-their-marketing-2025-06-13.md"
    
    print(f"📝 Reading updated content from: {file_path}")
    
    # Parse the markdown file
    parsed = publisher.parse_markdown_post(file_path)
    metadata = parsed['metadata']
    content = parsed['content']
    
    print(f"📊 Content length: {len(content)} characters")
    print(f"🖼️ Featured image URL: {metadata.get('featured_image', {}).get('url', 'Not found')}")
    
    # Upload featured image first
    featured_image = metadata.get('featured_image')
    featured_media_id = None
    
    if featured_image and isinstance(featured_image, dict):
        print("📤 Uploading featured image...")
        featured_media_id = publisher._upload_featured_image(featured_image)
        if featured_media_id:
            print(f"✅ Featured image uploaded! Media ID: {featured_media_id}")
        else:
            print("❌ Failed to upload featured image")
    
    # Prepare update data
    update_data = {
        'content': content,
        'excerpt': metadata.get('description', ''),
    }
    
    # Add featured image if uploaded
    if featured_media_id:
        update_data['featured_media'] = featured_media_id
    
    # Update the post
    print(f"🔄 Updating post ID {post_id}...")
    
    try:
        response = requests.post(
            f"{publisher.api_url}/posts/{post_id}",
            headers=publisher.headers,
            json=update_data
        )
        
        if response.status_code == 200:
            print(f"✅ Post updated successfully!")
            print(f"🌐 URL: https://agenticaiupdates.space/ai-marketing/{post_id}/")
            return True
        else:
            print(f"❌ Failed to update post: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating post: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Fixing broken post with image and internal links...")
    
    if update_post_with_fixes():
        print("🎉 Post successfully fixed!")
        print("✅ Featured image should now display properly")
        print("✅ Internal links have been added for better SEO")
    else:
        print("❌ Failed to fix the post")

if __name__ == "__main__":
    main() 