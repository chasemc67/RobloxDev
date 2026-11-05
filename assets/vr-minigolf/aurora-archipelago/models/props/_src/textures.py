"""Procedural, seamlessly tiling 512x512 textures for Aurora Archipelago props (system python + numpy + Pillow).
Adapted from lantern-grove/models/_src/textures.py (same periodic FFT noise + wrap-around stamping).

  python out_props/_src/textures.py        -> out_props/textures/*.png

Colours stay on the course.md palette so a MeshPart that falls back to flat Color reads the same from a distance.
The material -> texture / tile-size map lives in aalib.TEX.
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

N = 512
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "textures")
os.makedirs(OUT, exist_ok=True)


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32) / 255.0


def noise(seed, beta=1.6, sx=1.0, sy=1.0, lo=1.0):
    """Periodic 1/f^beta noise in [0,1]. sx/sy stretch the spectrum (sx>sy -> smooth along x = horizontal streaks)."""
    rng = np.random.default_rng(seed)
    w = rng.standard_normal((N, N))
    F = np.fft.fft2(w)
    fy = np.fft.fftfreq(N)[:, None] * N
    fx = np.fft.fftfreq(N)[None, :] * N
    f = np.sqrt((fx * sx) ** 2 + (fy * sy) ** 2)
    f[0, 0] = 1.0
    amp = 1.0 / np.maximum(f, lo) ** beta
    amp[0, 0] = 0.0
    r = np.real(np.fft.ifft2(F * amp))
    r = (r - r.mean()) / (r.std() + 1e-9)
    return np.clip(0.5 + r * 0.18, 0, 1)


def ramp(t, stops):
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (t >= p0) & (t <= p1)
        u = ((t - p0) / max(p1 - p0, 1e-6))[m]
        out[m] = hexc(c0) * (1 - u[:, None]) + hexc(c1) * u[:, None]
    return out


def save(name, img):
    if isinstance(img, np.ndarray):
        img = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGB")
    img = img.convert("RGB")
    img.save(os.path.join(OUT, name + ".png"), optimize=True)    # 8-bit RGB, no metadata (Studio-safe)
    print("[tex]", name)


def wrap_draw(draw_fn, img):
    d = ImageDraw.Draw(img)
    for dx in (-N, 0, N):
        for dy in (-N, 0, N):
            draw_fn(d, dx, dy)


def timber():
    # warm timber #8A5A3C (pass 2b), vertical grain (V = height on side faces) + plank seams every 128 px
    g = noise(11, beta=1.2, sx=0.08, sy=1.0)
    fine = noise(12, beta=0.9, sx=0.05, sy=1.0)
    t = 0.55 * g + 0.45 * fine
    img = ramp(t, [(0, "#6A4128"), (0.5, "#8A5A3C"), (1, "#A8754F")])
    x = np.arange(N)[None, :]
    seam = (np.abs(((x % 128) - 64)) > 61).astype(np.float32)
    img *= (1 - 0.35 * seam)[..., None]
    save("timber", img)


def snow():
    t = 0.6 * noise(21, beta=1.8) + 0.4 * noise(22, beta=0.8)
    img = ramp(t, [(0, "#C9C3EC"), (0.35, "#E4E8FA"), (0.6, "#F4F6FF"), (1, "#FFFFFF")])
    rng = np.random.default_rng(23)
    sp = rng.random((N, N)) > 0.997
    img[sp] = 1.0
    save("snow", img)


def slate_rock():
    t = 0.65 * noise(31, beta=1.9) + 0.35 * noise(32, beta=1.0, sx=1.0, sy=0.3)
    img = ramp(t, [(0, "#3F4256"), (0.5, "#5E6177"), (1, "#7E8299")])
    save("slate_rock", img)


def basalt_hex():
    # dark basalt #3A3550 with hexagonal column joints (wrap-stamped)
    base = ramp(0.6 * noise(41, beta=1.7) + 0.4 * noise(42, beta=0.9), [(0, "#2A263B"), (0.5, "#3A3550"), (1, "#4E4868")])
    img = Image.fromarray((base * 255).astype(np.uint8), "RGB")
    r = 64.0
    pts = []
    for j in range(-1, int(N / (r * 1.5)) + 2):
        for i in range(-1, int(N / (r * math.sqrt(3))) + 2):
            cx = i * r * math.sqrt(3) + (j % 2) * r * math.sqrt(3) / 2
            cy = j * r * 1.5
            pts.append((cx, cy))
    def draw(d, dx, dy):
        for cx, cy in pts:
            poly = [(cx + dx + r * math.cos(math.radians(60 * k + 30)), cy + dy + r * math.sin(math.radians(60 * k + 30))) for k in range(6)]
            d.line(poly + [poly[0]], fill=(30, 26, 44), width=5)
    # 512 is not a multiple of the hex lattice; use a lattice that fits: 4 columns x (512/(1.5r)) rows
    r = N / (4 * math.sqrt(3))
    pts = [(i * r * math.sqrt(3) + (j % 2) * r * math.sqrt(3) / 2, j * r * 1.5) for j in range(-1, int(N / (1.5 * r)) + 2) for i in range(-1, 6)]
    wrap_draw(draw, img)
    save("basalt_hex", img)


def ice():
    t = 0.5 * noise(51, beta=1.5) + 0.5 * noise(52, beta=1.1, sx=0.25, sy=1.0)
    img = ramp(t, [(0, "#5FBFE6"), (0.5, "#8FE3FF"), (0.8, "#BFF6FF"), (1, "#E9FBFF")])
    im = Image.fromarray((img * 255).astype(np.uint8), "RGB")
    rnd = random.Random(53)
    cracks = [(rnd.uniform(0, N), rnd.uniform(0, N), rnd.uniform(0, math.tau), rnd.uniform(40, 140)) for _ in range(14)]
    def draw(d, dx, dy):
        for x, y, a, L in cracks:
            d.line([(x + dx, y + dy), (x + dx + L * math.cos(a), y + dy + L * math.sin(a))], fill=(233, 251, 255), width=2)
    wrap_draw(draw, im)
    save("ice", im)


def felt():
    # pass 2g felt #36997A with nap noise (2d: #3EA886, 2c: #45B892, 2b: #4FC29E; ramp shifted by the same -8,-15,-12 as the base)
    t = 0.5 * noise(61, beta=0.6) + 0.5 * noise(62, beta=1.4)
    img = ramp(t, [(0, "#267C61"), (0.5, "#36997A"), (1, "#4AAB8C")])
    save("felt", img)


def coral():
    t = 0.6 * noise(71, beta=1.3) + 0.4 * noise(72, beta=0.7)
    img = ramp(t, [(0, "#E8559C"), (0.5, "#FF6FB5"), (1, "#FF9CCB")])
    im = Image.fromarray((img * 255).astype(np.uint8), "RGB")
    rnd = random.Random(73)
    dots = [(rnd.uniform(0, N), rnd.uniform(0, N), rnd.uniform(3, 7)) for _ in range(160)]
    def draw(d, dx, dy):
        for x, y, r in dots:
            d.ellipse([x + dx - r, y + dy - r, x + dx + r, y + dy + r], fill=(255, 196, 222))
    wrap_draw(draw, im)
    save("coral", im)


def moonstone():
    # pale pearl flags with silver inlay seams every 128 px
    t = 0.6 * noise(81, beta=1.6) + 0.4 * noise(82, beta=0.8)
    img = ramp(t, [(0, "#CFCBDD"), (0.5, "#E6E2F0"), (1, "#F7F5FF")])
    x = np.arange(N)[None, :]
    y = np.arange(N)[:, None]
    seam = ((np.abs((x % 128) - 64) > 61) | (np.abs((y % 128) - 64) > 61)).astype(np.float32)
    img = img * (1 - seam[..., None]) + hexc("#B8C2D8") * seam[..., None]
    save("moonstone", img)


if __name__ == "__main__":
    for fn in (timber, snow, slate_rock, basalt_hex, ice, felt, coral, moonstone):
        fn()
