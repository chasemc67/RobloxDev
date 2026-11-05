"""P1 moving parts (origin = pivot, axis aligned) + their static companions."""
import math, random
import bmesh
from mathutils import Vector, Matrix
from registry import prop
from lglib import M, R, TAU
import lglib
import dressing_lib as DL

# pass 8 (holes.json Round 7 final): the H7 log, H8 root door and H9 pendulum read their size / motion from holes.json
_HJ = {h["number"]: h for h in DL.load_holes()}


def _mp(n, mid):
    return [m for m in _HJ[n]["moving_parts"] if m["id"] == mid][0]


def _slide_motion(n, mid, fit):
    m = _mp(n, mid)
    d = dict(type="slide", axis_roblox=list(m["axis"]), speed=m["speed"], units="studs/s", range=list(m["range"]),
             phase=m.get("phase", 0.0), course_local_pivot=list(m["pivot"]), hole=f"H{n}", holes_json_id=mid, fit=fit)
    for k in ("dwell", "period_s"):
        if k in m:
            d[k] = m[k]
    return d


_LOG, _DOOR, _PEND = _mp(7, "log"), _mp(8, "root_door"), _mp(9, "lantern_pendulum")
LOG_HALF = _LOG["blockers"][0]["size"][0] / 2                       # 2.6: round body
LOG_TIP = max(abs(b["center"][0]) + b["size"][0] / 2 * math.sqrt(2) for b in _LOG["blockers"][1:]) \
    if len(_LOG["blockers"]) > 1 else LOG_HALF                      # 3.0: pointed ends (45-deg end blockers)
DOOR_L = _DOOR["blockers"][0]["size"][2]                             # 3.6


def ring_box(pb, mat, r_in, r_out, thick, segs=16, matrix=None, smooth=False):
    """Flat annulus ring (rectangular section) in the XY plane, centred on z=0."""
    t = bmesh.new()
    loops = []
    for (r, z) in ((r_in, -thick / 2), (r_out, -thick / 2), (r_out, thick / 2), (r_in, thick / 2)):
        loops.append([t.verts.new((r * math.cos(TAU * i / segs), r * math.sin(TAU * i / segs), z)) for i in range(segs)])
    for a, b in zip(loops, loops[1:] + loops[:1]):
        for i in range(segs):
            t.faces.new((a[i], a[(i + 1) % segs], b[(i + 1) % segs], b[i]))
    bmesh.ops.recalc_face_normals(t, faces=t.faces)
    pb.add(mat, t, matrix, smooth)


def mushroom_cap(pb, r, z0, h, mat_cap="ToadRed", mat_under="Cream", spots=6, seed=0, segs=16, matrix=None,
                 spot_mat="Cream", squash=1.0):
    """Dome cap: underside at z0, top at z0+h. Spots sit on the surface."""
    mtx = matrix or Matrix.Identity(4)
    prof = [(r * 0.25, z0 + h * 0.05), (r * 0.92, z0), (r, z0 + h * 0.12)]
    for i in range(1, 7):
        a = i / 7 * math.pi / 2
        prof.append((r * math.cos(a) * 0.98, z0 + h * 0.12 + (h * 0.88) * math.sin(a)))
    prof.append((0, z0 + h))
    pb.lathe(mat_cap, prof, segs, matrix=mtx, smooth=True)
    pb.cyl(mat_under, r * 0.9, r * 0.25, h * 0.08, segs, loc=(0, 0, z0 + h * 0.02), matrix=mtx, smooth=False)
    rnd = random.Random(seed)
    for k in range(spots):
        a = TAU * k / spots + rnd.uniform(-0.3, 0.3)
        el = rnd.uniform(0.35, 1.05) if k else 1.45
        x, y = math.cos(a) * math.cos(el), math.sin(a) * math.cos(el)
        z = math.sin(el)
        p = Vector((x * r * 0.98, y * r * 0.98, z0 + h * 0.12 + h * 0.88 * z))
        nrm = Vector((x / r, y / r, z / (h * 0.88))).normalized()
        q = Vector((0, 0, 1)).rotation_difference(nrm)
        sr = r * rnd.uniform(0.12, 0.2)
        pb.sphere(spot_mat, sr, segs=8, rings=4,
                  matrix=mtx @ Matrix.Translation(p) @ q.to_matrix().to_4x4() @ Matrix.Diagonal((1, 1, 0.25, 1)))


