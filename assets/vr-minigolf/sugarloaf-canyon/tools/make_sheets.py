#!/usr/bin/env python3
"""Build holes_layouts_sheet.jpg from hNN-layout.png (all 18 holes, 6 x 3). Adapted from Lantern Grove (layouts only: no concept
images exist yet for Sugarloaf Canyon).   python3 tools/make_sheets.py   (run from anywhere)"""
import json, os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
H = json.load(open(os.path.join(ROOT, "holes.json")))["holes"]
tot = sum(h["par"] for h in H)
f = lambda s: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", s)


def sheet(kind, out, tw=760, cols=6):
    ims = [Image.open(os.path.join(ROOT, f"{h['id']}-{kind}.png")).convert("RGB") for h in H]
    th = max(int(tw * im.height / im.width) for im in ims)
    rows = (len(H) + cols - 1) // cols
    cap, pad, head = 46, 22, 90
    g = Image.new("RGB", (cols * tw + (cols + 1) * pad, head + rows * (th + cap + pad) + pad), (40, 26, 30))
    d = ImageDraw.Draw(g)
    d.text((pad, 25), f"Sugarloaf Canyon - 18-hole {kind}s (total par {tot})", font=f(42), fill=(255, 211, 107))
    for i, (h, im) in enumerate(zip(H, ims)):
        im.thumbnail((tw, th))
        x = pad + (i % cols) * (tw + pad)
        y = head + (i // cols) * (th + cap + pad)
        g.paste(im, (x, y))
        d.text((x, y + th + 8), f"{i + 1}. {h['name']} - par {h['par']}", font=f(24), fill=(250, 234, 214))
    q = 88
    path = os.path.join(ROOT, out)
    while True:
        g.save(path, quality=q)
        if os.path.getsize(path) < 4e6 or q < 50:
            break
        q -= 8
    print(path, os.path.getsize(path))


sheet("layout", "holes_layouts_sheet.jpg")
sheet("concept", "holes_concepts_sheet.jpg", tw=600, cols=3)
