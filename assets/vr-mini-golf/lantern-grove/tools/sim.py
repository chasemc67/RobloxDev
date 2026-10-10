#!/usr/bin/env python3
"""Lantern Grove playtest simulator + geometry validator.

    python3 tools/sim.py                 # validate + HIO search + 2000 plays/skill/hole
    python3 tools/sim.py --holes 1 4 --n 4000 --tag r2
    python3 tools/sim.py --validate-only

Needs numpy (+ numba for speed; falls back to pure Python, ~100x slower).
On the Mac: uv run --with numpy --with numba --with matplotlib python tools/sim.py

Physics = RobloxDevBot's real in-game values (all studs / seconds, 1 stud = 0.3 m):
  g = 32.7 studs/s^2 (9.81 m/s^2), slope accel = g*sin(theta) down the fall line
  rolling deceleration = 0.5 + 0.25*v studs/s^2
  max putt speed V_MAX = 19.8 studs/s (5.9 m/s), derived so a max putt rolls 60 studs (18 m) on flat felt:
      flat roll distance D(v) = v/k - (a/k^2) ln(1 + k v/a) with a=0.5, k=0.25;  D(19.8) = 60.
      60 studs = the longest single-stroke run the course asks for (H6/H9 ace lines: ~45 studs of travel plus a
      climb and two deflections). Longer holes (H8 long route ~95 studs) are designed as multi-shot holes.
  restitution: rails/deflectors 0.63, bumpers (static obstacle blocks + all moving blockers) 0.65
      (normal component scaled, tangential kept; moving blockers add their surface velocity)
  ball stops when v < 0.05 and slope accel < 0.5 (same as rolling resistance at rest)
  drops: ball leaving a piece onto felt >0.4 lower keeps 80% of horizontal speed
  cup: radius 0.5, holed when centre within radius and speed < 5.33 studs/s (1.6 m/s)
  hazard/escape: ball returns to its stroke start, +1 stroke. Cap 8 strokes.
  dt = 1/240 s, 30 s timeout per stroke.
"""
import argparse, json, math, os, sys, time
import numpy as np

try:
    from numba import njit, prange
    HAVE_NUMBA = True
except Exception:  # pragma: no cover
    HAVE_NUMBA = False
    prange = range

    def njit(*a, **k):
        if a and callable(a[0]):
            return a[0]
        return lambda f: f

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))

# ---------------------------------------------------------------- parameters
# Real Roblox values from RobloxDevBot (see docstring). Everything below reads from here.
STUD_M = 0.3                 # metres per stud
GRAVITY = 32.7               # studs/s^2
ROLL_DECEL_CONST = 0.5       # studs/s^2   rolling deceleration = 0.5 + 0.25*speed
ROLL_DECEL_PER_SPEED = 0.25  # 1/s
WALL_RESTITUTION = 0.63
BUMPER_RESTITUTION = 0.65
CUP_CAPTURE_SPEED = 5.33     # studs/s (1.6 m/s)
CUP_RADIUS = 0.5             # gameplay cup radius (real 4.25in cup = 0.36 stud diameter)
BALL_RADIUS = 0.08
MAX_PUTT_STUDS = 60.0        # design target for a full-power putt on flat felt


def _flat_dist(v, a=ROLL_DECEL_CONST, k=ROLL_DECEL_PER_SPEED):
    return v / k - (a / (k * k)) * math.log(1 + k * v / a)


def _derive_vmax(d=MAX_PUTT_STUDS):
    lo, hi = 0.0, 100.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if _flat_dist(mid) < d else (lo, mid)
    return round(0.5 * (lo + hi), 2)


V_MAX = _derive_vmax()       # = 19.8 studs/s

PHYS = dict(g=GRAVITY, roll_decel=ROLL_DECEL_CONST, drag=ROLL_DECEL_PER_SPEED, v_max=V_MAX,
            restitution=WALL_RESTITUTION, v_cup=CUP_CAPTURE_SPEED, cup_r=CUP_RADIUS, ball_r=BALL_RADIUS,
            step_tol=0.15, static_accel=ROLL_DECEL_CONST, v_stop=0.05, drop_damp=0.8, dt=1.0 / 240,
            t_max=30.0, bumper_restitution=BUMPER_RESTITUTION)
SKILLS = {  # aim sigma (deg), power sigma (fraction of intended speed)
    # ace_try: chance the golfer goes for the hole's known ace line from the tee (brute-force line, robust centre)
    # ace attempts use the line as remembered: extra per-attempt error ace_aim_sd (deg) / ace_pow_sd (fraction)
    "good": dict(aim_sd=1.0, pow_sd=0.05, ace_try=0.3, ace_aim_sd=1.5, ace_pow_sd=0.08),
    "average": dict(aim_sd=2.5, pow_sd=0.12, ace_try=0.0),
}
CAP = 8
PH_KEYS = ["g", "roll_decel", "drag", "v_max", "restitution", "v_cup", "cup_r", "ball_r", "step_tol",
           "static_accel", "v_stop", "drop_damp", "dt", "t_max", "bumper_restitution"]


def ph_array():
    return np.array([PHYS[k] for k in PH_KEYS], dtype=np.float64)


# ---------------------------------------------------------------- compile JSON -> arrays
def yaw_R(yaw_deg):
    a = math.radians(yaw_deg)
    c, s = math.cos(a), math.sin(a)
    # columns = local axes in world. local x -> (c,0,-s), local y -> (0,1,0), local z -> (s,0,c)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float64)


