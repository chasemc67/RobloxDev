"""Sugarloaf Canyon felt textures (system python3 + numpy + Pillow).

  python3 textures/_make_felts.py

Outputs (512 tileable):
  felt.png            main putting green (#4FA83D family, course.md)
  felt_bank.png       darker bank / slot felt (#3B7F35 / sage)
  slope_felt_C.png    one-way chevron slope felt (same formula as lantern-grove)
  *_tile2x2.png       seam-check tiles
"""
import math, os
import numpy as np
from PIL import Image

N = 512
OUT = os.path.dirname(os.path.abspath(__file__))


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32) / 255.0


def noise(seed, beta=1.6, sx=1.0, sy=1.0, lo=1.0):
    rng = np.random.default_rng(seed)
    w = rng.standard_normal((N, N))
    F = np.fft.fft2(w)
    fy = np.fft.fftfreq(N)[:, None] * N
    fx = np.fft.fftfreq(N)[None, :] * N
    f = np.sqrt((fx * sx) ** 2 + (fy * sy) ** 2)
    f[0, 0] = 1.0
    amp = 1.0 / np.maximum(f, lo) ** beta
    amp[0, 0] = 0.0
    r = np.real(np.fft.ifft2(F * amp))
    r = (r - r.mean()) / (r.std() + 1e-9)
    return np.clip(0.5 + r * 0.18, 0, 1)


def ramp(t, stops):
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (t >= p0) & (t <= p1)
        u = ((t - p0) / max(p1 - p0, 1e-6))[m]
        out[m] = hexc(c0) * (1 - u[:, None]) + hexc(c1) * u[:, None]
    return out


def seam_stats(arr):
    a = arr.astype(np.float64)
    return (np.abs(a[:, 0] - a[:, -1]).mean(), np.abs(a[:, 1:] - a[:, :-1]).mean(),
            np.abs(a[0] - a[-1]).mean(), np.abs(a[1:] - a[:-1]).mean())


def save_rgb(name, img_f_or_u8):
    if img_f_or_u8.dtype != np.uint8:
        arr = (np.clip(img_f_or_u8, 0, 1) * 255).astype(np.uint8)
    else:
        arr = img_f_or_u8
    Image.fromarray(arr, "RGB").save(os.path.join(OUT, name), optimize=True)
    Image.fromarray(np.tile(arr, (2, 2, 1))).save(
        os.path.join(OUT, name.replace(".png", "_tile2x2.png")), optimize=True)
    su, iu, sv, iv = seam_stats(arr)
    print(f"[tex] {name} mean={arr.mean(axis=(0,1)).round(1)} seamU={su:.2f}/{iu:.2f} seamV={sv:.2f}/{iv:.2f}")
    return arr


def main():
    lo = noise(11, beta=1.8)
    nap = noise(13, beta=0.9, sx=0.08, sy=1.0)
    fine = noise(12, beta=0.25)
    x = np.arange(N)[None, :] / N
    stripes = 0.5 + 0.5 * np.sign(np.sin(math.tau * 2 * x))
    f = np.fft.fftfreq(N)
    g = np.exp(-2 * (np.pi * 10.0 * f) ** 2)
    stripes_1d = np.real(np.fft.ifft(np.fft.fft(stripes[0]) * g))
    stripes = np.broadcast_to(stripes_1d[None, :], (N, N)).copy()
    t = 0.5 + (lo - 0.5) * 0.5 + (nap - 0.5) * 0.4 + (fine - 0.5) * 0.16 + (stripes - 0.5) * 0.12

    # course.md Putting green #4FA83D
    felt = save_rgb("felt.png", ramp(t, [(0, "#2F7A2A"), (0.45, "#4FA83D"), (1, "#6BC24F")]))
    # course.md Sage felt #3B7F35 (bank / slot / shadowed)
    save_rgb("felt_bank.png", ramp(t, [(0, "#245A22"), (0.45, "#3B7F35"), (1, "#4F9A44")]))

    # slope_felt_C — lantern-grove/_make_slope.py C formula, Sugarloaf edge tint
    y, xg = np.mgrid[0:N, 0:N] / N
    cu, cv = (xg * 4) % 1, (y * 4) % 1
    half = np.abs(cu - 0.5)
    d = (cv - (0.62 - half * 0.75) + 0.5) % 1 - 0.5
    wmask = np.clip((0.42 - half) / 0.06, 0, 1)
    tail = np.where(d < 0, np.exp(d / 0.22), 0) * wmask
    edge = np.clip(1 - np.abs(d + 0.012) / 0.018, 0, 1) * wmask
    EDGE = np.array([110.0, 140.0, 70.0])
    C = felt.astype(np.float64) * (1 - 0.42 * tail[..., None]) + edge[..., None] * EDGE
    save_rgb("slope_felt_C.png", np.clip(C, 0, 255).astype(np.uint8))


if __name__ == "__main__":
    main()
