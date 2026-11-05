#!/usr/bin/env python3
"""Club-setup VR UI — parchment/brass card + amber icons (matches wrist/)."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import random, math, os

OUT = os.path.dirname(os.path.abspath(__file__))
os.chdir(OUT)
random.seed(11)
S = 4

def ss(w, h):
    return Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))

def down(im, w, h):
    return im.resize((w, h), Image.LANCZOS)

def rr(d, box, r, **k):
    d.rounded_rectangle([c * S for c in box], r * S, **k)

def noise(w, h, scale, seed):
    random.seed(seed)
    n = Image.new("L", (w // scale + 2, h // scale + 2))
    n.putdata([random.randint(0, 255) for _ in range(n.width * n.height)])
    return n.resize((w, h), Image.BICUBIC)

BRASS_D = (122, 78, 30)
BRASS_L = (246, 206, 120)
PARCH = (250, 232, 198)
PARCH_D = (228, 196, 148)
DARK = (74, 40, 18, 255)
AMB = (232, 140, 40, 255)
GOLD = (250, 196, 70, 255)
CREAM = (255, 240, 210, 255)
TEXT_DK = (59, 36, 18)  # #3B2412
LAB = (156, 82, 24)

# ── howto_card_bg 1024×784, 3 empty panels ─────────────────────────────
W, H = 1024, 784
mask = ss(W, H)
d = ImageDraw.Draw(mask)
rr(d, (8, 8, W - 8, H - 8), 56, fill=(255, 255, 255, 255))
outer = down(mask, W, H).split()[3]
mask = ss(W, H)
d = ImageDraw.Draw(mask)
rr(d, (42, 42, W - 42, H - 42), 34, fill=(255, 255, 255, 255))
inner = down(mask, W, H).split()[3]

br = Image.new("RGB", (W, H))
bd = ImageDraw.Draw(br)
for y in range(H):
    t = y / H
    k = 0.5 + 0.5 * math.cos(t * math.pi * 2.2)
    bd.line(
        [(0, y), (W, y)],
        fill=tuple(int(BRASS_D[i] + (BRASS_L[i] - BRASS_D[i]) * (0.35 + 0.5 * k)) for i in range(3)),
    )
br = ImageChops.multiply(
    br, Image.merge("RGB", [noise(W, H, 3, 1).point(lambda v: 220 + v // 8)] * 3)
)
card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
card.paste(br, (0, 0), outer)
ring = ss(W, H)
d = ImageDraw.Draw(ring)
rr(d, (14, 14, W - 14, H - 14), 50, outline=(255, 236, 170, 200), width=5)
rr(d, (36, 36, W - 36, H - 36), 38, outline=(80, 46, 14, 255), width=8)
card = Image.alpha_composite(card, down(ring, W, H))
rv = ss(W, H)
d = ImageDraw.Draw(rv)
for x, y in [
    (25, 25), (W - 25, 25), (25, H - 25), (W - 25, H - 25),
    (W // 2, 24), (W // 2, H - 24), (24, H // 2), (W - 24, H // 2),
]:
    d.ellipse([(x - 9) * S, (y - 9) * S, (x + 9) * S, (y + 9) * S], fill=(92, 56, 18, 255))
    d.ellipse([(x - 7) * S, (y - 8) * S, (x + 5) * S, (y + 4) * S], fill=(255, 226, 150, 255))
card = Image.alpha_composite(card, down(rv, W, H))

p = Image.new("RGB", (W, H), PARCH)
n1 = noise(W, H, 40, 2)
n2 = noise(W, H, 6, 3)
pd = Image.new("RGB", (W, H), PARCH_D)
p = Image.composite(pd, p, Image.blend(n1, n2, 0.3).point(lambda v: max(0, v - 90)))
vg = Image.new("L", (W, H), 0)
ImageDraw.Draw(vg).rounded_rectangle([60, 60, W - 60, H - 60], 60, fill=255)
vg = vg.filter(ImageFilter.GaussianBlur(40))
p = Image.composite(p, Image.new("RGB", (W, H), (214, 170, 112)), vg)
card.paste(p, (0, 0), inner)

MARGIN_X, MARGIN_TOP, MARGIN_BOT, GAP = 72, 68, 68, 18
PANEL_H = (H - MARGIN_TOP - MARGIN_BOT - 2 * GAP) // 3
zones = {}
Z = ss(W, H)
d = ImageDraw.Draw(Z)
for i, name in enumerate(["step1", "step2", "step3"]):
    y0 = MARGIN_TOP + i * (PANEL_H + GAP)
    y1 = y0 + PANEL_H
    x0, x1 = MARGIN_X, W - MARGIN_X
    zones[name] = (x0, y0, x1, y1)
    rr(d, (x0, y0, x1, y1), 26, fill=(176, 112, 52, 40), outline=(150, 92, 40, 150), width=4)
    cy = (y0 + y1) // 2
    cx = x0 + 110
    r = 78
    d.ellipse(
        [(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S],
        fill=(255, 244, 220, 170),
        outline=(176, 112, 52, 170),
        width=4 * S,
    )
    zones[name + "_icon"] = (cx - r, cy - r, cx + r, cy + r)
card = Image.alpha_composite(card, down(Z, W, H))
card.save("howto_card_bg.png")

# ── icons 256×256 ──────────────────────────────────────────────────────
ICON, IS = 256, 4

def icon_canvas():
    return Image.new("RGBA", (ICON * IS, ICON * IS), (0, 0, 0, 0))

def add_outline(im, thickness=9):
    a = im.split()[3]
    for _ in range(max(1, thickness // 3)):
        a = a.filter(ImageFilter.MaxFilter(5))
    halo = Image.new("RGBA", im.size, DARK)
    halo.putalpha(a)
    return Image.alpha_composite(halo, im)

def P(pts):
    return [(x * IS, y * IS) for x, y in pts]

def finish_icon(im, name):
    out = add_outline(im.resize((ICON, ICON), Image.LANCZOS), 9)
    out.save(f"{name}.png")
    return out

im = icon_canvas()
d = ImageDraw.Draw(im)
d.rounded_rectangle([36 * IS, 214 * IS, 220 * IS, 228 * IS], 5 * IS, fill=GOLD)
d.ellipse([70 * IS, 200 * IS, 100 * IS, 222 * IS], fill=CREAM)
d.ellipse([148 * IS, 200 * IS, 178 * IS, 222 * IS], fill=CREAM)
d.line(P([(92, 130), (85, 205)]), fill=CREAM, width=16 * IS)
d.line(P([(130, 130), (163, 205)]), fill=CREAM, width=16 * IS)
d.polygon(P([(88, 78), (148, 70), (155, 135), (80, 140)]), fill=AMB)
d.ellipse([100 * IS, 28 * IS, 148 * IS, 76 * IS], fill=CREAM)
d.line(P([(95, 100), (72, 160)]), fill=CREAM, width=14 * IS)
d.line(P([(145, 95), (95, 165)]), fill=CREAM, width=14 * IS)
d.line(P([(84, 158), (188, 214)]), fill=CREAM, width=11 * IS)
d.rounded_rectangle([168 * IS, 200 * IS, 222 * IS, 222 * IS], 9 * IS, fill=GOLD)
d.ellipse([210 * IS, 186 * IS, 236 * IS, 212 * IS], fill=CREAM)
icon_stance = finish_icon(im, "step1_stance")

im = icon_canvas()
d = ImageDraw.Draw(im)
d.rounded_rectangle([48 * IS, 138 * IS, 208 * IS, 222 * IS], 30 * IS, fill=CREAM)
d.rounded_rectangle([112 * IS, 96 * IS, 144 * IS, 165 * IS], 10 * IS, fill=GOLD)
d.ellipse([84 * IS, 40 * IS, 172 * IS, 128 * IS], fill=AMB)
d.ellipse([106 * IS, 62 * IS, 150 * IS, 106 * IS], fill=GOLD)
d.polygon(P([(192, 78), (230, 104), (192, 130)]), fill=GOLD)
d.polygon(P([(64, 78), (26, 104), (64, 130)]), fill=GOLD)
d.polygon(P([(104, 22), (128, 0), (152, 22)]), fill=GOLD)
d.polygon(P([(104, 234), (128, 256), (152, 234)]), fill=GOLD)
icon_stick = finish_icon(im, "step2_stick")

im = icon_canvas()
d = ImageDraw.Draw(im)
d.rounded_rectangle([56 * IS, 40 * IS, 168 * IS, 190 * IS], 28 * IS, fill=CREAM)
d.rounded_rectangle([76 * IS, 150 * IS, 148 * IS, 236 * IS], 22 * IS, fill=GOLD)
d.polygon(P([(56, 85), (14, 110), (14, 165), (56, 175), (56, 155), (34, 140), (34, 125), (56, 110)]), fill=AMB)
d.polygon(P([(56, 100), (28, 120), (28, 150), (56, 160)]), fill=GOLD)
d.line(P([(150, 100), (182, 140), (240, 55)]), fill=AMB, width=20 * IS)
icon_trigger = finish_icon(im, "step3_trigger")

im = icon_canvas()
d = ImageDraw.Draw(im)
cx, cy, r = 128.0, 128.0, 82.0
pts = []
for i in range(90):
    a = math.radians(50 + i * (270 / 89))
    pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
for x, y in pts:
    d.ellipse([(x - 16) * IS, (y - 16) * IS, (x + 16) * IS, (y + 16) * IS], fill=GOLD)
for x, y in pts:
    d.ellipse([(x - 7) * IS, (y - 7) * IS, (x + 7) * IS, (y + 7) * IS], fill=CREAM)
end_a = math.radians(50 + 270)
ex = cx + r * math.cos(end_a)
ey = cy + r * math.sin(end_a)
tx, ty = -math.sin(end_a), math.cos(end_a)
nx, ny = math.cos(end_a), math.sin(end_a)
tip = (ex + tx * 32, ey + ty * 32)
left = (ex - tx * 6 + nx * 24, ey - ty * 6 + ny * 24)
right = (ex - tx * 6 - nx * 24, ey - ty * 6 - ny * 24)
d.polygon(P([tip, left, right]), fill=AMB)
icon_reset = finish_icon(im, "icon_reset")

# ── ground_marker ──────────────────────────────────────────────────────
G = 256
im = Image.new("RGBA", (G, G), (0, 0, 0, 0))
glow = Image.new("L", (G, G), 0)
gd = ImageDraw.Draw(glow)
for rr_ in range(120, 68, -1):
    t = (120 - rr_) / 52
    a = int(100 * (1 - t) ** 1.3)
    gd.ellipse([G // 2 - rr_, G // 2 - rr_, G // 2 + rr_, G // 2 + rr_], outline=a, width=2)
glow = glow.filter(ImageFilter.GaussianBlur(7))
layer = Image.new("RGBA", (G, G), (255, 170, 50, 0))
layer.putalpha(glow)
im = Image.alpha_composite(im, layer)
d = ImageDraw.Draw(im)
cx = cy = G // 2
d.ellipse([cx - 100, cy - 100, cx + 100, cy + 100], outline=(74, 40, 18, 220), width=5)
d.ellipse([cx - 96, cy - 96, cx + 96, cy + 96], outline=(250, 196, 70, 255), width=11)
d.ellipse([cx - 86, cy - 86, cx + 86, cy + 86], outline=(232, 140, 40, 255), width=7)
d.ellipse([cx - 76, cy - 76, cx + 76, cy + 76], outline=(255, 240, 210, 230), width=3)
gap, arm = 20, 72
d.rounded_rectangle([cx - arm, cy - 4, cx - gap, cy + 4], 2, fill=AMB)
d.rounded_rectangle([cx + gap, cy - 4, cx + arm, cy + 4], 2, fill=AMB)
d.rounded_rectangle([cx - 4, cy - arm, cx + 4, cy - gap], 2, fill=AMB)
d.rounded_rectangle([cx - 4, cy + gap, cx + 4, cy + arm], 2, fill=AMB)
d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=GOLD)
d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=CREAM)
im.save("ground_marker.png")
marker = im

# ── mock ───────────────────────────────────────────────────────────────
F = "/usr/share/fonts/truetype/sand-box/google/Fredoka/Fredoka-VariableFont_wdth,wght.ttf"

def font(sz):
    f = ImageFont.truetype(F, sz)
    try:
        f.set_variation_by_axes([100.0, 700.0])
    except Exception:
        try:
            f.set_variation_by_name("Bold")
        except Exception:
            pass
    return f

def wrap_text(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

m = card.copy()
d = ImageDraw.Draw(m)
f56, f40 = font(56), font(40)
for name, text, ic in [
    ("step1", "STAND LIKE YOU'RE PUTTING", icon_stance),
    ("step2", "NUDGE THE CLUB HEAD WITH THE STICK", icon_stick),
    ("step3", "PULL TRIGGER TO SAVE", icon_trigger),
]:
    x0, y0, x1, y1 = zones[name]
    ix0, iy0, ix1, iy1 = zones[name + "_icon"]
    ic_sz = 136
    ix = (ix0 + ix1) // 2 - ic_sz // 2
    iy = (iy0 + iy1) // 2 - ic_sz // 2
    m.alpha_composite(ic.resize((ic_sz, ic_sz), Image.LANCZOS), (ix, iy))
    tx = ix1 + 24
    max_w = x1 - tx - 24
    lines = wrap_text(d, text, f56, max_w)
    line_h = 62
    block_h = len(lines) * line_h
    ty = (y0 + y1) // 2 - block_h // 2 + line_h // 2
    for li, line in enumerate(lines):
        d.text((tx, ty + li * line_h), line, font=f56, fill=TEXT_DK, anchor="lm")

fx = zones["step3"][2] - 28
fy = zones["step3"][3] - 40
m.alpha_composite(icon_reset.resize((44, 44), Image.LANCZOS), (fx - 170, fy - 22))
d.text((fx - 116, fy), "B: reset", font=f40, fill=LAB, anchor="lm")
m.save("howto_mock.png")

sh = Image.new("RGB", (1400, 1100), (40, 28, 22))
sd = ImageDraw.Draw(sh)
mr = m.resize((700, 536), Image.LANCZOS)
sh.paste(mr, (30, 30), mr)
cr = card.resize((350, 268), Image.LANCZOS)
sh.paste(cr, (760, 30), cr)
sd.text((760, 310), "howto_card_bg (empty)", font=font(22), fill=(250, 220, 170))
for i, (n, ic) in enumerate([
    ("step1_stance", icon_stance),
    ("step2_stick", icon_stick),
    ("step3_trigger", icon_trigger),
    ("icon_reset", icon_reset),
    ("ground_marker", marker),
]):
    x = 40 + i * 260
    sh.paste(ic, (x, 620), ic)
    sd.text((x, 900), n, font=font(20), fill=(250, 220, 170))
sh.save("club_setup_sheet.jpg", quality=92)
print("zones", {k: v for k, v in zones.items() if not k.endswith("_icon")})
print("done")