class HoleArrays:
    def __init__(self, hole):
        self.hole = hole
        felt = hole["felt"]
        self.piece_ids = [p["id"] for p in felt]
        zones = []
        for p in felt:
            if p["zone"] not in zones:
                zones.append(p["zone"])
        self.zones = zones
        P = np.zeros((len(felt), 13))
        for i, p in enumerate(felt):
            a = math.radians(p.get("yaw", 0.0))
            sl = p.get("slope")
            axis = -1 if not sl else (0 if sl["axis"] == "x" else 1)
            P[i] = [p["center"][0], p["center"][1], p["center"][2], p["size"][0] / 2, p["size"][1] / 2,
                    math.cos(a), math.sin(a), axis, (sl["rise"] if sl else 0.0), 0,
                    0.0 if p.get("solid", True) is False else 1.0, p.get("thickness", 0.4),
                    1.0 if p.get("overlay") else 0.0]
        self.P = P
        self.pzone = np.array([zones.index(p["zone"]) for p in felt], dtype=np.int64)
        W = np.zeros((max(1, len(hole["walls"])), 18))
        for i, w in enumerate(hole["walls"]):
            R = yaw_R(w.get("yaw", 0.0))
            c, s = w["center"], w["size"]
            W[i, 0:3] = c
            W[i, 3:6] = [s[0] / 2, s[1] / 2, s[2] / 2]
            W[i, 6:15] = R.reshape(-1)
            W[i, 15] = c[1] - s[1] / 2
            W[i, 16] = c[1] + s[1] / 2
            W[i, 17] = BUMPER_RESTITUTION if w.get("kind") == "bumper" else WALL_RESTITUTION
        self.nW = len(hole["walls"])
        self.W = W
        mps = hole.get("moving_parts", [])
        MP = np.zeros((max(1, len(mps)), 12))
        MB = []
        for j, m in enumerate(mps):
            rot = m["type"] == "rotate"
            ax = np.array(m["axis"], float)
            ax /= np.linalg.norm(ax)
            sp = math.radians(m["speed"]) if rot else m["speed"]
            rng = m.get("range")
            ph = m.get("phase", 0.0)
            ph = math.radians(ph) if rot else ph
            if rng:
                lo, hi = (math.radians(rng[0]), math.radians(rng[1])) if rot else (rng[0], rng[1])
            else:
                lo = hi = 0.0
            MP[j] = [0 if rot else 1, *m["pivot"], *ax, sp, 1.0 if rng else 0.0, lo, hi, ph]
            for b in m["blockers"]:
                R0 = yaw_R(b.get("yaw", 0.0))
                cen = np.array(b["center"], float)
                if b.get("roll"):  # initial rotation about the part axis (e.g. wheel paddles at 0/120/240)
                    Rr = np.zeros(9)
                    axis_rot(ax[0], ax[1], ax[2], math.radians(b["roll"]), Rr)
                    Rr = Rr.reshape(3, 3)
                    cen = Rr @ cen
                    R0 = Rr @ R0
                MB.append([j, *cen, b["size"][0] / 2, b["size"][1] / 2, b["size"][2] / 2, *R0.reshape(-1)])
        self.nMP = len(mps)
        self.MP = MP
        self.MB = np.array(MB, dtype=np.float64) if MB else np.zeros((1, 16))
        self.nMB = len(MB)
        tps = hole.get("teleports", [])
        TP = np.zeros((max(1, len(tps)), 12))
        for j, t in enumerate(tps):
            TP[j] = [*t["entry"]["center"], t["entry"]["radius"], *t["exit"]["center"], *t["exit"]["dir"],
                     t.get("speed_factor", 0.8), t.get("min_speed", 2.0), t.get("max_speed", 8.0)]
        self.nTP = len(tps)
        self.TP = TP
        hz = hole.get("hazards", [])
        HZ = np.zeros((max(1, len(hz)), 7))
        for j, h in enumerate(hz):
            a = math.radians(h.get("yaw", 0.0))
            HZ[j] = [*h["center"], h["size"][0] / 2, h["size"][1] / 2, math.cos(a), math.sin(a)]
        self.nHZ = len(hz)
        self.HZ = HZ
        cp = hole["cup"]
        self.CUP = np.array([*cp["position"], cp.get("radius", PHYS["cup_r"])], dtype=np.float64)
        self.TEE = np.array(hole["tee"]["position"], dtype=np.float64)

    def waypoints(self, skill):
        wps = self.hole.get("ai_waypoints", {})
        lst = wps.get(skill, wps.get("all", []))
        nz = len(self.zones)
        WP = np.zeros((max(1, len(lst)), 5))
        M = np.zeros((max(1, len(lst)), nz), dtype=np.bool_)
        for k, w in enumerate(lst):
            WP[k] = [*w["pos"], w.get("carry", 1.0), w.get("power_scale", 1.0)]
            for zname in w.get("from", self.zones):
                if zname in self.zones:
                    M[k, self.zones.index(zname)] = True
                else:
                    raise ValueError(f"{self.hole['id']}: waypoint {w['id']} unknown zone {zname}")
        cf = self.hole.get("cup_from")
        CM = np.ones(nz, dtype=np.bool_)
        if cf:
            CM[:] = False
            for zname in cf:
                CM[self.zones.index(zname)] = True
        return WP, M, len(lst), CM

    def args(self):
        return (self.P, self.W, self.nW, self.MP, self.nMP, self.MB, self.nMB, self.TP, self.nTP,
                self.HZ, self.nHZ, self.CUP)


# ---------------------------------------------------------------- numba kernels
@njit(cache=True)
def piece_local(P, i, x, z):
    dx = x - P[i, 0]
    dz = z - P[i, 2]
    c = P[i, 5]
    s = P[i, 6]
    return dx * c - dz * s, dx * s + dz * c


@njit(cache=True)
def piece_h(P, i, lx, lz):
    ax = P[i, 7]
    if ax == 0:
        return P[i, 1] + P[i, 8] * lx / (2 * P[i, 3])
    elif ax == 1:
        return P[i, 1] + P[i, 8] * lz / (2 * P[i, 4])
    return P[i, 1]


@njit(cache=True)
def piece_grad(P, i):
    """world-space gradient (dh/dx, dh/dz) of piece i."""
    ax = P[i, 7]
    if ax < 0:
        return 0.0, 0.0
    if ax == 0:
        glx, glz = P[i, 8] / (2 * P[i, 3]), 0.0
    else:
        glx, glz = 0.0, P[i, 8] / (2 * P[i, 4])
    c = P[i, 5]
    s = P[i, 6]
    # world vector of local gradient (covector maps the same way for rotations)
    return glx * c + glz * s, -glx * s + glz * c


@njit(cache=True)
def support(P, x, z, y, tol, r):
    """highest felt under (x,z) reachable from height y; blocking cliff if a solid piece rises above."""
    best = -1
    bh = -1e9
    blk = -1
    blkh = 1e9
    for i in range(P.shape[0]):
        lx, lz = piece_local(P, i, x, z)
        if abs(lx) <= P[i, 3] + 1e-3 and abs(lz) <= P[i, 4] + 1e-3:
            h = piece_h(P, i, lx, lz)
            if h <= y + tol:
                if h > bh:
                    bh = h
                    best = i
            else:
                if P[i, 10] > 0.5 or (h - P[i, 11]) < y + 2 * r + 0.05:
                    if h < blkh:
                        blkh = h
                        blk = i
    return best, bh, blk


