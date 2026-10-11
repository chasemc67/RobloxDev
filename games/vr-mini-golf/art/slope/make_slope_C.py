"""Bake 3D Model Bot's pattern-C slope felt colour map (one-way arrowheads, +V = downhill) into the course felt
tones and the four Top-face rotations CourseBuilder needs (a Texture can't be rotated).

usage: uv run --with pillow --with numpy python make_slope_C.py <slope_felt_color.png> <outdir>
Writes slope_C_<tone>_r<deg>.png. r0: tips toward part -Z, r90: +X, r180: +Z, r270: -X
(Top-face Texture: image +U = part -X, +V = part -Z; images are turned clockwise).
"""
import sys
import numpy as np
from PIL import Image

TONES = {"felt": "4F9A3A", "feltHi": "86C24A", "feltLo": "2F6B2A"}  # CourseBuilder palette P.felt / feltHi / feltLo
src, out = sys.argv[1], sys.argv[2]
A = np.asarray(Image.open(src).convert("RGB")).astype(float)
mean = A.reshape(-1, 3).mean(0)
for tone, hx in TONES.items():
    target = np.array([int(hx[i:i + 2], 16) for i in (0, 2, 4)], float)
    im = Image.fromarray(np.clip(A * (target / mean), 0, 255).round().astype(np.uint8))
    for k in range(4):
        im.rotate(-90 * k).save(f"{out}/slope_C_{tone}_r{k * 90}.png")
    print(tone, "mean", np.asarray(im).reshape(-1, 3).mean(0).round(1), "target", target)
