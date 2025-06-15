#!/usr/bin/env python3
"""
Enhanced Settings Manager with Multilingual Support
Manages application settings including WordPress websites and language configurations
"""

import json
import os
import uuid
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class WordPressWebsite:
    """WordPress website configuration"""
    id: str
    name: str
    url: str
    username: str
    password: str  # Application password
    description: str = ""
    is_active: bool = True
    created_date: str = ""
    last_tested: str = ""
    test_status: str = "unknown"  # unknown, success, failed
    language: str = "english"  # Default language
    
    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().isoformat()

@dataclass
class LanguageConfig:
    """Language-specific configuration"""
    code: str
    name: str
    native_name: str
    rtl: bool
    cultural_rules: Dict
    editorial_rules: Dict
    seo_rules: Dict
    content_templates: Dict
    
class SettingsManager:
    def __init__(self, settings_file: str = "config/settings.json"):
        self.settings_file = settings_file
        self.settings = self.load_settings()
        self.language_configs = self._initialize_language_configs()
        
        # Load API keys into environment variables
        self._load_api_keys()
    
    def _load_api_keys(self):
        """Load API keys from settings into environment variables"""
        import os
        
        # Load Claude API key
        claude_key = self.settings.get("claude_api_key")
        if claude_key:
            os.environ["ANTHROPIC_API_KEY"] = claude_key
    
    def _initialize_language_configs(self) -> Dict[str, LanguageConfig]:
        """Initialize language-specific configurations"""
        return {
            "english": LanguageConfig(
                code="en",
                name="English",
                native_name="English",
                rtl=False,
                cultural_rules={
                    "communication_style": "direct",
                    "formality_level": "professional",
                    "cultural_context": "western_business",
                    "authority_distance": "low",
                    "individualism": "high",
                    "uncertainty_avoidance": "medium",
                    "time_orientation": "short_term",
                    "preferred_content_length": "medium_to_long",
                    "visual_preferences": "clean_modern",
                    "color_associations": {
                        "trust": ["blue", "navy"],
                        "success": ["green"],
                        "warning": ["orange", "yellow"],
                        "error": ["red"]
                    }
                },
                editorial_rules={
                    "tone": "professional_friendly",
                    "voice": "authoritative_helpful",
                    "sentence_structure": "varied",
                    "paragraph_length": "medium",
                    "use_contractions": True,
                    "use_active_voice": True,
                    "technical_level": "intermediate",
                    "examples_style": "practical_business",
                    "call_to_action_style": "direct_encouraging"
                },
                seo_rules={
                    "title_length": {"min": 30, "max": 60},
                    "meta_description_length": {"min": 120, "max": 160},
                    "keyword_density": {"min": 0.5, "max": 2.0},
                    "heading_structure": ["h1", "h2", "h3", "h4"],
                    "internal_links": {"min": 2, "max": 8},
                    "external_links": {"min": 1, "max": 5},
                    "readability_target": "flesch_60_80",
                    "sentence_length_max": 20,
                    "paragraph_sentences_max": 4
                },
                content_templates={
                    "greeting": "Welcome to",
                    "conclusion": "In conclusion",
                    "call_to_action": "Take action now",
                    "learn_more": "Learn more about"
                }
            ),
            
            "farsi": LanguageConfig(
                code="fa",
                name="Farsi (Persian)",
                native_name="فارسی",
                rtl=True,
                cultural_rules={
                    "communication_style": "indirect_respectful",
                    "formality_level": "high",
                    "cultural_context": "persian_islamic",
                    "authority_distance": "high",
                    "individualism": "medium",
                    "uncertainty_avoidance": "high",
                    "time_orientation": "long_term",
                    "preferred_content_length": "detailed_comprehensive",
                    "visual_preferences": "elegant_traditional",
                    "respect_hierarchy": True,
                    "use_honorifics": True,
                    "cultural_sensitivity": {
                        "religious_considerations": True,
                        "family_values": "high_importance",
                        "hospitality": "essential",
                        "respect_for_elders": True
                    },
                    "color_associations": {
                        "trust": ["blue", "turquoise"],
                        "success": ["green", "gold"],
                        "wisdom": ["purple", "deep_blue"],
                        "prosperity": ["gold", "emerald"]
                    },
                    "number_preferences": {
                        "use_persian_numerals": True,
                        "lucky_numbers": [7, 8],
                        "avoid_numbers": [13]
                    }
                },
                editorial_rules={
                    "tone": "respectful_formal",
                    "voice": "knowledgeable_humble",
                    "sentence_structure": "complex_elegant",
                    "paragraph_length": "longer",
                    "use_contractions": False,
                    "use_active_voice": True,
                    "technical_level": "detailed",
                    "examples_style": "cultural_relevant",
                    "call_to_action_style": "respectful_inviting",
                    "honorific_usage": "appropriate",
                    "metaphor_style": "persian_literary",
                    "storytelling": "narrative_rich",
                    "poetry_integration": "subtle_appropriate"
                },
                seo_rules={
                    "title_length": {"min": 25, "max": 55},  # Persian characters are wider
                    "meta_description_length": {"min": 100, "max": 140},
                    "keyword_density": {"min": 0.8, "max": 2.5},  # Higher for Persian SEO
                    "heading_structure": ["h1", "h2", "h3", "h4", "h5"],
                    "internal_links": {"min": 3, "max": 10},
                    "external_links": {"min": 2, "max": 6},
                    "readability_target": "persian_standard",
                    "sentence_length_max": 25,  # Persian sentences can be longer
                    "paragraph_sentences_max": 5,
                    "rtl_optimization": True,
                    "persian_seo_factors": {
                        "use_persian_keywords": True,
                        "local_search_optimization": True,
                        "cultural_keyword_integration": True
                    }
                },
                content_templates={
                    "greeting": "به ... خوش آمدید",
                    "conclusion": "در نتیجه",
                    "call_to_action": "همین حالا اقدام کنید",
                    "learn_more": "بیشتر بدانید درباره",
                    "respectful_address": "جناب آقای / سرکار خانم",
                    "blessing": "به امید موفقیت شما"
                }
            ),
            
            "spanish": LanguageConfig(
                code="es",
                name="Spanish",
                native_name="Español",
                rtl=False,
                cultural_rules={
                    "communication_style": "warm_expressive",
                    "formality_level": "medium_high",
                    "cultural_context": "hispanic_latin",
                    "authority_distance": "medium_high",
                    "individualism": "medium",
                    "uncertainty_avoidance": "high",
                    "time_orientation": "relationship_focused",
                    "preferred_content_length": "comprehensive_detailed",
                    "visual_preferences": "vibrant_warm",
                    "family_orientation": "high",
                    "relationship_importance": "very_high",
                    "cultural_sensitivity": {
                        "religious_considerations": True,
                        "family_values": "central",
                        "community_focus": True,
                        "respect_traditions": True
                    },
                    "color_associations": {
                        "trust": ["blue", "navy"],
                        "success": ["green", "gold"],
                        "passion": ["red", "orange"],
                        "wisdom": ["purple", "deep_blue"],
                        "celebration": ["bright_colors"]
                    },
                    "regional_considerations": {
                        "spain": "formal_traditional",
                        "mexico": "warm_family_oriented",
                        "argentina": "sophisticated_european",
                        "colombia": "friendly_business_focused"
                    }
                },
                editorial_rules={
                    "tone": "warm_professional",
                    "voice": "knowledgeable_approachable",
                    "sentence_structure": "flowing_expressive",
                    "paragraph_length": "medium_long",
                    "use_contractions": False,  # More formal in Spanish
                    "use_active_voice": True,
                    "technical_level": "accessible_detailed",
                    "examples_style": "culturally_relevant",
                    "call_to_action_style": "encouraging_motivational",
                    "formality_markers": "appropriate_usted_tu",
                    "emotional_expression": "moderate_warm",
                    "storytelling": "narrative_engaging",
                    "cultural_references": "hispanic_appropriate"
                },
                seo_rules={
                    "title_length": {"min": 35, "max": 65},  # Spanish titles tend to be longer
                    "meta_description_length": {"min": 130, "max": 170},
                    "keyword_density": {"min": 0.7, "max": 2.2},
                    "heading_structure": ["h1", "h2", "h3", "h4", "h5"],
                    "internal_links": {"min": 3, "max": 9},
                    "external_links": {"min": 2, "max": 6},
                    "readability_target": "spanish_standard",
                    "sentence_length_max": 22,
                    "paragraph_sentences_max": 5,
                    "spanish_seo_factors": {
                        "use_spanish_keywords": True,
                        "regional_optimization": True,
                        "cultural_keyword_integration": True,
                        "accent_mark_optimization": True
                    }
                },
                content_templates={
                    "greeting": "Bienvenido a",
                    "conclusion": "En conclusión",
                    "call_to_action": "Actúa ahora",
                    "learn_more": "Aprende más sobre",
                    "formal_address": "Estimado/a",
                    "closing": "Saludos cordiales"
                }
            )
        }
    
    def load_settings(self) -> Dict:
        """Load settings from file"""
        default_settings = {
            "wordpress_websites": {},
            "default_website": None,
            "auto_publish": True,
            "backup_enabled": True,
            "max_retries": 3,
            "timeout": 30,
            "image_quality": 85,
            "seo_enabled": True,
            "analytics_enabled": False,
            "default_language": "english",
            "supported_languages": ["english", "farsi", "spanish"],
            "language_specific_settings": {
                "english": {"enabled": True},
                "farsi": {"enabled": True},
                "spanish": {"enabled": True}
            }
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_settings.update(loaded_settings)
                    return default_settings
            except Exception as e:
                print(f"Error loading settings: {e}")
                return default_settings
        
        return default_settings
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def add_wordpress_website(self, website: WordPressWebsite) -> bool:
        """Add a new WordPress website"""
        try:
            self.settings["wordpress_websites"][website.id] = asdict(website)
            
            # Set as default if it's the first website
            if not self.settings["default_website"]:
                self.settings["default_website"] = website.id
            
            return self.save_settings()
        except Exception as e:
            print(f"Error adding WordPress website: {e}")
            return False
    
    def update_wordpress_website(self, website_id: str, website: WordPressWebsite) -> bool:
        """Update an existing WordPress website"""
        try:
            if website_id in self.settings["wordpress_websites"]:
                self.settings["wordpress_websites"][website_id] = asdict(website)
                return self.save_settings()
            return False
        except Exception as e:
            print(f"Error updating WordPress website: {e}")
            return False
    
    def remove_wordpress_website(self, website_id: str) -> bool:
        """Remove a WordPress website"""
        try:
            if website_id in self.settings["wordpress_websites"]:
                del self.settings["wordpress_websites"][website_id]
                
                # Update default if removed website was default
                if self.settings["default_website"] == website_id:
                    remaining_websites = list(self.settings["wordpress_websites"].keys())
                    self.settings["default_website"] = remaining_websites[0] if remaining_websites else None
                
                return self.save_settings()
            return False
        except Exception as e:
            print(f"Error removing WordPress website: {e}")
            return False
    
    def get_wordpress_website(self, website_id: str) -> Optional[WordPressWebsite]:
        """Get a specific WordPress website"""
        website_data = self.settings["wordpress_websites"].get(website_id)
        if website_data:
            return WordPressWebsite(**website_data)
        return None
    
    def list_wordpress_websites(self) -> List[WordPressWebsite]:
        """Get all WordPress websites"""
        websites = []
        for website_data in self.settings["wordpress_websites"].values():
            websites.append(WordPressWebsite(**website_data))
        return websites
    
    def get_active_websites(self) -> List[WordPressWebsite]:
        """Get only active WordPress websites"""
        return [site for site in self.list_wordpress_websites() if site.is_active]
    
    def get_default_website(self) -> Optional[WordPressWebsite]:
        """Get the default WordPress website"""
        default_id = self.settings.get("default_website")
        if default_id:
            return self.get_wordpress_website(default_id)
        return None
    
    def set_default_website(self, website_id: str) -> bool:
        """Set default WordPress website"""
        if website_id in self.settings["wordpress_websites"]:
            self.settings["default_website"] = website_id
            return self.save_settings()
        return False
    
    def test_wordpress_connection(self, website: WordPressWebsite) -> bool:
        """Test connection to WordPress website"""
        try:
            import requests
            from requests.auth import HTTPBasicAuth
            
            # Test WordPress REST API
            api_url = f"{website.url.rstrip('/')}/wp-json/wp/v2/posts"
            
            response = requests.get(
                api_url,
                auth=HTTPBasicAuth(website.username, website.password),
                timeout=10,
                params={'per_page': 1}
            )
            
            success = response.status_code == 200
            
            # Update test status
            website.last_tested = datetime.now().isoformat()
            website.test_status = "success" if success else "failed"
            self.update_wordpress_website(website.id, website)
            
            return success
            
        except Exception as e:
            print(f"Error testing WordPress connection: {e}")
            website.last_tested = datetime.now().isoformat()
            website.test_status = "failed"
            self.update_wordpress_website(website.id, website)
            return False
    
    def get_setting(self, key: str, default=None):
        """Get a specific setting"""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value) -> bool:
        """Set a specific setting"""
        self.settings[key] = value
        return self.save_settings()
    
    def export_settings(self, export_file: str) -> bool:
        """Export settings to a file"""
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, import_file: str) -> bool:
        """Import settings from a file"""
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
                self.settings.update(imported_settings)
                return self.save_settings()
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False
    
    def get_language_config(self, language: str) -> Optional[LanguageConfig]:
        """Get language configuration"""
        return self.language_configs.get(language)
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.settings.get("supported_languages", ["english"])
    
    def set_default_language(self, language: str):
        """Set default language"""
        if language in self.language_configs:
            self.settings["default_language"] = language
            self.save_settings()
            return True
        return False
    
    def get_default_language(self) -> str:
        """Get default language"""
        return self.settings.get("default_language", "english")

def main():
    """Test the settings manager - FOR TESTING PURPOSES ONLY"""
    settings = SettingsManager()
    
    # Test adding a WordPress website (TEST DATA ONLY - NOT FOR PRODUCTION)
    test_site = WordPressWebsite(
        id="test_site_1",
        name="Test Blog",
        url="https://example.com",  # Example URL for testing only
        username="admin",  # Test username
        password="test_password",  # Test password - replace with real credentials
        description="Test WordPress site for development/testing"
    )
    
    print("Adding test website...")
    success = settings.add_wordpress_website(test_site)
    print(f"Success: {success}")
    
    # List websites
    print("\nWordPress websites:")
    for site in settings.list_wordpress_websites():
        print(f"- {site.name}: {site.url}")
    
    print(f"\nDefault website: {settings.get_default_website()}")
    print("\nNOTE: This is test data only. In production, use real website credentials.")

if __name__ == "__main__":
    main() 