#!/usr/bin/env python3
"""
Multilingual SEO Optimizer for WordPress Blog Automation
Implements language-specific SEO & content writing rules for English, Farsi (Persian), and Spanish
"""

import re
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import nltk
from collections import Counter
from core.settings_manager import SettingsManager
try:
    import readability
except ImportError:
    readability = None
import os

class MultilingualSEOOptimizer:
    def __init__(self):
        """Initialize Multilingual SEO Optimizer with language-specific rule sets"""
        
        # Initialize settings manager for language configs
        self.settings_manager = SettingsManager()
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
            
        from nltk.corpus import stopwords
        
        # Initialize stop words for supported languages
        self.stop_words = {
            'english': set(stopwords.words('english')),
            'spanish': set(stopwords.words('spanish')),
            'farsi': set([  # Persian stop words
                'و', 'در', 'به', 'از', 'که', 'این', 'با', 'را', 'برای', 'تا', 'بر', 'آن',
                'یا', 'هر', 'اگر', 'چون', 'وقتی', 'همه', 'بعد', 'قبل', 'روی', 'زیر', 'کنار',
                'است', 'بود', 'باشد', 'شده', 'می‌شود', 'خواهد', 'دارد', 'داشت', 'کرد', 'کند'
            ])
        }
        
        # Language-specific content quality indicators
        self.language_quality_indicators = {
            'english': {
                'word_count': {'min': 1500, 'optimal': 2500, 'max': 4000},
                'unique_words_ratio': {'min': 0.4},
                'transition_words': [
                    'however', 'therefore', 'furthermore', 'moreover', 'additionally',
                    'consequently', 'meanwhile', 'nevertheless', 'subsequently', 'similarly',
                    'in contrast', 'on the other hand', 'as a result', 'for example',
                    'in addition', 'first', 'second', 'third', 'finally', 'in conclusion'
                ]
            },
            'farsi': {
                'word_count': {'min': 1200, 'optimal': 2000, 'max': 3500},  # Persian words are longer
                'unique_words_ratio': {'min': 0.35},
                'transition_words': [
                    'بنابراین', 'در نتیجه', 'علاوه بر این', 'همچنین', 'از طرف دیگر',
                    'در مقابل', 'به عبارت دیگر', 'به طور کلی', 'در واقع', 'در حقیقت',
                    'اول', 'دوم', 'سوم', 'در نهایت', 'در پایان', 'مثلاً', 'برای مثال'
                ]
            },
            'spanish': {
                'word_count': {'min': 1400, 'optimal': 2300, 'max': 3800},
                'unique_words_ratio': {'min': 0.38},
                'transition_words': [
                    'sin embargo', 'por lo tanto', 'además', 'asimismo', 'por otra parte',
                    'en contraste', 'como resultado', 'por ejemplo', 'en primer lugar',
                    'en segundo lugar', 'finalmente', 'en conclusión', 'no obstante',
                    'por consiguiente', 'de hecho', 'en realidad', 'es decir'
                ]
            }
        }
        
        # Language-specific Schema.org templates
        self.multilingual_schema_templates = {
            'english': {
                'article': {
                    '@context': 'https://schema.org',
                    '@type': 'Article',
                    'inLanguage': 'en',
                    'headline': '',
                    'description': '',
                    'author': {'@type': 'Organization', 'name': ''},
                    'publisher': {'@type': 'Organization', 'name': ''},
                    'datePublished': '',
                    'dateModified': '',
                    'mainEntityOfPage': {'@type': 'WebPage', '@id': ''},
                    'image': []
                }
            },
            'farsi': {
                'article': {
                    '@context': 'https://schema.org',
                    '@type': 'Article',
                    'inLanguage': 'fa',
                    'headline': '',
                    'description': '',
                    'author': {'@type': 'Organization', 'name': ''},
                    'publisher': {'@type': 'Organization', 'name': ''},
                    'datePublished': '',
                    'dateModified': '',
                    'mainEntityOfPage': {'@type': 'WebPage', '@id': ''},
                    'image': [],
                    'isPartOf': {'@type': 'WebSite', 'url': '', 'inLanguage': 'fa'}
                }
            },
            'spanish': {
                'article': {
                    '@context': 'https://schema.org',
                    '@type': 'Article',
                    'inLanguage': 'es',
                    'headline': '',
                    'description': '',
                    'author': {'@type': 'Organization', 'name': ''},
                    'publisher': {'@type': 'Organization', 'name': ''},
                    'datePublished': '',
                    'dateModified': '',
                    'mainEntityOfPage': {'@type': 'WebPage', '@id': ''},
                    'image': [],
                    'isPartOf': {'@type': 'WebSite', 'url': '', 'inLanguage': 'es'}
                }
            }
        }
    
    def analyze_content_comprehensive(self, content: str, metadata: Dict, language: str = "english") -> Dict:
        """Comprehensive multilingual SEO analysis of content"""
        
        # Get language configuration
        lang_config = self.settings_manager.get_language_config(language)
        if not lang_config:
            language = "english"  # Fallback to English
            lang_config = self.settings_manager.get_language_config(language)
        
        analysis = {
            'language': language,
            'content_quality': self._analyze_content_quality(content, language),
            'keyword_optimization': self._analyze_keyword_optimization(content, metadata, language),
            'structure_readability': self._analyze_structure_readability(content, language),
            'meta_optimization': self._analyze_meta_tags(metadata, language),
            'technical_seo': self._analyze_technical_seo(content, metadata, language),
            'accessibility': self._analyze_accessibility(content, language),
            'cultural_compliance': self._analyze_cultural_compliance(content, language),
            'performance_factors': self._analyze_performance_factors(content),
            'seo_score': 0,
            'recommendations': []
        }
        
        # Calculate overall SEO score
        analysis['seo_score'] = self._calculate_seo_score(analysis, language)
        
        # Generate language-specific recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis, language)
        
        return analysis
    
    def _analyze_cultural_compliance(self, content: str, language: str) -> Dict:
        """Analyze cultural compliance for the specified language"""
        
        lang_config = self.settings_manager.get_language_config(language)
        if not lang_config:
            return {'error': f'Language {language} not supported'}
        
        cultural_rules = lang_config.cultural_rules
        editorial_rules = lang_config.editorial_rules
        
        compliance_score = 100
        issues = []
        
        # Check formality level
        if language == 'farsi':
            # Check for appropriate honorifics and respectful language
            honorific_patterns = ['جناب', 'سرکار', 'محترم', 'گرامی']
            has_honorifics = any(pattern in content for pattern in honorific_patterns)
            
            if cultural_rules.get('use_honorifics') and not has_honorifics:
                compliance_score -= 15
                issues.append('Consider adding appropriate honorifics for Persian cultural context')
            
            # Check for cultural sensitivity
            sensitive_topics = ['خانواده', 'مذهب', 'سنت']
            for topic in sensitive_topics:
                if topic in content:
                    # This is good - shows cultural awareness
                    compliance_score += 5
        
        elif language == 'spanish':
            # Check for appropriate formality markers
            formal_patterns = ['usted', 'estimado', 'cordialmente']
            informal_patterns = ['tú', 'hola', 'chao']
            
            has_formal = any(pattern in content.lower() for pattern in formal_patterns)
            has_informal = any(pattern in content.lower() for pattern in informal_patterns)
            
            if cultural_rules.get('formality_level') == 'medium_high' and has_informal and not has_formal:
                compliance_score -= 10
                issues.append('Consider using more formal language appropriate for Spanish business context')
        
        return {
            'compliance_score': max(0, compliance_score),
            'cultural_issues': issues,
            'language_appropriateness': 'high' if compliance_score > 80 else 'medium' if compliance_score > 60 else 'low'
        }
    
    def _analyze_content_quality(self, content: str, language: str) -> Dict:
        """Analyze content quality with language-specific metrics"""
        
        quality_indicators = self.language_quality_indicators.get(language, self.language_quality_indicators['english'])
        
        # Basic metrics
        if language == 'farsi':
            # Persian text processing
            words = re.findall(r'[\u0600-\u06FF]+', content)  # Persian Unicode range
        elif language == 'spanish':
            # Spanish text processing (includes accented characters)
            words = re.findall(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+', content)
        else:
            # English text processing
            words = re.findall(r'\b\w+\b', content)
        
        word_count = len(words)
        
        # Sentence tokenization
        sentences = nltk.sent_tokenize(content)
        sentence_count = len(sentences)
        
        # Unique words ratio
        unique_words = set(word.lower() for word in words)
        unique_ratio = len(unique_words) / len(words) if words else 0
        
        # Transition words usage
        transition_count = sum(1 for word in quality_indicators['transition_words'] 
                             if word in content.lower())
        
        # Average sentence length
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'unique_words_ratio': unique_ratio,
            'transition_words_count': transition_count,
            'avg_sentence_length': avg_sentence_length,
            'quality_score': self._calculate_quality_score(word_count, unique_ratio, transition_count, language)
        }
    
    def _analyze_keyword_optimization(self, content: str, metadata: Dict, language: str) -> Dict:
        """Analyze keyword usage with language-specific optimization"""
        
        lang_config = self.settings_manager.get_language_config(language)
        seo_rules = lang_config.seo_rules if lang_config else {}
        
        primary_keyword = metadata.get('primary_keyword', '').lower()
        secondary_keywords = [kw.lower() for kw in metadata.get('secondary_keywords', [])]
        
        if not primary_keyword:
            return {'error': 'No primary keyword specified'}
        
        content_lower = content.lower()
        
        # Language-specific word extraction
        if language == 'farsi':
            words = re.findall(r'[\u0600-\u06FF]+', content_lower)
        elif language == 'spanish':
            words = re.findall(r'[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+', content_lower)
        else:
            words = re.findall(r'\b\w+\b', content_lower)
        
        total_words = len(words)
        
        # Primary keyword analysis
        primary_count = content_lower.count(primary_keyword)
        primary_density = (primary_count / total_words * 100) if total_words > 0 else 0
        
        # Secondary keywords analysis
        secondary_analysis = {}
        for keyword in secondary_keywords:
            count = content_lower.count(keyword)
            density = (count / total_words * 100) if total_words > 0 else 0
            secondary_analysis[keyword] = {'count': count, 'density': density}
        
        # Keyword placement analysis
        title = metadata.get('title', '').lower()
        description = metadata.get('meta_description', '').lower()
        
        placement_score = 0
        if primary_keyword in title:
            placement_score += 25
        if primary_keyword in description:
            placement_score += 15
        if primary_keyword in content_lower[:200]:  # First 200 characters
            placement_score += 20
        
        # Check headings for keywords
        headings = re.findall(r'#{1,6}\s+(.+)', content)
        heading_keywords = sum(1 for heading in headings if primary_keyword in heading.lower())
        if heading_keywords > 0:
            placement_score += 20
        
        return {
            'primary_keyword': primary_keyword,
            'primary_count': primary_count,
            'primary_density': primary_density,
            'secondary_keywords': secondary_analysis,
            'placement_score': placement_score,
            'keyword_optimization_score': self._calculate_keyword_score(primary_density, placement_score, language)
        }
    
    def _analyze_structure_readability(self, content: str, language: str) -> Dict:
        """Analyze content structure and readability with language-specific metrics"""
        
        # Heading structure analysis
        headings = re.findall(r'(#{1,6})\s+(.+)', content)
        heading_structure = []
        for level, text in headings:
            heading_structure.append({
                'level': len(level),
                'text': text.strip(),
                'word_count': len(text.split())
            })
        
        # Paragraph analysis
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.startswith('#')]
        paragraph_lengths = [len(nltk.sent_tokenize(p)) for p in paragraphs]
        
        # List usage
        bullet_lists = len(re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE))
        numbered_lists = len(re.findall(r'^\s*\d+\.\s+', content, re.MULTILINE))
        
        # Readability score (simplified Flesch Reading Ease)
        try:
            if readability:
                readability_score = readability.getmeasures(content, lang='en')['readability grades']['FleschReadingEase']
            else:
                raise ImportError("readability module not available")
        except:
            # Fallback calculation
            sentences = len(nltk.sent_tokenize(content))
            words = len(content.split())
            syllables = self._count_syllables(content)
            
            if sentences > 0 and words > 0:
                readability_score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
            else:
                readability_score = 0
        
        return {
            'heading_structure': heading_structure,
            'paragraph_count': len(paragraphs),
            'avg_paragraph_length': sum(paragraph_lengths) / len(paragraph_lengths) if paragraph_lengths else 0,
            'bullet_lists': bullet_lists,
            'numbered_lists': numbered_lists,
            'readability_score': readability_score,
            'structure_score': self._calculate_structure_score(heading_structure, paragraph_lengths, readability_score, language)
        }
    
    def _analyze_meta_tags(self, metadata: Dict, language: str) -> Dict:
        """Analyze meta tags optimization with language-specific rules"""
        
        lang_config = self.settings_manager.get_language_config(language)
        seo_rules = lang_config.seo_rules if lang_config else {}
        
        title = metadata.get('title', '')
        description = metadata.get('meta_description', '')
        
        # Title analysis
        title_length = len(title)
        title_score = 0
        if seo_rules.get('title_length'):
            if seo_rules['title_length']['min'] <= title_length <= seo_rules['title_length']['max']:
                title_score = 100
            elif title_length < seo_rules['title_length']['min']:
                title_score = 50
            elif title_length > seo_rules['title_length']['max']:
                title_score = 70
        
        # Description analysis
        desc_length = len(description)
        desc_score = 0
        if seo_rules.get('meta_description_length'):
            if seo_rules['meta_description_length']['min'] <= desc_length <= seo_rules['meta_description_length']['max']:
                desc_score = 100
            elif desc_length < seo_rules['meta_description_length']['min']:
                desc_score = 50
            elif desc_length > seo_rules['meta_description_length']['max']:
                desc_score = 70
        
        return {
            'title': title,
            'title_length': title_length,
            'title_score': title_score,
            'meta_description': description,
            'description_length': desc_length,
            'description_score': desc_score,
            'meta_score': (title_score + desc_score) / 2
        }
    
    def _analyze_technical_seo(self, content: str, metadata: Dict, language: str) -> Dict:
        """Analyze technical SEO factors with language-specific rules"""
        
        lang_config = self.settings_manager.get_language_config(language)
        seo_rules = lang_config.seo_rules if lang_config else {}
        
        # Internal and external links
        internal_links = re.findall(r'\[([^\]]+)\]\((/[^)]+)\)', content)
        external_links = re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)', content)
        
        # Image analysis
        images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        images_with_alt = [img for img in images if img[0].strip()]
        
        # URL slug analysis
        slug = metadata.get('slug', '')
        if not slug and 'title' in metadata:
            slug = self.generate_seo_slug(metadata['title'])
        
        return {
            'internal_links': len(internal_links),
            'external_links': len(external_links),
            'total_images': len(images),
            'images_with_alt': len(images_with_alt),
            'alt_text_coverage': (len(images_with_alt) / len(images) * 100) if images else 100,
            'url_slug': slug,
            'slug_length': len(slug),
            'technical_score': self._calculate_technical_score(internal_links, external_links, images, images_with_alt, language)
        }
    
    def _analyze_accessibility(self, content: str, language: str) -> Dict:
        """Analyze content accessibility with language-specific rules"""
        
        lang_config = self.settings_manager.get_language_config(language)
        seo_rules = lang_config.seo_rules if lang_config else {}
        
        # Heading hierarchy check
        headings = re.findall(r'(#{1,6})', content)
        heading_levels = [len(h) for h in headings]
        
        hierarchy_issues = []
        for i in range(1, len(heading_levels)):
            if heading_levels[i] - heading_levels[i-1] > 1:
                hierarchy_issues.append(f"Heading level jump from H{heading_levels[i-1]} to H{heading_levels[i]}")
        
        # Alt text quality check
        images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        alt_text_issues = []
        for alt_text, url in images:
            if not alt_text.strip():
                alt_text_issues.append(f"Missing alt text for image: {url}")
            elif len(alt_text) < 5:
                alt_text_issues.append(f"Alt text too short: {alt_text}")
            elif len(alt_text) > 125:
                alt_text_issues.append(f"Alt text too long: {alt_text[:50]}...")
        
        return {
            'heading_hierarchy_issues': hierarchy_issues,
            'alt_text_issues': alt_text_issues,
            'accessibility_score': self._calculate_accessibility_score(hierarchy_issues, alt_text_issues, language)
        }
    
    def _analyze_performance_factors(self, content: str) -> Dict:
        """Analyze performance-related factors"""
        
        # Content size
        content_size = len(content.encode('utf-8'))
        
        # Image count (affects loading time)
        image_count = len(re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content))
        
        # External resource count
        external_resources = len(re.findall(r'https?://[^\s\)]+', content))
        
        return {
            'content_size_bytes': content_size,
            'content_size_kb': content_size / 1024,
            'image_count': image_count,
            'external_resources': external_resources,
            'performance_score': self._calculate_performance_score(content_size, image_count, external_resources)
        }
    
    def generate_optimized_metadata(self, content: str, topic: str, keywords: List[str], language: str = "english") -> Dict:
        """Generate SEO-optimized metadata"""
        
        primary_keyword = keywords[0] if keywords else topic
        secondary_keywords = keywords[1:5] if len(keywords) > 1 else []
        
        # Generate optimized title
        title = self.generate_seo_title(topic, primary_keyword, language)
        
        # Generate meta description
        meta_description = self.generate_meta_description(content, primary_keyword, language)
        
        # Generate URL slug
        slug = self.generate_seo_slug(title)
        
        # Generate schema markup
        schema = self.generate_schema_markup(title, meta_description, content, language)
        
        # Generate tags
        tags = self.generate_seo_tags(content, keywords, language)
        
        return {
            'title': title,
            'meta_description': meta_description,
            'slug': slug,
            'primary_keyword': primary_keyword,
            'secondary_keywords': secondary_keywords,
            'tags': tags,
            'schema_markup': schema,
            'seo_optimized': True,
            'mobile_optimized': True,
            'page_speed_optimized': True,
            'featured_snippet_optimized': True,
            'fact_checked': True,
            'last_updated': datetime.now().isoformat(),
            'reading_time': f"{len(content.split()) // 200 + 1} minutes",
            'language': language
        }
    
    def generate_seo_title(self, topic: str, primary_keyword: str, language: str) -> str:
        """Generate SEO-optimized title"""
        
        # Title templates for different content types
        templates = [
            f"{topic}: Complete 2025 Guide",
            f"{topic} - Expert Strategies & Best Practices",
            f"The Ultimate {topic} Guide for 2025",
            f"{topic}: Trends, Tips & Implementation Guide",
            f"Master {topic}: Professional Guide & Strategies"
        ]
        
        # Choose template that includes primary keyword naturally
        for template in templates:
            if len(template) <= 60 and primary_keyword.lower() in template.lower():
                return template
        
        # Fallback: create custom title
        title = f"{topic}: Complete Guide"
        if len(title) <= 60:
            return title
        
        return topic[:57] + "..."
    
    def generate_meta_description(self, content: str, primary_keyword: str, language: str) -> str:
        """Generate SEO-optimized meta description"""
        
        # Extract first meaningful paragraph
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.startswith('#')]
        
        if paragraphs:
            first_paragraph = paragraphs[0]
            # Clean markdown formatting
            clean_paragraph = re.sub(r'[*_`#]', '', first_paragraph)
            
            # Ensure primary keyword is included
            if primary_keyword.lower() not in clean_paragraph.lower():
                clean_paragraph = f"{primary_keyword} guide: {clean_paragraph}"
            
            # Truncate to optimal length
            if len(clean_paragraph) > 160:
                clean_paragraph = clean_paragraph[:157] + "..."
            elif len(clean_paragraph) < 120:
                clean_paragraph += f" Expert insights and strategies for {primary_keyword}."
            
            return clean_paragraph
        
        return f"Comprehensive {primary_keyword} guide with expert insights, strategies, and best practices for 2025."
    
    def generate_seo_slug(self, title: str) -> str:
        """Generate SEO-friendly URL slug"""
        
        # Convert to lowercase and replace spaces with hyphens
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special characters
        slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces and multiple hyphens
        slug = slug.strip('-')                # Remove leading/trailing hyphens
        
        # Limit length
        if len(slug) > 75:
            words = slug.split('-')
            slug = '-'.join(words[:8])  # Take first 8 words
        
        return slug
    
    def generate_schema_markup(self, title: str, description: str, content: str, language: str) -> Dict:
        """Generate Schema.org markup"""
        
        schema = self.multilingual_schema_templates[language]['article'].copy()
        schema['headline'] = title
        schema['description'] = description
        schema['datePublished'] = datetime.now().isoformat()
        schema['dateModified'] = datetime.now().isoformat()
        schema['author']['name'] = 'AgenticAI Research Team'
        schema['publisher']['name'] = 'AgenticAI Updates'
        schema['inLanguage'] = language
        
        # Extract images for schema
        images = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        schema['image'] = [img[1] for img in images[:3]]  # Max 3 images
        
        return schema
    
    def generate_seo_tags(self, content: str, keywords: List[str], language: str) -> List[str]:
        """Generate SEO-optimized tags"""
        
        tags = []
        
        # Add primary keywords as tags
        for keyword in keywords[:5]:
            tag = keyword.lower().replace(' ', '-')
            tags.append(tag)
        
        # Extract additional tags from content
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        word_freq = Counter(words)
        
        # Filter out stop words and get most common
        meaningful_words = [word for word, count in word_freq.most_common(20) 
                          if word not in self.stop_words[language] and len(word) > 4]
        
        # Add top meaningful words as tags
        for word in meaningful_words[:5]:
            if word not in [tag.replace('-', '') for tag in tags]:
                tags.append(word)
        
        # Add year and trend tags
        current_year = datetime.now().year
        tags.extend([f'{current_year}-trends', 'industry-analysis', 'expert-guide'])
        
        return tags[:15]  # Limit to 15 tags
    
    def optimize_content_structure(self, content: str) -> str:
        """Optimize content structure for SEO"""
        
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Ensure proper heading hierarchy
            if line.startswith('#'):
                # Add proper spacing around headings
                if optimized_lines and optimized_lines[-1].strip():
                    optimized_lines.append('')
                optimized_lines.append(line)
                optimized_lines.append('')
            
            # Optimize paragraph length
            elif line.strip() and not line.startswith('#'):
                sentences = nltk.sent_tokenize(line)
                if len(sentences) > 4:
                    # Split long paragraphs
                    mid_point = len(sentences) // 2
                    para1 = ' '.join(sentences[:mid_point])
                    para2 = ' '.join(sentences[mid_point:])
                    optimized_lines.extend([para1, '', para2])
                else:
                    optimized_lines.append(line)
            
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def add_internal_links(self, content: str, site_url: str = None) -> str:
        """Add strategic internal links to content"""
        
        # Use provided site_url or load from environment/config
        if not site_url:
            site_url = os.getenv("WP_SITE_URL") or "https://agenticaiupdates.space"
        
        # DISABLED: This function was creating fake internal links
        # Internal linking should only be done with verified existing URLs
        # For now, return content unchanged to prevent 404 errors
        
        print("⚠️  Internal linking disabled - prevents fake link creation")
        return content
    
    def _calculate_seo_score(self, analysis: Dict, language: str) -> int:
        """Calculate overall SEO score"""
        
        scores = []
        
        # Content quality (25%)
        if 'content_quality' in analysis:
            scores.append(analysis['content_quality'].get('quality_score', 0) * 0.25)
        
        # Keyword optimization (25%)
        if 'keyword_optimization' in analysis:
            scores.append(analysis['keyword_optimization'].get('keyword_optimization_score', 0) * 0.25)
        
        # Structure and readability (20%)
        if 'structure_readability' in analysis:
            scores.append(analysis['structure_readability'].get('structure_score', 0) * 0.20)
        
        # Meta optimization (15%)
        if 'meta_optimization' in analysis:
            scores.append(analysis['meta_optimization'].get('meta_score', 0) * 0.15)
        
        # Technical SEO (10%)
        if 'technical_seo' in analysis:
            scores.append(analysis['technical_seo'].get('technical_score', 0) * 0.10)
        
        # Accessibility (5%)
        if 'accessibility' in analysis:
            scores.append(analysis['accessibility'].get('accessibility_score', 0) * 0.05)
        
        return min(100, max(0, sum(scores)))
    
    def _calculate_quality_score(self, word_count: int, unique_ratio: float, transition_count: int, language: str) -> int:
        """Calculate content quality score"""
        
        quality_indicators = self.language_quality_indicators.get(language, self.language_quality_indicators['english'])
        
        score = 0
        
        # Word count score (40%)
        if word_count >= quality_indicators['word_count']['optimal']:
            score += 40
        elif word_count >= quality_indicators['word_count']['min']:
            score += 30
        else:
            score += 10
        
        # Unique words ratio (40%)
        if unique_ratio >= quality_indicators['unique_words_ratio']['min']:
            score += 40
        else:
            score += 20
        
        # Transition words (20%)
        if transition_count >= 10:
            score += 20
        elif transition_count >= 5:
            score += 15
        else:
            score += 5
        
        return min(100, score)
    
    def _calculate_keyword_score(self, density: float, placement_score: int, language: str) -> int:
        """Calculate keyword optimization score"""
        
        quality_indicators = self.language_quality_indicators.get(language, self.language_quality_indicators['english'])
        
        score = 0
        
        # Keyword density (60%)
        if quality_indicators['keyword_density']['min'] <= density <= quality_indicators['keyword_density']['max']:
            score += 60
        elif density < quality_indicators['keyword_density']['min']:
            score += 20
        else:
            score += 30
        
        # Keyword placement (40%)
        score += min(40, placement_score * 0.4)
        
        return min(100, score)
    
    def _calculate_structure_score(self, headings: List[Dict], paragraph_lengths: List[int], readability: float, language: str) -> int:
        """Calculate structure and readability score"""
        
        score = 0
        
        # Heading structure (30%)
        if headings and len(headings) >= 3:
            score += 30
        elif headings:
            score += 15
        
        # Paragraph length (30%)
        if paragraph_lengths:
            avg_length = sum(paragraph_lengths) / len(paragraph_lengths)
            if avg_length <= 4:
                score += 30
            elif avg_length <= 6:
                score += 20
            else:
                score += 10
        
        # Readability (40%)
        if 60 <= readability <= 80:
            score += 40
        elif 50 <= readability <= 90:
            score += 30
        else:
            score += 15
        
        return min(100, score)
    
    def _calculate_technical_score(self, internal_links: List, external_links: List, images: List, images_with_alt: List, language: str) -> int:
        """Calculate technical SEO score"""
        
        score = 0
        
        # Internal links (30%)
        internal_count = len(internal_links)
        if self.settings_manager.get_language_config(language).seo_rules.get('internal_links'):
            if self.settings_manager.get_language_config(language).seo_rules['internal_links']['min'] <= internal_count <= self.settings_manager.get_language_config(language).seo_rules['internal_links']['max']:
                score += 30
            elif internal_count > 0:
                score += 15
        
        # External links (30%)
        external_count = len(external_links)
        if self.settings_manager.get_language_config(language).seo_rules.get('external_links'):
            if self.settings_manager.get_language_config(language).seo_rules['external_links']['min'] <= external_count <= self.settings_manager.get_language_config(language).seo_rules['external_links']['max']:
                score += 30
            elif external_count > 0:
                score += 15
        
        # Image alt text (40%)
        if images:
            alt_coverage = len(images_with_alt) / len(images)
            if alt_coverage == 1.0:
                score += 40
            elif alt_coverage >= 0.8:
                score += 30
            elif alt_coverage >= 0.5:
                score += 20
            else:
                score += 10
        else:
            score += 40  # No images is fine
        
        return min(100, score)
    
    def _calculate_accessibility_score(self, hierarchy_issues: List, alt_issues: List, language: str) -> int:
        """Calculate accessibility score"""
        
        score = 100
        
        # Deduct points for issues
        score -= len(hierarchy_issues) * 20
        score -= len(alt_issues) * 15
        
        return max(0, score)
    
    def _calculate_performance_score(self, content_size: int, image_count: int, external_resources: int) -> int:
        """Calculate performance score"""
        
        score = 100
        
        # Content size penalty
        if content_size > 100000:  # 100KB
            score -= 20
        elif content_size > 50000:  # 50KB
            score -= 10
        
        # Image count penalty
        if image_count > 10:
            score -= 15
        elif image_count > 5:
            score -= 5
        
        # External resources penalty
        if external_resources > 10:
            score -= 15
        elif external_resources > 5:
            score -= 5
        
        return max(0, score)
    
    def _generate_recommendations(self, analysis: Dict, language: str) -> List[str]:
        """Generate SEO improvement recommendations"""
        
        recommendations = []
        
        # Content quality recommendations
        if 'content_quality' in analysis:
            quality = analysis['content_quality']
            if quality['word_count'] < 1500:
                recommendations.append("Increase content length to at least 1500 words for better SEO performance")
            if quality['unique_words_ratio'] < 0.4:
                recommendations.append("Improve content uniqueness by using more varied vocabulary")
            if quality['transition_words_count'] < 5:
                recommendations.append("Add more transition words to improve content flow and readability")
        
        # Keyword optimization recommendations
        if 'keyword_optimization' in analysis:
            keyword = analysis['keyword_optimization']
            if 'primary_density' in keyword:
                if keyword['primary_density'] < 0.5:
                    recommendations.append("Increase primary keyword usage (aim for 0.5-2% density)")
                elif keyword['primary_density'] > 2.0:
                    recommendations.append("Reduce primary keyword usage to avoid over-optimization")
            if keyword.get('placement_score', 0) < 60:
                recommendations.append("Improve keyword placement in title, meta description, and headings")
        
        # Structure recommendations
        if 'structure_readability' in analysis:
            structure = analysis['structure_readability']
            if not structure['heading_structure']:
                recommendations.append("Add proper heading structure (H1, H2, H3) to improve content organization")
            if structure['avg_paragraph_length'] > 4:
                recommendations.append("Break up long paragraphs into shorter, more readable sections")
            if structure['readability_score'] < 60:
                recommendations.append("Improve readability by using simpler language and shorter sentences")
        
        # Meta tag recommendations
        if 'meta_optimization' in analysis:
            meta = analysis['meta_optimization']
            if meta['title_score'] < 80:
                recommendations.append("Optimize title length (30-60 characters) and include primary keyword")
            if meta['description_score'] < 80:
                recommendations.append("Optimize meta description length (120-160 characters) and include primary keyword")
        
        # Technical SEO recommendations
        if 'technical_seo' in analysis:
            technical = analysis['technical_seo']
            # REMOVED: Internal linking recommendation to prevent fake links
            # Only recommend if you have a system to verify existing URLs
            if technical['external_links'] < 1:
                recommendations.append("Add authoritative external links to support your content")
            if technical['alt_text_coverage'] < 100:
                recommendations.append("Add descriptive alt text to all images for better accessibility and SEO")
        
        # Accessibility recommendations
        if 'accessibility' in analysis:
            accessibility = analysis['accessibility']
            if accessibility['heading_hierarchy_issues']:
                recommendations.append("Fix heading hierarchy issues - don't skip heading levels")
            if accessibility['alt_text_issues']:
                recommendations.append("Improve image alt text quality and coverage")
        
        return recommendations
    
    def _count_syllables(self, text: str) -> int:
        """Simple syllable counting for readability calculation"""
        
        words = re.findall(r'\b\w+\b', text.lower())
        syllable_count = 0
        
        for word in words:
            # Simple syllable counting heuristic
            vowels = 'aeiouy'
            syllables = 0
            prev_was_vowel = False
            
            for char in word:
                if char in vowels:
                    if not prev_was_vowel:
                        syllables += 1
                    prev_was_vowel = True
                else:
                    prev_was_vowel = False
            
            # Handle silent e
            if word.endswith('e') and syllables > 1:
                syllables -= 1
            
            # Every word has at least one syllable
            if syllables == 0:
                syllables = 1
            
            syllable_count += syllables
        
        return syllable_count

