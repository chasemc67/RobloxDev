# usage: halo.py img... -> count of Studio hover-outline pixels (178,229,255 +-6)
import sys
from PIL import Image
for f in sys.argv[1:]:
    im = Image.open(f).convert("RGB"); n = 0
    for (r, g, b) in im.getdata():
        if abs(r-178) <= 6 and abs(g-229) <= 6 and abs(b-255) <= 6: n += 1
    print(f.split("/")[-1], n)
