# Changelog

All notable changes to the AI Content Management System will be documented in this file.

## [0.1.1] - 2025-06-14

### 🚀 Major System Upgrade with Claude Sonnet 4

#### ✨ Added
- **Claude Sonnet 4 Integration**: Upgraded to `claude-sonnet-4-20250514` - Anthropic's latest and most advanced model
- **Resume Project Button**: Added resume functionality to dashboard controls for paused projects
- **Enhanced Model Selection**: Updated dashboard with latest Claude models (Sonnet 4, Opus 4, 3.5 Sonnet, Haiku)
- **Environment Variables**: Secure credential management with `.env` file support
- **Comprehensive Documentation**: Added README.md, requirements.txt, and setup guides

#### 🔧 Improved
- **Content Generation**: 64K token output support (8x increase from previous models)
- **Multilingual Support**: Enhanced Persian/Farsi content generation with better cultural context
- **Error Handling**: Improved retry logic and connection stability
- **System Architecture**: Better organized codebase structure
- **Security**: Removed hardcoded API keys, implemented environment variable system

#### 🐛 Fixed
- **Dashboard Routing**: Fixed settings dashboard path from root to `dashboards/settings_dashboard.py`
- **Import Errors**: Resolved Python path and module import issues
- **Project Status**: Fixed project resume and status management functionality
- **Settings Management**: Corrected settings file path to `config/settings.json`

#### 🌍 Enhanced Multilingual Features
- **Persian/Farsi**: Improved SEO optimization and cultural adaptation
- **Content Templates**: Language-specific templates with cultural context
- **Research Enhancement**: Better multilingual keyword research and content generation

#### 📊 Performance Improvements
- **Claude Sonnet 4**: Superior reasoning, coding, and content quality
- **Instruction Following**: Reduced AI shortcuts and improved precision
- **Content Quality**: More engaging and accurate multilingual content
- **System Stability**: Enhanced error recovery and connection management

#### 🏗️ Technical Changes
- **Project Structure**: Organized into core/, dashboards/, content/, publishing/ directories
- **Configuration**: Centralized config management with environment variables
- **Dependencies**: Updated requirements.txt with all necessary packages
- **Git Security**: Added .gitignore to protect sensitive files

### 🔄 Migration Notes
- Copy `env.example` to `.env` and fill in your credentials
- Update any custom scripts to use new directory structure
- Verify Claude API key is set in environment variables

### 🎯 Next Release Preview
- Enhanced WordPress integration
- Advanced SEO analytics
- Multi-site management
- Automated content scheduling improvements

---

## [0.1.0] - Previous Release
- Initial system with basic Claude integration
- WordPress publishing functionality
- Multilingual content support
- Project management dashboard 