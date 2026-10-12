"""Grayscale tint masters of the Sugarloaf felt textures for Roblox (stage w).

  uv run --with pillow --with numpy python textures/_make_roblox_tints.py

The felt colour is set per part via Texture.Color3 (multiply), so one upload serves every felt tone:
  roblox/felt_gray.png            from felt.png, mean luminance normalised to 0.86
  roblox/slope_gray_r{0,90,180,270}.png  from slope_felt_C.png (+V = downhill at r0), rotated like the LG set
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "roblox")
os.makedirs(OUT, exist_ok=True)


def gray(name, target=0.86):
    a = np.asarray(Image.open(os.path.join(HERE, name)).convert("RGB")).astype(np.float32) / 255
    lum = a @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    lum = lum * (target / lum.mean())
    return Image.fromarray((np.clip(lum, 0, 1) * 255 + 0.5).astype(np.uint8), "L").convert("RGB")


gray("felt.png").save(os.path.join(OUT, "felt_gray.png"), optimize=True)
s = gray("slope_felt_C.png")
for r in (0, 90, 180, 270):
    s.rotate(-r).save(os.path.join(OUT, "slope_gray_r%d.png" % r), optimize=True)
print(sorted(os.listdir(OUT)))
