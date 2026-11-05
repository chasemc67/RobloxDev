"""Build textures/bw_atlas_1024.png procedurally (Pillow). Layout: atlas_def.py / atlas_layout.md.
8-bit RGB, no metadata chunks. Deterministic (seeded).
Run: python -I models/_src/make_atlas.py
"""
import os, sys, math, random, colorsys
from PIL import Image, ImageDraw, ImageFilter

SRC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SRC)
from atlas_def import SIZE, PAL, R, SW, DECK_PLANKS, hex_rgb255  # noqa: E402

OUT = os.path.join(os.path.dirname(SRC), "textures", "bw_atlas_1024.png")
rng = random.Random(137)
img = Image.new("RGB", (SIZE, SIZE), hex_rgb255(PAL["awn_cream"]))
px = img.load()


def C(name):
    return hex_rgb255(PAL[name])


def clamp(v):
    return max(0, min(255, int(round(v))))


def jitter(rgb, dv=0.0, dh=0.0, ds=0.0):
    h, s, v = colorsys.rgb_to_hsv(*[c / 255 for c in rgb])
    h = (h + dh) % 1.0
    s = max(0, min(1, s * (1 + ds)))
    v = max(0, min(1, v * (1 + dv)))
    return tuple(clamp(c * 255) for c in colorsys.hsv_to_rgb(h, s, v))


def lerp(a, b, t):
    return tuple(clamp(x + (y - x) * t) for x, y in zip(a, b))


def mul(rgb, k):
    return tuple(clamp(c * k) for c in rgb)


def fill(rect, rgb):
    ImageDraw.Draw(img).rectangle([rect[0], rect[1], rect[2] - 1, rect[3] - 1], fill=rgb)


def pnoise(u, period, seed, octaves=3):
    """Cheap periodic 1D value noise in [−1, 1] (period in px, wraps at SIZE)."""
    s = 0.0
    amp = 1.0
    tot = 0.0
    for o in range(octaves):
        n = int(SIZE / period) * (2 ** o)
        x = u / SIZE * n
        i0 = int(math.floor(x)) % n
        i1 = (i0 + 1) % n
        f = x - math.floor(x)
        f = f * f * (3 - 2 * f)
        r0 = random.Random(seed * 7919 + o * 104729 + i0).uniform(-1, 1)
        r1 = random.Random(seed * 7919 + o * 104729 + i1).uniform(-1, 1)
        s += amp * (r0 + (r1 - r0) * f)
        tot += amp
        amp *= 0.5
    return s / tot


