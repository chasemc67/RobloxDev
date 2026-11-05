"""Compose previews/props/<name>.png (3/4 view | eye-height view with 2x5 capsule, labelled) and
previews/contact_sheet.png (all props, labelled). Plain python + Pillow:  python -I post_previews.py"""
import os, json
from PIL import Image, ImageDraw, ImageFont

SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
VIEWS = os.path.join(OUT, "previews", "props", "_views")
PROPS_DIR = os.path.join(OUT, "previews", "props")


def font(size, bold=True):
    for f in (("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
              "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def main():
    man = json.load(open(os.path.join(OUT, "manifest.json")))
    tiles = []
    for p in man["props"]:
        n = p["name"]
        a = os.path.join(VIEWS, f"{n}_34.png")
        b = os.path.join(VIEWS, f"{n}_eye.png")
        if not (os.path.exists(a) and os.path.exists(b)):
            print("missing views", n)
            continue
        A, B = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
        W, H = A.width + B.width, max(A.height, B.height) + 70
        im = Image.new("RGB", (W, H), (34, 28, 26))
        im.paste(A, (0, 70))
        im.paste(B, (A.width, 70))
        d = ImageDraw.Draw(im)
        s = p["bbox_size_studs"]
        d.text((14, 8), n, fill=(255, 214, 150), font=font(30))
        d.text((14, 42), f"{p['triangles']} tris (budget {p['tris_max']}) x{p.get('builder_count', 0)}   "
                         f"bbox {s[0]:.2f} x {s[1]:.2f} x {s[2]:.2f} studs   {', '.join(p['materials'])}",
               fill=(235, 225, 210), font=font(18, False))
        d.text((A.width + 12, 76), "eye height 5 studs + 2x5 capsule", fill=(255, 255, 255), font=font(16, False))
        d.text((12, 76), "3/4 view", fill=(255, 255, 255), font=font(16, False))
        im.save(os.path.join(PROPS_DIR, f"{n}.png"))
        tiles.append((n, p, im))
    # contact sheet: 5 columns of half-size tiles
    cols = 5
    tw = tiles[0][2].width // 2
    th = tiles[0][2].height // 2
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * th + 80), (24, 20, 19))
    d = ImageDraw.Draw(sheet)
    tot = man["totals"]
    d.text((16, 14), f"Golden Hour Boardwalk lobby props - pass 1   ({len(tiles)} FBX, lobby total "
                     f"{tot['tris_total']} tris incl. {tot['instances']} instances)", fill=(255, 214, 150),
           font=font(34))
    for k, (n, p, im) in enumerate(tiles):
        t = im.resize((tw, th), Image.LANCZOS)
        sheet.paste(t, ((k % cols) * tw, 80 + (k // cols) * th))
    sheet.save(os.path.join(OUT, "previews", "contact_sheet.png"))
    print("composed", len(tiles), "props")


main()