# ============================================================================ H4 carousel
@prop("h4_carousel_bar", ["H4"], "P1", kind="moving", target=[6, 4, 6], group="moving",
      origin="PIVOT = hub centre at felt level (course-local H4 [0, 0, -21])",
      front="n/a (rotates)",
      motion=dict(type="rotate", axis_roblox=[0, 1, 0], speed=30.0, units="deg/s", range=None, phase=0.0,
                  course_local_pivot=[0, 0, -21], hole="H4", holes_json_id="spinner",
                  fit="pass 6 (Round 5): padded arms = blocker boxes 2.3x1x0.7 at x +-1.85 (r 0.7..3.0), y 0..1 "
                      "(bar spans x -3..3); everything below y 1 stays inside them"),
      placements=[dict(hole="H4", pos=[0, 0, -21], yaw=0, note="CFrame = pivot * Angles(0, rad(30*t), 0)")],
      notes="2 short PADDED puffball arms (soft bumpers, restitution 0.65) + toadstool hub cap (rotates). Static "
            "stalk = toadstool_hub_static. props.md 6x4x6 is the swept circle; the part itself is ~6.4 x 3.6 x 1.5.")
def carousel(pb):
    # pass 6: arms 2.3 long (r 0.7..3.0); padded = cream cushion pads + rounded cream tip bumpers, red core
    pb.box("MoveRed", (6.0, 0.62, 0.9), loc=(0, 0, 0.47), bevel=0.22, segs=2)
    for sx in (-1, 1):
        for x in (1.05, 1.75):
            pb.box("MoveCream", (0.34, 0.7, 0.98), loc=(sx * x, 0, 0.5), bevel=0.14, segs=2)
        # rounded tip bumper (cushion), inside the blocker end (|x| <= 3.0, |z| <= 0.35, y 0..1)
        pb.box("MoveCream", (0.52, 0.7, 0.98), loc=(sx * 2.72, 0, 0.5), bevel=0.26, segs=3)
        pb.box("MoveRed", (0.12, 0.66, 0.9), loc=(sx * 2.4, 0, 0.47), bevel=0.04)
        pb.tube("MoveCream", [(sx * 2.62, 0, 0.95), (sx * 2.7, 0, 1.5), (sx * 2.6, 0, 2.0), (sx * 2.55, 0, 2.3)],
                [0.2, 0.17, 0.15, 0.15], 8)
        pb.sphere("MoveCream", 0.62, loc=(sx * 2.55, 0, 2.8), scale=(1, 1, 0.9), segs=14, rings=9)
        pb.sphere("MoveCream", 0.4, loc=(sx * 1.4, 0, 1.28), scale=(1, 1, 0.85), segs=12, rings=7)
        for k in range(5):
            a = TAU * k / 5
            pb.sphere("MoveRed", 0.07, loc=(sx * 2.55 + math.cos(a) * 0.45, math.sin(a) * 0.45, 3.1), segs=6, rings=4)
    # hub cap (rotates with the bar), sits on the static stalk top (y=2.0)
    pb.cyl("Cream", 0.5, 0.55, 0.55, 12, loc=(0, 0, 2.27))
    mushroom_cap(pb, 1.5, 2.5, 1.1, spots=7, seed=4)


@prop("toadstool_hub_static", ["H4"], "P1", target=[1.4, 2, 1.4], group="moving",
      notes="Static stalk under the carousel (collision = the 'hub' bumper block 1.4x2.5x1.4).",
      placements=[dict(hole="H4", pos=[0, 0, -21], yaw=0)])
