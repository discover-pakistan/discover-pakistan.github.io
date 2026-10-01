"""
Niche Background & Visual Plate Engine.
Engineered from a graphic designer & video editor perspective to eliminate
unrelated stock lawn grass and create 100% authentic, studio-grade backdrops:

1. sports_cricket: Stadium floodlights, athletic speed stripes, deep pitch night vignette.
2. tech_news: Editorial cobalt radial glow, digital dot-matrix grid, clean tech slate.
3. business_finance: Bloomberg executive slate, subtle bullish chart curve, gold/emerald orbs.
4. it_agency: Linear/Stripe style bento mesh, violet/cyan ambient spotlights, micro-grid.
5. debate_trigger: High-tension polarity arena (Hot Crimson vs Electric Cyan glows).
6. quran_spiritual: Royal midnight obsidian, golden stardust aura, Islamic geometric watermark.
7. quran_edu: Scholarly dark emerald, Islamic arabesque tessellation watermark.
8. viral_youth: Modern dark street asphalt, pop-art halftone pattern, neon edge rim lights.
9. travel_pakistan: Majestic alpine sky/peaks with cinematic atmospheric gradient mask.
"""

import math
from pathlib import Path
from typing import Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

class NicheBackgroundEngine:
    """Generates authentic, niche-specific graphic designer plates."""

    @classmethod
    def generate_background(cls, niche_id: str, size: Tuple[int, int] = (1080, 1350)) -> Image.Image:
        w, h = size
        dispatch = {
            "sports_cricket": cls._create_sports_stadium_background,
            "tech_news": cls._create_tech_grid_background,
            "business_finance": cls._create_finance_chart_background,
            "it_agency": cls._create_it_agency_bento_background,
            "debate_trigger": cls._create_debate_tension_background,
            "quran_spiritual": cls._create_quran_spiritual_background,
            "quran_edu": cls._create_quran_edu_background,
            "viral_youth": cls._create_viral_youth_background,
            "travel_pakistan": cls._create_travel_background,
        }
        creator = dispatch.get(niche_id, cls._create_tech_grid_background)
        return creator(w, h)

    # ──────────────────────────────────────────────────────────────────────────
    # 1. SPORTS / CRICKET: Stadium Floodlights & Athletic Speed Lines
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def _create_sports_stadium_background(cls, w: int, h: int) -> Image.Image:
        # 1. Deep sports emerald-to-midnight gradient
        base = Image.new("RGBA", (w, h), (0, 0, 0, 255))
        draw = ImageDraw.Draw(base)
        for y in range(h):
            prog = y / float(h)
            # Top dark pitch green (2, 22, 14) to bottom pitch black (1, 8, 5)
            r = int(2 * (1.0 - prog) + 1 * prog)
            g = int(24 * (1.0 - prog) + 8 * prog)
            b = int(15 * (1.0 - prog) + 5 * prog)
            draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

        # 2. Athletic Diagonal Speed Stripes (45-degree angled lines)
        stripe_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(stripe_layer)
        for i in range(-h, w + h, 48):
            s_draw.line([(i, 0), (i + h, h)], fill=(16, 185, 129, 14), width=3)
        base = Image.alpha_composite(base, stripe_layer)

        # 3. Dual Stadium Floodlight Flares (High-energy arena lights at top)
        light_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        l_draw = ImageDraw.Draw(light_layer)

        # Left stadium floodlight beam
        l_draw.ellipse([60, -60, 420, 260], fill=(245, 158, 11, 75)) # Trophy Gold warm flare
        l_draw.ellipse([140, -20, 340, 160], fill=(255, 255, 255, 120)) # Core white bulb

        # Right stadium floodlight beam
        l_draw.ellipse([w - 420, -60, w - 60, 260], fill=(16, 185, 129, 75)) # Emerald turf flare
        l_draw.ellipse([w - 340, -20, w - 140, 160], fill=(255, 255, 255, 120)) # Core white bulb

        # Angled floodlight god-ray cones
        l_draw.polygon([(240, 30), (0, h // 2), (w // 2, h // 2)], fill=(255, 255, 255, 18))
        l_draw.polygon([(w - 240, 30), (w // 2, h // 2), (w, h // 2)], fill=(255, 255, 255, 18))

        light_layer = light_layer.filter(ImageFilter.GaussianBlur(radius=45))
        base = Image.alpha_composite(base, light_layer)

        # 4. Heavy Perimeter Vignette (Guarantees 100% text contrast)
        vignette = cls._create_radial_vignette(w, h, darkness=0.75)
        return Image.alpha_composite(base, vignette)

    # ──────────────────────────────────────────────────────────────────────────
    # 2. TECH NEWS: Editorial Cobalt Glow & Digital Dot Grid
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def _create_tech_grid_background(cls, w: int, h: int) -> Image.Image:
        # Deep obsidian tech slate
        base = Image.new("RGBA", (w, h), (11, 15, 25, 255))

        # Radial Cobalt Tech Spotlight
        glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glow)
        g_draw.ellipse([(w // 2) - 450, 60, (w // 2) + 450, 680], fill=(30, 58, 138, 90))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=80))
        base = Image.alpha_composite(base, glow)

        # Subtle Digital Dot-Matrix Grid (36px spacing)
        grid = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        grid_draw = ImageDraw.Draw(grid)
        for x in range(30, w, 36):
            for y in range(30, h, 36):
                grid_draw.rectangle([x, y, x + 2, y + 2], fill=(148, 163, 184, 22))
        base = Image.alpha_composite(base, grid)

        vignette = cls._create_radial_vignette(w, h, darkness=0.70)
        return Image.alpha_composite(base, vignette)

    # ──────────────────────────────────────────────────────────────────────────
    # 3. BUSINESS & FINANCE: Bloomberg Executive Slate & Chart Line
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def _create_finance_chart_background(cls, w: int, h: int) -> Image.Image:
        base = Image.new("RGBA", (w, h), (7, 10, 18, 255))

        # Subtle horizontal price level grids
        grid = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(grid)
        for y in range(160, h - 100, 130):
            g_draw.line([(0, y), (w, y)], fill=(255, 255, 255, 12), width=1)
        base = Image.alpha_composite(base, grid)

        # Bullish Stock Market Chart Wave
        chart_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        c_draw = ImageDraw.Draw(chart_layer)

        # Generate smooth financial trend curve
        points = []
        base_y = int(h * 0.72)
        step = 60
        for i, x in enumerate(range(0, w + step, step)):
            # Ascending trend with realistic market volatility
            vol = math.sin(i * 0.8) * 35 + math.cos(i * 1.5) * 20
            trend = - (i * 8.5) # upward climb
            y = int(base_y + vol + trend)
            points.append((x, y))

        # Fill under chart line
        fill_poly = [(0, h)] + points + [(w, h)]
        c_draw.polygon(fill_poly, fill=(16, 185, 129, 20))

        # Glow line
        for i in range(len(points) - 1):
            c_draw.line([points[i], points[i + 1]], fill=(34, 197, 94, 90), width=4)

        chart_layer = chart_layer.filter(ImageFilter.GaussianBlur(radius=3))
        base = Image.alpha_composite(base, chart_layer)

        # Executive Radial Ambient Orbs
        glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gl_draw = ImageDraw.Draw(glow)
        gl_draw.ellipse([w - 400, -80, w + 100, 380], fill=(250, 204, 21, 45)) # Gold wealth glow
        gl_draw.ellipse([-100, h - 500, 350, h], fill=(16, 185, 129, 45))     # Market green glow
        glow = glow.filter(ImageFilter.GaussianBlur(radius=80))
        base = Image.alpha_composite(base, glow)

        vignette = cls._create_radial_vignette(w, h, darkness=0.75)
        return Image.alpha_composite(base, vignette)

    # ──────────────────────────────────────────────────────────────────────────
    # 4. IT AGENCY: Modern Linear / Stripe Bento Mesh
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def _create_it_agency_bento_background(cls, w: int, h: int) -> Image.Image:
        base = Image.new("RGBA", (w, h), (8, 11, 20, 255))

        # Subtle 32px Micro-Grid (Linear.app design system)
        grid = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(grid)
        for x in range(0, w, 32):
            g_draw.line([(x, 0), (x, h)], fill=(255, 255, 255, 10), width=1)
        for y in range(0, h, 32):
            g_draw.line([(0, y), (w, y)], fill=(255, 255, 255, 10), width=1)
        base = Image.alpha_composite(base, grid)

        # Glowing Bento Ambient Spotlights (Violet at top-left, Cyan at bottom-right)
        orbs = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        o_draw = ImageDraw.Draw(orbs)
        o_draw.ellipse([-100, -80, 520, 480], fill=(124, 58, 237, 80)) # AI Violet
        o_draw.ellipse([w - 500, h - 600, w + 150, h + 80], fill=(6, 182, 212, 70)) # Cyan Laser
        orbs = orbs.filter(ImageFilter.GaussianBlur(radius=90))
        base = Image.alpha_composite(base, orbs)

        vignette = cls._create_radial_vignette(w, h, darkness=0.68)
        return Image.alpha_composite(base, vignette)

    # ──────────────────────────────────────────────────────────────────────────
    # 5. DEBATE TRIGGER: Tension Arena (Hot Crimson vs Electric Cyan)
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def _create_debate_tension_background(cls, w: int, h: int) -> Image.Image:
        base = Image.new("RGBA", (w, h), (10, 12, 16, 255))

        # Split Dual-Glow (Cyan on Left, Crimson on Right)
        glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glow)
        # Left Stance A Glow (Cyan)
        g_draw.ellipse([-200, 200, 450, 950], fill=(2, 132, 199, 85))
        # Right Stance B Glow (Crimson)
        g_draw.ellipse([w - 450, 200, w + 200, 950], fill=(220, 38, 38, 85))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=85))
        base = Image.alpha_composite(base, glow)

        # Central Tension Energy Lines
        tension = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        t_draw = ImageDraw.Draw(tension)
        cx = w // 2
        t_draw.line([(cx, 80), (cx, h - 80)], fill=(255, 255, 255, 20), width=2)
        base = Image.alpha_composite(base, tension)

        vignette = cls._create_radial_vignette(w, h, darkness=0.72)
        return Image.alpha_composite(base, vignette)

    # ──────────────────────────────────────────────────────────────────────────
    # 6. SPIRITUAL QURAN: Royal Obsidian & Golden Islamic Rosette Watermark
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def _create_quran_spiritual_background(cls, w: int, h: int) -> Image.Image:
        # Deep sacred midnight navy
        base = Image.new("RGBA", (w, h), (3, 7, 18, 255))

        # Golden Stardust / Ethereal Aura in center
        aura = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        a_draw = ImageDraw.Draw(aura)
        cx, cy = w // 2, int(h * 0.45)
        a_draw.ellipse([cx - 360, cy - 360, cx + 360, cy + 360], fill=(255, 215, 80, 50))
        aura = aura.filter(ImageFilter.GaussianBlur(radius=75))
        base = Image.alpha_composite(base, aura)

        # Islamic 8-Point Rosette Star Watermark
        pattern = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        p_draw = ImageDraw.Draw(pattern)
        r = 280
        # Draw two overlapping squares rotated 45 degrees
        def get_rotated_rect(center, size, angle_rad):
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)
            hs = size // 2
            pts = [(-hs, -hs), (hs, -hs), (hs, hs), (-hs, hs)]
            rot_pts = []
            for px, py in pts:
                rx = center[0] + (px * cos_a - py * sin_a)
                ry = center[1] + (px * sin_a + py * cos_a)
                rot_pts.append((rx, ry))
            return rot_pts

        sq1 = get_rotated_rect((cx, cy), r * 2, 0)
        sq2 = get_rotated_rect((cx, cy), r * 2, math.pi / 4.0)
        p_draw.polygon(sq1, outline=(255, 215, 80, 28), width=2)
        p_draw.polygon(sq2, outline=(255, 215, 80, 28), width=2)
        p_draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 215, 80, 24), width=2)
        p_draw.ellipse([cx - int(r*0.6), cy - int(r*0.6), cx + int(r*0.6), cy + int(r*0.6)], outline=(255, 215, 80, 20), width=1)

        base = Image.alpha_composite(base, pattern)

        # Stardust particles
        stars = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        st_draw = ImageDraw.Draw(stars)
        import random
        rnd = random.Random(786)
        for _ in range(50):
            sx = rnd.randint(40, w - 40)
            sy = rnd.randint(40, h - 40)
            sr = rnd.uniform(1.0, 3.5)
            sa = rnd.randint(35, 120)
            st_draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 235, 160, sa))
        base = Image.alpha_composite(base, stars)

        vignette = cls._create_radial_vignette(w, h, darkness=0.72)
        return Image.alpha_composite(base, vignette)

    # ──────────────────────────────────────────────────────────────────────────
    # 7. QURANIC EDUCATION: Scholarly Emerald & Islamic Arabesque
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def _create_quran_edu_background(cls, w: int, h: int) -> Image.Image:
        base = Image.new("RGBA", (w, h), (4, 21, 14, 255))
        # Subtle Islamic geometric diamond tessellation
        pattern = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        p_draw = ImageDraw.Draw(pattern)
        step = 80
        for x in range(0, w + step, step):
            for y in range(0, h + step, step):
                p_draw.polygon([(x, y - 25), (x + 25, y), (x, y + 25), (x - 25, y)], outline=(70, 200, 160, 18), width=1)
        base = Image.alpha_composite(base, pattern)

        vignette = cls._create_radial_vignette(w, h, darkness=0.72)
        return Image.alpha_composite(base, vignette)

    # ──────────────────────────────────────────────────────────────────────────
    # 8. VIRAL YOUTH: Street Dark Asphalt & Pop-Art Halftone
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def _create_viral_youth_background(cls, w: int, h: int) -> Image.Image:
        base = Image.new("RGBA", (w, h), (9, 9, 11, 255))

        # Halftone pop-art pattern
        halftone = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        h_draw = ImageDraw.Draw(halftone)
        for x in range(25, w, 40):
            for y in range(25, h, 40):
                # distance from center determines dot radius
                dist = math.sqrt((x - w/2)**2 + (y - h/2)**2)
                rad = max(1.0, 3.5 - (dist / 350.0))
                h_draw.ellipse([x - rad, y - rad, x + rad, y + rad], fill=(250, 204, 21, 22))
        base = Image.alpha_composite(base, halftone)

        # Neon rim lights
        rim = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        r_draw = ImageDraw.Draw(rim)
        r_draw.ellipse([-80, -80, 360, 360], fill=(250, 204, 21, 60)) # Electric Yellow
        r_draw.ellipse([w - 360, h - 360, w + 80, h + 80], fill=(239, 68, 68, 55)) # Punchy Red
        rim = rim.filter(ImageFilter.GaussianBlur(radius=80))
        base = Image.alpha_composite(base, rim)

        vignette = cls._create_radial_vignette(w, h, darkness=0.70)
        return Image.alpha_composite(base, vignette)

    # ──────────────────────────────────────────────────────────────────────────
    # 9. SCENIC TRAVEL: Alpine Nature Plate with Atmospheric Mask
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def _create_travel_background(cls, w: int, h: int) -> Image.Image:
        # Check if genuine nature video or plate is available (clean_sky or clouds_timelapse)
        video_dir = Path(__file__).parent.parent / "assets" / "backgrounds" / "videos"
        sky_path = video_dir / "clean_sky.mp4"
        clouds_path = video_dir / "clouds_timelapse.mp4"
        sunrise_path = video_dir / "sunrise_dawn.mp4"

        nature_file = clouds_path if clouds_path.exists() else (sky_path if sky_path.exists() else sunrise_path)
        if nature_file.exists():
            from video_engine.islamic_backgrounds import VideoBackgroundProvider
            provider = VideoBackgroundProvider(str(nature_file), size=(w, h), dimming_alpha=0.45)
            frame_arr = provider.get_frame(0.0)
            base = Image.fromarray(frame_arr).convert("RGBA")
            provider.close()
        else:
            # Majestic alpine deep twilight gradient
            base = Image.new("RGBA", (w, h), (0, 0, 0, 255))
            draw = ImageDraw.Draw(base)
            for y in range(h):
                prog = y / float(h)
                r = int(12 * (1.0 - prog) + 4 * prog)
                g = int(35 * (1.0 - prog) + 18 * prog)
                b = int(58 * (1.0 - prog) + 26 * prog)
                draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

        # Bottom 40% atmospheric darken mask for Dossier pill
        mask = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        m_draw = ImageDraw.Draw(mask)
        for y in range(int(h * 0.55), h):
            prog = (y - int(h * 0.55)) / float(h * 0.45)
            a = int(210 * prog)
            m_draw.line([(0, y), (w, y)], fill=(6, 12, 18, a))
        base = Image.alpha_composite(base, mask)

        vignette = cls._create_radial_vignette(w, h, darkness=0.60)
        return Image.alpha_composite(base, vignette)

    # ──────────────────────────────────────────────────────────────────────────
    # Helper: Vignette Generator
    # ──────────────────────────────────────────────────────────────────────────
    @classmethod
    def _create_radial_vignette(cls, w: int, h: int, darkness: float = 0.7) -> Image.Image:
        vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vignette)
        cx, cy = w / 2.0, h / 2.0
        max_dist = math.sqrt(cx**2 + cy**2)

        # Concentric gradient steps
        steps = 30
        for i in range(steps):
            ratio = (i + 1) / float(steps)
            rad = max_dist * ratio
            # Exponential curve so center stays clean and corners get dramatic falloff
            alpha = int(255 * darkness * (ratio**2.5))
            draw.rectangle([0, 0, w, h], fill=(0, 0, 0, 0))
            # Draw border vignette
            inset_x = int(cx * (1.0 - ratio))
            inset_y = int(cy * (1.0 - ratio))
            # Smooth outer edge
            draw.rectangle([inset_x, inset_y, w - inset_x, h - inset_y],
                           outline=(0, 0, 0, alpha // steps), width=int(cx / steps) + 2)

        # Smooth blur pass
        return vignette.filter(ImageFilter.GaussianBlur(radius=30))
