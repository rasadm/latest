#!/usr/bin/env python3
"""
Claude Content Generator
Integrates with Anthropic's Claude API for high-quality content creation
"""

import requests
import json
import random
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

class ClaudeContentGenerator:
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY', '')
        self.api_url = "https://api.anthropic.com/v1/messages"
        # Use Claude 3.5 Sonnet as default (best balance of performance and cost)
        self.model = "claude-sonnet-4-20250514"  # Claude Sonnet 4 - Latest and most advanced
        self.max_tokens = 8000  # Increased for better content generation
        
        # Available Claude models (using correct model names)
        self.available_models = {
            "claude-sonnet-4": "claude-sonnet-4-20250514",      # $3/$15 per MTok - Latest Sonnet 4
            "claude-4-sonnet": "claude-sonnet-4-20250514",      # Alias for compatibility
            "claude-opus-4": "claude-opus-4-20250514",          # $15/$75 per MTok - Most powerful
            "claude-3.5-sonnet": "claude-3-5-sonnet-20241022",  # $3/$15 per MTok - Previous stable
            "claude-3-5-sonnet": "claude-3-5-sonnet-20241022",  # Alias for compatibility
            "claude-3.5-sonnet-old": "claude-3-5-sonnet-20240620",  # $3/$15 per MTok - Previous
            "claude-3-haiku": "claude-3-haiku-20240307"         # $0.25/$1.25 per MTok - Fast & cheap
        }
        
        # Load content topics from config
        self.topics = self._load_topics_config()
    
    def _load_topics_config(self):
        """Load topics configuration from file with fallback defaults"""
        config_file = "claude_topics_config.json"
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get("topics", self._get_default_topics())
        except Exception as e:
            print(f"Warning: Could not load Claude topics config: {e}")
        
        # Return default topics as fallback
        return self._get_default_topics()
    
    def _get_default_topics(self):
        """Get default topics list"""
        return [
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
            "Real-time Personalization Strategies",
            "AI-Driven Customer Journey Mapping",
            "Marketing Mix Modeling with AI",
            "Sentiment Analysis in Brand Management",
            "AI Ethics in Marketing"
        ]
    
    def set_model(self, model_name: str):
        """Set the Claude model to use"""
        if model_name in self.available_models:
            self.model = self.available_models[model_name]
            print(f"✅ Claude model set to: {self.model}")
        else:
            print(f"❌ Unknown model: {model_name}")
            print(f"Available models: {list(self.available_models.keys())}")
    
    def set_api_key(self, api_key: str):
        """Set the Anthropic API key"""
        self.api_key = api_key
        os.environ['ANTHROPIC_API_KEY'] = api_key
    
    def test_connection(self) -> bool:
        """Test connection to Claude API"""
        if not self.api_key:
            print("❌ No Anthropic API key found. Set ANTHROPIC_API_KEY environment variable.")
            return False
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json={
                    "model": self.model,
                    "max_tokens": 50,
                    "messages": [
                        {"role": "user", "content": "Hello, are you working?"}
                    ]
                },
                timeout=30  # Increased timeout for connection test
            )
            
            if response.status_code == 200:
                print("✅ Claude connection successful")
                return True
            else:
                print(f"❌ Claude API error: {response.status_code}")
                return False
            
        except Exception as e:
            print(f"❌ Claude connection failed: {e}")
            return False
    
    def generate_content_with_claude(self, topic: str, keyword: str = None, target_audience: str = "Marketing professionals") -> str:
        """Generate content using Claude API with retry logic"""
        
        if not self.api_key:
            print("❌ No Anthropic API key found")
            return None
        
        # Use topic as keyword if no specific keyword provided
        if not keyword:
            keyword = topic
        
        prompt = self.create_content_prompt(topic, keyword, target_audience)
        
        # Retry configuration
        max_retries = 3
        timeout_seconds = 180  # Increased to 3 minutes for long content
        
        for attempt in range(max_retries):
            try:
                print(f"🤖 Generating blog post with Claude: {topic} (Attempt {attempt + 1}/{max_retries})")
                
                headers = {
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
                
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json={
                        "model": self.model,
                        "max_tokens": self.max_tokens,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7
                    },
                    timeout=timeout_seconds
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("content", [])
                    if content and len(content) > 0:
                        print(f"✅ Content generated successfully on attempt {attempt + 1}")
                        return content[0].get("text", "")
                else:
                    print(f"❌ Claude API error: {response.status_code} - {response.text}")
                    if attempt < max_retries - 1:
                        print(f"🔄 Retrying in 5 seconds...")
                        import time
                        time.sleep(5)
                    continue
                
            except requests.exceptions.Timeout:
                print(f"⏰ Request timed out after {timeout_seconds} seconds (Attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    print(f"🔄 Retrying with shorter content request...")
                    # Use shorter prompt for retry attempts
                    prompt = self.create_short_content_prompt(topic, keyword, target_audience)
                    # Reduce max_tokens for retry attempts
                    self.max_tokens = max(4000, self.max_tokens - 1000)
                continue
                
            except Exception as e:
                print(f"❌ Error generating content with Claude: {e}")
                if attempt < max_retries - 1:
                    print(f"🔄 Retrying in 10 seconds...")
                    import time
                    time.sleep(10)
                continue
        
        print(f"❌ Failed to generate content after {max_retries} attempts")
        return None
    
    def create_content_prompt(self, topic: str, keyword: str, target_audience: str = "Marketing professionals") -> str:
        """Create comprehensive prompt for Claude content generation"""
        
        current_year = datetime.now().year
        
        return f"""You are an expert marketing content strategist and professional writer specializing in AI, technology, and digital marketing. Your task is to write a comprehensive, authoritative, and highly engaging 2500-word article about "{topic}" for {target_audience} and business leaders.

🎯 CONTENT OBJECTIVES:
- Create actionable, implementable strategies
- Provide real business value and ROI insights
- Include specific examples and case studies
- Write with authority and expertise
- Focus on practical application over theory
- Ensure content is scannable and engaging

📋 MANDATORY ARTICLE STRUCTURE:

# How to Master {topic.title()} in {current_year}: The Complete Strategic Guide

## Executive Summary (200 words)
Write a compelling executive summary that:
- Highlights the 3 most important findings about {keyword}
- States the primary business value proposition
- Mentions specific ROI potential or business outcomes
- Previews the key strategies covered in the article
- Creates urgency about why this matters now in {current_year}

## Current Market Landscape (500 words)

### Market Size and Growth Dynamics
- Analyze current {keyword} market conditions
- Reference specific growth rates, market size, or adoption statistics
- Discuss key market drivers and accelerators
- Identify market leaders and emerging players in {keyword}

### Competitive Environment
- Describe the competitive landscape for {keyword}
- Identify key differentiators in the market
- Analyze market positioning strategies
- Discuss barriers to entry and market consolidation

### Technology Maturation
- Assess current {keyword} technology readiness
- Evaluate integration capabilities and compatibility
- Discuss scalability and performance considerations
- Address security and compliance factors

## Strategic Implementation Framework (600 words)

### Phase 1: Foundation Building (200 words)
- Prerequisites and infrastructure requirements
- Team structure and skill requirements
- Initial budget considerations and resource allocation
- Timeline expectations and milestone planning

### Phase 2: Pilot Program Development (200 words)
- Proof of concept strategy and testing methodology
- Success metrics and KPI establishment
- Risk assessment and mitigation strategies
- Stakeholder engagement and communication plans

### Phase 3: Scale and Optimization (200 words)
- Scaling strategies and operational excellence
- Performance optimization and continuous improvement
- Advanced features and capability expansion
- Long-term strategic roadmap development

## Best Practices and Expert Insights (400 words)

### Industry Standards and Benchmarks
- Performance benchmarks and industry standards
- Quality assurance and testing protocols
- Documentation and knowledge management
- Training and skill development programs

### Common Pitfalls and How to Avoid Them
- Typical implementation challenges and solutions
- Budget overruns and scope creep prevention
- Technical debt and maintenance considerations
- Change management and adoption strategies

## Practical Tools and Resources (300 words)

### Essential Tools and Platforms
- Recommended tools and software solutions
- Integration requirements and compatibility
- Cost considerations and ROI calculations
- Implementation timelines and complexity

### Templates and Frameworks
- Ready-to-use templates and checklists
- Decision-making frameworks and evaluation criteria
- Project management tools and methodologies
- Measurement and reporting templates

## Future Trends and Predictions (300 words)

### Emerging Technologies and Innovations
- Next-generation capabilities and features
- Integration with emerging technologies
- Market evolution and disruption potential
- Investment and funding trends

### Strategic Positioning for the Future
- Competitive advantage development
- Future skill requirements and capabilities
- Market positioning and differentiation
- Long-term strategic planning

## Actionable Next Steps (200 words)

### Immediate Actions (Next 30 Days)
- Quick wins and immediate value creation
- Assessment and evaluation activities
- Team preparation and skill development
- Initial budget and resource planning

### Medium-term Objectives (Next 90 Days)
- Pilot program development and launch
- Stakeholder engagement and buy-in
- Technology evaluation and selection
- Process development and optimization

### Long-term Goals (Next 12 Months)
- Full-scale implementation and rollout
- Performance optimization and scaling
- Advanced feature development
- Strategic partnership and collaboration

Remember to:
- Use data-driven insights throughout
- Include specific, actionable recommendations
- Provide real-world examples and case studies
- Focus on practical implementation
- Address common challenges and solutions
- Maintain professional, authoritative tone
- Ensure content is comprehensive yet accessible"""
    
    def generate_blog_post_with_claude(self, topic: str, keyword: str = None, target_audience: str = "Marketing professionals", custom_prompt: str = None) -> Dict:
        """Generate a complete blog post using Claude"""
        
        print(f"🤖 Generating blog post with Claude: {topic}")
        
        # Use custom prompt if provided, otherwise use default
        if custom_prompt:
            print("📊 Using research-enhanced prompt")
            content = self.generate_content_with_custom_prompt(custom_prompt)
        else:
            content = self.generate_content_with_claude(topic, keyword, target_audience)
        
        if not content:
            print("❌ Failed to generate content with Claude")
            return None
        
        # Extract title from content if using custom prompt (multilingual support)
        title = topic  # fallback
        if custom_prompt and content:
            # Look for title in the generated content
            lines = content.split('\n')
            for line in lines[:5]:  # Check first 5 lines
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
                elif line.strip() and not line.startswith('**') and len(line.strip()) > 10:
                    # If no markdown title found, use first substantial line
                    title = line.strip()
                    break
        
        # If still using fallback, generate title based on context
        if title == topic and not custom_prompt:
            title = self.generate_title(topic)
        
        # Create post structure
        post_data = {
            "title": title,
            "content": content,
            "excerpt": self.generate_excerpt(content),
            "tags": self.generate_tags(topic),
            "meta_description": self.generate_meta_description(topic),
            "image_keywords": self.generate_image_keywords(topic),
            "word_count": len(content.split()),
            "generation_method": "claude",
            "topic": topic,
            "keyword": keyword or topic,
            "target_audience": target_audience,
            "estimated_cost": self.estimate_cost(content),
            "seo_keywords": [keyword or topic] + self.generate_tags(topic)[:3]
        }
        
        print(f"✅ Generated {post_data['word_count']} words")
        return post_data
    
    def generate_title(self, topic: str) -> str:
        """Generate SEO-optimized title"""
        title_templates = [
            f"{topic}: 2025 Trends and Predictions for Modern Marketers",
            f"How {topic} is Transforming Marketing in 2025",
            f"The Complete Guide to {topic} for Marketing Success",
            f"{topic}: Strategies, Tools, and Best Practices for 2025",
            f"Mastering {topic}: A Marketing Leader's Guide to Success"
        ]
        return random.choice(title_templates)
    
    def generate_excerpt(self, content: str) -> str:
        """Generate excerpt from content"""
        sentences = content.split('.')[:3]
        excerpt = '. '.join(sentences) + '.'
        return excerpt[:200] + "..." if len(excerpt) > 200 else excerpt
    
    def generate_tags(self, topic: str) -> List[str]:
        """Generate relevant tags"""
        # Load base tags from config or use defaults
        default_base_tags = ["AI Marketing", "Marketing Technology", "Digital Marketing", "Marketing Automation"]
        base_tags = os.getenv("DEFAULT_TAGS", "").split(",") or self._load_config_value("base_tags") or default_base_tags
        
        # Clean tags if they came from environment variable
        if isinstance(base_tags, list) and len(base_tags) == 1 and "," in base_tags[0]:
            base_tags = [tag.strip() for tag in base_tags[0].split(",")]
        
        topic_words = topic.lower().split()
        topic_tags = [word.capitalize() for word in topic_words if len(word) > 3]
        return base_tags + topic_tags[:3]
    
    def _load_config_value(self, key):
        """Load a configuration value from the config file"""
        try:
            config_file = "claude_topics_config.json"
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return config.get(key)
        except Exception as e:
            print(f"Warning: Could not load config value '{key}': {e}")
        return None
    
    def generate_meta_description(self, topic: str) -> str:
        """Generate SEO meta description"""
        return f"Discover the latest {topic.lower()} trends, strategies, and best practices for modern marketers. Expert insights and actionable tips for 2025."
    
    def generate_image_keywords(self, topic: str) -> List[str]:
        """Generate keywords for featured image search"""
        keywords = [
            f"{topic.lower()} marketing",
            "AI marketing technology",
            "digital marketing strategy",
            "marketing automation",
            "business technology"
        ]
        return keywords
    
    def estimate_cost(self, content: str) -> float:
        """Estimate cost based on content length and model"""
        # Rough token estimation (1 token ≈ 4 characters)
        input_tokens = 1000  # Approximate prompt tokens
        output_tokens = len(content) // 4
        
        # Claude 4 pricing per million tokens
        if "claude-sonnet-4" in self.model:
            input_cost = (input_tokens / 1_000_000) * 3.00    # $3 per MTok
            output_cost = (output_tokens / 1_000_000) * 15.00  # $15 per MTok
        elif "claude-3.7-sonnet" in self.model:
            input_cost = (input_tokens / 1_000_000) * 3.00    # $3 per MTok
            output_cost = (output_tokens / 1_000_000) * 15.00  # $15 per MTok
        else:  # Claude 3.5 Sonnet (legacy)
            input_cost = (input_tokens / 1_000_000) * 3.00    # $3 per MTok
            output_cost = (output_tokens / 1_000_000) * 15.00  # $15 per MTok
        
        return round(input_cost + output_cost, 4)
    
    def save_claude_post(self, post_data: Dict, content_dir: str = "serie 1") -> str:
        """Save Claude-generated post to file"""
        
        # Create filename
        title_slug = post_data["title"].lower().replace(" ", "-").replace(":", "").replace(",", "")
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{title_slug}-{date_str}.md"
        
        # Ensure directory exists
        Path(content_dir).mkdir(exist_ok=True)
        
        # Create markdown content
        markdown_content = f"""# {post_data['title']}

**Generated with Claude on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**
**Model:** {post_data.get('model_used', 'claude-3-5-sonnet')}
**Word Count:** {post_data.get('word_count', 0)}
**Estimated Cost:** ${post_data.get('cost_estimate', 0):.4f}

## Meta Information
- **Category:** {post_data['category']}
- **Tags:** {', '.join(post_data['tags'])}
- **Meta Description:** {post_data['meta_description']}
- **Featured Image Keywords:** {', '.join(post_data['featured_image_keywords'])}

## Excerpt
{post_data['excerpt']}

---

## Content

{post_data['content']}

---

*Generated using Claude AI for AgenticAI Updates*
"""
        
        # Save to file
        filepath = Path(content_dir) / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"💾 Claude post saved: {filepath}")
        return str(filepath)
    
    def generate_content_with_custom_prompt(self, prompt: str) -> str:
        """Generate content using a custom prompt"""
        
        if not self.api_key:
            print("❌ No Anthropic API key found")
            return None
        
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json={
                    "model": self.model,
                    "max_tokens": self.max_tokens,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("content", [])
                if content and len(content) > 0:
                    return content[0].get("text", "")
            else:
                print(f"❌ Claude API error: {response.status_code} - {response.text}")
                return None
            
        except Exception as e:
            print(f"❌ Error generating content with Claude: {e}")
            return None
    
    def create_short_content_prompt(self, topic: str, keyword: str, target_audience: str = "Marketing professionals") -> str:
        """Create a shorter prompt for faster generation when timeouts occur"""
        
        current_year = datetime.now().year
        
        return f"""You are an expert marketing content writer. Write a comprehensive 1500-word article about "{topic}" for {target_audience}.

# {topic.title()}: Complete Guide for {current_year}

## Introduction
Write an engaging introduction that explains what {keyword} is and why it matters for businesses in {current_year}.

## Key Benefits and Applications
- List 5-7 main benefits of {keyword}
- Provide specific examples and use cases
- Include practical applications for businesses

## Implementation Strategy
- Step-by-step approach to implementing {keyword}
- Best practices and common pitfalls to avoid
- Timeline and resource requirements

## Current Trends and Future Outlook
- Latest developments in {keyword} for {current_year}
- Emerging trends and technologies
- Predictions for the next 2-3 years

## Conclusion and Next Steps
- Summarize key takeaways
- Provide actionable next steps
- Include a compelling call-to-action

Requirements:
- Write exactly 1500 words
- Use professional, authoritative tone
- Include specific examples and data points
- Make content actionable and practical
- Optimize for SEO with natural keyword usage
- Structure with clear headings and subheadings"""

    def create_project_aware_prompt(self, project_data: Dict, keyword: str, research_data: Dict = None) -> str:
        """Create project-aware prompt that leverages project context for dynamic content generation"""
        
        project_name = project_data.get('name', 'Content Project')
        project_description = project_data.get('description', '')
        language = project_data.get('language', 'english')
        target_audience = project_data.get('target_audience', 'Marketing professionals')
        content_length = project_data.get('content_length', 'medium')
        seo_focus = project_data.get('seo_focus', [])
        
        # Word count mapping
        word_count_map = {
            'short': 1500,
            'medium': 2500,
            'long': 3500
        }
        target_words = word_count_map.get(content_length, 2500)
        
        # Research context
        research_context = ""
        if research_data:
            if research_data.get('key_insights'):
                research_context += "\n🔍 VERIFIED MARKET INSIGHTS:\n"
                for i, insight in enumerate(research_data['key_insights'][:5], 1):
                    research_context += f"{i}. {insight}\n"
            
            if research_data.get('statistics'):
                research_context += "\n📊 VERIFIED DATA POINTS:\n"
                for i, stat in enumerate(research_data['statistics'][:5], 1):
                    value = stat.get('value', 'Market trend')
                    context = stat.get('context', 'industry development')
                    research_context += f"{i}. {value}: {context}\n"
        
        # Language-specific prompts
        if language == 'farsi':
            return f"""شما یک استراتژیست محتوای خبره هستید که بر روی پروژه "{project_name}" کار می‌کنید.

جزئیات پروژه:
- نام پروژه: {project_name}
- توضیحات: {project_description}
- موضوع اصلی: {keyword}
- مخاطب هدف: {target_audience}
- هدف کلمات: {target_words} کلمه
- تمرکز سئو: {', '.join(seo_focus) if seo_focus else keyword}

{research_context}

ماموریت خلاقانه:
مقاله‌ای استثنایی درباره "{keyword}" بنویسید که برای {target_audience} ارزش منحصر به فرد داشته باشد.

آزادی خلاقانه شما:
✅ ساختار منحصر به فرد بر اساس نیاز موضوع
✅ استفاده از داستان‌گویی و مثال‌های جذاب
✅ بینش‌های عملی برای {target_audience}
✅ سرتیترهای خلاقانه و طبیعی
✅ استراتژی‌های قابل اجرا

محدودیت‌های سخت:
❌ هیچ آمار ساختگی یا مثال شرکت جعلی
❌ هیچ قالب سفت و سخت
❌ هیچ پر کردن کلیدواژه
❌ هیچ ساختار عمومی مقدمه-بدنه-نتیجه

دقیقاً {target_words} کلمه محتوای جامع و اصیل ایجاد کنید."""

        elif language == 'spanish':
            return f"""Usted es un estratega de contenido experto trabajando en el proyecto "{project_name}".

Detalles del Proyecto:
- Nombre del Proyecto: {project_name}
- Descripción: {project_description}
- Tema Principal: {keyword}
- Audiencia Objetivo: {target_audience}
- Meta de Palabras: {target_words} palabras
- Enfoque SEO: {', '.join(seo_focus) if seo_focus else keyword}

{research_context}

Misión Creativa:
Cree un artículo excepcional sobre "{keyword}" que proporcione valor único para {target_audience}.

Su Libertad Creativa:
✅ Estructura única basada en las necesidades del tema
✅ Use narrativa y ejemplos atractivos
✅ Perspectivas prácticas para {target_audience}
✅ Encabezados creativos y naturales
✅ Estrategias accionables

Límites Estrictos:
❌ NO estadísticas fabricadas o ejemplos de empresas falsas
❌ NO plantillas rígidas
❌ NO saturación de palabras clave
❌ NO estructura genérica introducción-cuerpo-conclusión

Cree exactamente {target_words} palabras de contenido integral y original."""

        else:  # English
            return f"""You are an expert content strategist working on the project "{project_name}".

Project Details:
- Project Name: {project_name}
- Description: {project_description}
- Primary Topic: {keyword}
- Target Audience: {target_audience}
- Word Goal: {target_words} words
- SEO Focus: {', '.join(seo_focus) if seo_focus else keyword}

{research_context}

Creative Mission:
Create an exceptional article about "{keyword}" that provides unique value for {target_audience}.

Your Creative Freedom:
✅ Design unique structure based on topic needs
✅ Use storytelling and engaging examples
✅ Provide practical insights for {target_audience}
✅ Create natural, creative headers
✅ Include actionable strategies

Strict Boundaries:
❌ NO fabricated statistics or fake company examples
❌ NO rigid templates
❌ NO keyword stuffing
❌ NO generic introduction-body-conclusion structure

Create exactly {target_words} words of comprehensive, original content."""

def setup_claude_api():
    """Setup guide for Claude API"""
    print("""
🤖 Claude API Setup Guide:

1. Get API Key:
   - Visit: https://console.anthropic.com/
   - Create account and get API key
   - Add billing information (pay-per-use)

2. Set Environment Variable:
   - Windows: set ANTHROPIC_API_KEY=your_api_key_here
   - Linux/Mac: export ANTHROPIC_API_KEY=your_api_key_here

3. Pricing (approximate):
   - Claude 3.5 Sonnet: $3 per million input tokens
   - Typical blog post: ~$0.01-0.03 per post
   - Much higher quality than local models

4. Test Connection:
   - Run this script to test your setup
   - Ensure API key is properly configured
""")

def main():
    """Test Claude content generation"""
    generator = ClaudeContentGenerator()
    
    # Test connection
    if not generator.test_connection():
        setup_claude_api()
        return
    
    # Generate test content
    topic = "AI-Powered Customer Segmentation"
    post = generator.generate_blog_post_with_claude(topic)
    
    if post:
        print(f"✅ Successfully generated post: {post['title']}")
        print(f"📊 Word count: {post['word_count']}")
        print(f"💰 Estimated cost: ${post['cost_estimate']:.4f}")
        
        # Save post
        filepath = generator.save_claude_post(post)
        print(f"💾 Saved to: {filepath}")
    else:
        print("❌ Failed to generate post")

if __name__ == "__main__":
    main() 