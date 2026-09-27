#!/usr/bin/env python3
"""
Netflix Content Analytics - Cinematic Background Generator
===========================================================
Generates a polished 1920x1080 (16:9) dark-mode canvas with smooth
radial glows, micro-dithering to prevent color banding, and authentic
Netflix brand aesthetic for Power BI dashboards.
"""

from pathlib import Path
from typing import Tuple
import numpy as np
from PIL import Image, ImageFilter


def generate_cinematic_canvas(
    width: int = 1920,
    height: int = 1080,
    output_filename: str = "Netflix_Background.png"
) -> Path:
    """Generate high-fidelity, band-free cinematic background canvas."""
    print(f"Rendering canvas at {width}x{height} resolution...")

    # 1. Base Gradient: Subtle top-to-bottom vignette (#101010 to #181818)
    y_coords, x_coords = np.ogrid[:height, :width]
    
    vertical_ratio = y_coords / height
    base_r = 14 + (10 * vertical_ratio)
    base_g = 14 + (10 * vertical_ratio)
    base_b = 14 + (10 * vertical_ratio)
    
    # Initialize float array for smooth math
    canvas = np.zeros((height, width, 3), dtype=np.float32)
    canvas[:, :, 0] = base_r
    canvas[:, :, 1] = base_g
    canvas[:, :, 2] = base_b

    # 2. Define Cinematic Lighting Glows
    glows = [
        # Glow 1: Vibrant Brand Red (Top Left - Header / KPI accent)
        {
            "center": (260, 220),
            "radius": 580.0,
            "color": np.array([229.0, 9.0, 20.0]),
            "intensity": 0.38
        },
        # Glow 2: Deep Crimson / Burgundy (Bottom Right - Balance)
        {
            "center": (1680, 840),
            "radius": 680.0,
            "color": np.array([184.0, 10.0, 22.0]),
            "intensity": 0.32
        },
        # Glow 3: Faint Atmosphere Warmth (Center Accent)
        {
            "center": (960, 540),
            "radius": 900.0,
            "color": np.array([120.0, 10.0, 15.0]),
            "intensity": 0.12
        }
    ]

    # 3. Apply Radial Glows
    for i, glow in enumerate(glows, start=1):
        gx, gy = glow["center"]
        radius = glow["radius"]
        color = glow["color"]
        strength = glow["intensity"]

        dist_sq = (x_coords - gx) ** 2 + (y_coords - gy) ** 2
        falloff = np.exp(-dist_sq / (2.0 * (radius ** 2)))

        for c in range(3):
            canvas[:, :, c] += falloff * color[c] * strength

    # 4. Anti-Banding Subtle Dither (Micro-noise eliminates dark gradient steps)
    rng = np.random.default_rng(seed=42)
    dither_noise = rng.normal(loc=0.0, scale=0.45, size=(height, width, 3))
    canvas += dither_noise

    # 5. Clamp and convert to uint8
    canvas_uint8 = np.clip(canvas, 0, 255).astype(np.uint8)
    image = Image.fromarray(canvas_uint8, mode="RGB")

    # 6. Smooth Blending via Dual-Pass Gaussian Filter
    image = image.filter(ImageFilter.GaussianBlur(radius=8))

    # 7. Export
    output_path = Path(__file__).resolve().parent / output_filename
    image.save(output_path, format="PNG", optimize=True)
    print(f"Canvas exported successfully to: {output_path.name}")
    return output_path


if __name__ == "__main__":
    generate_cinematic_canvas()
