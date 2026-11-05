# usage: sheet.py out.png img... -> 3-column contact sheet (each scaled to 680 wide)
import sys
from PIL import Image
fs = sys.argv[2:]; ims = []
for f in fs:
    im = Image.open(f).convert("RGB"); im = im.resize((680, int(im.height * 680 / im.width))); ims.append(im)
w, h = ims[0].size; rows = (len(ims) + 2) // 3
S = Image.new("RGB", (w * 3, h * rows))
for i, im in enumerate(ims): S.paste(im, ((i % 3) * w, (i // 3) * h))
S.save(sys.argv[1])
