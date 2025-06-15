#!/usr/bin/env python3
"""
Automated Content Creation & Publishing System
Continuously creates and publishes AI marketing blog posts
"""

import os
import json
import time
import random
import requests
import base64
import yaml
import markdown
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import schedule
from core.local_llm_content import MultilingualLocalLLMContentGenerator
from core.enhanced_research_llm import EnhancedResearchLLMGenerator
from content.claude_content import ClaudeContentGenerator
from seo.seo_optimizer import MultilingualSEOOptimizer

class AutoContentSystem:
    def __init__(self):
        self.config_file = "config/settings.json"  # Use new settings file
        self.site_url = os.getenv("WP_SITE_URL") or self._load_config_value("site_url") or "https://agenticaiupdates.space"
        self.api_url = f"{self.site_url}/wp-json/wp/v2"
        self.content_dir = os.getenv("CONTENT_DIR") or self._load_config_value("content_dir") or "serie 1"
        self.headers = None
        
        # WordPress website info
        self.wordpress_website = None
        
        # Initialize local LLM generator
        self.local_llm = MultilingualLocalLLMContentGenerator()
        self.use_local_llm = False  # Default to template-based generation
        
        # Initialize enhanced research + LLM generator
        self.enhanced_research = EnhancedResearchLLMGenerator()
        self.use_research_llm = False  # Default to template-based generation
        
        # Initialize SEO optimizer
        self.seo_optimizer = MultilingualSEOOptimizer()
        
        # Load dynamic configuration
        self.image_collections = self._load_image_config().get("collections", self._get_default_image_collections())
        self.featured_image_map = self._load_image_config().get("featured_map", self._get_default_featured_map())
        
        # Content topics and templates
        self.topics = [
            "AI Marketing Automation Trends",
            "Machine Learning in Customer Experience",
            "Predictive Analytics for Marketing",
            "Conversational AI and Chatbots",
            "AI-Powered Content Personalization",
            "Marketing Attribution with AI",
            "Voice Search Optimization",
            "AI in Social Media Marketing",
            "Programmatic Advertising Evolution",
            "Customer Data Platform Innovation",
            "AI Ethics in Marketing",
            "Marketing Technology Stack Optimization",
            "Real-time Personalization Strategies",
            "AI-Driven Customer Journey Mapping",
            "Automated Email Marketing Campaigns"
        ]
        
        self.content_templates = {
            "trend_analysis": {
                "title_format": "{topic}: {year} Trends and Predictions for Modern Marketers",
                "sections": [
                    "Current State of {topic}",
                    "Emerging Trends and Technologies",
                    "Industry Impact and Applications",
                    "Implementation Strategies",
                    "Future Outlook and Predictions"
                ]
            },
            "how_to_guide": {
                "title_format": "The Complete Guide to {topic}: Best Practices and Implementation",
                "sections": [
                    "Understanding {topic}",
                    "Getting Started: Essential Requirements",
                    "Step-by-Step Implementation",
                    "Common Challenges and Solutions",
                    "Measuring Success and ROI"
                ]
            },
            "case_study": {
                "title_format": "How Leading Companies Are Using {topic} to Transform Their Marketing",
                "sections": [
                    "The Challenge: Traditional Marketing Limitations",
                    "The Solution: {topic} Implementation",
                    "Real-World Success Stories",
                    "Key Lessons and Takeaways",
                    "Actionable Insights for Your Business"
                ]
            }
        }
        
    def _load_config_value(self, key):
        """Load a configuration value from the config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                return config.get(key)
        except Exception as e:
            print(f"Warning: Could not load config value '{key}': {e}")
        return None
    
    def _load_image_config(self):
        """Load image configuration from file"""
        try:
            if os.path.exists("image_config.json"):
                with open("image_config.json", "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load image config: {e}")
        return {}
    
    def _get_default_image_collections(self):
        """Get default image collections as fallback"""
        return {
            "AI Marketing Automation": [
                {"id": "photo-1677442136019-21780ecad995", "keywords": "ai-marketing-automation-dashboard"},
                {"id": "photo-1551288049-bebda4e38f71", "keywords": "marketing-automation-analytics"},
                {"id": "photo-1460925895917-afdab827c52f", "keywords": "ai-powered-marketing-tools"},
                {"id": "photo-1519389950473-47ba0277781c", "keywords": "automated-marketing-workflow"},
                {"id": "photo-1563013544-824ae1b704d3", "keywords": "ai-marketing-strategy-planning"}
            ],
            "Machine Learning": [
                {"id": "photo-1620712943543-bcc4688e7485", "keywords": "machine-learning-algorithms"},
                {"id": "photo-1518709268805-4e9042af2176", "keywords": "ai-neural-network-visualization"},
                {"id": "photo-1507003211169-0a1dd7228f2d", "keywords": "data-science-machine-learning"},
                {"id": "photo-1454165804606-c3d57bc86b40", "keywords": "ai-algorithm-development"},
                {"id": "photo-1555949963-aa79dcee981c", "keywords": "machine-learning-data-analysis"}
            ],
            "Customer Experience": [
                {"id": "photo-1560472354-b33ff0c44a43", "keywords": "customer-experience-personalization"},
                {"id": "photo-1556742049-0cfed4f6a45d", "keywords": "digital-customer-journey"},
                {"id": "photo-1573164713714-d95e436ab8d6", "keywords": "customer-satisfaction-analytics"},
                {"id": "photo-1552664730-d307ca884978", "keywords": "customer-engagement-strategy"},
                {"id": "photo-1600880292203-757bb62b4baf", "keywords": "personalized-customer-service"}
            ],
            "Analytics": [
                {"id": "photo-1551288049-bebda4e38f71", "keywords": "marketing-analytics-dashboard"},
                {"id": "photo-1460925895917-afdab827c52f", "keywords": "data-visualization-charts"},
                {"id": "photo-1504868584819-f8e8b4b6d7e3", "keywords": "business-intelligence-analytics"},
                {"id": "photo-1551650975-87deedd944c3", "keywords": "predictive-analytics-graphs"},
                {"id": "photo-1590650153855-d9e808231d41", "keywords": "marketing-performance-metrics"}
            ],
            "Technology": [
                {"id": "photo-1518709268805-4e9042af2176", "keywords": "ai-technology-innovation"},
                {"id": "photo-1485827404703-89b55fcc595e", "keywords": "digital-transformation-tech"},
                {"id": "photo-1519389950473-47ba0277781c", "keywords": "modern-technology-solutions"},
                {"id": "photo-1581091226825-a6a2a5aee158", "keywords": "artificial-intelligence-tech"},
                {"id": "photo-1677442136019-21780ecad995", "keywords": "advanced-ai-systems"}
            ]
        }
    
    def _get_default_featured_map(self):
        """Get default featured image map as fallback"""
        return {
            "AI Marketing Automation": "photo-1677442136019-21780ecad995",
            "Machine Learning": "photo-1620712943543-bcc4688e7485", 
            "Predictive Analytics": "photo-1551288049-bebda4e38f71",
            "Conversational AI": "photo-1485827404703-89b55fcc595e",
            "Content Personalization": "photo-1560472354-b33ff0c44a43",
            "Marketing Attribution": "photo-1504868584819-f8e8b4b6d7e3",
            "Voice Search": "photo-1589254065878-42c9da997008",
            "Social Media": "photo-1611224923853-80b023f02d71",
            "Programmatic Advertising": "photo-1460925895917-afdab827c52f",
            "Customer Data Platform": "photo-1551650975-87deedd944c3",
            "AI Ethics": "photo-1507003211169-0a1dd7228f2d",
            "Marketing Technology": "photo-1518709268805-4e9042af2176",
            "Real-time Personalization": "photo-1556742049-0cfed4f6a45d",
            "Customer Journey": "photo-1573164713714-d95e436ab8d6",
            "Email Marketing": "photo-1596526131083-e8c633c948d2"
        }
    
    def load_credentials(self) -> bool:
        """Load WordPress credentials from new settings structure"""
        try:
            if not os.path.exists(self.config_file):
                print(f"❌ Settings file not found: {self.config_file}")
                return False
                
            with open(self.config_file, 'r') as f:
                settings = json.load(f)
            
            # Get WordPress websites
            wordpress_websites = settings.get('wordpress_websites', {})
            if not wordpress_websites:
                print("❌ No WordPress websites configured")
                return False
            
            # Get the default website or first available
            default_website_id = settings.get('default_website')
            if default_website_id and default_website_id in wordpress_websites:
                self.wordpress_website = wordpress_websites[default_website_id]
            else:
                # Get first available website
                website_id = next(iter(wordpress_websites.keys()))
                self.wordpress_website = wordpress_websites[website_id]
            
            # Update site URL and API URL
            self.site_url = self.wordpress_website['url'].rstrip('/')
            self.api_url = f"{self.site_url}/wp-json/wp/v2"
            
            # Create authentication header
            credentials = f"{self.wordpress_website['username']}:{self.wordpress_website['password']}"
            token = base64.b64encode(credentials.encode()).decode('utf-8')
            
            self.headers = {
                'Authorization': f'Basic {token}',
                'Content-Type': 'application/json',
                'User-Agent': 'AutoContentSystem/1.0'
            }
            
            print(f"✅ Loaded credentials for: {self.wordpress_website['name']}")
            print(f"🌐 Site URL: {self.site_url}")
            print(f"👤 Username: {self.wordpress_website['username']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading credentials: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def enable_local_llm(self, provider: str = "deepseek") -> bool:
        """Enable local LLM content generation"""
        try:
            self.local_llm.set_provider(provider)
            if self.local_llm.test_connection():
                self.use_local_llm = True
                print(f"✅ Local LLM enabled: {provider}")
                return True
            else:
                print(f"❌ Cannot connect to {provider}")
                return False
        except Exception as e:
            print(f"❌ Error enabling local LLM: {e}")
            return False
    
    def disable_local_llm(self):
        """Disable local LLM and use template generation"""
        self.use_local_llm = False
        print("📝 Using template-based content generation")
    
    def enable_research_llm(self, provider: str = "deepseek") -> bool:
        """Enable research-enhanced LLM content generation"""
        try:
            self.enhanced_research.local_llm.set_provider(provider)
            if self.enhanced_research.local_llm.test_connection():
                self.use_research_llm = True
                self.use_local_llm = False  # Disable basic LLM when using research
                print(f"✅ Research-enhanced LLM enabled: {provider}")
                return True
            else:
                print(f"❌ Cannot connect to {provider}")
                return False
        except Exception as e:
            print(f"❌ Error enabling research LLM: {e}")
            return False
    
    def disable_research_llm(self):
        """Disable research LLM and use template generation"""
        self.use_research_llm = False
        print("📝 Using template-based content generation")
    
    def generate_content_idea(self) -> Dict:
        """Generate a new content idea"""
        topic = random.choice(self.topics)
        template_type = random.choice(list(self.content_templates.keys()))
        template = self.content_templates[template_type]
        
        # Generate title
        title = template["title_format"].format(
            topic=topic,
            year=datetime.now().year
        )
        
        # Generate filename
        filename = title.lower().replace(" ", "-").replace(":", "").replace(",", "")
        filename = "".join(c for c in filename if c.isalnum() or c in "-_")
        filename = f"{filename}-{datetime.now().strftime('%Y-%m-%d')}.md"
        
        return {
            "title": title,
            "topic": topic,
            "template_type": template_type,
            "template": template,
            "filename": filename,
            "sections": [section.format(topic=topic) for section in template["sections"]]
        }
    
    def create_blog_post(self, content_idea: Dict) -> str:
        """Create a complete blog post"""
        
        # Generate SEO-friendly description
        description = f"Discover how {content_idea['topic'].lower()} is transforming marketing in {datetime.now().year}. Learn implementation strategies, best practices, and future trends."
        
        # Generate tags and categories
        default_categories = ["AI Marketing", "Marketing Technology", "Digital Innovation"]
        default_tags = ["ai-marketing", "marketing-automation", "digital-transformation"]
        
        categories = self._load_config_value("categories") or default_categories
        base_tags = self._load_config_value("tags") or default_tags
        
        tags = [
            content_idea['topic'].lower().replace(" ", "-"),
            *base_tags,
            f"{datetime.now().year}-trends"
        ]
        
        # Generate SEO-optimized featured image
        featured_image = self.generate_featured_image(content_idea)
        
        # Calculate reading time based on content length (estimate)
        estimated_word_count = len(content_idea["sections"]) * 400  # Rough estimate
        reading_time = max(1, estimated_word_count // 200)
        
        # Create YAML front matter with enhanced SEO
        front_matter = {
            "title": content_idea["title"],
            "description": description,
            "categories": categories,
            "tags": tags,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "featured_image": featured_image,
            "author": os.getenv("BLOG_AUTHOR") or self._load_config_value("author") or "RasaDM Research Team",
            "reading_time": f"{reading_time} minutes",
            "seo_keywords": ", ".join(tags[:5]),
            "schema_type": "Article",
            "image_count": len(content_idea["sections"]),
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "image_seo": {
                "optimized": True,
                "alt_text_strategy": "descriptive_with_keywords",
                "filename_strategy": "seo_optimized_slugs",
                "size_optimization": "responsive_webp_fallback"
            }
        }
        
        # Generate content sections
        content_sections = []
        
        # Introduction
        intro = f"""
