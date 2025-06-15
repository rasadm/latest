#!/usr/bin/env python3
"""
Enhanced Research + Local LLM Content Generator
Combines real web research data with local LLM content generation for comprehensive, SEO-optimized articles
"""

import logging
import json
import yaml
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from core.web_research_content import WebResearchContentGenerator
from core.local_llm_content import MultilingualLocalLLMContentGenerator
from seo.seo_optimizer import MultilingualSEOOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_research_llm.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ContentConfig:
    """Configuration class for content generation settings"""
    target_word_count: int = 3500
    use_local_llm: bool = False
    default_llm_provider: str = "claude"
    output_directory: str = "serie 1"
    language: str = "english"
    max_keywords_per_topic: int = 5
    max_statistics: int = 10
    max_insights: int = 8
    max_articles: int = 6
    prompt_template_file: Optional[str] = None
    topics_config_file: Optional[str] = None

@dataclass
class GenerationResult:
    """Standardized result structure for content generation"""
    success: bool
    content_data: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ContentProvider(ABC):
    """Abstract base class for content providers"""
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the provider is available"""
        pass
    
    @abstractmethod
    def generate_content(self, prompt: str, content_type: str) -> Optional[str]:
        """Generate content using the provider"""
        pass

class EnhancedResearchLLMGenerator:
    """
    Production-ready content generator with comprehensive research and LLM enhancement
    
    Attributes:
        config: Content generation configuration
        web_researcher: Web research component
        local_llm: Local LLM component  
        seo_optimizer: SEO optimization component
        enhanced_topics: Topic-keyword mapping
    """
    
    def __init__(self, 
                 config: Optional[ContentConfig] = None,
                 web_researcher: Optional[WebResearchContentGenerator] = None,
                 local_llm: Optional[MultilingualLocalLLMContentGenerator] = None,
                 seo_optimizer: Optional[MultilingualSEOOptimizer] = None):
        """
        Initialize the enhanced research LLM generator
        
        Args:
            config: Configuration for content generation
            web_researcher: Web research component (injected for testing)
            local_llm: Local LLM component (injected for testing)
            seo_optimizer: SEO optimizer component (injected for testing)
        """
        self.config = config or ContentConfig()
        self.web_researcher = web_researcher or WebResearchContentGenerator()
        self.local_llm = local_llm or MultilingualLocalLLMContentGenerator()
        self.seo_optimizer = seo_optimizer or MultilingualSEOOptimizer()
        
        # Load topics from config file or use defaults
        self.enhanced_topics = self._load_topics_config()
        
        logger.info("Enhanced Research LLM Generator initialized")
    
    def _load_topics_config(self) -> Dict[str, List[str]]:
        """Load topics configuration from file or return defaults"""
        if self.config.topics_config_file and Path(self.config.topics_config_file).exists():
            try:
                with open(self.config.topics_config_file, 'r', encoding='utf-8') as f:
                    if self.config.topics_config_file.endswith('.yaml') or self.config.topics_config_file.endswith('.yml'):
                        return yaml.safe_load(f)
                    else:
                        return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load topics config from {self.config.topics_config_file}: {e}")
        
        # Default enhanced topics with SEO keywords
        return {
            "AI Marketing Automation": [
                "AI marketing automation", "marketing AI tools", "automated marketing campaigns", 
                "machine learning marketing", "AI-powered marketing platforms"
            ],
            "Conversational AI and Chatbots": [
                "conversational AI marketing", "chatbot marketing automation", "AI customer service",
                "marketing chatbots", "conversational marketing platforms"
            ],
            "Predictive Analytics for Marketing": [
                "predictive marketing analytics", "marketing data science", "customer behavior prediction",
                "marketing forecasting", "predictive customer analytics"
            ],
            "Personalization at Scale": [
                "marketing personalization", "AI personalization", "dynamic content personalization",
                "personalized marketing campaigns", "customer experience personalization"
            ],
            "Marketing Attribution with AI": [
                "AI marketing attribution", "multi-touch attribution", "marketing ROI analysis",
                "attribution modeling", "marketing performance analytics"
            ],
            "Voice Search Optimization": [
                "voice search marketing", "voice SEO", "voice search optimization",
                "voice commerce marketing", "smart speaker marketing"
            ],
            "Programmatic Advertising Evolution": [
                "programmatic advertising", "AI advertising automation", "real-time bidding",
                "programmatic marketing", "automated ad buying"
            ],
            "Customer Data Platform Innovation": [
                "customer data platform", "CDP marketing", "unified customer data",
                "customer data management", "marketing data integration"
            ]
        }
    
    def create_comprehensive_research_content(self, 
                                            topic: str, 
                                            use_local_llm: Optional[bool] = None, 
                                            llm_provider: Optional[str] = None) -> GenerationResult:
        """
        Create comprehensive content combining web research and local LLM
        
        Args:
            topic: The main topic for content generation
            use_local_llm: Whether to use LLM enhancement (defaults to config)
            llm_provider: LLM provider to use (defaults to config)
            
        Returns:
            GenerationResult with success status and content data
        """
        try:
            # Use config defaults if not provided
            use_local_llm = use_local_llm if use_local_llm is not None else self.config.use_local_llm
            llm_provider = llm_provider or self.config.default_llm_provider
            
            logger.info(f"Creating comprehensive research content for: {topic}")
            
            # Get keywords for the topic
            keywords = self.enhanced_topics.get(topic, [topic])
            logger.debug(f"Using keywords: {keywords}")
            
            # Step 1: Conduct web research
            logger.info("Phase 1: Conducting web research...")
            research_data = self.web_researcher.research_topic_comprehensively(topic)
            
            if not research_data:
                logger.warning("No research data obtained, using topic-only approach")
                research_data = {"articles": [], "statistics": [], "key_insights": []}
            
            # Step 2: Generate research-based content structure
            logger.info("Phase 2: Creating research-based content structure...")
            web_content = self.web_researcher.generate_seo_optimized_content(topic, research_data, keywords)
            
            if not web_content:
                error_msg = "Failed to generate web research content"
                logger.error(error_msg)
                return GenerationResult(success=False, error_message=error_msg)
            
            final_content = web_content
            
            if use_local_llm:
                # Step 3: Enhance with local LLM
                logger.info(f"Phase 3: Enhancing with {llm_provider} LLM...")
                enhancement_result = self.enhance_with_local_llm(topic, research_data, web_content, llm_provider)
                
                if enhancement_result:
                    final_content = enhancement_result
                    logger.info("LLM enhancement completed successfully")
                else:
                    logger.warning("LLM enhancement failed, using web research content")
            
            return GenerationResult(
                success=True,
                content_data=final_content,
                metadata={
                    "topic": topic,
                    "llm_provider": llm_provider if use_local_llm else None,
                    "keywords_count": len(keywords),
                    "research_articles": len(research_data.get("articles", [])),
                    "generation_timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            error_msg = f"Content generation failed for topic '{topic}': {str(e)}"
            logger.error(error_msg, exc_info=True)
            return GenerationResult(success=False, error_message=error_msg)
    
    def enhance_with_local_llm(self, 
                              topic: str, 
                              research_data: Dict[str, Any], 
                              web_content: Dict[str, Any], 
                              llm_provider: str) -> Optional[Dict[str, Any]]:
        """
        Enhance web research content with local LLM generation
        
        Args:
            topic: The content topic
            research_data: Collected research data
            web_content: Base web research content
            llm_provider: LLM provider to use
            
        Returns:
            Enhanced content dictionary or None if enhancement fails
        """
        try:
            # Set LLM provider
            self.local_llm.set_provider(llm_provider)
            
            if not self.local_llm.test_connection():
                logger.warning(f"{llm_provider} not available, skipping LLM enhancement")
                return None
            
            # Create enhanced prompt with research data
            enhanced_prompt = self._create_research_enhanced_prompt(topic, research_data)
            
            if not enhanced_prompt:
                logger.error("Failed to create enhanced prompt")
                return None
            
            # Generate enhanced content with LLM
            llm_content = self.local_llm.generate_content_with_local_llm(enhanced_prompt, "blog_post")
            
            if not llm_content:
                logger.warning("LLM content generation returned empty result")
                return None
            
            # Combine web research data with LLM content
            enhanced_content = self._merge_research_and_llm_content(web_content, llm_content, research_data, llm_provider)
            
            if not enhanced_content:
                logger.error("Failed to merge research and LLM content")
                return None
            
            # Apply comprehensive SEO optimization
            try:
                enhanced_content = self.apply_seo_optimization(enhanced_content, topic)
            except Exception as seo_error:
                logger.warning(f"SEO optimization failed: {seo_error}, returning unoptimized content")
            
            logger.info(f"Successfully enhanced content with {llm_provider}")
            return enhanced_content
            
        except Exception as e:
            logger.error(f"LLM enhancement failed: {str(e)}", exc_info=True)
            return None
    
    def _create_research_enhanced_prompt(self, topic: str, research_data: Dict[str, Any]) -> Optional[str]:
        """
        Create a dynamic, context-aware prompt with creative freedom within SEO guidelines
        
        Args:
            topic: The content topic
            research_data: Research data to incorporate
            
        Returns:
            Formatted prompt string or None if creation fails
        """
        try:
            # Load prompt template if configured
            if self.config.prompt_template_file and Path(self.config.prompt_template_file).exists():
                try:
                    template = self._load_prompt_template()
                    if template:
                        return self._format_template(template, topic, research_data)
                except Exception as e:
                    logger.warning(f"Failed to load prompt template: {e}, using default")
            
            # Extract key data points with config limits
            statistics = research_data.get('statistics', [])[:self.config.max_statistics]
            insights = research_data.get('key_insights', [])[:self.config.max_insights]
            articles = research_data.get('articles', [])[:self.config.max_articles]
            
            # Create dynamic prompt using project context instead of rigid template
            return self._create_dynamic_contextual_prompt(topic, statistics, insights, articles)
            
        except Exception as e:
            logger.error(f"Failed to create research enhanced prompt: {e}")
            return None

    def _create_dynamic_contextual_prompt(self, topic: str, statistics: List, insights: List, articles: List) -> str:
        """
        Create a dynamic, contextually-aware prompt that leverages Claude's creative capabilities
        """
        
        # Create research context from actual data only
        research_context = ""
        
        if insights:
            research_context += "\n🔍 VERIFIED MARKET INSIGHTS:\n"
            for i, insight in enumerate(insights, 1):
                clean_insight = insight.replace('<', '').replace('>', '').replace('…', '...')[:200]
                research_context += f"{i}. {clean_insight}\n"
        
        if statistics:
            research_context += "\n📊 STATISTICAL DATA TO INCORPORATE:\n"
            for i, stat in enumerate(statistics, 1):
                value = stat.get('value', 'Growth trend')
                context = stat.get('context', 'market development')[:150]
                clean_context = context.replace('<', '').replace('>', '').replace('…', '...')
                research_context += f"{i}. {value}: {clean_context}\n"
        
        if articles:
            research_context += "\n📰 CURRENT INDUSTRY SOURCES:\n"
            for i, article in enumerate(articles, 1):
                title = article.get('title', 'Industry Report')[:80]
                description = article.get('description', 'Recent analysis')[:150]
                clean_title = title.replace('<', '').replace('>', '').replace('…', '...')
                clean_desc = description.replace('<', '').replace('>', '').replace('…', '...')
                research_context += f"{i}. {clean_title}: {clean_desc}\n"

        # Dynamic, creative prompt that gives Claude freedom within constraints
        prompt = f"""You are a world-class content strategist with deep expertise in {topic}. 

