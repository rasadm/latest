#!/usr/bin/env python3
"""
Enhanced Multilingual Project-Based Content Management System
Manages multiple content projects with custom keywords, templates, research, and language support
"""

import os
import json
import time
import random
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid
from dataclasses import dataclass, asdict
from content.auto_content_system import AutoContentSystem
from core.web_research_content import WebResearchContentGenerator
from core.local_llm_content import MultilingualLocalLLMContentGenerator
from content.claude_content import ClaudeContentGenerator
from core.settings_manager import SettingsManager
import re

@dataclass
class ContentProject:
    """Enhanced data class for multilingual content project configuration"""
    id: str
    name: str
    description: str
    keywords: List[str]
    target_count: int
    content_type: str  # "template", "local_llm", "llama", "research_llm", "claude"
    llm_model: str  # for LLM-based generation
    research_sites: List[str]  # specific sites to research
    template_style: str  # "trend_analysis", "how_to_guide", "case_study"
    created_date: str
    completed_count: int
    status: str  # "active", "paused", "completed"
    output_directory: str
    seo_focus: List[str]  # SEO keywords to focus on
    target_audience: str  # target audience description
    content_length: str  # "short", "medium", "long"
    publishing_schedule: str  # "immediate", "daily", "weekly"
    publishing_interval: int  # minutes between posts for automatic publishing
    website_id: str  # WordPress website ID for publishing
    language: str = "english"  # Content language
    cultural_context: str = "western_business"  # Cultural context for content

