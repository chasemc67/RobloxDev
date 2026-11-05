"""Slope felt SurfaceAppearance set (system python3 + numpy + Pillow, no Blender).

  python3 models/_src/slope_felt.py

Inputs : textures/slope_felt_C.png        (512px tiling, 4x4 one-way arrowheads: bright tip line at the +V end,
                                           dark fill + gradient tail fading upslope toward -V; textures/_make_slope.py)
         models/textures/felt.png         (flat felt colour; C = felt * (1 - 0.42 tail) + edge * (95, 120, 60))
         models/textures/felt_normal.png  (flat felt nap normal, OpenGL / Roblox convention: +G = up the image)
Outputs: models/textures/slope_felt_color.png, slope_felt_normal.png, slope_felt_roughness.png
         models/textures/_check/slope_felt_*_tile2x2.png (seam check tiles)

UV convention: Roblox samples image row 0 at V = 0 (top-left origin), so +V = DOWN the image (increasing row) and
the arrow tips point down the image. (Blender's UV editor has v = 0 at the image bottom, so in Blender terms the tips
point toward decreasing v; Roblox's FBX import flips V, so a mesh that looks right in Blender looks right in Studio.)

felt.png has a faint U seam (non-wrapping stripe blur); the slope set corrects it near x = 0 (fix_felt_u_seam).
The tail / tip masks are recovered from slope_felt_C.png by per-pixel least squares against felt.png and checked
against the analytic C formula. Colour is renormalised per channel to felt.png's mean. Normal = felt nap slopes +
a raised-arrow emboss (height peaks at the tip, steep front face toward +V, gentle ramp upslope; wrap-around
gradients). Roughness = high felt roughness (0.85..0.95), arrows a touch smoother. Everything uses np.roll / FFT,
so it tiles. main() ends with numeric direction checks: every map must agree with C and not with C flipped.
"""
import colorsys, os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.dirname(HERE)
TEX = os.path.join(MODELS, "textures")
CHECK = os.path.join(TEX, "_check")
SRC = os.path.join(os.path.dirname(MODELS), "textures", "slope_felt_C.png")
N = 512
CELLS = 4                                  # 4x4 arrowheads per tile -> 128 px cells

C_TAIL, C_EDGE = 0.42, np.array([95.0, 120.0, 60.0])   # the strengths _make_slope.py used for C
TAIL_DARK = 0.42         # keep C's look (the approved test render)
EDGE_GAIN = 1.0
EMBOSS = 2.2             # raised-arrow emboss strength (felt nap uses 4.0 on its own height field)
FELT_TILE_STUDS = 8.0    # lglib.TEX["Felt"] = ("felt", 8.0)


def load(p, mode="RGB"):
    return np.asarray(Image.open(p).convert(mode)).astype(np.float64)


def blur_wrap(a, r):
    """Periodic Gaussian blur via FFT (sigma r px), so the result still tiles."""
    fy = np.fft.fftfreq(N)[:, None]
    fx = np.fft.fftfreq(N)[None, :]
    g = np.exp(-2 * (np.pi * r) ** 2 * (fx ** 2 + fy ** 2))
    return np.real(np.fft.ifft2(np.fft.fft2(a) * g))


def fix_felt_u_seam(felt, sigma=10.0, half=48):
    """felt.png's mowing stripes were blurred with PIL (no wrap), leaving a ~4-level step at the U seam (x = 0).
    Replace the column-mean profile near the seam with a wrap-blurred one (cosine fade over +-half px)."""
    prof = felt.mean(0)                                            # (N, 3) column means
    f = np.fft.fftfreq(N)[:, None]
    smooth = np.real(np.fft.ifft(np.fft.fft(prof, axis=0) * np.exp(-2 * (np.pi * sigma * f) ** 2), axis=0))
    d = np.minimum(np.arange(N), N - np.arange(N))                 # wrapped distance to the seam
    win = np.where(d < half, 0.5 + 0.5 * np.cos(np.pi * d / half), 0.0)
    return felt + (win[:, None] * (smooth - prof))[None]


