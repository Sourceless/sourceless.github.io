#!/usr/bin/env python3
"""Generate per-post Open Graph cards as Julia set fractals in the site palette.

Each post gets a deterministic image derived from a SHA-256 of its body text
(front matter excluded, so retagging a post doesn't churn its art). The hash
picks an angle on the boundary of the Mandelbrot set's main cardioid. Sampling
the boundary rather than an arbitrary disc matters: a c drawn from open space
outside the set gives a Cantor dust Julia set, which renders as an almost empty
card. Every point on the cardioid borders the set, so every post gets structure.

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
SUPERSAMPLE = 2
MAX_ITER = 400
ESCAPE_R = 2.0

# Site palette, from assets/css/main.css. Ordered darkest to lightest; the
# escape-time ramp walks this from the set's edge outward.
PALETTE = ["#1F2933", "#323F4B", "#CBD2D9", "#F5F7FA"]
INTERIOR = "#1F2933"

FRONT_MATTER = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def build_lut(stops, size=1024):
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
    # Parameterise the boundary of the Mandelbrot set's main cardioid. Every
    # point on it borders the set, so the Julia set is connected and richly
    # structured. Nudging fractionally outward turns the fat interiors into the
    # dendritic filigree that reads well at card size.
    cardioid = 0.5 * np.exp(1j * theta) - 0.25 * np.exp(2j * theta)
    c = cardioid * (1.0 + 0.002 + unit(24) * 0.018)
    zoom = 1.0 + unit(8) * 0.5
    rotation = unit(16) * 2 * np.pi
    return c, zoom, rotation


def render(c, zoom, rotation, lut):
    w, h = WIDTH * SUPERSAMPLE, HEIGHT * SUPERSAMPLE
    half_h = 1.3 / zoom
    half_w = half_h * (WIDTH / HEIGHT)

    xs = np.linspace(-half_w, half_w, w)
    ys = np.linspace(-half_h, half_h, h)
    grid = xs[np.newaxis, :] + 1j * ys[:, np.newaxis]
    grid *= np.exp(1j * rotation)

    z = grid.ravel().astype(np.complex128)
    n = z.size
    nu = np.zeros(n, dtype=np.float64)
    active = np.arange(n)

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

    # Escape rates vary hugely with c, so a fixed ceiling blows out some cards
    # and leaves others near-black. Stretch each card against its own
    # distribution instead: the bulk of the plane falls to the dark end of the
    # ramp, and the slowest-escaping filaments get the bright end.
    escaped_nu = nu[nu > 0.0]
    if escaped_nu.size:
        lo = float(np.percentile(escaped_nu, 55.0))
        hi = float(np.percentile(escaped_nu, 99.7))
        if hi <= lo:
            hi = lo + 1.0
    else:
        lo, hi = 0.0, 1.0
    t = np.clip((nu - lo) / (hi - lo), 0.0, 1.0) ** 1.1
    idx = np.clip((t * (len(lut) - 1)).astype(np.int32), 0, len(lut) - 1)
    pixels = lut[idx]
    pixels[nu == 0.0] = hex_to_rgb(INTERIOR)

    img = Image.fromarray(pixels.reshape(h, w, 3), mode="RGB")
    return img.resize((WIDTH, HEIGHT), Image.LANCZOS)


def write_card(name, seed_bytes, lut):
    c, zoom, rotation = params_from(seed_bytes)
    img = render(c, zoom, rotation, lut)
    # Quantise to keep the committed PNGs small; the palette is narrow anyway.
    # Dithering matters here: without it the wide, smooth gradients band badly.
    img = img.convert(
        "P", palette=Image.ADAPTIVE, colors=256, dither=Image.FLOYDSTEINBERG
    )
    path = OUT_DIR / f"{name}.png"
    img.save(path, optimize=True)
    size_kb = path.stat().st_size / 1024
    print(f"  {path.relative_to(ROOT)}  c={c:.4f}  zoom={zoom:.2f}  {size_kb:.0f}KB")


def main():
    if not POSTS.is_dir():
        sys.exit(f"no _posts directory at {POSTS}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    posts = sorted(POSTS.glob("*.md"))
    print(f"rendering {len(posts) + 1} cards into {OUT_DIR.relative_to(ROOT)}")
    lut = build_lut(PALETTE)

    for post in posts:
        # Strip the date prefix: 2026-08-15-slug.md -> slug
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", post.stem)
        write_card(slug, body_of(post).encode("utf-8"), lut)

    # Fallback card for the landing page and any page without its own post.
    write_card("default", b"sourceless.org", lut)


if __name__ == "__main__":
    main()
