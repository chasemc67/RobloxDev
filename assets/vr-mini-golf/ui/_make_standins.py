"""Stage z stand-in UI art (the real art lives on the box's /workspace, which wasn't reachable from the Mini).
Same file names and sizes as the brief, so the real files can replace these 1:1 (then re-upload, update Config.UI).
  menu/menu_frame.png   1200x800 9-slice panel, SliceCenter 64,64,1136,736 (corners/rim inside the 64 px border)
  menu/close_x.png      128x128 round red close button with an X
  menu/menu_button.png  320x112 amber pill, no text (the game draws "Menu" on it)
  loading/loading_<course>.png 1920x1080 from the course card art + title background
Run: uv run --with pillow python assets/vr-mini-golf/ui/_make_standins.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
STORE = HERE.parent / "store" / "ui"
NAVY = (14, 22, 38, 255)
AMBER = (255, 179, 71, 255)
CREAM = (255, 238, 206, 255)


def font(size):
    for f in ["/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"]:
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def menu_frame():
    w, h, r = 1200, 800, 48
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([4, 4, w - 5, h - 5], r, fill=(14, 22, 38, 150), outline=AMBER, width=8)
    d.rounded_rectangle([20, 20, w - 21, h - 21], r - 14, outline=(255, 179, 71, 110), width=3)
    # brass corner studs (inside the 64 px corners, so 9-slicing keeps them round)
    for cx, cy in [(34, 34), (w - 35, 34), (34, h - 35), (w - 35, h - 35)]:
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=AMBER, outline=CREAM, width=2)
    img.save(HERE / "menu" / "menu_frame.png")


def close_x():
    s = 128
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 4, s - 5, s - 5], fill=(170, 58, 46, 255), outline=CREAM, width=6)
    m = 40
    d.line([m, m, s - m, s - m], fill=CREAM, width=14)
    d.line([m, s - m, s - m, m], fill=CREAM, width=14)
    img.save(HERE / "menu" / "close_x.png")


def menu_button():
    w, h = 320, 112
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([3, 3, w - 4, h - 4], 40, fill=AMBER, outline=CREAM, width=5)
    # hamburger icon on the left; the label is drawn by the game to its right
    for i in range(3):
        y = 34 + i * 20
        d.rounded_rectangle([34, y, 82, y + 9], 4, fill=NAVY)
    img.save(HERE / "menu" / "menu_button.png")


def loading(course, card, title):
    bg = Image.open(STORE / "title_bg_v2.png").convert("RGBA").resize((1920, 1080))
    bg = bg.filter(ImageFilter.GaussianBlur(6))
    wash = Image.new("RGBA", bg.size, (14, 22, 38, 150))
    img = Image.alpha_composite(bg, wash)
    c = Image.open(STORE / card).convert("RGBA").resize((620, 620))
    mask = Image.new("L", c.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 619, 619], 48, fill=255)
    frame = Image.new("RGBA", (644, 644), (0, 0, 0, 0))
    ImageDraw.Draw(frame).rounded_rectangle([0, 0, 643, 643], 58, fill=AMBER)
    img.alpha_composite(frame, (638, 150))
    img.paste(c, (650, 162), mask)
    d = ImageDraw.Draw(img)
    f = font(96)
    tw = d.textlength(title, font=f)
    d.text(((1920 - tw) / 2 + 4, 812 + 4), title, font=f, fill=NAVY)
    d.text(((1920 - tw) / 2, 812), title, font=f, fill=AMBER)
    f2 = font(44)
    sub = "Heading to the course..."
    tw2 = d.textlength(sub, font=f2)
    d.text(((1920 - tw2) / 2, 940), sub, font=f2, fill=CREAM)
    img.convert("RGB").save(HERE / "loading" / f"loading_{course}.png")


menu_frame()
close_x()
menu_button()
loading("lantern_grove", "card_lanterngrove_v2.png", "Lantern Grove")
loading("sugarloaf_canyon", "card_sugarloafcanyon_v2.png", "Sugarloaf Canyon")
print("ok")