@njit(cache=True)
def sphere_box(px, py, pz, cx, cy, cz, hx, hy, hz, R, r):
    """sphere vs oriented box. R: 9-array row-major, columns = local axes. returns pen, nx, nz (horizontal)."""
    dx = px - cx
    dy = py - cy
    dz = pz - cz
    l0 = R[0] * dx + R[3] * dy + R[6] * dz
    l1 = R[1] * dx + R[4] * dy + R[7] * dz
    l2 = R[2] * dx + R[5] * dy + R[8] * dz
    c0 = min(max(l0, -hx), hx)
    c1 = min(max(l1, -hy), hy)
    c2 = min(max(l2, -hz), hz)
    e0 = l0 - c0
    e1 = l1 - c1
    e2 = l2 - c2
    d2 = e0 * e0 + e1 * e1 + e2 * e2
    if d2 >= r * r:
        return 0.0, 0.0, 0.0
    if d2 > 1e-12:
        d = math.sqrt(d2)
        n0, n1, n2 = e0 / d, e1 / d, e2 / d
        pen = r - d
    else:
        # centre inside the box: push out across the box's thinner horizontal axis (rails, arms, gates)
        fx = hx - abs(l0)
        fz = hz - abs(l2)
        n1 = 0.0
        if hx <= hz:
            n0 = 1.0 if l0 >= 0 else -1.0
            n2 = 0.0
            pen = r + fx
        else:
            n2 = 1.0 if l2 >= 0 else -1.0
            n0 = 0.0
            pen = r + fz
    wx = R[0] * n0 + R[1] * n1 + R[2] * n2
    wz = R[6] * n0 + R[7] * n1 + R[8] * n2
    hn = math.sqrt(wx * wx + wz * wz)
    if hn < 0.3:
        return 0.0, 0.0, 0.0
    return pen, wx / hn, wz / hn


@njit(cache=True)
def part_state(MP, j, t):
    sp = MP[j, 7]
    if MP[j, 8] < 0.5:
        return MP[j, 11] + sp * t, sp
    a = MP[j, 9]
    b = MP[j, 10]
    span = b - a
    if span <= 0:
        return a, 0.0
    per = 2 * span
    u = (MP[j, 11] - a) + abs(sp) * t
    u = u - per * math.floor(u / per)
    if u < span:
        return a + u, abs(sp)
    return b - (u - span), -abs(sp)


@njit(cache=True)
def axis_rot(kx, ky, kz, th, out):
    c = math.cos(th)
    s = math.sin(th)
    C = 1 - c
    out[0] = c + kx * kx * C
    out[1] = kx * ky * C - kz * s
    out[2] = kx * kz * C + ky * s
    out[3] = ky * kx * C + kz * s
    out[4] = c + ky * ky * C
    out[5] = ky * kz * C - kx * s
    out[6] = kz * kx * C - ky * s
    out[7] = kz * ky * C + kx * s
    out[8] = c + kz * kz * C


@njit(cache=True)
def matmul3(A, B, out):
    for i in range(3):
        for j in range(3):
            out[i * 3 + j] = A[i * 3] * B[j] + A[i * 3 + 1] * B[3 + j] + A[i * 3 + 2] * B[6 + j]


@njit(cache=True)
def blocker_pose(MP, MB, k, t, Rth, Rw, cen):
    """fills Rw (box rotation) and cen (centre); returns (kind, rate, j)."""
    j = int(MB[k, 0])
    val, rate = part_state(MP, j, t)
    if MP[j, 0] == 0:  # rotate
        axis_rot(MP[j, 4], MP[j, 5], MP[j, 6], val, Rth)
        ox, oy, oz = MB[k, 1], MB[k, 2], MB[k, 3]
        cen[0] = MP[j, 1] + Rth[0] * ox + Rth[1] * oy + Rth[2] * oz
        cen[1] = MP[j, 2] + Rth[3] * ox + Rth[4] * oy + Rth[5] * oz
        cen[2] = MP[j, 3] + Rth[6] * ox + Rth[7] * oy + Rth[8] * oz
        matmul3(Rth, MB[k, 7:16], Rw)
    else:
        cen[0] = MP[j, 1] + MB[k, 1] + MP[j, 4] * val
        cen[1] = MP[j, 2] + MB[k, 2] + MP[j, 5] * val
        cen[2] = MP[j, 3] + MB[k, 3] + MP[j, 6] * val
        for q in range(9):
            Rw[q] = MB[k, 7 + q]
    return MP[j, 0], rate, j


@njit(cache=True)
def in_hazard(HZ, nHZ, x, z):
    for j in range(nHZ):
        dx = x - HZ[j, 0]
        dz = z - HZ[j, 2]
        c = HZ[j, 5]
        s = HZ[j, 6]
        lx = dx * c - dz * s
        lz = dx * s + dz * c
        if abs(lx) <= HZ[j, 3] and abs(lz) <= HZ[j, 4]:
            return j
    return -1


