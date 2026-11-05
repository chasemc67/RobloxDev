"""Sugarloaf Canyon world layout -> models/layout.json (system python3; numpy + world/tools/worldlib.py).

  python3 models/_src/sc_layout.py

Every placed instance: {piece, pos [x,y,z] (Roblox world studs, piece pivot = base centre), yaw (deg about +Y,
Roblox CFrame.Angles(0, rad(yaw), 0)), scale (optional [sx,sy,sz]), src (world.json id or generator rule), note}.
Clusters (`clusters`) are merged meshes: the build bakes their members (world.json pieces) into one FBX per material
at the cluster pivot, so stripes follow the members' real world heights.
Everything that world.json doesn't give is logged in `assumptions` (copied into pass1_summary.md).
"""
import json, math, os, random, sys
import numpy as np

SRC = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.dirname(SRC)
COURSE = os.path.dirname(MODELS)
sys.path.insert(0, os.path.join(COURSE, "world", "tools"))
import worldlib as WL  # noqa: E402
import sc_specs as S   # noqa: E402

W = WL.load_world()
PIECES = {p["id"]: p for p in W["backdrop"]["pieces"]}
ASSUME = []
INST = []
CLUSTERS = {}


def assume(s):
    ASSUME.append(s)


def r3(v, n=2):
    return [round(float(x), n) for x in v]


def H(x, z):
    return float(WL.height_at(W, np.array([x]), np.array([z]))[0])


def Hv(X, Z):
    return WL.height_at(W, np.asarray(X, float), np.asarray(Z, float))


def yaw_facing(dx, dz):
    """yaw so that local -Z (the front) points along world (dx, dz)."""
    return round(math.degrees(math.atan2(-dx, -dz)), 2)


def add(piece, pos, yaw=0.0, scale=None, src=None, note=""):
    e = dict(piece=piece, pos=r3(pos), yaw=round(float(yaw), 2))
    if scale is not None:
        e["scale"] = r3(scale, 3)
    e["src"] = src or "generated"
    if note:
        e["note"] = note
    INST.append(e)
    return e


# ----------------------------------------------------------------------------- keep-outs
FOOT = [(h["number"], h["footprint_bbox"]) for h in W["holes"]]
WALK_TYPES = ("walk", "ramp", "stairs", "landing", "bridge", "dam_crest")
SEGS = []
for p in W["paths"]:
    for s in p["segments"]:
        if s["type"] in WALK_TYPES or s["type"] == "on_hole":
            SEGS.append((p["id"], s, p["width"]))


def foot_dist(x, z):
    """Distance (XZ) to the nearest hole footprint bbox (0 inside)."""
    best = 1e9
    for _, b in FOOT:
        dx = max(b["x"][0] - x, 0, x - b["x"][1])
        dz = max(b["z"][0] - z, 0, z - b["z"][1])
        best = min(best, math.hypot(dx, dz))
    return best


def seg_dist(x, z, s):
    a, b = s["start"], s["end"]
    ax, az, bx, bz = a[0], a[2], b[0], b[2]
    vx, vz = bx - ax, bz - az
    L2 = vx * vx + vz * vz
    t = 0 if L2 < 1e-9 else max(0, min(1, ((x - ax) * vx + (z - az) * vz) / L2))
    return math.hypot(x - ax - t * vx, z - az - t * vz), t


def walk_clear(x, z, y_lo=-1e9, y_hi=1e9):
    """Smallest (distance to walkway centreline - half width) over walkway segments whose y is in [y_lo, y_hi]."""
    best = 1e9
    for _, s, w in SEGS:
        if s["type"] == "on_hole":
            continue
        d, t = seg_dist(x, z, s)
        y = s["start"][1] + (s["end"][1] - s["start"][1]) * t
        if y_lo - 8 <= y <= y_hi + 8:
            best = min(best, d - w / 2)
    return best


def lift_points():
    out = []
    for l in W["lifts"]:
        out += [l["bottom"], l["top"]]
    return out


LIFTP = lift_points()