The landscape of {content_idea['topic'].lower()} continues to evolve at an unprecedented pace in {datetime.now().year}. As businesses increasingly rely on artificial intelligence and machine learning technologies, understanding the latest developments in {content_idea['topic'].lower()} has become crucial for marketing success.

Recent industry research indicates that companies implementing advanced {content_idea['topic'].lower()} strategies are seeing significant improvements in customer engagement, conversion rates, and overall marketing ROI. This comprehensive analysis explores the current state of {content_idea['topic'].lower()}, emerging trends, and practical implementation strategies for modern marketing teams.
"""
        
        content_sections.append(intro.strip())
        
        # Main sections
        for i, section in enumerate(content_idea["sections"]):
            section_content = self.generate_section_content(section, content_idea["topic"], i)
            content_sections.append(f"## {section}\n\n{section_content}")
        
        # Conclusion
        conclusion = f"""
## Conclusion: Embracing the Future of {content_idea['topic']}

The evolution of {content_idea['topic'].lower()} represents a fundamental shift in how businesses approach marketing and customer engagement. Organizations that embrace these technologies and implement them strategically will gain significant competitive advantages in efficiency, personalization, and customer satisfaction.

Success in this rapidly changing landscape requires continuous learning, strategic planning, and careful implementation. By understanding the trends, challenges, and opportunities outlined in this analysis, marketing teams can make informed decisions about their {content_idea['topic'].lower()} strategies and drive meaningful business results.

