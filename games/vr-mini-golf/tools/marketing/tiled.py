"""Render a 1920x1080 still from several Studio MCP screen_captures (pitch/yaw tiles from one camera point, narrow
FOV) reprojected onto one target camera. Pure rotations about the camera centre -> exact homographies."""
import sys, os, json, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cap

TW, TH = 1920, 1080

def basis(c, l):
    f = np.array(l, float) - np.array(c, float); f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1, 0]); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return r, u, f

def render(name, c, l, vfov, outdir, rawdir, clock=None, margin=0.12):
    W, H = 1469, 789
    tv = math.tan(math.radians(vfov) / 2); th = tv * TW / TH
    ft = (TH / 2) / tv
    tvc = (H / 2) / (ft * 1.0)       # tile tan half-height (native res)
    thc = tvc * W / H
    nx = max(1, math.ceil((2 * th) / (2 * thc * (1 - margin))))
    ny = max(1, math.ceil((2 * tv) / (2 * tvc * (1 - margin))))
    vc = 2 * math.degrees(math.atan(tvc))
    xs = [0.0] if nx == 1 else list(np.linspace(-th + thc * (1 - margin), th - thc * (1 - margin), nx))
    ys = [0.0] if ny == 1 else list(np.linspace(-tv + tvc * (1 - margin), tv - tvc * (1 - margin), ny))
    r, u, f = basis(c, l)
    setup = "workspace.CurrentCamera.FieldOfView = %.4f; game.Selection:Set({})" % vc
    setup += "; game.Lighting.ClockTime = %s" % (clock if clock is not None else 17.1)
    cap.luau(setup)
    tiles = []
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            d = f + x * r + y * u
            look = (np.array(c) + d * 10).tolist()
            p = os.path.join(rawdir, "%s_%d_%d.jpg" % (name, j, i))
            cap.capture(p, list(c), look)
            tiles.append((p, basis(c, look)))
    # target rays
    uu, vv = np.meshgrid(np.arange(TW) + 0.5, np.arange(TH) + 0.5)
    dx = (uu - TW / 2) / ft; dy = -(vv - TH / 2) / ft
    rays = f[None, None, :] + dx[..., None] * r + dy[..., None] * u
    acc = np.zeros((TH, TW, 3)); wsum = np.zeros((TH, TW))
    fc = (H / 2) / tvc
    for p, (r2, u2, f2) in tiles:
        img = np.asarray(Image.open(p).convert("RGB"), dtype=np.float64)
        h_, w_ = img.shape[:2]
        z = rays @ f2
        px = w_ / 2 + fc * (rays @ r2) / z - 0.5
        py = h_ / 2 - fc * (rays @ u2) / z - 0.5
        nxn = np.abs(px - w_ / 2) / (w_ / 2); nyn = np.abs(py - h_ / 2) / (h_ / 2)
        wgt = np.clip(np.minimum(1 - nxn, 1 - nyn), 0, None) * (z > 0)
        wgt = np.minimum(wgt / 0.06, 1.0) ** 2  # feather the outer 6%
        x0 = np.clip(np.floor(px).astype(int), 0, w_ - 2); y0 = np.clip(np.floor(py).astype(int), 0, h_ - 2)
        ax = np.clip(px - x0, 0, 1)[..., None]; ay = np.clip(py - y0, 0, 1)[..., None]
        s = (img[y0, x0] * (1 - ax) * (1 - ay) + img[y0, x0 + 1] * ax * (1 - ay) +
             img[y0 + 1, x0] * (1 - ax) * ay + img[y0 + 1, x0 + 1] * ax * ay)
        acc += s * wgt[..., None]; wsum += wgt
    holes = int((wsum < 1e-6).sum())
    out = acc / np.maximum(wsum, 1e-6)[..., None]
    path = os.path.join(outdir, name + ".png")
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(path)
    return {"name": name, "tiles": len(tiles), "grid": [nx, ny], "tileFov": round(vc, 2), "uncovered": holes, "path": path}

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    outdir, rawdir = sys.argv[2], sys.argv[3]
    only = sys.argv[4].split(",") if len(sys.argv) > 4 else None
    os.makedirs(outdir, exist_ok=True); os.makedirs(rawdir, exist_ok=True)
    try:
        for s in spec:
            if only and s["name"] not in only:
                continue
            print(json.dumps(render(s["name"], s["cam"], s["look"], s.get("fov", 60), outdir, rawdir, s.get("clock"))), flush=True)
    finally:
        cap.luau("workspace.CurrentCamera.FieldOfView = 70; game.Lighting.ClockTime = 17.1")