@njit(cache=True)
def sim_shot(P, W, nW, MP, nMP, MB, nMB, TP, nTP, HZ, nHZ, CUP, PH,
             x, z, y, vx, vz, t0, rec, path):
    """simulate one stroke. outcome: 0 stopped, 1 holed, 2 hazard, 3 escaped, 4 timeout.
    returns x, z, y, outcome, elapsed, min_cup_dist, n_path."""
    g = PH[0]; a_r = PH[1]; kd = PH[2]; e = PH[4]; vcup = PH[5]; br = PH[7]
    tol = PH[8]; a_st = PH[9]; vstop = PH[10]; ddamp = PH[11]; dt = PH[12]; tmax = PH[13]
    Rth = np.empty(9)
    Rw = np.empty(9)
    cen = np.empty(3)
    t = t0
    tpcool = 0.0
    mind = 1e9
    npath = 0
    nsteps = int(tmax / dt)
    cur, h0, b0 = support(P, x, z, y + 0.01, tol, br)
    if cur >= 0:
        y = h0
    outcome = 4
    touching = False
    for step in range(nsteps):
        if rec and step % 6 == 0 and npath < path.shape[0]:
            path[npath, 0] = x; path[npath, 1] = y; path[npath, 2] = z
            npath += 1
        # --- forces
        gx = 0.0; gz = 0.0
        if cur >= 0:
            gx, gz = piece_grad(P, cur)
        gm = math.sqrt(gx * gx + gz * gz)
        a_sl = 0.0
        ax = 0.0; az = 0.0
        if gm > 1e-9:
            sinth = gm / math.sqrt(1 + gm * gm)
            a_sl = g * sinth
            ax = -a_sl * gx / gm
            az = -a_sl * gz / gm
        sp = math.sqrt(vx * vx + vz * vz)
        if sp < vstop and a_sl < a_st:
            outcome = 0
            break
        if touching and sp < 0.3:
            outcome = 0  # resting against a rail/cliff on a slope: gravity just presses it into the wall
            break
        touching = False
        vx += ax * dt
        vz += az * dt
        sp = math.sqrt(vx * vx + vz * vz)
        dec = (a_r + kd * sp) * dt
        if sp <= dec:
            vx = 0.0; vz = 0.0
        else:
            f = (sp - dec) / sp
            vx *= f; vz *= f
        ox = x; oz = z
        nx = x + vx * dt
        nz = z + vz * dt
        best, bh, blk = support(P, nx, nz, y, tol, br)
        if blk >= 0:
            lx, lz = piece_local(P, blk, x, z)
            ex = abs(lx) - P[blk, 3]
            ez = abs(lz) - P[blk, 4]
            c = P[blk, 5]; s = P[blk, 6]
            if ex > ez:
                nlx = 1.0 if lx > 0 else -1.0
                wx, wz = nlx * c, -nlx * s
            else:
                nlz = 1.0 if lz > 0 else -1.0
                wx, wz = nlz * s, nlz * c
            vn = vx * wx + vz * wz
            touching = True
            if vn < 0:
                vx -= (1 + e) * vn * wx
                vz -= (1 + e) * vn * wz
        else:
            x = nx; z = nz
        # --- walls & moving blockers (2 passes) at the current level, before deciding on support
        cy = y + br
        for ps in range(2):
            bp = 0.0; bnx = 0.0; bnz = 0.0; bvx = 0.0; bvz = 0.0; ec = e
            for k in range(nW):
                pen, wnx, wnz = sphere_box(x, cy, z, W[k, 0], W[k, 1], W[k, 2], W[k, 3], W[k, 4], W[k, 5], W[k, 6:15], br)
                if pen > bp:
                    bp = pen; bnx = wnx; bnz = wnz; bvx = 0.0; bvz = 0.0; ec = W[k, 17]
            for k in range(nMB):
                kind, rate, j = blocker_pose(MP, MB, k, t, Rth, Rw, cen)
                pen, wnx, wnz = sphere_box(x, cy, z, cen[0], cen[1], cen[2], MB[k, 4], MB[k, 5], MB[k, 6], Rw, br)
                if pen > bp:
                    bp = pen; bnx = wnx; bnz = wnz; ec = PH[14]
                    if kind == 0:
                        rx = x - MP[j, 1]; ry = cy - MP[j, 2]; rz = z - MP[j, 3]
                        wxv = MP[j, 4] * rate; wyv = MP[j, 5] * rate; wzv = MP[j, 6] * rate
                        bvx = wyv * rz - wzv * ry
                        bvz = wxv * ry - wyv * rx
                    else:
                        bvx = MP[j, 4] * rate
                        bvz = MP[j, 6] * rate
            if bp <= 0:
                break
            touching = True
            x += bnx * bp
            z += bnz * bp
            rvx = vx - bvx; rvz = vz - bvz
            vn = rvx * bnx + rvz * bnz
            if vn < 0:
                rvx -= (1 + ec) * vn * bnx
                rvz -= (1 + ec) * vn * bnz
            vx = rvx + bvx; vz = rvz + bvz
        # --- support at the resolved position
        b2, bh2, k2 = support(P, x, z, y, tol, br)
        if k2 >= 0:
            x = ox; z = oz  # a blocker shoved the ball into a cliff face: keep it where it was
        elif b2 < 0:
            if in_hazard(HZ, nHZ, x, z) >= 0:
                outcome = 2
            else:
                outcome = 3
            break
        else:
            if y - bh2 > 0.4:
                vx *= ddamp; vz *= ddamp
            y = bh2; cur = b2
        # --- teleports
        if tpcool > 0:
            tpcool -= dt
        else:
            for j in range(nTP):
                ddx = x - TP[j, 0]; ddz = z - TP[j, 2]
                if ddx * ddx + ddz * ddz < TP[j, 3] * TP[j, 3] and abs(y - TP[j, 1]) < 0.5:
                    sp = math.sqrt(vx * vx + vz * vz)
                    ns = min(max(sp * TP[j, 9], TP[j, 10]), TP[j, 11])
                    x = TP[j, 4]; y = TP[j, 5]; z = TP[j, 6]
                    vx = TP[j, 7] * ns; vz = TP[j, 8] * ns
                    b3, bh3, k3 = support(P, x, z, y + 0.01, tol, br)
                    if b3 >= 0:
                        cur = b3; y = bh3
                    tpcool = 0.5
                    break
        # --- cup
        cdx = x - CUP[0]; cdz = z - CUP[2]
        cd = math.sqrt(cdx * cdx + cdz * cdz)
        if abs(y - CUP[1]) < 0.3:
            if cd < mind:
                mind = cd
            if cd < CUP[3] and math.sqrt(vx * vx + vz * vz) < vcup:
                outcome = 1
                x = CUP[0]; z = CUP[2]
                break
        t += dt
    if rec and npath < path.shape[0]:
        path[npath, 0] = x; path[npath, 1] = y; path[npath, 2] = z
        npath += 1
    return x, z, y, outcome, t - t0, mind, npath


@njit(cache=True)
def los(P, W, nW, x, z, y, tx, tz, ty, br):
    dx = tx - x; dz = tz - z
    d = math.sqrt(dx * dx + dz * dz)
    n = int(d / 0.35) + 1
    hp = y
    for q in range(1, n + 1):
        f = q / n
        px = x + dx * f; pz = z + dz * f
        best, bh, blk = support(P, px, pz, hp, 0.3, br)
        if blk >= 0 or best < 0:
            return False
        hp = bh
        for k in range(nW):
            if W[k, 16] <= hp + br or W[k, 15] >= hp + br:
                continue
            ddx = px - W[k, 0]; ddz = pz - W[k, 2]
            lx = W[k, 6] * ddx + W[k, 12] * ddz
            lz = W[k, 8] * ddx + W[k, 14] * ddz
            if abs(lx) <= W[k, 3] + br and abs(lz) <= W[k, 5] + br:
                return False
    return True


