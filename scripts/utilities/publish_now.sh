#!/bin/bash

# Quick Publish Script - Publishes the latest blog post automatically
# Usage: ./publish_now.sh

echo "🚀 Quick Publishing Latest Blog Post..."
echo "======================================"

# Install dependencies if needed
if ! python3 -c "import requests, yaml, markdown" 2>/dev/null; then
    echo "📦 Installing required dependencies..."
    pip3 install requests PyYAML markdown
fi

# Run the auto publisher
python3 auto_publisher.py

echo ""
echo "✅ Publishing complete!" 