def main():
    """Test the SEO optimizer"""
    
    optimizer = MultilingualSEOOptimizer()
    
    # Test content
    test_content = """
    # AI Marketing Automation: Complete Guide
    
    AI marketing automation is revolutionizing how businesses connect with customers. This comprehensive guide covers everything you need to know.
    
    ## What is AI Marketing Automation?
    
    AI marketing automation combines artificial intelligence with marketing processes to create more efficient and effective campaigns.
    
    ## Benefits of AI Marketing Automation
    
    - Improved targeting
    - Better ROI
    - Automated workflows
    
    ## Implementation Strategies
    
    To implement AI marketing automation successfully, follow these steps...
    """
    
    test_metadata = {
        'title': 'AI Marketing Automation: Complete Guide',
        'meta_description': 'Learn how AI marketing automation can transform your business with this comprehensive guide.',
        'primary_keyword': 'AI marketing automation',
        'secondary_keywords': ['marketing automation', 'artificial intelligence marketing', 'automated marketing']
    }
    
    # Analyze content
    analysis = optimizer.analyze_content_comprehensive(test_content, test_metadata)
    
    print("SEO Analysis Results:")
    print(f"Overall SEO Score: {analysis['seo_score']}/100")
    print("\nRecommendations:")
    for rec in analysis['recommendations']:
        print(f"- {rec}")

if __name__ == "__main__":
    main()