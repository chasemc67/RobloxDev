#!/usr/bin/env python3
"""Bug-recorder VR UI — parchment/brass card + amber icons (matches club-setup/)."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import random, math, os

OUT = os.path.dirname(os.path.abspath(__file__))
os.chdir(OUT)
random.seed(42)
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
STROKE = (255, 244, 220, 255)  # #FFF4DC
TEXT_DK = (59, 36, 18)  # #3B2412
LAB = (156, 82, 24)
RED = (220, 48, 48, 255)
RED_DK = (140, 24, 24, 255)
RED_LT = (255, 120, 100, 255)

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

def add_outline(im, thickness=9, color=DARK):
    a = im.split()[3]
    for _ in range(max(1, thickness // 3)):
        a = a.filter(ImageFilter.MaxFilter(5))
    halo = Image.new("RGBA", im.size, color)
    halo.putalpha(a)
    return Image.alpha_composite(halo, im)

def add_cream_stroke(im, thickness=2):
    """2px #FFF4DC stroke around opaque pixels, then dark outline outside."""
    # cream stroke
    a = im.split()[3]
    for _ in range(max(1, thickness)):
        a = a.filter(ImageFilter.MaxFilter(3))
    cream = Image.new("RGBA", im.size, STROKE)
    cream.putalpha(a)
    # dark outer
    a2 = cream.split()[3]
    for _ in range(2):
        a2 = a2.filter(ImageFilter.MaxFilter(5))
    dark = Image.new("RGBA", im.size, DARK)
    dark.putalpha(a2)
    return Image.alpha_composite(Image.alpha_composite(dark, cream), im)

def P(pts, scale):
    return [(x * scale, y * scale) for x, y in pts]

def finish_icon(im, name, size, outline_t=9, cream_stroke=True):
    resized = im.resize((size, size), Image.LANCZOS)
    if cream_stroke:
        out = add_cream_stroke(resized, 2)
    else:
        out = add_outline(resized, outline_t)
    out.save(f"{name}.png")
    return out

