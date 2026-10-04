"""
Editorial Image Service — dedicated clean 16:9 blog covers.

Blog posts must NEVER reuse the Instagram/Facebook social card (text overlays,
badges, vertical ratios). This service produces a separate photojournalistic
cover per post:
  1. Pollinations FLUX, seeded by post_id so every article gets a unique image.
  2. Curated Unsplash editorial photography for the niche (fallback).
Output is resized to 1280x720 and saved as an optimised progressive JPEG.
"""

import io
import random
import logging
import urllib.parse
import zlib
from pathlib import Path
from typing import Dict, List

import requests
from PIL import Image

logger = logging.getLogger(__name__)

NICHE_EDITORIAL_FALLBACKS: Dict[str, List[str]] = {
    "sports_cricket": [
        "https://images.unsplash.com/photo-1531415074968-036ba1b575da?w=1280&h=720&fit=crop&q=80",
        "https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=1280&h=720&fit=crop&q=80",
        "https://images.unsplash.com/photo-1624526267942-ab0ff8a3e972?w=1280&h=720&fit=crop&q=80",
        "https://images.unsplash.com/photo-1593341646782-e0b495cff86d?w=1280&h=720&fit=crop&q=80",
        "https://images.unsplash.com/photo-1512719994953-eabf50895df7?w=1280&h=720&fit=crop&q=80",
    ],
    "travel_pakistan": [
        "https://images.unsplash.com/photo-1586183189334-a4a7f6b3f5a9?w=1280&h=720&fit=crop&q=80",
        "https://images.unsplash.com/photo-1589308078059-be1415eab4c3?w=1280&h=720&fit=crop&q=80",
        "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=1280&h=720&fit=crop&q=80",
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=1280&h=720&fit=crop&q=80",
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1280&h=720&fit=crop&q=80",
    ],
}


def _save_optimised(raw: bytes, output_path: Path, width: int, height: int) -> bool:
    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        return False
    if img.width < 600:
        return False
    # Center-crop to 16:9 then resize
    target = width / height
    w, h = img.size
    if w / h > target:
        nw = int(h * target)
        img = img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / target)
        img = img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    img = img.resize((width, height), Image.LANCZOS)
    img.save(output_path, "JPEG", quality=78, optimize=True, progressive=True)
    return True


class EditorialImageService:
    @staticmethod
    def generate_editorial_cover(prompt: str, niche_key: str, output_path: Path,
                                 seed_key: str = "", width: int = 1280, height: int = 720,
                                 timeout: int = 60) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        seed = zlib.crc32((seed_key or prompt).encode("utf-8")) % 1_000_000

        enhanced = (
            f"photojournalism editorial photograph, {prompt}, shot on 35mm lens, "
            "natural cinematic lighting, highly detailed, no text, no letters, "
            "no watermark, no logo, no overlays, no frames, widescreen 16:9"
        )
        try:
            url = (f"https://image.pollinations.ai/prompt/{urllib.parse.quote(enhanced)}"
                   f"?width={width}&height={height}&nologo=true&model=flux&seed={seed}")
            res = requests.get(url, headers={"User-Agent": "EditorialCovers/2.0"}, timeout=timeout)
            if res.status_code == 200 and len(res.content) > 5000 and \
                    _save_optimised(res.content, output_path, width, height):
                logger.info(f"✅ Unique 16:9 cover generated: {output_path}")
                return output_path
            logger.warning(f"Pollinations status {res.status_code}; using curated fallback.")
        except Exception as e:
            logger.warning(f"Pollinations failed ({e}); using curated fallback.")

        urls = list(NICHE_EDITORIAL_FALLBACKS.get(niche_key, NICHE_EDITORIAL_FALLBACKS["sports_cricket"]))
        random.Random(seed).shuffle(urls)
        for u in urls:
            try:
                res = requests.get(u, timeout=20)
                if res.status_code == 200 and _save_optimised(res.content, output_path, width, height):
                    logger.info(f"✅ Curated 16:9 cover saved: {output_path}")
                    return output_path
            except Exception as e:
                logger.warning(f"Fallback download failed: {e}")

        raise RuntimeError("Could not produce a clean editorial cover image")
