"""
Discover Pakistan — Autonomous Content Publishing Agent.
Generates editorial cards, AI captions, and publishes directly to Facebook & Instagram.
"""

import os
import sys
import json
import random
import logging
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load local environment
load_dotenv()

BASE_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("travel_pakistan")

from video_engine.niche_catalog import NicheCatalog
from video_engine.niche_card_compositor import NicheCardCompositor
from agents.niche_content_agent import generate_niche_content
from publish_reels import publish_facebook_photo, publish_instagram_reel, publish_facebook_reel

NICHE_ID = "travel_pakistan"
DEFAULT_PAGE_ID = "1304442402758898"
DEFAULT_IG_ID = "17841438750095367"
SITE_URL = "https://discover-pakistan.github.io"

def run_pipeline(format_type: str = "card", topic: str = None, city: str = None, lang: str = None, no_publish: bool = False, blog_lang: str = None):
    niche = NicheCatalog.resolve_niche(NICHE_ID)
    lang = lang or niche.get("default_lang", "english")

    if city and NICHE_ID == "travel_pakistan":
        topic = f"Scenic beauty, hidden travel destinations, and tourism facts for {city}, Pakistan"
    elif city and not topic:
        topic = f"Featured updates and local highlights from {city}"

    logger.info(f"🎯 Executing Agent: '{niche['name']}' (Format: {format_type.upper()}, Lang: {lang.upper()})")
    content = generate_niche_content(niche, topic=topic, lang=lang)

    storage_dir = BASE_DIR / "storage" / "videos"
    storage_dir.mkdir(parents=True, exist_ok=True)
    created_paths = []

    if format_type in ("card", "both"):
        fonts_dir = BASE_DIR / "assets" / "fonts"
        compositor = NicheCardCompositor(font_dir=fonts_dir)
        filename = f"post_{NICHE_ID}_{random.randint(1000, 9999)}.png"
        output_path = str(storage_dir / filename)
        card_path = compositor.render_card(niche, content, output_path)
        created_paths.append(card_path)
        logger.info(f"🖼️ Editorial Card Generated: {card_path}")

    captions = content.get("captions", {})
    with open(BASE_DIR / "latest_caption.txt", "w", encoding="utf-8") as f:
        f.write(captions.get("threads", captions.get("facebook", "")))

    log_entry = {
        "niche": NICHE_ID,
        "headline": content.get("headline", ""),
        "captions": captions,
        "media_paths": created_paths
    }
    with open(BASE_DIR / "captions_log.jsonl", "a", encoding="utf-8") as lf:
        lf.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    logger.info(f"[+] Appended to captions_log.jsonl")

    # Update static GitHub Pages blog catalog
    update_blog_catalog(NICHE_ID, content, created_paths, blog_lang=blog_lang)

    if not no_publish:
        target_page_id = (os.getenv("FB_PAGE_ID") or DEFAULT_PAGE_ID).strip()
        logger.info(f"[*] Publishing media to target Facebook Page ID: {target_page_id}")

        for path in created_paths:
            try:
                if path.endswith(".png") or path.endswith(".jpg"):
                    publish_facebook_photo(path, captions.get("facebook", ""), page_id=target_page_id)
                elif path.endswith(".mp4"):
                    publish_instagram_reel(path, captions.get("instagram", ""))
                    publish_facebook_reel(path, captions.get("facebook", ""), title=content.get("headline", ""), page_id=target_page_id)
            except Exception as e:
                logger.error(f"[-] Social publishing error: {e}")
    else:
        logger.info("ℹ️ --no-publish flag set. Media preserved locally.")

    return created_paths