The future of marketing lies in the intelligent application of these technologies, combined with human creativity and strategic thinking. Companies that master this balance will not only survive the digital transformation but will define the next era of marketing excellence.

*Ready to transform your marketing with {content_idea['topic'].lower()}? The RasaDM platform offers cutting-edge solutions designed for modern marketing teams. Contact our experts to discover how these technologies can revolutionize your marketing performance and drive unprecedented business growth.*
"""
        
        content_sections.append(conclusion.strip())
        
        # Combine all content
        yaml_content = yaml.dump(front_matter, default_flow_style=False)
        full_content = f"---\n{yaml_content}---\n\n" + "\n\n".join(content_sections)
        
        return full_content
    
    def generate_section_content(self, section_title: str, topic: str, section_index: int) -> str:
        """Generate content for a specific section"""
        
        content_templates = {
            0: f"""
{section_title} encompasses the current technological landscape and market dynamics shaping modern marketing strategies. The integration of artificial intelligence and machine learning has fundamentally transformed how businesses approach customer engagement, data analysis, and campaign optimization.

Current market research indicates that organizations implementing {topic.lower()} are experiencing measurable improvements in key performance metrics, including conversion rates, customer engagement, and customer acquisition costs. (Insert live statistics here when available.)

The technology stack supporting {topic.lower()} has evolved considerably, with new platforms and tools emerging regularly. Modern solutions offer enhanced integration capabilities, real-time analytics, and sophisticated automation features that enable marketing teams to operate more efficiently and effectively.