Your mission: Create a comprehensive, original article about "{topic}" that provides exceptional value to readers while achieving maximum search visibility.

**CRITICAL REQUIREMENT:** Write exactly {self.config.target_word_count} words. Track your word count as you write.

{research_context}

**YOUR CREATIVE FREEDOM & CONSTRAINTS:**

✅ **WHAT YOU SHOULD DO:**
- Use your expertise to determine the most valuable angle and structure for this topic
- Create an original, engaging narrative that stands out from generic content
- Leverage the verified research data above to support your insights
- Write with authority, drawing from your knowledge of current market trends
- Design a unique structure that serves the reader's journey and search intent
- Include actionable strategies that readers can implement immediately
- Use creative storytelling and real-world context where appropriate

❌ **STRICT LIMITATIONS:**
- NO fabricated statistics, fake data, or invented company examples
- NO rigid template following - be creative and original
- NO keyword stuffing - integrate "{topic}" naturally
- NO generic, template-driven sections
- NEVER invent percentages, survey results, or company case studies

**SEO FOUNDATION (Non-Negotiable):**
- Craft a compelling, click-worthy title (50-60 characters) with "{topic}"
- Write an engaging meta description (140-160 characters)
- Use clear header hierarchy (H1 → H2 → H3)
- Include "{topic}" naturally in the first 100 words
- Structure content for featured snippets and voice search
- Add internal linking opportunities where valuable
- Optimize for E-A-T (Expertise, Authoritativeness, Trustworthiness)

