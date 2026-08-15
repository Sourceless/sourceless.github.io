#!/usr/bin/env python3
"""Generate per-post fractal artwork in the site palette.

Each post gets a deterministic Julia set derived from a SHA-256 of its body text
(front matter excluded, so retagging a post doesn't churn its art). The hash
picks an angle on the boundary of the Mandelbrot set's main cardioid. Sampling
the boundary rather than an arbitrary disc matters: a c drawn from open space
outside the set gives a Cantor dust Julia set, which renders as an almost empty
frame. Every point on the cardioid borders the set, so every post gets structure.

Four files per post, because the site has both a dark and a light theme and the
post index needs something far smaller than a social card:

    <slug>.png              1200x630, dark   (also the og:image)
    <slug>-light.png        1200x630, light
    <slug>-thumb.png          96x96,   dark
    <slug>-thumb-light.png    96x96,   light

The expensive escape-time field is computed once per post and colourised twice.

Run from the repo root inside the dev shell:

    nix develop -c python tools/generate_og_images.py

Output lands in assets/og/. Re-run after adding or editing a post.
"""

import hashlib
import pathlib
import re
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTS = ROOT / "_posts"
OUT_DIR = ROOT / "assets" / "og"

WIDTH, HEIGHT = 1200, 630
THUMB = 96
SUPERSAMPLE = 2
MAX_ITER = 400
ESCAPE_R = 2.0
LUT_SIZE = 1024

# Both palettes come from assets/css/main.css. Each is ordered background-first,
# so the ramp walks from the page colour out to the colour with most contrast
# against it, and the set's interior takes the background end.
THEMES = {
    "dark": {
        "stops": ["#1F2933", "#323F4B", "#CBD2D9", "#F5F7FA"],
        "interior": "#1F2933",
    },
    "light": {
        "stops": ["#F5F7FA", "#E4E7EB", "#323F4B", "#1F2933"],
        "interior": "#F5F7FA",
    },
}

FRONT_MATTER = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def build_lut(stops, size=LUT_SIZE):
    """Linear ramp through the palette stops, as an (size, 3) uint8 array."""
    rgb = np.array([hex_to_rgb(s) for s in stops], dtype=np.float64)
    positions = np.linspace(0.0, 1.0, len(rgb))
    t = np.linspace(0.0, 1.0, size)
    return np.stack(
        [np.interp(t, positions, rgb[:, ch]) for ch in range(3)], axis=1
    ).astype(np.uint8)


def body_of(path):
    """Post text with YAML front matter stripped."""
    text = path.read_text(encoding="utf-8")
    return FRONT_MATTER.sub("", text, count=1)


def params_from(seed_bytes):
    """Derive the Julia constant, zoom and rotation from a content hash."""
    digest = hashlib.sha256(seed_bytes).digest()

    def unit(offset):
        """Eight hash bytes as a float in [0, 1)."""
        return int.from_bytes(digest[offset:offset + 8], "big") / 2 ** 64

    theta = unit(0) * 2 * np.pi
    # The boundary of the main cardioid. Nudging fractionally outward turns fat
    # interiors into the dendritic filigree that reads better at card size.
    cardioid = 0.5 * np.exp(1j * theta) - 0.25 * np.exp(2j * theta)
    c = cardioid * (1.0 + 0.002 + unit(24) * 0.018)
    zoom = 1.0 + unit(8) * 0.5
    rotation = unit(16) * 2 * np.pi
    return c, zoom, rotation


