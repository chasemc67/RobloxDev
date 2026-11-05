"""tee_contact_sheet.png: the 9 tee views (previews/assembly_hNN_tee.png), labelled. System python3 + Pillow.
  python3 models/_src/tee_sheet.py [--compare OUT.png]   (--compare: concept | render pairs, for review)
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
COURSE = os.path.dirname(OUT)
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
holes = json.load(open(os.path.join(COURSE, "holes.json")))["holes"]
man = json.load(open(os.path.join(OUT, "manifest.json")))
dress = man.get("dressing", {}).get("holes", {})

W, H = 640, 360
f1, f2 = ImageFont.truetype(F, 20), ImageFont.truetype(F, 13)


def label(h):
    d = dress.get(f"H{h['number']}", {})
    st = d.get("stats", {})
    return (f"{h['number']}. {h['name']} - par {h['par']}",
            f"{st.get('final_3d', 0)} props + {st.get('final_cards', 0)} cards | near-field tris "
            f"{st.get('near_field_tris_before', 0):,} -> {st.get('near_field_tris_after', 0):,}")


if "--compare" in sys.argv:
    out = sys.argv[sys.argv.index("--compare") + 1]
    sheet = Image.new("RGB", (2 * W + 30, 9 * (H + 34) + 10), (20, 22, 24))
    d = ImageDraw.Draw(sheet)
    for i, h in enumerate(holes):
        n = h["number"]
        y = 10 + i * (H + 34)
        c = Image.open(os.path.join(COURSE, f"h{n:02d}-concept.png")).convert("RGB").resize((W, H))
        r = Image.open(os.path.join(OUT, "previews", f"assembly_h{n:02d}_tee.png")).convert("RGB").resize((W, H))
        sheet.paste(c, (10, y))
        sheet.paste(r, (W + 20, y))
        d.text((10, y + H + 4), label(h)[0] + "   concept | render   " + label(h)[1], font=f2, fill=(240, 200, 90))
    sheet.save(out)
else:
    cols = 3
    sheet = Image.new("RGB", (cols * (W + 12) + 12, 3 * (H + 52) + 64), (20, 22, 24))
    d = ImageDraw.Draw(sheet)
    d.text((14, 16), "Lantern Grove - tee views, pass 8: lantern-lit H9, rail lanterns H7 lower tiers + H8, brighter H8 glow, <= 34k tris", font=ImageFont.truetype(F, 26),
           fill=(242, 182, 50))
    for i, h in enumerate(holes):
        x = 12 + (i % cols) * (W + 12)
        y = 64 + (i // cols) * (H + 52)
        r = Image.open(os.path.join(OUT, "previews", f"assembly_h{h['number']:02d}_tee.png")).convert("RGB").resize((W, H))
        sheet.paste(r, (x, y))
        a, b = label(h)
        d.text((x, y + H + 4), a, font=f1, fill=(240, 240, 240))
        d.text((x, y + H + 28), b, font=f2, fill=(200, 200, 200))
    sheet.save(os.path.join(OUT, "tee_contact_sheet.png"))
    print("tee_contact_sheet.png written")
