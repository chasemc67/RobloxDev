"""Moving meshes: origin = holes.json pivot exactly; contact bodies coincide with the holes.json blockers. Red/cream
signal bands (MoveRed/MoveCream) appear ONLY on these moving parts. Decoration only (blockers carry collision)."""
import math
import bmesh
import holesdata as D
from aalib import R, hbox
from registry import prop


def _motion(n, mid):
    m = D.mover(n, mid)
    mo = dict(type=m["type"], axis_roblox=m["axis"], speed=m.get("speed"), units=m.get("speed_units"),
              range=m.get("range"), phase=m.get("phase", m.get("phase_s", 0.0)), course_local_pivot=m["pivot"],
              world_pivot=D.to_world(n, m["pivot"]))
    for k in ("dwell", "period_s", "amplitude_deg", "profile", "solid_window"):
        if k in m:
            mo[k] = m[k]
    a = D.yaw_rot(m["axis"][0], m["axis"][2], D.H[n]["world_yaw"])
    mo["axis_world"] = [round(a[0], 4), m["axis"][1], round(a[1], 4)]
    return mo


def extrude_xy(pb, mat, poly, z0, z1, roll=0.0):
    """Polygon in the Roblox x-y plane (mover frame), rotated by `roll` about Roblox +Z, extruded z0..z1."""
    t = bmesh.new()
    c, s = math.cos(math.radians(roll)), math.sin(math.radians(roll))
    P = [(x * c - y * s, x * s + y * c) for x, y in poly]
    a = [t.verts.new(R(x, y, z0)) for x, y in P]
    b = [t.verts.new(R(x, y, z1)) for x, y in P]
    t.faces.new(a)
    t.faces.new(b)
    n = len(P)
    for i in range(n):
        t.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.recalc_face_normals(t, faces=t.faces)
    bmesh.ops.triangulate(t, faces=[f for f in t.faces if len(f.verts) > 4])
    pb.add(mat, t)


def extrude_xz(pb, mat, poly, y0, y1):
    t = bmesh.new()
    a = [t.verts.new(R(x, y0, z)) for x, z in poly]
    b = [t.verts.new(R(x, y1, z)) for x, z in poly]
    t.faces.new(a)
    t.faces.new(b)
    n = len(poly)
    for i in range(n):
        t.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.recalc_face_normals(t, faces=t.faces)
    bmesh.ops.triangulate(t, faces=[f for f in t.faces if len(f.verts) > 4])
    pb.add(mat, t)


# ------------------------------------------------------------------------------------------------ H5 geyser column
@prop("aa_h05_geyser_column", [5], "P1", target=[3, 4, 3], kind="moving", motion=_motion(5, "geyser_column"),
      placements=[dict(hole=5, pos=D.mover(5, "geyser_column")["pivot"], yaw=0.0)],
      origin="pivot = platform TOP centre at offset 0 [0,0,-26.5] (flush with the basin felt)",
      notes="Basalt geyser platform: contact body = the exact 3 x 4 x 3 blocker (y -4..0), square 3 x 3 faces; hex basalt look in the top texture; red/cream signal bands flush on the sides; brass hex vent ring (<=0.005 proud) on top; brass gauge on the EAST face (0.09 proud) shows the 13.5 s cycle. Steam column = aa_h05_geyser_steam.",
      extra=dict(cls="mover", merge=False, mover=(5, "geyser_column"), proud_ok=0.1))
def geyser_column(pb):
    for y0, y1, m in ((-4.0, -1.05, "Basalt"), (-1.05, -0.75, "MoveRed"), (-0.75, -0.45, "MoveCream"), (-0.45, 0.0, "Basalt")):
        hbox(pb, m, (0, (y0 + y1) / 2, 0), (3, y1 - y0, 3))
    ring = [(0.75 * math.cos(math.radians(60 * k)), 0.75 * math.sin(math.radians(60 * k))) for k in range(6)]
    inner = [(0.55 * math.cos(math.radians(60 * k)), 0.55 * math.sin(math.radians(60 * k))) for k in range(6)]
    for k in range(6):
        q = [ring[k], ring[(k + 1) % 6], inner[(k + 1) % 6], inner[k]]
        extrude_xz(pb, "Brass", q, 0.0, 0.005)
    extrude_xz(pb, "Steam", inner, 0.0, 0.003)
    # gauge on the east (+X) face
    pb.cyl("Brass", 0.38, 0.38, 0.06, 12, loc=tuple(R(1.53, -1.7, 0)), rot=(0, 90, 0), smooth=False)
    pb.cyl("Ink", 0.3, 0.3, 0.03, 12, loc=tuple(R(1.565, -1.7, 0)), rot=(0, 90, 0), smooth=False)
    hbox(pb, "AuroraMint", (1.583, -1.62, 0), (0.006, 0.22, 0.04))