def escape_field(c, zoom, rotation):
    """Render the Julia set to palette indices, independent of any theme.

    Returns (indices, interior_mask, height, width) at supersampled resolution.
    """
    w, h = WIDTH * SUPERSAMPLE, HEIGHT * SUPERSAMPLE
    half_h = 1.3 / zoom
    half_w = half_h * (WIDTH / HEIGHT)

    xs = np.linspace(-half_w, half_w, w)
    ys = np.linspace(-half_h, half_h, h)
    grid = xs[np.newaxis, :] + 1j * ys[:, np.newaxis]
    grid *= np.exp(1j * rotation)

    z = grid.ravel().astype(np.complex128)
    nu = np.zeros(z.size, dtype=np.float64)
    active = np.arange(z.size)

    for i in range(MAX_ITER):
        z = z * z + c
        magnitude = np.abs(z)
        escaped = magnitude > ESCAPE_R
        if escaped.any():
            mag = magnitude[escaped]
            # Normalised iteration count, so bands blend instead of stepping.
            nu[active[escaped]] = i + 1 - np.log(np.log(mag)) / np.log(2.0)
            keep = ~escaped
            z = z[keep]
            active = active[keep]
        if active.size == 0:
            break

    # Escape rates vary hugely with c, so a fixed ceiling blows out some frames
    # and leaves others near-black. Stretch each against its own distribution:
    # the bulk of the plane falls to the background end of the ramp, and the
    # slowest-escaping filaments get the high-contrast end.
    escaped_nu = nu[nu > 0.0]
    if escaped_nu.size:
        lo = float(np.percentile(escaped_nu, 55.0))
        hi = float(np.percentile(escaped_nu, 99.7))
        if hi <= lo:
            hi = lo + 1.0
    else:
        lo, hi = 0.0, 1.0
    t = np.clip((nu - lo) / (hi - lo), 0.0, 1.0) ** 1.1
    idx = np.clip((t * (LUT_SIZE - 1)).astype(np.int32), 0, LUT_SIZE - 1)
    return idx, nu == 0.0, h, w


def colourise(idx, interior, h, w, theme):
    pixels = build_lut(THEMES[theme]["stops"])[idx]
    pixels[interior] = hex_to_rgb(THEMES[theme]["interior"])
    return Image.fromarray(pixels.reshape(h, w, 3), mode="RGB")


def save(img, path):
    # Quantise to keep the committed PNGs small; the palette is narrow anyway.
    # Dithering matters here: without it the wide, smooth gradients band badly.
    img = img.convert(
        "P", palette=Image.ADAPTIVE, colors=256, dither=Image.FLOYDSTEINBERG
    )
    img.save(path, optimize=True)
    return path.stat().st_size


def write_set(name, seed_bytes):
    c, zoom, rotation = params_from(seed_bytes)
    idx, interior, h, w = escape_field(c, zoom, rotation)

    total = 0
    for theme in THEMES:
        suffix = "" if theme == "dark" else "-light"
        full = colourise(idx, interior, h, w, theme)

        banner = full.resize((WIDTH, HEIGHT), Image.LANCZOS)
        total += save(banner, OUT_DIR / f"{name}{suffix}.png")

        # Centre square for the post index. The set is centred on the origin,
        # so a centre crop keeps the structure rather than an empty corner.
        side = min(full.width, full.height)
        left = (full.width - side) // 2
        top = (full.height - side) // 2
        square = full.crop((left, top, left + side, top + side))
        thumb = square.resize((THUMB, THUMB), Image.LANCZOS)
        total += save(thumb, OUT_DIR / f"{name}-thumb{suffix}.png")

    print(f"  {name}  c={c:.4f}  zoom={zoom:.2f}  {total / 1024:.0f}KB total")


def main():
    if not POSTS.is_dir():
        sys.exit(f"no _posts directory at {POSTS}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    posts = sorted(POSTS.glob("*.md"))
    print(f"rendering {len(posts) + 1} sets into {OUT_DIR.relative_to(ROOT)}")

    for post in posts:
        # Strip the date prefix: 2026-08-15-slug.md -> slug
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", post.stem)
        write_set(slug, body_of(post).encode("utf-8"))

    # Fallback for the landing page and any page without a post of its own.
    write_set("default", b"sourceless.org")


if __name__ == "__main__":
    main()