def free_spot(x, z, r, y=None, foot=2.0, walk=1.5):
    """Instance of radius r at (x,z) keeps >= foot from footprints, >= walk from walkway edges, >= 4 from lift points."""
    if foot_dist(x, z) < r + foot:
        return False
    if walk_clear(x, z, (y if y is not None else -1e9), (y if y is not None else 1e9)) < r + walk:
        return False
    for p in LIFTP:
        if math.hypot(x - p[0], z - p[2]) < r + 6:
            return False
    return True


# ----------------------------------------------------------------------------- cliff + slot kit
def stack(base, top, slot=False):
    """Kit pieces (id, base_y) filling [base, base + 6n] with n = floor((top-base)/6)."""
    n = int(math.floor((top - base) / 6.0 + 1e-6))
    out = []
    y = base
    for h in (48, 24, 12, 6):
        k = h // 6
        while n >= k:
            kind = "slot" if slot and h in (24, 48) else "cliff"
            phase = int(round(y / 6)) % 6
            out.append((f"{kind}_w24_h{h}_p{phase}", y, h))
            y += h
            n -= k
    return out


def resample(pts, step, closed=False):
    pts = [np.array(p, float) for p in pts]
    if closed:
        pts = pts + [pts[0]]
    out = []
    for a, b in zip(pts, pts[1:]):
        L = np.linalg.norm(b - a)
        n = max(1, int(round(L / step)))
        t_ = b - a
        nrm = np.array([t_[1], -t_[0]]) / max(L, 1e-9)
        for i in range(n):
            out.append((a + t_ * (i + 0.5) / n, nrm))
    return out


def cliff_lines():
    """(name, slot?, [(point, normal)...], face_offset) for every set-region edge and slot wall."""
    lines = []
    for r in W["terrain"]["regions"]:
        if r["op"] == "set":
            sh = r["shape"]
            if sh["type"] == "polygon":
                lines.append((r["id"], False, resample(sh["points"], S.CLIFF_STEP, closed=True), 3.4))
            else:
                cx, cz = sh["center"]
                rx, rz = sh["radii"]
                n = int(2 * math.pi * max(rx, rz) / S.CLIFF_STEP)
                pts = [(cx + rx * math.cos(2 * math.pi * i / n), cz + rz * math.sin(2 * math.pi * i / n)) for i in range(n)]
                lines.append((r["id"], False, resample(pts, S.CLIFF_STEP, closed=True), 3.4))
        elif r["op"] == "slot":
            for side in (-1, 1):
                pts = []
                P = r["points"]
                for i, p in enumerate(P):
                    a = np.array(P[max(i - 1, 0)][:2], float)
                    b = np.array(P[min(i + 1, len(P) - 1)][:2], float)
                    t_ = (b - a) / np.linalg.norm(b - a)
                    nrm = np.array([t_[1], -t_[0]]) * side
                    pts.append(np.array(p[:2], float) + nrm * (p[3] / 2 + 0.6))
                lines.append((f"{r['id']}_{'L' if side < 0 else 'R'}", r["id"] == "rock_candy_narrows",
                              resample(pts, S.CLIFF_STEP), 0.0))
    return lines


PANEL_X = 12.5          # half width of a kit panel (+ relief)
PANEL_Z = (-2.6, 8.5)   # local z extent: front relief (toward -Z) .. back


def panel_corners(fx, fz, yaw, grow=0.0):
    a = math.radians(yaw)
    c, s_ = math.cos(a), math.sin(a)
    out = []
    for lx, lz in ((-PANEL_X - grow, PANEL_Z[0] - grow), (PANEL_X + grow, PANEL_Z[0] - grow),
                   (PANEL_X + grow, PANEL_Z[1] + grow), (-PANEL_X - grow, PANEL_Z[1] + grow)):
        out.append((fx + lx * c + lz * s_, fz - lx * s_ + lz * c))
    return out


def rects_overlap(A, B):
    for P in (A, B):
        for i in range(4):
            ax, az = P[i]
            bx, bz = P[(i + 1) % 4]
            nx, nz = bz - az, ax - bx
            pa = [px * nx + pz * nz for px, pz in A]
            pb = [px * nx + pz * nz for px, pz in B]
            if max(pa) < min(pb) or max(pb) < min(pa):
                return False
    return True


def obb_corners(cx, cz, yaw, hx, hz):
    a = math.radians(yaw)
    c, s_ = math.cos(a), math.sin(a)
    return [(cx + lx * c + lz * s_, cz - lx * s_ + lz * c) for lx, lz in ((-hx, -hz), (hx, -hz), (hx, hz), (-hx, hz))]