class MultilingualProjectManager:
    def __init__(self):
        self.projects_file = "projects.json"
        self.projects_dir = "projects"
        self.projects: Dict[str, ContentProject] = {}
        
        # Initialize settings manager
        self.settings_manager = SettingsManager()
        
        # Initialize content generators
        self.auto_content = AutoContentSystem()
        self.web_research = WebResearchContentGenerator()
        self.local_llm = MultilingualLocalLLMContentGenerator()
        self.claude = ClaudeContentGenerator()
        
        # Initialize enhanced research generator for project-aware prompts
        from core.enhanced_research_llm import EnhancedResearchLLMGenerator
        self.enhanced_research_generator = EnhancedResearchLLMGenerator()
        
        # Load multilingual research sites from config
        self.multilingual_research_sites = self._load_research_sites_config()
        
        self.load_projects()
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories"""
        Path(self.projects_dir).mkdir(exist_ok=True)
    
    def load_projects(self):
        """Load projects from file"""
        if os.path.exists(self.projects_file):
            try:
                with open(self.projects_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for project_id, project_data in data.items():
                        # Add language and cultural_context if missing (backward compatibility)
                        if 'language' not in project_data:
                            project_data['language'] = 'english'
                        if 'cultural_context' not in project_data:
                            project_data['cultural_context'] = 'western_business'
                        
                        self.projects[project_id] = ContentProject(**project_data)
            except Exception as e:
                print(f"Error loading projects: {e}")
    
    def save_projects(self):
        """Save projects to file"""
        try:
            data = {project_id: asdict(project) for project_id, project in self.projects.items()}
            with open(self.projects_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving projects: {e}")
            return False
    
    def create_project(self, name: str, description: str, keywords: List[str], 
                      content_type: str, target_count: int = 10, 
                      language: str = "english", **kwargs) -> str:
        """Create a new multilingual content project"""
        
        project_id = str(uuid.uuid4())[:8]
        
        # Get language configuration
        lang_config = self.settings_manager.get_language_config(language)
        cultural_context = lang_config.cultural_rules.get('cultural_context', 'general') if lang_config else 'general'
        
        # Create language-specific output directory
        output_dir = f"{self.projects_dir}/project_{project_id}_{sanitize_filename(name)}_{language}"
        Path(output_dir).mkdir(exist_ok=True)
        
        project = ContentProject(
            id=project_id,
            name=name,
            description=description,
            keywords=keywords,
            target_count=target_count,
            content_type=content_type,
            llm_model=kwargs.get('llm_model', 'deepseek'),
            research_sites=kwargs.get('research_sites', []),
            template_style=kwargs.get('template_style', 'trend_analysis'),
            created_date=datetime.now().isoformat(),
            completed_count=0,
            status="active",
            output_directory=output_dir,
            seo_focus=kwargs.get('seo_focus', []),
            target_audience=kwargs.get('target_audience', 'Marketing professionals'),
            content_length=kwargs.get('content_length', 'medium'),
            publishing_schedule=kwargs.get('publishing_schedule', 'immediate'),
            publishing_interval=kwargs.get('publishing_interval', 60),
            website_id=kwargs.get('website_id', ''),
            language=language,
            cultural_context=cultural_context
        )
        
        self.projects[project_id] = project
        self.save_projects()
        
        print(f"✅ Created {language} project: {name} (ID: {project_id})")
        return project_id
    
    def get_project(self, project_id: str) -> Optional[ContentProject]:
        """Get project by ID"""
        return self.projects.get(project_id)
    
    def list_projects(self) -> List[ContentProject]:
        """List all projects"""
        return list(self.projects.values())
    
    def update_project_status(self, project_id: str, status: str):
        """Update project status"""
        if project_id in self.projects:
            self.projects[project_id].status = status
            self.save_projects()
    
    def remove_project(self, project_id: str) -> bool:
        """Remove a project completely"""
        try:
            if project_id in self.projects:
                del self.projects[project_id]
                self.save_projects()
                print(f"🗑️ Project {project_id} removed from system")
                return True
            else:
                print(f"⚠️ Project {project_id} not found")
                return False
        except Exception as e:
            print(f"❌ Error removing project {project_id}: {e}")
            return False
    
    def get_available_websites(self):
        """Get list of available WordPress websites"""
        return self.settings_manager.get_active_websites()
    
    def get_website_by_id(self, website_id: str):
        """Get WordPress website by ID"""
        return self.settings_manager.get_wordpress_website(website_id)
    
    def generate_multilingual_content(self, project_id: str, custom_topic: str = None) -> Dict:
        """Generate content for a multilingual project"""
        
        if project_id not in self.projects:
            return {"error": "Project not found"}
        
        project = self.projects[project_id]
        
        # Select topic based on language and project keywords
        if custom_topic:
            topic = custom_topic
        else:
            if project.language in self.local_llm.multilingual_topics:
                available_topics = self.local_llm.multilingual_topics[project.language]
                topic = random.choice(available_topics)
            else:
                # Fallback to project keywords
                topic = random.choice(project.keywords) if project.keywords else "AI Marketing Trends"
        
        print(f"🌍 Generating {project.language} content for: {topic}")
        
        try:
            if project.content_type == "local_llm":
                return self._generate_with_local_llm(project, topic)
            elif project.content_type == "research_llm":
                return self._generate_with_research_llm(project, topic)
            elif project.content_type == "claude":
                return self._generate_with_claude(project, topic)
            elif project.content_type == "claude_research":
                return self._generate_with_claude_research(project, topic)
            else:
                return self._generate_with_template(project, topic)
                
        except Exception as e:
            print(f"❌ Error generating content: {e}")
            return {"error": str(e)}
    
    def _generate_with_local_llm(self, project: ContentProject, topic: str) -> Dict:
        """Generate content using local LLM with language support"""
        
        # Set the LLM provider
        self.local_llm.set_provider(project.llm_model)
        
        # Generate multilingual content
        result = self.local_llm.generate_multilingual_blog_post(topic, project.language)
        
        if result:
            # Save to project directory
            file_path = self._save_project_content(project, result)
            result["file_path"] = file_path
            result["project_id"] = project.id
            result["generation_method"] = f"local_llm_{project.llm_model}"
            
            # Update project completion count
            project.completed_count += 1
            self.save_projects()
            
            return result
        
        return {"error": "Failed to generate content with local LLM"}
    
    def _generate_with_template(self, project: ContentProject, topic: str) -> Dict:
        """Generate content using language-specific templates"""
        
        # Get language configuration
        lang_config = self.settings_manager.get_language_config(project.language)
        if not lang_config:
            return {"error": f"Language {project.language} not supported"}
        
        # Create language-specific template
        template = self.generate_multilingual_template(project, topic)
        
        # Generate content using template
        content_result = self.generate_multilingual_template_content(project, template)
        
        if content_result:
            # Create metadata
            metadata = self._create_multilingual_metadata(project, content_result, topic)
            
            # Save content
            file_path = self._save_template_content(project, content_result, metadata)
            
            # Update project completion count
            project.completed_count += 1
            self.save_projects()
            
            return {
                "title": content_result["title"],
                "content": content_result["content"],
                "metadata": metadata,
                "file_path": file_path,
                "project_id": project.id,
                "language": project.language,
                "generation_method": "multilingual_template"
            }
        
        return {"error": "Failed to generate template content"}
    
    def generate_multilingual_template(self, project: ContentProject, keyword: str) -> Dict:
        """Generate language-specific content template"""
        
        lang_config = self.settings_manager.get_language_config(project.language)
        content_templates = lang_config.content_templates if lang_config else {}
        
        template_style = project.template_style
        
        # Language-specific title templates
        if project.language == "english":
            title_templates = {
                "trend_analysis": [
                    f"{keyword}: {datetime.now().year} Trends and Predictions for Modern Marketers",
                    f"The Future of {keyword}: Comprehensive Analysis for {datetime.now().year}",
                    f"How {keyword} is Transforming Marketing in {datetime.now().year}"
                ],
                "how_to_guide": [
                    f"The Complete Guide to {keyword}: Best Practices and Implementation",
                    f"How to Master {keyword}: A Step-by-Step Guide for Marketers",
                    f"Implementing {keyword}: From Strategy to Success"
                ],
                "case_study": [
                    f"How Leading Companies Are Using {keyword} to Transform Their Marketing",
                    f"Success Stories: {keyword} Implementation in Modern Businesses",
                    f"Real-World Results: {keyword} Case Studies and Lessons Learned"
                ]
            }
        elif project.language == "farsi":
            title_templates = {
                "trend_analysis": [
                    f"{keyword}: روندها و پیش‌بینی‌های {datetime.now().year} برای بازاریابان مدرن",
                    f"آینده {keyword}: تحلیل جامع برای سال {datetime.now().year}",
                    f"چگونه {keyword} بازاریابی را در سال {datetime.now().year} متحول می‌کند"
                ],
                "how_to_guide": [
                    f"راهنمای کامل {keyword}: بهترین شیوه‌ها و پیاده‌سازی",
                    f"چگونه {keyword} را تسلط یابیم: راهنمای گام‌به‌گام برای بازاریابان",
                    f"پیاده‌سازی {keyword}: از استراتژی تا موفقیت"
                ],
                "case_study": [
                    f"چگونه شرکت‌های پیشرو از {keyword} برای تحول بازاریابی خود استفاده می‌کنند",
                    f"داستان‌های موفقیت: پیاده‌سازی {keyword} در کسب‌وکارهای مدرن",
                    f"نتایج واقعی: مطالعات موردی {keyword} و درس‌های آموخته شده"
                ]
            }
        elif project.language == "spanish":
            title_templates = {
                "trend_analysis": [
                    f"{keyword}: Tendencias y Predicciones {datetime.now().year} para Profesionales de Marketing",
                    f"El Futuro de {keyword}: Análisis Integral para {datetime.now().year}",
                    f"Cómo {keyword} está Transformando el Marketing en {datetime.now().year}"
                ],
                "how_to_guide": [
                    f"La Guía Completa de {keyword}: Mejores Prácticas e Implementación",
                    f"Cómo Dominar {keyword}: Una Guía Paso a Paso para Profesionales de Marketing",
                    f"Implementando {keyword}: De la Estrategia al Éxito"
                ],
                "case_study": [
                    f"Cómo las Empresas Líderes Usan {keyword} para Transformar su Marketing",
                    f"Historias de Éxito: Implementación de {keyword} en Empresas Modernas",
                    f"Resultados Reales: Estudios de Caso de {keyword} y Lecciones Aprendidas"
                ]
            }
        
        # Create keyword-focused sections
        if project.language == "english":
            section_templates = {
                "trend_analysis": [
                    f"Current State of {keyword} in the Market",
                    f"Emerging Trends in {keyword}",
                    f"Impact of {keyword} on Marketing Industry",
                    f"Implementation Strategies for {keyword}",
                    f"Future Outlook and Predictions for {keyword}"
                ],
                "how_to_guide": [
                    f"Understanding {keyword} Fundamentals",
                    f"Preparation for {keyword} Implementation",
                    f"Step-by-Step {keyword} Execution",
                    f"Challenges and Solutions in {keyword}",
                    f"Measuring {keyword} Success"
                ],
                "case_study": [
                    f"Challenges Before Using {keyword}",
                    f"Solution: {keyword} Implementation",
                    f"Results and Achievements with {keyword}",
                    f"Lessons Learned from {keyword}",
                    f"Practical Recommendations for {keyword}"
                ]
            }
        elif project.language == "farsi":
            section_templates = {
                "trend_analysis": [
                    f"وضعیت فعلی {keyword} در بازار",
                    f"روندهای نوظهور در {keyword}",
                    f"تأثیر {keyword} بر صنعت بازاریابی",
                    f"استراتژی‌های پیاده‌سازی برای {keyword}",
                    f"چشم‌انداز آینده و پیش‌بینی‌ها برای {keyword}"
                ],
                "how_to_guide": [
                    f"درک مبانی {keyword}",
                    f"آماده‌سازی برای پیاده‌سازی {keyword}",
                    f"اجرای گام‌به‌گام {keyword}",
                    f"چالش‌ها و راه‌حل‌ها در {keyword}",
                    f"اندازه‌گیری موفقیت {keyword}"
                ],
                "case_study": [
                    f"چالش‌ها قبل از استفاده از {keyword}",
                    f"راه‌حل: پیاده‌سازی {keyword}",
                    f"نتایج و دستاوردها با {keyword}",
                    f"درس‌های آموخته شده از {keyword}",
                    f"توصیه‌های عملی برای {keyword}"
                ]
            }
        elif project.language == "spanish":
            section_templates = {
                "trend_analysis": [
                    f"Estado Actual de {keyword} en el Mercado",
                    f"Tendencias Emergentes en {keyword}",
                    f"Impacto de {keyword} en la Industria del Marketing",
                    f"Estrategias de Implementación para {keyword}",
                    f"Perspectivas Futuras y Predicciones para {keyword}"
                ],
                "how_to_guide": [
                    f"Entendiendo los Fundamentos de {keyword}",
                    f"Preparación para la Implementación de {keyword}",
                    f"Ejecución Paso a Paso de {keyword}",
                    f"Desafíos y Soluciones en {keyword}",
                    f"Midiendo el Éxito de {keyword}"
                ],
                "case_study": [
                    f"Desafíos Antes de Usar {keyword}",
                    f"Solución: Implementación de {keyword}",
                    f"Resultados y Logros con {keyword}",
                    f"Lecciones Aprendidas de {keyword}",
                    f"Recomendaciones Prácticas para {keyword}"
                ]
            }
        
        selected_title = random.choice(title_templates[template_style])
        selected_sections = section_templates[template_style]
        
        return {
            "title": selected_title,
            "keyword": keyword,
            "sections": selected_sections,
            "template_style": template_style,
            "seo_focus": project.seo_focus,
            "target_audience": project.target_audience,
            "content_length": project.content_length,
            "language": project.language,
            "cultural_context": project.cultural_context
        }
    
    def create_enhanced_prompt(self, project: ContentProject, keyword: str, research_data: Dict = None) -> str:
        """Create enhanced prompt with research data and multilingual support using project-aware approach"""
        
        # Create project data dictionary for the new system
        project_data = {
            'name': project.name,
            'description': project.description,
            'language': project.language,
            'target_audience': project.target_audience,
            'content_length': project.content_length,
            'cultural_context': project.cultural_context,
            'seo_focus': project.seo_focus
        }
        
        # Use the enhanced research LLM generator's new project-aware prompt system
        if hasattr(self, 'enhanced_research_generator'):
            return self.enhanced_research_generator.create_project_aware_prompt(
                project_data, keyword, research_data or {}
            )
        
        # Fallback to create our own project-aware prompt (for standalone use)
        return self._create_fallback_project_prompt(project_data, keyword, research_data or {})
    
    def _create_fallback_project_prompt(self, project_data: Dict, keyword: str, research_data: Dict) -> str:
        """Fallback project-aware prompt creation when enhanced generator is not available"""
        
        language = project_data.get('language', 'english')
        
        # Basic language-specific prompt structure
        if language == 'farsi':
            return f"""شما یک استراتژیست محتوای حرفه‌ای هستید که بر روی پروژه "{project_data['name']}" کار می‌کنید.

