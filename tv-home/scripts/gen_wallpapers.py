#!/usr/bin/env python3
"""Génère des fonds d'écran nature 1920x1080 (paysages stylisés, sans licence tierce)."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

W, H = 1920, 1080
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "wallpapers")


def rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def vgrad(stops):
    """Dégradé vertical: stops = [(position 0..1, '#hex'), ...]."""
    y = np.linspace(0, 1, H)
    pos = [s[0] for s in stops]
    cols = np.stack([rgb(s[1]) for s in stops])
    col = np.stack([np.interp(y, pos, cols[:, c]) for c in range(3)], axis=1)
    return np.repeat(col[:, None, :], W, axis=1)


def ridge(rng, base, amp, rough=0.55, octaves=8, freq=2.0):
    x = np.linspace(0, 1, W)
    y = np.zeros(W)
    a, f = amp, freq
    for _ in range(octaves):
        y += a * np.sin(2 * np.pi * (f * x + rng.random())) * (0.6 + 0.4 * rng.random())
        a *= rough
        f *= 2.03
    return base + y


def fill_below(img, heights, color, alpha=1.0, soft=1.5):
    yy = np.arange(H)[:, None]
    mask = np.clip((yy - heights[None, :] * H) / soft + 0.5, 0, 1) * alpha
    img[:] = img * (1 - mask[..., None]) + color * mask[..., None]


def glow(img, cx, cy, r, color, strength):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    g = np.exp(-(d / r) ** 2) * strength
    img[:] = img + (color - img) * g[..., None]


def disc(img, cx, cy, r, color):
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    m = np.clip(r - d + 0.5, 0, 1)
    img[:] = img * (1 - m[..., None]) + color * m[..., None]


def trees(rng, img, base_line, color, count, hmin, hmax):
    """Silhouettes de sapins le long d'une ligne de crête."""
    yy, xx = np.mgrid[0:H, 0:W]
    mask = np.zeros((H, W), dtype=np.float32)
    for _ in range(count):
        cx = rng.uniform(0, W)
        th = rng.uniform(hmin, hmax) * H
        tw = th * rng.uniform(0.22, 0.3)
        by = base_line[int(np.clip(cx, 0, W - 1))] * H + 4
        x0, x1 = int(max(cx - tw, 0)), int(min(cx + tw, W))
        y0, y1 = int(max(by - th, 0)), int(min(by, H))
        if x1 <= x0 or y1 <= y0:
            continue
        sy, sx = yy[y0:y1, x0:x1], xx[y0:y1, x0:x1]
        t = (sy - (by - th)) / th
        half = tw * t * (0.85 + 0.15 * np.sin(t * 40))
        m = np.clip(half - np.abs(sx - cx) + 0.5, 0, 1)
        mask[y0:y1, x0:x1] = np.maximum(mask[y0:y1, x0:x1], m)
    img[:] = img * (1 - mask[..., None]) + color * mask[..., None]


def stars(rng, img, n, top=0.6):
    for _ in range(n):
        x, y = rng.integers(0, W), rng.integers(0, int(H * top))
        b = rng.uniform(0.3, 1.0) * (1 - y / (H * top))
        img[y, x] = img[y, x] + (255 - img[y, x]) * b


def reflect(img, horizon, tint, blur=6):
    h = int(horizon * H)
    above = img[:h][::-1][: H - h].copy()
    pil = Image.fromarray(np.clip(above, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur))
    ref = np.asarray(pil).astype(np.float32)
    n = ref.shape[0]
    ripple = (np.sin(np.arange(n)[:, None] * 0.9 + np.linspace(0, 30, W)[None, :]) * 0.04 + 0.96)
    ref = ref * ripple[..., None]
    fade = np.linspace(0.85, 0.55, n)[:, None, None]
    img[h:h + n] = ref * fade + tint * (1 - fade)


def finish(img, rng, name):
    img += rng.normal(0, 2.2, img.shape)  # grain anti-banding
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    out.save(OUT / name, quality=86, optimize=True, progressive=True)
    print("✓", name)


def scene_alpes(rng):
    img = vgrad([(0, "#1d2b53"), (0.35, "#7a5c8e"), (0.55, "#f2a07b"), (0.62, "#ffd6a0"), (1, "#ffd6a0")])
    glow(img, W * 0.62, H * 0.56, 380, rgb("#fff1c9"), 0.8)
    disc(img, W * 0.62, H * 0.56, 46, rgb("#fff6dd"))
    layers = [(0.50, 0.10, "#9c7fa6"), (0.58, 0.08, "#6f5a85"), (0.67, 0.07, "#4a3d66"), (0.78, 0.05, "#2b2645"), (0.90, 0.03, "#16142a")]
    for base, amp, c in layers:
        fill_below(img, ridge(rng, base, amp, rough=0.5), rgb(c))
    finish(img, rng, "01-alpes-aube.jpg")