def obb_foot_conflict(cx, cz, yaw, hx, hz, margin=2.05):
    P = obb_corners(cx, cz, yaw, hx, hz)
    for _, b in FOOT:
        B = [(b["x"][0] - margin, b["z"][0] - margin), (b["x"][1] + margin, b["z"][0] - margin),
             (b["x"][1] + margin, b["z"][1] + margin), (b["x"][0] - margin, b["z"][1] + margin)]
        if rects_overlap(P, B):
            return True
    return False


def panel_conflict(fx, fz, yaw, base, top):
    """'footprint' if the panel OBB is within 2 of a hole footprint bbox, 'walkway' if a walkway corridor passes through
    the panel's footprint at a height where the panel would stick up into it (panel top > walk y + 0.3)."""
    P = panel_corners(fx, fz, yaw)
    for _, b in FOOT:
        B = [(b["x"][0] - 2, b["z"][0] - 2), (b["x"][1] + 2, b["z"][0] - 2), (b["x"][1] + 2, b["z"][1] + 2),
             (b["x"][0] - 2, b["z"][1] + 2)]
        if rects_overlap(P, B):
            return "footprint"
    a = math.radians(yaw)
    c, s_ = math.cos(a), math.sin(a)
    for _, sg, w in SEGS:
        if sg["type"] == "on_hole":
            continue
        A, Bp = sg["start"], sg["end"]
        L = math.hypot(Bp[0] - A[0], Bp[2] - A[2])
        n = max(2, int(L / 0.75) + 1)
        for i in range(n):
            t = i / (n - 1)
            x = A[0] + (Bp[0] - A[0]) * t
            z = A[2] + (Bp[2] - A[2]) * t
            y = A[1] + (Bp[1] - A[1]) * t
            dx, dz = x - fx, z - fz
            lx, lz = dx * c - dz * s_, dx * s_ + dz * c
            m = w / 2 + 0.5
            if -PANEL_X - m <= lx <= PANEL_X + m and PANEL_Z[0] - m <= lz <= PANEL_Z[1] + m and top > y + 0.3 and base < y + 8:
                return "walkway"
    return None


def cliffs():
    n_stack = 0
    skipped = dict(low=0, outside=0, footprint=0, walkway=0)
    seen = []
    for name, slot, samples, off in cliff_lines():
        for p, nrm in samples:
            x, z = p
            if abs(x) > S.CLIFF_LIMIT or abs(z) > S.CLIFF_LIMIT:
                skipped["outside"] += 1
                continue
            ha, hb = H(x + nrm[0] * 4, z + nrm[1] * 4), H(x - nrm[0] * 4, z - nrm[1] * 4)
            out = nrm if ha < hb else -nrm                       # outward = downhill
            top = H(x - out[0] * 1.5, z - out[1] * 1.5) if not slot and not name.startswith(("taffy_gap", "licorice")) else None
            if top is None:                                      # slot walls: top of wall = mesa beyond the wall
                top = H(x - out[0] * 6, z - out[1] * 6)
            bot = H(x + out[0] * 8, z + out[1] * 8)
            if top - bot < S.CLIFF_MIN_DROP:
                skipped["low"] += 1
                continue
            fx, fz = x + out[0] * off, z + out[1] * off           # front-face line
            yaw = yaw_facing(out[0], out[1])
            base = math.floor((bot - 0.75) / 6.0) * 6.0
            why = panel_conflict(fx, fz, yaw, base, top)
            if why:
                skipped[why] += 1
                continue
            if any(math.hypot(fx - a, fz - b) < 6 for a, b in seen):
                continue
            seen.append((fx, fz))
            n_stack += 1
            for pid, y, h in stack(base, top, slot):
                add(pid, (fx, y, fz), yaw, src=f"cliff:{name}",
                    note=f"cliff stack {n_stack}: ground {bot:.1f} -> rim {top:.1f}")
    assume(f"Cliff/slot kit auto-placed along every terrain `set` edge and slot wall (resampled every {S.CLIFF_STEP} studs) "
           f"where the real heightfield drops >= {S.CLIFF_MIN_DROP} studs, |x|,|z| <= {S.CLIFF_LIMIT} (the outer rim is left to "
           f"terrain). Front face {3.4} studs outside the mesa edge (slot walls 0.6 inside the wall foot), base snapped down to a "
           f"multiple of 6 (buried >= 0.75), stack height floor((rim-base)/6)*6 so nothing pokes above the rim. {n_stack} stacks; "
           f"skipped: {skipped}.")