موضوع: {keyword}
مخاطب هدف: {project_data['target_audience']}
توضیحات پروژه: {project_data['description']}

مقاله‌ای اصیل و ارزشمند درباره "{keyword}" بنویسید که از قالب‌های آماده استفاده نکند.

الزامات:
- کاملاً به زبان فارسی
- ساختار خلاقانه و منحصر به فرد
- بدون استفاده از آمار ساختگی
- عملی و قابل اجرا برای {project_data['target_audience']}

محتوای جامع و اصیل ایجاد کنید."""
        
        elif language == 'spanish':
            return f"""Usted es un estratega de contenido profesional trabajando en el proyecto "{project_data['name']}".

Tema: {keyword}
Audiencia objetivo: {project_data['target_audience']}
Descripción del proyecto: {project_data['description']}

Escriba un artículo original y valioso sobre "{keyword}" que no use plantillas predefinidas.

Requisitos:
- Completamente en español
- Estructura creativa y única
- Sin usar estadísticas falsas
- Práctico y accionable para {project_data['target_audience']}

Cree contenido integral y original."""
        
        else:  # English
            return f"""You are a professional content strategist working on the project "{project_data['name']}".

Topic: {keyword}
Target Audience: {project_data['target_audience']}
Project Description: {project_data['description']}