def hub_static(pb):
    pb.lathe("Cream", [(0.72, 0), (0.7, 0.15), (0.6, 0.5), (0.56, 1.2), (0.58, 1.8), (0.62, 2.0), (0, 2.0)], 14,
             wobble=0.03)
    pb.torus("Moss", 0.66, 0.1, 14, 5, loc=(0, 0, 0.07))
    ring_box(pb, "Cream", 0.55, 0.7, 0.06, 14, matrix=M((0, 0, 1.55)))


# ============================================================================ H6 mill wheel
WHEEL_PIVOT = [7.5, 3.6, -8.5]


@prop("h6_mill_wheel", ["H6"], "P1", kind="moving", target=[7.2, 7.2, 8], group="moving",
      origin="PIVOT = axle centre (course-local H6 [7.5, 3.6, -8.5]); axle along Roblox Z",
      front="n/a (rotates)",
      motion=dict(type="rotate", axis_roblox=[0, 0, 1], speed=30.0, units="deg/s", range=None, phase=0.0,
                  course_local_pivot=WHEEL_PIVOT, hole="H6", holes_json_id="millwheel",
                  fit="2 paddle boards = blockers 0.6x1.4x7.6 at r=2.9 (roll 0 and 180). Rims at z=+-3.65 sit "
                      "just outside the 7-wide felt. Axle runs z -4.4 (north bearing trestle) .. +7.8 (0.3 into "
                      "the mill-house north wall at course z=-1).",
                  discrepancy="props.md lists pivot (12.5,3.6,-12.5) and 3 paddles; holes.json (authoritative, "
                              "matches collision) has pivot (7.5,3.6,-8.5) and 2 paddles. Built to holes.json."),
      placements=[dict(hole="H6", pos=WHEEL_PIVOT, yaw=0, note="CFrame = pivot * Angles(0, 0, rad(30*t))")],
      notes="Rotates about Roblox +Z. Paddles dip to the felt: cut the 0.8 slot in the visual felt and notch the "
            "visual rail5 (north rail) at x 5..10 up to rail height, the rims/paddles pass through there.")
def mill_wheel(pb):
    # Blender: axle along -Y (Roblox +Z). Wheel plane = Blender XZ.
    W = Matrix.Rotation(math.radians(90), 4, "X")  # maps local Z (ring normal) -> Blender -Y
    for zr in (-3.65, 3.65):
        yb = -zr
        ring_box(pb, "Oak", 3.15, 3.6, 0.26, 16, matrix=Matrix.Translation((0, yb, 0)) @ W)
        for k in range(6):
            a = math.radians(30 + 60 * k)
            mid = 1.9
            pb.box("Oak", (3.0, 0.2, 0.24), loc=(math.cos(a) * mid, yb, math.sin(a) * mid), rot=(0, -math.degrees(a), 0),
                   bevel=0.04)
        pb.cyl("RootBark", 0.7, 0.7, 0.5, 10, loc=(0, yb, 0), rot=(90, 0, 0), smooth=False)
        pb.cyl("Iron", 0.74, 0.74, 0.14, 10, loc=(0, yb, 0), rot=(90, 0, 0), smooth=False)
    # axle
    pb.cyl("RootBark", 0.3, 0.3, 12.2, 10, loc=(0, -(7.8 - 4.4) / 2, 0), rot=(90, 0, 0))
    for yb in (4.0, 0.0, -5.5, -7.3):
        pb.cyl("Iron", 0.34, 0.34, 0.16, 10, loc=(0, yb, 0), rot=(90, 0, 0), smooth=False)
    # 2 paddle boards (roll 0 = straight down, roll 180 = straight up) + their arms
    for sgn in (-1, 1):
        zc = sgn * 2.9
        pb.box("MoveRed", (0.5, 7.5, 1.36), loc=(0, 0, zc), bevel=0.06)
        for yy in (-3.0, -1.5, 0.0, 1.5, 3.0):
            pb.box("MoveCream", (0.54, 0.5, 1.38), loc=(0, yy, zc))
        for yy in (-2.2, 2.2):
            pb.box("MoveCream", (0.24, 0.24, 2.3), loc=(0, yy, sgn * 1.2), bevel=0.04)