# ----------------------------------------------------------------------------- world.json pieces
def heroes():
    p = PIECES["old_sugarloaf_dome"]
    add("old_sugarloaf_shell", (p["pos"][0], 18.0, p["pos"][2]), 0, src=p["id"],
        note="pivot = dome base centre on the canyon floor")
    assume("old_sugarloaf_dome: world.json pos y is 207.1 (the summit); the shell's pivot is the base centre (80, 18, -130) "
           "and it is generated from the terrain hill formula (18 + 190 cos^2(pi/2 q), r 72) + 0.6 clearance, so it hugs "
           "the dome. It ends at y ~21 where the dome flattens into the floor.")
    p = PIECES["sunset_arch"]
    add("sunset_arch", p["pos"], 0, src=p["id"], note="opening axis = world X (faces west/east); legs span world Z")
    assume("sunset_arch: size [16, 46, 50] read as 16 thick (X, faces west), 50 wide along Z, 46 tall; opening 30 wide x 34 high, "
           "lintel 12 thick; legs buried 2 into the Crown.")
    p = PIECES["peppermint_dam"]
    add("peppermint_dam", p["pos"], 0, src=p["id"], note="crest deck y 116 (walkway), parapets to y 118")
    assume("peppermint_dam: body 8 thick + pilasters/cornice to the 10-stud bbox (z -310..-300); deck at y 116 (path p_h11_h12), "
           "parapet walls to y 118 at 4..5 studs from the centre line (walkway half-width 3), iron railings on the parapets to "
           "y 119.5. Spillway slot x -10..10, lip y 108, bridged by the crest deck (deck underside y 114.5). Arched relief bays on the "
           "downstream (south) face. Peppermint bands 8 studs high. The spillway water is NOT modelled (Beams per course.md).")
    p = PIECES["intake_tower"]
    add("intake_tower", p["pos"], 0, src=p["id"], note="base 8 below the reservoir surface (108)")
    p = PIECES["ranger_station"]
    add("ranger_station", p["pos"], -90, src=p["id"], note="porch faces east, toward the river and the Ranger Footbridge")
    assume("ranger_station: yaw -90 so the porch faces east (river/footbridge); world size [18,16,14] = depth 18 (X) x width 14 (Z).")
    p = PIECES["junction_town"]
    add("junction_town", p["pos"], 90, src=p["id"], note="5 false fronts face west toward the plaza/boardwalk")
    assume("junction_town: yaw 90 so the 5 false fronts (row 80 long, 30 deep incl. boardwalk) face west toward the plaza; "
           "shops: Candy Co., Saloon (clubhouse), Assay Office, General Store, Taffy Pull.")
    p = PIECES["water_tower"]
    add("water_tower", p["pos"], 0, src=p["id"])
    for k in ("gondola_top_station", "gondola_bottom_station"):
        p = PIECES[k]
        g = [l for l in W["lifts"] if l["type"] == "gondola"][0]
        other = g["bottom"] if k.startswith("gondola_top") else g["top"]
        add("gondola_station", p["pos"], yaw_facing(other[0] - p["pos"][0], other[2] - p["pos"][2]), src=p["id"],
            note="open end + bull wheel face along the cable")
    assume("gondola stations: one model for both ends, yawed so the open end faces along the cable. The cable, cabin and "
           "any mid-span towers are not modelled (moving parts / out of scope).")
    # cableway trestles: 3, one per 60 studs, centred at world.json pos
    p = PIECES["cableway_trestles"]
    cx, cz = p["pos"][0], p["pos"][2]
    for i, dz in enumerate((-60, 0, 60)):
        x, z = cx, cz + dz
        while not free_spot(x, z, 4.5, 150):
            x -= 2
        add("cableway_trestle", (x, H(x, z) - 0.3, z), 0, src=p["id"], note=f"trestle {i + 1}/3; cable runs along world Z")
    assume("cableway_trestles: 3 trestles on a line along Z at x -330 (z -260/-200/-140), shifted west only if they would "
           "touch a footprint or walkway; crossarm along X. The H14 swinging bucket is not built (per-hole moving part).")
    # mine-head (H2 landmark, not in backdrop.pieces)
    x, z = S.MINE_HEAD_POS
    assert free_spot(x, z, 9, 18), "mine head spot not clear"
    add("mine_head", (x, H(x, z) - 0.2, z), 90, src="invented:mine_head", note="headframe faces west toward H2")
    assume(f"mine_head: not in world.json backdrop.pieces; placed at ({x}, ground, {z}) east of H2 (>= 9 studs from its "
           "footprint), facing west. Static headframe, sheave wheel and portal only (no ore carts on rails).")


