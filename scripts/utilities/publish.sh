#!/bin/bash

# WordPress Auto Publisher - Quick Start Script
# For AgenticAI Updates (https://agenticaiupdates.space)

echo "🚀 WordPress Auto Publisher for AgenticAI Updates"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully!"
    else
        echo "❌ Failed to install dependencies. Please check your Python setup."
        exit 1
    fi
else
    echo "⚠️  requirements.txt not found. Installing basic dependencies..."
    pip3 install requests PyYAML markdown
fi

echo ""
echo "🔧 Setup complete! Starting WordPress publisher..."
echo ""

# Run the WordPress publisher
python3 wordpress_publisher.py 