@prop("h6_wheel_trestle", ["H6"], "P1", target=[2.2, 4.2, 0.8], group="moving",
      notes="Static A-frame bearing that carries the north end of the mill-wheel axle, just outside rail5.",
      placements=[dict(hole="H6", pos=[7.5, 0.0, -12.95], yaw=0)])
def trestle(pb):
    for sx in (-1, 1):
        pb.tube("Oak", [(sx * 1.0, 0, 0.0), (sx * 0.25, 0, 3.4)], 0.13, 6, smooth=False)
    pb.box("Oak", (1.6, 0.2, 0.18), loc=(0, 0, 1.4), bevel=0.03)
    pb.box("RootBark", (0.9, 0.6, 0.5), loc=(0, 0, 3.55), bevel=0.06)
    pb.cyl("Iron", 0.36, 0.36, 0.64, 10, loc=(0, 0, 3.6), rot=(90, 0, 0), smooth=False)
    for sx in (-1, 1):
        pb.box("Slate", (0.5, 0.5, 0.25), loc=(sx * 1.0, 0, 0.12), bevel=0.06)


# ============================================================================ H7 floating log
@prop("h7_floating_log", ["H7"], "P1", kind="moving", target=[2 * LOG_TIP, 0.8, 0.8], group="moving",
      origin="PIVOT = log bottom centre on the felt (course-local H7 [0, -1.2, -20.5]); log centre is +0.4 above",
      front="n/a (slides along X)",
      motion=_slide_motion(7, "log", (f"Round 7: round body {2 * LOG_HALF:g} long (blocker {2 * LOG_HALF:g}x0.8x0.8 "
                                      f"+0.4 above the pivot) + whittled points to a vertical edge at x = "
                                      f"+-{LOG_TIP:g} (the 45-deg end blockers); travel {_LOG['range']} at "
                                      f"{_LOG['speed']} studs/s with dwell {_LOG.get('dwell')}, cycle "
                                      f"{_LOG.get('period_s')} s; the tips stop {_LOG.get('end_clearance', 0.5)} short "
                                      "of each rail line (x = +-10)")),
      placements=[dict(hole="H7", pos=list(_LOG["pivot"]), yaw=0, note="pos = pivot + (offset(t), 0, 0)")],
      notes=f"Mossy log on a hidden rail, {2 * LOG_TIP:g} long with whittled pointed ends (pale MoveCream wood, the "
            "last 0.4 tapers to a vertical edge). No rail mesh (hidden). Pauses at the ends: see motion.dwell.")