def update_blog_catalog(niche_id: str, content: dict, created_paths: list, blog_lang: str = None):
    """
    Publishes a long-form article to posts.json for the GitHub Pages blog.

    Rules (do not regress):
      * NEVER use the social card (.png with text overlays) as the blog image.
        A dedicated, unique 16:9 editorial cover is generated per post.
      * NEVER publish placeholder text. If the long-form article can't be
        generated, the blog is left untouched (social posting still happens).
      * Human editorial bylines only; Urdu and English alternate daily.
    """
    import re
    from datetime import datetime
    from agents.blog_article_agent import generate_blog_article, pick_author, URDU_CATEGORY
    from video_engine.editorial_image_service import EditorialImageService
    import blog_sync

    niche = NicheCatalog.resolve_niche(niche_id)
    if blog_lang not in ("urdu", "english"):
        blog_lang = "urdu" if datetime.now().timetuple().tm_yday % 2 else "english"

    article = generate_blog_article(niche, content, lang=blog_lang)
    if not article:
        logger.warning("⛔ Long-form article unavailable — blog NOT updated (no placeholder posts).")
        return

    slug = re.sub(r'[^a-z0-9]+', '-', (content.get("headline") or "story").lower()).strip('-')[:40] or "story"
    post_id = f"{slug}-{'ur' if blog_lang == 'urdu' else 'en'}-{random.randint(100, 999)}"

    cover_rel = f"assets/posts/{post_id}_cover.jpg"
    try:
        EditorialImageService.generate_editorial_cover(
            prompt=article.get("image_prompt") or content.get("headline", "mountain landscape in northern Pakistan"),
            niche_key=niche_id, output_path=BASE_DIR / cover_rel, seed_key=post_id,
        )
    except Exception as e:
        logger.warning(f"⛔ No clean cover image ({e}) — blog NOT updated.")
        return

    author, role, avatar = pick_author(niche_id, blog_lang)
    new_article = {
        "id": post_id,
        "category": URDU_CATEGORY.get(niche_id) if blog_lang == "urdu" else content.get("category_tag", "Travel Guide").title(),
        "badge": article.get("badge") or content.get("badge", ""),
        "title": article["title"],
        "subdeck": article.get("subdeck", ""),
        "image": cover_rel,
        "stat_number": article.get("stat_number", ""),
        "stat_label": article.get("stat_label", ""),
        "author": author,
        "author_role": role,
        "author_avatar": avatar,
        "date": datetime.now().strftime("%d %b %Y"),
        "read_time": article.get("read_time", "5 min read"),
        "lang": "ur" if blog_lang == "urdu" else "en",
        "featured": True,
        "body": article.get("intro", []),
        "sections": article.get("sections", []),
        "faqs": article.get("faqs", []),
        "takeaways": article.get("takeaways", []),
    }

    posts_file = BASE_DIR / "posts.json"
    posts = json.loads(posts_file.read_text(encoding="utf-8")) if posts_file.exists() else []
    for p in posts:
        p["featured"] = False
    posts.insert(0, new_article)
    posts_file.write_text(json.dumps(posts[:50], indent=2, ensure_ascii=False), encoding="utf-8")
    blog_sync.sync(SITE_URL)
    logger.info(f"📰 Blog updated (+1 {blog_lang} article by {author}): {new_article['title']}")
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discover Pakistan Publishing Agent")
    parser.add_argument("--format", choices=["card", "reel", "both"], default="card", help="Format to generate")
    parser.add_argument("--topic", type=str, default=None, help="Custom topic / angle")
    parser.add_argument("--city", type=str, default=None, help="City / region override (for travel)")
    parser.add_argument("--lang", type=str, default=None, help="Language override (english, urdu)")
    parser.add_argument("--no-publish", action="store_true", help="Generate card without social publish")
    parser.add_argument("--blog-lang", type=str, choices=["english", "urdu"], default=None, help="Blog article language (default: alternates daily)")
    parser.add_argument("--once", action="store_true", help="Run single generation cycle")

    args = parser.parse_args()
    run_pipeline(format_type=args.format, topic=args.topic, city=args.city, lang=args.lang, no_publish=args.no_publish, blog_lang=args.blog_lang)