Write an original, valuable article about "{keyword}" that doesn't use preset templates.

Requirements:
- Entirely in English
- Creative and unique structure
- No fabricated statistics
- Practical and actionable for {project_data['target_audience']}

Create comprehensive, original content."""
    
    def perform_targeted_research(self, project: ContentProject, keyword: str) -> Dict:
        """Perform targeted research for specific keyword"""
        
        print(f"🔍 Starting research for keyword: {keyword}")
        
        research_results = {
            "keyword": keyword,
            "statistics": [],
            "trends": [],
            "expert_opinions": [],
            "sources": []
        }
        
        try:
            # Use web research generator with limited sites
            for site in project.research_sites[:2]:  # Limit to 2 sites
                try:
                    print(f"📊 Researching {site}...")
                    
                    # Create search query
                    search_query = f"{keyword} marketing trends 2025"
                    
                    # Simulate research (in real implementation, you'd scrape these sites)
                    site_data = self.web_research.search_google_news(search_query, max_results=3)
                    
                    if site_data:
                        research_results["sources"].extend(site_data[:2])
                        
                        # Extract key information
                        for article in site_data[:2]:
                            if article.get("summary"):
                                research_results["trends"].append(article["summary"][:200])
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    print(f"⚠️ Research error for {site}: {e}")
                    continue
            
            # Only add real statistics if found during research
            # Do not fabricate any statistics
            
            print(f"✅ Research completed for {keyword}")
            
        except Exception as e:
            print(f"❌ Research error: {e}")
        
        return research_results
    
    def generate_featured_image_for_project(self, project: ContentProject, keyword: str) -> Dict:
        """Generate SEO-optimized featured image for project content using Unsplash API"""
        
        # Create search query based on keyword and project context
        search_query = self._create_image_search_query(keyword, project.name)
        
        # Fetch image from Unsplash
        image_data = self._fetch_unsplash_image(search_query)
        
        if not image_data:
            # Fallback to a broader search if specific search fails
            fallback_query = self._create_fallback_search_query(keyword)
            image_data = self._fetch_unsplash_image(fallback_query)
        
        if not image_data:
            # Final fallback to generic business/marketing image
            image_data = self._fetch_unsplash_image("business marketing technology")
        
        # Generate SEO-optimized filename and metadata
        topic_slug = keyword.lower().replace(' ', '-').replace(',', '').replace(':', '')
        topic_slug = ''.join(c for c in topic_slug if c.isalnum() or c in '-_')
        
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"{topic_slug}-featured-image-{date_str}"
        
        # Create comprehensive SEO metadata
        if image_data:
            featured_image = {
                "url": f"{image_data['urls']['regular']}?w=1200&h=630&fit=crop&auto=format&q=80",
                "url_webp": f"{image_data['urls']['regular']}?w=1200&h=630&fit=crop&auto=format&fm=webp&q=80",
                "url_mobile": f"{image_data['urls']['regular']}?w=800&h=420&fit=crop&auto=format&q=80",
                "alt": f"{keyword} - Complete implementation guide and best practices for modern marketers in {datetime.now().year}",
                "title": f"{keyword}: Advanced strategies for business growth and marketing success",
                "filename": filename,
                "caption": f"Comprehensive guide to {keyword.lower()} implementation and optimization strategies",
                "width": 1200,
                "height": 630,
                "format": "webp",
                "seo_score": 95,
                "keywords": [keyword.lower().replace(' ', '-'), "marketing-strategy", "business-growth", f"{datetime.now().year}-trends"],
                "unsplash_id": image_data['id'],
                "photographer": image_data['user']['name'],
                "photographer_url": image_data['user']['links']['html']
            }
        else:
            # Emergency fallback with a generic business image URL
            featured_image = {
                "url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&h=630&fit=crop&auto=format&q=80",
                "url_webp": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&h=630&fit=crop&auto=format&fm=webp&q=80",
                "url_mobile": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&h=420&fit=crop&auto=format&q=80",
                "alt": f"{keyword} - Complete implementation guide and best practices for modern marketers in {datetime.now().year}",
                "title": f"{keyword}: Advanced strategies for business growth and marketing success",
                "filename": filename,
                "caption": f"Comprehensive guide to {keyword.lower()} implementation and optimization strategies",
                "width": 1200,
                "height": 630,
                "format": "webp",
                "seo_score": 95,
                "keywords": [keyword.lower().replace(' ', '-'), "marketing-strategy", "business-growth", f"{datetime.now().year}-trends"]
            }
        
        return featured_image
    
    def add_seo_images_to_content(self, content: str, project: ContentProject, keyword: str) -> str:
        """Add SEO-optimized images to content sections using dynamic Unsplash fetching"""
        
        # Extract sections from content (look for ## headers)
        lines = content.split('\n')
        sections = []
        for line in lines:
            if line.startswith('## ') and not line.startswith('### '):
                section_title = line.replace('## ', '').strip()
                if section_title and section_title.lower() not in ['conclusion', 'summary', 'references', 'final thoughts']:
                    sections.append(section_title)
        
        # Fetch images for each section dynamically
        section_images = []
        for section_title in sections[:6]:  # Limit to 6 images max
            search_query = f"{section_title} {keyword} business"
            image_data = self._fetch_unsplash_image(search_query)
            if image_data:
                section_images.append({
                    'section': section_title,
                    'image_data': image_data
                })
        
        # Add images after each major section
        new_lines = []
        image_index = 0
        
        for line in lines:
            new_lines.append(line)
            
            # Check if this line is a section header and we have an image for it
            if line.startswith('## ') and not line.startswith('### ') and image_index < len(section_images):
                section_title = line.replace('## ', '').strip()
                
                # Skip conclusion/summary sections
                if section_title.lower() in ['conclusion', 'summary', 'references', 'final thoughts']:
                    continue
                
                # Find matching image for this section
                matching_image = None
                for img_data in section_images[image_index:]:
                    if img_data['section'] == section_title:
                        matching_image = img_data['image_data']
                        break
                
                if matching_image:
                    # Generate SEO alt text
                    alt_text = f"{section_title} - {keyword} strategies and implementation guide for modern marketers"
                    
                    # Create SEO-optimized image title
                    title_text = f"{section_title}: Advanced {keyword} solutions for business growth and customer engagement"
                    
                    # Generate caption with SEO keywords
                    caption = f"*{section_title} leverages cutting-edge {keyword.lower()} to drive measurable business results and enhance customer experiences.*"
                    
                    # Build optimized Unsplash URL with SEO parameters
                    image_url = f"{matching_image['urls']['regular']}?w=800&h=400&fit=crop&auto=format&q=80"
                    
                    # Add SEO-optimized image with proper markup
                    image_line = f'\n\n![{alt_text}]({image_url} "{title_text}")'
                    caption_line = f'{caption}\n'
                    
                    new_lines.extend([image_line, caption_line])
                    image_index += 1
        
        return '\n'.join(new_lines)
    
    def _create_image_search_query(self, keyword: str, project_name: str) -> str:
        """Create optimized search query for Unsplash based on keyword and project context"""
        
        # Clean and prepare search terms
        clean_keyword = keyword.lower().replace('-', ' ')
        clean_project = project_name.lower().replace('-', ' ')
        
        # Create contextual search query
        if 'ai' in clean_keyword or 'artificial intelligence' in clean_keyword:
            return f"artificial intelligence technology business {clean_keyword}"
        elif 'seo' in clean_keyword or 'search' in clean_keyword:
            return f"seo search engine optimization marketing {clean_keyword}"
        elif 'social media' in clean_keyword or 'social' in clean_keyword:
            return f"social media marketing digital {clean_keyword}"
        elif 'content' in clean_keyword:
            return f"content marketing writing business {clean_keyword}"
        elif 'marketing' in clean_keyword:
            return f"digital marketing business strategy {clean_keyword}"
        else:
            return f"business technology marketing {clean_keyword}"
    
    def _create_fallback_search_query(self, keyword: str) -> str:
        """Create broader fallback search query"""
        
        clean_keyword = keyword.lower().replace('-', ' ')
        
        if any(word in clean_keyword for word in ['ai', 'artificial', 'technology', 'digital']):
            return "technology business innovation"
        elif any(word in clean_keyword for word in ['marketing', 'social', 'content']):
            return "marketing business strategy"
        else:
            return "business professional modern"
    
    def _fetch_unsplash_image(self, search_query: str) -> Optional[Dict]:
        """Fetch image from Unsplash API based on search query"""
        
        try:
            import requests
            
            # Unsplash API endpoint
            url = "https://api.unsplash.com/search/photos"
            
            # Get Unsplash access key from environment or use demo key
            access_key = os.getenv('UNSPLASH_ACCESS_KEY', 'YOUR_UNSPLASH_ACCESS_KEY')
            
            # If no API key is set, return None to use fallback
            if access_key == 'YOUR_UNSPLASH_ACCESS_KEY':
                print("⚠️ No Unsplash API key found. Using fallback images.")
                return None
            
            headers = {
                'Authorization': f'Client-ID {access_key}'
            }
            
            params = {
                'query': search_query,
                'per_page': 1,
                'orientation': 'landscape',
                'content_filter': 'high'
            }
            
            print(f"🔍 Searching Unsplash for: {search_query}")
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['results']:
                    image = data['results'][0]
                    print(f"✅ Found image: {image['alt_description'] or 'Professional image'}")
                    return image
                else:
                    print(f"❌ No images found for: {search_query}")
                    return None
            else:
                print(f"❌ Unsplash API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching image from Unsplash: {e}")
            return None
    
    def generate_content_for_project(self, project_id: str, keyword: str = None) -> bool:
        """Generate one piece of content for a project"""
        
        project = self.get_project(project_id)
        if not project:
            print(f"❌ Project {project_id} not found")
            return False
        
        if project.completed_count >= project.target_count:
            print(f"✅ Project {project.name} is completed")
            return False
        
        # Select keyword
        if not keyword:
            remaining_keywords = project.keywords[project.completed_count % len(project.keywords)]
            keyword = remaining_keywords
        
        print(f"🚀 Generating content for project '{project.name}'")
        print(f"🎯 Keyword: {keyword}")
        
        try:
            # Always perform research to get real data and avoid fabrication
            research_data = self.perform_targeted_research(project, keyword)
            
            # Generate content based on type
            content_data = None
            
            if project.content_type == "template":
                template = self.generate_custom_template(project, keyword)
                content_data = self.generate_template_content(project, template)
                
            elif project.content_type == "local_llm":
                self.local_llm.set_provider(project.llm_model)
                prompt = self.create_enhanced_prompt(project, keyword, research_data)
                content = self.local_llm.generate_content_with_local_llm(keyword, "blog_post")
                if content:
                    content_data = self.create_content_structure(project, keyword, content)
                    
            elif project.content_type == "llama":
                self.local_llm.set_provider(project.llm_model)
                prompt = self.create_enhanced_prompt(project, keyword, research_data)
                content = self.local_llm.generate_content_with_local_llm(keyword, "blog_post")
                if content:
                    content_data = self.create_content_structure(project, keyword, content)
                    
            elif project.content_type == "research_llm":
                # Use proper research method that returns compatible format
                research_data = self.web_research.research_topic_comprehensively(keyword)
                
                prompt = self.create_enhanced_prompt(project, keyword, research_data)
                # Use enhanced research generator
                research_content = self.web_research.generate_seo_optimized_content(
                    keyword, research_data, [keyword] + project.seo_focus
                )
                
                # Transform research content to expected format
                if research_content:
                    content_data = {
                        "title": research_content.get("title", f"{keyword}: Research-Based Guide"),
                        "content": research_content.get("content", ""),
                        "keyword": keyword,
                        "generation_method": "research_llm",
                        "word_count": research_content.get("seo_analysis", {}).get("word_count", len(research_content.get("content", "").split())),
                        "seo_keywords": project.seo_focus,
                        "target_audience": project.target_audience,
                        "metadata": research_content.get("metadata", {}),
                        "research_data": research_content.get("research_data", {})
                    }
                else:
                    content_data = None
                
            elif project.content_type == "claude":
                if not self.claude.test_connection():
                    print("❌ Claude connection failed")
                    return False
                # Set Claude model if specified
                if project.llm_model.startswith("claude-"):
                    self.claude.set_model(project.llm_model)
                
                # Create language-specific and research-enhanced prompt
                enhanced_prompt = self.create_enhanced_prompt(project, keyword, research_data)
                content_data = self.claude.generate_blog_post_with_claude(keyword, custom_prompt=enhanced_prompt)
                
            elif project.content_type == "claude_research":
                if not self.claude.test_connection():
                    print("❌ Claude connection failed")
                    return False
                # Set Claude model if specified
                if project.llm_model.startswith("claude-"):
                    self.claude.set_model(project.llm_model)
                # Perform research first
                research_data = self.perform_targeted_research(project, keyword)
                # Generate enhanced prompt with research data
                prompt = self.create_enhanced_prompt(project, keyword, research_data)
                # Use Claude with research-enhanced prompt
                content_data = self.claude.generate_blog_post_with_claude(keyword, custom_prompt=prompt)
            
            if content_data:
                # Save content to project directory
                filepath = self.save_project_content(project, content_data, keyword)
                
                # Update project progress
                project.completed_count += 1
                self.save_projects()
                
                print(f"✅ Content generated: {filepath}")
                print(f"📊 Progress: {project.completed_count}/{project.target_count}")
                
                # Publish if immediate
                if project.publishing_schedule == "immediate":
                    success = self.auto_content.publish_to_wordpress(filepath)
                    if success:
                        print(f"🌐 Content published")
                
                return True
            else:
                print("❌ Content generation failed")
                return False
                
        except Exception as e:
            print(f"❌ Content generation error: {e}")
            return False
    
    def generate_template_content(self, project: ContentProject, template: Dict) -> Dict:
        """Generate content using custom template"""
        
        keyword = template["keyword"]
        sections_content = []
        
        # Generate content for each section
        for i, section in enumerate(template["sections"]):
            section_content = f"""
{section} encompasses comprehensive analysis and deep examination of {keyword} in the current market. This section explores various aspects of {keyword} and its impact on modern marketing strategies.

