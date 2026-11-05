"""Sunset Gondola line geometry (pass 5). Pure python (no bpy/numpy); used by sc_pieces (Blender build), the pass-5
layout/manifest finaliser and sc_fitcheck_holes.py. All coordinates are Roblox WORLD studs (x east, y up, z south).

Attach points come from the exported gondola_station bull wheel: torus groove radius 3.8 centred at station-local
Roblox (0, 7.6, -2) (measured from _cache/tris/gondola_station.npy: ring y 7.36..7.84, radial 3.60..4.05 about
(x 0, z -2)), placed by the two layout.json gondola_station instances. The haul rope leaves each wheel tangentially
at local x = +-3.8 heading local -Z (the open end), so the two ropes are 7.6 apart and parallel in plan.

Profile: straight in plan, but the direct chord passes ~37 studs inside the Crown cliff (terrain steps 70 -> 190 at
plan distance 506-510 from the bottom wheel) and Hole 17 lies directly under the line on the Crown, so the rope is
carried over the Crown lip by ONE support tower (plan distance TOWER_D from the bottom wheel centre, on the line
centre). Each span is a parabolic catenary hanging SAG[i] below its chord.
"""
import math

WHEEL_LOCAL = (0.0, 7.6, -2.0)       # Roblox station-local bull-wheel centre (rope plane) of gondola_station
WHEEL_R = 3.8                        # groove radius -> haul-rope spacing 7.6
STATIONS = {"bottom": ((132.0, 18.0, 544.0), 53.53), "top": ((-420.0, 190.1, 128.0), -126.84)}
# pass 6 (RobloxDevBot clearance request): the bottom station is the raised gondola_station_bottom variant. Its deck,
# bull wheel and roof sit BOTTOM_RAISE higher on a timber/sandstone undercroft (same footprint position and yaw), so
# the cabin's swept path clears the Junction walkway p_h18_hub seg 3 by >= 8 studs. Set BOTTOM_RAISE = 0 to get the
# pass-5 line back (used once to prove the step-1 recolour kept the geometry identical).
BOTTOM_RAISE = 7.2                   # 9 risers of 0.8 (world.json design_step_rise)
WHEEL_Y = {"bottom": WHEEL_LOCAL[1] + BOTTOM_RAISE, "top": WHEEL_LOCAL[1]}
TOWER_D = 524.0                      # plan distance of the tower from the bottom wheel centre along the line
TOWER_ROPE_Y = 221.0                 # rope (sheave-crest) height at the tower
SAG = (10.0, 2.5)                    # mid-span sag of span 1 (bottom -> tower) and span 2 (tower -> top)
SPEED = 6.0                          # studs/s along the rope
HANG = 6.4                           # grip -> bottom of cabin floor
CABIN_YAW_UP = 53.53                 # cabin front (local -Z) faces the top station on the up line


def to_world(pos, yaw, l):
    a = math.radians(yaw)
    c, s = math.cos(a), math.sin(a)
    return (l[0] * c + l[2] * s + pos[0], l[1] + pos[1], -l[0] * s + l[2] * c + pos[2])


def attach(which, side):
    pos, yaw = STATIONS[which]
    return to_world(pos, yaw, (side * WHEEL_R, WHEEL_Y[which], WHEEL_LOCAL[2]))


def wheel_centre(which):
    pos, yaw = STATIONS[which]
    return to_world(pos, yaw, (WHEEL_LOCAL[0], WHEEL_Y[which], WHEEL_LOCAL[2]))


def set_bottom_raise(r):
    """Re-derive every module-level value that depends on the bottom wheel height (build scripts call this once)."""
    global BOTTOM_RAISE, ORIGIN
    BOTTOM_RAISE = r
    WHEEL_Y["bottom"] = WHEEL_LOCAL[1] + r
    ORIGIN = wheel_centre("bottom")


ORIGIN = wheel_centre("bottom")      # gondola_cable pivot (line start = bottom bull-wheel centre)
_TOP = wheel_centre("top")
PLAN_D = math.hypot(_TOP[0] - ORIGIN[0], _TOP[2] - ORIGIN[2])
UDIR = ((_TOP[0] - ORIGIN[0]) / PLAN_D, (_TOP[2] - ORIGIN[2]) / PLAN_D)       # plan direction bottom -> top
FT = TOWER_D / PLAN_D                                                         # plan fraction of the tower


def tower_centre():
    return (ORIGIN[0] + UDIR[0] * TOWER_D, TOWER_ROPE_Y, ORIGIN[2] + UDIR[1] * TOWER_D)


def ropes():
    """{name: (A, T, B)} bottom attach, tower sheave crest, top attach. Up line = bottom +x side -> top -x side."""
    out = {}
    for name, sb, st in (("up_line", +1, -1), ("down_line", -1, +1)):
        A, B = attach("bottom", sb), attach("top", st)
        T = (A[0] + (B[0] - A[0]) * FT, TOWER_ROPE_Y, A[2] + (B[2] - A[2]) * FT)
        out[name] = (A, T, B)
    return out


def span_point(P, Q, w, sag):
    """Point at chord fraction w of span P->Q hanging 4*sag*w*(1-w) below the chord (world y)."""
    return (P[0] + (Q[0] - P[0]) * w, P[1] + (Q[1] - P[1]) * w - 4 * sag * w * (1 - w), P[2] + (Q[2] - P[2]) * w)


def rope_point(rope, f):
    """f = plan fraction 0..1 from the bottom attach to the top attach."""
    A, T, B = rope
    if f <= FT:
        return span_point(A, T, f / FT, SAG[0])
    return span_point(T, B, (f - FT) / (1 - FT), SAG[1])


def span_lengths(rope, n=600):
    A, T, B = rope
    out = []
    for P, Q, sg in ((A, T, SAG[0]), (T, B, SAG[1])):
        L, p = 0.0, P
        for i in range(1, n + 1):
            q = span_point(P, Q, i / n, sg)
            L += math.dist(p, q)
            p = q
        out.append(L)
    return out


def f_at_time(rope, t, n=2000):
    """Plan fraction reached t seconds after leaving the bottom attach at SPEED studs/s of rope arc length."""
    target, L = SPEED * t, 0.0
    p = rope_point(rope, 0.0)
    for i in range(1, n + 1):
        q = rope_point(rope, i / n)
        d = math.dist(p, q)
        if L + d >= target:
            return (i - 1 + (target - L) / d) / n
        L += d
        p = q
    return 1.0


def samples(rope, step=1.0):
    """Points every ~step studs of arc length along the rope (bottom -> top)."""
    total = sum(span_lengths(rope))
    n = int(math.ceil(total / step))
    fs, pts, L = [0.0], [rope_point(rope, 0.0)], 0.0
    m = 20 * n
    p = pts[0]
    nxt = step
    for i in range(1, m + 1):
        q = rope_point(rope, i / m)
        L += math.dist(p, q)
        p = q
        if L >= nxt or i == m:
            fs.append(i / m)
            pts.append(q)
            nxt += step
    return fs, pts
