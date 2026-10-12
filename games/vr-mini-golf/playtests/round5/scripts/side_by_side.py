"""side_by_side.py OUT LEFT RIGHT [label_left label_right]: two images at the same height, side by side, with labels."""
import sys
from PIL import Image, ImageDraw
out, a, b = sys.argv[1:4]
la, lb = (sys.argv[4:6] + ["", ""])[:2] if len(sys.argv) > 4 else ("", "")
A, B = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
H = 640
A = A.resize((int(A.width * H / A.height), H)); B = B.resize((int(B.width * H / B.height), H))
im = Image.new("RGB", (A.width + B.width + 30, H + 40), (30, 24, 20))
im.paste(A, (0, 40)); im.paste(B, (A.width + 30, 40))
d = ImageDraw.Draw(im)
d.text((10, 10), la, fill=(255, 230, 180)); d.text((A.width + 40, 10), lb, fill=(255, 230, 180))
im.save(out)
print("saved", out)
