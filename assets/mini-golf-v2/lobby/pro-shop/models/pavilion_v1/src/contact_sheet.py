"""Contact sheet for the room: concept A beside the v1 Blender previews (Pillow).

Usage: python contact_sheet.py --previews <dir> --output <png> [--concept <A-park-pavilion.jpg>]
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont


def font(size):
    for f in ("segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def fit(im, w, h):
    im = im.convert("RGB")
    s = min(w / im.width, h / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    cell = Image.new("RGB", (w, h), (236, 232, 222))
    cell.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return cell


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--previews", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--concept", default=None)
    a = ap.parse_args()
    cells = [(a.concept, "CONCEPT A (reference, Art)"),
             (os.path.join(a.previews, "Front34.png"), "v1 front three-quarter"),
             (os.path.join(a.previews, "Rear34.png"), "v1 side / rear three-quarter"),
             (os.path.join(a.previews, "Eye_Counter.png"), "v1 counter, 5-stud eye, 28 mm"),
             (os.path.join(a.previews, "Eye_BallTray.png"), "v1 ball tray (left), 5-stud eye, 32 mm"),
             (os.path.join(a.previews, "Eye_ClubRack.png"), "v1 club rack (right), 5-stud eye, 32 mm")]
    cw, ch, lab, head, pad = 800, 520, 40, 86, 14
    W = pad * 4 + cw * 3
    H = head + (lab + ch + pad) * 2 + pad
    sheet = Image.new("RGB", (W, H), (247, 244, 236))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 12), "Pro Shop pavilion v1 - first detailed Blender model (concept A) - for Art + Chase review, "
                      "not final", fill=(34, 40, 34), font=font(30))
    d.text((pad, 50), "UI on the screen is an illustrative placeholder only (no commerce, no prices). "
                      "Previews are not committed.", fill=(90, 90, 84), font=font(20))
    for i, (fn, label) in enumerate(cells):
        r, c = divmod(i, 3)
        x = pad + c * (cw + pad)
        y = head + r * (lab + ch + pad)
        d.text((x, y + 8), label, fill=(34, 40, 34), font=font(22))
        if fn and os.path.exists(fn):
            im = Image.open(fn)
            if "CONCEPT" in label:  # left half of the concept sheet is the whole-asset view
                im = im.crop((0, int(im.height * 0.085), im.width // 2, im.height))
            sheet.paste(fit(im, cw, ch), (x, y + lab))
        else:
            d.rectangle([x, y + lab, x + cw, y + lab + ch], outline=(200, 0, 0), width=3)
            d.text((x + 20, y + lab + 20), "MISSING " + str(fn), fill=(200, 0, 0), font=font(20))
    sheet.save(a.output)
    print("WROTE", a.output, sheet.size)


if __name__ == "__main__":
    main()
