# shiplib: shared helpers for the start ship v3 detail pass (Blender 5.2, bpy + numpy only).
# Coordinates: all design numbers are ROBLOX-local (x, y up, z; stern -X, bow +X, low/sand side +Z).
# Blender mapping B(x,y,z) = (x, -z, y)  (a proper rotation, so winding is preserved).
# Hull analytic profile functions are ported verbatim from source_scripts/gen_start_ship.py (v2.3).
import math
import numpy as np

# ------------------------------------------------------------------ ship analytic profile (gen_start_ship.py v2.3)
PHI = math.radians(15); CP, SP = math.cos(PHI), math.sin(PHI)
PHIR = math.radians(18); CPR, SPR = math.cos(PHIR), math.sin(PHIR)
DECK = 24.0
L = 320.0; X0 = -160.0; BEAM = 45.0; PW = 2.2; HG = 45.2
GAP = (-130.0, -110.0); NOTCH_W = 23.0
CAB = dict(x0=-150.0, x1=-90.0, z0=-19.0, z1=24.0, wt=2.0, wall_h=16.0, peak=30.0)
DOORX = -120.0; DOOR_W = 8.0; DOOR_H = 10.0
SKIRT_Y = -2.1; SKIRT_X0, SKIRT_X1 = 85.0, 125.0
CASTLE_H = 10.0; CAS_X0, CAS_X1 = -95.0, -65.0
BS0 = (118.0, 45.0, 0.0); BS1 = (215.0, 70.0, 0.0)
FC_X0 = 112.0; FC_H = 6.0; FT = DECK + FC_H
MAIN_X, FORE_X = 10.0, 95.0
WATER_Y = -0.6   # world water level (world Y 0) expressed in the model's local frame (placement offset +0.6)


def tilt(p):
    x, y, z = p; return np.array((x, y * CP - z * SP, y * SP + z * CP), float)


def untilt(p):
    x, y, z = p; return np.array((x, y * CP + z * SP, -y * SP + z * CP), float)


def tiltR(p):
    x, y, z = p; return np.array((x, y * CPR - z * SPR, y * SPR + z * CPR), float)


def tpar(x): return (x - X0) / L
def bprof(x): return BEAM * max(0.0, 1 - tpar(x) ** 3.5) ** 0.75
def hgt(x): t = tpar(x); return HG * (1 + 0.15 * t ** 4 + 0.07 * (1 - t) ** 3)
def y0f(x): return 26 * tpar(x) ** 4
def twf(x): return min(2.5, 0.45 * bprof(x))
def cas_d(x): return CASTLE_H * min(1.0, max(0.0, (CAS_X1 - x) / (CAS_X1 - CAS_X0)))


_y0c = {}
def _y0req(x):
    k = round(x, 3)
    if k in _y0c: return _y0c[k]
    b = bprof(x); h = hgt(x); ss = np.linspace(-1, 1, 401)
    def lowest(y0): return float(np.min((y0 + (h - y0) * np.abs(ss) ** PW) * CP - ss * b * SP))
    lo, hi = -60.0, 60.0
    for _ in range(50):
        m = (lo + hi) / 2
        if lowest(m) < SKIRT_Y: lo = m
        else: hi = m
    _y0c[k] = (lo + hi) / 2; return _y0c[k]


def y0skirt(x):
    t = min(1.0, max(0.0, (x - SKIRT_X0) / (SKIRT_X1 - SKIRT_X0))); w = 0.5 * (1 + math.cos(math.pi * t))
    return y0f(x) - w * max(0.0, y0f(x) - _y0req(x))


def hull_outer(x, s):
    """analytic outer hull point (hull frame, untilted) at station x, girth parameter s in [-1,1] (+1 = low/sand side sheer)"""
    b = bprof(x); h = hgt(x); y0 = y0skirt(x)
    return np.array((x, y0 + (h - y0) * abs(s) ** PW, s * b), float)


def hull_outer_w(x, s): return tilt(hull_outer(x, s))