@prop("aa_h05_geyser_steam", [5], "P1", target=[2.4, 1, 2.4], kind="animated",
      placements=[dict(hole=5, pos=D.mover(5, "geyser_column")["pivot"], yaw=0.0)],
      origin="shaft top centre at basin felt level; mesh is y 0..1 -> script sets Size.Y = current offset (0..4)",
      notes="Translucent steam column under the risen platform (non-colliding, Steam Transparency 0.5).",
      extra=dict(cls="mover_aux", merge=False))
def geyser_steam(pb):
    pb.cyl("Steam", 1.2, 1.2, 1.0, 8, loc=tuple(R(0, 0.5, 0)), smooth=True)


# ------------------------------------------------------------------------------------------------ H11 ice floe
FLOE = [(-3.2, -0.318), (3.2, -0.318), (3.5, 0.0), (3.2, 0.318), (-3.2, 0.318), (-3.5, 0.0)]


@prop("aa_h11_ice_floe", [11], "P1", target=[7.0, 1.2, 0.636], kind="moving", motion=_motion(11, "ice_floe"),
      placements=[dict(hole=11, pos=D.mover(11, "ice_floe")["pivot"], yaw=0.0)],
      origin="pivot = floe centre at felt level [0,0,-28] (offset 0); slides along local +X, range -7..0",
      notes="Glacier-ice floe: contact profile y 0..1.0 = slab 6.4 x 0.636 + 45-degree pointed ends to x +-3.5 (the 3 blockers); red/cream bands flush; snow cap + a mini belly-sliding snowpuff inside the footprint, top y 1.12 (props.md allows 1.2; the rail5/berg18 slot lintel is at y 1.27 since Round 4 'walls' (was 1.17) - kept 0.15 under it).",
      extra=dict(cls="mover", merge=False, mover=(11, "ice_floe")))
def ice_floe(pb):
    for y0, y1, m in ((0.0, 0.45, "Ice"), (0.45, 0.62, "MoveRed"), (0.62, 0.79, "MoveCream"), (0.79, 1.0, "Ice")):
        extrude_xz(pb, m, FLOE, y0, y1)
    cap = [(x * 0.94, z * 0.7) for x, z in FLOE]
    extrude_xz(pb, "Snow", cap, 1.0, 1.07)
    pb.sphere("Ink", 1.0, loc=tuple(R(1.4, 1.075, 0)), scale=(0.24, 0.13, 0.045), segs=8, rings=4)
    pb.sphere("Cream", 1.0, loc=tuple(R(1.62, 1.095, 0)), scale=(0.08, 0.08, 0.025), segs=6, rings=3)
    pb.sphere("Beak", 1.0, loc=tuple(R(1.66, 1.075, 0)), scale=(0.04, 0.03, 0.02), segs=5, rings=3)


# ------------------------------------------------------------------------------------------------ H12 paddle wheel
# Pass 2d: visual felt gap 0.0625 for the two blocking movers (target 0.06-0.065); only the VISUAL mesh moved then.
# Round 3 "clear" (holes.json): the COLLIDERS now sit 0.06 over the felt themselves (H12 hub y 4.12 -> 4.16, strip corners
# r 4.10; H14 foot = 9 strips whose outer bottom corners lie on r 10.289 about the hinge), so the visual meshes follow the
# colliders again: tip / skid arcs = the collider corner radius read from holes.json (visual felt gap = collider gap).
FELT_GAP_2D = 0.0625                    # pass 2d value (history; no longer used for the geometry)