def lifts():
    LP = S.lift_params(W)
    for l in W["lifts"]:
        if l["type"] != "lift":
            continue
        key = S.LIFT_KEYS[l["name"]]
        b = l["bottom"]
        yaw = LP[key]["yaw"]
        add(f"lift_frame_{key}", b, yaw, src=f"lifts:{l['name']}",
            note=f"pivot = bottom boarding point; shaft + headframe here, gangway at +{l['rise']} runs local -Z to the top point")
        add("lift_cage", b, yaw, src=f"lifts:{l['name']}", note="static cage frame at the bottom stop; animate +Y by rise")
    assume("lift frames: shaft (11.2 x 11.2 well, 4 corner posts, bracing on the local +-X faces only between the two boarding "
           "levels, every face open 0..10 above both landings) stands on the BOTTOM boarding point, yawed to bisect the arriving "
           "walkway and the direction to the top point; a railed gangway at the top level runs from the shaft to 1 stud past the "
           "top boarding point (railings stop 6 short of it so the departing walk can turn). Cage roof 9.5 above its floor, "
           "headframe crosshead 11.5 above the top landing (head clearance >= 8). Cage gates are left to the build (open frame).")


def bridges():
    for p in W["paths"]:
        for s in p["segments"]:
            if s["type"] != "bridge":
                continue
            a, b = s["start"], s["end"]
            mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2]
            key = "ranger_footbridge" if "Ranger" in s["name"] else "licorice_rope_bridge"
            add(key, mid, yaw_facing(b[0] - a[0], b[2] - a[2]), src=f"paths:{p['id']}",
                note=f"{s['name']}: deck top = walkway y, length along local Z")


def walkway_kit():
    for p in W["paths"]:
        for s in p["segments"]:
            a, b = s["start"], s["end"]
            dx, dz = b[0] - a[0], b[2] - a[2]
            L = math.hypot(dx, dz)
            if L < 0.5:
                continue
            ux, uz = dx / L, dz / L
            if s["type"] == "stairs":
                lo, hi = (a, b) if b[1] > a[1] else (b, a)
                add("stair_flight_5", lo, yaw_facing(hi[0] - lo[0], hi[2] - lo[2]), src=f"paths:{p['id']}",
                    note="5 steps x 0.8 rise x 1.5 tread, 6 wide; pivot = bottom edge centre, climbs toward local -Z")
            elif s["type"] == "landing":
                add("landing_6x4", [(a[0] + b[0]) / 2, a[1], (a[2] + b[2]) / 2], yaw_facing(ux, uz),
                    scale=[1, 1, round(max(L, 1.0) / 4.0, 3)], src=f"paths:{p['id']}",
                    note="sandstone landing slab; scale Z = landing length / 4")
            elif s["type"] == "walk" and p["id"] == "p_h1_h2":
                n = max(1, math.ceil(L / 12.0))
                for i in range(n):
                    t0 = min(i * 12.0 + 6.0, L - 6.0) if L >= 12 else L / 2
                    cx, cz = a[0] + ux * t0, a[2] + uz * t0
                    yw = yaw_facing(ux, uz)
                    if obb_foot_conflict(cx, cz, yw, 3.0, 6.0):
                        continue
                    add("walk_boardwalk_6x12", [cx, a[1], cz], yw,
                        src=f"paths:{p['id']}", note="Junction boardwalk planks, top flush with the graded walkway")
            if s.get("rails") and s["type"] in ("walk", "ramp", "landing"):
                for side in s["rails"]:
                    sgn = 1 if side == "right" else -1
                    rx, rz = -uz * sgn, ux * sgn                     # right of the walking direction
                    off = p["width"] / 2 + 0.6
                    n = max(1, math.floor(L / 12.0))
                    for i in range(n):
                        t0 = (i + 0.5) * L / n
                        add("railing_12", [a[0] + ux * t0 + rx * off, a[1] + (b[1] - a[1]) * t0 / L, a[2] + uz * t0 + rz * off],
                            yaw_facing(ux, uz), scale=[1, 1, round(L / n / 12.0, 3)], src=f"paths:{p['id']}",
                            note=f"railing on the {side} side; scale Z = run / 12")
    assume("walkway kit placement: stair flights + landings on every world.json stairs/landing segment, boardwalk planks on the "
           "Junction Boardwalk (p_h1_h2) walk segments (pieces within 2 of a footprint dropped), railing_12 runs on every walk/ramp/landing side listed in `rails` "
           "(bridges and the dam crest carry their own railings). Other walk segments stay graded terrain (Ground).")