def hull_normal_w(x, s):
    e = 1e-3
    P = hull_outer_w(x, s); dx = hull_outer_w(x + 0.05, s) - hull_outer_w(x - 0.05, s)
    s1, s0 = min(1, s + e), max(-1, s - e); ds = hull_outer_w(x, s1) - hull_outer_w(x, s0)
    n = np.cross(dx, ds); n /= np.linalg.norm(n)
    axis = tilt((x, hgt(x) * 0.55, 0))
    if np.dot(n, P - axis) < 0: n = -n
    return n


def inner_cross(x, level=DECK):
    n = 801; b = bprof(x); h = hgt(x); y0 = y0f(x); tw = twf(x); bi = b - tw
    s = np.linspace(-1, 1, n); z = s * bi; y = y0 + tw + (h - y0 - tw) * np.abs(s) ** PW
    yw = y * CP - z * SP; zw = z * CP + y * SP
    d = yw - level; idx = np.where(np.diff(np.sign(d)))[0]
    if len(idx) < 2: return None
    def interp(i):
        t = d[i] / (d[i] - d[i + 1]); return zw[i] + t * (zw[i + 1] - zw[i])
    return interp(idx[0]), interp(idx[-1])


def deck_edges(x):
    """(HI, LO): world z of the level deck's high-side (-Z) and low-side (+Z) inner-hull edges at Y=24 (deck slab is expanded 0.6 outward)."""
    r = inner_cross(x); return (r[0] - 0.6, r[1] + 0.6) if r else None


# ------------------------------------------------------------------ small linear algebra
def nrm(v):
    v = np.asarray(v, float); l = np.linalg.norm(v); return v / l if l > 1e-12 else v