Recent research indicates that organizations implementing {keyword} have observed measurable improvements in key performance indicators such as conversion rates, customer engagement, and customer acquisition costs. (Replace this sentence with concrete statistics pulled from live research data when available.)

The technology stack supporting {keyword} has evolved considerably, with new platforms and tools emerging regularly. Modern solutions offer enhanced integration capabilities, real-time analytics, and sophisticated automation features that enable marketing teams to operate more efficiently and effectively.

Key market drivers include increasing customer expectations for personalized experiences, the need for data-driven decision making, and competitive pressure to adopt innovative technologies. These factors are accelerating adoption across industries and company sizes.
"""
            sections_content.append(f"## {section}\n\n{section_content.strip()}")
        
        # Create complete content
        full_content = f"""# {template['title']}

{template['keyword']} is one of the most important digital marketing trends in 2025, creating fundamental transformation in how businesses interact with customers.

{chr(10).join(sections_content)}

## Conclusion

Effective implementation of {keyword} requires careful planning, strategic thinking, and systematic execution. Organizations that properly implement these technologies will gain significant competitive advantages in efficiency, personalization, and customer satisfaction.
"""
        
        return {
            "title": template["title"],
            "content": full_content,
            "keyword": keyword,
            "generation_method": "custom_template",
            "word_count": len(full_content.split()),
            "seo_keywords": project.seo_focus
        }
    
    def create_content_structure(self, project: ContentProject, keyword: str, content: str) -> Dict:
        """Create structured content data"""
        
        title = f"{keyword}: Comprehensive Guide for Modern Marketers"
        
        return {
            "title": title,
            "content": content,
            "keyword": keyword,
            "generation_method": project.content_type,
            "word_count": len(content.split()),
            "seo_keywords": project.seo_focus,
            "target_audience": project.target_audience
        }
    
    def save_project_content(self, project: ContentProject, content_data: Dict, keyword: str) -> str:
        """Save content to project directory with proper YAML front matter and SEO-optimized images"""
        
        # Create filename
        keyword_slug = keyword.lower().replace(" ", "-").replace(",", "")
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{keyword_slug}-{date_str}.md"
        
        filepath = Path(project.output_directory) / filename
        
        # Create YAML front matter for WordPress
        default_categories = ["AI Marketing", "Digital Innovation"]
        default_author = "RasaDM Research Team"
        
        # Get categories and author from project settings or config
        categories = getattr(project, 'categories', None) or os.getenv("DEFAULT_CATEGORIES", "").split(",") or default_categories
        author = getattr(project, 'author', None) or os.getenv("DEFAULT_AUTHOR") or default_author
        
        # Clean categories if they came from environment variable
        if isinstance(categories, list) and len(categories) == 1 and "," in categories[0]:
            categories = [cat.strip() for cat in categories[0].split(",")]
        
        # Generate SEO-optimized featured image
        featured_image = self.generate_featured_image_for_project(project, keyword)
        
        # Add images to content
        content_with_images = self.add_seo_images_to_content(content_data.get("content", ""), project, keyword)
        
        front_matter = {
            "title": content_data['title'],
            "date": datetime.now().strftime("%Y-%m-%d"),
            "categories": categories,
            "tags": content_data.get('seo_keywords', []),
            "excerpt": f"Comprehensive guide to {keyword} for marketing professionals in {datetime.now().year}.",
            "author": author,
            "meta_description": f"Learn how to implement {keyword} effectively in your marketing strategy. Expert insights and practical guidance.",
            "reading_time": f"{max(3, len(content_with_images.split()) // 200)} minutes",
            "seo_optimized": True,
            "featured_image": featured_image,
            "schema_type": "Article",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "image_seo": {
                "optimized": True,
                "alt_text_strategy": "descriptive_with_keywords",
                "filename_strategy": "seo_optimized_slugs",
                "size_optimization": "responsive_webp_fallback"
            },
            # Internal metadata (for tracking only - not published)
            "_internal": {
                "project_name": project.name,
                "keyword": keyword,
                "generation_method": content_data['generation_method'],
                "generated_date": datetime.now().isoformat(),
                "word_count": len(content_with_images.split()),
                "target_audience": content_data.get('target_audience', 'Not specified'),
                "project_id": project.id
            }
        }
        
        # Create markdown content with YAML front matter
        import yaml
        yaml_content = yaml.dump(front_matter, default_flow_style=False, allow_unicode=True)
        
        # Clean content - remove any existing title if it duplicates the front matter title
        clean_content = content_with_images.strip()
        
        # Remove duplicate title if content starts with the same title
        if clean_content.startswith(f"# {content_data['title']}"):
            lines = clean_content.split('\n')
            clean_content = '\n'.join(lines[1:]).strip()
        
        markdown_content = f"""---
{yaml_content}---

