# RasaDM News Hub

Latest insights, trends, and breakthroughs in AI-powered content automation and marketing technology.

## GitHub Pages Setup

This site is deployed using GitHub Pages with Jekyll.

Welcome to **RasaDM News Hub** - your premier source for AI and marketing technology intelligence. This Jekyll-powered blog delivers breaking news, expert insights, and strategic analysis on AI-powered content automation and marketing technology trends.

## 🚀 Quick Start

### Prerequisites
- Ruby 2.7 or higher
- Jekyll 4.3+
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/rasadm-news-hub.git
   cd rasadm-news-hub
   ```

2. **Install dependencies**
   ```bash
   bundle install
   ```

3. **Run the development server**
   ```bash
   bundle exec jekyll serve
   ```

4. **View your site**
   Open `http://localhost:4000` in your browser

### GitHub Pages Deployment

This blog is configured to work seamlessly with GitHub Pages:

1. **Enable GitHub Pages**
   - Go to your repository settings
   - Scroll to "Pages" section
   - Select "Deploy from a branch"
   - Choose `main` branch and `/ (root)` folder
   - Click "Save"

2. **Update configuration**
   - Edit `_config.yml`
   - Update the `url` field with your GitHub Pages URL
   - Commit and push changes

3. **Your blog will be live at**
   `https://yourusername.github.io/repository-name`

## 📝 Content Management

### Adding New Posts

1. **Create a new post file** in the `_posts` directory
   ```
   _posts/YYYY-MM-DD-post-title.md
   ```

2. **Use the following front matter template:**
   ```yaml
   ---
   title: "Your Post Title"
   meta_title: "SEO Optimized Title | RasaDM News"
   meta_description: "Brief description for SEO and social sharing"
   keywords: ["keyword1", "keyword2", "keyword3"]
   date: YYYY-MM-DD HH:MM:SS +0000
   categories: ["AI News", "Marketing Technology"]
   tags: ["ai", "content automation", "martech"]
   ---
   ```

3. **Write your content** using Markdown syntax

### Content Guidelines

- **Research-backed**: All content must include credible sources and verified data
- **No fabrication**: Never create false statistics or unsubstantiated claims
- **Academic standards**: Follow rigorous editorial standards
- **Strategic focus**: Emphasize business impact and actionable insights
- **RasaDM integration**: Naturally incorporate RasaDM branding and perspective

## 🛠 Customization

### Theme Customization

The blog uses the Minima theme with custom styling:

1. **Override theme files** by creating corresponding files in your repository
2. **Custom CSS** can be added to `assets/css/style.scss`
3. **Layout modifications** go in the `_layouts` directory

### Configuration Options

Key settings in `_config.yml`:

```yaml
title: "RasaDM News Hub"
description: "Your site description"
url: "https://yourusername.github.io"
author:
  name: "RasaDM Editorial Team"
  email: "news@rasadm.com"
```

### Analytics and SEO

- **Google Analytics**: Update the `google_analytics` field in `_config.yml`
- **SEO**: The site includes jekyll-seo-tag for optimal search engine optimization
- **Social sharing**: Configured for Twitter Cards and Open Graph

## 📊 Features

### Built-in Functionality

- ✅ **Responsive design** - Mobile-friendly layout
- ✅ **SEO optimized** - Meta tags, sitemaps, and structured data
- ✅ **Social sharing** - Twitter Cards and Open Graph support
- ✅ **RSS feed** - Automatic feed generation
- ✅ **Pagination** - Organized post navigation
- ✅ **Search engine friendly** - Clean URLs and proper markup

### Plugins Included

- `jekyll-feed` - RSS feed generation
- `jekyll-sitemap` - XML sitemap
- `jekyll-seo-tag` - SEO meta tags
- `jekyll-paginate` - Post pagination

## 📁 Project Structure

```
rasadm-news-hub/
├── _config.yml          # Jekyll configuration
├── _posts/              # Blog posts
├── _layouts/            # Custom layouts (optional)
├── _includes/           # Reusable components (optional)
├── _sass/               # Custom styles (optional)
├── assets/              # Images, CSS, JS
├── _pages/              # Static pages
├── Gemfile              # Ruby dependencies
├── index.md             # Homepage
└── README.md            # This file
```

## 🚀 Publishing Workflow

### Recommended Process

1. **Create content** locally in `_posts/`
2. **Test locally** with `bundle exec jekyll serve`
3. **Commit and push** to GitHub
4. **GitHub Pages** automatically builds and deploys

### Content Categories

Organize posts using these categories:
- `AI News` - Breaking industry news
- `Marketing Technology` - MarTech developments
- `Industry Analysis` - Strategic insights
- `Platform Updates` - Tool and platform news
- `Research Reports` - Data-driven content

## 🔧 Troubleshooting

### Common Issues

1. **Build failures**: Check `Gemfile` dependencies
2. **Styling issues**: Verify CSS/Sass syntax
3. **Plugin errors**: Ensure all plugins are listed in `_config.yml`
4. **Deployment delays**: GitHub Pages can take 5-10 minutes to update

### Support Resources

- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Minima Theme Guide](https://github.com/jekyll/minima)

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

---

**RasaDM News Hub** - Delivering intelligence for the AI-driven marketing future.

For questions or support, contact the editorial team at news@rasadm.com 