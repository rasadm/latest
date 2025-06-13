---
layout: archive
title: "Content Archive"
permalink: /archive/
author_profile: true
---

# Content Archive

Browse our complete collection of articles, analysis, and news coverage organized by date and category.

## Browse by Year

{% for post in site.posts %}
  {% assign currentdate = post.date | date: "%Y" %}
  {% if currentdate != date %}
    {% unless forloop.first %}</ul>{% endunless %}
    <h3>{{ currentdate }}</h3>
    <ul>
    {% assign date = currentdate %}
  {% endif %}
    <li><a href="{{ post.url }}">{{ post.title }}</a> - {{ post.date | date: "%B %d" }}</li>
  {% if forloop.last %}</ul>{% endif %}
{% endfor %}

---

## Browse by Category

<div class="category-archive">
  {% for category in site.categories %}
    <div class="category-section">
      <h3>{{ category[0] | replace: '-', ' ' | capitalize }}</h3>
      <p>{{ category[1].size }} posts</p>
      <a href="/categories/{{ category[0] | slugify }}/" class="btn btn--primary btn--small">View Category</a>
    </div>
  {% endfor %}
</div>

<style>
.category-archive {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}

.category-section {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  border-left: 4px solid #007acc;
}

.category-section h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  color: #2d3748;
}

.category-section p {
  color: #6c757d;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}
</style> 