def clusters():
    hoo = sorted([p for p in W["backdrop"]["pieces"] if p["kind"] == "hoodoo_spire"], key=lambda p: p["pos"][2])
    n = len(hoo)
    groups = [hoo[:n // 3], hoo[n // 3: 2 * n // 3], hoo[2 * n // 3:]]
    for name, g in zip(("hoodoos_north", "hoodoos_mid", "hoodoos_south"), groups):
        mk_cluster(name, "hoodoo", g)
    mk_cluster("narrows_crystals", "crystal", [p for p in W["backdrop"]["pieces"] if p["kind"] == "rock_candy_crystal"])
    cac = [p for p in W["backdrop"]["pieces"] if p["kind"] == "lollipop_cactus"]
    mk_cluster("cacti_floor", "cactus", [p for p in cac if p["pos"][1] < 40])
    taffy = [p for p in cac if 40 <= p["pos"][1] < 150]
    mk_cluster("cacti_taffy_north", "cactus", [p for p in taffy if p["pos"][2] < 120])
    mk_cluster("cacti_taffy_south", "cactus", [p for p in taffy if p["pos"][2] >= 120])
    mk_cluster("cacti_crown", "cactus", [p for p in cac if p["pos"][1] >= 150])
    assume("hoodoos (34), crystals (16) and cacti (72) from world.json are baked into 8 merged cluster FBXs (Taffy Mesa cacti split north/south of z 120) (one MeshPart per "
           "material each) at their exact world pos/yaw/size, so strata follow world y. Variant FBXs (hoodoo_spire_a-d, "
           "crystal_cluster_a-c, lollipop_cactus_a-c) are also exported for hand placement. Member variant = hash of the id.")


def mk_cluster(name, kind, members):
    xs = [p["pos"][0] for p in members]
    zs = [p["pos"][2] for p in members]
    ys = [p["pos"][1] for p in members]
    piv = [round(sum(xs) / len(xs), 1), round(min(ys), 1), round(sum(zs) / len(zs), 1)]
    mem = []
    for p in members:
        v = S.variant_for(kind, p["id"])
        mem.append(dict(id=p["id"], kind=kind, variant=v, pos=p["pos"], yaw=p.get("yaw_deg", 0.0), size=p["size"]))
    CLUSTERS[name] = dict(kind=kind, pivot=piv, members=mem)
    add(name, piv, 0, src=f"cluster:{kind}", note=f"merged {len(mem)} world.json {kind}s; pivot = centroid at min member y")


def scatter():
    rnd = random.Random(1311)
    zone_of_hole = {h["number"]: h["zone"] for h in W["holes"]}
    centres = [(h["number"], (h["footprint_bbox"]["x"][0] + h["footprint_bbox"]["x"][1]) / 2,
                (h["footprint_bbox"]["z"][0] + h["footprint_bbox"]["z"][1]) / 2) for h in W["holes"]]
    taken = [(p["pos"][0], p["pos"][2], max(p["size"][0], p["size"][2]) / 2) for p in W["backdrop"]["pieces"]
             if p["kind"] in ("hoodoo_spire", "lollipop_cactus", "rock_candy_crystal")]
    taken += [(e["pos"][0], e["pos"][2], 10) for e in INST if not e["piece"].startswith(("cliff_", "slot_"))]
    groups = {}
    for pid, s, w in SEGS:
        if s["type"] not in ("walk", "ramp", "landing"):
            continue
        a, b = s["start"], s["end"]
        L = math.hypot(b[0] - a[0], b[2] - a[2])
        if L < 4:
            continue
        ux, uz = (b[0] - a[0]) / L, (b[2] - a[2]) / L
        t = rnd.uniform(2, 8)
        while t < L:
            side = rnd.choice((-1, 1))
            d = w / 2 + rnd.uniform(3.0, 10.0)
            x, z = a[0] + ux * t - uz * side * d, a[2] + uz * t + ux * side * d
            t += rnd.uniform(9, 16)
            y0 = a[1]
            hz = Hv([x - 1.5, x + 1.5, x, x], [z, z, z - 1.5, z + 1.5])
            if np.ptp(hz) > 1.0 or abs(float(np.mean(hz)) - y0) > 3:
                continue
            ws = float(WL.water_surface(W, np.array([x]), np.array([z]))[0])
            if ws > float(np.min(hz)) - 0.5:
                continue
            nh = min(centres, key=lambda c: math.hypot(c[1] - x, c[2] - z))[0]
            zone = zone_of_hole[nh]
            kinds = S.SCATTER_KINDS[zone]
            kind = rnd.choice(kinds)
            sc = rnd.uniform(0.8, 1.3)
            rad = S.SCATTER_RADIUS[kind] * sc
            if not free_spot(x, z, rad, y0, foot=4.0, walk=2.0):
                continue
            if any(math.hypot(x - tx, z - tz) < rad + tr + 1.5 for tx, tz, tr in taken):
                continue
            taken.append((x, z, rad))
            groups.setdefault(zone, []).append(dict(id=f"scatter_{len(taken)}", kind=kind, variant=kind,
                                                    pos=r3([x, float(np.min(hz)) - 0.25, z]),
                                                    yaw=round(rnd.uniform(0, 360), 1), scale=round(sc, 3)))
    for zone, mem in groups.items():
        name = "scatter_" + zone.lower().replace("sugarloaf ", "").replace(" ", "_")
        piv = [round(sum(m["pos"][0] for m in mem) / len(mem), 1), round(min(m["pos"][1] for m in mem), 1),
               round(sum(m["pos"][2] for m in mem) / len(mem), 1)]
        CLUSTERS[name] = dict(kind="scatter", pivot=piv, members=mem)
        add(name, piv, 0, src="generated:scatter", note=f"{len(mem)} scrub/rocks/gumdrop boulders along {zone} walkways")
    assume("scatter (not in world.json): scrub, rocks and gumdrop boulders every 9-16 studs along walk/ramp/landing segments, "
           "3-10 studs beyond the walkway edge, on flat dry ground (height range < 1 over 3 studs), >= 4 from footprints, >= 2 from "
           "walkway edges, >= 6 from lift points, not overlapping world.json scenery; kinds per zone (gumdrops on Taffy Mesa and "
           "the Crown); merged per zone.")


def dunes():
    rnd = random.Random(77)
    n = 0
    tries = 0
    while n < S.N_DUNES and tries < 4000:
        tries += 1
        x, z = rnd.uniform(-600, -330), rnd.uniform(-560, 60)
        hz = Hv([x - 10, x + 10, x, x, x], [z, z, z - 7, z + 7, z])
        if np.ptp(hz) > 1.2 or abs(float(np.mean(hz)) - 150) > 2:
            continue
        if not free_spot(x, z, 14, 150, foot=6.0, walk=4.0):
            continue
        if any(math.hypot(x - p["pos"][0], z - p["pos"][2]) < 18 for p in W["backdrop"]["pieces"] if p["kind"] == "hoodoo_spire"):
            continue
        if any(math.hypot(x - e["pos"][0], z - e["pos"][2]) < 30 for e in INST if e["piece"].startswith("sugar_dune")):
            continue
        add(f"sugar_dune_cap_{'ab'[n % 2]}", (x, float(np.min(hz)) - 0.4, z), rnd.uniform(0, 180), src="generated:dunes",
            note="powdered-sugar dune cap on the Hoodoo Bench")
        n += 1
    assume(f"powdered-sugar dune caps: {n} placed on flat Hoodoo Bench ground (x -600..-330), >= 6 from footprints, "
           ">= 4 from walkways, >= 18 from hoodoos (H15's own dune is a per-hole prop).")


def far_and_sky():
    for p in W["backdrop"]["pieces"]:
        k = p["kind"]
        if k in ("distant_mesa", "butte_spire", "far_arch", "far_butte"):
            piece, ref = S.CARD_REF[k]
            sx, sy, sz = p["size"]
            w = max(sx, sz) if k in ("butte_spire", "far_butte") else sx
            yaw = yaw_facing(-p["pos"][0], -p["pos"][2])
            add(piece, p["pos"], yaw, scale=[w / ref[0], sy / ref[1], w / ref[0]], src=p["id"],
                note="alpha-cut card facing the canyon centre; CastShadow off")
    assume("far cards: every distant_mesa / butte_spire / far_arch / far_butte is an alpha-cut bent card (<= 12 tris) yawed to "
           "face the canyon centre (world.json yaw ignored for buttes, whose local -Z didn't face the canyon); scale = "
           "[width/ref, height/ref, width/ref] (width = max(x, z) for buttes and the twin domes).")
    sun = PIECES["sun_disc"]
    add("sun_disc", sun["pos"], yaw_facing(-sun["pos"][0], -sun["pos"][2]), src=sun["id"], note="Neon card, CastShadow off")
    rnd = random.Random(9)
    for i in range(8):
        b = [205, 225, 245, 280, 300, 320, 160, 30][i] + rnd.uniform(-6, 6)
        r = rnd.uniform(1800, 2400)
        x, z = r * math.sin(math.radians(b)), -r * math.cos(math.radians(b))
        y = rnd.uniform(320, 620)
        add("cloud_streak", (x, y, z), yaw_facing(-x, -z), scale=[rnd.uniform(0.8, 1.3), rnd.uniform(0.7, 1.1), 1],
            src="cloud_streaks", note="pink-orange streak card")
    assume("cloud streaks: 8 cards (ref 700 x 70) at r 1800-2400, y 320-620, 6 of them in the western half around the sunset.")
    for i in range(6):
        b = i * 60 + 25 + rnd.uniform(-12, 12)
        r = rnd.uniform(520, 880)
        x, z = r * math.sin(math.radians(b)), -r * math.cos(math.radians(b))
        add(f"balloon_{'abc'[i % 3]}", (x, rnd.uniform(260, 420), z), rnd.uniform(0, 360), src="hot_air_balloons",
            note="start point of a slow drift loop (animate in Studio)")
    assume("hot-air balloons: 3 colourways x 2, start points every ~60 deg at r 520-880, y 260-420 (world.json gives only the "
           "loop ranges); the drift animation is for the build.")


def main():
    heroes()
    lifts()
    bridges()
    walkway_kit()
    clusters()
    cliffs()
    scatter()
    dunes()
    far_and_sky()
    counts = {}
    for e in INST:
        counts[e["piece"]] = counts.get(e["piece"], 0) + 1
    out = dict(
        units="Roblox world studs, +Y up, +X east, -Z north (world/world.json axes)",
        placement=("model:PivotTo(CFrame.new(pos) * CFrame.Angles(0, math.rad(yaw), 0)); pivot = piece base centre (see "
                   "manifest origin). `scale` = per-axis resize factors (local X, Y, Z) applied to every MeshPart Size and "
                   "its offset from the pivot."),
        source="world/world.json v" + W["version"] + " + generator rules in models/_src/sc_layout.py",
        instances=INST, clusters=CLUSTERS, counts=counts, assumptions=ASSUME)
    from pass2_rules import apply
    apply(out)
    json.dump(out, open(os.path.join(MODELS, "layout.json"), "w"), indent=1)
    print(f"[layout] {len(INST)} instances, {len(CLUSTERS)} clusters")
    for k in sorted(counts):
        print(f"   {k:28s} {counts[k]}")
    for a in ASSUME:
        print(" -", a[:220])


if __name__ == "__main__":
    main()