Key market drivers include increasing customer expectations for personalized experiences, the need for data-driven decision making, and competitive pressure to adopt innovative technologies. These factors are accelerating adoption across industries and company sizes.
""",
            1: f"""
{section_title} are reshaping the marketing landscape through innovative applications of artificial intelligence, machine learning, and advanced analytics. These developments are creating new opportunities for businesses to enhance customer experiences and improve marketing performance.

Emerging technologies in {topic.lower()} include advanced predictive analytics, real-time personalization engines, and autonomous decision-making systems. These innovations enable marketing teams to anticipate customer needs, deliver relevant experiences, and optimize campaigns automatically.

The integration of Internet of Things (IoT) data, voice technology, and augmented reality is expanding the possibilities for {topic.lower()} applications. These technologies provide new touchpoints for customer interaction and additional data sources for enhanced personalization.

Industry experts predict that the next wave of innovation will focus on emotional intelligence, cross-platform integration, and privacy-preserving technologies. These developments will enable more sophisticated customer understanding while maintaining data security and compliance requirements.
""",
            2: f"""
{section_title} demonstrates the practical value and transformative potential of {topic.lower()} across various industries and use cases. Organizations are leveraging these technologies to solve complex marketing challenges and achieve measurable business results.

In the retail sector, companies are using {topic.lower()} to create personalized shopping experiences, optimize inventory management, and improve customer service. E-commerce platforms report significant improvements in conversion rates and customer satisfaction through intelligent product recommendations and dynamic pricing strategies.

Financial services organizations are implementing {topic.lower()} for risk assessment, fraud prevention, and personalized financial advice. These applications enable more accurate customer segmentation and targeted marketing campaigns while maintaining regulatory compliance.

Healthcare and pharmaceutical companies are utilizing {topic.lower()} for patient education, treatment adherence programs, and clinical trial recruitment. These applications demonstrate the technology's versatility and potential for positive social impact.