def analytic_c():
    """The tail / tip-edge formula textures/_make_slope.py used for slope_felt_C (sanity check only)."""
    y, x = np.mgrid[0:N, 0:N] / N                                  # y = row / N = V (grows down the image)
    cu, cv = (x * CELLS) % 1, (y * CELLS) % 1
    half = np.abs(cu - 0.5)
    d = (cv - (0.62 - half * 0.75) + 0.5) % 1 - 0.5               # 0 on the leading V edge, < 0 upslope
    w = np.clip((0.42 - half) / 0.06, 0, 1)
    tail = np.where(d < 0, np.exp(d / 0.22), 0) * w
    edge = np.clip(1 - np.abs(d + 0.012) / 0.018, 0, 1) * w
    return tail, edge


def recover_masks(src, felt):
    """Per pixel: src - felt = tail * (-C_TAIL * felt) + edge * C_EDGE, solved by 2x2 least squares over RGB."""
    a = -C_TAIL * felt                                              # (N, N, 3) tail basis
    b = np.broadcast_to(C_EDGE, felt.shape)                         # edge basis
    r = src - felt
    aa, ab, bb = (a * a).sum(-1), (a * b).sum(-1), (b * b).sum(-1)
    ar, br = (a * r).sum(-1), (b * r).sum(-1)
    det = aa * bb - ab * ab
    tail = (bb * ar - ab * br) / det
    edge = (aa * br - ab * ar) / det
    return np.clip(tail, 0, 1), np.clip(edge, 0, 1)


def seam_stats(img):
    """Wrap-around edge difference vs interior neighbour difference (mean abs, 0..255 units)."""
    a = img.astype(np.float64)
    if a.ndim == 2:
        a = a[..., None]
    seam_v = np.abs(a[0] - a[-1]).mean()             # bottom row -> top row (V wrap)
    seam_u = np.abs(a[:, 0] - a[:, -1]).mean()       # right col -> left col (U wrap)
    int_v = np.abs(a[1:] - a[:-1]).mean()
    int_u = np.abs(a[:, 1:] - a[:, :-1]).mean()
    return seam_u, int_u, seam_v, int_v


def hsv_mean(rgb):
    m = rgb.reshape(-1, 3).mean(0)
    h, s, v = colorsys.rgb_to_hsv(*(m / 255.0))
    return m, (h * 360, s, v)