def Rx(a):
    c, s = math.cos(a), math.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Ry(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def Rz(a):
    c, s = math.cos(a), math.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def Raxis(axis, a):
    k = nrm(axis); K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(a) * K + (1 - math.cos(a)) * K @ K


def frame_from(n, hint=(1, 0, 0)):
    """R with columns (u, v, n): u = hint projected to the plane of n, v = n x u (so local x=u, y=v, z=n)."""
    n = nrm(n); u = np.asarray(hint, float) - np.dot(hint, n) * n
    if np.linalg.norm(u) < 1e-6: u = np.cross(n, (0, 1, 0))
    u = nrm(u); v = np.cross(n, u)
    return np.column_stack([u, v, n])


def B(p): return (float(p[0]), float(-p[2]), float(p[1]))
def Binv(p): return np.array((p[0], p[2], -p[1]), float)


# ------------------------------------------------------------------ mesh builder (stores BLENDER coords)
class MB:
    def __init__(s, name=''):
        s.name = name; s.V = []; s.F = []; s.M = []

    def _add(s, pts, faces, mats, tf=None):
        o = len(s.V)
        for p in pts:
            p = np.asarray(p, float)
            if tf is not None: p = tf(p)
            s.V.append(B(p))
        for f, m in zip(faces, mats):
            s.F.append([o + i for i in f]); s.M.append(m)

    def extend(s, other):
        o = len(s.V); s.V += other.V; s.F += [[o + i for i in f] for f in other.F]; s.M += other.M

    def tris(s): return sum(len(f) - 2 for f in s.F)

    # --- primitives (all inputs Roblox-local; tf maps local->Roblox model frame; R rotation about c)
    def box(s, c, size, mat, R=None, tf=None):
        c = np.asarray(c, float); hs = np.asarray(size, float) / 2; R = np.eye(3) if R is None else np.asarray(R)
        P = [c + R @ (np.array((sx, sy, sz)) * hs) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        F = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        N = [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
        mats = [mat(R @ np.array(n, float)) if callable(mat) else mat for n in N]
        s._add(P, F, mats, tf)

    def tube(s, path, radii, mat, sec=8, up=(0, 1, 0), caps=True, tf=None, rect=None, twist=0.0, phase=0.0):
        """sweep along polyline path. radii: float or list. rect: list/tuple of (w,h) half sizes per point -> rectangular section (sec ignored)."""
        P = [np.asarray(p, float) for p in path]; n = len(P)
        if not isinstance(radii, (list, tuple, np.ndarray)): radii = [radii] * n
        T = []
        for i in range(n):
            if i == 0: t = P[1] - P[0]
            elif i == n - 1: t = P[-1] - P[-2]
            else: t = nrm(P[i + 1] - P[i]) + nrm(P[i] - P[i - 1])
            T.append(nrm(t))
        a = np.asarray(up, float) - np.dot(up, T[0]) * T[0]
        if np.linalg.norm(a) < 1e-6: a = np.cross(T[0], (1, 0, 0))
        a = nrm(a); frames = []
        for i in range(n):
            if i > 0:
                a = a - np.dot(a, T[i]) * T[i]
                if np.linalg.norm(a) < 1e-9: a = np.cross(T[i], (0, 0, 1))
                a = nrm(a)
            b = np.cross(T[i], a); frames.append((a, b))
        rings = []
        for i in range(n):
            a, b = frames[i]
            if rect is not None:
                w, h = rect[i] if isinstance(rect[0], (list, tuple, np.ndarray)) else rect
                loc = [(-w, -h), (w, -h), (w, h), (-w, h)]
                rings.append([P[i] + x * b + y * a for x, y in loc])
            else:
                r = radii[i]; ang0 = phase + twist * i
                rings.append([P[i] + r * (math.cos(ang0 + 2 * math.pi * k / sec) * a + math.sin(ang0 + 2 * math.pi * k / sec) * b) for k in range(sec)])
        m = len(rings[0]); pts = [p for r in rings for p in r]; F = []
        for i in range(n - 1):
            for k in range(m):
                j = (k + 1) % m; F.append((i * m + k, i * m + j, (i + 1) * m + j, (i + 1) * m + k))
        if caps:
            F.append(tuple(range(m))[::-1]); F.append(tuple((n - 1) * m + k for k in range(m)))
        mats = [mat] * len(F) if not callable(mat) else [mat(i) for i in range(len(F))]
        s._add(pts, F, mats, tf)

    def frustum(s, p0, p1, r0, r1, mat, sec=8, tf=None, up=(0, 1, 0), phase=0.0):
        s.tube([p0, p1], [r0, r1], mat, sec=sec, tf=tf, up=up, phase=phase)

    def torus(s, c, axis, R, r, mat, nu=12, nv=6, tf=None):
        c = np.asarray(c, float); Fm = frame_from(axis, (1, 0, 0) if abs(nrm(axis)[0]) < 0.9 else (0, 1, 0))
        u, v, n = Fm[:, 0], Fm[:, 1], Fm[:, 2]; pts = []
        for i in range(nu):
            a = 2 * math.pi * i / nu; d = math.cos(a) * u + math.sin(a) * v
            for j in range(nv):
                b = 2 * math.pi * j / nv; pts.append(c + (R + r * math.cos(b)) * d + r * math.sin(b) * n)
        F = []
        for i in range(nu):
            for j in range(nv):
                i2 = (i + 1) % nu; j2 = (j + 1) % nv
                F.append((i * nv + j, i2 * nv + j, i2 * nv + j2, i * nv + j2))
        s._add(pts, F, [mat] * len(F), tf)

    def ellipsoid(s, c, radii, mat, R=None, nu=10, nv=6, tf=None, cut_below=None):
        c = np.asarray(c, float); R = np.eye(3) if R is None else np.asarray(R); pts = []; rx, ry, rz = radii
        pts.append(c + R @ np.array((0, -ry, 0)))
        for j in range(1, nv):
            ph = -math.pi / 2 + math.pi * j / nv
            for i in range(nu):
                th = 2 * math.pi * i / nu
                pts.append(c + R @ np.array((rx * math.cos(ph) * math.cos(th), ry * math.sin(ph), rz * math.cos(ph) * math.sin(th))))
        pts.append(c + R @ np.array((0, ry, 0))); top = len(pts) - 1; F = []
        for i in range(nu): F.append((0, 1 + (i + 1) % nu, 1 + i))
        for j in range(nv - 2):
            for i in range(nu):
                a = 1 + j * nu + i; b = 1 + j * nu + (i + 1) % nu; F.append((a, b, b + nu, a + nu))
        base = 1 + (nv - 2) * nu
        for i in range(nu): F.append((base + i, base + (i + 1) % nu, top))
        mats = []
        for f in F:
            cc = np.mean([pts[k] for k in f], axis=0) - c
            mats.append(mat(nrm(cc)) if callable(mat) else mat)
        s._add(pts, F, mats, tf)

    def loft(s, rings, mat, caps=True, tf=None, centre_hint=None):
        """rings: list of equal-length point loops. mat callable(outward normal) or str."""
        n = len(rings); m = len(rings[0]); pts = [np.asarray(p, float) for r in rings for p in r]; F = []
        for i in range(n - 1):
            for k in range(m):
                j = (k + 1) % m; F.append((i * m + k, i * m + j, (i + 1) * m + j, (i + 1) * m + k))
        if caps:
            F.append(tuple(range(m))[::-1]); F.append(tuple((n - 1) * m + k for k in range(m)))
        mats = []
        for fi, f in enumerate(F):
            q = [pts[k] for k in f]; nv_ = np.zeros(3)
            for a in range(len(q)): nv_ += np.cross(q[a], q[(a + 1) % len(q)])
            if fi < (n - 1) * m:
                ring_c = np.mean(rings[fi // m], axis=0); out = np.mean(q, axis=0) - ring_c
                if np.dot(nv_, out) < 0: nv_ = -nv_
            mats.append(mat(nrm(nv_)) if callable(mat) else mat)
        s._add(pts, F, mats, tf)

    def thick_surface(s, fn, nu, nv, th, mat, tf=None, side_mat=None):
        """closed slab from a parametric surface fn(u,v)->(point, normal) sampled on (nu+1)x(nv+1); thickness th centred."""
        G = [[fn(i / nu, j / nv) for j in range(nv + 1)] for i in range(nu + 1)]
        pts = []
        idx = lambda i, j, side: 2 * (i * (nv + 1) + j) + side
        for i in range(nu + 1):
            for j in range(nv + 1):
                p, n_ = G[i][j]; p = np.asarray(p, float); n_ = nrm(n_)
                pts.append(p + n_ * th / 2); pts.append(p - n_ * th / 2)
        F = []; M = []
        for i in range(nu):
            for j in range(nv):
                F.append((idx(i, j, 0), idx(i + 1, j, 0), idx(i + 1, j + 1, 0), idx(i, j + 1, 0))); M.append(mat)
                F.append((idx(i, j, 1), idx(i, j + 1, 1), idx(i + 1, j + 1, 1), idx(i + 1, j, 1))); M.append(mat)
        sm = side_mat or mat
        for i in range(nu):
            for j in (0, nv):
                F.append((idx(i, j, 0), idx(i, j, 1), idx(i + 1, j, 1), idx(i + 1, j, 0))); M.append(sm)
        for j in range(nv):
            for i in (0, nu):
                F.append((idx(i, j, 0), idx(i, j + 1, 0), idx(i, j + 1, 1), idx(i, j, 1))); M.append(sm)
        s._add(pts, F, M, tf)


def arc_path(c, r0, r1, a0, a1, n, plane_u, plane_v):
    """spiral/arc points c + r(t)*(cos a * u + sin a * v)"""
    c = np.asarray(c, float); u = np.asarray(plane_u, float); v = np.asarray(plane_v, float); out = []
    for i in range(n + 1):
        t = i / n; a = a0 + (a1 - a0) * t; r = r0 + (r1 - r0) * t
        out.append(c + r * (math.cos(a) * u + math.sin(a) * v))
    return out


def untiltR(p):   # v3_1: inverse of tiltR (18 deg rigging roll frame)
    x, y, z = p; return np.array((x, y * CPR + z * SPR, -y * SPR + z * CPR), float)
