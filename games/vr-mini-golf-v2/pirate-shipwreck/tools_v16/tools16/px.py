# usage: px.py img x,y[,r] ...  -> median RGB in a (2r+1)^2 box per point
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert("RGB")
for a in sys.argv[2:]:
    v = [int(t) for t in a.split(",")]; x, y = v[0], v[1]; r = v[2] if len(v) > 2 else 4
    px = [im.getpixel((i, j)) for i in range(x-r, x+r+1) for j in range(y-r, y+r+1)]
    med = tuple(sorted(c[k] for c in px)[len(px)//2] for k in range(3))
    print(a, med)