def log(pb):
    L = LOG_HALF
    rot = Matrix.Rotation(math.radians(90), 4, "Y")
    prof = [(0.39, -L + 2 * L * i / 6) for i in range(7)]
    pb.lathe("MoveRed", prof, 10, matrix=Matrix.Translation((0, 0, 0.4)) @ rot, smooth=True, wobble=0.04, seed=3)
    for xb in (-L * 0.67, 0.0, L * 0.67):
        pb.cyl("MoveCream", 0.4, 0.4, 0.42, 10, loc=(xb, 0, 0.4), rot=(0, 90, 0), smooth=True)
    # whittled points: hull of the body ring at |x| = L and a vertical edge at |x| = LOG_TIP (inside the 45-deg box)
    for sx in (-1, 1):
        t = bmesh.new()
        for k in range(10):
            a = TAU * k / 10
            t.verts.new((sx * (L - 0.02), 0.385 * math.cos(a), 0.4 + 0.385 * math.sin(a)))
        for z in (0.03, 0.4, 0.77):
            t.verts.new((sx * (LOG_TIP - 0.01), 0.0, z))
        bmesh.ops.convex_hull(t, input=t.verts)
        pb.add("MoveCream", t)
        pb.torus("MoveRed", 0.395, 0.03, 10, 4, loc=(sx * (L - 0.05), 0, 0.4), rot=(0, 90, 0))
    pb.sphere("Moss", 0.5, loc=(-0.6, 0.05, 0.72), scale=(2.0, 0.7, 0.16), segs=10, rings=5)
    pb.sphere("Moss", 0.35, loc=(1.3, -0.05, 0.73), scale=(1.6, 0.8, 0.2), segs=10, rings=5)
    # tiny mushrooms on the side (stay inside the 0.8 box)
    for x in (0.5, 0.8):
        pb.cyl("Cream", 0.03, 0.03, 0.12, 6, loc=(x, -0.36, 0.52), rot=(90, 0, 0))
        pb.sphere("CapOrange", 0.07, loc=(x, -0.42, 0.52), scale=(1, 0.6, 1), segs=8, rings=4)


# ============================================================================ H9 portcullis
@prop("h9_root_portcullis", ["H9"], "P1", kind="moving", target=[0.8, 1.4, 7.4], group="moving",
      origin="PIVOT = base centre at felt level (course-local H9 [6, 1, -25.5]); mesh spans y -0.3..+1.1",
      front="n/a (slides along Y)",
      motion=dict(type="slide", axis_roblox=[0, 1, 0], speed=0.9, units="studs/s", range=[0.0, 1.8], phase=0.0,
                  course_local_pivot=[6, 1.0, -25.5], hole="H9", holes_json_id="root_gate",
                  fit="matches blocker 0.8x1.4x7.4 centred +0.4 above pivot (bottom 0.3 under the felt when closed); "
                      "pass 6: travel 0..1.8 at 0.9 studs/s (same 4 s cycle, open ~70%)"),
      placements=[dict(hole="H9", pos=[6, 1.0, -25.5], yaw=0, note="pos = pivot + (0, offset(t), 0)")],
      notes="Gate of twisted roots in the trunk-tunnel mouth. Bottom tips go 0.3 below the felt when closed; "
            "hide that with the felt (it is under the felt surface).")
def portcullis(pb):
    rnd = random.Random(9)
    n = 12
    for i in range(n):
        y = -3.45 + 6.9 * i / (n - 1)
        x0 = rnd.uniform(-0.12, 0.12)
        pts = [(x0 * 0.3, y, -0.3), (x0, y + rnd.uniform(-0.08, 0.08), 0.15), (-x0, y, 0.6), (x0 * 0.5, y, 1.04)]
        pb.tube("MoveRed" if i % 2 == 0 else "MoveCream", pts, [0.03, 0.11, 0.12, 0.11], 6, wobble=0.15, seed=i)
    for z, ph in ((0.3, 0), (0.85, 1)):
        pts = []
        for k in range(25):
            y = -3.7 + 7.4 * k / 24
            pts.append((0.22 * math.sin(k * math.pi / 2 + ph * math.pi), y, z + 0.04 * math.sin(k)))
        pb.tube("MoveCream", pts, 0.09, 6, wobble=0.1, seed=20 + z)
    for y in (-2.5, 0.4, 2.9):
        pb.sphere("Moss", 0.22, loc=(0.1, y, 0.95), scale=(1.2, 2.0, 0.6), segs=8, rings=4)
    for k in range(10):
        y = rnd.uniform(-3.4, 3.4)
        pb.sphere(rnd.choice(["MapleRed", "Pumpkin", "Gold"]), 0.09, loc=(rnd.uniform(-0.3, 0.3), y, rnd.uniform(0.1, 1.0)),
                  scale=(1, 1.8, 0.3), rot=(rnd.uniform(0, 90), 0, rnd.uniform(0, 180)), segs=6, rings=3, smooth=False)


