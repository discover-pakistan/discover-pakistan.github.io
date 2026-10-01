"""
Niche Catalog & Versatile Theme Engine.
Empowers automated multi-niche content generation across 8 distinct media verticals:
1. QuranicHearts (Spiritual & Emotional Quran)
2. Kalamullah Online (Quranic Education & Word-by-Word Tafseer)
3. Discover Pakistan TV (Scenic Tourism, Heritage & Aerial Landscapes)
4. MLGAA Fan (Viral Pakistani Pop Culture & Desi Relatable Youth)
5. Pakistan Cricket Board (Cricket Hype, Player Milestones & Match Stats)
6. ProPakistani (Tech News, Telecom, Policies & Gadgets)
7. Business Bytes PK (Business, Finance, PSX & Startup Insights)
8. IT Agency English & Urdu (Web/App Development, AI Automation & Tech Services)
"""

from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

NICHE_ROSTER: Dict[str, Dict] = {
    # ── 1. Spiritual & Emotional Quran (QuranicHearts Style) ──
    "quran_spiritual": {
        "id": "quran_spiritual",
        "name": "Quranic Hearts — Spiritual Solace",
        "reference_page": "https://www.facebook.com/QuranicHearts",
        "category": "Islamic Spirituality",
        "tagline": "Comfort for Tired Hearts · سكينة واطمئنان",
        "badge_text": "QURANIC HEARTS ✨",
        "primary_color": (255, 215, 80),      # Royal Gold
        "secondary_color": (245, 245, 255),   # Soft White
        "accent_color": (64, 180, 220),       # Calming Turquoise
        "bg_theme": "clean_sky",              # or starry_sky / kaaba_rain
        "ambient_audio": "ambient_wind.mp3",
        "aspect_ratios": ["9:16", "4:5", "1:1"],
        "default_lang": "urdu",
        "hashtags": [
            "#QuranicHearts", "#SoulfulQuran", "#PeaceOfMind", "#Tahajjud",
            "#IslamicReminders", "#Dua", "#Sabr", "#QuranRecitation"
        ],
        "caption_header": "Al_Quran✨ || 🕊️ سکونِ قلب کی ضمانت",
        "content_family": "Faith & Learning",
        "primary_theme": "sacred_geometry",
        "allowed_themes": ["sacred_geometry", "cinematic_documentary"],
        "recommended_production_mode": "Static Sacred-Geometry background + animated Arabic/translation text + Quran recitation audio (licensed) — not full AI video gen",
        "sample_reel_hook": "This verse changes how you see hardship…",
        "prompt_tone": (
            "Deeply emotional, spiritual, comforting, and soul-softening. "
            "Focus on healing broken hearts, trusting Allah's timing, overcoming anxiety, "
            "and the beauty of sincere Dua and Tahajjud."
        )
    },

    # ── 2. Quranic Education & Tafseer (Kalamullah Online Style) ──
    "quran_edu": {
        "id": "quran_edu",
        "name": "Kalamullah — Quranic Education & Tafseer",
        "reference_page": "https://www.facebook.com/kalamullahonline.edu",
        "category": "Islamic Education",
        "tagline": "Understand The Divine Word · کلامُ اللہ فہم و تدبر",
        "badge_text": "KALAMULLAH · ACADEMY 📖",
        "primary_color": (70, 200, 160),      # Emerald Mint
        "secondary_color": (255, 255, 255),   # Crisp White
        "accent_color": (255, 215, 80),       # Gold Root Accent
        "bg_theme": "desert_dunes",           # scholarly golden parchment
        "ambient_audio": "ambient_wind.mp3",
        "aspect_ratios": ["4:5", "9:16", "1:1"],
        "default_lang": "urdu",
        "hashtags": [
            "#Kalamullah", "#QuranTafseer", "#ArabicGrammar", "#WordByWordQuran",
            "#Tajweed", "#LearnQuran", "#QuranicArabic", "#IslamicKnowledge"
        ],
        "caption_header": "فہمِ قرآن || 📖 کلامُ اللہ اکیڈمی",
        "content_family": "Faith & Learning",
        "primary_theme": "sacred_geometry",
        "allowed_themes": ["sacred_geometry", "editorial_minimal"],
        "recommended_production_mode": "Talking-head / authentic tutor clips + word-by-word graphic text-card intercuts",
        "sample_reel_hook": "3 signs you need a Tajweed teacher",
        "prompt_tone": (
            "Educational, scholarly yet accessible, pedagogical, and enlightening. "
            "Break down Arabic root words, reveal linguistic gems, explain historical context (Sabab an-Nuzul), "
            "and provide 3 clear actionable life lessons from the verse."
        )
    },

    # ── 3. Scenic Tourism & Landscapes (Discover Pakistan TV Style) ──
    "travel_pakistan": {
        "id": "travel_pakistan",
        "name": "Discover Pakistan — Tourism & Heritage",
        "reference_page": "https://www.facebook.com/DiscoverPakistan.TV",
        "category": "Travel & Culture",
        "tagline": "Land of Majestic Peaks & Timeless Heritage",
        "badge_text": "DISCOVER PAKISTAN 🇵🇰",
        "primary_color": (34, 197, 94),       # Lush Northern Green
        "secondary_color": (255, 255, 255),   # Snow Peak White
        "accent_color": (234, 179, 8),        # Golden Sun
        "bg_theme": "clouds_timelapse",       # or green_grass / sunrise_dawn
        "ambient_audio": "ambient_wind.mp3",
        "aspect_ratios": ["9:16", "4:5", "1:1"],
        "default_lang": "english",
        "hashtags": [
            "#DiscoverPakistan", "#BeautifulPakistan", "#HunzaValley", "#Skardu",
            "#NorthernPakistan", "#TravelPakistan", "#Karakoram", "#PakistanZindabad"
        ],
        "caption_header": "Discover Pakistan 🇵🇰 || 📍 Spectacular Landscapes",
        "content_family": "Culture & Sport",
        "primary_theme": "cinematic_documentary",
        "allowed_themes": ["cinematic_documentary", "editorial_minimal"],
        "recommended_production_mode": "Real drone/phone B-roll + AI motion (Runway/Pika/Luma) only for transitions, not fabricated locations",
        "sample_reel_hook": "You won't believe this exists in Pakistan",
        "prompt_tone": (
            "Inspiring, adventurous, descriptive, and culturally proud. "
            "Highlight breathtaking geography (K2, Passu Cones, Deosai, Katpana Cold Desert, Margalla Hills), "
            "travel tips, historical forts, local hospitality, and pristine nature."
        )
    },

    # ── 4. Viral Relatable Youth & Desi Humor (MLGAA Fan Style) ──
    "viral_youth": {
        "id": "viral_youth",
        "name": "MLGAA Fan — Viral Relatable Youth & Pop Culture",
        "reference_page": "https://www.facebook.com/mlgaafan",
        "category": "Viral Entertainment",
        "tagline": "Desi Realities & Relatable Situations 😂",
        "badge_text": "DESI VIBES ⚡",
        "primary_color": (250, 204, 21),      # High-Voltage Yellow
        "secondary_color": (255, 255, 255),   # High-Contrast White
        "accent_color": (239, 68, 68),        # Punchy Red
        "bg_theme": "night_traffic",          # neon city vibes
        "ambient_audio": "ambient_drone_120s.mp3",
        "aspect_ratios": ["9:16", "4:5", "1:1"],
        "default_lang": "urdu",
        "hashtags": [
            "#DesiMemes", "#Relatable", "#PakistaniYouth", "#StudentLife",
            "#DesiHumor", "#PakistaniTweets", "#ViralReels", "#Fun"
        ],
        "caption_header": "ہر پاکستانی کا دکھ 😭 || 100% Relatable",
        "content_family": "Tech & Agency",
        "primary_theme": "flat_pop_meme",
        "allowed_themes": ["flat_pop_meme", "bold_sports_dynamic"],
        "recommended_production_mode": "Meme-style quick-cut edit, trending desi audio, flat-pop text stickers & reaction cards",
        "sample_reel_hook": "POV: when your squad finally wins",
        "prompt_tone": (
            "Witty, highly relatable, conversational, satirical, and punchy. "
            "Focus on desi student life, exam stress, parents vs rishta aunty, office deadlines, "
            "load shedding, chai love, and unspoken cultural observations."
        )
    },

    # ── 5. Cricket & Sports Hype (Pakistan Cricket Board Style) ──
    "sports_cricket": {
        "id": "sports_cricket",
        "name": "Pakistan Cricket — Sports & Match Highlights",
        "reference_page": "https://www.facebook.com/PakistanCricketBoard",
        "category": "Sports & Cricket",
        "tagline": "Passion, Pride & Unstoppable Yorkers 🏏",
        "badge_text": "PAKISTAN CRICKET 🏏",
        "primary_color": (16, 185, 129),      # PCB Emerald Green
        "secondary_color": (255, 255, 255),   # Jersey White
        "accent_color": (245, 158, 11),       # Trophy Gold
        "bg_theme": "stadium_floodlights",    # stadium floodlight arena & athletic lines
        "ambient_audio": "ambient_drone_120s.mp3",
        "aspect_ratios": ["9:16", "4:5", "1:1"],
        "default_lang": "english",
        "hashtags": [
            "#PakistanCricket", "#PCB", "#ShaheenAfridi", "#BabarAzam",
            "#PSL", "#CricketFever", "#GreenShirts", "#PakVsAll"
        ],
        "caption_header": "PAKISTAN CRICKET 🏏 || Match Hype & Records",
        "content_family": "Culture & Sport",
        "primary_theme": "bold_sports_dynamic",
        "allowed_themes": ["bold_sports_dynamic", "editorial_minimal"],
        "recommended_production_mode": "Real match footage/highlights only — AI limited to intro/outro graphics and kinetic stat cards",
        "sample_reel_hook": "Relive the moment that won us the match",
        "prompt_tone": (
            "Energetic, electrifying, authoritative, and patriotic. "
            "Focus on player records, thunderous yorkers, clutch sixes, PSL updates, "
            "match statistics, post-match analysis, and the unwavering passion of 240M fans."
        )
    },

    # ── 6. Tech News, Telecom & Policy (ProPakistani Style) ──
    "tech_news": {
        "id": "tech_news",
        "name": "ProPakistani — Tech, Telecom & Digital Economy",
        "reference_page": "https://www.facebook.com/ProPakistani",
        "category": "Technology & News",
        "tagline": "Leading Digital Pakistan & Telecom Updates",
        "badge_text": "TECH NEWS ⚡",
        "primary_color": (59, 130, 246),      # Tech Cobalt Blue
        "secondary_color": (255, 255, 255),   # Editorial White
        "accent_color": (16, 185, 129),       # Success Green
        "bg_theme": "tech_grid",              # editorial tech grid & cobalt spotlight
        "ambient_audio": "ambient_drone_120s.mp3",
        "aspect_ratios": ["4:5", "1:1", "9:16"],
        "default_lang": "english",
        "hashtags": [
            "#ProPakistani", "#TechNewsPK", "#Telecom", "#DigitalPakistan",
            "#Startups", "#Smartphones", "#PTA", "#SolarEnergy"
        ],
        "caption_header": "TECH UPDATE 📱 || ProPakistani Pulse",
        "content_family": "News & Business",
        "primary_theme": "editorial_minimal",
        "allowed_themes": ["editorial_minimal", "tech_gradient_glass"],
        "recommended_production_mode": "Text-driven news reel: AI-generated minimalist background + kinetic typography of real facts",
        "sample_reel_hook": "Here's what changed in Pakistan's telecom sector this week",
        "prompt_tone": (
            "Editorial, objective, breaking-news style, clear, and informative. "
            "Deliver fast facts, telecom updates, gadget price changes, PTA regulations, "
            "EV and solar policies, and digital innovation impacting everyday Pakistanis."
        )
    },

    # ── 7. Business, Finance & PSX (Business Bytes PK Style) ──
    "business_finance": {
        "id": "business_finance",
        "name": "Business Bytes — Finance, Economy & Wealth",
        "reference_page": "https://www.facebook.com/businessbytespk",
        "category": "Finance & Economy",
        "tagline": "Financial Literacy, PSX & Money Intelligence",
        "badge_text": "BUSINESS BYTES 📈",
        "primary_color": (34, 197, 94),       # Market Emerald Green
        "secondary_color": (255, 255, 255),   # Executive White
        "accent_color": (250, 204, 21),       # Gold Accent
        "bg_theme": "financial_slate",        # executive slate & market trend curve
        "ambient_audio": "ambient_drone_120s.mp3",
        "aspect_ratios": ["4:5", "1:1", "9:16"],
        "default_lang": "english",
        "hashtags": [
            "#BusinessBytes", "#PSX", "#EconomyPK", "#PersonalFinance",
            "#Investing", "#FreelancingWealth", "#StartupsPK", "#MoneyMindset"
        ],
        "caption_header": "BUSINESS PULSE 💼 || Financial Intelligence",
        "content_family": "News & Business",
        "primary_theme": "editorial_minimal",
        "allowed_themes": ["editorial_minimal", "tech_gradient_glass"],
        "recommended_production_mode": "Data-viz motion graphics (After Effects / Compositor template) with real verified figures",
        "sample_reel_hook": "3 numbers that explain this quarter",
        "prompt_tone": (
            "Analytical, insightful, wealth-oriented, and empowering. "
            "Cover PSX market movements, dollar & gold trends, inflation navigation, "
            "smart investing strategies for salaried youth, and Pakistani startup case studies."
        )
    },

    # ── 8. IT Agency English & Urdu (Web, AI & Software Agency) ──
    "it_agency": {
        "id": "it_agency",
        "name": "IT Agency — Web, Mobile & AI Solutions (En & Ur)",
        "reference_page": "https://www.facebook.com/profile.php?id=61553389594812",
        "category": "IT Services & AI",
        "tagline": "Transforming Ideas into Scalable Digital Products",
        "badge_text": "TECH AGENCY 🚀",
        "primary_color": (139, 92, 246),      # AI Violet Glow
        "secondary_color": (255, 255, 255),   # Modern SaaS White
        "accent_color": (6, 182, 212),        # Cyan Laser
        "bg_theme": "bento_mesh",             # modern Linear bento mesh with violet/cyan orbs
        "ambient_audio": "ambient_drone_120s.mp3",
        "aspect_ratios": ["4:5", "9:16", "1:1"],
        "default_lang": "bilingual",          # English headline + Urdu voiceover/text
        "hashtags": [
            "#WebDevelopment", "#AppDevelopment", "#AIAgency", "#SoftwareHouse",
            "#FreelanceAgency", "#CustomSoftware", "#TechServices", "#DigitalAgency"
        ],
        "caption_header": "DIGITAL INNOVATION 💻 || IT Agency Solutions",
        "content_family": "Tech & Agency",
        "primary_theme": "tech_gradient_glass",
        "allowed_themes": ["tech_gradient_glass", "editorial_minimal"],
        "recommended_production_mode": "Case-study script + Tech-Gradient animated template + voiceover (TTS or real bilingual talent)",
        "sample_reel_hook": "Here's how we cut a client's server cost by 40%",
        "prompt_tone": (
            "Professional, results-driven, modern, client-focused, and bilingual (English + Urdu). "
            "Showcase website & mobile app development, AI automations that cut business costs, "
            "SaaS software architectures, and client success transformations."
        )
    },

    # ── 9. High-Engagement Debate & Comment Trigger (Agree / Disagree) ──
    "debate_trigger": {
        "id": "debate_trigger",
        "name": "Public Perspective — Agree or Disagree",
        "reference_page": "https://www.facebook.com/groups/pakistanithoughts",
        "category": "Social Debate & Public Opinion",
        "tagline": "Unfiltered Thoughts & Public Opinion · آپ کا کیا خیال ہے؟",
        "badge_text": "AGREE OR DISAGREE? 💬",
        "primary_color": (239, 68, 68),       # Hot Red / Provocative
        "secondary_color": (255, 255, 255),   # High-Contrast White
        "accent_color": (14, 165, 233),       # Electric Cyan (Opposing Pole)
        "bg_theme": "tension_arena",          # high-tension split red/cyan ambient lighting
        "ambient_audio": "ambient_drone_120s.mp3",
        "aspect_ratios": ["4:5", "1:1", "9:16"],
        "default_lang": "bilingual",
        "hashtags": [
            "#AgreeOrDisagree", "#HotTake", "#PublicOpinion", "#PakistanDebate",
            "#DiscussionOfTheDay", "#YourThoughts", "#DesiThoughts"
        ],
        "caption_header": "AGREE OR DISAGREE? 💬 || Public Opinion Poll",
        "content_family": "News & Business",
        "primary_theme": "editorial_minimal",
        "allowed_themes": ["editorial_minimal", "bold_sports_dynamic", "tech_gradient_glass"],
        "recommended_production_mode": "Split-card video poll with countdown timer + dual audio soundbites prompting immediate comments",
        "sample_reel_hook": "Degree vs Skills in 2026: Settle this debate once and for all",
        "prompt_tone": (
            "Thought-provoking, polarizing yet respectful, debate-igniting, and conversation-starting. "
            "Frame high-stakes relatable dilemmas that compel readers to immediately comment their stance "
            "(e.g., Degree vs Skills in 2026, Remote Freelancing vs Stable 9-5 in Pakistan, Extravagant Weddings vs Simple Sunnah, "
            "Moving Abroad vs Staying with Parents, AI Replacing White-Collar Jobs, Living Joint Family vs Separate). "
            "Present clear, compelling arguments for both Option A and Option B so both sides feel eager to comment."
        )
    }
}

