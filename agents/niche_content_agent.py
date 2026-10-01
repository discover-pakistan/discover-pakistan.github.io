"""
Niche Content Agent — Synthesizes high-engagement content across all 8 niches.
Generates structured card payloads and video scripts using Gemini LLM.
"""

import json
import logging
import os
from typing import Dict, Optional
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

def _get_genai_client():
    try:
        import dotenv
        dotenv.load_dotenv()
    except ImportError:
        pass
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not set in environment.")
        return None
    return genai.Client(api_key=api_key)

def generate_niche_content(niche: Dict, topic: Optional[str] = None, lang: str = "english") -> Dict:
    """
    Generates structured editorial content (headline, badge, highlight, bullets, CTA, captions)
    tailored to the niche profile using Gemini API with resilient multi-model fallback.
    """
    client = _get_genai_client()
    niche_id = niche.get("id", "tech_news")
    niche_name = niche.get("name", "Content Engine")
    tone_guidelines = niche.get("prompt_tone", "Informative and engaging.")
    badge_text = niche.get("badge_text", "DAILY UPDATE")

    theme_id = niche.get("primary_theme", "editorial_minimal")
    from video_engine.theme_system import MultiNicheThemeEngine

    prompt = f"""You are a world-class social media viral content editor and graphic art director for '{niche_name}'.
Tone & Philosophy: {tone_guidelines}
Target Language: {lang.upper()} (If Urdu, use natural, fluent Nastaliq-style Urdu. If Bilingual, English headline with Urdu body points).
Specific Topic / Focus: {topic if topic else "Create a timely, highly viral, top-performing post for this niche."}

Generate an ultra-high-converting, designer-ready social media content package in strict JSON format:
{{
    "badge": "{badge_text}",
    "category_tag": "A short 1-2 word category tag (e.g. 'MATCH STAT', 'TECH PULSE', 'MARKET HIGH', 'HIDDEN GEM')",
    "headline": "A bold, punchy, high-impact headline (5-8 words max, suitable for large bold typography)",
    "subdeck": "A compelling 1-line sub-headline that contextualizes the story (10-14 words)",
    "stat_number": "A prominent metric/number/stat (e.g. '4/18', '+1,450 PTS', '152 KPH', '2,438m', 'PKR 5,000', '10X')",
    "stat_label": "A short uppercase label for the stat (e.g. 'DEATH OVERS SPELL', 'ALL-TIME HIGH', 'PEAK SPEED', 'ELEVATION')",
    "highlight": "A single powerful insight or memorable quote (1 concise sentence)",
    "stance_a": "For debate niches: The argument for Option A / Agree (1-2 punchy lines)",
    "stance_b": "For debate niches: The argument for Option B / Disagree (1-2 punchy lines)",
    "bullet_points": [
        "First punchy takeaway / key point",
        "Second punchy takeaway / supporting fact",
        "Third punchy takeaway / strategic action"
    ],
    "call_to_action": "A natural save/share trigger (e.g. 'Save this for later' or 'Share with a cricket fan')",
    "reel_framework": {{
        "hook_0_3s": "Bold on-screen text + pattern-interrupt visual hook (Stops the scroll in first 0-3s)",
        "context_3_8s": "One sentence setting up the high-stakes problem or value proposition (3-8s)",
        "payoff_8_20s": "The actual value delivery (verse, highlight, tip, news, stats) (8-20s)",
        "cta_last_2_3s": "Clear follow, comment, save, or link-in-bio call-to-action (last 2-3s)"
    }},
    "voiceover_script": "A natural, conversational 20-second voiceover script (approx 45-55 words) that can be read aloud for a short Reel",
    "captions": {{
        "instagram": "Engaging IG caption with 3 bullet reflections, CTA, and 6-8 relevant hashtags",
        "threads": "Short, introspective, conversational question or reflection without hashtag spam (max 2 hashtags)",
        "facebook": "Detailed, community-focused commentary inviting discussion and family shares"
    }}
}}

Output ONLY valid JSON without markdown fences.
"""

    data = None
    if client:
        candidate_models = ["gemini-2.5-flash", "gemini-3-flash-preview", "gemini-3.1-flash-lite"]
        for model_name in candidate_models:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.7,
                    ),
                )
                data = json.loads(response.text.strip())
                logger.info(f"✅ Generated {niche_id} content via {model_name}: '{data.get('headline')}'")
                break
            except Exception as e:
                logger.warning(f"Model {model_name} attempt error: {e}. Trying fallback model...")

    if not data:
        data = _fallback_niche_content(niche, topic, lang)

    # Attach theme specifications and image/video prompt packages
    reel_fw = data.get("reel_framework", {})
    hook_text = reel_fw.get("hook_0_3s") or data.get("headline", "")
    context_text = reel_fw.get("context_3_8s") or data.get("subdeck", "")
    payoff_text = reel_fw.get("payoff_8_20s") or data.get("highlight", "")
    cta_text = reel_fw.get("cta_last_2_3s") or data.get("call_to_action", "")

    img_spec = MultiNicheThemeEngine.build_image_prompt(
        niche_id=niche_id,
        theme_id=theme_id,
        subject=data.get("headline"),
    )
    reel_spec = MultiNicheThemeEngine.build_reel_script(
        niche_id=niche_id,
        topic=topic or data.get("headline"),
        custom_hook=hook_text,
        custom_context=context_text,
        custom_payoff=payoff_text,
        custom_cta=cta_text,
    )

    data["image_prompt_spec"] = img_spec
    data["universal_reel_script"] = reel_spec.to_dict()
    data["recommended_production_mode"] = niche.get(
        "recommended_production_mode",
        "Motion graphics template + verified figures"
    )
    return data