# ============================================================================ H9 lantern pendulum (pass 6)
# Round 5 replaced the rotating lantern bar + its post with a swinging pendulum (holes.json moving_parts
# 'lantern_pendulum', type 'swing'). Origin = HINGE; the bob (lantern body) fills the 1.6 x 1.8 x 1.0 blocker centred
# 7.0 below the hinge; the chain links run hinge -> bob top. Swing plane = local x-y (axis Roblox +Z).
PEND_PIVOT = list(_PEND["pivot"])                        # Round 7: [22, 8.996, -38.5]
_PB = _PEND["blockers"][0]                               # Round 7: bob 1.6 x 1.8 x 1.6 turned 30 deg, 7.0 below
# pass 9 (Round 9): collider foot 0.9 x 0.4 x 1.6 (Round 10: 1.0 x 0.4 x 1.6 centred 7.759 below), yaw 0 (square to
# the swing), centred 7.762 below the hinge; the mesh
# gets a matching dark-iron base plinth of exactly that box (merged into the __Iron MeshPart)
_PF = _PEND["blockers"][1] if len(_PEND["blockers"]) > 1 else None
PEND_AMP, PEND_T = _PEND["amplitude_deg"], _PEND["period_s"]


@prop("h9_lantern_pendulum", ["H9"], "P1", kind="moving", target=[1.6, 8.0, 1.6], group="moving",
      origin=f"PIVOT = HINGE (course-local H9 {PEND_PIVOT}); the mesh hangs straight down from it",
      front="n/a (swings about Roblox +Z)",
      motion=dict(type="swing", axis_roblox=list(_PEND["axis"]), amplitude_deg=PEND_AMP, period_s=PEND_T,
                  phase=_PEND.get("phase", 0.0), speed=_PEND["speed"], units="deg/s (peak, at the bottom of the swing)",
                  range=list(_PEND["range"]), course_local_pivot=PEND_PIVOT, hole="H9",
                  holes_json_id="lantern_pendulum",
                  formula=f"angle(t) = {PEND_AMP:g} * sin(360 * t / {PEND_T:g} s + 0) deg, right-hand rule about +Z",
                  fit=(f"Round 7: square bob (lantern body) inside the blocker {_PB['size'][0]:g}x{_PB['size'][1]:g}x"
                       f"{_PB['size'][2]:g} turned {_PB['yaw']:g} deg about the vertical, centred "
                       f"{-_PB['center'][1]:g} below the hinge (bottom {-_PB['center'][1] + _PB['size'][1] / 2:g} "
                       "below); chain links 0.12 thick from the hinge to the bob top" +
                       (f". Pass 9-10 (Round 10): base plinth = the collider foot {_PF['size'][0]:g}x{_PF['size'][1]:g}x"
                        f"{_PF['size'][2]:g} at yaw {_PF.get('yaw', 0):g} (= {_PF.get('yaw', 0) - _PB['yaw']:g} deg "
                        f"relative to the body), centred {-_PF['center'][1]:g} below the hinge (bottom "
                        f"{-_PF['center'][1] + _PF['size'][1] / 2:g} below), dark iron, part of the __Iron mesh"
                        if _PF else ""))),
      placements=[dict(hole="H9", pos=PEND_PIVOT, yaw=0,
                       note=f"CFrame = CFrame.new(hinge) * CFrame.Angles(0, 0, rad({PEND_AMP:g} * sin(2*pi*t/"
                            f"{PEND_T:g})))")],
      notes="Great brass-and-paper lantern on a 7-stud chain, hung from h9_pendulum_root_beam. Round 7: square "
            f"{_PB['size'][0]:g} x {_PB['size'][1]:g} x {_PB['size'][2]:g} lantern body turned {_PB['yaw']:g} deg "
            "about the vertical. Red paper with cream bands/caps (moving-part signal scheme) and a glowing Neon "
            "window band: add a PointLight to the Glow part (Range 14, Brightness 2, #FFB347); it moves with the bob."
            + (" Pass 9-10 (Round 10, 1.0 long along the swing): weighted dark-iron base plinth under the body, the exact size / yaw of the "
               "invisible collider foot (holes.json blocker 2), so the foot never stops a ball outside the visible "
               "lantern. It is merged into the __Iron MeshPart and swings rigidly with the bob." if _PF else ""))