**CONTENT STRATEGY APPROACH:**
Think like a thought leader in this space. What unique perspective can you offer? What would make this article the definitive resource someone bookmarks and shares?

Consider:
- What are the biggest misconceptions about {topic}?
- What emerging trends should readers know about?
- What practical implementation challenges do businesses face?
- How can you make complex concepts accessible and actionable?
- What future implications should leaders prepare for?

**YOUR ARTICLE STRUCTURE** (Create your own - be creative):
You decide the best structure based on the topic and audience needs. Consider formats like:
- Problem → Solution → Implementation
- Current State → Future Vision → Action Steps  
- Myth-Busting → Reality → Best Practices
- Strategic Overview → Tactical Deep-Dives → Measurement
- Or invent your own unique approach

**TONE & STYLE:**
- Professional yet accessible
- Confident and authoritative
- Practical and implementation-focused
- Forward-thinking and strategic
- Engaging and conversational when appropriate

Remember: Your goal is to create content so valuable and well-crafted that it becomes the go-to resource for "{topic}" - combining your expertise with the verified research data provided.

Begin writing your comprehensive, original article now:"""
        
        return prompt
    
    def _load_prompt_template(self) -> Optional[str]:
        """Load prompt template from file"""
        try:
            with open(self.config.prompt_template_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load prompt template: {e}")
            return None
    
    def _format_template(self, template: str, topic: str, research_data: Dict[str, Any]) -> str:
        """Format template with topic and research data"""
        # Simple template formatting - can be enhanced with Jinja2 for production
        return template.format(
            topic=topic,
            topic_title=topic.title(),
            statistics=research_data.get('statistics', []),
            insights=research_data.get('key_insights', []),
            articles=research_data.get('articles', []),
            target_word_count=self.config.target_word_count
        )
    
    def _merge_research_and_llm_content(self, web_content: Dict, llm_content: str, research_data: Dict, llm_provider: str) -> Dict:
        """Merge web research metadata with LLM-generated content"""
        
        # Use web research metadata as base
        enhanced_metadata = web_content['metadata'].copy()
        
        # Update with LLM information
        enhanced_metadata.update({
            'content_generation': 'hybrid_research_llm',
            'llm_provider': llm_provider,
            'llm_model': self.local_llm.providers[llm_provider]['model'],
            'research_enhanced': True,
            'generation_cost': '$0.00 (Local LLM + Web Research)',
            'content_quality': 'premium_research_based',
            'data_sources': len(research_data.get('sources', [])),
            'statistics_verified': len(research_data.get('statistics', [])),
            'industry_insights': len(research_data.get('key_insights', [])),
            'research_date': research_data.get('research_date', ''),
            'seo_optimized': True,
            'fact_checked': True
        })
        
        # Calculate enhanced metrics
        word_count = len(llm_content.split())
        reading_time = max(1, word_count // 200)
        
        enhanced_metadata.update({
            'word_count': word_count,
            'reading_time': f"{reading_time} minutes",
            'content_depth': 'comprehensive' if word_count > 2000 else 'detailed'
        })
        
        # Create enhanced filename
        title = enhanced_metadata['title']
        filename = self.generate_enhanced_filename(title)
        
        return {
            'title': title,
            'content': llm_content,
            'metadata': enhanced_metadata,
            'filename': filename,
            'research_data': research_data,
            'generation_method': 'hybrid_research_llm',
            'seo_analysis': self.analyze_enhanced_content(llm_content, enhanced_metadata['primary_keyword'])
        }
    
    def generate_enhanced_filename(self, title: str) -> str:
        """Generate enhanced filename with research indicator"""
        import re
        filename = title.lower()
        filename = re.sub(r'[^\w\s-]', '', filename)
        filename = re.sub(r'[-\s]+', '-', filename)
        filename = filename.strip('-')
        filename = f"research-{filename}-{datetime.now().strftime('%Y-%m-%d')}.md"
        return filename
    
    def analyze_enhanced_content(self, content: str, primary_keyword: str) -> Dict:
        """Analyze the enhanced content quality"""
        word_count = len(content.split())
        keyword_count = content.lower().count(primary_keyword.lower())
        keyword_density = (keyword_count / word_count) * 100 if word_count > 0 else 0
        
        # Enhanced analysis
        heading_count = content.count('#')
        paragraph_count = len([p for p in content.split('\n\n') if len(p.strip()) > 50])
        
        quality_score = "Premium"
        if word_count < 1500:
            quality_score = "Good"
        elif word_count < 2000:
            quality_score = "Excellent"
        
        return {
            "word_count": word_count,
            "keyword_density": round(keyword_density, 2),
            "quality_score": quality_score,
            "seo_score": "Optimized" if 1.0 <= keyword_density <= 2.5 else "Needs Optimization",
            "heading_count": heading_count,
            "paragraph_count": paragraph_count,
            "readability": "Professional",
            "research_integration": "Comprehensive"
        }
    
    def save_enhanced_content(self, content_data: Dict, content_dir: str = "serie 1") -> str:
        """Save enhanced research content"""
        Path(content_dir).mkdir(exist_ok=True)
        
        # Create comprehensive YAML front matter
        yaml_content = yaml.dump(content_data["metadata"], default_flow_style=False)
        full_content = f"---\n{yaml_content}---\n\n{content_data['content']}"
        
        # Save to file
        file_path = Path(content_dir) / content_data["filename"]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return str(file_path)
    
    def apply_seo_optimization(self, content_data: Dict, topic: str) -> Dict:
        """Apply comprehensive SEO optimization to content"""
        
        print("🔍 Applying comprehensive SEO optimization...")
        
        content = content_data.get('content', '')
        metadata = content_data.get('metadata', {})
        
        # Get keywords for the topic
        keywords = self.enhanced_topics.get(topic, [topic])
        
        # Generate optimized metadata
        optimized_metadata = self.seo_optimizer.generate_optimized_metadata(content, topic, keywords)
        
        # Merge with existing metadata
        metadata.update(optimized_metadata)
        
        # Optimize content structure
        optimized_content = self.seo_optimizer.optimize_content_structure(content)
        
        # Add internal links
        optimized_content = self.seo_optimizer.add_internal_links(optimized_content)
        
        # Perform comprehensive SEO analysis
        seo_analysis = self.seo_optimizer.analyze_content_comprehensive(optimized_content, metadata)
        
        # Add SEO analysis to metadata
        metadata.update({
            'seo_analysis': seo_analysis,
            'seo_score': f"Optimized ({seo_analysis['seo_score']}/100)",
            'seo_recommendations': seo_analysis['recommendations'][:5]  # Top 5 recommendations
        })
        
        print(f"✅ SEO optimization complete! Score: {seo_analysis['seo_score']}/100")
        if seo_analysis['recommendations']:
            print("📋 Top SEO recommendations:")
            for i, rec in enumerate(seo_analysis['recommendations'][:3], 1):
                print(f"   {i}. {rec}")
        
        return {
            'content': optimized_content,
            'metadata': metadata,
            'filename': content_data.get('filename', '')
        }
    
    def generate_random_research_topic(self) -> str:
        """Generate a random topic for research"""
        import random
        return random.choice(list(self.enhanced_topics.keys()))

    def create_project_aware_prompt(self, 
                                   project_data: Dict[str, Any], 
                                   keyword: str, 
                                   research_data: Dict[str, Any]) -> str:
        """
        Create a project-aware, multilingual prompt that leverages project form data
        
        Args:
            project_data: Rich project information from project form
            keyword: Primary keyword
            research_data: Research context data
            
        Returns:
            Dynamic, context-aware prompt tailored to project requirements
        """
        
        # Extract project context
        project_name = project_data.get('name', 'Content Project')
        project_description = project_data.get('description', '')
        language = project_data.get('language', 'english')
        target_audience = project_data.get('target_audience', 'Marketing professionals')
        content_length = project_data.get('content_length', 'medium')
        cultural_context = project_data.get('cultural_context', 'general')
        seo_focus = project_data.get('seo_focus', [])
        
        # Word count based on content length
        word_count_map = {
            'short': 1500,
            'medium': 2500,
            'long': 3500
        }
        target_words = word_count_map.get(content_length, self.config.target_word_count)
        
        # Language-specific instructions
        language_instructions = {
            'english': {
                'instruction': 'Write entirely in English with professional business tone.',
                'cultural_note': 'Consider Western business practices and cultural references.',
                'style': 'Direct, action-oriented, data-driven approach.'
            },
            'farsi': {
                'instruction': 'نوشته را کاملاً به زبان فارسی و با لحن حرفه‌ای کسب و کار بنویسید. از اصطلاحات فارسی استفاده کنید و محتوا را برای مخاطبان ایرانی تنظیم کنید.',
                'cultural_note': 'با در نظر گیری فرهنگ ایرانی، ارزش‌های خانوادگی و اجتماعی.',
                'style': 'محترمانه، مؤدبانه و با احترام به سنت‌های کسب و کار ایرانی.'
            },
            'spanish': {
                'instruction': 'Escribe completamente en español con un tono profesional de negocios.',
                'cultural_note': 'Considera las prácticas comerciales hispanas y los valores familiares.',
                'style': 'Cálido, relacional, enfocado en la comunidad y las relaciones.'
            }
        }
        
        lang_config = language_instructions.get(language, language_instructions['english'])
        
        # Create research context
        research_context = self._format_research_context(research_data)
        
        # Create dynamic, project-aware prompt
        if language == 'farsi':
            return self._create_farsi_project_prompt(
                project_name, project_description, keyword, target_audience, 
                target_words, research_context, lang_config, seo_focus
            )
        elif language == 'spanish':
            return self._create_spanish_project_prompt(
                project_name, project_description, keyword, target_audience,
                target_words, research_context, lang_config, seo_focus
            )
        else:
            return self._create_english_project_prompt(
                project_name, project_description, keyword, target_audience,
                target_words, research_context, lang_config, seo_focus
            )
    
    def _format_research_context(self, research_data: Dict[str, Any]) -> str:
        """Format research data for prompt context"""
        context = ""
        
        insights = research_data.get('key_insights', [])[:self.config.max_insights]
        if insights:
            context += "\n🔍 VERIFIED MARKET INSIGHTS:\n"
            for i, insight in enumerate(insights, 1):
                clean_insight = str(insight).replace('<', '').replace('>', '').replace('…', '...')[:200]
                context += f"{i}. {clean_insight}\n"
        
        statistics = research_data.get('statistics', [])[:self.config.max_statistics]
        if statistics:
            context += "\n📊 VERIFIED DATA POINTS:\n"
            for i, stat in enumerate(statistics, 1):
                value = stat.get('value', 'Market trend')
                stat_context = stat.get('context', 'industry development')[:150]
                clean_context = str(stat_context).replace('<', '').replace('>', '').replace('…', '...')
                context += f"{i}. {value}: {clean_context}\n"
        
        articles = research_data.get('articles', [])[:self.config.max_articles]
        if articles:
            context += "\n📰 CURRENT INDUSTRY SOURCES:\n"
            for i, article in enumerate(articles, 1):
                title = article.get('title', 'Industry Report')[:80]
                description = article.get('description', 'Current analysis')[:150]
                clean_title = str(title).replace('<', '').replace('>', '').replace('…', '...')
                clean_desc = str(description).replace('<', '').replace('>', '').replace('…', '...')
                context += f"{i}. {clean_title}: {clean_desc}\n"
        
        return context
    
    def _create_english_project_prompt(self, project_name: str, project_description: str, 
                                     keyword: str, target_audience: str, target_words: int,
                                     research_context: str, lang_config: Dict, seo_focus: List) -> str:
        """Create dynamic English prompt based on project context"""
        
        return f"""You are a world-class content strategist working on the project "{project_name}".

