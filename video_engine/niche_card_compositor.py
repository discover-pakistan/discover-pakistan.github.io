"""
Niche Editorial Card & Infographic Compositor.
Creates viral 4:5 (1080x1350) and 1:1 (1080x1080) cards inspired by:
- Pakistan Cricket Board (PCB) Match Stat & Adrenaline Sports Cards
- ProPakistani Split-Deck News Cards
- Discover Pakistan Majestic Nature & Travel Dossiers
- Business Bytes Executive Financial Infographics
- Quranic Hearts Spiritual & Soul-Softening Calligraphy Cards
- Kalamullah Online Academic Tafseer & Linguistic Cards
- MLGAA Fan Viral Desi Youth & Tweet Cards
- IT Agency Modern B2B SaaS Bento Cards
"""

import os
import math
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

from video_engine.niche_background_engine import NicheBackgroundEngine

logger = logging.getLogger(__name__)

CARD_SIZE_4_5 = (1080, 1350)
CARD_SIZE_1_1 = (1080, 1080)


class NicheCardCompositor:
    def __init__(self, font_dir: Path, size: Tuple[int, int] = CARD_SIZE_4_5):
        self.font_dir = font_dir
        self.size = size
        self.width, self.height = size

        self.font_latin_bold = str(font_dir / "NotoSans-Bold.ttf")
        self.font_urdu_bold = str(font_dir / "NotoNastaliqUrdu-Bold.ttf")
        self.font_arabic_bold = str(font_dir / "Amiri-Bold.ttf")

    def _clean_text(self, text: str) -> str:
        """Strip emojis and non-renderable characters to prevent missing glyph box artifacts."""
        if not text:
            return ""
        import unicodedata
        clean_chars = []
        for ch in text:
            cat = unicodedata.category(ch)
            if cat in ('So', 'Cs', 'Cn'):
                continue
            clean_chars.append(ch)
        return " ".join("".join(clean_chars).split())

    def _detect_script(self, text: str) -> str:
        """Detect whether text is predominantly Urdu/Arabic (RTL) or Latin (LTR)."""
        if not text:
            return "latin"
        rtl_count = sum(1 for c in text if '\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F')
        return "rtl" if rtl_count > (len(text) * 0.25) else "latin"

    def _select_font(self, text: str, size: int) -> ImageFont.FreeTypeFont:
        script = self._detect_script(text)
        if script == "rtl":
            has_tashkeel = any(c in "\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652" for c in text)
            font_path = self.font_arabic_bold if has_tashkeel else self.font_urdu_bold
        else:
            font_path = self.font_latin_bold
        return ImageFont.truetype(font_path, size)

    def _wrap_text(self, draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """Wrap text into lines respecting word boundaries."""
        words = text.split()
        if not words:
            return []
        lines = []
        cur_line = []
        for word in words:
            test_line = " ".join(cur_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if (bbox[2] - bbox[0]) <= max_width:
                cur_line.append(word)
            else:
                if cur_line:
                    lines.append(" ".join(cur_line))
                    cur_line = [word]
                else:
                    lines.append(word)
                    cur_line = []
        if cur_line:
            lines.append(" ".join(cur_line))
        return lines

    def _draw_blurred_shadow(self, img: Image.Image, draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont,
                             xy: Tuple[int, int], fill=(0, 0, 0, 180), radius: int = 4,
                             offset: Tuple[int, int] = (2, 2), direction="ltr"):
        bbox = draw.textbbox((0, 0), text, font=font, direction=direction)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w <= 0 or h <= 0:
            return
        pad = radius * 2 + 8
        s_img = Image.new("RGBA", (w + pad, h + pad), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(s_img)
        s_draw.text((radius + 4 - bbox[0], radius + 4 - bbox[1]), text, font=font, fill=fill, direction=direction)
        s_img = s_img.filter(ImageFilter.GaussianBlur(radius=radius))
        paste_x = xy[0] + bbox[0] - (radius + 4) + offset[0]
        paste_y = xy[1] + bbox[1] - (radius + 4) + offset[1]
        img.paste(s_img, (int(paste_x), int(paste_y)), s_img)

    def _draw_glass_card(self, draw: ImageDraw.Draw, xy: Tuple[int, int, int, int], radius: int = 20,
                         fill=(15, 23, 42, 210), border_color=(255, 215, 80, 140), border_width: int = 2):
        x1, y1, x2, y2 = xy
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=border_color, width=border_width)

    def _resolve_hero_image(self, niche_id: str, content: Dict) -> Optional[Path]:
        """
        Locates an authentic real-world photograph matching the subject.
        Checks explicit content parameters first, then scans hero_subjects/ and backgrounds/images/.
        """
        for key in ("hero_image_path", "hero_image", "hero_path"):
            val = content.get(key)
            if val and Path(val).exists():
                return Path(val)

        search_corpus = " ".join([
            str(content.get("headline", "")),
            str(content.get("subdeck", "")),
            str(content.get("highlight", "")),
            str(content.get("category_tag", "")),
            str(content.get("badge", ""))
        ]).lower()

        hero_dir = Path(__file__).parent.parent / "assets" / "hero_subjects"
        bg_dir = Path(__file__).parent.parent / "assets" / "backgrounds" / "images"

        if niche_id == "sports_cricket":
            if "shaheen" in search_corpus or "afridi" in search_corpus:
                p = hero_dir / "shaheen_afridi.jpg"
                if p.exists(): return p
            if "babar" in search_corpus or "azam" in search_corpus:
                p = hero_dir / "babar_azam.jpg"
                if p.exists(): return p
            # Default cricket hero: Babar or Shaheen
            if (hero_dir / "babar_azam.jpg").exists():
                return hero_dir / "babar_azam.jpg"
            if (hero_dir / "shaheen_afridi.jpg").exists():
                return hero_dir / "shaheen_afridi.jpg"

        elif niche_id == "travel_pakistan":
            p = hero_dir / "hunza_valley.jpg"
            if p.exists(): return p

        elif niche_id in ("tech_news", "it_agency"):
            p = hero_dir / "propakistani_tech.jpg"
            if p.exists(): return p

        elif niche_id in ("quran_spiritual", "quran_edu"):
            if "kaaba" in search_corpus or "makkah" in search_corpus or "rain" in search_corpus:
                p = bg_dir / "kaaba_rain.jpg"
                if p.exists(): return p
            p = hero_dir / "quran_rehal.jpg"
            if p.exists(): return p

        return None

    def _get_base_canvas(self, niche_id: str) -> Tuple[Image.Image, ImageDraw.Draw]:
        """Synthesizes an authentic studio-grade graphic designer plate tailored to the niche."""
        card_img = NicheBackgroundEngine.generate_background(niche_id, size=self.size)
        draw = ImageDraw.Draw(card_img)
        return card_img, draw

    # ──────────────────────────────────────────────────────────────────────────
    # 1. SPORTS / CRICKET (Pakistan Cricket Board Style)
    # ──────────────────────────────────────────────────────────────────────────
    def _render_sports_card(self, niche: Dict, content: Dict, output_path: str) -> str:
        """
        Athletic adrenaline card: Real player action photograph with authentic PCB lower-third
        broadcast graphics, stadium floodlight vignette, PCB emerald & trophy gold ribbons,
        giant bold stat callout (4/18, 152 KPH), and match takeaways.
        """
        hero_path = self._resolve_hero_image("sports_cricket", content)
        margin = 55
        content_w = self.width - (2 * margin)

        if hero_path:
            # 1. Scale and center-crop hero image to canvas
            hero_img = Image.open(hero_path).convert("RGBA")
            hw, hh = hero_img.size
            scale = max(self.width / hw, self.height / hh)
            nw, nh = int(hw * scale), int(hh * scale)
            hero_img = hero_img.resize((nw, nh), Image.Resampling.LANCZOS)
            cx = (nw - self.width) // 2
            card_img = hero_img.crop((cx, 0, cx + self.width, self.height))

            # 2. Multi-stop broadcast gradient mask: Top vignette + deep bottom lower third
            gradient = Image.new("RGBA", self.size, (0, 0, 0, 0))
            g_draw = ImageDraw.Draw(gradient)

            # Top vignette (y=0..220) to make badges stand out crisply
            for y in range(220):
                a = int(140 * (1.0 - y / 220.0))
                g_draw.line([(0, y), (self.width, y)], fill=(0, 10, 5, a))

            # Bottom deep sports gradient starting from y=580 to bottom
            for y in range(580, self.height):
                prog = (y - 580) / float(self.height - 580)
                a = int(245 * (prog ** 1.3))
                g_draw.line([(0, y), (self.width, y)], fill=(2, 14, 8, a))

            card_img = Image.alpha_composite(card_img, gradient)
            draw = ImageDraw.Draw(card_img)

            # Top Header Ribbons (Slanted dual accent)
            draw.rectangle([0, 0, self.width, 12], fill=(16, 185, 129))     # PCB Green
            draw.polygon([(0, 12), (320, 12), (280, 24), (0, 24)], fill=(245, 158, 11)) # Trophy Gold

            # Top Badges
            b_font = ImageFont.truetype(self.font_latin_bold, 22)
            badge_text = self._clean_text(content.get("badge", "PAKISTAN CRICKET 🏏")).upper()
            draw.rounded_rectangle([margin, 60, margin + 270, 102], radius=8, fill=(10, 35, 22, 240), outline=(16, 185, 129), width=2)
            draw.text((margin + 20, 68), badge_text, font=b_font, fill=(245, 158, 11))

            cat_tag = self._clean_text(content.get("category_tag", "MATCH STAT")).upper()
            c_bbox = draw.textbbox((0, 0), cat_tag, font=b_font)
            cw = c_bbox[2] - c_bbox[0]
            draw.rounded_rectangle([self.width - margin - cw - 30, 60, self.width - margin, 102], radius=8, fill=(16, 185, 129, 230))
            draw.text((self.width - margin - cw - 15, 68), cat_tag, font=b_font, fill=(255, 255, 255))

            # Lower Third Headline (Over dark gradient at y=685 so player's face/action is 100% visible)
            headline = self._clean_text(content.get("headline", "RECORD-BREAKING SPELL STUNS OPPOSITION")).upper()
            h_font = ImageFont.truetype(self.font_latin_bold, 44 if len(headline) < 55 else 38)
            h_lines = self._wrap_text(draw, headline, h_font, content_w)
            h_y = 685
            for line in h_lines[:2]:
                self._draw_blurred_shadow(card_img, draw, line, h_font, (margin, h_y), radius=6, fill=(0, 0, 0, 240))
                draw.text((margin, h_y), line, font=h_font, fill=(255, 255, 255))
                h_y += int(h_font.size * 1.22)

            # Central Stadium Stat Box
            stat_top = h_y + 15
            stat_h = 190
            self._draw_glass_card(draw, (margin, stat_top, self.width - margin, stat_top + stat_h),
                                  radius=16, fill=(8, 28, 20, 240), border_color=(245, 158, 11, 230), border_width=2)
            draw.rounded_rectangle([margin, stat_top, margin + 10, stat_top + stat_h], radius=4, fill=(245, 158, 11))

            stat_num = self._clean_text(content.get("stat_number", "4 / 18"))
            stat_lbl = self._clean_text(content.get("stat_label", "MATCH HIGHLIGHT")).upper()
            num_font = ImageFont.truetype(self.font_latin_bold, 74 if len(stat_num) < 8 else 60)
            lbl_font = ImageFont.truetype(self.font_latin_bold, 18)

            draw.text((margin + 36, stat_top + 22), stat_lbl, font=lbl_font, fill=(16, 185, 129))
            self._draw_blurred_shadow(card_img, draw, stat_num, num_font, (margin + 36, stat_top + 50), radius=5, fill=(0, 0, 0, 220))
            draw.text((margin + 36, stat_top + 50), stat_num, font=num_font, fill=(245, 158, 11))

            split_x = margin + 340
            draw.line([split_x, stat_top + 25, split_x, stat_top + stat_h - 25], fill=(255, 255, 255, 30), width=1)

            highlight = self._clean_text(content.get("highlight", "Pace, precision, and relentless aggression on display."))
            hl_font = ImageFont.truetype(self.font_latin_bold, 25)
            hl_lines = self._wrap_text(draw, highlight, hl_font, (self.width - margin) - split_x - 30)
            text_y = stat_top + 35
            for hline in hl_lines[:3]:
                draw.text((split_x + 25, text_y), hline, font=hl_font, fill=(241, 245, 249))
                text_y += 34

            # Match Key Points
            bullets_y = stat_top + stat_h + 24
            b_font = ImageFont.truetype(self.font_latin_bold, 24)
            for pt in content.get("bullet_points", [])[:2]:
                clean_pt = self._clean_text(pt)
                pt_lines = self._wrap_text(draw, clean_pt, b_font, content_w - 60)
                draw.polygon([(margin + 12, bullets_y + 8), (margin + 20, bullets_y + 16),
                              (margin + 12, bullets_y + 24), (margin + 4, bullets_y + 16)], fill=(16, 185, 129))
                for pline in pt_lines[:2]:
                    draw.text((margin + 38, bullets_y + 2), pline, font=b_font, fill=(226, 232, 240))
                    bullets_y += 32
                bullets_y += 10

            # Footer CTA
            footer_y = self.height - 85
            draw.line([margin, footer_y - 20, self.width - margin, footer_y - 20], fill=(255, 255, 255, 40), width=1)
            cta_text = self._clean_text(content.get("call_to_action", "SHARE YOUR MATCH REACTION · TAG A CRICKET FAN 🏏")).upper()
            cta_font = ImageFont.truetype(self.font_latin_bold, 21)
            cw = draw.textbbox((0, 0), cta_text, font=cta_font)[2] - draw.textbbox((0, 0), cta_text, font=cta_font)[0]
            draw.text(((self.width - cw) // 2, footer_y), cta_text, font=cta_font, fill=(245, 158, 11))

            return self._save_card(card_img, output_path)

        # Fallback if no hero player image
        card_img, draw = self._get_base_canvas("sports_cricket")
        margin = 55
        content_w = self.width - (2 * margin)

        # Athletic Top Header Ribbons (Slanted dual accent)
        draw.rectangle([0, 0, self.width, 12], fill=(16, 185, 129))     # PCB Green
        draw.polygon([(0, 12), (320, 12), (280, 24), (0, 24)], fill=(245, 158, 11)) # Trophy Gold

        # Top Badge & Category Tag
        badge_text = self._clean_text(content.get("badge", "PAKISTAN CRICKET 🏏")).upper()
        cat_tag = self._clean_text(content.get("category_tag", "MATCH STAT")).upper()

        b_font = ImageFont.truetype(self.font_latin_bold, 22)
        b_bbox = draw.textbbox((0, 0), badge_text, font=b_font)
        bw = b_bbox[2] - b_bbox[0]
        bh = b_bbox[3] - b_bbox[1]
        badge_y = 60

        draw.rounded_rectangle([margin, badge_y, margin + bw + 40, badge_y + bh + 20], radius=8,
                               fill=(10, 35, 22, 240), outline=(16, 185, 129), width=2)
        draw.text((margin + 20, badge_y + 8), badge_text, font=b_font, fill=(245, 158, 11))

        # Right category pill
        c_bbox = draw.textbbox((0, 0), cat_tag, font=b_font)
        cw = c_bbox[2] - c_bbox[0]
        draw.text((self.width - margin - cw, badge_y + 8), cat_tag, font=b_font, fill=(255, 255, 255, 220))

        # Hero Headline (Uppercase, heavy athletic impact)
        headline = self._clean_text(content.get("headline", "RECORD-BREAKING SPELL STUNS THE OPPOSITION")).upper()
        h_font = ImageFont.truetype(self.font_latin_bold, 50 if len(headline) < 55 else 42)
        h_lines = self._wrap_text(draw, headline, h_font, content_w)
        h_y = badge_y + bh + 50
        for line in h_lines[:3]:
            self._draw_blurred_shadow(card_img, draw, line, h_font, (margin, h_y), radius=5, fill=(0, 0, 0, 240))
            draw.text((margin, h_y), line, font=h_font, fill=(255, 255, 255))
            h_y += int(h_font.size * 1.22)

        # Subdeck (Context line in silver)
        subdeck = self._clean_text(content.get("subdeck", ""))
        if subdeck:
            s_font = ImageFont.truetype(self.font_latin_bold, 26)
            s_lines = self._wrap_text(draw, subdeck, s_font, content_w)
            for s_line in s_lines[:2]:
                draw.text((margin, h_y + 4), s_line, font=s_font, fill=(203, 213, 225))
                h_y += 34

        # Central Stadium Stat Box
        stat_top = h_y + 25
        stat_h = 220
        self._draw_glass_card(draw, (margin, stat_top, self.width - margin, stat_top + stat_h),
                              radius=18, fill=(8, 28, 20, 235), border_color=(245, 158, 11, 230), border_width=2)
        draw.rounded_rectangle([margin, stat_top, margin + 10, stat_top + stat_h], radius=4, fill=(245, 158, 11))

        stat_num = self._clean_text(content.get("stat_number", "4 / 18"))
        stat_lbl = self._clean_text(content.get("stat_label", "MATCH HIGHLIGHT")).upper()
        num_font = ImageFont.truetype(self.font_latin_bold, 78 if len(stat_num) < 8 else 62)
        lbl_font = ImageFont.truetype(self.font_latin_bold, 20)

        draw.text((margin + 36, stat_top + 28), stat_lbl, font=lbl_font, fill=(16, 185, 129))
        self._draw_blurred_shadow(card_img, draw, stat_num, num_font, (margin + 36, stat_top + 58), radius=6, fill=(0, 0, 0, 220))
        draw.text((margin + 36, stat_top + 58), stat_num, font=num_font, fill=(245, 158, 11))

        split_x = margin + 360
        draw.line([split_x, stat_top + 30, split_x, stat_top + stat_h - 30], fill=(255, 255, 255, 40), width=2)

        highlight = self._clean_text(content.get("highlight", "Pace, precision, and relentless aggression on display."))
        hl_font = ImageFont.truetype(self.font_latin_bold, 27)
        hl_lines = self._wrap_text(draw, highlight, hl_font, (self.width - margin) - split_x - 40)
        hl_y = stat_top + 45
        for hl in hl_lines[:3]:
            draw.text((split_x + 30, hl_y), hl, font=hl_font, fill=(241, 245, 249))
            hl_y += 36

        # Match Key Points
        bullets_y = stat_top + stat_h + 38
        b_font = ImageFont.truetype(self.font_latin_bold, 25)
        for pt in content.get("bullet_points", [])[:3]:
            clean_pt = self._clean_text(pt)
            pt_lines = self._wrap_text(draw, clean_pt, b_font, content_w - 60)
            draw.polygon([(margin + 12, bullets_y + 8), (margin + 22, bullets_y + 18),
                          (margin + 12, bullets_y + 28), (margin + 2, bullets_y + 18)], fill=(16, 185, 129))
            for pline in pt_lines[:2]:
                draw.text((margin + 42, bullets_y + 2), pline, font=b_font, fill=(226, 232, 240))
                bullets_y += 34
            bullets_y += 14

        footer_y = self.height - 90
        draw.line([margin, footer_y - 20, self.width - margin, footer_y - 20], fill=(255, 255, 255, 40), width=1)
        cta_text = self._clean_text(content.get("call_to_action", "SHARE YOUR MATCH REACTION · TAG A CRICKET FAN 🏏")).upper()
        cta_font = ImageFont.truetype(self.font_latin_bold, 22)
        cw = draw.textbbox((0, 0), cta_text, font=cta_font)[2] - draw.textbbox((0, 0), cta_text, font=cta_font)[0]
        draw.text(((self.width - cw) // 2, footer_y), cta_text, font=cta_font, fill=(245, 158, 11))

        return self._save_card(card_img, output_path)

    # ──────────────────────────────────────────────────────────────────────────
    # 2. TECH NEWS (ProPakistani Split-Deck Style)
    # ──────────────────────────────────────────────────────────────────────────
    def _render_tech_news_card(self, niche: Dict, content: Dict, output_path: str) -> str:
        """
        Split-Deck Editorial News Layout:
        Top 38% has the clean cinematic visual backdrop fading downward.
        Bottom 62% is a solid high-contrast dark-mode editorial card (#0B0F19).
        Bold Swiss headline, silver subdeck, cobalt pill, and structured takeaway cards.
        """
        # Base tech plate with dot-matrix grid and cobalt glow
        card_img = NicheBackgroundEngine.generate_background("tech_news", size=self.size)
        split_y = int(self.height * 0.40)

        hero_path = self._resolve_hero_image("tech_news", content)
        if hero_path:
            hero_img = Image.open(hero_path).convert("RGBA")
            hw, hh = hero_img.size
            scale = max(self.width / hw, (split_y + 80) / hh)
            nw, nh = int(hw * scale), int(hh * scale)
            hero_img = hero_img.resize((nw, nh), Image.Resampling.LANCZOS)
            cx = (nw - self.width) // 2
            top_part = hero_img.crop((cx, 0, cx + self.width, split_y + 80))
            card_img.paste(top_part, (0, 0))
            gradient_h = 130
            for y in range(gradient_h):
                prog = y / float(gradient_h)
                a = int(255 * (prog ** 1.3))
                ov = Image.new("RGBA", (self.width, 1), (11, 15, 25, a))
                card_img.paste(ov, (0, split_y - 50 + y), ov)
        else:
            video_dir = Path(__file__).parent.parent / "assets" / "backgrounds" / "videos"
            city_file = video_dir / "islamabad_roads.mp4"
            if city_file.exists():
                from video_engine.islamic_backgrounds import VideoBackgroundProvider
                provider = VideoBackgroundProvider(str(city_file), size=self.size, dimming_alpha=0.45)
                frame_arr = provider.get_frame(0.0)
                base_img = Image.fromarray(frame_arr).convert("RGBA")
                provider.close()
                card_img.paste(base_img.crop((0, 0, self.width, split_y + 80)), (0, 0))
                gradient_h = 120
                for y in range(gradient_h):
                    prog = y / float(gradient_h)
                    a = int(255 * prog)
                    ov = Image.new("RGBA", (self.width, 1), (11, 15, 25, a))
                    card_img.paste(ov, (0, split_y - 40 + y), ov)

        draw = ImageDraw.Draw(card_img)
        margin = 55
        content_w = self.width - (2 * margin)

        # Top Bar: Cobalt Blue Accent
        draw.rectangle([0, 0, self.width, 8], fill=(59, 130, 246))

        # Top Brand & Category Badge over visual
        brand_name = "PROPAKISTANI"
        cat_tag = self._clean_text(content.get("category_tag", "TECH NEWS")).upper()
        badge_font = ImageFont.truetype(self.font_latin_bold, 20)

        # Brand pill on top left
        draw.rounded_rectangle([margin, 50, margin + 175, 88], radius=6, fill=(15, 23, 42, 230), outline=(59, 130, 246), width=2)
        draw.text((margin + 18, 58), brand_name, font=badge_font, fill=(255, 255, 255))

        # Category tag on right
        draw.rounded_rectangle([self.width - margin - 160, 50, self.width - margin, 88], radius=6, fill=(239, 68, 68), outline=None)
        cw = draw.textbbox((0, 0), cat_tag, font=badge_font)[2] - draw.textbbox((0, 0), cat_tag, font=badge_font)[0]
        draw.text((self.width - margin - 80 - (cw // 2), 58), cat_tag, font=badge_font, fill=(255, 255, 255))

        # Editorial Content Section (Begins below split_y)
        content_top = split_y + 20

        # Headline
        headline = self._clean_text(content.get("headline", "Digital Pakistan: Groundbreaking Telecommunications Expansion"))
        head_font = ImageFont.truetype(self.font_latin_bold, 48 if len(headline) < 65 else 40)
        h_lines = self._wrap_text(draw, headline, head_font, content_w)
        h_y = content_top
        for line in h_lines[:3]:
            self._draw_blurred_shadow(card_img, draw, line, head_font, (margin, h_y), radius=3, fill=(0, 0, 0, 180))
            draw.text((margin, h_y), line, font=head_font, fill=(255, 255, 255))
            h_y += int(head_font.size * 1.25)

        # Subdeck (1-line context in soft silver)
        subdeck = self._clean_text(content.get("subdeck", ""))
        if subdeck:
            s_font = ImageFont.truetype(self.font_latin_bold, 26)
            s_lines = self._wrap_text(draw, subdeck, s_font, content_w)
            for s_line in s_lines[:2]:
                draw.text((margin, h_y + 6), s_line, font=s_font, fill=(148, 163, 184))
                h_y += 34

        # Divider with cobalt dot
        div_y = h_y + 22
        draw.line([margin, div_y, self.width - margin, div_y], fill=(255, 255, 255, 30), width=1)
        draw.rectangle([margin, div_y - 1, margin + 90, div_y + 2], fill=(59, 130, 246))

        # Stat / Highlight Pill Card
        stat_num = self._clean_text(content.get("stat_number", ""))
        stat_lbl = self._clean_text(content.get("stat_label", "KEY METRIC")).upper()
        highlight = self._clean_text(content.get("highlight", ""))

        card_y = div_y + 26
        card_h = 160
        self._draw_glass_card(draw, (margin, card_y, self.width - margin, card_y + card_h),
                              radius=14, fill=(18, 26, 44, 240), border_color=(59, 130, 246, 180), border_width=2)
        # Left blue stripe
        draw.rounded_rectangle([margin, card_y, margin + 8, card_y + card_h], radius=4, fill=(59, 130, 246))

        if stat_num:
            num_font = ImageFont.truetype(self.font_latin_bold, 54)
            lbl_font = ImageFont.truetype(self.font_latin_bold, 18)
            draw.text((margin + 28, card_y + 22), stat_lbl, font=lbl_font, fill=(59, 130, 246))
            draw.text((margin + 28, card_y + 50), stat_num, font=num_font, fill=(255, 255, 255))
            
            # Right text in pill
            hl_font = ImageFont.truetype(self.font_latin_bold, 25)
            split_x = margin + 320
            draw.line([split_x, card_y + 20, split_x, card_y + card_h - 20], fill=(255, 255, 255, 30), width=1)
            hl_lines = self._wrap_text(draw, highlight, hl_font, (self.width - margin) - split_x - 30)
            text_y = card_y + 35
            for hline in hl_lines[:3]:
                draw.text((split_x + 25, text_y), hline, font=hl_font, fill=(226, 232, 240))
                text_y += 34
        else:
            hl_font = ImageFont.truetype(self.font_latin_bold, 28)
            hl_lines = self._wrap_text(draw, highlight, hl_font, content_w - 60)
            text_y = card_y + 35
            for hline in hl_lines[:3]:
                draw.text((margin + 30, text_y), hline, font=hl_font, fill=(226, 232, 240))
                text_y += 36

        # Key Takeaway Bullets
        bullets_y = card_y + card_h + 35
        b_font = ImageFont.truetype(self.font_latin_bold, 25)
        for pt in content.get("bullet_points", [])[:3]:
            clean_pt = self._clean_text(pt)
            pt_lines = self._wrap_text(draw, clean_pt, b_font, content_w - 60)
            # Arrow / chevron icon
            draw.polygon([(margin + 10, bullets_y + 6), (margin + 20, bullets_y + 14),
                          (margin + 10, bullets_y + 22)], fill=(59, 130, 246))
            for pline in pt_lines[:2]:
                draw.text((margin + 36, bullets_y), pline, font=b_font, fill=(203, 213, 225))
                bullets_y += 32
            bullets_y += 12

        # Footer CTA
        footer_y = self.height - 90
        draw.line([margin, footer_y - 20, self.width - margin, footer_y - 20], fill=(255, 255, 255, 30), width=1)
        cta_text = self._clean_text(content.get("call_to_action", "SAVE THIS UPDATE · SHARE WITH A TECH ENTHUSIAST")).upper()
        cta_font = ImageFont.truetype(self.font_latin_bold, 21)
        cw = draw.textbbox((0, 0), cta_text, font=cta_font)[2] - draw.textbbox((0, 0), cta_text, font=cta_font)[0]
        draw.text(((self.width - cw) // 2, footer_y), cta_text, font=cta_font, fill=(59, 130, 246))

        return self._save_card(card_img, output_path)

    # ──────────────────────────────────────────────────────────────────────────
    # 3. SCENIC TOURISM (Discover Pakistan & The North Style)
    # ──────────────────────────────────────────────────────────────────────────
    def _render_travel_card(self, niche: Dict, content: Dict, output_path: str) -> str:
        """
        Cinematic Panoramic Nature Layout:
        85%+ of canvas lets the breathtaking landscape shine!
        Minimalist frosted glass Travel Dossier pill at the bottom with Location, Altitude, and Quote.
        """
        hero_path = self._resolve_hero_image("travel_pakistan", content)
        margin = 55
        content_w = self.width - (2 * margin)

        if hero_path:
            hero_img = Image.open(hero_path).convert("RGBA")
            hw, hh = hero_img.size
            scale = max(self.width / hw, self.height / hh)
            nw, nh = int(hw * scale), int(hh * scale)
            hero_img = hero_img.resize((nw, nh), Image.Resampling.LANCZOS)
            cx = (nw - self.width) // 2
            card_img = hero_img.crop((cx, 0, cx + self.width, self.height))

            gradient = Image.new("RGBA", self.size, (0, 0, 0, 0))
            g_draw = ImageDraw.Draw(gradient)
            for y in range(320):
                a = int(150 * (1.0 - y / 320.0))
                g_draw.line([(0, y), (self.width, y)], fill=(5, 12, 20, a))
            for y in range(750, self.height):
                prog = (y - 750) / float(self.height - 750)
                a = int(220 * (prog ** 1.2))
                g_draw.line([(0, y), (self.width, y)], fill=(8, 14, 22, a))

            card_img = Image.alpha_composite(card_img, gradient)
            draw = ImageDraw.Draw(card_img)
        else:
            card_img, draw = self._get_base_canvas("travel_pakistan")

        # Top Frosted Pill: DISCOVER PAKISTAN 🇵🇰
        badge_text = self._clean_text(content.get("badge", "DISCOVER PAKISTAN 🇵🇰")).upper()
        b_font = ImageFont.truetype(self.font_latin_bold, 22)
        b_bbox = draw.textbbox((0, 0), badge_text, font=b_font)
        bw = b_bbox[2] - b_bbox[0]
        badge_y = 65

        draw.rounded_rectangle([margin, badge_y, margin + bw + 40, badge_y + 44], radius=22,
                               fill=(15, 23, 42, 190), outline=(255, 255, 255, 180), width=1)
        draw.text((margin + 20, badge_y + 8), badge_text, font=b_font, fill=(255, 255, 255))

        # Top Right Tag: "EXPLORE THE NORTH"
        region_tag = "EXPLORE THE NORTH"
        draw.text((self.width - margin - 220, badge_y + 10), region_tag, font=b_font, fill=(234, 179, 8))

        # Majestic Location Title (Centered or Left, Clean & Huge)
        headline = self._clean_text(content.get("headline", "Passu Cones · The Majestic Cathedral Peaks")).upper()
        h_font = ImageFont.truetype(self.font_latin_bold, 54 if len(headline) < 50 else 44)
        h_lines = self._wrap_text(draw, headline, h_font, content_w)
        h_y = 150
        for line in h_lines[:2]:
            self._draw_blurred_shadow(card_img, draw, line, h_font, (margin, h_y), radius=6, fill=(0, 0, 0, 240))
            draw.text((margin, h_y), line, font=h_font, fill=(255, 255, 255))
            h_y += int(h_font.size * 1.25)

        # Subdeck / Wonder quote
        subdeck = self._clean_text(content.get("subdeck", "Where jagged granite spires meet the roof of the world."))
        if subdeck:
            s_font = ImageFont.truetype(self.font_latin_bold, 28)
            s_lines = self._wrap_text(draw, subdeck, s_font, content_w)
            for s_line in s_lines[:2]:
                self._draw_blurred_shadow(card_img, draw, s_line, s_font, (margin, h_y), radius=4, fill=(0, 0, 0, 220))
                draw.text((margin, h_y), s_line, font=s_font, fill=(226, 232, 240))
                h_y += 36

        # ── Bottom Floating Travel Dossier Pill ──
        pill_y = self.height - 460
        pill_h = 320
        self._draw_glass_card(draw, (margin, pill_y, self.width - margin, pill_y + pill_h),
                              radius=24, fill=(10, 20, 30, 220), border_color=(255, 255, 255, 120), border_width=1)

        # Stat / Altitude Pill on Left
        stat_num = self._clean_text(content.get("stat_number", "2,438m"))
        stat_lbl = self._clean_text(content.get("stat_label", "ELEVATION")).upper()
        draw.rounded_rectangle([margin + 24, pill_y + 24, margin + 270, pill_y + 115], radius=14,
                               fill=(20, 35, 50, 230), outline=(34, 197, 94), width=2)
        lbl_font = ImageFont.truetype(self.font_latin_bold, 18)
        num_font = ImageFont.truetype(self.font_latin_bold, 44)
        draw.text((margin + 44, pill_y + 34), stat_lbl, font=lbl_font, fill=(34, 197, 94))
        draw.text((margin + 44, pill_y + 58), stat_num, font=num_font, fill=(255, 255, 255))

        # Travel Highlight Quote on Right
        highlight = self._clean_text(content.get("highlight", "One of the most dramatic landscapes on Earth."))
        hl_font = ImageFont.truetype(self.font_latin_bold, 26)
        hl_lines = self._wrap_text(draw, highlight, hl_font, content_w - 320)
        hl_y = pill_y + 36
        for hl in hl_lines[:2]:
            draw.text((margin + 295, hl_y), hl, font=hl_font, fill=(241, 245, 249))
            hl_y += 34

        # 2 Traveler Fact Bullets
        bullets_y = pill_y + 140
        b_font = ImageFont.truetype(self.font_latin_bold, 24)
        for pt in content.get("bullet_points", [])[:2]:
            clean_pt = self._clean_text(pt)
            pt_lines = self._wrap_text(draw, clean_pt, b_font, content_w - 70)
            # Emerald diamond marker
            draw.polygon([(margin + 30, bullets_y + 6), (margin + 38, bullets_y + 14),
                          (margin + 30, bullets_y + 22), (margin + 22, bullets_y + 14)], fill=(34, 197, 94))
            for pline in pt_lines[:2]:
                draw.text((margin + 52, bullets_y), pline, font=b_font, fill=(203, 213, 225))
                bullets_y += 32
            bullets_y += 8

        # Footer CTA
        footer_y = self.height - 85
        cta_text = self._clean_text(content.get("call_to_action", "TAG SOMEONE YOU'D TRAVEL HERE WITH · SAVE FOR YOUR ITINERARY 🏔️")).upper()
        cta_font = ImageFont.truetype(self.font_latin_bold, 20)
        cw = draw.textbbox((0, 0), cta_text, font=cta_font)[2] - draw.textbbox((0, 0), cta_text, font=cta_font)[0]
        draw.text(((self.width - cw) // 2, footer_y), cta_text, font=cta_font, fill=(234, 179, 8))

        return self._save_card(card_img, output_path)

    # ──────────────────────────────────────────────────────────────────────────
    # 4. BUSINESS & FINANCE (Business Bytes PK Style)
    # ──────────────────────────────────────────────────────────────────────────
    def _render_business_card(self, niche: Dict, content: Dict, output_path: str) -> str:
        """
        Executive Bloomberg / Financial Times Infographic Card:
        Obsidian canvas, emerald market indicators, huge stat metric box (+1,450 PTS / PKR 280),
        sharp executive headline, and concise market takeaways.
        """
        card_img, draw = self._get_base_canvas("business_finance")
        margin = 55
        content_w = self.width - (2 * margin)

        # Executive Dual Trim (Emerald & Gold)
        draw.rectangle([0, 0, self.width, 8], fill=(34, 197, 94))
        draw.rectangle([0, 8, int(self.width * 0.4), 14], fill=(250, 204, 21))

        # Top Header: BUSINESS BYTES 📈 + Market Category
        badge_text = self._clean_text(content.get("badge", "BUSINESS BYTES 📈")).upper()
        cat_tag = self._clean_text(content.get("category_tag", "FINANCIAL INTELLIGENCE")).upper()
        b_font = ImageFont.truetype(self.font_latin_bold, 22)

        draw.rounded_rectangle([margin, 60, margin + 260, 102], radius=8, fill=(15, 28, 20, 240), outline=(34, 197, 94), width=2)
        draw.text((margin + 20, 68), badge_text, font=b_font, fill=(34, 197, 94))

        cw = draw.textbbox((0, 0), cat_tag, font=b_font)[2] - draw.textbbox((0, 0), cat_tag, font=b_font)[0]
        draw.text((self.width - margin - cw, 70), cat_tag, font=b_font, fill=(250, 204, 21))

        # Hero Headline
        headline = self._clean_text(content.get("headline", "PSX Crosses Historic Benchmark as Foreign Inflows Surge"))
        head_font = ImageFont.truetype(self.font_latin_bold, 48 if len(headline) < 60 else 42)
        h_lines = self._wrap_text(draw, headline, head_font, content_w)
        h_y = 135
        for line in h_lines[:3]:
            self._draw_blurred_shadow(card_img, draw, line, head_font, (margin, h_y), radius=4, fill=(0, 0, 0, 200))
            draw.text((margin, h_y), line, font=head_font, fill=(255, 255, 255))
            h_y += int(head_font.size * 1.25)

        # Subdeck
        subdeck = self._clean_text(content.get("subdeck", ""))
        if subdeck:
            s_font = ImageFont.truetype(self.font_latin_bold, 26)
            s_lines = self._wrap_text(draw, subdeck, s_font, content_w)
            for s_line in s_lines[:2]:
                draw.text((margin, h_y + 4), s_line, font=s_font, fill=(148, 163, 184))
                h_y += 34

        # ── Central Financial Stat Box ──
        stat_top = h_y + 25
        stat_h = 210
        self._draw_glass_card(draw, (margin, stat_top, self.width - margin, stat_top + stat_h),
                              radius=18, fill=(10, 24, 18, 245), border_color=(34, 197, 94, 220), border_width=2)
        # Left emerald bar
        draw.rounded_rectangle([margin, stat_top, margin + 10, stat_top + stat_h], radius=4, fill=(34, 197, 94))

        stat_num = self._clean_text(content.get("stat_number", "+1,450 PTS"))
        stat_lbl = self._clean_text(content.get("stat_label", "MARKET BENCHMARK")).upper()
        num_font = ImageFont.truetype(self.font_latin_bold, 74 if len(stat_num) < 10 else 60)
        lbl_font = ImageFont.truetype(self.font_latin_bold, 20)

        draw.text((margin + 35, stat_top + 26), stat_lbl, font=lbl_font, fill=(250, 204, 21))
        self._draw_blurred_shadow(card_img, draw, stat_num, num_font, (margin + 35, stat_top + 56), radius=5, fill=(0, 0, 0, 200))
        draw.text((margin + 35, stat_top + 56), stat_num, font=num_font, fill=(34, 197, 94))

        # Vertical divider
        split_x = margin + 380
        draw.line([split_x, stat_top + 25, split_x, stat_top + stat_h - 25], fill=(255, 255, 255, 30), width=1)

        # Highlight Takeaway
        highlight = self._clean_text(content.get("highlight", "Sustained liquidity and macroeconomic stabilization boost sentiment."))
        hl_font = ImageFont.truetype(self.font_latin_bold, 26)
        hl_lines = self._wrap_text(draw, highlight, hl_font, (self.width - margin) - split_x - 35)
        hl_y = stat_top + 40
        for hl in hl_lines[:3]:
            draw.text((split_x + 30, hl_y), hl, font=hl_font, fill=(226, 232, 240))
            hl_y += 36

        # Market Drivers & Bullets
        bullets_y = stat_top + stat_h + 38
        b_font = ImageFont.truetype(self.font_latin_bold, 25)
        for pt in content.get("bullet_points", [])[:3]:
            clean_pt = self._clean_text(pt)
            pt_lines = self._wrap_text(draw, clean_pt, b_font, content_w - 60)
            # Market trend indicator dot
            draw.ellipse([margin + 10, bullets_y + 10, margin + 22, bullets_y + 22], fill=(34, 197, 94))
            for pline in pt_lines[:2]:
                draw.text((margin + 40, bullets_y + 2), pline, font=b_font, fill=(203, 213, 225))
                bullets_y += 34
            bullets_y += 12

        # Footer CTA
        footer_y = self.height - 90
        draw.line([margin, footer_y - 20, self.width - margin, footer_y - 20], fill=(255, 255, 255, 30), width=1)
        cta_text = self._clean_text(content.get("call_to_action", "SAVE FOR MARKET ANALYSIS · SHARE WITH FELLOW INVESTORS 💼")).upper()
        cta_font = ImageFont.truetype(self.font_latin_bold, 21)
        cw = draw.textbbox((0, 0), cta_text, font=cta_font)[2] - draw.textbbox((0, 0), cta_text, font=cta_font)[0]
        draw.text(((self.width - cw) // 2, footer_y), cta_text, font=cta_font, fill=(34, 197, 94))

        return self._save_card(card_img, output_path)

    # ──────────────────────────────────────────────────────────────────────────
    # 5. SPIRITUAL QURAN (Quranic Hearts Style)
    # ──────────────────────────────────────────────────────────────────────────
    def _render_quran_spiritual_card(self, niche: Dict, content: Dict, output_path: str) -> str:
        """
        Sacred & Ethereal Spiritual Quran Card:
        Deep midnight obsidian/emerald canvas, 8-point gold geometric frame accents,
        prominent Amiri bold Arabic calligraphy with radiant glow, Nastaliq translation, and solace reflections.
        """
        hero_path = self._resolve_hero_image("quran_spiritual", content)
        margin = 55
        content_w = self.width - (2 * margin)

        if hero_path:
            hero_img = Image.open(hero_path).convert("RGBA")
            hw, hh = hero_img.size
            scale = max(self.width / hw, self.height / hh)
            nw, nh = int(hw * scale), int(hh * scale)
            hero_img = hero_img.resize((nw, nh), Image.Resampling.LANCZOS)
            cx = (nw - self.width) // 2
            card_img = hero_img.crop((cx, 0, cx + self.width, self.height))

            # Midnight dark vignette so gold frame and Arabic text have maximum reverence & contrast
            gradient = Image.new("RGBA", self.size, (0, 0, 0, 0))
            g_draw = ImageDraw.Draw(gradient)
            for y in range(self.height):
                if y < 240:
                    a = int(140 * (1.0 - y / 240.0))
                elif y > 600:
                    a = int(220 * (((y - 600) / float(self.height - 600)) ** 1.1))
                else:
                    a = 80
                g_draw.line([(0, y), (self.width, y)], fill=(8, 12, 20, a))

            card_img = Image.alpha_composite(card_img, gradient)
            draw = ImageDraw.Draw(card_img)
        else:
            card_img, draw = self._get_base_canvas("quran_spiritual")

        # Ornate Gold Frame Borders
        gold_color = (255, 215, 80)
        draw.rectangle([margin - 15, margin - 15, self.width - margin + 15, self.height - margin + 15],
                       outline=gold_color + (80,), width=1)
        draw.rectangle([margin - 8, margin - 8, self.width - margin + 8, self.height - margin + 8],
                       outline=gold_color + (160,), width=2)

        # Top Badge: QURANIC HEARTS ✨
        badge_text = self._clean_text(content.get("badge", "QURANIC HEARTS ✨"))
        b_font = ImageFont.truetype(self.font_latin_bold, 22)
        b_bbox = draw.textbbox((0, 0), badge_text, font=b_font)
        bw = b_bbox[2] - b_bbox[0]
        badge_y = 75

        # Centered badge pill
        badge_x = (self.width - bw - 50) // 2
        draw.rounded_rectangle([badge_x, badge_y, badge_x + bw + 50, badge_y + 42], radius=21,
                               fill=(20, 25, 40, 240), outline=gold_color, width=2)
        draw.text((badge_x + 25, badge_y + 8), badge_text, font=b_font, fill=gold_color)

        # ── Central Arabic Sacred Stage ──
        # Check if headline contains Arabic/Urdu
        arabic_text = self._clean_text(content.get("headline", "فَإِنَّ مَعَ الْعُسْرِ يُسْرًا"))
        ar_font = ImageFont.truetype(self.font_arabic_bold, 54 if len(arabic_text) < 45 else 44)
        ar_lines = self._wrap_text(draw, arabic_text, ar_font, content_w - 40)
        ar_y = badge_y + 90

        for aline in ar_lines[:2]:
            abox = draw.textbbox((0, 0), aline, font=ar_font, direction="rtl")
            aw = abox[2] - abox[0]
            ax = (self.width - aw) // 2
            # Golden glow halo
            self._draw_blurred_shadow(card_img, draw, aline, ar_font, (ax, ar_y), fill=gold_color + (140,),
                                      radius=8, offset=(0, 0), direction="rtl")
            draw.text((ax, ar_y), aline, font=ar_font, fill=(255, 255, 255), direction="rtl")
            ar_y += int(ar_font.size * 1.55)

        # Ornamental gold divider
        div_y = ar_y + 20
        draw.line([(self.width // 2) - 150, div_y, (self.width // 2) + 150, div_y], fill=gold_color + (120,), width=1)
        draw.polygon([((self.width // 2), div_y - 6), ((self.width // 2) + 6, div_y),
                      ((self.width // 2), div_y + 6), ((self.width // 2) - 6, div_y)], fill=gold_color)

        # ── Urdu / English Translation ──
        highlight = self._clean_text(content.get("highlight", "Indeed, with hardship comes ease — Surah Ash-Sharh"))
        hl_script = self._detect_script(highlight)
        hl_dir = "rtl" if hl_script == "rtl" else "ltr"
        hl_font = self._select_font(highlight, 34 if hl_script == "rtl" else 30)
        hl_lines = self._wrap_text(draw, highlight, hl_font, content_w - 40)
        hl_y = div_y + 25

        for hline in hl_lines[:3]:
            hbox = draw.textbbox((0, 0), hline, font=hl_font, direction=hl_dir)
            hw = hbox[2] - hbox[0]
            hx = (self.width - hw) // 2
            draw.text((hx, hl_y), hline, font=hl_font, fill=(255, 245, 220), direction=hl_dir)
            hl_y += int(hl_font.size * (1.6 if hl_script == "rtl" else 1.35))

        # ── Heart Reflection Card ──
        card_top = hl_y + 30
        card_h = 240
        self._draw_glass_card(draw, (margin, card_top, self.width - margin, card_top + card_h),
                              radius=18, fill=(18, 24, 38, 230), border_color=gold_color + (140,), border_width=1)

        # Reflection Points
        pts_y = card_top + 28
        for pt in content.get("bullet_points", [])[:2]:
            clean_pt = self._clean_text(pt)
            pt_script = self._detect_script(clean_pt)
            pt_dir = "rtl" if pt_script == "rtl" else "ltr"
            pt_font = self._select_font(clean_pt, 27)
            pt_lines = self._wrap_text(draw, clean_pt, pt_font, content_w - 80)

            for pline in pt_lines[:2]:
                pbox = draw.textbbox((0, 0), pline, font=pt_font, direction=pt_dir)
                pw = pbox[2] - pbox[0]
                px = (self.width - margin - 35 - pw) if pt_dir == "rtl" else (margin + 35)
                draw.text((px, pts_y), pline, font=pt_font, fill=(230, 235, 245), direction=pt_dir)
                pts_y += int(pt_font.size * (1.55 if pt_script == "rtl" else 1.3))
            pts_y += 16

        # Footer CTA (Spiritual)
        footer_y = self.height - 118
        cta_text = self._clean_text(content.get("call_to_action", "اس آیت کو تہجد اور دعا کے لیے محفوظ فرمائیں 🕊️"))
        cta_script = self._detect_script(cta_text)
        cta_font = self._select_font(cta_text, 24 if cta_script == "rtl" else 22)
        cta_dir = "rtl" if cta_script == "rtl" else "ltr"
        cw = draw.textbbox((0, 0), cta_text, font=cta_font, direction=cta_dir)[2] - draw.textbbox((0, 0), cta_text, font=cta_font, direction=cta_dir)[0]
        draw.text(((self.width - cw) // 2, footer_y), cta_text, font=cta_font, fill=gold_color, direction=cta_dir)

        return self._save_card(card_img, output_path)

    # ──────────────────────────────────────────────────────────────────────────
    # 6. QURANIC EDUCATION & TAFSEER (Kalamullah Online Style)
    # ──────────────────────────────────────────────────────────────────────────
    def _render_quran_edu_card(self, niche: Dict, content: Dict, output_path: str) -> str:
        """
        Scholarly Islamic Academy Card:
        Emerald & parchment borders, Arabic word-by-word linguistic gem module,
        Tafseer insight box, and 3 practical action points.
        """
        card_img, draw = self._get_base_canvas("quran_edu")
        margin = 55
        content_w = self.width - (2 * margin)

        # Emerald Top Stripe
        draw.rectangle([0, 0, self.width, 10], fill=(70, 200, 160))

        # Header Badge
        badge_text = self._clean_text(content.get("badge", "KALAMULLAH · ACADEMY 📖"))
        b_font = ImageFont.truetype(self.font_latin_bold, 22)
        draw.rounded_rectangle([margin, 60, margin + 290, 104], radius=8, fill=(12, 32, 26, 240), outline=(70, 200, 160), width=2)
        draw.text((margin + 20, 68), badge_text, font=b_font, fill=(70, 200, 160))

        # Right: Tafseer Category
        cat_tag = "فہمِ قرآن و تدبر"
        c_font = ImageFont.truetype(self.font_urdu_bold, 24)
        cw = draw.textbbox((0, 0), cat_tag, font=c_font, direction="rtl")[2] - draw.textbbox((0, 0), cat_tag, font=c_font, direction="rtl")[0]
        draw.text((self.width - margin - cw, 68), cat_tag, font=c_font, fill=(255, 215, 80), direction="rtl")

        # Academic Headline (Ayah or Topic)
        headline = self._clean_text(content.get("headline", "تدبرِ قرآن: صبر اور شکر کی حکمت"))
        h_script = self._detect_script(headline)
        h_dir = "rtl" if h_script == "rtl" else "ltr"
        h_font = self._select_font(headline, 46 if h_script == "rtl" else 42)
        h_lines = self._wrap_text(draw, headline, h_font, content_w)
        h_y = 135
        for line in h_lines[:2]:
            bbox = draw.textbbox((0, 0), line, font=h_font, direction=h_dir)
            lw = bbox[2] - bbox[0]
            lx = (self.width - margin - lw) if h_dir == "rtl" else margin
            draw.text((lx, h_y), line, font=h_font, fill=(255, 255, 255), direction=h_dir)
            h_y += int(h_font.size * (1.6 if h_script == "rtl" else 1.3))

        # ── Module 1: Linguistic Gem / Root Word Box ──
        gem_y = h_y + 15
        gem_h = 160
        self._draw_glass_card(draw, (margin, gem_y, self.width - margin, gem_y + gem_h),
                              radius=14, fill=(10, 30, 24, 235), border_color=(70, 200, 160, 180), border_width=2)
        draw.rounded_rectangle([margin, gem_y, margin + 8, gem_y + gem_h], radius=4, fill=(70, 200, 160))

        highlight = self._clean_text(content.get("highlight", "کلامِ الٰہی کے لغوی اور روحانی اسرار"))
        hl_script = self._detect_script(highlight)
        hl_dir = "rtl" if hl_script == "rtl" else "ltr"
        hl_font = self._select_font(highlight, 30)
        hl_lines = self._wrap_text(draw, highlight, hl_font, content_w - 60)
        text_y = gem_y + 30
        for hline in hl_lines[:3]:
            bbox = draw.textbbox((0, 0), hline, font=hl_font, direction=hl_dir)
            lw = bbox[2] - bbox[0]
            lx = (self.width - margin - 35 - lw) if hl_dir == "rtl" else (margin + 35)
            draw.text((lx, text_y), hline, font=hl_font, fill=(255, 215, 80), direction=hl_dir)
            text_y += int(hl_font.size * 1.5)

        # ── Module 2: 3 Action Points ("عمل کے ۳ سنہرے اصول") ──
        bullets_y = gem_y + gem_h + 35
        # Section header
        sec_title = "عمل کے ۳ سنہرے اصول:"
        sec_font = ImageFont.truetype(self.font_urdu_bold, 28)
        sw = draw.textbbox((0, 0), sec_title, font=sec_font, direction="rtl")[2] - draw.textbbox((0, 0), sec_title, font=sec_font, direction="rtl")[0]
        draw.text((self.width - margin - sw, bullets_y), sec_title, font=sec_font, fill=(70, 200, 160), direction="rtl")
        bullets_y += 48

        for pt in content.get("bullet_points", [])[:3]:
            clean_pt = self._clean_text(pt)
            pt_script = self._detect_script(clean_pt)
            pt_dir = "rtl" if pt_script == "rtl" else "ltr"
            pt_font = self._select_font(clean_pt, 26)
            pt_lines = self._wrap_text(draw, clean_pt, pt_font, content_w - 50)
            for pline in pt_lines[:2]:
                bbox = draw.textbbox((0, 0), pline, font=pt_font, direction=pt_dir)
                pw = bbox[2] - bbox[0]
                px = (self.width - margin - 20 - pw) if pt_dir == "rtl" else (margin + 20)
                draw.text((px, bullets_y), pline, font=pt_font, fill=(230, 240, 235), direction=pt_dir)
                bullets_y += int(pt_font.size * (1.55 if pt_script == "rtl" else 1.3))
            bullets_y += 14

        # Footer CTA
        footer_y = self.height - 90
        cta_text = self._clean_text(content.get("call_to_action", "اس علم کو صدقہ جاریہ کے طور پر شیئر فرمائیں 📖"))
        cta_script = self._detect_script(cta_text)
        cta_font = self._select_font(cta_text, 23 if cta_script == "rtl" else 21)
        cw = draw.textbbox((0, 0), cta_text, font=cta_font, direction="rtl")[2] - draw.textbbox((0, 0), cta_text, font=cta_font, direction="rtl")[0]
        draw.text(((self.width - cw) // 2, footer_y), cta_text, font=cta_font, fill=(70, 200, 160), direction="rtl")

        return self._save_card(card_img, output_path)

    # ──────────────────────────────────────────────────────────────────────────
    # 7. VIRAL YOUTH & MEMES (MLGAA Fan Style)
    # ──────────────────────────────────────────────────────────────────────────
    def _render_youth_card(self, niche: Dict, content: Dict, output_path: str) -> str:
        """
        High-Voltage Relatable Dark Mode Card (X/Instagram Tweet Style):
        Electric yellow & red accents, verified username header, massive punchy relatable headline,
        humorous reaction callout box, and friend-tag CTA.
        """
        card_img, draw = self._get_base_canvas("viral_youth")
        margin = 55
        content_w = self.width - (2 * margin)

        # Electric Yellow Top Accent
        draw.rectangle([0, 0, self.width, 10], fill=(250, 204, 21))

        # Top Social Handle / Header
        avatar_r = 26
        avatar_x = margin + avatar_r
        avatar_y = 75
        draw.ellipse([avatar_x - avatar_r, avatar_y - avatar_r, avatar_x + avatar_r, avatar_y + avatar_r],
                     fill=(250, 204, 21))
        # Letter M in avatar
        av_font = ImageFont.truetype(self.font_latin_bold, 30)
        draw.text((avatar_x - 13, avatar_y - 20), "M", font=av_font, fill=(10, 10, 10))

        # Usernames
        u_font = ImageFont.truetype(self.font_latin_bold, 24)
        h_font = ImageFont.truetype(self.font_latin_bold, 18)
        draw.text((margin + 68, avatar_y - 18), "MLGAA Fan", font=u_font, fill=(255, 255, 255))
        draw.text((margin + 68, avatar_y + 8), "@mlgaafan · 100% Relatable Desi Realities", font=h_font, fill=(148, 163, 184))

        # Divider
        div_y = 130
        draw.line([margin, div_y, self.width - margin, div_y], fill=(255, 255, 255, 30), width=1)

        # Massive Punchline Headline
        headline = self._clean_text(content.get("headline", "ہم رات کو جلدی سونے کی کوشش کرتے ہیں، لیکن دماغ میں پرانے گناہ یاد آ جاتے ہیں"))
        head_script = self._detect_script(headline)
        head_dir = "rtl" if head_script == "rtl" else "ltr"
        head_font = self._select_font(headline, 50 if head_script == "rtl" else 44)
        h_lines = self._wrap_text(draw, headline, head_font, content_w)
        h_y = div_y + 35

        for line in h_lines[:3]:
            bbox = draw.textbbox((0, 0), line, font=head_font, direction=head_dir)
            lw = bbox[2] - bbox[0]
            lx = (self.width - margin - lw) if head_dir == "rtl" else margin
            self._draw_blurred_shadow(card_img, draw, line, head_font, (lx, h_y), radius=4, fill=(0, 0, 0, 220), direction=head_dir)
            draw.text((lx, h_y), line, font=head_font, fill=(255, 255, 255), direction=head_dir)
            h_y += int(head_font.size * (1.6 if head_script == "rtl" else 1.25))

        # ── Relatable Reaction Box ──
        card_top = h_y + 30
        card_h = 180
        self._draw_glass_card(draw, (margin, card_top, self.width - margin, card_top + card_h),
                              radius=16, fill=(25, 20, 10, 240), border_color=(250, 204, 21, 200), border_width=2)
        draw.rounded_rectangle([margin, card_top, margin + 8, card_top + card_h], radius=4, fill=(250, 204, 21))

        highlight = self._clean_text(content.get("highlight", "ساری دنیا سو جاتی ہے اور ہمارا اوور تھنکنگ سیشن شروع ہوتا ہے"))
        hl_script = self._detect_script(highlight)
        hl_dir = "rtl" if hl_script == "rtl" else "ltr"
        hl_font = self._select_font(highlight, 32)
        hl_lines = self._wrap_text(draw, highlight, hl_font, content_w - 60)
        text_y = card_top + 30
        for hline in hl_lines[:3]:
            bbox = draw.textbbox((0, 0), hline, font=hl_font, direction=hl_dir)
            lw = bbox[2] - bbox[0]
            lx = (self.width - margin - 35 - lw) if hl_dir == "rtl" else (margin + 35)
            draw.text((lx, text_y), hline, font=hl_font, fill=(250, 204, 21), direction=hl_dir)
            text_y += int(hl_font.size * 1.5)

        # 2 Relatable Observations
        bullets_y = card_top + card_h + 38
        for pt in content.get("bullet_points", [])[:2]:
            clean_pt = self._clean_text(pt)
            pt_script = self._detect_script(clean_pt)
            pt_dir = "rtl" if pt_script == "rtl" else "ltr"
            pt_font = self._select_font(clean_pt, 28)
            pt_lines = self._wrap_text(draw, clean_pt, pt_font, content_w - 50)
            for pline in pt_lines[:2]:
                bbox = draw.textbbox((0, 0), pline, font=pt_font, direction=pt_dir)
                pw = bbox[2] - bbox[0]
                px = (self.width - margin - 20 - pw) if pt_dir == "rtl" else (margin + 20)
                draw.text((px, bullets_y), pline, font=pt_font, fill=(226, 232, 240), direction=pt_dir)
                bullets_y += int(pt_font.size * (1.55 if pt_script == "rtl" else 1.3))
            bullets_y += 16

        # Footer CTA
        footer_y = self.height - 90
        cta_text = self._clean_text(content.get("call_to_action", "TAG THAT ONE FRIEND WHO DOES THIS EVERY DAY 😂")).upper()
        cta_font = ImageFont.truetype(self.font_latin_bold, 21)
        cw = draw.textbbox((0, 0), cta_text, font=cta_font)[2] - draw.textbbox((0, 0), cta_text, font=cta_font)[0]
        draw.text(((self.width - cw) // 2, footer_y), cta_text, font=cta_font, fill=(250, 204, 21))

        return self._save_card(card_img, output_path)

    # ──────────────────────────────────────────────────────────────────────────
    # 8. IT AGENCY & AI SOLUTIONS (B2B SaaS Bento Card Style)
    # ──────────────────────────────────────────────────────────────────────────
    def _render_it_agency_card(self, niche: Dict, content: Dict, output_path: str) -> str:
        """
        Modern B2B Bento Grid & SaaS UI Layout:
        Violet/Cyan glowing gradients, tech badge, value proposition headline,
        side-by-side Bento metric cards, service checkmarks, and consultation CTA.
        """
        card_img, draw = self._get_base_canvas("it_agency")
        margin = 55
        content_w = self.width - (2 * margin)

        # Violet/Cyan Top Gradient Bar
        draw.rectangle([0, 0, self.width, 10], fill=(139, 92, 246))

        # Tech Badge Pill
        badge_text = self._clean_text(content.get("badge", "TECH AGENCY 🚀")).upper()
        b_font = ImageFont.truetype(self.font_latin_bold, 22)
        draw.rounded_rectangle([margin, 60, margin + 240, 104], radius=8, fill=(24, 18, 48, 240), outline=(139, 92, 246), width=2)
        draw.text((margin + 20, 68), badge_text, font=b_font, fill=(139, 92, 246))

        # Right Tag
        cat_tag = self._clean_text(content.get("category_tag", "AI & WEB SOLUTIONS")).upper()
        cw = draw.textbbox((0, 0), cat_tag, font=b_font)[2] - draw.textbbox((0, 0), cat_tag, font=b_font)[0]
        draw.text((self.width - margin - cw, 70), cat_tag, font=b_font, fill=(6, 182, 212))

        # Hero Value Proposition Headline
        headline = self._clean_text(content.get("headline", "Custom AI Automations That Scale Your Revenue & Operations"))
        head_font = ImageFont.truetype(self.font_latin_bold, 48 if len(headline) < 60 else 40)
        h_lines = self._wrap_text(draw, headline, head_font, content_w)
        h_y = 135
        for line in h_lines[:3]:
            self._draw_blurred_shadow(card_img, draw, line, head_font, (margin, h_y), radius=4, fill=(0, 0, 0, 200))
            draw.text((margin, h_y), line, font=head_font, fill=(255, 255, 255))
            h_y += int(head_font.size * 1.25)

        # Subdeck
        subdeck = self._clean_text(content.get("subdeck", "Transforming complex business workflows into scalable web & AI software."))
        if subdeck:
            s_font = ImageFont.truetype(self.font_latin_bold, 26)
            s_lines = self._wrap_text(draw, subdeck, s_font, content_w)
            for s_line in s_lines[:2]:
                draw.text((margin, h_y + 4), s_line, font=s_font, fill=(148, 163, 184))
                h_y += 34

        # ── Bento Grid: 2 Side-by-Side Cards ──
        bento_top = h_y + 30
        bento_w = (content_w - 20) // 2
        bento_h = 190

        # Bento Card 1: Metric / ROI
        card1_x = margin
        self._draw_glass_card(draw, (card1_x, bento_top, card1_x + bento_w, bento_top + bento_h),
                              radius=16, fill=(20, 16, 38, 240), border_color=(139, 92, 246, 200), border_width=2)
        stat_num = self._clean_text(content.get("stat_number", "10X"))
        stat_lbl = self._clean_text(content.get("stat_label", "FASTER WORKFLOWS")).upper()
        num_font = ImageFont.truetype(self.font_latin_bold, 58)
        lbl_font = ImageFont.truetype(self.font_latin_bold, 18)
        draw.text((card1_x + 24, bento_top + 24), stat_lbl, font=lbl_font, fill=(139, 92, 246))
        draw.text((card1_x + 24, bento_top + 56), stat_num, font=num_font, fill=(255, 255, 255))
        draw.text((card1_x + 24, bento_top + 130), "Automated Operations", font=lbl_font, fill=(148, 163, 184))

        # Bento Card 2: Core Capabilities
        card2_x = margin + bento_w + 20
        self._draw_glass_card(draw, (card2_x, bento_top, card2_x + bento_w, bento_top + bento_h),
                              radius=16, fill=(16, 26, 38, 240), border_color=(6, 182, 212, 200), border_width=2)
        draw.text((card2_x + 24, bento_top + 24), "SOLUTIONS STACK", font=lbl_font, fill=(6, 182, 212))
        cap_font = ImageFont.truetype(self.font_latin_bold, 24)
        draw.text((card2_x + 24, bento_top + 60), "Custom Web Apps", font=cap_font, fill=(255, 255, 255))
        draw.text((card2_x + 24, bento_top + 95), "AI Chatbots & Agents", font=cap_font, fill=(255, 255, 255))
        draw.text((card2_x + 24, bento_top + 130), "Mobile App Dev", font=cap_font, fill=(255, 255, 255))

        # ── Service Checkmarks & Deliverables ──
        bullets_y = bento_top + bento_h + 38
        for pt in content.get("bullet_points", [])[:3]:
            clean_pt = self._clean_text(pt)
            pt_script = self._detect_script(clean_pt)
            pt_dir = "rtl" if pt_script == "rtl" else "ltr"
            pt_font = self._select_font(clean_pt, 25)
            pt_lines = self._wrap_text(draw, clean_pt, pt_font, content_w - 65)

            # Modern cyan diamond marker
            if pt_dir == "rtl":
                icon_x = self.width - margin - 15
                draw.polygon([(icon_x, bullets_y + 8), (icon_x - 8, bullets_y + 16),
                              (icon_x, bullets_y + 24), (icon_x + 8, bullets_y + 16)], fill=(6, 182, 212))
            else:
                icon_x = margin + 15
                draw.polygon([(icon_x, bullets_y + 8), (icon_x + 8, bullets_y + 16),
                              (icon_x, bullets_y + 24), (icon_x - 8, bullets_y + 16)], fill=(6, 182, 212))

            lh = 25 * (1.55 if pt_script == "rtl" else 1.3)
            for pline in pt_lines[:2]:
                bbox = draw.textbbox((0, 0), pline, font=pt_font, direction=pt_dir)
                pw = bbox[2] - bbox[0]
                px = (self.width - margin - 35 - pw) if pt_dir == "rtl" else (margin + 35)
                draw.text((px, bullets_y), pline, font=pt_font, fill=(226, 232, 240), direction=pt_dir)
                bullets_y += int(lh)
            bullets_y += 12

        # Footer CTA
        footer_y = self.height - 90
        draw.line([margin, footer_y - 20, self.width - margin, footer_y - 20], fill=(255, 255, 255, 30), width=1)
        cta_text = self._clean_text(content.get("call_to_action", "BOOK A 15-MINUTE STRATEGY CONSULTATION · LINK IN BIO 💻")).upper()
        cta_font = ImageFont.truetype(self.font_latin_bold, 21)
        cw = draw.textbbox((0, 0), cta_text, font=cta_font)[2] - draw.textbbox((0, 0), cta_text, font=cta_font)[0]
        draw.text(((self.width - cw) // 2, footer_y), cta_text, font=cta_font, fill=(139, 92, 246))

        return self._save_card(card_img, output_path)

    # ──────────────────────────────────────────────────────────────────────────
    # 9. DEBATE & COMMENT TRIGGER (Agree or Disagree Style)
    # ──────────────────────────────────────────────────────────────────────────
    def _render_debate_card(self, niche: Dict, content: Dict, output_path: str) -> str:
        """
        High-tension debate & public opinion card engineered for comment velocity:
        Split dual-color top trim (Hot Red & Electric Cyan), bold proposition headline,
        stacked Stance A (Agree) vs Stance B (Disagree) cards with VS badge,
        and high-converting comment call-to-action pill.
        """
        card_img, draw = self._get_base_canvas("debate_trigger")
        margin = 55
        content_w = self.width - (2 * margin)

        # Split Dual-Tone Top Ribbon (Red vs Cyan Polarity)
        half_w = self.width // 2
        draw.rectangle([0, 0, half_w, 10], fill=(239, 68, 68))       # Red / Hot Take
        draw.rectangle([half_w, 0, self.width, 10], fill=(14, 165, 233)) # Electric Cyan

        # Top Header: AGREE OR DISAGREE? 💬
        badge_text = self._clean_text(content.get("badge", "AGREE OR DISAGREE? 💬")).upper()
        b_font = ImageFont.truetype(self.font_latin_bold, 22)
        b_bbox = draw.textbbox((0, 0), badge_text, font=b_font)
        bw = b_bbox[2] - b_bbox[0]

        draw.rounded_rectangle([margin, 60, margin + bw + 40, 104], radius=8, fill=(35, 15, 20, 240), outline=(239, 68, 68), width=2)
        draw.text((margin + 20, 68), badge_text, font=b_font, fill=(239, 68, 68))

        # Right Tag: "PUBLIC POLL" or "BURNING QUESTION"
        cat_tag = self._clean_text(content.get("category_tag", "PUBLIC OPINION POLL")).upper()
        cw = draw.textbbox((0, 0), cat_tag, font=b_font)[2] - draw.textbbox((0, 0), cat_tag, font=b_font)[0]
        draw.text((self.width - margin - cw, 70), cat_tag, font=b_font, fill=(14, 165, 233))

        # Hero Proposition / Debate Headline
        headline = self._clean_text(content.get("headline", "A University Degree Is Becoming Irrelevant for High Earners"))
        h_script = self._detect_script(headline)
        h_dir = "rtl" if h_script == "rtl" else "ltr"
        h_font = self._select_font(headline, 48 if len(headline) < 60 else 40)
        h_lines = self._wrap_text(draw, headline, h_font, content_w)
        h_y = 135
        for line in h_lines[:3]:
            bbox = draw.textbbox((0, 0), line, font=h_font, direction=h_dir)
            lw = bbox[2] - bbox[0]
            lx = (self.width - margin - lw) if h_dir == "rtl" else margin
            self._draw_blurred_shadow(card_img, draw, line, h_font, (lx, h_y), radius=4, fill=(0, 0, 0, 220), direction=h_dir)
            draw.text((lx, h_y), line, font=h_font, fill=(255, 255, 255), direction=h_dir)
            h_y += int(h_font.size * (1.6 if h_script == "rtl" else 1.25))

        # Subdeck (Context line)
        subdeck = self._clean_text(content.get("subdeck", "With remote digital work booming, where does the real leverage lie?"))
        if subdeck:
            s_script = self._detect_script(subdeck)
            s_dir = "rtl" if s_script == "rtl" else "ltr"
            s_font = self._select_font(subdeck, 25)
            s_lines = self._wrap_text(draw, subdeck, s_font, content_w)
            for s_line in s_lines[:2]:
                bbox = draw.textbbox((0, 0), s_line, font=s_font, direction=s_dir)
                lw = bbox[2] - bbox[0]
                lx = (self.width - margin - lw) if s_dir == "rtl" else margin
                draw.text((lx, h_y + 4), s_line, font=s_font, fill=(148, 163, 184), direction=s_dir)
                h_y += 34

        # ── The Split Stance Arena (Option A vs Option B) ──
        stance_a = self._clean_text(content.get("stance_a", ""))
        stance_b = self._clean_text(content.get("stance_b", ""))
        if not stance_a and content.get("bullet_points"):
            stance_a = "AGREE: " + self._clean_text(content["bullet_points"][0])
        if not stance_b and len(content.get("bullet_points", [])) > 1:
            stance_b = "DISAGREE: " + self._clean_text(content["bullet_points"][1])

        arena_top = h_y + 25
        card_h = 165

        # ── Stance A Card (Cyan / AGREE) ──
        self._draw_glass_card(draw, (margin, arena_top, self.width - margin, arena_top + card_h),
                              radius=16, fill=(12, 28, 42, 240), border_color=(14, 165, 233, 200), border_width=2)
        draw.rounded_rectangle([margin, arena_top, margin + 8, arena_top + card_h], radius=4, fill=(14, 165, 233))

        lbl_font = ImageFont.truetype(self.font_latin_bold, 19)
        draw.text((margin + 26, arena_top + 18), "THE CASE FOR 'AGREE' (OPTION A)", font=lbl_font, fill=(14, 165, 233))

        a_script = self._detect_script(stance_a)
        a_dir = "rtl" if a_script == "rtl" else "ltr"
        a_font = self._select_font(stance_a, 26)
        a_lines = self._wrap_text(draw, stance_a, a_font, content_w - 60)
        a_y = arena_top + 50
        for aline in a_lines[:3]:
            bbox = draw.textbbox((0, 0), aline, font=a_font, direction=a_dir)
            aw = bbox[2] - bbox[0]
            ax = (self.width - margin - 35 - aw) if a_dir == "rtl" else (margin + 26)
            draw.text((ax, a_y), aline, font=a_font, fill=(241, 245, 249), direction=a_dir)
            a_y += int(a_font.size * (1.55 if a_script == "rtl" else 1.3))

        # ── VS Divider Pill ──
        vs_y = arena_top + card_h + 10
        vs_r = 24
        draw.ellipse([(self.width // 2) - vs_r, vs_y - vs_r + 14, (self.width // 2) + vs_r, vs_y + vs_r + 14],
                     fill=(250, 204, 21), outline=(255, 255, 255), width=2)
        vs_font = ImageFont.truetype(self.font_latin_bold, 20)
        draw.text(((self.width // 2) - 14, vs_y + 2), "VS", font=vs_font, fill=(15, 23, 42))

        # ── Stance B Card (Crimson / DISAGREE) ──
        b_top = vs_y + 36
        self._draw_glass_card(draw, (margin, b_top, self.width - margin, b_top + card_h),
                              radius=16, fill=(35, 14, 20, 240), border_color=(239, 68, 68, 200), border_width=2)
        draw.rounded_rectangle([margin, b_top, margin + 8, b_top + card_h], radius=4, fill=(239, 68, 68))

        draw.text((margin + 26, b_top + 18), "THE CASE FOR 'DISAGREE' (OPTION B)", font=lbl_font, fill=(239, 68, 68))

        b_script = self._detect_script(stance_b)
        b_dir = "rtl" if b_script == "rtl" else "ltr"
        b_font = self._select_font(stance_b, 26)
        b_lines = self._wrap_text(draw, stance_b, b_font, content_w - 60)
        b_y = b_top + 50
        for bline in b_lines[:3]:
            bbox = draw.textbbox((0, 0), bline, font=b_font, direction=b_dir)
            bw = bbox[2] - bbox[0]
            bx = (self.width - margin - 35 - bw) if b_dir == "rtl" else (margin + 26)
            draw.text((bx, b_y), bline, font=b_font, fill=(241, 245, 249), direction=b_dir)
            b_y += int(b_font.size * (1.55 if b_script == "rtl" else 1.3))

        # ── Reality Check / Middle Ground Bullet ──
        if len(content.get("bullet_points", [])) > 2:
            mid_pt = self._clean_text(content["bullet_points"][2])
            mid_script = self._detect_script(mid_pt)
            mid_dir = "rtl" if mid_script == "rtl" else "ltr"
            mid_font = self._select_font(mid_pt, 24)
            mid_lines = self._wrap_text(draw, mid_pt, mid_font, content_w - 50)
            mid_y = b_top + card_h + 24
            for mline in mid_lines[:2]:
                bbox = draw.textbbox((0, 0), mline, font=mid_font, direction=mid_dir)
                mw = bbox[2] - bbox[0]
                mx = (self.width - margin - 20 - mw) if mid_dir == "rtl" else (margin + 20)
                draw.text((mx, mid_y), mline, font=mid_font, fill=(180, 195, 215), direction=mid_dir)
                mid_y += 30

        # ── Footer: Comment Ignition Button Pill ──
        footer_y = self.height - 105
        btn_h = 58
        draw.rounded_rectangle([margin, footer_y, self.width - margin, footer_y + btn_h],
                               radius=29, fill=(20, 24, 38, 250), outline=(239, 68, 68), width=2)

        cta_text = self._clean_text(content.get("call_to_action", "DROP 'AGREE' OR 'DISAGREE' IN THE COMMENTS BELOW 👇")).upper()
        cta_font = ImageFont.truetype(self.font_latin_bold, 22)
        cw = draw.textbbox((0, 0), cta_text, font=cta_font)[2] - draw.textbbox((0, 0), cta_text, font=cta_font)[0]
        draw.text(((self.width - cw) // 2, footer_y + 16), cta_text, font=cta_font, fill=(255, 255, 255))

        return self._save_card(card_img, output_path)

    # ──────────────────────────────────────────────────────────────────────────
    # Helper & General Fallback Renderer
    # ──────────────────────────────────────────────────────────────────────────
    def _save_card(self, card_img: Image.Image, output_path: str) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        card_img.convert("RGB").save(output_path, quality=95)
        logger.info(f"✅ Generated Specialized Niche Card: {output_path}")
        return output_path

    def render_card(self, niche: Dict, content: Dict, output_path: str) -> str:
        """
        Routes each niche to its bespoke graphic layout.
        """
        niche_id = niche.get("id", "tech_news")
        dispatch_table = {
            "sports_cricket": self._render_sports_card,
            "tech_news": self._render_tech_news_card,
            "travel_pakistan": self._render_travel_card,
            "business_finance": self._render_business_card,
            "quran_spiritual": self._render_quran_spiritual_card,
            "quran_edu": self._render_quran_edu_card,
            "viral_youth": self._render_youth_card,
            "it_agency": self._render_it_agency_card,
            "debate_trigger": self._render_debate_card,
        }

        renderer = dispatch_table.get(niche_id)
        if renderer:
            return renderer(niche, content, output_path)

        # Fallback to tech news layout if unknown
        return self._render_tech_news_card(niche, content, output_path)
