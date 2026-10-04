"""
blog_sync.py — keeps index.html pre-rendered (fast first paint) and sitemap.xml
in sync with posts.json. Called by run_agent.py after every new article and can
be run standalone:  python blog_sync.py
"""

import html
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
DEFAULT_AVATAR = "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=80&h=80&fit=crop"


def _e(v):
    return html.escape(str(v or ""))


def _is_urdu(p):
    return p.get("lang") == "ur" or any("\u0600" <= c <= "\u06FF" for c in p.get("title", ""))


def _meta(p, size, with_read=False):
    extra = (f'\n        <span class="meta-separator">•</span>\n'
             f'        <span class="meta-date">{_e(p.get("read_time", "4 min read"))}</span>') if with_read else ""
    return (f'<div class="author-meta-row">\n'
            f'        <img class="author-avatar" src="{p.get("author_avatar") or DEFAULT_AVATAR}" alt="{_e(p.get("author"))}" width="{size}" height="{size}" loading="lazy" decoding="async" />\n'
            f'        <span class="author-name">{_e(p.get("author"))}</span>\n'
            f'        <span class="meta-separator">•</span>\n'
            f'        <span class="meta-date">{_e(p.get("date"))}</span>{extra}\n'
            f'      </div>')


def render_lead(p):
    u = _is_urdu(p)
    d = ' dir="rtl"' if u else ""
    stat = ""
    if p.get("stat_number"):
        stat = (f'\n        <div class="stat-chip"><span class="stat-chip-num">{_e(p["stat_number"])}</span>'
                f'<span class="stat-chip-label">{_e(p.get("stat_label", "KEY METRIC"))}</span></div>')
    return f'''
    <div class="featured-lead-card" onclick="openArticleModal('{p["id"]}')">
      <div class="featured-media-wrapper">
        <img class="featured-media-img" src="{p["image"]}" alt="{_e(p["title"])}" width="1200" height="675" loading="eager" fetchpriority="high" decoding="async" />
        <span class="media-badge">{_e(p.get("badge") or p.get("category"))}</span>{stat}
      </div>
      <h2 class="featured-title{' urdu-title' if u else ''}"{d}>{_e(p["title"])}</h2>
      <p class="featured-subdeck{' urdu-subdeck' if u else ''}"{d}>{_e(p.get("subdeck"))}</p>
      {_meta(p, 28, True)}
    </div>'''


def render_stack(p):
    u = _is_urdu(p)
    d = ' dir="rtl"' if u else ""
    return f'''
    <div class="stacked-story-card" onclick="openArticleModal('{p["id"]}')">
      <div class="stacked-thumb-wrapper">
        <img class="stacked-thumb-img" src="{p["image"]}" alt="{_e(p["title"])}" width="480" height="270" loading="lazy" decoding="async" />
      </div>
      <div class="stacked-story-info">
        <h3 class="stacked-story-title{' urdu-title' if u else ''}"{d}>{_e(p["title"])}</h3>
        <p class="stacked-story-excerpt{' urdu-subdeck' if u else ''}"{d}>{_e(p.get("subdeck"))}</p>
        {_meta(p, 24)}
      </div>
    </div>'''


def render_grid(p):
    u = _is_urdu(p)
    d = ' dir="rtl"' if u else ""
    badge = f'<span class="media-badge">{_e(p["badge"])}</span>' if p.get("badge") else ""
    return f'''
      <div class="editorial-card" onclick="openArticleModal('{p["id"]}')">
        <div class="editorial-card-thumb">
          <img class="editorial-card-img" src="{p["image"]}" alt="{_e(p["title"])}" width="600" height="338" loading="lazy" decoding="async" />
          {badge}
        </div>
        <div class="card-category-tag">{_e(p.get("category"))}</div>
        <h3 class="editorial-card-title{' urdu-title' if u else ''}"{d}>{_e(p["title"])}</h3>
        <p class="editorial-card-excerpt{' urdu-subdeck' if u else ''}"{d}>{_e(p.get("subdeck"))}</p>
        {_meta(p, 24)}
      </div>'''


def sync(site_url: str):
    posts = json.loads((BASE_DIR / "posts.json").read_text(encoding="utf-8"))
    index = BASE_DIR / "index.html"
    content = index.read_text(encoding="utf-8")
    lead, stack, grid = posts[0], posts[1:4], posts[4:]

    content = re.sub(r'window\.INITIAL_POSTS\s*=\s*\[.*?\];',
                     lambda _: f'window.INITIAL_POSTS = {json.dumps(posts, ensure_ascii=False)};',
                     content, flags=re.DOTALL)
    lead_url = f"{site_url}/{lead['image']}"
    content = re.sub(r'(<meta property="og:image" content=")[^"]+', lambda m: m.group(1) + lead_url, content)
    content = re.sub(r'(<meta name="twitter:image" content=")[^"]+', lambda m: m.group(1) + lead_url, content)
    content = re.sub(r'(<link rel="preload" as="image" href=")[^"]+', lambda m: m.group(1) + lead["image"], content)

    content = re.sub(r'<div id="featured-story-slot">.*?</div>\s*<div id="stacked-stories-slot"',
                     lambda _: f'<div id="featured-story-slot">\n{render_lead(lead)}\n        </div>\n        <div id="stacked-stories-slot"',
                     content, flags=re.DOTALL)
    content = re.sub(r'<div id="stacked-stories-slot" class="story-stack-col">.*?</div>\s*</div>\s*</section>',
                     lambda _: ('<div id="stacked-stories-slot" class="story-stack-col">\n'
                                + "\n".join(render_stack(p) for p in stack)
                                + '\n        </div>\n      </div>\n    </section>'),
                     content, count=1, flags=re.DOTALL)
    content = re.sub(r'<div id="editorial-grid" class="editorial-grid">.*?</div>\s*<!-- Pagination / End Marker -->',
                     lambda _: ('<div id="editorial-grid" class="editorial-grid">\n'
                                + "\n".join(render_grid(p) for p in grid)
                                + '\n    </div>\n\n    <!-- Pagination / End Marker -->'),
                     content, flags=re.DOTALL)
    index.write_text(content, encoding="utf-8")

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
             f'  <url><loc>{site_url}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>']
    for p in posts:
        lines.append(f'  <url><loc>{site_url}/#{p["id"]}</loc><changefreq>weekly</changefreq><priority>0.85</priority>'
                     f'<image:image><image:loc>{site_url}/{p["image"]}</image:loc><image:title>{_e(p["title"])}</image:title></image:image></url>')
    lines.append('</urlset>')
    (BASE_DIR / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    import sys
    sync(sys.argv[1] if len(sys.argv) > 1 else "https://discover-pakistan.github.io")
    print("index.html + sitemap.xml synced")