@njit(cache=True)
def flat_dist(v, a, k):
    return v / k - (a / (k * k)) * math.log(1 + k * v / a)


@njit(cache=True)
def speed_for(d, a, k, vmax):
    lo = 0.0; hi = vmax
    if flat_dist(hi, a, k) <= d:
        return vmax
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if flat_dist(mid, a, k) < d:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


@njit(cache=True)
def plan(P, pzone, W, nW, CUP, WP, WPM, nWP, CM, PH, x, z, y, zone):
    br = PH[7]
    # furthest allowed target with line of sight: cup, then waypoints last -> first.
    # No line of sight to anything: fall back to the furthest allowed waypoint (else the cup).
    chosen = -2; fb = -2
    if zone < 0 or CM[zone]:
        if los(P, W, nW, x, z, y, CUP[0], CUP[2], CUP[1], br):
            chosen = -1
    if chosen == -2:
        for kk in range(nWP - 1, -1, -1):
            if zone < 0 or WPM[kk, zone]:
                if fb == -2:
                    fb = kk
                if los(P, W, nW, x, z, y, WP[kk, 0], WP[kk, 2], WP[kk, 1], br):
                    chosen = kk
                    break
    if chosen == -2:
        chosen = fb if fb != -2 else -1
    if chosen == -1:
        tx, ty, tz, carry, ps = CUP[0], CUP[1], CUP[2], 0.8, 1.0
    else:
        tx, ty, tz, carry, ps = WP[chosen, 0], WP[chosen, 1], WP[chosen, 2], WP[chosen, 3], WP[chosen, 4]
    dx = tx - x; dz = tz - z
    d = math.sqrt(dx * dx + dz * dz)
    v = speed_for(d + carry, PH[1], PH[2], PH[3])
    dh = ty - y
    if dh > 0:
        v = math.sqrt(v * v + 2 * PH[0] * dh)
    v *= ps
    return math.atan2(dz, dx), min(v, PH[3]), chosen


@njit(cache=True, parallel=True)
def play_batch(P, pzone, W, nW, MP, nMP, MB, nMB, TP, nTP, HZ, nHZ, CUP, PH, TEE,
               WP, WPM, nWP, CM, aim_sd, pow_sd, NA, NP, NT, cap, ACE, ACE_LINE_AIM):
    N = NA.shape[0]
    score = np.zeros(N, dtype=np.int64)
    holed = np.zeros(N, dtype=np.bool_)
    nhaz = np.zeros(N, dtype=np.int64)
    nesc = np.zeros(N, dtype=np.int64)
    nto = np.zeros(N, dtype=np.int64)
    end1 = np.zeros((N, 3))
    dummy = np.zeros((1, 3))
    for p in prange(N):
        x = TEE[0]; y = TEE[1]; z = TEE[2]
        strokes = 0
        for s in range(cap):
            if strokes >= cap:
                break
            b, bh, kb = support(P, x, z, y + 0.01, PH[8], PH[7])
            zone = pzone[b] if b >= 0 else -1
            aim, v, ch = plan(P, pzone, W, nW, CUP, WP, WPM, nWP, CM, PH, x, z, y, zone)
            if s == 0 and ACE[p, 0] > 0:  # going for the remembered ace line (per-play aim/speed in ACE[p, 1:3])
                aim = ACE[p, 1]
                v = ACE[p, 2]
            aim += math.radians(aim_sd) * NA[p, s]
            v = v * (1 + pow_sd * NP[p, s])
            v = min(max(v, 0.3), PH[3])
            rx, rz, ry, oc, el, md, npth = sim_shot(P, W, nW, MP, nMP, MB, nMB, TP, nTP, HZ, nHZ, CUP, PH,
                                                     x, z, y, v * math.cos(aim), v * math.sin(aim), NT[p, s], False, dummy)
            strokes += 1
            if s == 0:
                end1[p, 0] = rx; end1[p, 1] = ry; end1[p, 2] = rz
            if oc == 1:
                holed[p] = True
                break
            if oc == 2 or oc == 3:
                strokes += 1
                if oc == 2:
                    nhaz[p] += 1
                else:
                    nesc[p] += 1
            else:
                if oc == 4:
                    nto[p] += 1
                x = rx; y = ry; z = rz
        score[p] = min(strokes, cap) if holed[p] else cap
    return score, holed, nhaz, nesc, nto, end1


@njit(cache=True, parallel=True)
def shot_batch(P, W, nW, MP, nMP, MB, nMB, TP, nTP, HZ, nHZ, CUP, PH, x, z, y, AIM, V, T0):
    N = AIM.shape[0]
    oc = np.zeros(N, dtype=np.int64)
    md = np.zeros(N)
    ex = np.zeros((N, 3))
    dummy = np.zeros((1, 3))
    for i in prange(N):
        rx, rz, ry, o, el, m, npth = sim_shot(P, W, nW, MP, nMP, MB, nMB, TP, nTP, HZ, nHZ, CUP, PH,
                                              x, z, y, V[i] * math.cos(AIM[i]), V[i] * math.sin(AIM[i]), T0[i], False, dummy)
        oc[i] = o; md[i] = m
        ex[i, 0] = rx; ex[i, 1] = ry; ex[i, 2] = rz
    return oc, md, ex


@njit(cache=True, parallel=True)
def fuzz_batch(P, W, nW, MP, nMP, MB, nMB, TP, nTP, HZ, nHZ, CUP, PH, X, Z, Y, AIM, V, T0):
    N = AIM.shape[0]
    oc = np.zeros(N, dtype=np.int64)
    ex = np.zeros((N, 3))
    dummy = np.zeros((1, 3))
    for i in prange(N):
        rx, rz, ry, o, el, m, npth = sim_shot(P, W, nW, MP, nMP, MB, nMB, TP, nTP, HZ, nHZ, CUP, PH,
                                              X[i], Z[i], Y[i], V[i] * math.cos(AIM[i]), V[i] * math.sin(AIM[i]), T0[i], False, dummy)
        oc[i] = o
        ex[i, 0] = rx; ex[i, 1] = ry; ex[i, 2] = rz
    return oc, ex