# ═══════════════════════════════════════════════════════════════════════
# Shared parchment+brass card builder
# ═══════════════════════════════════════════════════════════════════════
def make_brass_parchment_card(W, H, seed=1):
    mask = ss(W, H)
    d = ImageDraw.Draw(mask)
    rr(d, (8, 8, W - 8, H - 8), 56 if min(W, H) > 400 else 28, fill=(255, 255, 255, 255))
    outer = down(mask, W, H).split()[3]
    mask = ss(W, H)
    d = ImageDraw.Draw(mask)
    rr(d, (42, 42, W - 42, H - 42), 34 if min(W, H) > 400 else 18, fill=(255, 255, 255, 255))
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
        br, Image.merge("RGB", [noise(W, H, 3, seed).point(lambda v: 220 + v // 8)] * 3)
    )
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    card.paste(br, (0, 0), outer)
    ring = ss(W, H)
    d = ImageDraw.Draw(ring)
    r_out = 50 if min(W, H) > 400 else 24
    r_in = 38 if min(W, H) > 400 else 18
    rr(d, (14, 14, W - 14, H - 14), r_out, outline=(255, 236, 170, 200), width=5)
    rr(d, (36, 36, W - 36, H - 36), r_in, outline=(80, 46, 14, 255), width=8)
    card = Image.alpha_composite(card, down(ring, W, H))

    # rivets
    rv = ss(W, H)
    d = ImageDraw.Draw(rv)
    rivet_pts = [
        (25, 25), (W - 25, 25), (25, H - 25), (W - 25, H - 25),
        (W // 2, 24), (W // 2, H - 24), (24, H // 2), (W - 24, H // 2),
    ]
    # skip mid-side rivets on short cards
    if min(W, H) < 400:
        rivet_pts = [(25, 25), (W - 25, 25), (25, H - 25), (W - 25, H - 25)]
    for x, y in rivet_pts:
        d.ellipse([(x - 9) * S, (y - 9) * S, (x + 9) * S, (y + 9) * S], fill=(92, 56, 18, 255))
        d.ellipse([(x - 7) * S, (y - 8) * S, (x + 5) * S, (y + 4) * S], fill=(255, 226, 150, 255))
    card = Image.alpha_composite(card, down(rv, W, H))

    p = Image.new("RGB", (W, H), PARCH)
    n1 = noise(W, H, 40, seed + 1)
    n2 = noise(W, H, 6, seed + 2)
    pd = Image.new("RGB", (W, H), PARCH_D)
    p = Image.composite(pd, p, Image.blend(n1, n2, 0.3).point(lambda v: max(0, v - 90)))
    vg = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vg).rounded_rectangle(
        [60 if W > 400 else 30, 60 if H > 400 else 30, W - (60 if W > 400 else 30), H - (60 if H > 400 else 30)],
        60 if min(W, H) > 400 else 20,
        fill=255,
    )
    vg = vg.filter(ImageFilter.GaussianBlur(40 if min(W, H) > 400 else 16))
    p = Image.composite(p, Image.new("RGB", (W, H), (214, 170, 112)), vg)
    card.paste(p, (0, 0), inner)
    return card

# ═══════════════════════════════════════════════════════════════════════
# 1. Bug button icon 512×512
# ═══════════════════════════════════════════════════════════════════════
ICON_BUG = 512
IS = 4

def icon_canvas(size=ICON_BUG):
    return Image.new("RGBA", (size * IS, size * IS), (0, 0, 0, 0))

im = icon_canvas()
d = ImageDraw.Draw(im)
# rounded square badge
d.rounded_rectangle([48 * IS, 48 * IS, 464 * IS, 464 * IS], 72 * IS, fill=AMB)
d.rounded_rectangle([72 * IS, 72 * IS, 440 * IS, 440 * IS], 56 * IS, fill=GOLD)
# bug body
cx, cy = 256, 250
d.ellipse([(cx - 70) * IS, (cy - 55) * IS, (cx + 70) * IS, (cy + 75) * IS], fill=CREAM)
# head
d.ellipse([(cx - 48) * IS, (cy - 110) * IS, (cx + 48) * IS, (cy - 30) * IS], fill=CREAM)
# antennae
d.line(P([(cx - 28, cy - 95), (cx - 70, cy - 160)], IS), fill=CREAM, width=14 * IS)
d.line(P([(cx + 28, cy - 95), (cx + 70, cy - 160)], IS), fill=CREAM, width=14 * IS)
d.ellipse([(cx - 82) * IS, (cy - 172) * IS, (cx - 58) * IS, (cy - 148) * IS], fill=GOLD)
d.ellipse([(cx + 58) * IS, (cy - 172) * IS, (cx + 82) * IS, (cy - 148) * IS], fill=GOLD)
# eyes
d.ellipse([(cx - 30) * IS, (cy - 85) * IS, (cx - 8) * IS, (cy - 55) * IS], fill=DARK)
d.ellipse([(cx + 8) * IS, (cy - 85) * IS, (cx + 30) * IS, (cy - 55) * IS], fill=DARK)
# legs
for dx, dy0, dy1 in [(-95, -10, 50), (-110, 20, 90), (-95, 55, 125),
                      (95, -10, 50), (110, 20, 90), (95, 55, 125)]:
    d.line(P([(cx + dx * 0.35, cy + dy0), (cx + dx, cy + dy1)], IS), fill=CREAM, width=12 * IS)
# wing line
d.line(P([(cx, cy - 20), (cx, cy + 60)], IS), fill=GOLD, width=8 * IS)
# exclamation accent (report feel)
d.rounded_rectangle([(cx + 90) * IS, (cy - 140) * IS, (cx + 130) * IS, (cy - 40) * IS], 12 * IS, fill=RED)
d.ellipse([(cx + 92) * IS, (cy - 20) * IS, (cx + 128) * IS, (cy + 16) * IS], fill=RED)
bug_btn = finish_icon(im, "icon_bug_button", ICON_BUG, cream_stroke=True)
print("icon_bug_button", ICON_BUG)

# ═══════════════════════════════════════════════════════════════════════
# 2. Recording indicator — red pulse dot + REC badge
# ═══════════════════════════════════════════════════════════════════════
# Pulsing red dot (256, for Billboard/overlay)
REC_DOT = 256
im = Image.new("RGBA", (REC_DOT * IS, REC_DOT * IS), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
cx = cy = REC_DOT // 2
# outer glow rings
for r, a in [(110, 40), (90, 80), (70, 140)]:
    d.ellipse([(cx - r) * IS, (cy - r) * IS, (cx + r) * IS, (cy + r) * IS], fill=(220, 48, 48, a))
d.ellipse([(cx - 52) * IS, (cy - 52) * IS, (cx + 52) * IS, (cy + 52) * IS], fill=RED)
d.ellipse([(cx - 36) * IS, (cy - 40) * IS, (cx + 20) * IS, (cy + 16) * IS], fill=RED_LT)
rec_dot = im.resize((REC_DOT, REC_DOT), Image.LANCZOS)
# dark outline on solid core only — keep glow soft
core = Image.new("RGBA", (REC_DOT, REC_DOT), (0, 0, 0, 0))
cd = ImageDraw.Draw(core)
cd.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=RED)
cd.ellipse([cx - 36, cy - 40, cx + 20, cy + 16], fill=RED_LT)
core = add_outline(core, 6)
rec_dot = Image.alpha_composite(rec_dot, core)
rec_dot.save("rec_dot.png")
print("rec_dot", REC_DOT)

# REC 5s badge (512×160)
BW, BH = 512, 160
im = ss(BW, BH)
d = ImageDraw.Draw(im)
# badge body
rr(d, (8, 8, BW - 8, BH - 8), 40, fill=(60, 28, 22, 240))
rr(d, (16, 16, BW - 16, BH - 16), 34, fill=(120, 40, 36, 230))
# cream stroke rim
rr(d, (12, 12, BW - 12, BH - 12), 38, outline=STROKE[:3] + (255,), width=4)
# red live dot
dot_cx, dot_cy = 70, BH // 2
d.ellipse([(dot_cx - 28) * S, (dot_cy - 28) * S, (dot_cx + 28) * S, (dot_cy + 28) * S], fill=RED)
d.ellipse([(dot_cx - 18) * S, (dot_cy - 22) * S, (dot_cx + 10) * S, (dot_cy + 6) * S], fill=RED_LT)
badge = down(im, BW, BH)
# text
td = ImageDraw.Draw(badge)
f64 = font(64)
td.text((120, BH // 2), "REC  5s", font=f64, fill=(255, 244, 220), anchor="lm")
# dark text shadow via second pass outline feel
badge.save("rec_badge.png")
print("rec_badge", BW, BH)

# Combined recording indicator strip (640×180) for convenience
CW, CH = 640, 180
combo = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
combo.alpha_composite(rec_dot.resize((120, 120), Image.LANCZOS), (20, 30))
combo.alpha_composite(badge.resize((480, 150), Image.LANCZOS), (140, 15))
combo.save("rec_indicator.png")
print("rec_indicator", CW, CH)

# ═══════════════════════════════════════════════════════════════════════
# 3. Five tag icons 256×256
# ═══════════════════════════════════════════════════════════════════════
TAG = 256
TS = 4

def tag_canvas():
    return Image.new("RGBA", (TAG * TS, TAG * TS), (0, 0, 0, 0))

def finish_tag(im, name):
    return finish_icon(im, name, TAG, cream_stroke=True)

# physics — ball with motion arcs
im = tag_canvas()
d = ImageDraw.Draw(im)
d.ellipse([60 * TS, 70 * TS, 196 * TS, 206 * TS], fill=CREAM)
d.ellipse([80 * TS, 85 * TS, 140 * TS, 145 * TS], fill=GOLD)
# dimples
for px, py in [(100, 160), (150, 150), (130, 180), (160, 120)]:
    d.ellipse([(px - 8) * TS, (py - 8) * TS, (px + 8) * TS, (py + 8) * TS], fill=AMB)
# motion arcs
for i, r in enumerate([90, 110, 130]):
    bbox = [(128 - r) * TS, (40 - i * 8) * TS, (128 + r) * TS, (100 - i * 8) * TS]
    d.arc(bbox, 200, 340, fill=GOLD, width=10 * TS)
tag_physics = finish_tag(im, "tag_physics")

# club — putter head + shaft
im = tag_canvas()
d = ImageDraw.Draw(im)
d.line(P([(90, 30), (150, 170)], TS), fill=CREAM, width=18 * TS)
d.line(P([(90, 30), (150, 170)], TS), fill=GOLD, width=10 * TS)
d.rounded_rectangle([70 * TS, 160 * TS, 210 * TS, 220 * TS], 14 * TS, fill=AMB)
d.rounded_rectangle([80 * TS, 170 * TS, 200 * TS, 210 * TS], 10 * TS, fill=GOLD)
d.ellipse([175 * TS, 175 * TS, 205 * TS, 205 * TS], fill=CREAM)  # ball near head
tag_club = finish_tag(im, "tag_club")

# camera — viewfinder / lens
im = tag_canvas()
d = ImageDraw.Draw(im)
d.rounded_rectangle([36 * TS, 70 * TS, 200 * TS, 190 * TS], 22 * TS, fill=CREAM)
d.rounded_rectangle([48 * TS, 82 * TS, 188 * TS, 178 * TS], 14 * TS, fill=AMB)
d.ellipse([78 * TS, 95 * TS, 158 * TS, 175 * TS], fill=GOLD)
d.ellipse([98 * TS, 115 * TS, 138 * TS, 155 * TS], fill=CREAM)
d.ellipse([108 * TS, 122 * TS, 122 * TS, 136 * TS], fill=DARK)
# flash / viewfinder bump
d.rounded_rectangle([150 * TS, 48 * TS, 190 * TS, 78 * TS], 8 * TS, fill=GOLD)
d.polygon(P([(200, 100), (240, 80), (240, 180), (200, 160)], TS), fill=GOLD)
tag_camera = finish_tag(im, "tag_camera")

# UI — window / panel with corner brackets
im = tag_canvas()
d = ImageDraw.Draw(im)
d.rounded_rectangle([48 * TS, 48 * TS, 208 * TS, 208 * TS], 20 * TS, fill=CREAM)
d.rounded_rectangle([62 * TS, 62 * TS, 194 * TS, 194 * TS], 14 * TS, fill=GOLD)
# title bar
d.rounded_rectangle([62 * TS, 62 * TS, 194 * TS, 100 * TS], 10 * TS, fill=AMB)
# dots
for i, col in enumerate([(220, 80, 60, 255), GOLD, (80, 180, 80, 255)]):
    x = 80 + i * 28
    d.ellipse([x * TS, 72 * TS, (x + 16) * TS, 88 * TS], fill=col)
# content lines
d.rounded_rectangle([78 * TS, 118 * TS, 178 * TS, 132 * TS], 4 * TS, fill=CREAM)
d.rounded_rectangle([78 * TS, 146 * TS, 160 * TS, 160 * TS], 4 * TS, fill=CREAM)
d.rounded_rectangle([78 * TS, 174 * TS, 148 * TS, 188 * TS], 4 * TS, fill=CREAM)
tag_ui = finish_tag(im, "tag_ui")

# other — ellipsis / question mark in circle
im = tag_canvas()
d = ImageDraw.Draw(im)
d.ellipse([40 * TS, 40 * TS, 216 * TS, 216 * TS], fill=AMB)
d.ellipse([58 * TS, 58 * TS, 198 * TS, 198 * TS], fill=GOLD)
# three dots
for i, x in enumerate([88, 128, 168]):
    d.ellipse([(x - 16) * TS, (118) * TS, (x + 16) * TS, (150) * TS], fill=CREAM)
tag_other = finish_tag(im, "tag_other")
print("tags done")

# ═══════════════════════════════════════════════════════════════════════
# 4. Report saved toast
# ═══════════════════════════════════════════════════════════════════════
TW, TH = 720, 160
toast = make_brass_parchment_card(TW, TH, seed=20)
# soften for toast — already brass+parchment
td = ImageDraw.Draw(toast)
# check circle
chk = Image.new("RGBA", (TW, TH), (0, 0, 0, 0))
cd = ImageDraw.Draw(chk)
cx, cy, r = 90, TH // 2, 42
cd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 140, 70, 255))
cd.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6], fill=(90, 180, 90, 255))
# check mark
cd.line([(cx - 18, cy + 2), (cx - 4, cy + 16), (cx + 22, cy - 14)], fill=CREAM, width=10)
toast = Image.alpha_composite(toast, add_outline(chk, 4))
td = ImageDraw.Draw(toast)
f56 = font(56)
# cream stroke simulation: draw cream then dark offset then main
for ox, oy, col in [(2, 2, STROKE[:3]), (-1, -1, STROKE[:3]), (0, 0, TEXT_DK)]:
    td.text((160 + ox, TH // 2 + oy), "REPORT SAVED", font=f56, fill=col, anchor="lm")
toast.save("toast_report_saved.png")
print("toast", TW, TH)

# ═══════════════════════════════════════════════════════════════════════
# 5. My reports list card 1024×784 with empty row slots
# ═══════════════════════════════════════════════════════════════════════
W, H = 1024, 784
card = make_brass_parchment_card(W, H, seed=7)

MARGIN_X, MARGIN_TOP, MARGIN_BOT, GAP = 72, 100, 60, 16
# header strip + 4 rows
HEADER_H = 72
ROW_H = (H - MARGIN_TOP - MARGIN_BOT - HEADER_H - 3 * GAP) // 4
zones = {}
Z = ss(W, H)
d = ImageDraw.Draw(Z)

# header band
hx0, hy0 = MARGIN_X, MARGIN_TOP - 20
hx1, hy1 = W - MARGIN_X, hy0 + HEADER_H
rr(d, (hx0, hy0, hx1, hy1), 20, fill=(176, 112, 52, 50), outline=(150, 92, 40, 160), width=4)
zones["header"] = (hx0, hy0, hx1, hy1)

for i in range(4):
    y0 = hy1 + GAP + i * (ROW_H + GAP)
    y1 = y0 + ROW_H
    x0, x1 = MARGIN_X, W - MARGIN_X
    name = f"row{i}"
    zones[name] = (x0, y0, x1, y1)
    rr(d, (x0, y0, x1, y1), 22, fill=(176, 112, 52, 35), outline=(150, 92, 40, 140), width=4)
    # left icon circle
    cy = (y0 + y1) // 2
    cx = x0 + 70
    r = 42
    d.ellipse(
        [(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S],
        fill=(255, 244, 220, 170),
        outline=(176, 112, 52, 170),
        width=3 * S,
    )
    zones[name + "_icon"] = (cx - r, cy - r, cx + r, cy + r)
    # right chevron / time slot
    d.rounded_rectangle(
        [(x1 - 160) * S, (cy - 22) * S, (x1 - 24) * S, (cy + 22) * S],
        12 * S,
        fill=(255, 244, 220, 100),
        outline=(176, 112, 52, 120),
        width=2 * S,
    )

card = Image.alpha_composite(card, down(Z, W, H))
# Bake "MY REPORTS" title lightly for empty bg? README says empty — keep text-free like howto.
# User asked for list card background with empty row slot — no baked text.
card.save("reports_list_bg.png")
print("reports_list_bg", W, H)

# ═══════════════════════════════════════════════════════════════════════
# 6. Replay controls
# ═══════════════════════════════════════════════════════════════════════
CTRL = 256
CS = 4

def ctrl_canvas():
    return Image.new("RGBA", (CTRL * CS, CTRL * CS), (0, 0, 0, 0))

def finish_ctrl(im, name):
    return finish_icon(im, name, CTRL, cream_stroke=True)

# play
im = ctrl_canvas()
d = ImageDraw.Draw(im)
d.ellipse([28 * CS, 28 * CS, 228 * CS, 228 * CS], fill=AMB)
d.ellipse([44 * CS, 44 * CS, 212 * CS, 212 * CS], fill=GOLD)
d.polygon(P([(100, 70), (100, 186), (190, 128)], CS), fill=CREAM)
ctrl_play = finish_ctrl(im, "ctrl_play")

# pause
im = ctrl_canvas()
d = ImageDraw.Draw(im)
d.ellipse([28 * CS, 28 * CS, 228 * CS, 228 * CS], fill=AMB)
d.ellipse([44 * CS, 44 * CS, 212 * CS, 212 * CS], fill=GOLD)
d.rounded_rectangle([88 * CS, 72 * CS, 118 * CS, 184 * CS], 10 * CS, fill=CREAM)
d.rounded_rectangle([138 * CS, 72 * CS, 168 * CS, 184 * CS], 10 * CS, fill=CREAM)
ctrl_pause = finish_ctrl(im, "ctrl_pause")

# slow-mo — turtle / snail-ish: clock with 0.5x
im = ctrl_canvas()
d = ImageDraw.Draw(im)
d.ellipse([28 * CS, 28 * CS, 228 * CS, 228 * CS], fill=AMB)
d.ellipse([44 * CS, 44 * CS, 212 * CS, 212 * CS], fill=GOLD)
# clock face
d.ellipse([70 * CS, 70 * CS, 186 * CS, 186 * CS], fill=CREAM)
d.ellipse([82 * CS, 82 * CS, 174 * CS, 174 * CS], fill=(255, 248, 230, 255))
# hands pointing slow (short arc marker)
d.line(P([(128, 128), (128, 95)], CS), fill=AMB, width=10 * CS)
d.line(P([(128, 128), (155, 140)], CS), fill=DARK[:3] + (255,), width=8 * CS)
d.ellipse([120 * CS, 120 * CS, 136 * CS, 136 * CS], fill=GOLD)
# 0.5 badge
d.rounded_rectangle([150 * CS, 175 * CS, 230 * CS, 230 * CS], 14 * CS, fill=AMB)
ctrl_slow = finish_ctrl(im, "ctrl_slowmo")
# bake 0.5 text on finished icon
sm = Image.open("ctrl_slowmo.png").convert("RGBA")
sd = ImageDraw.Draw(sm)
sd.text((190, 202), "½", font=font(36), fill=CREAM[:3], anchor="mm")
sm.save("ctrl_slowmo.png")
ctrl_slow = sm

# scrub bar (768×96)
SW, SH = 768, 96
im = ss(SW, SH)
d = ImageDraw.Draw(im)
# track
rr(d, (20, 36, SW - 20, 60), 12, fill=(80, 46, 14, 255))
rr(d, (24, 40, SW - 24, 56), 10, fill=GOLD)
# filled portion ~40%
fill_w = int((SW - 48) * 0.4) + 24
rr(d, (24, 40, fill_w, 56), 10, fill=AMB)
# cream stroke on track
rr(d, (18, 34, SW - 18, 62), 14, outline=STROKE[:3] + (255,), width=3)
# thumb
tx = fill_w
d.ellipse([(tx - 22) * S, (SH // 2 - 22) * S, (tx + 22) * S, (SH // 2 + 22) * S], fill=CREAM)
d.ellipse([(tx - 14) * S, (SH // 2 - 16) * S, (tx + 10) * S, (SH // 2 + 8) * S], fill=GOLD)
scrub = down(im, SW, SH)
scrub = add_outline(scrub, 4)
scrub.save("ctrl_scrub.png")
print("ctrl_scrub", SW, SH)

# free cam — camera with 6DOF arrows
im = ctrl_canvas()
d = ImageDraw.Draw(im)
d.ellipse([28 * CS, 28 * CS, 228 * CS, 228 * CS], fill=AMB)
d.ellipse([44 * CS, 44 * CS, 212 * CS, 212 * CS], fill=GOLD)
# cam body
d.rounded_rectangle([72 * CS, 95 * CS, 168 * CS, 165 * CS], 14 * CS, fill=CREAM)
d.ellipse([95 * CS, 108 * CS, 145 * CS, 158 * CS], fill=AMB)
d.ellipse([108 * CS, 121 * CS, 132 * CS, 145 * CS], fill=CREAM)
# free-move arrows N/S/E/W
arrow_col = CREAM
for tip, base_a, base_b in [
    ((128, 48), (112, 72), (144, 72)),   # N
    ((128, 208), (112, 184), (144, 184)),  # S
    ((208, 128), (184, 112), (184, 144)),  # E
    ((48, 128), (72, 112), (72, 144)),     # W
]:
    d.polygon(P([tip, base_a, base_b], CS), fill=arrow_col)
ctrl_freecam = finish_ctrl(im, "ctrl_freecam")
print("controls done")

# ═══════════════════════════════════════════════════════════════════════
# 7. Mock composite + sheet
# ═══════════════════════════════════════════════════════════════════════
# Mock: reports list with sample rows + toast + tags + controls
mock = card.copy()
md = ImageDraw.Draw(mock)
f56 = font(56)
f40 = font(40)
f32 = font(32)

# header title
hx0, hy0, hx1, hy1 = zones["header"]
for ox, oy, col in [(2, 2, STROKE[:3]), (0, 0, TEXT_DK)]:
    md.text(((hx0 + hx1) // 2 + ox, (hy0 + hy1) // 2 + oy), "MY REPORTS", font=f56, fill=col, anchor="mm")

sample_rows = [
    ("physics", "Hole 3 · bounce off rail", "2m ago", tag_physics),
    ("club", "Club clip through ground", "1h ago", tag_club),
    ("camera", "Wrist card pose miss", "3h ago", tag_camera),
    ("ui", "Leaderboard face wrong", "yday", tag_ui),
]
for i, (tag, title, when, ic) in enumerate(sample_rows):
    x0, y0, x1, y1 = zones[f"row{i}"]
    ix0, iy0, ix1, iy1 = zones[f"row{i}_icon"]
    ic_sz = 72
    ix = (ix0 + ix1) // 2 - ic_sz // 2
    iy = (iy0 + iy1) // 2 - ic_sz // 2
    mock.alpha_composite(ic.resize((ic_sz, ic_sz), Image.LANCZOS), (ix, iy))
    tx = ix1 + 20
    cy = (y0 + y1) // 2
    for ox, oy, col in [(1, 1, STROKE[:3]), (0, 0, TEXT_DK)]:
        md.text((tx + ox, cy - 14 + oy), title.upper(), font=f32, fill=col, anchor="lm")
    md.text((tx, cy + 22), f"#{tag}", font=f32, fill=LAB, anchor="lm")
    md.text((x1 - 92, cy), when, font=f32, fill=LAB, anchor="mm")

mock.save("reports_list_mock.png")

# Full QA sheet
sh = Image.new("RGB", (1800, 2200), (40, 28, 22))
sd = ImageDraw.Draw(sh)
f20 = font(22)
f28 = font(28)
label_col = (250, 220, 170)

# title
sd.text((40, 30), "BUG RECORDER UI — contact sheet", font=f28, fill=label_col)

# left: reports mock
mr = mock.resize((700, 536), Image.LANCZOS)
sh.paste(mr, (40, 80), mr)
sd.text((40, 630), "reports_list_mock (1024×784)", font=f20, fill=label_col)

# empty bg smaller
cr = card.resize((350, 268), Image.LANCZOS)
sh.paste(cr, (780, 80), cr)
sd.text((780, 360), "reports_list_bg (empty)", font=f20, fill=label_col)

# toast
tr = toast.resize((540, 120), Image.LANCZOS)
sh.paste(tr, (780, 400), tr)
sd.text((780, 530), "toast_report_saved", font=f20, fill=label_col)

# bug button
sh.paste(bug_btn.resize((200, 200), Image.LANCZOS), (1180, 80), bug_btn.resize((200, 200), Image.LANCZOS))
sd.text((1180, 290), "icon_bug_button 512", font=f20, fill=label_col)

# rec indicator
sh.paste(combo.resize((480, 135), Image.LANCZOS), (1180, 340), combo.resize((480, 135), Image.LANCZOS))
sd.text((1180, 490), "rec_indicator", font=f20, fill=label_col)

# tags row
sd.text((40, 680), "TAG ICONS (256)", font=f28, fill=label_col)
for i, (n, ic) in enumerate([
    ("tag_physics", tag_physics),
    ("tag_club", tag_club),
    ("tag_camera", tag_camera),
    ("tag_ui", tag_ui),
    ("tag_other", tag_other),
]):
    x = 40 + i * 220
    sh.paste(ic, (x, 730), ic)
    sd.text((x, 1000), n, font=f20, fill=label_col)

# controls row
sd.text((40, 1060), "REPLAY CONTROLS", font=f28, fill=label_col)
for i, (n, ic) in enumerate([
    ("ctrl_play", ctrl_play),
    ("ctrl_pause", ctrl_pause),
    ("ctrl_slowmo", ctrl_slow),
    ("ctrl_freecam", ctrl_freecam),
]):
    x = 40 + i * 220
    sh.paste(ic, (x, 1120), ic)
    sd.text((x, 1390), n, font=f20, fill=label_col)

# scrub
scr = scrub.resize((600, 75), Image.LANCZOS)
sh.paste(scr, (960, 1180), scr)
sd.text((960, 1270), "ctrl_scrub 768×96", font=f20, fill=label_col)

# rec pieces
sh.paste(rec_dot.resize((128, 128), Image.LANCZOS), (960, 1340), rec_dot.resize((128, 128), Image.LANCZOS))
sd.text((960, 1480), "rec_dot 256", font=f20, fill=label_col)
sh.paste(badge.resize((320, 100), Image.LANCZOS), (1120, 1350), badge.resize((320, 100), Image.LANCZOS))
sd.text((1120, 1470), "rec_badge 512×160", font=f20, fill=label_col)

# replay bar mock strip
bar = Image.new("RGBA", (1600, 200), (0, 0, 0, 0))
bar_card = make_brass_parchment_card(1600, 200, seed=30)
# overlay controls
bd = ImageDraw.Draw(bar_card)
icons_row = [
    (ctrl_play, 80),
    (ctrl_pause, 220),
    (ctrl_slow, 360),
    (ctrl_freecam, 500),
]
for ic, x in icons_row:
    bar_card.alpha_composite(ic.resize((96, 96), Image.LANCZOS), (x, 52))
bar_card.alpha_composite(scrub.resize((700, 88), Image.LANCZOS), (640, 56))
# REC badge small
bar_card.alpha_composite(badge.resize((240, 75), Image.LANCZOS), (1320, 62))
bar_card.save("replay_bar_mock.png")
br = bar_card.resize((1600, 200), Image.LANCZOS)
sh.paste(br, (40, 1560), br)
sd.text((40, 1780), "replay_bar_mock (composite reference)", font=f20, fill=label_col)

# phone bug button placement hint
phone = Image.new("RGBA", (280, 500), (0, 0, 0, 0))
pd = ImageDraw.Draw(phone)
pd.rounded_rectangle([10, 10, 270, 490], 36, fill=(30, 22, 18, 255), outline=BRASS_L, width=4)
pd.rounded_rectangle([24, 50, 256, 440], 16, fill=(50, 70, 45, 255))
phone.alpha_composite(bug_btn.resize((72, 72), Image.LANCZOS), (180, 360))
phone.alpha_composite(combo.resize((200, 56), Image.LANCZOS), (40, 70))
sh.paste(phone, (1480, 80), phone)
sd.text((1480, 600), "phone hint", font=f20, fill=label_col)

sh.save("bug_recorder_sheet.jpg", quality=92)
print("sheet done")

# also save a dedicated mock_composite name
mock_comp = sh.copy()
mock_comp.save("mock_composite.jpg", quality=92)
print("all done")