{clean_content}
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return str(filepath)
    
    def run_project(self, project_id: str, batch_size: int = 1):
        """Run a project and generate all content pieces with scheduled publishing queue"""
        
        project = self.get_project(project_id)
        if not project:
            print(f"❌ Project {project_id} not found")
            return
        
        if project.status != "active":
            print(f"⚠️ Project {project.name} is not active")
            return
        
        print(f"🚀 Starting project '{project.name}'")
        print(f"📊 Target: {project.target_count} contents")
        print(f"✅ Completed: {project.completed_count}")
        
        # Calculate remaining content to generate
        remaining_count = project.target_count - project.completed_count
        print(f"🎯 Remaining: {remaining_count}")
        
        if remaining_count <= 0:
            print(f"✅ Project '{project.name}' is already completed!")
            return
        
        # Generate all remaining content pieces
        generated_count = 0
        publishing_queue = []
        
        for i in range(remaining_count):
            if project.completed_count >= project.target_count:
                break
            
            print(f"\n📝 Generating content {project.completed_count + 1}/{project.target_count}")
            
            success = self.generate_content_for_project(project_id)
            if success:
                generated_count += 1
                
                # Calculate publishing time for this content
                if project.publishing_schedule != "immediate":
                    # Calculate scheduled publishing time
                    base_time = datetime.now()
                    if i > 0:  # First content publishes immediately, others are scheduled
                        minutes_delay = i * project.publishing_interval
                        scheduled_time = base_time + timedelta(minutes=minutes_delay)
                    else:
                        scheduled_time = base_time  # First content publishes now
                    
                    # Add to publishing queue
                    publishing_queue.append({
                        'project_id': project_id,
                        'content_index': project.completed_count,
                        'scheduled_time': scheduled_time,
                        'status': 'queued'
                    })
                    
                    print(f"⏰ Content scheduled for publishing at: {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    # Immediate publishing
                    print(f"📤 Publishing content immediately...")
                    # TODO: Implement immediate publishing here
            
            # Reload project to get updated count
            project = self.get_project(project_id)
            
            # Brief pause between generations
            time.sleep(2)
        
        # Save publishing queue to file
        if publishing_queue:
            self.save_publishing_queue(publishing_queue)
            print(f"\n📅 Created publishing queue with {len(publishing_queue)} items")
            print("📋 Publishing Schedule:")
            for item in publishing_queue:
                print(f"   • Content {item['content_index']}: {item['scheduled_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\n✅ Generated {generated_count} contents in this batch")
        
        if project.completed_count >= project.target_count:
            project.status = "completed"
            self.save_projects()
            print(f"🎉 Project '{project.name}' completed successfully!")
        
        return publishing_queue
    
    def save_publishing_queue(self, queue_items: List[Dict]):
        """Save publishing queue to file"""
        queue_file = "publishing_queue.json"
        
        # Load existing queue
        existing_queue = []
        if os.path.exists(queue_file):
            try:
                with open(queue_file, 'r', encoding='utf-8') as f:
                    existing_queue = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load existing queue: {e}")
        
        # Add new items to queue
        for item in queue_items:
            # Convert datetime to string for JSON serialization
            item['scheduled_time'] = item['scheduled_time'].isoformat()
            existing_queue.append(item)
        
        # Save updated queue
        try:
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(existing_queue, f, indent=2, ensure_ascii=False)
            print(f"💾 Publishing queue saved to {queue_file}")
        except Exception as e:
            print(f"❌ Error saving publishing queue: {e}")
    
    def get_publishing_queue(self) -> List[Dict]:
        """Get current publishing queue"""
        queue_file = "publishing_queue.json"
        
        if not os.path.exists(queue_file):
            return []
        
        try:
            with open(queue_file, 'r', encoding='utf-8') as f:
                queue = json.load(f)
            
            # Convert string timestamps back to datetime objects
            for item in queue:
                if isinstance(item['scheduled_time'], str):
                    item['scheduled_time'] = datetime.fromisoformat(item['scheduled_time'])
            
            return queue
        except Exception as e:
            print(f"❌ Error loading publishing queue: {e}")
            return []
    
    def update_queue_item_status(self, project_id: str, content_index: int, status: str):
        """Update status of a queue item"""
        queue = self.get_publishing_queue()
        
        for item in queue:
            if item['project_id'] == project_id and item['content_index'] == content_index:
                item['status'] = status
                break
        
        # Save updated queue
        queue_file = "publishing_queue.json"
        try:
            # Convert datetime objects to strings for JSON
            queue_for_json = []
            for item in queue:
                item_copy = item.copy()
                if isinstance(item_copy['scheduled_time'], datetime):
                    item_copy['scheduled_time'] = item_copy['scheduled_time'].isoformat()
                queue_for_json.append(item_copy)
            
            with open(queue_file, 'w', encoding='utf-8') as f:
                json.dump(queue_for_json, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error updating queue: {e}")

    def _load_research_sites_config(self):
        """Load research sites configuration from file with fallback defaults"""
        config_file = "research_sites_config.json"
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load research sites config: {e}")
        
        # Return default configuration as fallback
        return self._get_default_research_sites()
    
    def _get_default_research_sites(self):
        """Get default research sites configuration"""
        return {
            "english": {
                "marketing": [
                    "https://marketingland.com",
                    "https://contentmarketinginstitute.com",
                    "https://blog.hubspot.com",
                    "https://neilpatel.com/blog",
                    "https://moz.com/blog"
                ],
                "ai_tech": [
                    "https://venturebeat.com",
                    "https://techcrunch.com",
                    "https://www.theverge.com",
                    "https://arstechnica.com",
                    "https://www.wired.com"
                ],
                "business": [
                    "https://hbr.org",
                    "https://www.mckinsey.com/insights",
                    "https://www.bcg.com/insights",
                    "https://sloanreview.mit.edu",
                    "https://knowledge.wharton.upenn.edu"
                ]
            },
            "farsi": {
                "marketing": [
                    "https://www.zoomit.ir",
                    "https://www.digikala.com/mag",
                    "https://www.cafebazaar.ir/blog",
                    "https://www.snappfood.ir/blog",
                    "https://www.tapsi.ir/blog"
                ],
                "business": [
                    "https://www.donya-e-eqtesad.com",
                    "https://www.eghtesadnews.com",
                    "https://www.mehrnews.com/xjsv",
                    "https://www.isna.ir/xjsv",
                    "https://www.tasnimnews.com/fa/service/1"
                ],
                "technology": [
                    "https://www.zoomit.ir",
                    "https://www.gadgetnews.ir",
                    "https://www.technolife.ir/blog",
                    "https://www.digikala.com/mag/category/technology",
                    "https://www.cafebazaar.ir/blog"
                ]
            },
            "spanish": {
                "marketing": [
                    "https://www.marketingnews.es",
                    "https://www.puromarketing.com",
                    "https://www.marketingdirecto.com",
                    "https://www.reasonwhy.es",
                    "https://www.anuncios.com"
                ],
                "business": [
                    "https://www.expansion.com",
                    "https://www.eleconomista.es",
                    "https://www.cincodias.com",
                    "https://www.emprendedores.es",
                    "https://www.forbes.es"
                ],
                "technology": [
                    "https://www.xataka.com",
                    "https://www.genbeta.com",
                    "https://www.applesfera.com",
                    "https://www.androidphoria.com",
                    "https://www.computerhoy.com"
                ]
            }
        }

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters for Windows/Unix filesystems
    
    Args:
        filename: Original filename string
        
    Returns:
        Sanitized filename safe for filesystem use
    """
    # Remove invalid characters for Windows: < > : " | ? * \
    # Also remove other problematic characters
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(invalid_chars, '', filename)
    
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores and dots
    sanitized = sanitized.strip('_.')
    
    # Ensure it's not empty and not too long
    if not sanitized:
        sanitized = "project"
    
    # Limit length to 50 characters to avoid path length issues
    if len(sanitized) > 50:
        sanitized = sanitized[:50].rstrip('_')
    
    return sanitized

def main():
    """Test the project manager"""
    pm = MultilingualProjectManager()
    
    # Example: Create a sample project (for testing only - no default keywords in production)
    project_id = pm.create_project(
        name="Sample Project",
        description="Sample project for testing",
        keywords=[],  # No default keywords - user will input dynamically
        target_count=5,
        content_type="template",
        template_style="trend_analysis",
        seo_focus=[],  # No default SEO keywords - user will input dynamically
        target_audience="",  # No default target audience - user will input dynamically
        content_length="medium"
    )
    
    print("Sample project created for testing purposes")
    print("In production, all keywords and settings will be provided by user")

if __name__ == "__main__":
    main() 