class NicheCatalog:
    """Manager for multi-niche profiles, visual aesthetics, and prompt templates."""

    @classmethod
    def get_all_niches(cls) -> List[Dict]:
        return list(NICHE_ROSTER.values())

    @classmethod
    def get_niche_ids(cls) -> List[str]:
        return list(NICHE_ROSTER.keys())

    @classmethod
    def resolve_niche(cls, identifier: Optional[str] = None) -> Dict:
        """Resolves niche by ID, name, or partial match. Defaults to 'quran_spiritual'."""
        if not identifier:
            return NICHE_ROSTER["quran_spiritual"]

        s = str(identifier).lower().strip()
        # Direct key match
        if s in NICHE_ROSTER:
            return NICHE_ROSTER[s]

        # Alias/Keyword resolution
        keyword_map = {
            "quran": "quran_spiritual",
            "spiritual": "quran_spiritual",
            "hearts": "quran_spiritual",
            "quranichearts": "quran_spiritual",
            "kalamullah": "quran_edu",
            "edu": "quran_edu",
            "tafseer": "quran_edu",
            "tajweed": "quran_edu",
            "travel": "travel_pakistan",
            "tourism": "travel_pakistan",
            "discover": "travel_pakistan",
            "discoverpakistan": "travel_pakistan",
            "youth": "viral_youth",
            "mlgaa": "viral_youth",
            "meme": "viral_youth",
            "desi": "viral_youth",
            "sports": "sports_cricket",
            "cricket": "sports_cricket",
            "pcb": "sports_cricket",
            "tech": "tech_news",
            "propakistani": "tech_news",
            "gadgets": "tech_news",
            "business": "business_finance",
            "finance": "business_finance",
            "psx": "business_finance",
            "businessbytes": "business_finance",
            "agency": "it_agency",
            "it": "it_agency",
            "software": "it_agency",
            "ai": "it_agency",
            "debate": "debate_trigger",
            "opinion": "debate_trigger",
            "agree": "debate_trigger",
            "disagree": "debate_trigger",
            "poll": "debate_trigger",
            "hottake": "debate_trigger",
        }
        for kw, target_id in keyword_map.items():
            if kw in s:
                return NICHE_ROSTER[target_id]

        logger.warning(f"Niche '{identifier}' not found. Defaulting to 'quran_spiritual'.")
        return NICHE_ROSTER["quran_spiritual"]

    @classmethod
    def get_content_families(cls) -> Dict[str, List[str]]:
        """Returns map of Content Families to niche IDs."""
        families: Dict[str, List[str]] = {}
        for niche_id, data in NICHE_ROSTER.items():
            fam = data.get("content_family", "General")
            families.setdefault(fam, []).append(niche_id)
        return families

    @classmethod
    def get_themes(cls) -> Dict[str, Any]:
        """Returns all 6 themes from MultiNicheThemeEngine."""
        from video_engine.theme_system import THEME_CATALOG
        return THEME_CATALOG

    @classmethod
    def build_image_prompt(
        cls,
        niche_id: str,
        theme_id: Optional[str] = None,
        subject: Optional[str] = None,
        palette_override: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generates compliant image prompt using the Theme System."""
        from video_engine.theme_system import MultiNicheThemeEngine
        resolved = cls.resolve_niche(niche_id)
        return MultiNicheThemeEngine.build_image_prompt(
            niche_id=resolved["id"],
            theme_id=theme_id,
            subject=subject,
            palette_override=palette_override,
            aspect_ratio=aspect_ratio,
        )

    @classmethod
    def build_reel_script(
        cls,
        niche_id: str,
        topic: Optional[str] = None,
        custom_hook: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Builds a 4-beat Universal Reel Script."""
        from video_engine.theme_system import MultiNicheThemeEngine
        resolved = cls.resolve_niche(niche_id)
        script = MultiNicheThemeEngine.build_reel_script(
            niche_id=resolved["id"],
            topic=topic,
            custom_hook=custom_hook,
        )
        return script.to_dict()

    @classmethod
    def build_ai_video_prompt(
        cls,
        theme_id: str,
        scene_description: str,
        palette: Optional[str] = None,
        camera_motion: str = "smooth cinematic camera drift and subtle forward push",
        aspect_ratio: str = "9:16 vertical",
    ) -> str:
        """Generates AI video prompt for Runway Gen-3, Pika, Luma."""
        from video_engine.theme_system import MultiNicheThemeEngine
        return MultiNicheThemeEngine.build_ai_video_prompt(
            theme_id=theme_id,
            scene_description=scene_description,
            palette=palette,
            camera_motion=camera_motion,
            aspect_ratio=aspect_ratio,
        )
