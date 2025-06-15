# AI Content Management System v0.1.1

🚀 **Major System Upgrade with Claude Sonnet 4**

An advanced AI-powered multilingual content management system with WordPress integration, featuring the latest Claude Sonnet 4 model for superior content generation.

## ✨ What's New in v0.1.1

### 🤖 Claude Sonnet 4 Integration
- **Latest AI Model**: Upgraded to `claude-sonnet-4-20250514` - Anthropic's most advanced model
- **Enhanced Performance**: 64K token output support (vs 8K in previous models)
- **Superior Quality**: Better reasoning, coding, and multilingual content generation
- **Advanced Features**: Extended thinking, improved instruction following

### 🎛️ Dashboard Improvements
- **Resume Button**: Added resume functionality for paused projects
- **Model Selection**: Updated with latest Claude models (Sonnet 4, Opus 4)
- **Better Controls**: Enhanced project management interface
- **Fixed Routing**: Resolved settings dashboard path issues

### 🌍 Multilingual Excellence
- **Enhanced Persian/Farsi**: Improved cultural context and SEO optimization
- **Better Translation**: Advanced language-specific content templates
- **Cultural Adaptation**: Context-aware content generation

### 🔧 System Architecture
- **Organized Structure**: Clean separation into core/, dashboards/, content/, publishing/
- **Security**: Environment variables for API keys and credentials
- **Stability**: Improved error handling and retry logic

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/rasadm/latest.git
   cd latest
   ```

2. **Set up environment**
   ```bash
   copy env.example .env
   # Edit .env with your API keys and credentials
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   start_app.bat
   ```

## 📋 Environment Variables

Create a `.env` file with:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
WP_USERNAME=your_wordpress_username
WP_PASSWORD=your_wordpress_password
UNSPLASH_API_KEY=your_unsplash_api_key_here
```

## 🎯 Features

- **🤖 Claude Sonnet 4**: Latest AI model for superior content generation
- **🌍 Multilingual**: English, Persian/Farsi, Spanish support
- **📝 WordPress Integration**: Automated publishing and scheduling
- **🎨 SEO Optimization**: Advanced SEO features and analytics
- **📊 Project Management**: Comprehensive project tracking and control
- **🔄 Content Automation**: Intelligent content generation workflows
- **📱 Modern UI**: Clean, responsive dashboard interface

## 🏗️ Architecture

```
├── core/                 # Core system components
├── dashboards/          # UI applications
├── content/             # Content generation tools
├── publishing/          # WordPress integration
├── config/              # Configuration files
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── tests/               # Test files
└── projects/            # Project data
```

## 🔧 Technical Requirements

- **Python 3.11+**
- **Anthropic API Key** (Claude Sonnet 4)
- **WordPress Site** (for publishing)
- **Windows** (batch files included)

## 📖 Documentation

- [WordPress Setup Guide](docs/WORDPRESS_SETUP.md)
- [Multilingual System Guide](docs/MULTILINGUAL_SYSTEM_GUIDE.md)
- [Project Management Guide](docs/PROJECT_MANAGEMENT_GUIDE.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in the `docs/` folder

---

**Version 0.1.1** - Major upgrade with Claude Sonnet 4, enhanced multilingual support, and improved system architecture. 