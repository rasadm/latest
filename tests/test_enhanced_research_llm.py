#!/usr/bin/env python3
"""
Unit tests for Enhanced Research LLM Generator

This demonstrates how the improved structure supports comprehensive testing
through dependency injection and proper error handling.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import json
from pathlib import Path

# Import the classes we want to test
from core.enhanced_research_llm import (
    EnhancedResearchLLMGenerator, 
    ContentConfig, 
    GenerationResult,
    load_config_from_file
)

class TestContentConfig(unittest.TestCase):
    """Test the ContentConfig dataclass"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = ContentConfig()
        self.assertEqual(config.target_word_count, 3500)
        self.assertTrue(config.use_local_llm)
        self.assertEqual(config.default_llm_provider, "deepseek")
        self.assertEqual(config.output_directory, "serie 1")
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = ContentConfig(
            target_word_count=2000,
            use_local_llm=False,
            default_llm_provider="claude"
        )
        self.assertEqual(config.target_word_count, 2000)
        self.assertFalse(config.use_local_llm)
        self.assertEqual(config.default_llm_provider, "claude")

class TestGenerationResult(unittest.TestCase):
    """Test the GenerationResult dataclass"""
    
    def test_successful_result(self):
        """Test successful generation result"""
        content_data = {"title": "Test Article", "content": "Test content"}
        result = GenerationResult(
            success=True,
            content_data=content_data,
            file_path="/path/to/file.md"
        )
        self.assertTrue(result.success)
        self.assertEqual(result.content_data["title"], "Test Article")
        self.assertEqual(result.file_path, "/path/to/file.md")
        self.assertIsNone(result.error_message)
    
    def test_failed_result(self):
        """Test failed generation result"""
        result = GenerationResult(
            success=False,
            error_message="Generation failed"
        )
        self.assertFalse(result.success)
        self.assertIsNone(result.content_data)
        self.assertEqual(result.error_message, "Generation failed")