def lantern_pendulum(pb):
    # hinge: iron pin along the swing axis (Blender -Y) + shackle
    pb.cyl("Iron", 0.11, 0.11, 0.7, 10, loc=(0, 0, 0), rot=(90, 0, 0), smooth=False)
    pb.torus("Iron", 0.16, 0.045, 10, 4, loc=(0, 0, -0.12), rot=(0, 0, 0))
    hy = _PB["size"][1] / 2
    zc = _PB["center"][1]                 # -7.0
    zb, zt = zc - hy, zc + hy             # -7.9, -6.1
    # chain: 15 elongated links, alternating red / cream and alternating planes, hinge (-0.25) -> bob top
    n = 15
    top, bot = -0.25, zt - 0.02
    step = (top - bot) / n
    for i in range(n):
        z_ = top - step * (i + 0.5)
        mat = "MoveRed" if i % 2 == 0 else "MoveCream"
        rot = (90, 0, 0) if i % 2 == 0 else (90, 0, 90)
        pb.torus(mat, 0.13, 0.04, 8, 4, loc=(0, 0, z_), rot=rot)
        pb.box(mat, (0.06, 0.06, step * 0.55), loc=((0.13 if i % 2 == 0 else 0), (0 if i % 2 == 0 else 0.13), z_))
        pb.box(mat, (0.06, 0.06, step * 0.55), loc=((-0.13 if i % 2 == 0 else 0), (0 if i % 2 == 0 else -0.13), z_))
    # bob = square great lantern filling the blocker (half-width w), turned by the blocker yaw about the vertical.
    # 4-sided lathes / tori turned 45 deg give axis-aligned squares (radius = half-diagonal).
    w = min(_PB["size"][0], _PB["size"][2]) / 2
    Y = Matrix.Rotation(math.radians(_PB.get("yaw", 0.0)), 4, "Z") @ Matrix.Rotation(math.radians(45), 4, "Z")
    d = math.sqrt(2)
    pb.cyl("CapGold", 0.78 * w * d, 0.6 * w * d, 0.2, 4, loc=(0, 0, zt - 0.1), matrix=Y, smooth=False)   # top cap
    pb.cyl("MoveCream", 0.35 * w * d, 0.19, 0.12, 4, loc=(0, 0, zt - 0.02), matrix=Y, smooth=False)   # <= chain 0.2
    pb.cyl("CapGold", 0.6 * w * d, 0.76 * w * d, 0.18, 4, loc=(0, 0, zb + 0.09), matrix=Y, smooth=False)  # bottom
    prof = [(0.78 * w * d, zb + 0.18), (0.92 * w * d, zb + 0.4), (0.985 * w * d, zb + 0.7), (0.99 * w * d, zb + 0.9),
            (0.985 * w * d, zb + 1.1), (0.92 * w * d, zb + 1.4), (0.78 * w * d, zt - 0.2)]
    pb.lathe("MoveRed", prof, 4, matrix=Y, smooth=False)
    for z, r in ((zb + 0.4, 0.9 * w * d), (zb + 1.4, 0.9 * w * d)):
        pb.torus("MoveCream", r, 0.045, 4, 4, matrix=Y @ Matrix.Translation((0, 0, z)), smooth=False)
    pb.cyl("Glow", 0.985 * w * d, 0.985 * w * d, 0.22, 4, loc=(0, 0, zb + 0.9), matrix=Y, smooth=False)
    for z in (zb + 0.76, zb + 1.04):
        pb.torus("MoveCream", 0.955 * w * d, 0.035, 4, 4, matrix=Y @ Matrix.Translation((0, 0, z)), smooth=False)
    # vertical cream corner posts (brass-lantern frame)
    for k in range(4):
        a = TAU * k / 4
        pts = [(math.cos(a) * r * w * d, math.sin(a) * r * w * d, z) for (r, z) in
               ((0.76, zb + 0.2), (0.9, zb + 0.55), (0.95, zb + 0.9), (0.9, zb + 1.25), (0.76, zt - 0.2))]
        pb.tube("MoveCream", pts, 0.035, 4, matrix=Y, smooth=False)
    if _PF is None:
        pb.cyl("MoveRed", 0.08, 0.12, 0.06, 6, loc=(0, 0, zb + 0.03), smooth=False)
    else:
        # pass 9: base plinth = the collider foot box exactly (Roblox x/y/z size -> Blender x/z/y), turned by the
        # foot's own course yaw (body yaw 30, foot yaw 0 -> -30 relative to the body). Sharp-edged so it covers the
        # foot to its corners; the old bottom finial would sit inside it, so it is dropped.
        fx, fy, fz = _PF["size"]
        Yf = Matrix.Rotation(math.radians(_PF.get("yaw", 0.0)), 4, "Z")
        pb.box("Iron", (fx, fz, fy), loc=(_PF["center"][0], -_PF["center"][2], _PF["center"][1]), matrix=Yf)


