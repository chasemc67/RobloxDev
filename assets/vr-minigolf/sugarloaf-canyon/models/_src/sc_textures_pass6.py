"""Sugarloaf Canyon pass 6 textures (system python3 + numpy + Pillow). Adds new maps only; existing PNGs untouched.

  python _src/sc_textures_pass6.py        -> models/textures/{timber_weathered,clay_brick,red_dirt,red_dirt_light}.png

* timber_weathered: the pass-1 timber planks, desaturated and silvered (grey-brown), with cracks and darker end
  grain, for the gondola tower, the trading-post deck and barrels.
* clay_brick: running-bond terracotta bricks with rounded, lighter tops (lane edging curbs).
* red_dirt / red_dirt_light: packed red canyon dirt with faint pebble specks (ground patches).
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textures import N, hexc, noise          # noqa: E402
from sc_textures import save, yy_xx          # noqa: E402


def timber_weathered():
    y, x = yy_xx()
    g = noise(331, beta=1.2, sx=4.0, sy=0.15)
    crack = noise(337, beta=0.6, sx=6.0, sy=0.05)
    pl = np.floor(y / (N / 4))
    tone = 0.9 + 0.1 * np.sin(pl * 2.3 + 0.7)
    base = hexc("#9C7B5C")
    img = base[None, None] * (tone[..., None] * (0.86 + (g[..., None] - 0.5) * 0.55))
    silver = np.clip((noise(339, beta=1.4) - 0.45) * 2.5, 0, 1)[..., None]     # sun-bleached grey patches
    img = img * (1 - 0.25 * silver) + hexc("#B8A68E")[None, None] * 0.25 * silver
    img[crack > 0.78] *= 0.62
    gap = (y % (N / 4)) < 4
    img[gap] = hexc("#4A3626")
    save("timber_weathered", img)


def clay_brick():
    y, x = yy_xx()
    rows = 4
    rh = N / rows
    r = np.floor(y / rh)
    off = (r % 2) * (N / 4)
    bx = ((x + off) % (N / 2))
    by = y % rh
    mortar = (bx < 6) | (by < 6)
    n = noise(351, beta=1.3)
    brick_id = (np.floor((x + off) / (N / 2)) * 7 + r * 3) % 5
    tint = 0.92 + brick_id[..., None] * 0.035
    top = np.clip(1.0 - by / rh, 0, 1)[..., None]                              # lighter upper course edge
    img = hexc("#B65C3E")[None, None] * tint * (0.9 + (n[..., None] - 0.5) * 0.3) * (0.94 + 0.12 * top)
    img[mortar] = hexc("#D9B08C")
    save("clay_brick", img)


def red_dirt(name, base, seed):
    n1 = noise(seed, beta=1.7)
    n2 = noise(seed + 1, beta=0.7)
    img = hexc(base)[None, None] * (0.9 + (n1[..., None] - 0.5) * 0.35 + (n2[..., None] - 0.5) * 0.12)
    rng = np.random.default_rng(seed)
    yy, xx = yy_xx()
    for _ in range(220):                                                        # pebble specks (wrap = tiling)
        cx, cy, rr = rng.uniform(0, N), rng.uniform(0, N), rng.uniform(1.5, 4.5)
        dx = (xx - cx + N / 2) % N - N / 2
        dy = (yy - cy + N / 2) % N - N / 2
        m = dx * dx + dy * dy < rr * rr
        img[m] = img[m] * rng.uniform(0.75, 1.2)
    save(name, img)


if __name__ == "__main__":
    timber_weathered()
    clay_brick()
    red_dirt("red_dirt", "#B9643F", 361)
    red_dirt("red_dirt_light", "#C98055", 371)
