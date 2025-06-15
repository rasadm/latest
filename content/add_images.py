#!/usr/bin/env python3
"""
Add Images to Blog Post
Adds relevant images to blog posts with configurable file paths
"""

import re
import os
import sys
import argparse

def add_images_to_post(file_path=None):
    """Add images to a blog post"""
    
    # Use provided file path or get from environment variable or use default
    if not file_path:
        file_path = os.getenv('BLOG_POST_FILE', 'serie 1/agentic-ai-revolution-marketing-automation-2025.md')
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        return False
    
    # Read the current content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Define image insertions with relevant alt text and captions
    image_insertions = [
        {
            'after': '# The Agentic AI Revolution: How Autonomous Marketing Agents Are Transforming Business Operations in 2025',
            'image': '\n\n![Agentic AI Revolution in Marketing](https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=400&fit=crop&auto=format "AI agents transforming marketing automation in 2025")\n*AI agents are revolutionizing how businesses approach marketing automation and customer engagement.*\n'
        },
        {
            'after': '## Understanding Agentic AI: The Next Evolution Beyond Traditional Automation',
            'image': '\n\n![AI Agent Network Visualization](https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=800&h=400&fit=crop&auto=format "Autonomous AI agents working together in intelligent networks")\n*Agentic AI represents autonomous intelligent systems that make decisions and take actions independently.*\n'
        },
        {
            'after': '### Campaign Management Revolution',
            'image': '\n\n![AI-Powered Marketing Dashboard](https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=400&fit=crop&auto=format "Real-time marketing campaign optimization through AI")\n*AI agents continuously optimize marketing campaigns across multiple channels in real-time.*\n'
        },
        {
            'after': '### Customer Experience Personalization at Scale',
            'image': '\n\n![Personalized Customer Experience](https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=400&fit=crop&auto=format "Hyper-personalized customer experiences powered by AI")\n*AI enables unprecedented levels of personalization across all customer touchpoints.*\n'
        },
        {
            'after': '## Multi-Agent AI Networks: The Future of Marketing Ecosystems',
            'image': '\n\n![Multi-Agent AI Network](https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=400&fit=crop&auto=format "Collaborative AI agents working together in marketing ecosystems")\n*Specialized AI agents collaborate to accomplish complex marketing objectives autonomously.*\n'
        },
        {
            'after': '### E-commerce and Retail Transformation',
            'image': '\n\n![AI in E-commerce](https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=800&h=400&fit=crop&auto=format "AI transforming e-commerce and retail marketing")\n*E-commerce platforms leverage AI agents for automated product marketing and customer engagement.*\n'
        },
        {
            'after': '## Implementation Strategies for 2025',
            'image': '\n\n![AI Implementation Strategy](https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=400&fit=crop&auto=format "Strategic implementation of AI agents in marketing operations")\n*Successful AI implementation requires careful planning and phased deployment strategies.*\n'
        },
        {
            'after': '## The Competitive Advantage of Early Adoption',
            'image': '\n\n![Competitive Advantage Through AI](https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=400&fit=crop&auto=format "Early AI adoption provides significant competitive advantages")\n*Companies implementing Agentic AI gain substantial competitive advantages in efficiency and performance.*\n'
        }
    ]
    
    # Insert images into the content
    for insertion in image_insertions:
        content = content.replace(insertion['after'], insertion['after'] + insertion['image'])
    
    # Write the updated content back to the file
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return False
    
    print("✅ Images added successfully to the blog post!")
    print("📝 Updated file: " + file_path)
    
    return True

def main():
    """Main function with command line argument support"""
    parser = argparse.ArgumentParser(description='Add images to blog posts')
    parser.add_argument('--file', '-f', type=str, 
                       help='Path to the blog post file to update')
    parser.add_argument('--list-env', action='store_true',
                       help='List environment variables that can be used')
    
    args = parser.parse_args()
    
    if args.list_env:
        print("Environment variables:")
        print("  BLOG_POST_FILE - Path to the blog post file")
        return
    
    success = add_images_to_post(args.file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 