def apex_rows(sig):
    """Per arrow column: row (within its 128px cell, 0..127) of the strongest signal, at the arrow centre column vs
    the arrow shoulders (|cu - 0.5| = 0.25). Returns mean centre row, mean shoulder row over all 16 cells."""
    c = N // CELLS
    cen, sho = [], []
    for i in range(CELLS):
        for j in range(CELLS):
            blk = sig[i * c:(i + 1) * c, j * c:(j + 1) * c]
            cen.append(blk[:, c // 2 - 2:c // 2 + 3].mean(1).argmax())
            sho.append(np.mean([blk[:, k - 2:k + 3].mean(1).argmax() for k in (c // 4, 3 * c // 4)]))
    return float(np.mean(cen)), float(np.mean(sho))


def corr(a, b):
    return float(np.corrcoef(a.ravel(), b.ravel())[0, 1])


def main():
    os.makedirs(CHECK, exist_ok=True)
    felt_raw = load(os.path.join(TEX, "felt.png"))
    felt = fix_felt_u_seam(felt_raw)
    fn = load(os.path.join(TEX, "felt_normal.png")) / 255.0 * 2 - 1
    src = load(SRC)
    w = np.array([0.299, 0.587, 0.114])

    # masks from the C image (vs felt.png as it was when C was made), lightly wrap-blurred against 8-bit noise
    tail_r, edge_r = recover_masks(src, felt_raw)
    tail = np.clip(blur_wrap(tail_r, 0.6), 0, 1)
    edge = np.clip(blur_wrap(edge_r, 0.5), 0, 1)
    tail_a, edge_a = analytic_c()
    recon = np.clip(felt_raw * (1 - C_TAIL * tail[..., None]) + edge[..., None] * C_EDGE, 0, 255)

    # 1) colour: felt grain * dark arrow fill + bright tip line, renormalised per channel to felt's mean
    col = felt * (1 - TAIL_DARK * tail)[..., None] + EDGE_GAIN * edge[..., None] * C_EDGE
    col *= felt_raw.reshape(-1, 3).mean(0) / col.reshape(-1, 3).mean(0)
    col8 = np.clip(np.round(col), 0, 255).astype(np.uint8)
    Image.fromarray(col8, "RGB").save(os.path.join(TEX, "slope_felt_color.png"), optimize=True)

    # 2) normal: felt nap slopes (decoded from felt_normal.png) + raised-arrow emboss, same convention as textures.felt():
    #    n = (-dh/dx, +dh/drow, 1) with central differences, i.e. OpenGL / Roblox (+G = up the image).
    #    Height = arrow fill (peaks right behind the tip line, ramps down upslope) + a small ridge on the tip line, so the
    #    steep face sits at the tip and faces +V (G < 128 there) and the long back ramp faces -V (G slightly > 128).
    nz = np.maximum(fn[..., 2], 1e-3)
    sx, sy = fn[..., 0] / nz, fn[..., 1] / nz          # sx = -gx, sy = gy of the felt height field
    hgt = blur_wrap(tail + 0.35 * edge, 1.2)
    gx = (np.roll(hgt, -1, 1) - np.roll(hgt, 1, 1)) * EMBOSS
    gy = (np.roll(hgt, -1, 0) - np.roll(hgt, 1, 0)) * EMBOSS
    n = np.stack([sx - gx, sy + gy, np.ones_like(gx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    nrm8 = np.clip(np.round((n * 0.5 + 0.5) * 255), 0, 255).astype(np.uint8)
    Image.fromarray(nrm8, "RGB").save(os.path.join(TEX, "slope_felt_normal.png"), optimize=True)

    # 3) roughness: 0.915 felt, arrow fill + tip line a touch smoother (crushed nap), faint grain; clamp 0.85..0.95
    lum = felt @ w
    grain = (lum - lum.mean()) / (lum.std() + 1e-9)
    rough = np.clip(0.915 - 0.035 * tail - 0.03 * edge + 0.008 * grain, 0.85, 0.95)
    rgh8 = np.round(rough * 255).astype(np.uint8)
    Image.fromarray(rgh8, "L").save(os.path.join(TEX, "slope_felt_roughness.png"), optimize=True)

    print("== slope felt set (pattern C) ==")
    print(f"masks recovered from slope_felt_C.png: corr with analytic C tail {corr(tail, tail_a):.3f}, "
          f"tip {corr(edge, edge_a):.3f}; re-synthesised C vs file: mean abs {np.abs(recon - src).mean():.2f} levels; "
          f"coverage tail {tail.mean():.3f}, tip {edge.mean():.3f}")

    # 2x2 tiles + seam numbers
    for name, arr in (("color", col8), ("normal", nrm8), ("roughness", rgh8)):
        reps = (2, 2, 1) if arr.ndim == 3 else (2, 2)
        Image.fromarray(np.tile(arr, reps)).save(os.path.join(CHECK, f"slope_felt_{name}_tile2x2.png"), optimize=True)
        su, iu, sv, iv = seam_stats(arr)
        ok = su <= 1.5 * iu + 0.5 and sv <= 1.5 * iv + 0.5
        print(f"seam {name:9s}: U wrap {su:6.3f} vs interior {iu:6.3f} | V wrap {sv:6.3f} vs interior {iv:6.3f}  -> {'OK' if ok else 'SEAM'}")
    su, iu, sv, iv = seam_stats(felt_raw)
    print(f"(felt.png itself : U wrap {su:6.3f} vs interior {iu:6.3f} | V wrap {sv:6.3f} vs interior {iv:6.3f}; "
          f"its U seam is corrected in the slope set)")

    for label, img in (("felt.png", felt_raw), ("slope_felt_color.png", col8.astype(np.float64))):
        m, (h, s, v) = hsv_mean(img)
        print(f"{label:21s}: mean RGB ({m[0]:6.2f}, {m[1]:6.2f}, {m[2]:6.2f})  HSV of mean ({h:6.2f} deg, {s:.4f}, {v:.4f})")
    cl = col8.astype(np.float64) @ w
    plain = (tail < 0.03) & (edge < 0.03)
    print(f"colour luma: arrow fill (tail>0.5) {cl[tail > 0.5].mean():.1f}, tip line (tip>0.5) {cl[edge > 0.5].mean():.1f}, "
          f"plain felt {cl[plain].mean():.1f}")
    print(f"normal: mean Z {n[..., 2].mean():.3f} (felt_normal {fn[..., 2].mean():.3f})")
    print(f"roughness: min {rough.min():.3f} max {rough.max():.3f} mean {rough.mean():.3f}")

    # ---- direction checks. Convention: +V = increasing image row (Roblox: row 0 = V 0 at the top).
    # Per-map "arrow signal", strongest at the tip: colour = brightness over felt, normal = how much the normal leans
    # toward +V (-(G - nap G)), roughness = smoothness drop. Each must (a) have its V apex at a larger row than the
    # shoulders (tip points +V), (b) correlate with the same signal built from source C, not with C flipped in V.
    nap_g = sy / np.sqrt(sx ** 2 + sy ** 2 + 1)
    sigs = {
        "source C": (src @ w) / np.maximum(felt_raw @ w, 1) - 1,
        "colour": (col8.astype(np.float64) @ w) / np.maximum(felt @ w, 1) - 1,
        "normal": -(nrm8[..., 1] / 255.0 * 2 - 1 - nap_g),
        "roughness": -(rough - 0.008 * grain),
    }
    # source-side references for (b): what each map should look like if it follows C exactly
    hs = blur_wrap(tail_r + 0.35 * edge_r, 1.2)
    refs = {"source C": sigs["source C"], "colour": sigs["source C"],
            "normal": (np.roll(hs, 1, 0) - np.roll(hs, -1, 0)), "roughness": 0.035 * tail_r + 0.03 * edge_r}
    print("direction (+V = down the image / increasing row; apex row > shoulder row => tips point +V):")
    all_ok = True
    for k, s in sigs.items():
        ac, ash = apex_rows(s)
        c0, cf, cm = corr(s, refs[k]), corr(s, refs[k][::-1]), corr(s, refs[k][:, ::-1])
        ok = ac > ash + 5 and c0 > 0.8 and c0 > cf + 0.3
        all_ok &= ok
        print(f"  {k:9s}: apex row {ac:5.1f} vs shoulders {ash:5.1f} (Δ {ac - ash:+5.1f} px toward +V) | "
              f"corr vs C {c0:+.3f}, vs C flipped V {cf:+.3f}, flipped U {cm:+.3f}  -> {'OK' if ok else 'FAIL'}")
    # tail lies upslope of the tip line: arrow fill is darker just above (-V) the tip than just below (+V)
    tip = edge > 0.5
    up = np.roll(tip, -6, 0) & ~tip & (edge < 0.1)     # 6 px toward -V
    dn = np.roll(tip, 6, 0) & ~tip & (edge < 0.1)      # 6 px toward +V
    g = nrm8[..., 1].astype(np.float64)
    front = np.roll(tip, 3, 0) & (edge < 0.3)
    print(f"  colour luma 6 px upslope of tip {cl[up].mean():.1f} vs 6 px downslope {cl[dn].mean():.1f} (dark tail is upslope)")
    print(f"  normal G just downslope of tip {g[front].mean():.1f} (<128: front face leans +V), "
          f"on the tail ramp {g[(tail > 0.2) & (tail < 0.7) & (edge < 0.05)].mean():.1f}")
    print(f"  roughness upslope {rough[up].mean():.3f} vs downslope {rough[dn].mean():.3f}")
    print(f"direction checks: {'ALL OK' if all_ok else 'FAILED'}")
    print(f"tile size: {FELT_TILE_STUDS:g} studs (StudsPerTileU = StudsPerTileV = {FELT_TILE_STUDS:g})")


if __name__ == "__main__":
    main()