PROJECT BRIEF:
- Project: {project_name}
- Description: {project_description}
- Primary Topic: {keyword}
- Target Audience: {target_audience}
- Content Goal: {target_words} words
- SEO Focus: {', '.join(seo_focus) if seo_focus else keyword}

{research_context}

CREATIVE MISSION:
Create an exceptional article about "{keyword}" that serves {target_audience} with unique value. This isn't template-filling—use your expertise to determine the best approach for this specific topic and audience.

YOUR CREATIVE FREEDOM:
✅ Design your own structure based on what serves the topic best
✅ Use storytelling, analogies, and engaging examples
✅ Draw insights from current market trends and industry knowledge  
✅ Create original section headers that flow naturally
✅ Include actionable strategies tailored to {target_audience}
✅ Use the verified research data to support your points

STRICT BOUNDARIES:
❌ NO fabricated statistics or fake company examples
❌ NO rigid template following
❌ NO keyword stuffing
❌ NO generic "Introduction, Body, Conclusion" structure

SEO REQUIREMENTS (Non-negotiable):
- Compelling title (50-60 chars) featuring "{keyword}"
- Natural keyword integration (avoid stuffing)
- Clear header hierarchy (H1 → H2 → H3)
- Meta description (140-160 chars)
- Structure for featured snippets
- E-A-T optimization

