"""
Core system components for AI-powered multilingual content management system.

This module contains the essential system modules and engines:
- Enhanced Research LLM Generator
- Project Manager
- Settings Manager
- Web Research Engine
- Local LLM Integration
"""

from .enhanced_research_llm import EnhancedResearchLLMGenerator
from .project_manager import MultilingualProjectManager, ContentProject
from .settings_manager import SettingsManager
from .web_research_content import WebResearchContentGenerator
from .local_llm_content import MultilingualLocalLLMContentGenerator

__all__ = [
    'EnhancedResearchLLMGenerator',
    'MultilingualProjectManager',
    'ContentProject',
    'SettingsManager',
    'WebResearchContentGenerator',
    'MultilingualLocalLLMContentGenerator'
]

__version__ = "1.0.0" 