def fuzz_escapes(ha, n=60000, seed=3):
    """random shots (any direction, any power, any phase) from random reachable felt points.
    Returns (escape_count, examples[(start, aim_deg, v, t0, end)])."""
    rng = np.random.default_rng(seed)
    PH = ph_array()
    P = ha.P
    pts = []
    base = [i for i in range(P.shape[0]) if P[i, 12] < 0.5]
    while len(pts) < n:
        i = base[rng.integers(len(base))]
        lx = rng.uniform(-P[i, 3] + 0.15, P[i, 3] - 0.15)
        lz = rng.uniform(-P[i, 4] + 0.15, P[i, 4] - 0.15)
        x = P[i, 0] + lx * P[i, 5] + lz * P[i, 6]
        z = P[i, 2] - lx * P[i, 6] + lz * P[i, 5]
        y = piece_h(P, i, lx, lz)
        b, bh, k = support(P, x, z, y + 0.01, PH[8], PH[7])
        if b != i or k >= 0:
            continue
        inside = False
        for q in range(ha.nW):
            pen, _, _ = sphere_box(x, y + PH[7], z, *ha.W[q, 0:6], ha.W[q, 6:15], PH[7])
            if pen > 0:
                inside = True
                break
        if not inside:
            pts.append((x, y, z))
    pts = np.array(pts)
    A = rng.uniform(0, 2 * np.pi, n)
    V = rng.uniform(0.5, PHYS["v_max"], n)
    T = rng.uniform(0, 300, n)
    oc, ex = fuzz_batch(*ha.args(), PH, pts[:, 0].copy(), pts[:, 2].copy(), pts[:, 1].copy(), A, V, T)
    bad = np.where(oc == 3)[0]
    exs = [dict(start=pts[i].round(2).tolist(), aim_deg=round(float(np.degrees(A[i])), 1), v=round(float(V[i]), 2),
                t0=round(float(T[i]), 2), end=ex[i].round(2).tolist()) for i in bad[:5]]
    return int(len(bad)), exs


def shot_batch_chunked(ha, PH, x, z, y, A, V, T, chunk=60000):
    ocs, mds, exs = [], [], []
    for i in range(0, len(A), chunk):
        o, m, e = shot_batch(*ha.args(), PH, x, z, y, A[i:i + chunk].copy(), V[i:i + chunk].copy(), T[i:i + chunk].copy())
        ocs.append(o); mds.append(m); exs.append(e)
    return np.concatenate(ocs), np.concatenate(mds), np.concatenate(exs)


def trace_shot(ha, aim, v, t0, start=None):
    PH = ph_array()
    path = np.zeros((4000, 3))
    x, y, z = start if start is not None else ha.TEE
    r = sim_shot(*ha.args(), PH, x, z, y, v * math.cos(aim), v * math.sin(aim), t0, True, path)
    return path[:r[6]].copy(), r


# ---------------------------------------------------------------- geometry validator
def validate(hole):
    """returns list of (severity, message). severity: ERROR / WARN."""
    ha = HoleArrays(hole)
    P = ha.P
    issues = []
    felt = hole["felt"]
    drops_from = set()
    for d in hole.get("drops", []):
        drops_from.add(d["from"])
    walls = hole["walls"]

    def pieces_at(x, z, skip=-1, eps=1e-3):
        out = []
        for i in range(len(felt)):
            if i == skip:
                continue
            lx, lz = piece_local(P, i, x, z)
            if abs(lx) <= P[i, 3] + eps and abs(lz) <= P[i, 4] + eps:
                out.append((i, piece_h(P, i, lx, lz)))
        return out

    def wall_at(x, z, yb):
        for k in range(ha.nW):
            W = ha.W[k]
            if W[16] < yb + 0.2 or W[15] > yb:
                continue
            dx, dz = x - W[0], z - W[2]
            lx = W[6] * dx + W[12] * dz
            lz = W[8] * dx + W[14] * dz
            if abs(lx) <= W[3] + 1e-3 and abs(lz) <= W[5] + 1e-3:
                return True
        return False

    def hazard_at(x, z):
        return in_hazard(ha.HZ, ha.nHZ, x, z) >= 0

    for i, p in enumerate(felt):
        hx, hz = P[i, 3], P[i, 4]
        c, s = P[i, 5], P[i, 6]
        overlay = P[i, 12] > 0.5
        edges = [((1, 0), hz, "+x"), ((-1, 0), hz, "-x"), ((0, 1), hx, "+z"), ((0, -1), hx, "-z")]
        for (ox, oz), half, ename in edges:
            n = max(2, int(2 * half / 0.4))
            bad = {}
            for q in range(n + 1):
                tpar = -half + 0.08 + (2 * half - 0.16) * q / n
                if ox != 0:
                    lx, lz = ox * hx, tpar
                else:
                    lx, lz = tpar, oz * hz
                he = piece_h(P, i, lx, lz)
                lxo, lzo = lx + ox * 0.15, lz + oz * 0.15
                lxi, lzi = lx - ox * 0.15, lz - oz * 0.15
                wx = lxo * c + lzo * s + P[i, 0]
                wz = -lxo * s + lzo * c + P[i, 2]
                if overlay:
                    ix = lxi * c + lzi * s + P[i, 0]
                    iz = -lxi * s + lzi * c + P[i, 2]
                    base = [hh for (j, hh) in pieces_at(ix, iz, skip=i) if P[j, 12] < 0.5]
                    if not base:
                        continue  # this part of the bank is buried behind the rails
                others = pieces_at(wx, wz, skip=i)
                hs = [hh for (_, hh) in others]
                kind = None
                if any(abs(hh - he) <= 0.06 for hh in hs):
                    continue
                if wall_at(wx, wz, he + PHYS["ball_r"]):
                    continue
                if overlay and any(hh < he for hh in hs):
                    continue
                higher = [hh for hh in hs if hh > he + 0.06]
                lower = [hh for hh in hs if hh < he - 0.06]
                if higher and min(higher) - he >= 0.5:
                    continue
                if higher:
                    kind = ("ERROR", f"height mismatch: step up {min(higher) - he:.2f}")
                elif lower:
                    dh = he - max(lower)
                    if dh >= 0.4:
                        if p["id"] in drops_from or p["zone"] in drops_from:
                            continue
                        kind = ("WARN", f"undeclared drop {dh:.2f}")
                    else:
                        kind = ("ERROR", f"height mismatch: step down {dh:.2f}")
                elif hazard_at(wx, wz):
                    continue
                else:
                    kind = ("ERROR", "unenclosed edge (no felt/rail/hazard)")
                bad.setdefault(kind, []).append((round(wx, 2), round(wz, 2)))
            for (sev, msg), pts in bad.items():
                issues.append((sev, f"felt '{p['id']}' edge {ename}: {msg} at {len(pts)} samples, "
                                    f"from ({pts[0][0]},{pts[0][1]}) to ({pts[-1][0]},{pts[-1][1]})"))
    # overlaps between non-overlay pieces
    for i, p in enumerate(felt):
        if P[i, 12] > 0.5:
            continue
        hx, hz = P[i, 3], P[i, 4]
        c, s = P[i, 5], P[i, 6]
        for a in np.linspace(-hx + 0.05, hx - 0.05, max(2, int(hx * 2))):
            for b in np.linspace(-hz + 0.05, hz - 0.05, max(2, int(hz * 2))):
                wx = a * c + b * s + P[i, 0]
                wz = -a * s + b * c + P[i, 2]
                he = piece_h(P, i, a, b)
                for j, hh in pieces_at(wx, wz, skip=i):
                    if P[j, 12] > 0.5:
                        continue
                    if 0.06 < abs(hh - he) < 0.5:
                        issues.append(("ERROR", f"overlap height mismatch '{p['id']}' vs '{felt[j]['id']}' "
                                                f"({hh - he:+.2f}) near ({wx:.1f},{wz:.1f})"))
                        break
                else:
                    continue
                break
            else:
                continue
            break
    # points of interest
    def on_felt(pos, label, need_flat=False):
        hs = pieces_at(pos[0], pos[2])
        ok = [(j, hh) for j, hh in hs if abs(hh - pos[1]) < 0.06]
        if not ok:
            issues.append(("ERROR", f"{label} at {pos} not on felt (heights here: {[round(h, 2) for _, h in hs]})"))
        elif need_flat and all(P[j, 7] >= 0 for j, _ in ok):
            issues.append(("WARN", f"{label} sits on sloped felt"))
        if wall_at(pos[0], pos[2], pos[1] + 0.08):
            issues.append(("ERROR", f"{label} inside a wall"))
    on_felt(hole["tee"]["position"], "tee")
    on_felt(hole["cup"]["position"], "cup", need_flat=True)
    for t in hole.get("teleports", []):
        on_felt(t["entry"]["center"], f"teleport {t['id']} entry")
        on_felt(t["exit"]["center"], f"teleport {t['id']} exit")
    for sk, lst in hole.get("ai_waypoints", {}).items():
        for w in lst:
            hs = pieces_at(w["pos"][0], w["pos"][2])
            if not hs:
                issues.append(("WARN", f"waypoint {sk}/{w['id']} off felt"))
    cx, cy, cz = hole["cup"]["position"]
    for m in hole.get("moving_parts", []):
        piv = m["pivot"]
        reach = max(math.hypot(b["center"][0], b["center"][2]) + math.hypot(b["size"][0], b["size"][2]) / 2
                    for b in m["blockers"])
        if m["type"] == "rotate" and abs(m["axis"][1]) > 0.9 and math.hypot(cx - piv[0], cz - piv[2]) < reach + 0.5:
            issues.append(("WARN", f"moving part {m['id']} sweeps over the cup"))
    return issues


