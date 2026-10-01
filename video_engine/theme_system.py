"""
Versatile Theme System & Prompt Library Engine.
Empowers multi-niche content automation across 8 distinct media pages:
1. QuranicHearts (Faith & Learning)
2. kalamullahonline.edu (Faith & Learning)
3. DiscoverPakistan.TV (Culture & Sport)
4. PakistanCricketBoard (Culture & Sport)
5. ProPakistani (News & Business)
6. businessbytespk (News & Business)
7. IT Agency (Tech & Agency)
8. mlgaafan (Pop-Culture & Entertainment)

Implements:
- 6 Reusable Visual Themes with bracketed parameter interpolation
- 4 Content Families (Faith & Learning, Culture & Sport, News & Business, Tech & Agency)
- Master Image Prompt Generator & Per-Niche Presets
- Strict Hardcoded Compliance & Safety Filters
- Universal 4-Beat Reel Script & AI Video Prompt Framework (0-3s Hook, 3-8s Context, 8-20s Payoff, 2-3s CTA)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import logging
import re

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# 1. Content Families & Categorization
# ─────────────────────────────────────────────────────────────────────────────

class ContentFamily(str, Enum):
    FAITH_AND_LEARNING = "Faith & Learning"
    CULTURE_AND_SPORT = "Culture & Sport"
    NEWS_AND_BUSINESS = "News & Business"
    TECH_AND_AGENCY = "Tech & Agency"


CONTENT_FAMILY_MAP = {
    "quran_spiritual": ContentFamily.FAITH_AND_LEARNING,
    "quran_edu": ContentFamily.FAITH_AND_LEARNING,
    "travel_pakistan": ContentFamily.CULTURE_AND_SPORT,
    "sports_cricket": ContentFamily.CULTURE_AND_SPORT,
    "tech_news": ContentFamily.NEWS_AND_BUSINESS,
    "business_finance": ContentFamily.NEWS_AND_BUSINESS,
    "it_agency": ContentFamily.TECH_AND_AGENCY,
    "viral_youth": ContentFamily.TECH_AND_AGENCY,
    "debate_trigger": ContentFamily.NEWS_AND_BUSINESS,
}


# ─────────────────────────────────────────────────────────────────────────────
# 2. The 6 Reusable Visual Themes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ThemeDefinition:
    id: str
    name: str
    visual_language: str
    default_palette: str
    framing_guide: str
    lighting_guide: str
    best_fit_niches: List[str]
    negative_prompt: str
    aspect_ratios: List[str] = field(default_factory=lambda: ["1:1", "4:5", "9:16", "16:9"])
    skeleton_template: str = (
        "{theme_style}, {subject}, {composition}, {palette}, {lighting}, "
        "leave negative space for text overlay top/bottom, {aspect_ratio} for Facebook feed/story, "
        "high detail, brand-safe, no watermarks, no text baked into image --no {negative_prompt}"
    )


THEME_CATALOG: Dict[str, ThemeDefinition] = {}

def _init_theme_catalog() -> Dict[str, ThemeDefinition]:
    """Dynamically loads themes from YAML directories with robust built-in fallbacks."""
    import yaml
    from pathlib import Path

    # 1. Built-in Canonical Definitions (always available standalone)
    catalog: Dict[str, ThemeDefinition] = {
        "bold_sports_dynamic": ThemeDefinition(
            id="bold_sports_dynamic",
            name="Bold Sports Dynamic",
            visual_language="High-contrast action shots, motion-blur streaks, team-color gradients, stat overlays",
            default_palette="#10B981, #F59E0B, #0F172A, #FFFFFF",
            framing_guide="leave negative space for text overlay top/bottom",
            lighting_guide="dramatic stadium floodlights with rim highlights",
            best_fit_niches=["sports_cricket"],
            negative_prompt="deformed anatomy, distorted faces, unrealistic player bodies, third-party unauthorized sponsor logos, fake jerseys, cartoon, low-res, watermarks, text baked into image, clutter"
        ),
        "cinematic_documentary": ThemeDefinition(
            id="cinematic_documentary",
            name="Cinematic Documentary",
            visual_language="Real-photo aesthetic, warm golden-hour tones, shallow depth of field, travel-doc grading",
            default_palette="#C89666, #2D6A4F, #3D5A80, #E0FBFC",
            framing_guide="leave negative space for text overlay top/bottom",
            lighting_guide="natural golden hour sun and atmospheric mountain haze",
            best_fit_niches=["travel_pakistan"],
            negative_prompt="oversaturated CGI, fantasy landmarks, fake geography, surreal alien terrain, cartoon, 3D render, low-res, blur, watermark, logos, text baked into image, clutter"
        ),
        "editorial_minimal": ThemeDefinition(
            id="editorial_minimal",
            name="Editorial Minimal",
            visual_language="Clean grid layout, sans-serif headline, white/off-white background, single accent color, data-chart friendly",
            default_palette="#F8FAFC, #2563EB, #0F172A, #F59E0B",
            framing_guide="leave negative space for text overlay top/bottom",
            lighting_guide="clean studio softbox lighting with even contrast",
            best_fit_niches=["tech_news", "sports_cricket", "travel_pakistan"],
            negative_prompt="clutter, noisy textures, skeuomorphism, chaotic gradients, realistic photo mess, unreadable charts, low-res, watermarks, text baked into image"
        ),
        "flat_pop_meme": ThemeDefinition(
            id="flat_pop_meme",
            name="Flat Pop / Meme",
            visual_language="Bright flat illustration, bold rounded fonts, high-energy layout, sticker-style call-outs",
            default_palette="#FACC15, #EC4899, #06B6D4, #000000",
            framing_guide="leave negative space for text overlay top/bottom",
            lighting_guide="high-key flat ambient illustration lighting",
            best_fit_niches=["memes_youth"],
            negative_prompt="copyrighted cartoon characters, Disney/Marvel/Anime logos, real identifiable celebrity faces, gloomy shadows, realistic gore, low-res, watermark, text baked into image"
        ),
        "sacred_geometry": ThemeDefinition(
            id="sacred_geometry",
            name="Sacred Geometry",
            visual_language="Islamic geometric patterns, arabesque borders, calligraphy-forward, muted gold/teal/navy, no human or figurative imagery",
            default_palette="#D4AF37, #0F4C5C, #1D2D44, #F5F5FA",
            framing_guide="calligraphy-style negative space at center",
            lighting_guide="soft ambient divine light",
            best_fit_niches=["quran_spiritual", "quran_edu"],
            negative_prompt="human figures, faces, people, living beings, animals, idols, statues, text baked in, letters, watermark, logos of third parties, clutter, low-res"
        ),
        "tech_gradient_glass": ThemeDefinition(
            id="tech_gradient_glass",
            name="Tech Gradient / Glass",
            visual_language="Dark background, neon-gradient glassmorphism cards, glowing icons, futuristic grid lines",
            default_palette="#090A0F, #8B5CF6, #06B6D4, #3B82F6",
            framing_guide="leave negative space for text overlay top/bottom",
            lighting_guide="volumetric neon rim light and glowing cyber luminescence",
            best_fit_niches=["tech_news"],
            negative_prompt="opaque flat plastic, dull grey, messy wires, unreadable glass refraction, low contrast, low-res, watermarks, third-party logos, text baked into image"
        ),
    }

    # 2. Check candidate directories for custom or updated YAML definitions
    candidate_dirs = [
        Path(__file__).parent.parent / "social-content-engine" / "themes",
        Path(__file__).parent.parent / "themes",
        Path(__file__).parent / "themes",
    ]

    for yaml_dir in candidate_dirs:
        if yaml_dir.exists():
            for yf in yaml_dir.glob("*.yaml"):
                try:
                    with open(yf, "r", encoding="utf-8") as f:
                        d = yaml.safe_load(f)
                    tid = yf.stem
                    catalog[tid] = ThemeDefinition(
                        id=tid,
                        name=d.get("name", tid),
                        visual_language=d.get("description", ""),
                        default_palette=", ".join(d.get("color_palette", [])),
                        framing_guide="leave negative space for text overlay top/bottom",
                        lighting_guide="high detail studio lighting",
                        best_fit_niches=[],
                        negative_prompt=d.get("negative_prompt", "")
                    )
                except Exception as e:
                    logger.warning(f"Error loading theme {yf}: {e}")

    return catalog

THEME_CATALOG = _init_theme_catalog()



# ─────────────────────────────────────────────────────────────────────────────
# 3. Hardcoded Non-Negotiable Compliance Filters
# ─────────────────────────────────────────────────────────────────────────────

class ComplianceRuleViolation(Exception):
    """Raised when generated prompt or content violates strict niche safety guidelines."""
    pass


class ComplianceValidator:
    """
    Hardcoded compliance engine baked into the pipeline.
    Validates prompts, copy, and media modes against safety policies.
    """

    # Prohibited tokens for Islamic niches (Strictly zero figurative/human depictions)
    ISLAMIC_FORBIDDEN_TOKENS = [
        "human face", "face", "man", "woman", "boy", "girl", "child",
        "person", "people", "portrait", "eyes", "lips", "silhouette of prophet",
        "prophet", "angel", "god", "depiction of", "body", "character"
    ]

    # Universal prohibited prompt artifacts
    UNIVERSAL_FORBIDDEN = [
        "watermark", "lorem ipsum", "shutterstock", "getty", "stock photo stamp"
    ]

    @classmethod
    def validate_image_prompt(cls, niche_id: str, prompt: str) -> Tuple[bool, List[str]]:
        """
        Validates an image generation prompt for compliance.
        Splits into positive prompt and negative prompt (separated by --no) to evaluate rules accurately.
        """
        violations = []
        parts = prompt.split("--no")
        positive_part = parts[0].lower()
        negative_part = parts[1].lower() if len(parts) > 1 else ""

        # Rule 1: Zero figurative depictions in positive prompt for Faith & Learning
        if niche_id in ["quran_spiritual", "quran_edu"]:
            for token in cls.ISLAMIC_FORBIDDEN_TOKENS:
                pattern = rf"\b{re.escape(token)}\b"
                if re.search(pattern, positive_part):
                    # Check if it was explicitly negated in positive part (e.g. "no human figures")
                    if f"no {token}" not in positive_part and f"zero {token}" not in positive_part:
                        violations.append(
                            f"Faith Compliance Violation: Token '{token}' detected in positive prompt. "
                            "Islamic themes strictly prohibit human/figurative depictions."
                        )

        # Rule 2: Must request negative space for text overlay
        if "negative space" not in positive_part and "empty" not in positive_part and "space for" not in positive_part:
            violations.append(
                "Layout Violation: Prompt must explicitly specify negative space for text overlay."
            )

        # Rule 3: Must forbid baked-in text (added in post)
        if "no text baked into image" not in positive_part and "text baked in" not in negative_part:
            violations.append(
                "Typography Violation: Prompt must specify 'no text baked into image' or appropriate negative filter."
            )

        # Rule 4: Sports Player Rule
        if niche_id == "sports_cricket":
            if "ai face" in positive_part or "face generation" in positive_part:
                violations.append(
                    "Sports Compliance Violation: Do not generate AI faces of real national athletes. "
                    "Use authentic licensed editorial photography or motion-blur silhouette."
                )

        # Rule 5: Universal check on positive prompt (forbidden artifacts)
        for token in ["lorem ipsum", "shutterstock", "getty", "stock photo stamp"]:
            if token in positive_part:
                violations.append(f"Universal Violation: Forbidden term '{token}' in positive prompt.")

        is_valid = len(violations) == 0
        return is_valid, violations

    @classmethod
    def enforce_image_prompt(cls, niche_id: str, prompt: str) -> str:
        """Sanitizes positive prompt and automatically injects required compliance guardrails."""
        parts = prompt.split("--no")
        positive_part = parts[0]
        negative_part = ("--no" + parts[1]) if len(parts) > 1 else "--no logos of third parties, real identifiable people, low-res, clutter"

        # If faith niche, remove any accidental human depiction terms from POSITIVE prompt only
        if niche_id in ["quran_spiritual", "quran_edu"]:
            for token in cls.ISLAMIC_FORBIDDEN_TOKENS:
                # Don't replace if it's already "no human figures"
                if f"no {token}" in positive_part.lower():
                    continue
                pattern = rf"\b{re.escape(token)}\b"
                positive_part = re.sub(pattern, "geometric motif", positive_part, flags=re.IGNORECASE)

            if "no human figures" not in positive_part.lower():
                positive_part = positive_part.rstrip(" ,") + ", no human figures"

        # Guarantee negative space instruction
        if "negative space" not in positive_part.lower() and "empty space" not in positive_part.lower():
            positive_part = positive_part.rstrip(" ,") + ", generous negative space for typography overlay"

        # Guarantee clean canvas instruction
        if "no text baked into image" not in positive_part.lower():
            positive_part = positive_part.rstrip(" ,") + ", no text baked into image, brand-safe, no watermarks"

        sanitized = f"{positive_part.strip()} {negative_part.strip()}".strip()
        return sanitized


# ─────────────────────────────────────────────────────────────────────────────
# 4. Master Image Prompt Library & Niche Presets
# ─────────────────────────────────────────────────────────────────────────────

NICHE_IMAGE_PRESETS: Dict[str, Dict[str, Any]] = {
    "quran_spiritual": {
        "page_name": "QuranicHearts",
        "primary_theme": "sacred_geometry",
        "allowed_themes": ["sacred_geometry", "cinematic_documentary"],
        "default_subject": "Intricate gold arabesque centerpiece surrounded by sacred Islamic star geometry",
        "sample_prompt": (
            "Elegant Islamic geometric pattern background, gold and deep teal palette, intricate arabesque border, "
            "soft ambient light, calligraphy-style negative space at center for Arabic verse text, square 1:1, "
            "no human figures, no text baked into image --no logos of third parties, real identifiable people, low-res, clutter"
        ),
        "aspect_ratio": "1:1",
        "recommended_production_mode": (
            "Static Sacred-Geometry background + animated Arabic/translation text + Quran recitation audio (licensed) — not full AI video gen"
        ),
    },
    "quran_edu": {
        "page_name": "kalamullahonline.edu",
        "primary_theme": "sacred_geometry",
        "allowed_themes": ["sacred_geometry", "editorial_minimal"],
        "default_subject": "Warm minimal illustration of an open book with a lantern glow, geometric mosque-window motif in corner",
        "sample_prompt": (
            "Warm minimal illustration of an open book with a lantern glow, geometric mosque-window motif in corner, "
            "soft beige and gold tones, clean space at bottom for course-title text, 4:5 portrait, brand-safe, "
            "no human figures, no text baked into image --no logos of third parties, real identifiable people, low-res, clutter"
        ),
        "aspect_ratio": "4:5",
        "recommended_production_mode": (
            "Talking-head / authentic tutor clips + word-by-word graphic text-card intercuts"
        ),
    },
    "travel_pakistan": {
        "page_name": "DiscoverPakistan.TV",
        "primary_theme": "cinematic_documentary",
        "allowed_themes": ["cinematic_documentary", "editorial_minimal"],
        "default_subject": "Golden-hour landscape photo of Hunza Valley with Passu Cones in the background",
        "sample_prompt": (
            "Golden-hour landscape photo style of Hunza Valley, cinematic color grade, wide-angle, subtle lens flare, "
            "empty sky area top-left for headline text, 9:16 for reels cover, photorealistic, brand-safe, "
            "no text baked into image --no logos of third parties, real identifiable people, low-res, clutter, cartoon"
        ),
        "aspect_ratio": "9:16",
        "recommended_production_mode": (
            "Real drone/phone B-roll + AI motion (Runway/Pika/Luma) only for transitions, not fabricated locations"
        ),
    },
    "sports_cricket": {
        "page_name": "PakistanCricketBoard",
        "primary_theme": "bold_sports_dynamic",
        "allowed_themes": ["bold_sports_dynamic", "editorial_minimal"],
        "default_subject": "Dynamic sports graphic, motion-blur cricket ball trail, stadium floodlight flare",
        "sample_prompt": (
            "Dynamic sports graphic, green-white color scheme, motion-blur cricket ball trail, bold diagonal composition, "
            "stat-card frame bottom third left empty for player numbers, 1:1 or 4:5, energetic lighting, brand-safe, "
            "no text baked into image --no logos of third parties, fake player faces, low-res, clutter"
        ),
        "aspect_ratio": "4:5",
        "recommended_production_mode": (
            "Real match footage/highlights only — AI limited to intro/outro graphics and kinetic stat cards"
        ),
    },
    "tech_news": {
        "page_name": "ProPakistani",
        "primary_theme": "editorial_minimal",
        "allowed_themes": ["editorial_minimal", "tech_gradient_glass"],
        "default_subject": "Clean flat-design tech news graphic, minimal icon of 5G tower and smartphone chip",
        "sample_prompt": (
            "Clean flat-design tech news graphic, white background, single blue accent shape, minimal icon of 5G tower and smartphone chip, "
            "generous white space for headline, 1:1 square, brand-safe, no text baked into image "
            "--no logos of third parties, real identifiable people, low-res, clutter"
        ),
        "aspect_ratio": "1:1",
        "recommended_production_mode": (
            "Text-driven news reel: AI-generated minimalist background + kinetic typography of real facts"
        ),
    },
    "business_finance": {
        "page_name": "businessbytespk",
        "primary_theme": "editorial_minimal",
        "allowed_themes": ["editorial_minimal", "tech_gradient_glass"],
        "default_subject": "Minimal business infographic style, simple upward-trend line icon, currency pulse",
        "sample_prompt": (
            "Minimal business infographic style, off-white background, navy and mustard accent, simple upward-trend line icon, "
            "clear space for a 3–5 word headline, 1:1, crisp vector aesthetics, brand-safe, no text baked into image "
            "--no logos of third parties, real identifiable people, low-res, clutter"
        ),
        "aspect_ratio": "1:1",
        "recommended_production_mode": (
            "Data-viz motion graphics (After Effects / Compositor template) with real verified figures"
        ),
    },
    "it_agency": {
        "page_name": "IT Agency (EN/UR)",
        "primary_theme": "tech_gradient_glass",
        "allowed_themes": ["tech_gradient_glass", "editorial_minimal"],
        "default_subject": "Dark futuristic background, glassmorphism card floating center, subtle circuit-line texture",
        "sample_prompt": (
            "Dark futuristic background, glassmorphism card floating center, glowing blue-purple gradient, subtle circuit-line texture, "
            "empty glass panel for service name/logo, 1:1 and 16:9 variants, modern SaaS aesthetic, brand-safe, "
            "no text baked into image --no logos of third parties, real identifiable people, low-res, clutter"
        ),
        "aspect_ratio": "4:5",
        "recommended_production_mode": (
            "Case-study script + Tech-Gradient animated template + voiceover (TTS or real bilingual talent)"
        ),
    },
    "viral_youth": {
        "page_name": "mlgaafan",
        "primary_theme": "flat_pop_meme",
        "allowed_themes": ["flat_pop_meme", "bold_sports_dynamic"],
        "default_subject": "Bright flat-illustration meme template, exaggerated expressive character silhouette",
        "sample_prompt": (
            "Bright flat-illustration meme template, bold thick outlines, punchy yellow/pink palette, "
            "exaggerated expressive character silhouette (non-copyrighted), speech-bubble space empty, 1:1 square, "
            "brand-safe, no text baked into image --no logos of third parties, copyrighted characters, low-res, clutter"
        ),
        "aspect_ratio": "1:1",
        "recommended_production_mode": (
            "Meme-style quick-cut edit, trending desi audio, flat-pop text stickers & reaction cards"
        ),
    },
    "debate_trigger": {
        "page_name": "Public Perspective",
        "primary_theme": "editorial_minimal",
        "allowed_themes": ["editorial_minimal", "bold_sports_dynamic", "tech_gradient_glass"],
        "default_subject": "Split-frame visual contrast with high tension red and cyan dual lighting",
        "sample_prompt": (
            "Split-frame visual contrast, minimalist editorial debate background, high tension red and cyan accent lighting, "
            "central divider, generous space on both left and right flanks for Agree vs Disagree arguments, 4:5 portrait, "
            "no text baked into image --no logos of third parties, real identifiable people, low-res, clutter"
        ),
        "aspect_ratio": "4:5",
        "recommended_production_mode": (
            "Split-card video poll with countdown timer + dual audio soundbites prompting immediate comments"
        ),
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# 5. Reels/Video Prompt & Script Framework (Universal 4-Beat Structure)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ReelBeat:
    name: str
    timing: str
    duration_range: Tuple[float, float]
    purpose: str
    content: str


@dataclass
class UniversalReelScript:
    niche_id: str
    page_name: str
    topic: str
    hook: ReelBeat
    context: ReelBeat
    payoff: ReelBeat
    cta: ReelBeat
    production_mode: str
    ai_video_prompt: str
    total_duration_seconds: float = 20.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "niche_id": self.niche_id,
            "page_name": self.page_name,
            "topic": self.topic,
            "production_mode": self.production_mode,
            "total_duration_sec": self.total_duration_seconds,
            "beats": [
                {"beat": self.hook.name, "time": self.hook.timing, "purpose": self.hook.purpose, "script": self.hook.content},
                {"beat": self.context.name, "time": self.context.timing, "purpose": self.context.purpose, "script": self.context.content},
                {"beat": self.payoff.name, "time": self.payoff.timing, "purpose": self.payoff.purpose, "script": self.payoff.content},
                {"beat": self.cta.name, "time": self.cta.timing, "purpose": self.cta.purpose, "script": self.cta.content},
            ],
            "ai_video_prompt": self.ai_video_prompt
        }


# Per-Niche Hook & Script Templates
NICHE_HOOK_CATALOG: Dict[str, Dict[str, str]] = {
    "quran_spiritual": {
        "hook_line": "This verse changes how you see hardship…",
        "hook_visual": "Instant sound onset + gold arabesque pulse + 0.0s top hook pill banner",
        "sample_context": "When life feels heavy, Allah reminds us that relief is already written.",
        "sample_payoff": "Recitation of Surah Ash-Sharh (94:5-6) with synchronized glowing typography.",
        "sample_cta": "Save this verse for Tahajjud tonight ✨ Tag someone who needs Sabr today.",
    },
    "quran_edu": {
        "hook_line": "3 signs you need a Tajweed teacher",
        "hook_visual": "Pattern interrupt text card + close-up of open Uthmanic Mus-haf",
        "sample_context": "Most students mispronounce these 3 letters without realizing it alters the meaning.",
        "sample_payoff": "Side-by-side pronunciation breakdown of Qaf vs Kaf with instant audio correction.",
        "sample_cta": "Comment 'TAJWEED' for our free 1-on-1 diagnostic lesson link.",
    },
    "travel_pakistan": {
        "hook_line": "You won't believe this exists in Pakistan",
        "hook_visual": "Breathtaking FPV drone plunge over Katpana Cold Desert snow-sand dunes",
        "sample_context": "Hidden 2,400 meters above sea level in Skardu lies a desert where winter brings snow over sand.",
        "sample_payoff": "Cinematic 3-stop journey: Katpana dunes, Upper Kachura lake, and Shangrila dawn.",
        "sample_cta": "Save this for your northern roadtrip · Share with your travel squad 🇵🇰",
    },
    "sports_cricket": {
        "hook_line": "Relive the moment that won us the match",
        "hook_visual": "Thunderous 150 KPH toe-crushing yorker replay with shattered stumps sound fx",
        "sample_context": "Pakistan needed 2 wickets with 7 runs to defend in the final over.",
        "sample_payoff": "Ball-by-ball tension cut with real commentary crescendo and stadium roar.",
        "sample_cta": "Drop a 💚 if you believe in Green Shirts! Who was your Player of the Match?",
    },
    "tech_news": {
        "hook_line": "Here's what changed in Pakistan's telecom sector this week",
        "hook_visual": "Fast-cut neon grid radar graphic with breaking news flash banner",
        "sample_context": "PTA just approved the final framework for commercial 5G spectrum auction.",
        "sample_payoff": "3 concrete impacts: rollout timeline, expected city coverage, and device compatibility.",
        "sample_cta": "Follow @ProPakistani for daily verified tech intelligence.",
    },
    "business_finance": {
        "hook_line": "3 numbers that explain this quarter",
        "hook_visual": "Clean executive chart bar animating upwards with ticker audio",
        "sample_context": "The Pakistan Stock Exchange just crossed an all-time record index level.",
        "sample_payoff": "Stat 1: Inflation dropped to single digits. Stat 2: Remittances hit $3B. Stat 3: Tech exports up 32%.",
        "sample_cta": "Save this byte for your market briefing · Share with an entrepreneur.",
    },
    "it_agency": {
        "hook_line": "Here's how we cut a client's server cost by 40%",
        "hook_visual": "Floating glass card with glowing cost drop line chart",
        "sample_context": "A high-traffic e-commerce client was burning $8,000/mo on unoptimized cloud instances.",
        "sample_payoff": "We refactored their architecture into serverless workers and edge caching in 14 days.",
        "sample_cta": "DM us 'AUDIT' to book a free architectural review for your software.",
    },
    "viral_youth": {
        "hook_line": "POV: when your squad finally wins",
        "hook_visual": "Ultra-fast meme edit with punchy cartoon sticker pattern-interrupt",
        "sample_context": "After 14 consecutive losses in ranked lobby at 3:00 AM.",
        "sample_payoff": "The legendary clutch moment with victory hype and hilarious voice chat reactions.",
        "sample_cta": "Tag that one friend who always gets carried 😂👇",
    },
    "debate_trigger": {
        "hook_line": "Degree vs Skills in 2026: Settle this debate once and for all",
        "hook_visual": "Split red vs cyan screen with flashing 'AGREE OR DISAGREE?' badge",
        "sample_context": "82% of tech leaders say a formal degree no longer determines earning potential.",
        "sample_payoff": "Side A: Live code and client results win. Side B: Degrees provide immigration and corporate visas.",
        "sample_cta": "Where do you stand? Comment 'DEGREE' or 'SKILLS' below! 👇",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# 6. Core Engine: MultiNicheThemeEngine
# ─────────────────────────────────────────────────────────────────────────────

class MultiNicheThemeEngine:
    """
    Central Coordinator for:
    - Resolving Themes × Niches with full cross-pollination
    - Generating Master Image Prompts with hardcoded compliance checks
    - Assembling Universal 4-Beat Reel Scripts
    - Generating AI Video Prompts for Runway, Pika, Luma, etc.
    """

    @classmethod
    def get_theme(cls, theme_id: str) -> ThemeDefinition:
        theme_key = theme_id.lower().replace("-", "_").replace(" ", "_")
        if theme_key in THEME_CATALOG:
            return THEME_CATALOG[theme_key]
        if "editorial_minimal" in THEME_CATALOG:
            logger.warning(f"Theme '{theme_id}' not found. Defaulting to 'editorial_minimal'.")
            return THEME_CATALOG["editorial_minimal"]
        if THEME_CATALOG:
            fallback = next(iter(THEME_CATALOG.values()))
            logger.warning(f"Theme '{theme_id}' not found. Defaulting to '{fallback.id}'.")
            return fallback
        raise RuntimeError("No theme definitions available in THEME_CATALOG.")

    @classmethod
    def get_niche_preset(cls, niche_id: str) -> Dict[str, Any]:
        preset = NICHE_IMAGE_PRESETS.get(niche_id)
        if not preset:
            return NICHE_IMAGE_PRESETS["tech_news"]
        return preset

    @classmethod
    def build_image_prompt(
        cls,
        niche_id: str,
        theme_id: Optional[str] = None,
        subject: Optional[str] = None,
        palette_override: Optional[str] = None,
        framing_override: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        extra_negative: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Builds a production-ready image generation prompt adhering to the Master Skeleton:
        [THEME STYLE], [SUBJECT], [COMPOSITION/framing], [COLOR PALETTE],
        [LIGHTING], leave negative space for text overlay top/bottom,
        [ASPECT RATIO] for Facebook feed/story, high detail, brand-safe,
        no watermarks, no text baked into image --no [negative_prompt]
        """
        preset = cls.get_niche_preset(niche_id)
        selected_theme_id = theme_id or preset["primary_theme"]
        theme = cls.get_theme(selected_theme_id)

        # Swappable variables
        final_subject = subject or preset["default_subject"]
        final_palette = palette_override or theme.default_palette
        final_framing = framing_override or theme.framing_guide
        final_aspect = aspect_ratio or preset.get("aspect_ratio", "1:1")

        # Negative prompt consolidation
        neg_parts = [theme.negative_prompt]
        if extra_negative:
            neg_parts.append(extra_negative)
        neg_parts.append("logos of third parties, real identifiable people, low-res, clutter")
        combined_negative = ", ".join(dict.fromkeys(", ".join(neg_parts).split(", ")))

        raw_prompt = theme.skeleton_template.format(
            theme_style=f"{theme.name} style, {theme.visual_language}",
            subject=final_subject,
            composition=final_framing,
            palette=final_palette,
            lighting=theme.lighting_guide,
            aspect_ratio=final_aspect,
            negative_prompt=combined_negative
        )

        # Enforce hardcoded compliance
        compliant_prompt = ComplianceValidator.enforce_image_prompt(niche_id, raw_prompt)
        is_valid, violations = ComplianceValidator.validate_image_prompt(niche_id, compliant_prompt)

        return {
            "niche_id": niche_id,
            "page_name": preset["page_name"],
            "theme_id": theme.id,
            "theme_name": theme.name,
            "aspect_ratio": final_aspect,
            "prompt": compliant_prompt,
            "negative_prompt": combined_negative,
            "is_compliant": is_valid,
            "compliance_violations": violations,
            "recommended_production_mode": preset["recommended_production_mode"]
        }

    @classmethod
    def build_ai_video_prompt(
        cls,
        theme_id: str,
        scene_description: str,
        palette: Optional[str] = None,
        camera_motion: str = "smooth cinematic camera drift and subtle forward push",
        aspect_ratio: str = "9:16 vertical",
        duration_seconds: int = 4
    ) -> str:
        """
        AI video prompt template for tools like Runway Gen-3, Pika Labs, Luma Dream Machine:
        [THEME visual style], [scene description], smooth camera motion,
        loopable, no on-screen text baked in (added in post), 9:16 vertical,
        3–5 second clip, consistent color grade with [palette]
        """
        theme = cls.get_theme(theme_id)
        chosen_palette = palette or theme.default_palette

        prompt = (
            f"{theme.name} aesthetic, {theme.visual_language}. "
            f"Scene: {scene_description}. "
            f"Motion: {camera_motion}, seamless loopable motion. "
            f"Specifications: no on-screen text baked in (text added in post-production), {aspect_ratio}, "
            f"{duration_seconds}-second clip, consistent cinematic color grade with {chosen_palette}. "
            f"Ultra high fidelity, 4k master grading, brand-safe, zero artifacts."
        )
        return prompt

    @classmethod
    def build_reel_script(
        cls,
        niche_id: str,
        topic: Optional[str] = None,
        custom_hook: Optional[str] = None,
        custom_context: Optional[str] = None,
        custom_payoff: Optional[str] = None,
        custom_cta: Optional[str] = None,
    ) -> UniversalReelScript:
        """
        Constructs a complete 4-Beat Reel Script adhering to the Universal Structure:
        Beat 1: Hook (0–3s) — Bold on-screen text + pattern-interrupt visual
        Beat 2: Context (3–8s) — One sentence setting up the value
        Beat 3: Payoff (8–20s) — The actual core content (verse, highlight, tip, news)
        Beat 4: CTA (last 2–3s) — Follow / comment / link-in-bio
        """
        preset = cls.get_niche_preset(niche_id)
        hook_info = NICHE_HOOK_CATALOG.get(niche_id, NICHE_HOOK_CATALOG["tech_news"])
        theme_id = preset["primary_theme"]

        hook_line = custom_hook or hook_info["hook_line"]
        context_line = custom_context or hook_info["sample_context"]
        payoff_line = custom_payoff or hook_info["sample_payoff"]
        cta_line = custom_cta or hook_info["sample_cta"]
        resolved_topic = topic or hook_line

        # Generate accompanying AI video background prompt for the reel
        video_prompt = cls.build_ai_video_prompt(
            theme_id=theme_id,
            scene_description=f"Atmospheric background backdrop for '{resolved_topic}', ample central negative space for kinetic captions",
            camera_motion="slow, continuous, ambient cinematic pan",
            aspect_ratio="9:16 vertical",
            duration_seconds=5
        )

        return UniversalReelScript(
            niche_id=niche_id,
            page_name=preset["page_name"],
            topic=resolved_topic,
            production_mode=preset["recommended_production_mode"],
            hook=ReelBeat(
                name="Hook",
                timing="0–3s",
                duration_range=(0.0, 3.0),
                purpose="Bold on-screen text + pattern-interrupt visual (Stops the scroll)",
                content=hook_line
            ),
            context=ReelBeat(
                name="Context",
                timing="3–8s",
                duration_range=(3.0, 8.0),
                purpose="One sentence setting up the high-stakes value proposition",
                content=context_line
            ),
            payoff=ReelBeat(
                name="Payoff",
                timing="8–20s",
                duration_range=(8.0, 20.0),
                purpose="The core content deliverable (verse, highlight, tip, news, stats)",
                content=payoff_line
            ),
            cta=ReelBeat(
                name="Call to Action",
                timing="20–23s (Last 2–3s)",
                duration_range=(20.0, 23.0),
                purpose="Follow / comment / save / link-in-bio trigger",
                content=cta_line
            ),
            ai_video_prompt=video_prompt,
            total_duration_seconds=22.0
        )
