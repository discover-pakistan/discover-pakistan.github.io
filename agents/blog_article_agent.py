"""
Blog Article Agent — long-form, indexable article for the GitHub Pages blog.

The social card payload (headline + 3 bullets) is NOT a blog post. This agent
asks Gemini for a full article (H2 sections, FAQs, takeaways, image prompt) and
returns None if it can't produce real content. The caller must then SKIP the
blog update instead of publishing placeholder text.
"""

import json
import logging
import os
import random
from typing import Dict, Optional

logger = logging.getLogger(__name__)

AUTHORS = {
    "sports_cricket": {
        "english": [
            ("Hamid Raza", "Chief Cricket Analyst", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop"),
            ("Farhan Siddiqui", "Bowling Biomechanics Lead", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop"),
            ("Zainab Abbas", "Senior Broadcast Analyst", "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&h=100&fit=crop"),
        ],
        "urdu": [
            ("حمید رضا", "چیف کرکٹ اینالسٹ", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop"),
            ("فرحان صدیقی", "ٹیکنیکل بیٹنگ اینالسٹ", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop"),
            ("زینب عباس", "سپورٹس براڈکاسٹر و اینالسٹ", "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&h=100&fit=crop"),
        ],
    },
    "travel_pakistan": {
        "english": [
            ("Sherbaz Ali", "Senior Expedition Editor", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop"),
            ("Ayesha Khan", "Culture & Heritage Writer", "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&h=100&fit=crop"),
            ("Taimur Malik", "Northern Areas Correspondent", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop"),
        ],
        "urdu": [
            ("حمید رضا", "سینئر ٹریول ایڈیٹر", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop"),
            ("فاطمہ رحمان", "ثقافتی ورثہ نگار", "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&h=100&fit=crop"),
        ],
    },
}

URDU_CATEGORY = {"sports_cricket": "اردو اینالیٹکس", "travel_pakistan": "اردو گائیڈ"}

PLACEHOLDER_MARKERS = (
    "Consistency and quality drive",
    "Timely execution separates",
    "Focus on value-first insights",
    "Insight",  # generic "<Niche> Insight" headline
)


def pick_author(niche_id: str, lang: str):
    pool = AUTHORS.get(niche_id, AUTHORS["sports_cricket"]).get(lang, AUTHORS["sports_cricket"]["english"])
    return random.choice(pool)


def generate_blog_article(niche: Dict, social: Dict, lang: str = "english") -> Optional[Dict]:
    """Return a long-form article dict, or None if real content can't be produced."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY missing — refusing to publish placeholder blog content.")
        return None
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        logger.error("google-genai not installed.")
        return None

    niche_id = niche.get("id", "sports_cricket")
    language_rule = (
        "Write EVERYTHING (title, subdeck, sections, FAQs, takeaways) in fluent, natural Urdu script "
        "(Nastaliq style journalism, not Roman Urdu). Keep image_prompt in English."
        if lang == "urdu" else "Write in polished British/Pakistani English journalism style."
    )
    prompt = f"""You are a senior Pakistani journalist writing for '{niche.get('name')}'.
Story angle (from today's social post): "{social.get('headline', '')}" — {social.get('subdeck', '')}
Key facts to expand: {json.dumps(social.get('bullet_points', []), ensure_ascii=False)}
{language_rule}

Write an original, accurate, in-depth 550-750 word article. Do not invent precise statistics you
cannot stand behind; prefer well-known facts and clearly framed analysis.
Return STRICT JSON:
{{
  "title": "SEO headline, 8-14 words",
  "subdeck": "1-2 sentence standfirst",
  "badge": "short uppercase label with 1 emoji",
  "stat_number": "one headline metric or empty string",
  "stat_label": "label for the metric",
  "intro": ["2 opening paragraphs"],
  "sections": [{{"title": "H2 heading", "paragraphs": ["2-3 paragraphs"]}}, ... 3 or 4 sections],
  "faqs": [{{"question": "...", "answer": "..."}}, ... 3 items],
  "takeaways": ["3 concise key takeaways"],
  "read_time": "e.g. 5 min read / 5 منٹ مطالعہ",
  "image_prompt": "English description of a realistic news photograph for this story, no text in image"
}}"""

    client = genai.Client(api_key=api_key)
    for model_name in ("gemini-2.5-flash", "gemini-3-flash-preview", "gemini-3.1-flash-lite"):
        try:
            resp = client.models.generate_content(
                model=model_name, contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.6),
            )
            art = json.loads(resp.text.strip())
            if _passes_quality_gate(art):
                logger.info(f"✅ Long-form {lang} article via {model_name}: {art['title']}")
                return art
            logger.warning(f"{model_name} article failed quality gate; retrying.")
        except Exception as e:
            logger.warning(f"{model_name} article error: {e}")
    return None


def _passes_quality_gate(art: Dict) -> bool:
    if not isinstance(art, dict) or not art.get("title") or not art.get("sections"):
        return False
    text = " ".join(
        [art.get("title", "")] + art.get("intro", []) +
        [p for s in art["sections"] for p in s.get("paragraphs", [])]
    )
    if any(m in text for m in PLACEHOLDER_MARKERS[:3]):
        return False
    return len(art["sections"]) >= 3 and len(text.split()) >= 350