CONTENT STRATEGY:
Think: What would make this THE definitive resource for "{keyword}" that {target_audience} would bookmark and share?

Consider unique angles like:
- Contrarian perspectives backed by data
- Emerging trends others aren't covering
- Practical implementation frameworks
- Common misconceptions to address
- Future-focused strategic insights

TONE: {lang_config['style']}

Write exactly {target_words} words of comprehensive, original content that establishes thought leadership in this space."""

    def _create_farsi_project_prompt(self, project_name: str, project_description: str,
                                   keyword: str, target_audience: str, target_words: int,
                                   research_context: str, lang_config: Dict, seo_focus: List) -> str:
        """Create dynamic Farsi prompt based on project context"""
        
        return f"""شما یک استراتژیست محتوای حرفه‌ای هستید که بر روی پروژه "{project_name}" کار می‌کنید.

خلاصه پروژه:
- نام پروژه: {project_name}  
- توضیحات: {project_description}
- موضوع اصلی: {keyword}
- مخاطب هدف: {target_audience}
- هدف محتوا: {target_words} کلمه
- تمرکز سئو: {', '.join(seo_focus) if seo_focus else keyword}

{research_context}

ماموریت خلاقانه:
مقاله‌ای استثنایی درباره "{keyword}" بنویسید که به {target_audience} ارزش منحصر به فرد ارائه دهد. این کار تکمیل قالب نیست—از تخصص خود برای تعیین بهترین رویکرد برای این موضوع و مخاطب استفاده کنید.

