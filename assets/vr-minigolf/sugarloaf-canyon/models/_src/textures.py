"""Procedural, seamlessly tiling 512x512 textures for Lantern Grove (system python3 + numpy + Pillow).

  python3 models/_src/textures.py        -> models/textures/*.png

Every texture tiles (FFT noise is periodic; stamped shapes wrap around the edges). Colours stay close to the
course.md palette so a MeshPart that falls back to flat Color looks the same from a distance.
The material -> texture / tile-size map lives in lglib.TEX.
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


def lerp3(a, b, t):
    t = t[..., None]
    return a * (1 - t) + b * t


def ramp(t, stops):
    """stops: [(pos, hex)] -> colour image."""
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
    img.save(os.path.join(OUT, name + ".png"), optimize=True)
    print("[tex]", name)


def wrap_draw(draw_fn, img):
    """Call draw_fn(draw, dx, dy) for the 9 wrap offsets so stamps crossing an edge tile."""
    d = ImageDraw.Draw(img)
    for dx in (-N, 0, N):
        for dy in (-N, 0, N):
            draw_fn(d, dx, dy)


def leaf_poly(cx, cy, L, W, ang, kind):
    """Leaf outline points. kind 'maple' (5-lobed star-ish) or 'oval'."""
    pts = []
    if kind == "maple":
        for i in range(10):
            a = ang + math.tau * i / 10
            r = L * (1.0 if i % 2 == 0 else 0.48)
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    else:
        for i in range(12):
            t = math.tau * i / 12
            x, y = math.cos(t) * L, math.sin(t) * W * (1 - 0.35 * math.cos(t))
            pts.append((cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)))
    return pts


def jitter(hexv, rnd, amt=0.12):
    c = hexc(hexv)
    k = 1 + rnd.uniform(-amt, amt)
    return tuple(int(min(255, max(0, v * k * 255 + rnd.uniform(-8, 8)))) for v in c)


# ---------------------------------------------------------------------------- felt (soft putting green)
def felt():
    """Pass 4 (art director): softer, slightly darker felt like the concepts, with a faint nap so slopes read.
    Low-contrast mowing bands, fine directional fibres (nap runs along V) and soft mottling. felt_normal.png is the
    matching tangent-space normal map (nap ridges + mottling) for SurfaceAppearance.NormalMap.
    Pass 7: a bit darker again and a clearly stronger nap (colour streaks + normal ridges) so slopes and the H9 dip
    read; felt_bright (H8/H9) darkened less, so it stays relatively brighter."""
    lo = noise(1, beta=1.8)
    nap = noise(3, beta=0.9, sx=0.08, sy=1.0)          # streaks along the tile's V axis (fibre direction)
    fine = noise(2, beta=0.25)
    x = np.arange(N)[None, :] / N
    stripes = 0.5 + 0.5 * np.sign(np.sin(math.tau * 2 * x))  # 2 soft mowing bands per tile (tile = 8 studs)
    stripes = np.array(Image.fromarray((stripes * 255).astype(np.uint8).repeat(N, 0)).filter(ImageFilter.GaussianBlur(10))) / 255.0
    t = 0.5 + (lo - 0.5) * 0.5 + (nap - 0.5) * 0.4 + (fine - 0.5) * 0.16 + (stripes - 0.5) * 0.12
    img = ramp(t, [(0, "#285F25"), (0.5, "#367A2F"), (1, "#4D923D")])
    save("felt", img)
    # pass 5: brighter variant for the dark holes (H8 under the root arch, H9 inside the tree): same pattern, lifted
    # ~45% in value and a touch more yellow so it separates from the bark floor and the rails (pass 7: -5%)
    save("felt_bright", ramp(t, [(0, "#478F38"), (0.5, "#5EAE45"), (1, "#7BC657")]))
    # normal map from a height field: nap ridges + soft mottling (pass 7: about 2x the pass-4 strength)
    hgt = (nap - 0.5) * 1.0 + (lo - 0.5) * 0.6 + (fine - 0.5) * 0.25
    gx = (np.roll(hgt, -1, 1) - np.roll(hgt, 1, 1)) * 4.0
    gy = (np.roll(hgt, -1, 0) - np.roll(hgt, 1, 0)) * 4.0
    n = np.stack([-gx, gy, np.ones_like(gx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    save("felt_normal", n * 0.5 + 0.5)


def card_clump(name, seed, canopy, shadow, trunk="#4A2E1C"):
    """Pass 4 treeline CARD texture (RGBA, 1024x512, alpha-cut): a clump of 4-5 autumn trees + undergrowth, sunlit
    from the upper left, drawn as one silhouette. Used on crossed vertical quads (treeline_card_* props) beyond
    ~40-60 studs, where real 3D clumps cost 50x the triangles."""
    rnd = random.Random(seed)
    Wd, Hd = 1024, 512
    S = 2                                            # supersample for clean alpha edges
    img = Image.new("RGBA", (Wd * S, Hd * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    trees = []
    for k in range(7):
        cx = (0.08 + 0.14 * k + rnd.uniform(-0.03, 0.03)) * Wd
        top = rnd.uniform(0.02, 0.26) * Hd
        r = rnd.uniform(0.19, 0.26) * Hd
        trees.append((cx, top, r))
    for cx, top, r in trees:                          # trunks (mostly hidden by canopy + undergrowth)
        w = r * 0.13
        d.polygon([((cx - w) * S, Hd * 0.95 * S), ((cx + w) * S, Hd * 0.95 * S), ((cx + w * 0.5) * S, (top + r) * S),
                   ((cx - w * 0.5) * S, (top + r) * S)], fill=hexc_t(trunk))
    order = sorted(range(len(trees)), key=lambda i: -trees[i][1])
    for k in order:                                   # canopies: lumpy blobs, lit upper-left, back trees first
        cx, top, r = trees[k]
        col = canopy[k % len(canopy)]
        blobs = [(cx + rnd.uniform(-0.65, 0.65) * r, top + r * rnd.uniform(0.75, 1.6), r * rnd.uniform(0.5, 0.75))
                 for _ in range(10)] + [(cx, top + r * 0.8, r * 0.8)]
        for (bx, by, br) in blobs:
            d.ellipse(((bx - br) * S, (by - br) * S, (bx + br) * S, (by + br) * S), fill=hexc_t(shadow))
        for (bx, by, br) in blobs:
            o = br * 0.22
            d.ellipse(((bx - br) * S, (by - br) * S, (bx + br - o) * S, (by + br - o * 1.3) * S), fill=hexc_t(col))
        for _ in range(700):                          # small leaf speckles: light on the lit side, dark below
            a = rnd.uniform(0, math.tau)
            rr = r * math.sqrt(rnd.random()) * 1.15
            px, py = cx + math.cos(a) * rr, top + r * 1.15 + math.sin(a) * rr * 0.9
            lit = (px - cx) * 0.6 + (py - top - r * 1.15) < 0
            if lit:
                c = jitter(rnd.choice(canopy + ["#F6C64A"]), rnd, 0.15)
            elif rnd.random() < 0.5:
                c = hexc_t(shadow)[:3]
            else:
                continue
            sz = rnd.uniform(2, 4.5)
            d.ellipse(((px - sz) * S, (py - sz) * S, (px + sz) * S, (py + sz) * S), fill=c + (255,))
    for k in range(14):                               # undergrowth band
        bx = rnd.uniform(0.0, 1.0) * Wd
        br = rnd.uniform(0.08, 0.13) * Hd
        c = canopy[(k + 1) % len(canopy)]
        d.ellipse(((bx - br * 1.5) * S, (Hd - br * 1.6) * S, (bx + br * 1.5) * S, (Hd + br * 0.5) * S), fill=hexc_t(shadow))
        d.ellipse(((bx - br * 1.4) * S, (Hd - br * 1.6) * S, (bx + br * 1.2) * S, (Hd + br * 0.1) * S), fill=hexc_t(c))
    img = img.resize((Wd, Hd), Image.LANCZOS)
    a = np.asarray(img).astype(np.float32) / 255
    a[..., 3] = (a[..., 3] > 0.5).astype(np.float32)  # hard alpha cut (no sorting issues in Roblox)
    Image.fromarray((a * 255).astype(np.uint8), "RGBA").save(os.path.join(OUT, name + ".png"), optimize=True)
    print("[tex]", name)


def hexc_t(h):
    return tuple(int(v * 255) for v in hexc(h)) + (255,)


def paper_glow():
    """Pass 4 sky-lantern paper: warm glowing washi with bamboo ribs (vertical, 8 per tile) and fibres; brighter in
    the middle band where the flame lights it. Used as emissive ColorMap (Neon-ish SmoothPlastic + PointLight)."""
    fib = noise(70, beta=0.7, sx=1.0, sy=0.25)
    lo = noise(71, beta=1.8)
    y = np.arange(N)[:, None] / N
    band = np.exp(-((y - 0.62) / 0.3) ** 2)
    x = np.arange(N)[None, :] / N
    ribs = np.clip(1 - np.abs(((x * 8) % 1) - 0.5) * 2 / 0.08, 0, 1) ** 2
    t = 0.45 + band * 0.4 + (fib - 0.5) * 0.35 + (lo - 0.5) * 0.2 - ribs * 0.35
    img = ramp(t, [(0, "#B5501E"), (0.45, "#F08A3C"), (0.75, "#FFC266"), (1, "#FFE6A8")])
    save("paper_glow", img)


# ---------------------------------------------------------------------------- oak wood grain
def oak():
    warp = noise(3, beta=1.4, sx=6, sy=1)
    x = np.arange(N)[None, :] / N
    rings = 0.5 + 0.5 * np.sin(math.tau * (x * 9 + (warp - 0.5) * 3.0))
    fine = noise(4, beta=0.6, sx=12, sy=0.6)
    t = rings * 0.55 + fine * 0.45
    img = ramp(t, [(0, "#6B4224"), (0.45, "#8A5A33"), (0.8, "#A06C3E"), (1, "#B07A48")])
    # plank seams every 1/4 of the tile (tile = 4 studs -> 1-stud planks)
    for k in range(4):
        c = int(k * N / 4)
        img[:, max(c - 1, 0):c + 2] *= 0.62
    save("oak_wood", img)


def shingle():
    img = Image.new("RGB", (N, N))
    base = ramp(noise(5, beta=1.0, sx=8, sy=1), [(0, "#5E3522"), (0.5, "#7A4630"), (1, "#93583A")])
    img = Image.fromarray((base * 255).astype(np.uint8))
    rnd = random.Random(5)
    rows, cols = 8, 6
    def fn(d, dx, dy):
        for r in range(rows):
            for c in range(cols):
                x0 = c * N / cols + (N / cols / 2 if r % 2 else 0) + dx
                y0 = r * N / rows + dy
                d.line([(x0, y0), (x0, y0 + N / rows)], fill=(48, 28, 18), width=3)
            d.line([(dx, r * N / rows + dy), (N + dx, r * N / rows + dy)], fill=(40, 24, 16), width=5)
    wrap_draw(fn, img)
    a = np.asarray(img).astype(np.float32) / 255
    shade = np.tile(np.linspace(1.08, 0.82, N // rows)[:, None], (rows, N))[..., None]
    save("shingle", a * shade)


# ---------------------------------------------------------------------------- bark
def root_bark():
    furrow = noise(6, beta=1.2, sx=0.7, sy=10)
    ridges = np.clip(np.abs(furrow - 0.5) * 5, 0, 1)
    fine = noise(7, beta=0.5)
    t = 1 - ridges ** 0.6 * 0.8 + (fine - 0.5) * 0.3
    img = ramp(t, [(0, "#2E1C10"), (0.35, "#4A2E1A"), (0.7, "#5B3A22"), (1, "#7A5235")])
    save("root_bark", img)


def birch_bark():
    base = noise(8, beta=1.0, sx=0.6, sy=4)
    img = ramp(0.6 + (base - 0.5) * 0.5, [(0, "#CFC6B6"), (0.6, "#E9E2D3"), (1, "#F6F1E6")])
    pil = Image.fromarray((img * 255).astype(np.uint8))
    rnd = random.Random(8)
    def fn(d, dx, dy):
        rr = random.Random(9)
        for _ in range(70):
            x, y = rr.uniform(0, N), rr.uniform(0, N)
            w, h = rr.uniform(14, 60), rr.uniform(2, 6)
            d.ellipse([x - w / 2 + dx, y - h / 2 + dy, x + w / 2 + dx, y + h / 2 + dy], fill=(52, 42, 36))
        for _ in range(10):
            x, y = rr.uniform(0, N), rr.uniform(0, N)
            w, h = rr.uniform(40, 110), rr.uniform(10, 26)
            d.ellipse([x - w / 2 + dx, y - h / 2 + dy, x + w / 2 + dx, y + h / 2 + dy], fill=(120, 106, 92))
    wrap_draw(fn, pil)
    save("birch_bark", pil.filter(ImageFilter.GaussianBlur(0.8)))


# ---------------------------------------------------------------------------- stone
def voronoi(seed, n=36):
    rnd = np.random.default_rng(seed)
    pts = rnd.uniform(0, N, (n, 2))
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    d1 = np.full((N, N), 1e9, np.float32)
    d2 = np.full((N, N), 1e9, np.float32)
    cid = np.zeros((N, N), np.int32)
    for i, (px, py) in enumerate(pts):
        dx = np.abs(xx - px); dx = np.minimum(dx, N - dx)
        dy = np.abs(yy - py); dy = np.minimum(dy, N - dy)
        d = np.sqrt(dx * dx + dy * dy)
        m = d < d1
        d2 = np.where(m, d1, np.minimum(d2, d))
        cid = np.where(m, i, cid)
        d1 = np.where(m, d, d1)
    return d1, d2, cid, rnd.uniform(0, 1, n)


def slate():
    d1, d2, cid, tone = voronoi(10, 30)
    edge = np.clip((d2 - d1) / 6.0, 0, 1)
    t = 0.35 + tone[cid] * 0.35 + (noise(11, beta=1.3) - 0.5) * 0.6 + (noise(12, beta=0.4) - 0.5) * 0.25
    img = ramp(t, [(0, "#4E535C"), (0.45, "#6E7480"), (0.8, "#8A8C8E"), (1, "#9C968C")])
    img *= (0.55 + 0.45 * edge)[..., None]
    save("slate_stone", img)


def limestone():
    """Rail stone: 4 courses of blocks per tile (tile = 2 studs -> 0.5-stud courses, 1-stud blocks)."""
    t = 0.5 + (noise(13, beta=1.1) - 0.5) * 0.7 + (noise(14, beta=0.4) - 0.5) * 0.3
    img = ramp(t, [(0, "#968C7C"), (0.5, "#B8AFA0"), (1, "#D2CABA")])
    yy, xx = np.mgrid[0:N, 0:N]
    rows = 4
    rh = N // rows
    r = yy // rh
    xo = (xx + (r % 2) * (N // 4)) % (N // 2)
    mort = (yy % rh < 5) | (xo < 5)
    rnd = np.random.default_rng(15).uniform(0.88, 1.08, (rows, 4))
    blk = ((xx + (r % 2) * (N // 4)) % N) // (N // 2)
    img *= rnd[r, blk][..., None]
    img[mort] = hexc("#7D7466")
    save("limestone", img)


def moss():
    t = 0.5 + (noise(16, beta=1.5) - 0.5) * 0.9 + (noise(17, beta=0.2) - 0.5) * 0.5
    img = ramp(t, [(0, "#4F6E26"), (0.5, "#7A9A3A"), (1, "#A2BA52")])
    save("moss", img)


def plaster():
    t = 0.5 + (noise(18, beta=1.4) - 0.5) * 0.4 + (noise(19, beta=0.3) - 0.5) * 0.2
    save("plaster", ramp(t, [(0, "#E3D6BC"), (0.5, "#F4E9D2"), (1, "#FBF4E4")]))


def thatch():
    s = noise(20, beta=0.9, sx=0.5, sy=14)
    t = s * 0.8 + noise(21, beta=1.2) * 0.2
    img = ramp(t, [(0, "#8E6326"), (0.45, "#C9923E"), (1, "#E2B460")])
    rows = 8
    shade = np.tile(np.linspace(1.1, 0.75, N // rows)[:, None], (rows, N))
    save("thatch", img * shade[..., None])


# ---------------------------------------------------------------------------- leaves
def leaf_layer(seed, base_img, palette, count, size, kinds=("maple", "oval"), shadow=(40, 26, 16)):
    pil = Image.fromarray((base_img * 255).astype(np.uint8))
    rnd = random.Random(seed)
    leaves = [(rnd.uniform(0, N), rnd.uniform(0, N), rnd.uniform(*size), rnd.uniform(0, math.tau),
               rnd.choice(kinds), rnd.choice(palette), rnd.random()) for _ in range(count)]
    def fn(d, dx, dy):
        cr = random.Random(seed + 1)
        for (x, y, L, a, k, col, j) in leaves:
            if shadow:
                d.polygon(leaf_poly(x + dx + 2, y + dy + 3, L, L * 0.55, a, k), fill=shadow)
            c = jitter(col, random.Random(int(j * 1e6)), 0.16)
            d.polygon(leaf_poly(x + dx, y + dy, L, L * 0.55, a, k), fill=c)
            # midrib
            d.line([(x + dx, y + dy), (x + dx + math.cos(a) * L * 0.8, y + dy + math.sin(a) * L * 0.8)],
                   fill=tuple(int(v * 0.7) for v in c), width=1)
    wrap_draw(fn, pil)
    return pil


def leaf_litter():
    soil = ramp(noise(22, beta=1.4) * 0.8 + noise(23, beta=0.3) * 0.2,
                [(0, "#3B2A1C"), (0.5, "#5A4330"), (1, "#735638")])
    pil = leaf_layer(24, soil, ["#D2452A", "#E8862E", "#F2B632", "#B8532B", "#8C5A2E", "#C96A2C"], 900, (7, 15))
    save("leaf_litter", pil.filter(ImageFilter.GaussianBlur(0.5)))


def foliage(name, seed, base_stops, palette, shadow):
    shade = noise(seed, beta=1.6)
    base = ramp(shade, base_stops)
    pil = leaf_layer(seed + 1, base, palette, 2200, (6, 12), kinds=("maple", "maple", "oval"), shadow=shadow)
    pil = pil.filter(ImageFilter.GaussianBlur(0.6))
    a = np.asarray(pil).astype(np.float32) / 255
    a *= (0.88 + 0.22 * noise(seed + 2, beta=1.8))[..., None]  # soft clumpy light/shadow
    save(name, a)


def heartwood():
    """Warm interior of the giant hollow tree (pass 3): honey-orange vertical grain with darker furrows."""
    grain = noise(60, beta=1.3, sx=0.6, sy=9)
    furrow = np.clip(np.abs(noise(61, beta=1.2, sx=0.8, sy=12) - 0.5) * 4, 0, 1)
    fine = noise(62, beta=0.6)
    t = grain * 0.55 + (1 - furrow ** 0.7) * 0.3 + (fine - 0.5) * 0.25
    img = ramp(t, [(0, "#5E3418"), (0.35, "#8E5228"), (0.7, "#B9783F"), (1, "#D69A55")])
    save("heartwood", img)


def glow_emissive():
    """Pass 8: H8 glow boost. Emissive maps for the Neon glow materials (Firefly specks / teleport rings, ShroomGlow
    caps): a bright colour map with a soft hot core (SurfaceAppearance ColorMap) and a white emissive mask
    (SurfaceAppearance EmissiveMaskContent; EmissiveStrength / EmissiveTint in manifest.emissive)."""
    n = 256
    yy, xx = np.mgrid[0:n, 0:n] / (n - 1)
    core = np.clip(1 - np.hypot(xx - 0.5, yy - 0.5) * 1.6, 0, 1) ** 1.5
    for name, hx in (("firefly_emissive", "#D8FF6A"), ("shroomglow_emissive", "#7FE3D0")):
        c = hexc(hx)
        img = np.clip(c[None, None] * (0.92 + 0.08 * core[..., None]) + core[..., None] * 0.18, 0, 1)
        Image.fromarray((img * 255).astype(np.uint8)).save(os.path.join(OUT, name + ".png"))
    Image.fromarray(np.full((64, 64), 255, np.uint8)).save(os.path.join(OUT, "glow_emissive_mask.png"))


if __name__ == "__main__":
    glow_emissive()
    heartwood()
    felt(); paper_glow()
    card_clump("card_red", 81, ["#D2452A", "#E8862E", "#C23A24"], "#7E2618")
    card_clump("card_gold", 82, ["#F2B632", "#E8862E", "#E8A42A"], "#8E5A1A")
    oak(); shingle(); root_bark(); birch_bark(); slate(); limestone(); moss(); plaster(); thatch()
    leaf_litter()
    foliage("foliage_red", 30, [(0, "#8E2A1A"), (1, "#B83A22")], ["#D2452A", "#C23A24", "#E0573A", "#E8862E", "#D2452A"],
            (120, 36, 22))
    foliage("foliage_orange", 40, [(0, "#A0521C"), (1, "#C86A22")], ["#E8862E", "#F09A3A", "#D8702A", "#F2B632", "#E8862E"],
            (150, 74, 28))
    foliage("foliage_gold", 50, [(0, "#A87A1C"), (1, "#D49C2A")], ["#F2B632", "#F6C64A", "#E8A42A", "#E8862E", "#F2B632"],
            (160, 112, 34))