# ---------------------------------------------------------------- row0: deck planks (8 planks x 16 px)
def deck_row():
    x0, y0, x1, y1 = R["deck"]
    gap = C("plank_dark")
    base = C("plank")
    ph = (y1 - y0) // DECK_PLANKS          # 16 px per plank
    for p in range(DECK_PLANKS):
        # board segments along U: butt joints at seeded positions, different in each half (tile a / tile b)
        joints = sorted({0, 512} | {rng.randrange(60, 460), rng.randrange(572, 970)} |
                        ({rng.randrange(150, 360)} if rng.random() < 0.4 else set()))
        joints.append(SIZE)
        for a, b in zip(joints, joints[1:]):
            r = rng.random()
            if r < 0.14:      # a few darker boards leaning to #7A4E2D
                col = lerp(base, gap, rng.uniform(0.22, 0.32))
            else:
                col = jitter(base, dv=rng.uniform(-0.06, 0.06), dh=rng.uniform(-0.012, 0.012),
                             ds=rng.uniform(-0.05, 0.05))
            seed = rng.randrange(1 << 20)
            for x in range(a, b):
                for yy in range(ph):
                    y = y0 + p * ph + yy
                    if yy >= ph - 2 or x in (a, a + 1) and a not in (0, 512):
                        px[x, y] = gap
                        continue
                    g = pnoise(x + yy * 37, 64, seed + yy // 3, 3)
                    k = 1.0 + 0.045 * g
                    if yy == 0:
                        k *= 1.06     # top edge highlight
                    if yy == ph - 3:
                        k *= 0.9
                    px[x, y] = mul(col, k)


# ---------------------------------------------------------------- generic grain strip (tile in U)
def grain_strip(rect, base_rgb, seed, amp=0.08, dark=None, lines=6):
    x0, y0, x1, y1 = rect
    h = y1 - y0
    for y in range(y0, y1):
        row_seed = seed + (y - y0) // 3
        for x in range(x0, x1):
            g = pnoise(x, 128, row_seed, 3)
            k = 1.0 + amp * g
            # periodic darker grain streaks
            s = math.sin((y - y0) / h * math.pi * lines + 1.6 * pnoise(x, 256, seed + 99, 2) * math.pi)
            if s > 0.93:
                k *= 0.86
            px[x, y] = mul(base_rgb, k)
    if dark:
        for x in range(x0, x1):     # soft darker edge lines top/bottom (bevel read)
            for d, k in ((0, 0.8), (1, 0.9)):
                px[x, y0 + d] = mul(px[x, y0 + d], k)
                px[x, y1 - 1 - d] = mul(px[x, y1 - 1 - d], k)


# ---------------------------------------------------------------- brass bevel gradient
def brass_strip():
    x0, y0, x1, y1 = R["brass"]
    lo, base, hi = C("brass_lo"), C("brass"), C("brass_hi")
    for y in range(y0, y1):
        t = (y - y0) / (y1 - y0 - 1)
        # lo -> base -> hi (at 0.4) -> base -> lo
        if t < 0.2:
            c = lerp(lo, base, t / 0.2)
        elif t < 0.4:
            c = lerp(base, hi, (t - 0.2) / 0.2)
        elif t < 0.7:
            c = lerp(hi, base, (t - 0.4) / 0.3)
        else:
            c = lerp(base, lo, (t - 0.7) / 0.3)
        for x in range(x0, x1):
            px[x, y] = mul(c, 1.0 + 0.025 * pnoise(x, 64, 5 + y // 8, 2))


def rope_strip():
    x0, y0, x1, y1 = R["rope"]
    base = C("rope")
    h = y1 - y0
    period = 64             # one twist every 64 px (16 twists across 1024: wraps)
    for y in range(y0, y1):
        v = (y - y0) / h
        shade = 0.78 + 0.32 * math.sin(v * math.pi)      # round cross-section
        for x in range(x0, x1):
            ph = ((x + v * period * 1.2) % period) / period
            tw = 0.82 + 0.18 * math.cos(ph * math.tau)
            groove = 0.72 if ph < 0.06 else 1.0
            px[x, y] = mul(base, shade * tw * groove)


def parchment(rect, border):
    x0, y0, x1, y1 = rect
    base = C("parch")
    ink = C("ink")
    for y in range(y0, y1):
        for x in range(x0, x1):
            n = pnoise(x + y * 13, 96, 31 + y // 16, 2)
            px[x, y] = mul(base, 1.0 + 0.03 * n)
    if border:
        d = ImageDraw.Draw(img)
        bw = 6
        d.rectangle([x0 + 8, y0 + 8, x1 - 9, y1 - 9], outline=ink, width=bw)
        d.rectangle([x0 + 20, y0 + 20, x1 - 21, y1 - 21], outline=lerp(ink, base, 0.45), width=2)


def awning_strip():
    x0, y0, x1, y1 = R["awning"]
    w = (x1 - x0) // 8
    for i in range(8):
        col = C("awn_red") if i % 2 == 0 else C("awn_cream")
        for x in range(x0 + i * w, x0 + (i + 1) * w):
            edge = min(x - (x0 + i * w), x0 + (i + 1) * w - 1 - x)
            k = 0.93 if edge < 3 else 1.0
            for y in range(y0, y1):
                px[x, y] = mul(col, k * (1.0 + 0.02 * pnoise(x * 3 + y, 64, 77, 2)))


def stone_strip():
    x0, y0, x1, y1 = R["stone"]
    base = C("stone")
    mortar = mul(base, 0.72)
    bh = (y1 - y0) // 2
    for row in range(2):
        off = 0 if row == 0 else 64
        xs = list(range(-off, SIZE + 128, 128))
        for a in xs:
            col = jitter(base, dv=rng.uniform(-0.07, 0.07), dh=rng.uniform(-0.01, 0.01))
            for x in range(max(a, 0), min(a + 128, SIZE)):
                for yy in range(bh):
                    y = y0 + row * bh + yy
                    if yy < 2 or x - a < 3:
                        px[x, y] = mortar
                    else:
                        px[x, y] = mul(col, 1.0 + 0.05 * pnoise(x + yy * 29, 32, a + 5, 2))


def turf_strip():
    x0, y0, x1, y1 = R["turf"]
    base, fr = C("turf"), C("fringe")
    for y in range(y0, y1):
        t = (y - y0) / (y1 - y0 - 1)
        edge = min(t, 1 - t)
        for x in range(x0, x1):
            n = pnoise(x * 2 + y * 41, 32, 9 + (y - y0) // 2, 2)
            c = mul(base, 1.0 + 0.05 * n)
            if edge < 0.12:
                c = lerp(fr, c, edge / 0.12 * 0.5)
            # faint mowing stripes along U
            if (x // 128) % 2:
                c = mul(c, 0.965)
            px[x, y] = c


def sandstone_strip():
    """Bands alternate ALONG U (map U = height): 8 bands across 1024, uneven widths, soft edges."""
    x0, y0, x1, y1 = R["sandstone"]
    red, light = C("sand_red"), C("sand_light")
    widths = [160, 96, 144, 112, 160, 96, 144, 112]
    edges = []
    x = 0
    for i, w in enumerate(widths):
        edges.append((x, x + w, red if i % 2 == 0 else light))
        x += w
    for a, b, col in edges:
        for xx in range(a, b):
            for y in range(y0, y1):
                n = pnoise(xx + y * 17, 48, 61 + (y - y0) // 4, 2)
                k = 1.0 + 0.05 * n
                if xx - a < 4 or b - xx <= 4:
                    k *= 0.93
                px[xx, y] = mul(col, k)


def leaf_cell(rect, name, seed):
    x0, y0, x1, y1 = rect
    base = C(name)
    r = random.Random(seed)
    for y in range(y0, y1):
        for x in range(x0, x1):
            px[x, y] = mul(base, 1.0 + 0.04 * pnoise(x * 3 + y * 31, 32, seed, 2))
    sub = img.crop((x0, y0, x1, y1))
    d = ImageDraw.Draw(sub)
    for _ in range(40):      # soft blob mottling (clipped to the cell)
        cx, cy = r.randrange(0, x1 - x0), r.randrange(0, y1 - y0)
        rad = r.randrange(5, 14)
        col = jitter(base, dv=r.uniform(-0.1, 0.08), dh=r.uniform(-0.01, 0.01))
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=col)
    img.paste(sub, (x0, y0))


def crystal_cell(rect):
    x0, y0, x1, y1 = rect
    base, tip = C("crystal"), C("crystal_tip")
    for y in range(y0, y1):
        t = (y - y0) / (y1 - y0 - 1)
        for x in range(x0, x1):
            f = ((x - x0) // 32) % 2
            c = mul(base, 0.86 + 0.24 * (1 - t) + (0.06 if f else 0.0))
            if t < 0.1:
                c = lerp(tip, c, t / 0.1)
            px[x, y] = c


def swatches():
    for name, rect in SW.items():
        fill(rect, C(name))


deck_row()
grain_strip(R["beam"], C("post"), 211, amp=0.07, dark=True, lines=7)
brass_strip()
rope_strip()
parchment(R["parch_panel"], True)
parchment(R["parch"], False)
awning_strip()
stone_strip()
turf_strip()
sandstone_strip()
grain_strip(R["bark"], C("bark"), 401, amp=0.12, dark=False, lines=9)
leaf_cell(R["leaf_orange"], "leaf_orange", 1)
leaf_cell(R["leaf_red"], "leaf_red", 2)
leaf_cell(R["leaf_yellow"], "leaf_yellow", 3)
crystal_cell(R["crystal"])
# unused swatch cells stay awning cream; then exact palette swatches
swatches()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
img = img.convert("RGB")
img.info = {}
img.save(OUT, format="PNG", optimize=True)
chk = Image.open(OUT)
print("wrote", OUT, chk.size, chk.mode, "info:", {k: v for k, v in chk.info.items() if k not in ()})
