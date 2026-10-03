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

def run_pipeline(format_type: str = "card", topic: str = None, city: str = None, lang: str = None, no_publish: bool = False):
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
    update_blog_catalog(NICHE_ID, content, created_paths)

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

def update_blog_catalog(niche_id: str, content: dict, created_paths: list):
    """
    Appends newly generated post to posts.json and copies generated card
    into assets/posts/ so GitHub Pages blog updates autonomously.
    """
    import re
    import shutil
    from datetime import datetime

    posts_file = BASE_DIR / "posts.json"
    assets_posts_dir = BASE_DIR / "assets" / "posts"
    assets_posts_dir.mkdir(parents=True, exist_ok=True)

    slug = re.sub(r'[^a-z0-9]+', '-', content.get("headline", "story").lower()).strip('-')[:35]
    post_id = f"{slug}-{random.randint(100, 999)}"

    rel_img_path = "assets/images/hunza.jpg"
    for p in created_paths:
        if p.endswith(".png") or p.endswith(".jpg"):
            dst_name = f"{post_id}.png"
            shutil.copy2(p, assets_posts_dir / dst_name)
            rel_img_path = f"assets/posts/{dst_name}"
            break

    new_article = {
        "id": post_id,
        "category": content.get("category_tag", "Alpine Expeditions"),
        "badge": content.get("badge", "DAILY EXPEDITION"),
        "title": content.get("headline", "Scenic Travel Dossier"),
        "subdeck": content.get("subdeck", "Latest alpine journey and cultural discovery from Pakistan."),
        "image": rel_img_path,
        "stat_number": content.get("stat_number", ""),
        "stat_label": content.get("stat_label", "METRIC"),
        "author": "Autonomous Travel Agent",
        "author_avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&h=100&fit=crop",
        "date": datetime.now().strftime("%d %b %Y"),
        "read_time": "4 min read",
        "featured": True,
        "body": content.get("bullet_points", [content.get("subdeck", "")]),
        "takeaways": content.get("bullet_points", [])
    }

    try:
        posts = []
        if posts_file.exists():
            with open(posts_file, "r", encoding="utf-8") as f:
                posts = json.load(f)
        for p in posts:
            p["featured"] = False
        posts.insert(0, new_article)
        posts = posts[:50]
        with open(posts_file, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        logger.info(f"📰 Autonomous Blog Catalog Updated: {posts_file} (+1 article: '{new_article['title']}')")
    except Exception as e:
        logger.warning(f"Could not update blog catalog: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discover Pakistan Publishing Agent")
    parser.add_argument("--format", choices=["card", "reel", "both"], default="card", help="Format to generate")
    parser.add_argument("--topic", type=str, default=None, help="Custom topic / angle")
    parser.add_argument("--city", type=str, default=None, help="City / region override (for travel)")
    parser.add_argument("--lang", type=str, default=None, help="Language override (english, urdu)")
    parser.add_argument("--no-publish", action="store_true", help="Generate card without social publish")
    parser.add_argument("--once", action="store_true", help="Run single generation cycle")

    args = parser.parse_args()
    run_pipeline(format_type=args.format, topic=args.topic, city=args.city, lang=args.lang, no_publish=args.no_publish)