B2B companies are adopting {topic.lower()} for lead scoring, account-based marketing, and sales enablement. These implementations result in improved sales efficiency and higher-quality customer relationships.
""",
            3: f"""
{section_title} require careful planning, strategic thinking, and systematic execution to achieve optimal results. Successful implementation involves multiple phases, from initial assessment to full-scale deployment and optimization.

The foundation phase focuses on data infrastructure, team preparation, and technology selection. Organizations must ensure robust data management capabilities, develop AI literacy among team members, and choose platforms that align with business objectives and technical requirements.

Pilot implementation allows organizations to test {topic.lower()} applications in controlled environments before full-scale deployment. This approach enables learning, refinement, and risk mitigation while building internal expertise and confidence.

Scaling strategies involve expanding successful pilot programs across additional channels, customer segments, and use cases. This phase requires careful change management, performance monitoring, and continuous optimization to maximize impact.

Integration considerations include connecting {topic.lower()} systems with existing marketing technology stacks, ensuring data consistency, and maintaining security and compliance standards. Successful integration enables seamless workflows and comprehensive customer insights.
""",
            4: f"""
{section_title} indicate continued evolution and innovation in {topic.lower()}, with emerging technologies and changing market dynamics creating new opportunities and challenges for marketing organizations.

Technological advancement will focus on increased automation, enhanced personalization capabilities, and improved integration across platforms and channels. These developments will enable more sophisticated marketing strategies and better customer experiences.

Market trends suggest growing adoption across industries and company sizes, driven by competitive pressure and customer expectations. Organizations that delay implementation risk falling behind competitors who leverage these technologies effectively.

Regulatory developments will shape the future landscape, with increased focus on data privacy, algorithmic transparency, and ethical AI practices. Organizations must balance innovation with compliance and responsible technology use.

The convergence of {topic.lower()} with other emerging technologies, such as blockchain, quantum computing, and advanced robotics, will create new possibilities for marketing innovation and customer engagement.