def _fallback_niche_content(niche: Dict, topic: Optional[str], lang: str) -> Dict:
    """Deterministic fallback content if Gemini API is unreachable."""
    niche_id = niche.get("id", "tech_news")
    badge = niche.get("badge_text", "UPDATE")
    hashtags = " ".join(niche.get("hashtags", ["#Update", "#Trending"]))

    fallbacks = {
        "quran_spiritual": {
            "badge": "QURANIC HEARTS ✨",
            "headline": "جس دل میں صبر ہو، وہاں اللہ کی مدد ہوتی ہے",
            "highlight": "بے شک تنگی کے ساتھ آسانی ہے — سورۃ الشرح",
            "bullet_points": [
                "جب راستے بند ہونے لگیں، تو سمجھ لیں اللہ کچھ بہتر عطا کرنے والا ہے۔",
                "تہجد کے آنسو کبھی رائیگاں نہیں جاتے، اپنے دل کا حال رب سے کہیں۔",
                "ہر آزمائش کے پیچھے اللہ کی پوشیدہ رحمت چھپی ہوتی ہے۔"
            ],
            "call_to_action": "اس پوسٹ کو دعا اور تہجد کے لیے محفوظ فرمائیں 🕊️",
            "voiceover_script": "جب بھی زندگی میں اداسی یا پریشانی گھیرے، یاد رکھیں کہ اللہ اپنے بندوں کو کبھی تنہا نہیں چھوڑتا۔ صبر کریں، کیونکہ تنگی کے ساتھ ہی آسانی ہے۔",
            "captions": {
                "instagram": f"Al_Quran✨ || 🕊️ سکونِ قلب کی ضمانت\n\n- دلوں کا اصل سکون اللہ کی یاد میں ہے۔\n- ہر دکھ کے بعد رب کی طرف سے راحت کا وعدہ ہے۔\n\n{hashtags}",
                "threads": "کبھی ایسا ہوا ہے کہ دل بہت اداس ہو اور اچانک قرآن کی کوئی آیت سامنے آئے اور دل مطمئن ہو جائے؟ آپ کا پسندیدہ ترین سکون بخش کلام کون سا ہے؟",
                "facebook": "السلام علیکم پیارے دوستو! اللہ تعالیٰ ہم سب کو صبرِ جمیل عطا فرمائے اور ہر تنگی کے بعد آسانیاں پیدا فرمائے۔ آمین۔ اپنے پیاروں کے ساتھ شیئر کریں۔"
            }
        },
        "tech_news": {
            "badge": "TECH UPDATE ⚡",
            "headline": "Digital Pakistan 2026: Key Breakthroughs Shaping Telecom & Tech",
            "highlight": "Over 65% of national payments transitioned to instant digital rails this year.",
            "bullet_points": [
                "High-speed 5G test pilots approved for major metropolitan commercial corridors.",
                "Local assembly of smartphones hits new milestone, cutting import dependency.",
                "Solar tech adoption surges among tech freelance clusters nationwide."
            ],
            "call_to_action": "Save this update and share with a tech enthusiast 📲",
            "voiceover_script": "Here is your quick tech pulse: Pakistan's digital economy is accelerating as instant digital payments cross historic highs and local tech manufacturing expands.",
            "captions": {
                "instagram": f"Tech Pulse ⚡ || What you need to know about Pakistan's digital landscape today.\n\n{hashtags}",
                "threads": "Do you think 5G rollout will genuinely transform our remote freelancing hubs this year, or is fiber optic still the real MVP? What are you seeing in your city?",
                "facebook": "Tech Insights: The transformation of Pakistan's digital payment ecosystem is reaching every corner. Share your thoughts on how digital tools have impacted your work!"
            }
        },
        "debate_trigger": {
            "badge": "AGREE OR DISAGREE? 💬",
            "category_tag": "BURNING QUESTION",
            "headline": "A University Degree Is Becoming Irrelevant for High Earners",
            "subdeck": "With remote tech and AI booming, is 4 years of college still worth the cost?",
            "stat_number": "82%",
            "stat_label": "SAY SKILLS MATTER MORE",
            "highlight": "Your portfolio and proof of work speak louder than any paper credential.",
            "stance_a": "AGREE: Live projects, client results, and practical problem-solving beat theory every single time.",
            "stance_b": "DISAGREE: A degree builds foundational discipline, global visa eligibility, and long-term networking.",
            "bullet_points": [
                "Top international tech clients prioritize proof of work over formal degrees.",
                "Traditional corporate & civil sectors in Pakistan still strictly require a recognized degree.",
                "The winning path: Build high-income digital skills alongside formal education."
            ],
            "call_to_action": "WHERE DO YOU STAND? DROP 'AGREE' OR 'DISAGREE' BELOW 👇",
            "voiceover_script": "Agree or disagree? A university degree is becoming less relevant for high earners in Pakistan. With remote work and digital skills booming, where do you stand? Let us know in the comments!",
            "captions": {
                "instagram": f"AGREE OR DISAGREE? 💬 || Settle this in the comments 👇\n\n- Option A (Agree): Skills, portfolios, and real-world execution matter 100x more than GPA.\n- Option B (Disagree): A recognized degree provides immigration points, credibility, and security.\n\nWhere do you stand? Drop your vote below and explain why! 👇\n\n{hashtags}",
                "threads": "Honest question: If you could advise an 18-year-old in Pakistan today, would you tell them to spend 4 years on a traditional degree or 4 years mastering high-income digital skills? Agree or disagree: Degrees are overhyped.",
                "facebook": "PUBLIC PERSPECTIVE POLL: Agree or Disagree?\n\n'A university degree is no longer necessary to earn a high income in today's digital economy.'\n\nStance A: Skills and portfolio speak for themselves.\nStance B: Degree provides lifelong safety, visa opportunities, and networking.\n\nShare your honest experience in the comments below!"
            }
        }
    }

    fb = fallbacks.get(niche_id)
    if fb:
        return fb

    # Generic default fallback
    return {
        "badge": badge,
        "headline": f"{niche.get('name', 'Featured Topic')} Insight",
        "highlight": "Staying ahead of trends creates compounding long-term advantage.",
        "bullet_points": [
            "Consistency and quality drive authentic community engagement.",
            "Timely execution separates high performers from spectators.",
            "Focus on value-first insights that solve real everyday problems."
        ],
        "call_to_action": "Bookmark this post and share with your network ✨",
        "voiceover_script": f"Here is a key insight from {niche.get('name')}: Focus on consistency, value, and long-term execution to master your craft.",
        "captions": {
            "instagram": f"{niche.get('caption_header', 'Daily Update')} || Key insights for today.\n\n{hashtags}",
            "threads": f"What is the single biggest lesson you have learned in {niche.get('category', 'this field')} lately?",
            "facebook": f"Today's update from {niche.get('name')}. Let us know your perspective in the comments below!"
        }
    }
