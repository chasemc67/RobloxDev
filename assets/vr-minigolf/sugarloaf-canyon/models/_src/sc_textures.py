"""Sugarloaf Canyon textures (system python3 + numpy + Pillow).

  python3 models/_src/sc_textures.py        -> models/textures/*.png

* Tiling 512x512 material textures (periodic FFT noise from textures.py, so every map tiles).
* strata.png: the candy-stripe rock strip. V = world_y / 36: six 6-stud bands, course.md strata colours 1-6 bottom to
  top (band index floor(y/6) mod 6). Tiles in U (horizontal) and V (every 36 studs).
* card_*.png: RGBA alpha-cut silhouettes for the far scenery cards (not tiling; UV 0..1 over each card).
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textures import N, OUT, hexc, noise, ramp

STRATA = ["#E8736B", "#F6E3C8", "#D9534F", "#F2B48A", "#C8463F", "#FBEAD6"]


def save(name, img, mode="RGB"):
    if isinstance(img, np.ndarray):
        img = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), mode)
    img.save(os.path.join(OUT, name + ".png"), optimize=True)   # 8-bit, no metadata
    print("[tex]", name)


def yy_xx(n=N):
    return np.mgrid[0:n, 0:n].astype(np.float32)


BAND_WIDTHS = [4, 10, 6, 16]
STRATA = ['#E8C9A1','#C68C59','#CC8D91','#AF7061']
def strata():
    y,x=yy_xx(); v=1-(y+.5)/N
    band=np.searchsorted(np.cumsum(BAND_WIDTHS)/36,v,side='right')%4
    cols=np.stack([hexc(c) for c in STRATA])
    shade=1+(noise(12,beta=.8)-.5)*.08+(noise(13,beta=2.2)-.5)*.10
    im=Image.fromarray((np.clip(cols[band]*shade[...,None],0,1)*255).astype('uint8'))
    save('strata',im.filter(ImageFilter.GaussianBlur(2)))
    rough=np.where(band==2,.48,.84)
    save('strata_roughness',Image.fromarray((rough*255).astype('uint8')).filter(ImageFilter.GaussianBlur(2)),mode='L')

def tinted(name, base, seed, var=0.10, streak=(1.0, 1.0), beta=1.6, extra=None):
    n1 = noise(seed, beta=beta, sx=streak[0], sy=streak[1])
    n2 = noise(seed + 1, beta=0.9)
    shade = 1.0 + (n1 - 0.5) * var * 2 + (n2 - 0.5) * var
    img = hexc(base)[None, None] * shade[..., None]
    if extra:
        img = extra(img)
    save(name, img)


def sandstone_block():
    """Pink sandstone masonry (rail stone / building footings): 4 courses x 2 blocks per 512 tile."""
    y, x = yy_xx()
    rows = 4
    rh = N / rows
    r = np.floor(y / rh)
    off = (r % 2) * (N / 4)
    bx = ((x + off) % (N / 2))
    by = y % rh
    mortar = (bx < 5) | (by < 5)
    n = noise(21, beta=1.4)
    img = hexc("#E39A82")[None, None] * (0.92 + (n[..., None] - 0.5) * 0.25)
    img[mortar] = hexc("#B9786A")
    save("sandstone_block", img)


def timber():
    """Weathered timber planks running along U, 4 planks per tile."""
    y, x = yy_xx()
    g = noise(31, beta=1.2, sx=4.0, sy=0.15)
    pl = np.floor(y / (N / 4))
    tone = 0.9 + 0.1 * np.sin(pl * 2.3)
    img = hexc("#8A5A33")[None, None] * (tone[..., None] * (0.85 + (g[..., None] - 0.5) * 0.6))
    gap = (y % (N / 4)) < 4
    img[gap] = hexc("#4A2E1A")
    save("timber", img)


def rope():
    y, x = yy_xx()
    tw = 0.5 + 0.5 * np.sin((x + y) * 2 * np.pi / 32)
    n = noise(41, beta=1.0)
    img = hexc("#C9A46A")[None, None] * (0.78 + 0.3 * tw[..., None] + (n[..., None] - 0.5) * 0.15)
    save("rope", img)


def concrete(name, base, seed):
    def pits(img):
        p = noise(seed + 5, beta=0.3)
        img[p > 0.86] *= 0.85
        return img
    tinted(name, base, seed, var=0.06, beta=1.8, extra=pits)


def cactus():
    """Saguaro ribs run along V (vertical), 8 ribs per tile, with tiny spine dots."""
    y, x = yy_xx()
    rib = 0.5 + 0.5 * np.cos(x * 2 * np.pi / 64)
    n = noise(51, beta=1.4, sx=4.0, sy=0.3)
    img = hexc("#3E8E41")[None, None] * (0.78 + 0.32 * rib[..., None] + (n[..., None] - 0.5) * 0.12)
    rng = np.random.default_rng(52)
    for _ in range(260):
        cx, cy = rng.integers(0, N, 2)
        cx = (cx // 64) * 64 + 32
        img[max(cy - 1, 0):cy + 2, max(cx - 1, 0):cx + 2] = hexc("#F6E3C8")
    save("cactus", img)


def sand(name, base, seed, ripple=0.0):
    def rip(img):
        if ripple:
            y, x = yy_xx()
            n = noise(seed + 9, beta=2.0)
            r = 0.5 + 0.5 * np.sin((y + n * 120) * 2 * np.pi / 32)
            img *= (1 - ripple / 2 + ripple * r)[..., None]
        return img
    tinted(name, base, seed, var=0.07, beta=1.0, extra=rip)


def card(name, alpha_fn, color_fn, blur=1.0):
    """RGBA card. alpha_fn(u, v) -> bool mask (u right, v up, 0..1); color_fn(u, v) -> rgb."""
    y, x = yy_xx()
    u = (x + 0.5) / N
    v = 1.0 - (y + 0.5) / N
    a = alpha_fn(u, v).astype(np.float32)
    rgb = color_fn(u, v)
    al = Image.fromarray((a * 255).astype(np.uint8), "L")
    if blur:
        al = al.filter(ImageFilter.GaussianBlur(blur))
    al = (np.asarray(al) > 127).astype(np.uint8) * 255          # alpha-cut: hard 0/255
    img = np.dstack([(np.clip(rgb, 0, 1) * 255).astype(np.uint8), al])
    Image.fromarray(img, "RGBA").save(os.path.join(OUT, name + ".png"), optimize=True)
    print("[tex]", name)


def hazed_strata(u, v, haze_lo="#B49AC9", haze_hi="#F2B48A", haze=0.62, bands=10.0, seed=61):
    """Distant striped rock: strata colours mixed toward lilac at the foot and peach at the top."""
    cols = np.stack([hexc(c) for c in STRATA])
    b = np.searchsorted(np.cumsum(BAND_WIDTHS)/36, (v*bands/4)%1, side="right")%4
    base = cols[b]
    n = noise(seed, beta=1.6)
    base = base * (0.9 + (n[..., None] - 0.5) * 0.25)
    hz = ramp(v, [(0.0, haze_lo), (1.0, haze_hi)])
    k = haze + 0.15 * (1 - v)[..., None]
    return base * (1 - k) + hz * k


def far_cards():
    def wob(u, s, a=0.012):
        return a * (np.sin(u * 37 + s) + 0.6 * np.sin(u * 91 + 2 * s))
    # distant mesa: flat top at 0.92, talus shoulders to the edges
    card("card_mesa", lambda u, v: v < np.minimum(0.92 + wob(u, 1), np.minimum(u, 1 - u) * 6.0 + 0.10),
         lambda u, v: hazed_strata(u, v))
    # butte spire: tall narrow tower on a flared talus
    def butte_a(u, v):
        w = np.where(v < 0.2, 0.46 - v * 0.8, 0.30 - (v - 0.2) * 0.05)
        top = 0.97 + wob(u, 3)
        return (np.abs(u - 0.5) < w + wob(v, 2, 0.01)) & (v < top)
    card("card_butte", butte_a, lambda u, v: hazed_strata(u, v, haze=0.35, bands=24.0, seed=62))
    # far arch: two legs and a lintel, opening 0.20..0.80 x 0..0.66
    def arch_a(u, v):
        outer = (v < 0.95 - 0.10 * (2 * u - 1) ** 2 + wob(u, 5)) & (np.abs(u - 0.5) < 0.49)
        opening = ((u - 0.5) / 0.31) ** 2 + (v / 0.70) ** 2 < 1.0
        return outer & ~opening
    card("card_far_arch", arch_a, lambda u, v: hazed_strata(u, v, haze=0.55, bands=14.0, seed=63))
    # sugarloaf twins: two rounded domes
    def twins(u, v):
        d1 = ((u - 0.32) / 0.30) ** 2 + (v / 0.98) ** 2 < 1
        d2 = ((u - 0.72) / 0.26) ** 2 + (v / 0.80) ** 2 < 1
        return d1 | d2
    card("card_twins", twins, lambda u, v: hazed_strata(u, v, haze=0.55, bands=18.0, seed=64))
    # cloud streak: long soft pink-orange streak (alpha-cut, fringed)
    def cloud_a(u, v):
        n = noise(65, beta=2.0, sx=0.3, sy=2.0)
        env = np.sin(np.clip(u, 0, 1) * np.pi) ** 0.7
        return (np.abs(v - 0.5 - 0.06 * np.sin(u * 6)) < 0.30 * env * (0.6 + n * 0.8))
    card("card_cloud", cloud_a, lambda u, v: ramp(v, [(0, "#F28C28"), (0.5, "#F7A1A6"), (1, "#FFD9C2")]), blur=2.0)
    # sun disc: soft gold disc with a hot core (alpha-cut circle)
    card("sun_disc", lambda u, v: np.hypot(u - 0.5, v - 0.5) < 0.48,
         lambda u, v: ramp(1 - np.hypot(u - 0.5, v - 0.5) * 2, [(0, "#FFB347"), (0.5, "#FFD36B"), (1, "#FFF6D8")]))


def crystal():
    """Faint facet streaks for rock candy (Glass)."""
    tinted("crystal_pink", "#FF6FA8", 71, var=0.08, streak=(0.2, 3.0))
    tinted("crystal_amber", "#FFB347", 72, var=0.08, streak=(0.2, 3.0))


if __name__ == "__main__":
    strata()
    sandstone_block()
    timber()
    rope()
    concrete("concrete_red", "#D9343A", 81)
    concrete("concrete_white", "#FFF8F0", 83)
    cactus()
    sand("sand_peach", "#E59C7C", 91, ripple=0.08)
    sand("sand_floor", "#D88E5C", 93, ripple=0.06)
    sand("powder_sugar", "#FFF8F0", 95, ripple=0.10)
    crystal()
    far_cards()