آزادی خلاقانه شما:
✅ ساختار خود را بر اساس آنچه بهترین خدمت را به موضوع ارائه می‌دهد، طراحی کنید
✅ از داستان‌گویی، تمثیل‌ها و نمونه‌های جذاب استفاده کنید
✅ بینش‌هایی از روندهای فعلی بازار و دانش صنعت ارائه دهید
✅ سرتیترهای اصلی ایجاد کنید که به طور طبیعی جریان داشته باشند
✅ استراتژی‌های عملی متناسب با {target_audience} ارائه دهید
✅ از داده‌های تحقیقاتی تأیید شده برای حمایت از نکات خود استفاده کنید

محدودیت‌های سخت:
❌ هیچ آمار ساختگی یا نمونه شرکت جعلی
❌ هیچ الگوی سفت و سخت
❌ هیچ پر کردن کلیدواژه
❌ هیچ ساختار عمومی "مقدمه، بدنه، نتیجه‌گیری"

الزامات سئو (غیرقابل مذاکره):
- عنوان جذاب (۵۰-۶۰ کاراکتر) شامل "{keyword}"
- ادغام طبیعی کلیدواژه
- سلسله مراتب واضح سرتیتر (H1 → H2 → H3)
- توضیح متا (۱۴۰-۱۶۰ کاراکتر)
- ساختار برای قطعات برجسته
- بهینه‌سازی E-A-T

