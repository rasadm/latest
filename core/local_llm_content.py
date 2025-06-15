#!/usr/bin/env python3
"""
Enhanced Multilingual Local LLM Content Generator
Supports English, Farsi (Persian), and Spanish content generation with cultural awareness
"""

import os
import json
import time
import random
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from core.settings_manager import SettingsManager

class MultilingualLocalLLMContentGenerator:
    def __init__(self):
        self.settings_manager = SettingsManager()
        
        # LLM Provider configurations
        self.providers = {
            "deepseek": {
                "api_url": "http://localhost:11434/api/generate",
                "model": "deepseek-coder:6.7b",
                "cost_per_token": 0.0,
                "max_tokens": 32768  # DeepSeek has large context window
            },
            "deepseek-32b": {
                "api_url": "http://localhost:11434/api/generate", 
                "model": "deepseek-coder:32b",
                "cost_per_token": 0.0,
                "max_tokens": 32768  # Even larger context for 32B model
            },
            "deepseek-14b": {
                "api_url": "http://localhost:11434/api/generate",
                "model": "deepseek-coder:14b", 
                "cost_per_token": 0.0,
                "max_tokens": 32768  # Large context window
            },
            "llama3.3:latest": {
                "api_url": "http://localhost:11434/api/generate",
                "model": "llama3.3:latest",
                "cost_per_token": 0.0,
                "max_tokens": 16384  # Llama 3.3 context window
            },
            "ollama": {
                "api_url": "http://localhost:11434/api/generate",
                "model": "llama2:7b",
                "cost_per_token": 0.0,
                "max_tokens": 8192  # Older model, more conservative
            },
            "llamacpp": {
                "api_url": "http://localhost:8080/completion",
                "model": "local",
                "cost_per_token": 0.0,
                "max_tokens": 16384  # Configurable based on loaded model
            },
            "claude": {
                "api_url": "https://api.anthropic.com/v1/messages",
                "model": "claude-3-5-sonnet-20241022",
                "cost_per_token": 0.003,
                "max_tokens": 8192,
                "api_key_required": True
            }
        }
        
        self.current_provider = "deepseek"  # Default to DeepSeek
        
        # Load multilingual content topics from config
        self.multilingual_topics = self._load_multilingual_topics_config()

    def _load_multilingual_topics_config(self):
        """Load multilingual topics configuration from file with fallback defaults"""
        config_file = "multilingual_topics_config.json"
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load multilingual topics config: {e}")
        
        # Return default configuration as fallback
        return self._get_default_multilingual_topics()
    
    def _get_default_multilingual_topics(self):
        """Get default multilingual topics configuration"""
        return {
            "english": [
                "AI Marketing Automation Trends",
                "Machine Learning in Customer Experience", 
                "Predictive Analytics for Marketing",
                "Conversational AI and Chatbots",
                "AI-Powered Content Personalization",
                "Marketing Attribution with AI",
                "Voice Search Optimization",
                "AI in Social Media Marketing",
                "Programmatic Advertising Evolution",
                "Customer Data Platform Innovation"
            ],
            "farsi": [
                "روندهای اتوماسیون بازاریابی هوش مصنوعی",
                "یادگیری ماشین در تجربه مشتری",
                "تحلیل پیش‌بینی برای بازاریابی",
                "هوش مصنوعی مکالمه‌ای و چت‌بات‌ها",
                "شخصی‌سازی محتوا با هوش مصنوعی",
                "انتساب بازاریابی با هوش مصنوعی",
                "بهینه‌سازی جستجوی صوتی",
                "هوش مصنوعی در بازاریابی شبکه‌های اجتماعی",
                "تکامل تبلیغات برنامه‌ای",
                "نوآوری در پلتفرم داده‌های مشتری"
            ],
            "spanish": [
                "Tendencias de Automatización de Marketing con IA",
                "Aprendizaje Automático en la Experiencia del Cliente",
                "Análisis Predictivo para Marketing",
                "IA Conversacional y Chatbots",
                "Personalización de Contenido con IA",
                "Atribución de Marketing con IA",
                "Optimización de Búsqueda por Voz",
                "IA en Marketing de Redes Sociales",
                "Evolución de la Publicidad Programática",
                "Innovación en Plataformas de Datos de Clientes"
            ]
        }

    def set_provider(self, provider: str, custom_config: Dict = None):
        """Set the local LLM provider"""
        if provider in self.providers:
            self.current_provider = provider
        elif custom_config:
            self.providers[provider] = custom_config
            self.current_provider = provider
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def test_connection(self, provider: str = None) -> bool:
        """Test connection to local LLM"""
        test_provider = provider or self.current_provider
        config = self.providers[test_provider]
        
        try:
            if test_provider == "claude":
                # Claude API format
                import os
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if not api_key:
                    print("❌ ANTHROPIC_API_KEY environment variable not set")
                    return False
                
                headers = {
                    "x-api-key": api_key,
                    "content-type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                
                response = requests.post(
                    config["api_url"],
                    headers=headers,
                    json={
                        "model": config["model"],
                        "max_tokens": 10,
                        "messages": [{"role": "user", "content": "Hello"}]
                    },
                    timeout=30
                )
                return response.status_code == 200
                
            elif test_provider in ["deepseek", "deepseek-32b", "deepseek-14b", "llama3.3:latest", "ollama"]:
                # Ollama API format
                response = requests.post(
                    config["api_url"],
                    json={
                        "model": config["model"],
                        "prompt": "Hello",
                        "stream": False,
                        "options": {"max_tokens": 10}
                    },
                    timeout=30
                )
                return response.status_code == 200
            else:
                # llama.cpp format
                response = requests.post(
                    config["api_url"],
                    json={
                        "prompt": "Hello",
                        "n_predict": 10
                    },
                    timeout=30
                )
                return response.status_code == 200
                
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def generate_content_with_local_llm(self, topic: str, content_type: str = "blog_post", language: str = "english") -> str:
        """Generate multilingual content using local LLM"""
        
        prompt = self.create_multilingual_content_prompt(topic, content_type, language)
        config = self.providers[self.current_provider]
        
        try:
            if self.current_provider in ["deepseek", "deepseek-32b", "deepseek-14b", "llama3.3:latest", "ollama"]:
                # Ollama API format
                response = requests.post(
                    config["api_url"],
                    json={
                        "model": config["model"],
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "max_tokens": config["max_tokens"]
                        }
                    },
                    timeout=300  # RTX 5090 generating 4K+ word content needs more time
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                
            else:
                # llama.cpp format
                response = requests.post(
                    config["api_url"],
                    json={
                        "prompt": prompt,
                        "n_predict": config["max_tokens"],
                        "temperature": 0.7,
                        "top_p": 0.9
                    },
                    timeout=300  # Extended timeout for comprehensive content
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("content", "")
            
            print(f"❌ LLM API error: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"❌ Error generating content: {e}")
            return None
    
    def create_multilingual_content_prompt(self, topic: str, content_type: str, language: str) -> str:
        """Create language-specific optimized prompt for local LLM"""
        
        lang_config = self.settings_manager.get_language_config(language)
        if not lang_config:
            language = "english"  # Fallback
            lang_config = self.settings_manager.get_language_config(language)
        
        cultural_rules = lang_config.cultural_rules
        editorial_rules = lang_config.editorial_rules
        content_templates = lang_config.content_templates
        
        if content_type == "blog_post":
            if language == "english":
                return self._create_english_blog_prompt(topic, cultural_rules, editorial_rules)
            elif language == "farsi":
                return self._create_farsi_blog_prompt(topic, cultural_rules, editorial_rules, content_templates)
            elif language == "spanish":
                return self._create_spanish_blog_prompt(topic, cultural_rules, editorial_rules, content_templates)
        
        elif content_type == "section":
            if language == "english":
                return self._create_english_section_prompt(topic)
            elif language == "farsi":
                return self._create_farsi_section_prompt(topic, content_templates)
            elif language == "spanish":
                return self._create_spanish_section_prompt(topic, content_templates)
        
        else:
            return f"Write professional marketing content about: {topic}"
    
    def _create_english_blog_prompt(self, topic: str, cultural_rules: Dict, editorial_rules: Dict) -> str:
        """Create English blog post prompt"""
        return f"""Write a comprehensive, in-depth 3500-4000 word blog post about "{topic}" for modern marketers. With your expanded context window, create the most detailed and valuable content possible.

Structure:
1. Executive Summary (300 words)
2. Introduction & Market Context (400 words)
3. Current State Analysis (600 words)
4. Key Trends and Technologies (800 words)
5. Implementation Strategies & Best Practices (700 words)
6. Case Studies & Real-World Examples (500 words)
7. Challenges & Solutions (400 words)
8. Future Outlook & Predictions (500 words)
9. Actionable Recommendations (300 words)
10. Conclusion (200 words)

Requirements:
- Professional, authoritative tone with expert-level insights
- Include specific statistics, data points, and research findings
- Provide detailed, actionable strategies with step-by-step guidance
- Focus on practical implementation with real-world examples
- Target audience: Marketing professionals, business leaders, and decision-makers
- Include relevant case studies from major companies
- Add specific tools, platforms, and technologies mentioned by name
- Include budget considerations and ROI expectations
- Provide timeline estimates for implementation
- Address common challenges and their solutions
- Use markdown formatting with proper headers, lists, and emphasis
- Include relevant quotes from industry experts (create realistic ones)
- Add specific metrics and KPIs to track success

Topic: {topic}

Create the most comprehensive, valuable, and actionable blog post possible. Use your full context window to provide maximum value:"""
    
    def _create_farsi_blog_prompt(self, topic: str, cultural_rules: Dict, editorial_rules: Dict, content_templates: Dict) -> str:
        """Create Farsi (Persian) blog post prompt with cultural considerations"""
        return f"""یک مقاله جامع و عمیق ۳۰۰۰-۳۵۰۰ کلمه‌ای درباره "{topic}" برای بازاریابان مدرن بنویسید. با در نظر گیری فرهنگ و ارزش‌های ایرانی، محتوایی ارزشمند و کاربردی ایجاد کنید.

ساختار:
۱. خلاصه اجرایی (۲۵۰ کلمه)
۲. مقدمه و زمینه بازار (۳۵۰ کلمه)
۳. تحلیل وضعیت فعلی (۵۰۰ کلمه)
۴. روندها و فناوری‌های کلیدی (۷۰۰ کلمه)
۵. استراتژی‌های پیاده‌سازی و بهترین شیوه‌ها (۶۰۰ کلمه)
۶. مطالعات موردی و نمونه‌های واقعی (۴۵۰ کلمه)
۷. چالش‌ها و راه‌حل‌ها (۳۵۰ کلمه)
۸. چشم‌انداز آینده و پیش‌بینی‌ها (۴۵۰ کلمه)
۹. توصیه‌های عملی (۲۵۰ کلمه)
۱۰. نتیجه‌گیری (۱۵۰ کلمه)

الزامات فرهنگی و ویراستاری:
- لحن محترمانه و رسمی با بینش‌های تخصصی
- استفاده از عبارات مؤدبانه و احترام‌آمیز
- در نظر گیری ارزش‌های خانوادگی و اجتماعی ایرانی
- ارائه آمار و داده‌های دقیق و قابل اعتماد
- راهنمایی‌های عملی و قابل اجرا با مراحل مشخص
- مخاطب هدف: متخصصان بازاریابی، رهبران کسب‌وکار، و تصمیم‌گیرندگان
- شامل مطالعات موردی از شرکت‌های معتبر
- ذکر ابزارها، پلتفرم‌ها و فناوری‌های مشخص
- در نظر گیری بودجه و انتظارات بازگشت سرمایه
- ارائه برآورد زمانی برای پیاده‌سازی
- پرداختن به چالش‌های رایج و راه‌حل‌های آن‌ها
- استفاده از قالب‌بندی مارک‌داون با سرتیترها، فهرست‌ها و تأکیدات مناسب
- شامل نقل‌قول‌های مرتبط از کارشناسان صنعت
- اضافه کردن معیارها و شاخص‌های کلیدی عملکرد

موضوع: {topic}

{content_templates.get('respectful_address', 'جناب آقای / سرکار خانم')} خواننده محترم،

جامع‌ترین، ارزشمندترین و کاربردی‌ترین مقاله ممکن را ایجاد کنید. از تمام ظرفیت خود برای ارائه حداکثر ارزش استفاده کنید:"""
    
    def _create_spanish_blog_prompt(self, topic: str, cultural_rules: Dict, editorial_rules: Dict, content_templates: Dict) -> str:
        """Create Spanish blog post prompt with cultural considerations"""
        return f"""Escriba un artículo integral y profundo de 3200-3700 palabras sobre "{topic}" para profesionales de marketing modernos. Considerando la cultura hispana y los valores familiares, cree contenido valioso y práctico.

Estructura:
1. Resumen Ejecutivo (280 palabras)
2. Introducción y Contexto del Mercado (380 palabras)
3. Análisis del Estado Actual (550 palabras)
4. Tendencias y Tecnologías Clave (750 palabras)
5. Estrategias de Implementación y Mejores Prácticas (650 palabras)
6. Estudios de Caso y Ejemplos del Mundo Real (480 palabras)
7. Desafíos y Soluciones (380 palabras)
8. Perspectivas Futuras y Predicciones (480 palabras)
9. Recomendaciones Prácticas (280 palabras)
10. Conclusión (180 palabras)

Requisitos Culturales y Editoriales:
- Tono cálido y profesional con perspectivas expertas
- Enfoque en relaciones y valores familiares cuando sea apropiado
- Consideración de la diversidad regional hispana
- Incluir estadísticas específicas, datos y hallazgos de investigación
- Proporcionar estrategias detalladas y prácticas con orientación paso a paso
- Enfoque en implementación práctica con ejemplos del mundo real
- Audiencia objetivo: Profesionales de marketing, líderes empresariales y tomadores de decisiones
- Incluir estudios de caso relevantes de empresas importantes
- Agregar herramientas, plataformas y tecnologías específicas mencionadas por nombre
- Incluir consideraciones presupuestarias y expectativas de ROI
- Proporcionar estimaciones de tiempo para la implementación
- Abordar desafíos comunes y sus soluciones
- Usar formato markdown con encabezados, listas y énfasis apropiados
- Incluir citas relevantes de expertos de la industria (crear realistas)
- Agregar métricas específicas y KPIs para rastrear el éxito

Tema: {topic}

{content_templates.get('formal_address', 'Estimado/a')} profesional,

Cree el artículo más completo, valioso y práctico posible. Use toda su capacidad para proporcionar el máximo valor:"""
    
    def _create_english_section_prompt(self, topic: str) -> str:
        """Create English section prompt"""
        return f"""Write a comprehensive 600-800 word section about "{topic}" for a marketing blog post. With increased context capacity, provide maximum detail and value.

Requirements:
- Professional, expert-level tone
- Include specific examples with company names and results
- Provide detailed, actionable insights with step-by-step guidance
- Use relevant data, statistics, and research findings
- Focus on practical implementation value for marketers
- Include specific tools, platforms, and technologies
- Add budget considerations and timeline estimates
- Address potential challenges and solutions
- Use proper markdown formatting with subheadings and lists
- Include relevant metrics and KPIs

Create the most detailed and valuable section possible:"""
    
    def _create_farsi_section_prompt(self, topic: str, content_templates: Dict) -> str:
        """Create Farsi section prompt"""
        return f"""بخش جامع ۵۰۰-۷۰۰ کلمه‌ای درباره "{topic}" برای مقاله بازاریابی بنویسید. با ظرفیت افزایش‌یافته، حداکثر جزئیات و ارزش را ارائه دهید.

الزامات:
- لحن حرفه‌ای و تخصصی
- شامل نمونه‌های مشخص با نام شرکت‌ها و نتایج
- ارائه بینش‌های دقیق و عملی با راهنمایی گام‌به‌گام
- استفاده از داده‌ها، آمار و یافته‌های تحقیقاتی مرتبط
- تمرکز بر ارزش پیاده‌سازی عملی برای بازاریابان
- شامل ابزارها، پلتفرم‌ها و فناوری‌های مشخص
- اضافه کردن ملاحظات بودجه و برآورد زمانی
- پرداختن به چالش‌های احتمالی و راه‌حل‌ها
- استفاده از قالب‌بندی مارک‌داون مناسب با زیرعنوان‌ها و فهرست‌ها
- شامل معیارها و شاخص‌های کلیدی عملکرد مرتبط

مفصل‌ترین و ارزشمندترین بخش ممکن را ایجاد کنید:"""
    
    def _create_spanish_section_prompt(self, topic: str, content_templates: Dict) -> str:
        """Create Spanish section prompt"""
        return f"""Escriba una sección integral de 550-750 palabras sobre "{topic}" para un artículo de marketing. Con capacidad aumentada, proporcione el máximo detalle y valor.

Requisitos:
- Tono profesional y experto
- Incluir ejemplos específicos con nombres de empresas y resultados
- Proporcionar perspectivas detalladas y prácticas con orientación paso a paso
- Usar datos relevantes, estadísticas y hallazgos de investigación
- Enfoque en valor de implementación práctica para profesionales de marketing
- Incluir herramientas, plataformas y tecnologías específicas
- Agregar consideraciones presupuestarias y estimaciones de tiempo
- Abordar desafíos potenciales y soluciones
- Usar formato markdown apropiado con subtítulos y listas
- Incluir métricas y KPIs relevantes

Cree la sección más detallada y valiosa posible:"""

    def generate_multilingual_blog_post(self, topic: str, language: str = "english") -> Dict:
        """Generate complete multilingual blog post using local LLM"""
        
        print(f"🤖 Generating {language} content with {self.current_provider.upper()}...")
        
        # Generate main content
        content = self.generate_content_with_local_llm(topic, "blog_post", language)
        
        if not content:
            print(f"❌ Failed to generate {language} content with local LLM")
            return None
        
        # Get language configuration for metadata
        lang_config = self.settings_manager.get_language_config(language)
        content_templates = lang_config.content_templates if lang_config else {}
        
        # Create language-specific metadata
        if language == "english":
            title = f"{topic}: {datetime.now().year} Trends and Implementation Guide for Modern Marketers"
            description = f"Comprehensive guide to {topic.lower()} implementation, trends, and best practices for marketing professionals in {datetime.now().year}."
            tags = [
                topic.lower().replace(" ", "-"),
                "ai-marketing",
                "marketing-automation", 
                "digital-transformation",
                f"{datetime.now().year}-trends",
                "local-llm-generated"
            ]
            categories = ["AI Marketing", "Marketing Technology", "Digital Innovation"]
            
        elif language == "farsi":
            title = f"{topic}: راهنمای جامع روندها و پیاده‌سازی برای بازاریابان مدرن {datetime.now().year}"
            description = f"راهنمای کامل پیاده‌سازی {topic}، روندها و بهترین شیوه‌ها برای متخصصان بازاریابی در سال {datetime.now().year}."
            tags = [
                topic.lower().replace(" ", "-"),
                "بازاریابی-هوش-مصنوعی",
                "اتوماسیون-بازاریابی",
                "تحول-دیجیتال",
                f"روندهای-{datetime.now().year}",
                "تولید-محلی-llm"
            ]
            categories = ["بازاریابی هوش مصنوعی", "فناوری بازاریابی", "نوآوری دیجیتال"]
            
        elif language == "spanish":
            title = f"{topic}: Guía Integral de Tendencias e Implementación para Profesionales de Marketing {datetime.now().year}"
            description = f"Guía completa de implementación de {topic.lower()}, tendencias y mejores prácticas para profesionales de marketing en {datetime.now().year}."
            tags = [
                topic.lower().replace(" ", "-"),
                "marketing-ia",
                "automatización-marketing",
                "transformación-digital",
                f"tendencias-{datetime.now().year}",
                "generado-llm-local"
            ]
            categories = ["Marketing IA", "Tecnología de Marketing", "Innovación Digital"]
        
        # Create filename
        filename = title.lower().replace(" ", "-").replace(":", "").replace(",", "")
        filename = "".join(c for c in filename if c.isalnum() or c in "-_")
        filename = f"{filename}-{datetime.now().strftime('%Y-%m-%d')}.md"
        
        # Create YAML front matter
        front_matter = {
            "title": title,
            "description": description,
            "categories": categories,
            "tags": tags,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "author": "RasaDM AI Research Team",
            "reading_time": f"{random.randint(8, 15)} minutes",
            "seo_keywords": ", ".join(tags[:5]),
            "generated_by": f"local_llm_{self.current_provider}",
            "cost": "$0.00 (Local Generation)",
            "model": self.providers[self.current_provider]["model"],
            "language": language,
            "cultural_context": lang_config.cultural_rules.get("cultural_context", "general") if lang_config else "general"
        }
        
        return {
            "title": title,
            "content": content,
            "metadata": front_matter,
            "filename": filename,
            "topic": topic,
            "provider": self.current_provider,
            "language": language
        }

def setup_deepseek_ollama():
    """Setup instructions for DeepSeek with Ollama"""
    
    instructions = """
🚀 Setup DeepSeek with Ollama (Recommended)

1. Install Ollama:
   - Download from: https://ollama.ai
   - Run: ollama serve

2. Install DeepSeek model:
   - Run: ollama pull deepseek-coder:6.7b
   - Or: ollama pull deepseek-llm:7b

3. Test installation:
   - Run: ollama run deepseek-coder:6.7b "Hello"

4. Alternative models:
   - ollama pull llama2:7b (General purpose)
   - ollama pull codellama:7b (Code-focused)
   - ollama pull mistral:7b (Fast and efficient)

💰 Cost Benefits:
- $0.00 per post (vs $0.01-0.05 with cloud APIs)
- Complete privacy (no data sent to external servers)
- Unlimited usage (no rate limits)
- Works offline

🔧 Hardware Requirements:
- Minimum: 8GB RAM, 4GB VRAM
- Recommended: 16GB RAM, 8GB VRAM
- Storage: 4-8GB per model
"""
    
    print(instructions)
    return instructions

def main():
    """Test local LLM content generation"""
    
    generator = MultilingualLocalLLMContentGenerator()
    
    print("🤖 Local LLM Content Generator")
    print("=" * 40)
    
    # Test connection
    if generator.test_connection():
        print(f"✅ Connected to {generator.current_provider}")
        
        # Generate test content
        topic = random.choice(generator.multilingual_topics["english"])
        post_data = generator.generate_multilingual_blog_post(topic)
        
        if post_data:
            file_path = generator.save_local_llm_post(post_data)
            print(f"✅ Generated post saved to: {file_path}")
            print(f"📝 Title: {post_data['title']}")
            print(f"🤖 Provider: {post_data['provider']}")
            print(f"💰 Cost: $0.00 (Local Generation)")
        else:
            print("❌ Failed to generate content")
    else:
        print(f"❌ Cannot connect to {generator.current_provider}")
        print("\n" + setup_deepseek_ollama())

if __name__ == "__main__":
    main() 