def _corners(m):
    """holes.json blocker corners (Roblox, pivot frame, angle 0): yaw about +Y, then roll about the mover axis (+Z)."""
    out = []
    for b in m["blockers"]:
        cs = []
        for sx in (-.5, .5):
            for sy in (-.5, .5):
                for sz in (-.5, .5):
                    x, z = D.yaw_rot(sx * b["size"][0], sz * b["size"][2], b.get("yaw", 0.0))
                    p = [b["center"][0] + x, b["center"][1] + sy * b["size"][1], b["center"][2] + z]
                    a = math.radians(b.get("roll", 0.0))
                    p = [p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a), p[2]]
                    cs.append(p)
        out.append(cs)
    return out


_M12, _M14 = D.mover(12, "paddle_wheel"), D.mover(14, "icicle_bell")
H12_TIP_R = round(max(math.hypot(p[0], p[1]) for cs in _corners(_M12) for p in cs), 4)        # 4.1 (strip corner radius)
_FOOT14 = [b for b in _M14["blockers"][1:]]                                                     # Round 3: 9 strips
H14_SKID_R = round(max(math.hypot(p[0], p[1]) for cs in _corners(dict(blockers=_FOOT14)) for p in cs), 4)   # 10.289
H14_FOOT_X = sorted({round(b["center"][0] + s * b["size"][0] / 2, 4) for b in _FOOT14 for s in (-1, 1)})  # strip edges
H14_FOOT_TOP = round(max(b["center"][1] + b["size"][1] / 2 for b in _FOOT14), 4)                 # -9.889 (y 0.461 at rest)
H14_FOOT_Z = max(b["size"][2] for b in _FOOT14) / 2                                              # 0.075


@prop("aa_h12_paddle_wheel", [12], "P1", target=[8.2, 8.2, 0.4], kind="moving", motion=_motion(12, "paddle_wheel"),
      placements=[dict(hole=12, pos=D.mover(12, "paddle_wheel")["pivot"], yaw=0.0)],
      origin=f"pivot = hub {list(_M12['pivot'])}, axis local +Z (world +X)",
      notes=f"4 timber paddles 2.4 wide x 0.4 thick, r 0.6 -> outer ARC r {H12_TIP_R:g} = the holes.json strip-corner radius (Round 3 'clear': hub y 4.12 -> {_M12['pivot'][1]:g}; the arc follows the stepped strip colliders, strip ends 3.92/4.02/4.08, so visual and collider both clear the felt by {_M12['pivot'][1] - H12_TIP_R:.2f} at every angle; pass 2d had pulled the arc in to r 4.0575); cream band + red tips on every paddle; red/cream rim (r 3.5..3.85, z +-0.15) and cream spokes; brass hub r 0.6. Lowest rim point {_M12['pivot'][1] - 3.85:.2f} over the felt.",
      extra=dict(cls="mover", merge=False, mover=(12, "paddle_wheel")))