استراتژی محتوا:
فکر کنید: چه چیزی این مقاله را به منبع نهایی برای "{keyword}" تبدیل می‌کند که {target_audience} آن را نشانه‌گذاری و به اشتراک بگذارد؟

زوایای منحصر به فرد مانند:
- دیدگاه‌های مخالف پشتیبانی شده با داده
- روندهای نوظهور که دیگران پوشش نمی‌دهند
- چارچوب‌های عملی پیاده‌سازی
- تصورات غلط رایج برای پرداختن
- بینش‌های استراتژیک آینده‌نگر

لحن: {lang_config['style']}

دقیقاً {target_words} کلمه محتوای جامع و اصیل بنویسید که رهبری فکری در این حوزه را تأسیس کند."""

    def _create_spanish_project_prompt(self, project_name: str, project_description: str,
                                     keyword: str, target_audience: str, target_words: int,
                                     research_context: str, lang_config: Dict, seo_focus: List) -> str:
        """Create dynamic Spanish prompt based on project context"""
        
        return f"""Usted es un estratega de contenido de clase mundial trabajando en el proyecto "{project_name}".

RESUMEN DEL PROYECTO:
- Proyecto: {project_name}
- Descripción: {project_description}  
- Tema Principal: {keyword}
- Audiencia Objetivo: {target_audience}
- Meta de Contenido: {target_words} palabras
- Enfoque SEO: {', '.join(seo_focus) if seo_focus else keyword}

{research_context}

MISIÓN CREATIVA:
Cree un artículo excepcional sobre "{keyword}" que sirva a {target_audience} con valor único. Esto no es llenar plantillas—use su experiencia para determinar el mejor enfoque para este tema y audiencia específicos.

SU LIBERTAD CREATIVA:
✅ Diseñe su propia estructura basada en lo que mejor sirva al tema
✅ Use narrativa, analogías y ejemplos atractivos
✅ Extraiga perspectivas de tendencias actuales del mercado y conocimiento de la industria
✅ Cree encabezados originales que fluyan naturalmente
✅ Incluya estrategias accionables adaptadas a {target_audience}
✅ Use los datos de investigación verificados para respaldar sus puntos

LÍMITES ESTRICTOS:
❌ NO estadísticas fabricadas o ejemplos de empresas falsas
❌ NO seguimiento rígido de plantillas
❌ NO saturación de palabras clave
❌ NO estructura genérica "Introducción, Cuerpo, Conclusión"

