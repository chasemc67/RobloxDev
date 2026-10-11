import sys, numpy as np
from PIL import Image
src, felt, out = sys.argv[1], sys.argv[2], sys.argv[3]
A = np.asarray(Image.open(src).convert('RGB')).astype(float)
lum = A @ [0.299, 0.587, 0.114]
f = np.asarray(Image.open(felt).convert('RGB').resize(A.shape[1::-1])).astype(float) @ [0.299, 0.587, 0.114]
m = lum / f.mean()                      # chevron shading + felt grain, mean ~1 on the plain areas
m = m / np.percentile(m, 98)
g = (np.clip(m, 0, 1) * 255).astype(np.uint8)
im = Image.fromarray(g).convert('RGB')
print('mask mean', g.mean().round(1), 'min', g.min(), 'max', g.max())
for k in range(4):
    im.rotate(-90 * k).save(f'{out}/slope_mask_r{k*90}.png')   # rotate clockwise: +V (down the image) turns toward -U ... per k