def paddle_wheel(pb):
    xs = [-1.2 + 0.2 * i for i in range(13)]
    for k in range(4):
        roll = 90 * k
        extrude_xy(pb, "Timber", [(-1.2, -0.6), (1.2, -0.6), (1.2, -3.3), (-1.2, -3.3)], -0.2, 0.2, roll)
        extrude_xy(pb, "MoveCream", [(-1.2, -3.3), (1.2, -3.3), (1.2, -3.6), (-1.2, -3.6)], -0.2, 0.2, roll)
        tip = [(-1.2, -3.6), (1.2, -3.6)] + [(x, -math.sqrt(H12_TIP_R ** 2 - x * x)) for x in reversed(xs)]
        extrude_xy(pb, "MoveRed", tip, -0.2, 0.2, roll)
    nseg = 32
    for i in range(nseg):
        a0, a1 = math.tau * i / nseg, math.tau * (i + 1) / nseg
        q = [(3.5 * math.cos(a0), 3.5 * math.sin(a0)), (3.85 * math.cos(a0), 3.85 * math.sin(a0)),
             (3.85 * math.cos(a1), 3.85 * math.sin(a1)), (3.5 * math.cos(a1), 3.5 * math.sin(a1))]
        extrude_xy(pb, "MoveRed" if (i // 2) % 2 == 0 else "MoveCream", q, -0.15, 0.15)
    for k in range(4):
        extrude_xy(pb, "MoveCream", [(-0.12, 0.6), (0.12, 0.6), (0.12, 3.5), (-0.12, 3.5)], -0.1, 0.1, 45 + 90 * k)
    pb.cyl("Brass", 0.6, 0.6, 1.0, 12, loc=tuple(R(0, 0, 0)), rot=(90, 0, 0), smooth=True)
    pb.cyl("Brass", 0.35, 0.2, 0.3, 10, loc=tuple(R(0, 0, 0.62)), rot=(90, 0, 0), smooth=True)


# ------------------------------------------------------------------------------------------------ H13 carousel arms
@prop("aa_h13_carousel_arms", [13], "P1", target=[23.0, 3.4, 23.0], kind="moving", motion=_motion(13, "carousel_arms"),
      placements=[dict(hole=13, pos=D.mover(13, "carousel_arms")["pivot"], yaw=0.0)],
      origin="pivot = hub centre at felt level [0,0,-36], axis +Y",
      notes="4 sled-runner blocks skinning the blockers exactly (r 8.2..11.5, 3.6 wide, y 0..0.9, red/cream bands); cream sled bodies + snowpuff riders above y 0.9 inside the footprint (top < 4); spokes y 2.0..2.25 (>= 1.4 over felt for r < 8.2) to a brass collar r 0.75..1.0 around the static canopy pole.",
      extra=dict(cls="mover", merge=False, mover=(13, "carousel_arms")))
def carousel_arms(pb):
    scarf = ["AuroraMint", "Canvas", "AuroraTeal", "Canvas"]
    for k in range(4):
        a = 90 * k
        cx, cz = D.yaw_rot(9.85, 0, a)
        for y0, y1, m in ((0, 0.35, "MoveRed"), (0.35, 0.6, "MoveCream"), (0.6, 0.9, "MoveRed")):
            hbox(pb, m, (cx, (y0 + y1) / 2, cz), (3.3, y1 - y0, 3.6), a)
        hbox(pb, "MoveCream", (cx, 1.2, cz), (2.9, 0.6, 3.1), a, bevel=0.12)
        fx, fz = D.yaw_rot(9.85, 1.3, a)
        hbox(pb, "MoveRed", (fx, 1.65, fz), (2.9, 0.4, 0.3), a, bevel=0.08)
        px, pz = D.yaw_rot(9.85, -0.2, a)
        pb.sphere("Ink", 1.0, loc=tuple(R(px, 2.05, pz)), scale=(0.45, 0.42, 0.6), segs=10, rings=6)
        bx, bz = D.yaw_rot(9.85, 0.18, a)
        pb.sphere("Cream", 1.0, loc=tuple(R(bx, 2.0, bz)), scale=(0.33, 0.3, 0.45), segs=8, rings=5)
        pb.sphere("Ink", 0.34, loc=tuple(R(px, 2.85, pz)), segs=10, rings=6)
        kx, kz = D.yaw_rot(9.85, 0.12, a)
        pb.sphere("Beak", 1.0, loc=tuple(R(kx, 2.85, kz)), scale=(0.08, 0.08, 0.06), segs=6, rings=4)
        pb.torus(scarf[k], 0.33, 0.07, 10, 4, loc=tuple(R(px, 2.55, pz)), smooth=False)
        # spoke from the collar to the sled
        sx, sz = D.yaw_rot(4.7, 0, a)
        hbox(pb, "MoveCream", (sx, 2.125, sz), (7.4, 0.25, 0.3), a)
    for i in range(16):
        a0, a1 = math.tau * i / 16, math.tau * (i + 1) / 16
        extrude_xz(pb, "Brass", [(0.75 * math.cos(a0), 0.75 * math.sin(a0)), (1.0 * math.cos(a0), 1.0 * math.sin(a0)),
                                 (1.0 * math.cos(a1), 1.0 * math.sin(a1)), (0.75 * math.cos(a1), 0.75 * math.sin(a1))], 1.9, 2.4)


# ------------------------------------------------------------------------------------------------ H14 icicle bell
@prop("aa_h14_icicle_bell", [14], "P1", target=[2.1, 10.6, 2.1], kind="moving", motion=_motion(14, "icicle_bell"),
      placements=[dict(hole=14, pos=D.mover(14, "icicle_bell")["pivot"], yaw=0.0)],
      origin=f"pivot = hinge {list(_M14['pivot'])}, axis local +Z (world +X); swing amp {_M14['amplitude_deg']:g} deg, period {_M14['period_s']:g} s",
      notes=f"Brass bell: lower body = the 2x2x2 contact cube 9.0 below the hinge, yaw 30, vertical edges rounded 0.08; crown/flare and icicle fringe above the cube top only; brass rocker skid plate over the Round 3 collider foot (9 strips, 2.1 x 0.4 x 0.15 envelope, yaw 0): top y {_M14['pivot'][1] + H14_FOOT_TOP:.3f} at rest, curved UNDERSIDE = arc r {H14_SKID_R:g} about the hinge (= the strips' corner arc; vertices on the arc at every strip edge, chords never above a strip bottom) -> {_M14['pivot'][1] - H14_SKID_R:.3f} over the felt at the centre, {_M14['pivot'][1] - math.sqrt(H14_SKID_R ** 2 - 1.05 ** 2):.3f} at the ends, never below {_M14['pivot'][1] - H14_SKID_R:.3f} over the whole +-{_M14['amplitude_deg']:g} deg swing (an arc about the hinge rotates onto itself); 9-stud hanger (r 0.12) with red/cream bands.",
      extra=dict(cls="mover", merge=False, mover=(14, "icicle_bell")))
def icicle_bell(pb):
    hbox(pb, "Brass", (0, -9.0, 0), (2, 2, 2), 30, bevel=0.08)
    pb.lathe("Brass", [(1.32, -8.0), (1.48, -7.86), (1.22, -7.5), (0.75, -7.28), (0.3, -7.16), (0.0, -7.12)], 12,
             loc=(0, 0, 0), smooth=True)
    for k in range(10):
        x, z = D.yaw_rot(1.3, 0, 36 * k + 18)
        pb.cyl("Ice", 0.07, 0.0, 0.32, 5, loc=tuple(R(x, -7.98 + 0.16 + 0.02, z)), rot=(180, 0, 0), smooth=False)
    # rocker skid (Round 3 'clear'): envelope of the 9 strip colliders - flat top at the strip tops, underside on the arc
    # r H14_SKID_R about the hinge with a vertex at every strip edge (+3 between), so each chord stays at or below the strip
    # bottom it spans (the strip's outer corner is on the arc, its flat bottom inside it)
    xs = []
    for a, b in zip(H14_FOOT_X[:-1], H14_FOOT_X[1:]):
        xs += [a + (b - a) * k / 4 for k in range(4)]
    xs.append(H14_FOOT_X[-1])
    under = [(x, -math.sqrt(H14_SKID_R ** 2 - x * x)) for x in xs]
    skid = [(H14_FOOT_X[0], H14_FOOT_TOP), (H14_FOOT_X[-1], H14_FOOT_TOP)] + list(reversed(under))
    extrude_xy(pb, "Brass", skid, -H14_FOOT_Z, H14_FOOT_Z)
    for i in range(8):
        y0 = -0.3 - i * 0.85
        pb.cyl("MoveRed" if i % 2 == 0 else "MoveCream", 0.12, 0.12, 0.85, 8, loc=tuple(R(0, y0 - 0.425, 0)), smooth=True)
    pb.cyl("Brass", 0.25, 0.25, 0.7, 10, loc=tuple(R(0, 0, 0)), rot=(90, 0, 0), smooth=True)
    pb.cyl("Brass", 0.22, 0.22, 0.3, 8, loc=tuple(R(0, -7.12, 0)), smooth=True)


# ------------------------------------------------------------------------------------------------ H17 aurora span (toggle)
@prop("aa_h17_aurora_span", [17], "P1", target=[3, 0.4, 8], kind="toggle", motion=_motion(17, "aurora_span"),
      placements=[dict(hole=17, pos=D.mover(17, "aurora_span")["pivot"], yaw=0.0)],
      origin="pivot = light_span top centre [0,0,-29]",
      notes="Neon light deck 3 x 0.4 x 8 (top = felt light_span top 0), mint core with violet edges; script fades Transparency 1->0 (0.6 s) / solid 6 s / 0->0.85 (0.6 s) / gone 1.8 s; collider only in [0.6, 6.6) s. Not a moving part (no red/cream).",
      extra=dict(cls="mover", merge=False, mover=(17, "aurora_span"), gap_ok=True))
def aurora_span(pb):
    hbox(pb, "AuroraMint", (0, -0.2, 0), (2.7, 0.4, 8))
    for side in (-1, 1):
        hbox(pb, "AuroraViolet", (side * 1.425, -0.2, 0), (0.15, 0.4, 8))