class TestConfigLoading(unittest.TestCase):
    """Test configuration file loading"""
    
    def test_load_yaml_config(self):
        """Test loading configuration from YAML file"""
        config_data = {
            "target_word_count": 2000,
            "use_local_llm": False,
            "default_llm_provider": "claude"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            import yaml
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = load_config_from_file(temp_path)
            self.assertIsNotNone(config)
            self.assertEqual(config.target_word_count, 2000)
            self.assertFalse(config.use_local_llm)
            self.assertEqual(config.default_llm_provider, "claude")
        finally:
            Path(temp_path).unlink()
    
    def test_load_json_config(self):
        """Test loading configuration from JSON file"""
        config_data = {
            "target_word_count": 1500,
            "use_local_llm": True,
            "default_llm_provider": "deepseek"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = load_config_from_file(temp_path)
            self.assertIsNotNone(config)
            self.assertEqual(config.target_word_count, 1500)
            self.assertTrue(config.use_local_llm)
        finally:
            Path(temp_path).unlink()
    
    def test_load_nonexistent_config(self):
        """Test loading from non-existent file"""
        config = load_config_from_file("nonexistent.yaml")
        self.assertIsNone(config)

class TestEnhancedResearchLLMGenerator(unittest.TestCase):
    """Test the main generator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.mock_web_researcher = Mock()
        self.mock_local_llm = Mock()
        self.mock_seo_optimizer = Mock()
        
        # Configure mock responses
        self.mock_web_researcher.research_topic_comprehensively.return_value = {
            "articles": [{"title": "Test Article", "description": "Test description"}],
            "statistics": [{"value": "50%", "context": "growth rate"}],
            "key_insights": ["Key insight 1", "Key insight 2"]
        }
        
        self.mock_web_researcher.generate_seo_optimized_content.return_value = {
            "title": "Test Article",
            "content": "Test content",
            "metadata": {"primary_keyword": "test"}
        }
        
        self.mock_local_llm.test_connection.return_value = True
        self.mock_local_llm.generate_content_with_local_llm.return_value = "Enhanced test content"
        
    def test_initialization_with_defaults(self):
        """Test generator initialization with default dependencies"""
        generator = EnhancedResearchLLMGenerator()
        self.assertIsNotNone(generator.config)
        self.assertIsNotNone(generator.web_researcher)
        self.assertIsNotNone(generator.local_llm)
        self.assertIsNotNone(generator.seo_optimizer)
    
    def test_initialization_with_dependency_injection(self):
        """Test generator initialization with injected dependencies"""
        config = ContentConfig(target_word_count=2000)
        
        generator = EnhancedResearchLLMGenerator(
            config=config,
            web_researcher=self.mock_web_researcher,
            local_llm=self.mock_local_llm,
            seo_optimizer=self.mock_seo_optimizer
        )
        
        self.assertEqual(generator.config.target_word_count, 2000)
        self.assertEqual(generator.web_researcher, self.mock_web_researcher)
        self.assertEqual(generator.local_llm, self.mock_local_llm)
        self.assertEqual(generator.seo_optimizer, self.mock_seo_optimizer)
    
    def test_content_generation_success(self):
        """Test successful content generation"""
        generator = EnhancedResearchLLMGenerator(
            web_researcher=self.mock_web_researcher,
            local_llm=self.mock_local_llm,
            seo_optimizer=self.mock_seo_optimizer
        )
        
        # Mock the enhancement method to return content
        with patch.object(generator, 'enhance_with_local_llm') as mock_enhance:
            mock_enhance.return_value = {
                "title": "Enhanced Test Article",
                "content": "Enhanced test content",
                "metadata": {"primary_keyword": "test"}
            }
            
            result = generator.create_comprehensive_research_content("Test Topic")
            
            self.assertTrue(result.success)
            self.assertIsNotNone(result.content_data)
            self.assertEqual(result.content_data["title"], "Enhanced Test Article")
            self.assertIsNone(result.error_message)
    
    def test_content_generation_web_research_failure(self):
        """Test content generation when web research fails"""
        self.mock_web_researcher.generate_seo_optimized_content.return_value = None
        
        generator = EnhancedResearchLLMGenerator(
            web_researcher=self.mock_web_researcher,
            local_llm=self.mock_local_llm,
            seo_optimizer=self.mock_seo_optimizer
        )
        
        result = generator.create_comprehensive_research_content("Test Topic")
        
        self.assertFalse(result.success)
        self.assertIsNone(result.content_data)
        self.assertIsNotNone(result.error_message)
    
    def test_llm_enhancement_failure_fallback(self):
        """Test fallback to web research when LLM enhancement fails"""
        self.mock_local_llm.test_connection.return_value = False
        
        generator = EnhancedResearchLLMGenerator(
            web_researcher=self.mock_web_researcher,
            local_llm=self.mock_local_llm,
            seo_optimizer=self.mock_seo_optimizer
        )
        
        result = generator.create_comprehensive_research_content("Test Topic")
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.content_data)
        # Should use web research content since LLM is not available
        self.assertEqual(result.content_data["title"], "Test Article")

class TestPromptCreation(unittest.TestCase):
    """Test prompt creation methods"""
    
    def test_create_default_prompt(self):
        """Test default prompt creation"""
        generator = EnhancedResearchLLMGenerator()
        
        statistics = [{"value": "50%", "context": "growth rate"}]
        insights = ["Key insight"]
        articles = [{"title": "Test Article", "description": "Test description"}]
        
        prompt = generator._create_default_prompt("Test Topic", statistics, insights, articles)
        
        self.assertIsInstance(prompt, str)
        self.assertIn("Test Topic", prompt)
        self.assertIn("50%", prompt)
        self.assertIn("Key insight", prompt)
        self.assertIn("Test Article", prompt)

if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 