# Unsplash API Setup Guide

## Overview
The project system now uses dynamic image fetching from Unsplash API instead of hardcoded image IDs. This provides fresh, relevant images for each content piece based on the actual topic and keywords.

## Setup Instructions

### 1. Get Unsplash API Access Key

1. Go to [Unsplash Developers](https://unsplash.com/developers)
2. Create a free account or log in
3. Create a new application
4. Copy your **Access Key**

### 2. Set Environment Variable

**Windows (PowerShell):**
```powershell
$env:UNSPLASH_ACCESS_KEY="your_access_key_here"
```

**Windows (Command Prompt):**
```cmd
set UNSPLASH_ACCESS_KEY=your_access_key_here
```

**Linux/Mac:**
```bash
export UNSPLASH_ACCESS_KEY="your_access_key_here"
```

### 3. Permanent Setup

Create a `.env` file in your project root:
```
UNSPLASH_ACCESS_KEY=your_access_key_here
```

Or add it to your system environment variables.

## Features

### Dynamic Image Selection
- **Featured Images**: Automatically selected based on project topic and keywords
- **Section Images**: Dynamically fetched for each content section
- **SEO Optimized**: All images include proper alt text, titles, and captions
- **Responsive**: Multiple sizes (desktop, mobile, WebP format)

### Fallback System
1. **Primary Search**: Topic-specific search (e.g., "AI marketing automation business")
2. **Fallback Search**: Broader terms (e.g., "technology business innovation")  
3. **Emergency Fallback**: Generic business image if API fails

### Image Metadata
Each image includes:
- SEO-optimized alt text
- Descriptive titles
- Keyword-rich captions
- Photographer attribution
- Multiple format URLs (regular, WebP, mobile)

## Usage

The system automatically:
1. **Analyzes** your project topic and keywords
2. **Searches** Unsplash for relevant images
3. **Optimizes** image metadata for SEO
4. **Inserts** images into content sections
5. **Adds** featured image to WordPress posts

## API Limits

- **Free Tier**: 50 requests per hour
- **Paid Tier**: Higher limits available
- **Caching**: Images are referenced by URL, no local storage needed

## Troubleshooting

### No API Key
```
⚠️ No Unsplash API key found. Using fallback images.
```
**Solution**: Set the `UNSPLASH_ACCESS_KEY` environment variable

### API Errors
```
❌ Unsplash API error: 403
```
**Solution**: Check your API key and usage limits

### No Images Found
```
❌ No images found for: your search term
```
**Solution**: System will automatically use fallback searches

## Benefits

✅ **Fresh Content**: New images for every post  
✅ **SEO Optimized**: Proper alt text and metadata  
✅ **Professional Quality**: High-resolution Unsplash images  
✅ **Automatic**: No manual image selection needed  
✅ **Relevant**: Images match your content topics  
✅ **Legal**: Proper attribution and licensing  

## Example Output

```yaml
featured_image:
  url: "https://images.unsplash.com/photo-xyz?w=1200&h=630&fit=crop&auto=format&q=80"
  alt: "SEO optimization - Complete implementation guide for modern marketers in 2025"
  title: "SEO optimization: Advanced strategies for business growth"
  photographer: "John Doe"
  photographer_url: "https://unsplash.com/@johndoe"
```

The system is now ready to generate content with dynamic, SEO-optimized images! 