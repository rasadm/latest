# WordPress Auto Publisher Setup Guide

This guide will help you set up automatic publishing to your WordPress site at https://agenticaiupdates.space

## Prerequisites

1. **WordPress Application Password**: You need to create an application password in your WordPress admin
2. **Python 3.7+**: Make sure Python is installed on your system
3. **WordPress REST API**: Must be enabled (usually enabled by default)

## Step 1: Create WordPress Application Password

1. Log into your WordPress admin dashboard at `https://agenticaiupdates.space/wp-admin`
2. Go to **Users** → **Profile** (or **Users** → **All Users** → Click your username)
3. Scroll down to **Application Passwords** section
4. Enter a name like "Auto Publisher" 
5. Click **Add New Application Password**
6. **IMPORTANT**: Copy the generated password immediately (you won't see it again)

## Step 2: Install Python Dependencies

Run this command in your terminal:

```bash
pip install -r requirements.txt
```

## Step 3: Run the Publisher

Execute the publisher script:

```bash
python wordpress_publisher.py
```

The script will ask for:
- **WordPress Username**: Your WordPress admin username
- **WordPress Application Password**: The password you created in Step 1

## Features

### 🚀 What the Publisher Can Do:

1. **Batch Publishing**: Publish all posts from 'serie 1' directory at once
2. **Draft Mode**: Publish as drafts first for review
3. **Immediate Publishing**: Publish posts live immediately
4. **Individual Posts**: Publish specific files one by one
5. **Automatic Categories/Tags**: Creates categories and tags from your post metadata
6. **SEO Optimization**: Preserves all your SEO metadata from YAML front matter

### 📝 Supported Post Format:

Your markdown files should have YAML front matter like this:

```yaml
---
title: "Your Post Title"
description: "SEO description"
categories: ["AI", "Marketing"]
tags: ["automation", "content"]
date: "2025-01-13"
---

Your markdown content here...
```

## Usage Options

When you run the script, you'll see these options:

1. **Publish as Drafts** - Safe option to review before going live
2. **Publish Immediately** - Posts go live instantly
3. **Publish Specific File** - Choose individual files to publish
4. **Exit** - Close the publisher

## Security Notes

- ✅ Uses WordPress Application Passwords (secure)
- ✅ No need to store passwords in files
- ✅ Connects via HTTPS
- ✅ Uses WordPress REST API (official method)

## Troubleshooting

### Connection Issues
- Verify your WordPress site is accessible
- Check that REST API is enabled: Visit `https://agenticaiupdates.space/wp-json/wp/v2/posts`
- Ensure your application password is correct

### Publishing Issues
- Check that your user has publishing permissions
- Verify the markdown files have proper YAML front matter
- Make sure file paths are correct

### Common Errors
- **401 Unauthorized**: Wrong username/password
- **403 Forbidden**: User doesn't have publishing permissions
- **404 Not Found**: WordPress REST API not available

## Advanced Configuration

You can modify `wordpress_publisher.py` to:
- Change default categories/tags
- Modify HTML conversion settings
- Add custom post types
- Schedule posts for future publishing
- Add featured images automatically

## Support

If you encounter issues:
1. Check the error messages in the terminal
2. Verify your WordPress site settings
3. Test the REST API endpoint manually
4. Ensure all dependencies are installed correctly 