def scene_foret(rng):
    img = vgrad([(0, "#c9d6d3"), (0.6, "#e8ece4"), (1, "#e8ece4")])
    cols = ["#a9bbb3", "#86a096", "#5f7e73", "#3d5a50", "#1f3830"]
    for i, c in enumerate(cols):
        line = ridge(rng, 0.45 + i * 0.1, 0.035, rough=0.45, octaves=5)
        fill_below(img, line, rgb(c))
        trees(rng, img, line, rgb(c), 60 + i * 25, 0.05 + i * 0.03, 0.09 + i * 0.05)
        if i < len(cols) - 1:  # brume entre les plans
            mist = vgrad([(0, "#e8ece4"), (1, "#e8ece4")])
            yy = np.arange(H)[:, None, None] / H
            m = np.clip(1 - np.abs(yy - (0.47 + i * 0.1)) / 0.07, 0, 1) * 0.35
            img[:] = img * (1 - m) + mist * m
    finish(img, rng, "02-foret-brume.jpg")


def scene_lac(rng):
    img = vgrad([(0, "#0e2340"), (0.3, "#3b4f86"), (0.48, "#e0766a"), (0.56, "#ffb46b"), (1, "#ffb46b")])
    glow(img, W * 0.35, H * 0.55, 420, rgb("#ffd59a"), 0.9)
    disc(img, W * 0.35, H * 0.53, 54, rgb("#fff0cf"))
    for base, amp, c in [(0.45, 0.07, "#8a4f6e"), (0.51, 0.05, "#4b2f52"), (0.56, 0.02, "#22172e")]:
        fill_below(img, ridge(rng, base, amp), rgb(c))
    reflect(img, 0.58, rgb("#2a1f3a"))
    line = np.full(W, 0.86) + np.sin(np.linspace(0, 6, W)) * 0.01
    fill_below(img, line, rgb("#120c18"))
    trees(rng, img, line, rgb("#120c18"), 25, 0.12, 0.22)
    finish(img, rng, "03-lac-couchant.jpg")


def scene_dunes(rng):
    img = vgrad([(0, "#2c3e70"), (0.4, "#c97d6a"), (0.6, "#f5c58e"), (1, "#f5c58e")])
    glow(img, W * 0.78, H * 0.6, 300, rgb("#fff0c8"), 0.7)
    for i, (c, base) in enumerate([("#d99a6c", 0.6), ("#c27a52", 0.68), ("#9d5a3d", 0.77), ("#6e3a29", 0.88)]):
        x = np.linspace(0, 1, W)
        h = base + 0.06 * np.sin(2 * np.pi * (x * (1.2 + i * 0.4) + rng.random())) ** 2 * -1 + ridge(rng, 0, 0.008, octaves=4)
        fill_below(img, h, rgb(c))
    finish(img, rng, "04-dunes-crepuscule.jpg")


def scene_aurore(rng):
    img = vgrad([(0, "#030712"), (0.55, "#0b1d33"), (0.75, "#123049"), (1, "#123049")])
    stars(rng, img, 1400, top=0.75)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    for k, (c, off) in enumerate([("#3cf0a0", 0.0), ("#5fd1ff", 1.7), ("#9a7bff", 3.1)]):
        center = H * (0.28 + 0.06 * k) + 80 * np.sin(xx / W * 5 + off) + 30 * np.sin(xx / W * 13 + off)
        band = np.exp(-((yy - center) / (60 + 20 * k)) ** 2) * (0.55 - 0.13 * k)
        streak = 0.75 + 0.25 * np.sin(xx / 7 + off * 10)
        m = (band * streak)[..., None]
        img[:] = img + (rgb(c) - img) * m
    for base, amp, c in [(0.66, 0.08, "#0e1a26"), (0.76, 0.06, "#081018")]:
        fill_below(img, ridge(rng, base, amp, rough=0.5), rgb(c))
    reflect(img, 0.82, rgb("#05090f"), blur=8)
    finish(img, rng, "05-aurore-boreale.jpg")


def scene_ocean(rng):
    img = vgrad([(0, "#4a90c8"), (0.45, "#a9d2ea"), (0.55, "#e6f2f6"), (1, "#e6f2f6")])
    glow(img, W * 0.5, H * 0.52, 500, rgb("#fffaf0"), 0.6)
    fill_below(img, np.full(W, 0.55), rgb("#2d6f99"), soft=1)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sea = yy > H * 0.55
    t = (yy - H * 0.55) / (H * 0.45)
    waves = np.sin(xx / (40 + 200 * t) + yy / 3) * np.sin(xx / 97 + yy / 11)
    shade = (waves * 18 * (0.3 + t))[..., None]
    deep = rgb("#174a6e") * t[..., None] + rgb("#3a86b3") * (1 - t[..., None])
    img[:] = np.where(sea[..., None], deep + shade, img)
    glint = np.exp(-((xx - W * 0.5) / (90 + 260 * t)) ** 2) * (waves > 0.5) * sea * (1 - t)
    img[:] = img + (255 - img) * glint[..., None] * 0.8
    finish(img, rng, "06-ocean-horizon.jpg")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    for scene in (scene_alpes, scene_foret, scene_lac, scene_dunes, scene_aurore, scene_ocean):
        scene(rng)