Investment in {topic.lower()} is expected to continue growing, with venture capital and corporate funding supporting continued innovation and market expansion. This investment will accelerate technology development and market maturation.
"""
        }
        
        return content_templates.get(section_index, content_templates[0]).strip()
    
    def generate_seo_optimized_images(self, content_idea: Dict, sections: List[str]) -> List[Dict]:
        """Generate SEO-optimized images for each section"""
        
        # Use dynamic image collections loaded from config
        image_collections = self.image_collections
        
        # Determine which collection to use based on topic
        topic = content_idea['topic']
        collection_key = "AI Marketing Automation"  # default
        
        for key in image_collections.keys():
            if any(word in topic for word in key.split()):
                collection_key = key
                break
        
        selected_images = image_collections.get(collection_key, image_collections.get("AI Marketing Automation", []))
        
        # Generate unique images for each section
        seo_images = []
        for i, section in enumerate(sections[:len(selected_images)]):
            if i < len(selected_images):
                image_data = selected_images[i]
                
                # Create SEO-optimized filename
                section_slug = section.lower().replace(' ', '-').replace(':', '').replace(',', '')
                section_slug = ''.join(c for c in section_slug if c.isalnum() or c in '-_')
                
                # Generate SEO alt text
                alt_text = f"{section} - {topic} strategies and implementation guide for modern marketers"
                
                # Create SEO-optimized image title
                title_text = f"{section}: Advanced {topic} solutions for business growth and customer engagement"
                
                # Generate caption with SEO keywords
                caption = f"*{section} leverages cutting-edge {topic.lower()} to drive measurable business results and enhance customer experiences.*"
                
                # Build optimized Unsplash URL with SEO parameters
                image_url = f"https://images.unsplash.com/{image_data['id']}?w=800&h=400&fit=crop&auto=format&q=80"
                
                seo_images.append({
                    'url': image_url,
                    'alt': alt_text,
                    'title': title_text,
                    'caption': caption,
                    'filename': f"{image_data['keywords']}-{section_slug}",
                    'section': section
                })
        
        return seo_images
    
    def generate_featured_image(self, content_idea: Dict) -> Dict:
        """Generate SEO-optimized featured image for the blog post"""
        
        # Use dynamic featured image map loaded from config
        featured_image_map = self.featured_image_map
        
        # Find best matching image based on topic keywords
        topic = content_idea['topic']
        image_id = "photo-1677442136019-21780ecad995"  # default
        
        for key, img_id in featured_image_map.items():
            if any(word in topic for word in key.split()):
                image_id = img_id
                break
        
        # Generate SEO-optimized filename and metadata
        topic_slug = topic.lower().replace(' ', '-').replace(',', '').replace(':', '')
        topic_slug = ''.join(c for c in topic_slug if c.isalnum() or c in '-_')
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"{topic_slug}-featured-image-{date_str}"
        
        # Create comprehensive SEO metadata
        featured_image = {
            "url": f"https://images.unsplash.com/{image_id}?w=1200&h=630&fit=crop&auto=format&q=80",
            "url_webp": f"https://images.unsplash.com/{image_id}?w=1200&h=630&fit=crop&auto=format&fm=webp&q=80",
            "url_mobile": f"https://images.unsplash.com/{image_id}?w=800&h=420&fit=crop&auto=format&q=80",
            "alt": f"{topic} - Complete implementation guide and best practices for modern marketers in {datetime.now().year}",
            "title": f"{topic}: Advanced strategies for business growth and marketing success",
            "filename": filename,
            "caption": f"Comprehensive guide to {topic.lower()} implementation and optimization strategies",
            "width": 1200,
            "height": 630,
            "format": "webp",
            "seo_score": 95,
            "keywords": [topic.lower().replace(' ', '-'), "marketing-strategy", "business-growth", f"{datetime.now().year}-trends"]
        }
        
        return featured_image
    
    def add_images_to_content(self, content: str, content_idea: Dict) -> str:
        """Add SEO-optimized images to content"""
        
        # Extract sections from content
        lines = content.split('\n')
        sections = [line.replace('## ', '') for line in lines if line.startswith('## ')]
        
        # Generate SEO-optimized images
        seo_images = self.generate_seo_optimized_images(content_idea, sections)
        
        # Add images after each section
        new_lines = []
        image_index = 0
        
        for line in lines:
            new_lines.append(line)
            
            # Check if this line is a section header and we have an image for it
            if line.startswith('## ') and image_index < len(seo_images):
                image = seo_images[image_index]
                
                # Add SEO-optimized image with proper markup
                image_line = f'\n![{image["alt"]}]({image["url"]} "{image["title"]}")'
                caption_line = f'{image["caption"]}\n'
                
                new_lines.extend([image_line, caption_line])
                image_index += 1
        
        return '\n'.join(new_lines)
    
    def save_blog_post(self, content: str, filename: str, content_idea: Dict) -> str:
        """Save blog post to file"""
        
        # Ensure content directory exists
        Path(self.content_dir).mkdir(exist_ok=True)
        
        # Add SEO-optimized images to content
        content_with_images = self.add_images_to_content(content, content_idea)
        
        # Save to file
        file_path = Path(self.content_dir) / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_with_images)
        
        return str(file_path)
    
    def publish_to_wordpress(self, file_path: str) -> bool:
        """Publish blog post to WordPress with clean content"""
        
        if not self.load_credentials():
            print("❌ Failed to load WordPress credentials")
            return False
        
        # Parse the markdown file
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
        
        # Convert cleaned markdown to HTML
        html_content = markdown.markdown(cleaned_markdown, extensions=['extra', 'codehilite'])
        
        # Prepare WordPress post data
        post_data = {
            'title': metadata.get('title', 'AI Marketing Insights'),
            'content': html_content,
            'status': 'publish',  # Try to publish first
            'excerpt': metadata.get('excerpt', metadata.get('description', '')),
        }
        
        # Add categories and tags
        categories = metadata.get('categories', [])
        if categories:
            post_data['categories'] = self._get_category_ids(categories)
        
        tags = metadata.get('tags', [])
        if tags:
            post_data['tags'] = self._get_tag_ids(tags)
        
        # Set featured image if available
        featured_image = metadata.get('featured_image')
        if featured_image and isinstance(featured_image, dict):
            featured_media_id = self._upload_featured_image(featured_image)
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
        
        # Publish to WordPress with fallback to draft
        try:
            print(f"📤 Attempting to publish post: {post_data['title']}")
            response = requests.post(f"{self.api_url}/posts", 
                                   headers=self.headers, 
                                   json=post_data,
                                   timeout=60)
            
            if response.status_code == 201:
                post_id = response.json()['id']
                post_url = response.json().get('link', '')
                print(f"✅ Post published successfully!")
                print(f"📝 Post ID: {post_id}")
                print(f"🌐 URL: {post_url}")
                return True
            elif response.status_code in [401, 403]:
                # Permission issue - try as draft instead
                print(f"⚠️ Permission denied for publishing (status: {response.status_code})")
                print(f"🔄 Retrying as draft...")
                
                post_data['status'] = 'draft'
                draft_response = requests.post(f"{self.api_url}/posts", 
                                             headers=self.headers, 
                                             json=post_data,
                                             timeout=60)
                
                if draft_response.status_code == 201:
                    post_id = draft_response.json()['id']
                    post_url = draft_response.json().get('link', '')
                    print(f"✅ Post saved as draft successfully!")
                    print(f"📝 Post ID: {post_id}")
                    print(f"🌐 URL: {post_url}")
                    print(f"💡 Note: Post saved as draft due to publishing permissions")
                    return True
                else:
                    print(f"❌ Failed to save as draft: {draft_response.status_code}")
                    print(f"Response: {draft_response.text}")
                    return False
            else:
                print(f"❌ Failed to publish post: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error publishing post: {e}")
            return False
    
    def _get_category_ids(self, categories: List[str]) -> List[int]:
        """Get or create category IDs"""
        category_ids = []
        
        for category_name in categories:
            try:
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
    
    def create_and_publish_post(self):
        """Create and publish a new blog post"""
        
        print(f"\n🚀 Creating new blog post at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            if self.use_research_llm:
                # Use research-enhanced LLM for content generation
                print("🌐🤖 Using Research-Enhanced LLM for content generation...")
                topic = self.enhanced_research.generate_random_research_topic()
                post_data = self.enhanced_research.create_comprehensive_research_content(
                    topic=topic,
                    use_local_llm=True,
                    llm_provider="deepseek"
                )
                
                if not post_data:
                    print("❌ Research LLM failed, falling back to template generation")
                    self.use_research_llm = False
                    return self.create_and_publish_post()
                
                print(f"📝 Topic: {post_data['title']}")
                
                # Save research-enhanced content
                file_path = self.enhanced_research.save_enhanced_content(post_data, self.content_dir)
                print(f"💾 Saved to: {file_path}")
                print(f"💰 Cost: {post_data['metadata']['generation_cost']}")
                print(f"📊 Research sources: {post_data['metadata']['data_sources']}")
                print(f"📈 Statistics: {post_data['metadata']['statistics_verified']}")
                
            elif self.use_local_llm:
                # Use local LLM for content generation
                print("🤖 Using Local LLM for content generation...")
                topic = random.choice(self.topics)
                post_data = self.local_llm.generate_blog_post_with_local_llm(topic)
                
                if not post_data:
                    print("❌ Local LLM failed, falling back to template generation")
                    self.use_local_llm = False
                    return self.create_and_publish_post()
                
                print(f"📝 Topic: {post_data['title']}")
                
                # Save local LLM generated content
                file_path = self.local_llm.save_local_llm_post(post_data, self.content_dir)
                print(f"💾 Saved to: {file_path}")
                print(f"💰 Cost: $0.00 (Local LLM)")
                
            else:
                # Use template-based generation
                print("📝 Using template-based content generation...")
                content_idea = self.generate_content_idea()
                print(f"📝 Topic: {content_idea['title']}")
                
                # Create blog post content
                content = self.create_blog_post(content_idea)
                
                # Save to file
                file_path = self.save_blog_post(content, content_idea['filename'], content_idea)
                print(f"💾 Saved to: {file_path}")
            
            # Publish to WordPress
            if self.publish_to_wordpress(file_path):
                if self.use_research_llm or self.use_local_llm:
                    title = post_data['title']
                else:
                    title = content_idea['title']
                print(f"🎉 Successfully published: {title}")
                return True
            else:
                if self.use_research_llm or self.use_local_llm:
                    title = post_data['title']
                else:
                    title = content_idea['title']
                print(f"❌ Failed to publish: {title}")
                return False
                
        except Exception as e:
            print(f"❌ Error in content creation process: {e}")
            return False
    
    def create_and_publish_custom_post(self, custom_topic: str):
        """Create and publish a blog post with a custom topic"""
        
        print(f"\n🚀 Creating custom blog post at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📝 Custom Topic: {custom_topic}")
        
        try:
            if self.use_research_llm:
                # Use research-enhanced LLM for content generation
                print("🌐🤖 Using Research-Enhanced LLM for custom topic...")
                post_data = self.enhanced_research.create_comprehensive_research_content(
                    topic=custom_topic,
                    use_local_llm=True,
                    llm_provider="deepseek"
                )
                
                if not post_data:
                    print("❌ Research LLM failed, falling back to template generation")
                    self.use_research_llm = False
                    return self.create_and_publish_custom_post(custom_topic)
                
                print(f"📝 Generated Title: {post_data['title']}")
                
                # Save research-enhanced content
                file_path = self.enhanced_research.save_enhanced_content(post_data, self.content_dir)
                print(f"💾 Saved to: {file_path}")
                print(f"💰 Cost: {post_data['metadata']['generation_cost']}")
                print(f"📊 Research sources: {post_data['metadata']['data_sources']}")
                
            elif self.use_local_llm:
                # Use local LLM for content generation
                print("🤖 Using Local LLM for custom topic...")
                post_data = self.local_llm.generate_blog_post_with_local_llm(custom_topic)
                
                if not post_data:
                    print("❌ Local LLM failed, falling back to template generation")
                    self.use_local_llm = False
                    return self.create_and_publish_custom_post(custom_topic)
                
                print(f"📝 Generated Title: {post_data['title']}")
                
                # Save local LLM generated content
                file_path = self.local_llm.save_local_llm_post(post_data, self.content_dir)
                print(f"💾 Saved to: {file_path}")
                print(f"💰 Cost: $0.00 (Local LLM)")
                
            else:
                # Use template-based generation with custom topic
                print("📝 Using template-based generation for custom topic...")
                
                # Create custom content idea
                template_type = "trend_analysis"  # Default template
                template = self.content_templates[template_type]
                
                # Generate title from custom topic
                title = template["title_format"].format(
                    topic=custom_topic,
                    year=datetime.now().year
                )
                
                # Generate filename
                filename = title.lower().replace(" ", "-").replace(":", "").replace(",", "")
                filename = "".join(c for c in filename if c.isalnum() or c in "-_")
                filename = f"{filename}-{datetime.now().strftime('%Y-%m-%d')}.md"
                
                content_idea = {
                    "title": title,
                    "topic": custom_topic,
                    "template_type": template_type,
                    "template": template,
                    "filename": filename,
                    "sections": [section.format(topic=custom_topic) for section in template["sections"]]
                }
                
                print(f"📝 Generated Title: {title}")
                
                # Create blog post content
                content = self.create_blog_post(content_idea)
                
                # Save to file
                file_path = self.save_blog_post(content, content_idea['filename'], content_idea)
                print(f"💾 Saved to: {file_path}")
            
            # Publish to WordPress
            if self.publish_to_wordpress(file_path):
                if self.use_research_llm or self.use_local_llm:
                    title = post_data['title']
                else:
                    title = content_idea['title']
                print(f"🎉 Successfully published custom post: {title}")
                return True
            else:
                if self.use_research_llm or self.use_local_llm:
                    title = post_data['title']
                else:
                    title = content_idea['title']
                print(f"❌ Failed to publish custom post: {title}")
                return False
                
        except Exception as e:
            print(f"❌ Error in custom content creation process: {e}")
            return False
    
    def run_continuous_publishing(self):
        """Run continuous content publishing"""
        
        # Get publishing interval from config or environment
        interval = int(os.getenv("PUBLISH_INTERVAL") or self._load_config_value("publish_interval") or 5)
        
        print("🤖 Starting Automated Content Creation & Publishing System")
        print("=" * 60)
        print(f"📅 Schedule: New post every {interval} minutes")
        print(f"🌐 Target: {self.site_url}")
        print(f"📁 Content Directory: {self.content_dir}")
        print("=" * 60)
        
        # Schedule posts with dynamic interval
        schedule.every(interval).minutes.do(self.create_and_publish_post)
        
        # Create first post immediately
        self.create_and_publish_post()
        
        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main function"""
    system = AutoContentSystem()
    
    print("🚀 Automated Content Creation & Publishing System")
    print("=" * 50)
    print("1. Create and publish one post now (Template-based)")
    print("2. Create and publish one post now (Local LLM)")
    print("3. Start continuous publishing (Template-based)")
    print("4. Start continuous publishing (Local LLM)")
    print("5. Test local LLM connection")
    print("6. Exit")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == '1':
        system.disable_local_llm()
        system.create_and_publish_post()
    elif choice == '2':
        if system.enable_local_llm():
            system.create_and_publish_post()
        else:
            print("❌ Local LLM not available. Install Ollama and DeepSeek first.")
            from core.local_llm_content import setup_deepseek_ollama
            setup_deepseek_ollama()
    elif choice == '3':
        system.disable_local_llm()
        system.run_continuous_publishing()
    elif choice == '4':
        if system.enable_local_llm():
            system.run_continuous_publishing()
        else:
            print("❌ Local LLM not available")
    elif choice == '5':
        providers = ["deepseek", "ollama", "llamacpp"]
        print("\nTesting local LLM connections...")
        for provider in providers:
            if system.local_llm.test_connection(provider):
                print(f"✅ {provider}: Connected")
            else:
                print(f"❌ {provider}: Not available")
    elif choice == '6':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 