# ---------------------------------------------------------------- experiments
def hio_search(ha, coarse_deg=0.5, n_pow=48, phases=None):
    """brute-force grid of aim x power (x start phase) from the tee. Returns dict."""
    PH = ph_array()
    tee = ha.TEE
    if phases is None:
        phases = [0.0] if ha.nMP == 0 else list(np.linspace(0, 12, 8, endpoint=False))
    aims = np.radians(np.arange(0, 360, coarse_deg))
    pows = np.linspace(0.12, 1.0, n_pow) * PHYS["v_max"]
    A, V, T = np.meshgrid(aims, pows, np.array(phases), indexing="ij")
    A, V, T = A.ravel(), V.ravel(), T.ravel()
    t1 = time.time()
    oc, md, ex = shot_batch_chunked(ha, PH, tee[0], tee[2], tee[1], A, V, T)
    hits = np.where(oc == 1)[0]
    res = dict(shots=int(len(A)), hits=int(len(hits)), frac=float(len(hits) / len(A)), refined=False)
    if len(hits) == 0:
        # refine around closest approaches
        order = np.argsort(md)[:40]
        A2, V2, T2 = [], [], []
        for i in order:
            for da in np.radians(np.linspace(-coarse_deg, coarse_deg, 21)):
                for dv in np.linspace(-0.6, 0.6, 13):
                    A2.append(A[i] + da); V2.append(min(PHYS["v_max"], max(0.5, V[i] + dv))); T2.append(T[i])
        A2, V2, T2 = np.array(A2), np.array(V2), np.array(T2)
        oc2, md2, ex2 = shot_batch_chunked(ha, PH, tee[0], tee[2], tee[1], A2, V2, T2)
        h2 = np.where(oc2 == 1)[0]
        res.update(refined=True, refine_shots=int(len(A2)), refine_hits=int(len(h2)))
        if len(h2):
            Ah, Vh = A2[h2], V2[h2]
            score = [int(((np.abs(Ah - Ah[j]) <= math.radians(1.0)) & (np.abs(Vh - Vh[j]) <= 0.6)).sum()) for j in range(len(h2))]
            i = h2[int(np.argmax(score))]
            res["line"] = dict(aim_deg=float(np.degrees(A2[i]) % 360), speed=float(V2[i]), phase=float(T2[i]))
        res["closest"] = float(min(md.min(), md2.min()))
    else:
        # choose a representative hit: the one with most hit neighbours (most robust)
        # most robust hit: the one with the most hitting neighbours within +-1 deg and +-0.6 studs/s (any phase)
        Ah, Vh = A[hits], V[hits]
        score = [int(((np.abs(Ah - Ah[j]) <= math.radians(1.0)) & (np.abs(Vh - Vh[j]) <= 0.6)).sum()) for j in range(len(hits))]
        i = hits[int(np.argmax(score))]
        res["line"] = dict(aim_deg=float(np.degrees(A[i]) % 360), speed=float(V[i]), phase=float(T[i]))
        res["closest"] = 0.0
    res["seconds"] = round(time.time() - t1, 1)
    return res