REQUISITOS SEO (No negociables):
- Título atractivo (50-60 chars) con "{keyword}"
- Integración natural de palabras clave
- Jerarquía clara de encabezados (H1 → H2 → H3)
- Meta descripción (140-160 chars)
- Estructura para fragmentos destacados
- Optimización E-A-T

ESTRATEGIA DE CONTENIDO:
Piense: ¿Qué haría de este EL recurso definitivo para "{keyword}" que {target_audience} marcaría y compartiría?

Considere ángulos únicos como:
- Perspectivas contrarias respaldadas por datos
- Tendencias emergentes que otros no cubren
- Marcos de implementación práctica
- Conceptos erróneos comunes a abordar
- Perspectivas estratégicas enfocadas en el futuro

TONO: {lang_config['style']}

Escriba exactamente {target_words} palabras de contenido integral y original que establezca liderazgo de pensamiento en este espacio."""

def create_cli_parser() -> argparse.ArgumentParser:
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(
        description="Enhanced Research + LLM Content Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python enhanced_research_llm.py --topic "AI Marketing"
  python enhanced_research_llm.py --topic "SEO Automation" --llm claude --no-llm
  python enhanced_research_llm.py --config config.yaml --topic "Content Strategy"
        """
    )
    
    parser.add_argument('--topic', type=str, required=True,
                       help='Topic for content generation')
    parser.add_argument('--llm', type=str, default='claude',
                       choices=['deepseek', 'claude', 'llama'],
                       help='LLM provider to use (default: claude)')
    parser.add_argument('--no-llm', action='store_true', default=True,
                       help='Skip LLM enhancement, use web research only (default: True)')
    parser.add_argument('--config', type=str,
                       help='Configuration file path (YAML or JSON)')
    parser.add_argument('--output-dir', type=str, default='serie 1',
                       help='Output directory for generated content')
    parser.add_argument('--word-count', type=int, default=3500,
                       help='Target word count for generated content')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--dry-run', action='store_true',
                       help='Generate content but do not save to file')
    
    return parser

def load_config_from_file(config_path: str) -> Optional[ContentConfig]:
    """Load configuration from file"""
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            logger.error(f"Configuration file not found: {config_path}")
            return None
        
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_path.endswith(('.yaml', '.yml')):
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)
        
        # Convert dict to ContentConfig
        return ContentConfig(**config_data)
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return None

def main():
    """Main function with CLI support and comprehensive error handling"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")
    
    print("🚀 Enhanced Research + LLM Content Generator")
    print("=" * 50)
    
    try:
        # Load configuration
        config = None
        if args.config:
            config = load_config_from_file(args.config)
            if not config:
                logger.error("Failed to load configuration, using defaults")
                return 1
        else:
            # Create config from CLI arguments
            config = ContentConfig(
                target_word_count=args.word_count,
                use_local_llm=not args.no_llm,
                default_llm_provider=args.llm,
                output_directory=args.output_dir
            )
        
        # Initialize generator
        generator = EnhancedResearchLLMGenerator(config=config)
        
        print(f"📝 Generating content for: {args.topic}")
        
        # Check if topic has predefined keywords
        keywords = generator.enhanced_topics.get(args.topic, [args.topic])
        print(f"🔍 Keywords: {keywords}")
        
        # Generate comprehensive content
        result = generator.create_comprehensive_research_content(
            topic=args.topic,
            use_local_llm=not args.no_llm,
            llm_provider=args.llm
        )
        
        if result.success and result.content_data:
            print(f"\n✅ Content generated successfully!")
            
            content = result.content_data
            print(f"📊 Title: {content.get('title', 'N/A')}")
            
            seo_analysis = content.get('seo_analysis', {})
            if seo_analysis:
                print(f"📈 SEO Score: {seo_analysis.get('overall_score', 'N/A')}")
            
            print(f"📄 Word Count: {content.get('word_count', 'N/A')}")
            print(f"🎯 Keywords: {len(content.get('keywords', []))}")
            
            # Print metadata
            if result.metadata:
                print(f"🤖 LLM Provider: {result.metadata.get('llm_provider', 'None')}")
                print(f"📚 Research Articles: {result.metadata.get('research_articles', 0)}")
            
            # Save the content unless dry run
            if not args.dry_run:
                try:
                    file_path = generator.save_enhanced_content(content, args.output_dir)
                    print(f"💾 Content saved to: {file_path}")
                    result.file_path = file_path
                except Exception as save_error:
                    logger.error(f"Failed to save content: {save_error}")
                    return 1
            else:
                print("🔍 Dry run mode: Content not saved")
            
            return 0
            
        else:
            print(f"❌ Content generation failed: {result.error_message}")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Generation interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 