# ============================================================================ H8 root door
@prop("h8_root_door", ["H8"], "P1", kind="moving", target=[0.7, 1, DOOR_L], group="moving",
      origin="PIVOT = base centre at felt level (course-local H8 [4.75, 0, -11.5]) = the CLOSED position",
      front="n/a (slides along Z)",
      motion=_slide_motion(8, "root_door", (f"Round 7: matches blocker 0.7x1x{DOOR_L:g} centred +0.5 above the pivot; "
                                            f"travel {_DOOR['range']} at {_DOOR['speed']} studs/s, dwell "
                                            f"{_DOOR.get('dwell')}, cycle {_DOOR.get('period_s')} s; open (+4) the "
                                            "door slides through the junction's south rail line z -8 into the "
                                            "h8_door_pocket root knot")),
      placements=[dict(hole="H8", pos=list(_DOOR["pivot"]), yaw=0, note="pos = pivot + (0, 0, offset(t))")],
      notes=f"Sliding root door ({DOOR_L:g} long) across the firefly alcove mouth (P1). Closed at offset 0, open at "
            "+4 inside the h8_door_pocket knot on the south rail line (notch the visual rail kit there).")
def root_door(pb):
    L = DOOR_L
    n = 4
    seg = (L - 0.4) / n
    for i in range(n):
        y = -L / 2 + 0.2 + seg * (i + 0.5)
        pb.box("MoveRed" if i % 2 == 0 else "MoveCream", (0.36, seg - 0.04, 0.96), loc=(0, y, 0.48), bevel=0.05)
    for z in (0.22, 0.76):
        pb.box("Iron", (0.4, L - 0.02, 0.1), loc=(0, 0, z))
    for sx in (-1, 1):
        pts = [(sx * 0.25, -L / 2 + 0.05, 0.05)]
        for k in range(1, 9):
            pts.append((sx * (0.24 + 0.06 * math.sin(k * 1.3)), -L / 2 + L * k / 8 * 0.98,
                        0.12 + 0.75 * abs(math.sin(k * 0.8 + sx))))
        pb.tube("RootBark", pts, 0.1, 6, wobble=0.15, seed=sx + 5)
    for sy in (-1, 1):
        pb.box("RootBark", (0.7, 0.16, 1.0), loc=(0, sy * (L / 2 - 0.08), 0.5), bevel=0.05)
    pb.sphere("Moss", 0.3, loc=(0, 0.6, 0.96), scale=(1.1, 2.0, 0.15), segs=8, rings=4)