def run_plays(ha, skill, n, seed, ace_line=None):
    PH = ph_array()
    rng = np.random.default_rng(seed)
    NA = rng.standard_normal((n, CAP))
    NP = rng.standard_normal((n, CAP))
    NT = rng.uniform(0, 600, (n, CAP))
    WP, WPM, nWP, CM = ha.waypoints(skill)
    sk = SKILLS[skill]
    ACE = np.zeros((n, 3))
    ACE_LINE = np.zeros(2)
    if ace_line is not None and sk.get("ace_try", 0) > 0:
        ACE[:, 0] = (rng.uniform(0, 1, n) < sk["ace_try"]).astype(np.float64)
        ACE[:, 1] = math.radians(ace_line["aim_deg"]) + math.radians(sk["ace_aim_sd"]) * rng.standard_normal(n)
        ACE[:, 2] = ace_line["speed"] * (1 + sk["ace_pow_sd"] * rng.standard_normal(n))
    score, holed, nhaz, nesc, nto, end1 = play_batch(
        ha.P, ha.pzone, ha.W, ha.nW, ha.MP, ha.nMP, ha.MB, ha.nMB, ha.TP, ha.nTP, ha.HZ, ha.nHZ, ha.CUP, PH, ha.TEE,
        WP, WPM, nWP, CM, sk["aim_sd"], sk["pow_sd"], NA, NP, NT, CAP, ACE, ACE_LINE)
    dist = [int((score == k).sum()) for k in range(1, CAP + 1)]
    return dict(n=n, avg=float(score.mean()), dist=dist, hio=float((score == 1).mean()),
                capped=float((~holed).mean()), hazard_per_play=float(nhaz.mean()),
                escapes=int(nesc.sum()), timeouts=int(nto.sum()), end1=end1[:400].round(2).tolist())


def flags_for(hole, stats, issues, hio):
    par = hole["par"]
    fl = []
    if any(s == "ERROR" for s, _ in issues):
        fl.append("BROKEN:geometry")
    if any(stats[s]["escapes"] > 0 for s in stats):
        fl.append("BROKEN:escapes")
    if all(stats[s]["capped"] >= 0.999 for s in stats):
        fl.append("BROKEN:unreachable-cup")
    if "good" in stats and stats["good"]["capped"] > 0.5:
        fl.append("IMPOSSIBLE")
    for s in stats:
        if stats[s]["hio"] > 0.15:
            fl.append(f"TRIVIAL:{s}-HIO>{15}%")
        if stats[s]["avg"] < par - 1:
            fl.append(f"TRIVIAL:{s}-avg<par-1")
    if "good" in stats and stats["good"]["avg"] > par + 2:
        fl.append("TOO-HARD:good>par+2")
    if hio is not None and not hio.get("line"):
        fl.append("WARN:no-HIO-line")
    if any(stats[s]["timeouts"] > 0 for s in stats):
        fl.append("WARN:timeouts")
    return fl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=os.path.join(ROOT, "holes.json"))
    ap.add_argument("--holes", type=int, nargs="*")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--tag", default="latest")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--no-hio", action="store_true")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    course = json.load(open(a.json))
    vmax = PHYS["v_max"]
    print(f"numba={HAVE_NUMBA}  max putt on flat = {flat_dist(vmax, PHYS['roll_decel'], PHYS['drag']):.1f} studs "
          f"({flat_dist(vmax, PHYS['roll_decel'], PHYS['drag']) * STUD_M:.1f} m) at {vmax} studs/s ({vmax * STUD_M:.1f} m/s)")
    out = dict(tag=a.tag, phys=PHYS, skills=SKILLS, holes=[])
    rows = []
    for hole in course["holes"]:
        if a.holes and hole["number"] not in a.holes:
            continue
        t0 = time.time()
        issues = validate(hole)
        for sev, msg in issues:
            print(f"  [{hole['id']}] {sev}: {msg}")
        rec = dict(id=hole["id"], name=hole["name"], par=hole["par"], issues=issues)
        if not a.validate_only:
            ha = HoleArrays(hole)
            nesc, exs = fuzz_escapes(ha)
            if nesc:
                issues.append(("ERROR", f"fuzz: {nesc}/60000 random shots escaped the course, e.g. {exs[:2]}"))
                print(f"  [{hole['id']}] ERROR: fuzz escapes {nesc}: {exs[:3]}")
            rec["fuzz_escapes"] = nesc
            hio = None if a.no_hio else hio_search(ha)
            stats = {}
            for k, skill in enumerate(SKILLS):
                stats[skill] = run_plays(ha, skill, a.n, a.seed + 101 * hole["number"] + k,
                                         ace_line=(hio or {}).get("line"))
            fl = flags_for(hole, stats, issues, hio)
            rec.update(stats=stats, hio_search=hio, flags=fl)
            g, av = stats["good"], stats["average"]
            hs = "-" if hio is None else (f"{hio['hits']}/{hio['shots']}" if hio["hits"] else
                                           (f"refine {hio.get('refine_hits', 0)}/{hio.get('refine_shots', 0)}"))
            rows.append(f"| {hole['number']} | {hole['name']} | {hole['par']} | {g['avg']:.2f} | {g['hio'] * 100:.1f}% | "
                        f"{g['capped'] * 100:.1f}% | {av['avg']:.2f} | {av['hio'] * 100:.1f}% | {av['capped'] * 100:.1f}% | "
                        f"{av['hazard_per_play']:.2f} | {hs} | {', '.join(fl) or 'ok'} |")
            print(f"H{hole['number']} {hole['name']}: good {g['avg']:.2f} {g['dist']} hio {g['hio']:.3f} | "
                  f"avg {av['avg']:.2f} {av['dist']} hio {av['hio']:.3f} | HIO-search {hs} {hio and hio.get('line')} "
                  f"| {fl} ({time.time() - t0:.0f}s)")
        out["holes"].append(rec)
        os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
        with open(os.path.join(HERE, "out", f"sim-{a.tag}.json"), "w") as f:  # save progress per hole
            json.dump(out, f, indent=1)
    if rows:
        hdr = ("| # | Hole | Par | Good avg | Good HIO | Good capped | Avg avg | Avg HIO | Avg capped | Avg hazards/play | "
               "HIO search hits | Flags |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
        tbl = hdr + "\n" + "\n".join(rows)
        print("\n" + tbl)
        out["table"] = tbl
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    with open(os.path.join(HERE, "out", f"sim-{a.tag}.json"), "w") as f:
        json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
