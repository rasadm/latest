# Project-Based Content Management System Guide

## Overview

The Project-Based Content Management System is a comprehensive solution for managing multiple content creation projects with custom keywords, targeted research, and automated publishing to WordPress.

## Key Features

### 🚀 Multi-Project Management
- Create and manage multiple independent content projects
- Each project has its own settings, keywords, and output directory
- Track progress and completion status for each project

### 🎯 Custom Keywords & SEO
- Define specific keywords for each project
- Set SEO focus keywords for optimization
- Generate content based on project-specific keyword sets

### 🔍 Targeted Research
- Limit research to 1-2 specific sites per project
- Gather fresh, relevant data for content creation
- Combine research data with AI generation

### 🤖 Multiple Generation Methods
- **Template**: Pre-built templates with keyword substitution
- **Local LLM**: DeepSeek R1 models (deepseek, deepseek-32b, deepseek-14b)
- **Research+LLM**: Web research combined with local AI
- **Claude**: Anthropic's Claude 3.5 Sonnet API

### 📊 Progress Tracking
- Real-time progress monitoring
- Completion statistics
- Project status management (active, paused, completed)

## System Architecture

### Core Components

1. **ProjectManager** (`project_manager.py`)
   - Manages project lifecycle
   - Handles content generation
   - Coordinates research and AI systems

2. **ProjectDashboard** (`project_dashboard.py`)
   - Multi-page GUI interface
   - Project creation and management
   - Real-time monitoring and controls

3. **ContentProject** (Data Class)
   - Project configuration storage
   - Settings and metadata management
   - Progress tracking

## Getting Started

### 1. System Requirements
- Python 3.8+
- Required packages (see requirements.txt)
- Ollama with DeepSeek models (for local LLM)
- WordPress site with API access

### 2. Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Start the project dashboard
python project_dashboard.py
# OR
start_project_dashboard.bat
```

### 3. Creating Your First Project

1. **Launch Dashboard**
   - Run `start_project_dashboard.bat`
   - Click "✨ New Project"

2. **Basic Information**
   - Project Name: e.g., "AI Marketing 2025"
   - Description: Brief project description

3. **Keywords & SEO**
   - Keywords: Comma-separated list (e.g., "AI Marketing, Marketing Automation, Predictive Analytics")
   - SEO Focus: Optional specific SEO keywords

4. **Content Settings**
   - Target Count: Number of content pieces to generate
   - Generation Method: Choose from Template, Local LLM, Research+LLM, or Claude
   - LLM Model: Select DeepSeek variant
   - Template Style: trend_analysis, how_to_guide, or case_study
   - Content Length: short (1000-1500), medium (2000-2500), long (3000-4000)
   - Target Audience: Define your audience

5. **Research Settings**
   - Research Sites: Optional specific sites for research (one per line)
   - System will use default sites if none specified

## Content Generation Methods

### 1. Template Method
- **Cost**: $0.00 per post
- **Speed**: Very fast
- **Quality**: Consistent, structured content
- **Use Case**: High-volume, consistent content needs

**How it works**:
- Uses predefined templates with keyword substitution
- Creates structured content with consistent format
- Includes SEO optimization and proper headings

### 2. Local LLM Method
- **Cost**: $0.00 per post
- **Speed**: Fast (depends on hardware)
- **Quality**: High, AI-generated content
- **Use Case**: Creative, varied content with zero API costs

**Models Available**:
- `deepseek`: Latest DeepSeek R1 model
- `deepseek-32b`: 32B parameter model
- `deepseek-14b`: 14B parameter model

### 3. Research+LLM Method
- **Cost**: $0.00 per post (using local LLM)
- **Speed**: Moderate (includes research time)
- **Quality**: Highest, data-driven content
- **Use Case**: Premium content with real statistics and insights

**Process**:
1. Searches Google News for recent articles
2. Extracts statistics and trends
3. Combines research with local LLM generation
4. Creates comprehensive, fact-based content

### 4. Claude Method
- **Cost**: $0.01-0.03 per post
- **Speed**: Fast
- **Quality**: Very high, professional content
- **Use Case**: Premium content when budget allows

## Project Management

### Dashboard Features

#### Main Dashboard
- **System Overview**: Statistics cards showing total projects, active projects, completed projects, and total content
- **Project List**: All projects with status indicators and progress
- **Project Details**: Selected project information and settings
- **Quick Actions**: Generate content, run project, view files

#### Project Creation Page
- **Comprehensive Form**: All project settings in organized sections
- **Real-time Validation**: Input validation and error handling
- **Form Reset**: Clear all fields for new project

#### Project Detail Page
- **Detailed Information**: Complete project configuration and progress
- **Control Panel**: Generate content, run project, pause, view files
- **Activity Log**: Real-time activity and error logging

### Project Operations

#### Generate Single Content
- Creates one piece of content for the selected project
- Uses next keyword in rotation
- Publishes immediately if configured

#### Run Project
- Generates content in batches
- Continues until target count reached
- Automatic progress tracking

#### Pause/Resume
- Pause active projects
- Resume paused projects
- Status management

## File Organization

### Project Structure
```
projects/
├── project_[ID]_[name]/
│   ├── content-file-1.md
│   ├── content-file-2.md
│   └── ...
└── projects.json (configuration file)
```

### Content Files
Each generated content file includes:
- Project metadata
- Generation method information
- SEO keywords and settings
- Full markdown content
- Word count and statistics

## Configuration Files

### projects.json
Stores all project configurations:
```json
{
  "project_id": {
    "id": "project_id",
    "name": "Project Name",
    "description": "Project description",
    "keywords": ["keyword1", "keyword2"],
    "target_count": 10,
    "completed_count": 3,
    "status": "active",
    ...
  }
}
```

## Advanced Features

### Custom Research Sites
Specify particular websites for research:
```
https://marketingland.com
https://contentmarketinginstitute.com
https://blog.hubspot.com
```

### SEO Optimization
- Automatic keyword density optimization
- SEO-friendly headings and structure
- Meta information generation
- Internal linking (when available)

### WordPress Integration
- Automatic publishing to WordPress
- Featured image upload
- Category and tag assignment
- SEO metadata inclusion

## Troubleshooting

### Common Issues

1. **Project Creation Fails**
   - Check all required fields are filled
   - Ensure target count is a positive number
   - Verify keywords are properly formatted

2. **Content Generation Fails**
   - Check Ollama is running (for local LLM)
   - Verify internet connection (for research)
   - Check WordPress credentials

3. **Research Not Working**
   - Verify internet connection
   - Check if research sites are accessible
   - Try with default research sites

### Error Messages
- Check the Activity Log for detailed error information
- Console output provides additional debugging info
- Project status will show if there are issues

## Performance Tips

### Optimization
- Use Template method for high-volume content
- Local LLM for balance of quality and cost
- Research+LLM for premium content
- Batch generation for efficiency

### Resource Management
- Monitor system resources when using local LLM
- Adjust batch sizes based on system capacity
- Use appropriate content length settings

## API Costs Comparison

| Method | Cost per Post | Quality | Speed |
|--------|---------------|---------|-------|
| Template | $0.00 | Good | Very Fast |
| Local LLM | $0.00 | High | Fast |
| Research+LLM | $0.00 | Very High | Moderate |
| Claude | $0.01-0.03 | Very High | Fast |

## Support and Updates

### Getting Help
- Check this guide for common issues
- Review error logs in Activity Log
- Verify system requirements and dependencies

### System Updates
- Keep dependencies updated
- Monitor for new DeepSeek model releases
- Update WordPress credentials as needed

---

*Generated by Project Content Management System* 