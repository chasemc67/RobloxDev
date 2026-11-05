"""Author Lantern Grove's continuous world -> world/world.json.

Everything placed here is in WORLD studs (Y up, +X east, -Z north). Holes are placed by a
{origin, yaw_deg} transform of their holes.json local frame (holes.json is read, never written).
Run:  python3 world/tools/build_world.py && python3 world/tools/validate.py
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worldlib as W  # noqa: E402

holes = W.load_holes()
HB = {h["number"]: h for h in holes["holes"]}

# ------------------------------------------------------------------ hole placements
# origin = world position of the hole's LOCAL origin (= its tee), yaw about +Y.
PLACE = {
    1: dict(origin=[190.0, 24.0, 170.0], yaw_deg=0.0),     # forest-edge meadow, plays north
    2: dict(origin=[215.0, 26.0, 128.0], yaw_deg=0.0),     # acorn knoll, plays north
    3: dict(origin=[150.0, 44.0, 40.0], yaw_deg=0.0),      # village lower tier, S-bend NE
    4: dict(origin=[185.0, 48.0, -12.0], yaw_deg=0.0),     # village upper tier, plays north
    5: dict(origin=[100.0, 38.0, -110.0], yaw_deg=90.0),   # upper valley, plays WEST across the stream
    6: dict(origin=[45.0, 30.0, -70.0], yaw_deg=180.0),    # mill terrace (west bank), plays south
    7: dict(origin=[40.0, 26.0, -28.0], yaw_deg=180.0),    # cascade terraces (west bank), plays south
    8: dict(origin=[-10.0, 36.0, -24.0], yaw_deg=180.0),   # root terrace east of the tree, plays south
}
TREE_TARGET = (-74.0, 6.0)     # wanted trunk centre; H9 origin is solved from it
H9_DOOR_DIR = (0.55, 0.83)     # wanted world direction from trunk centre to H9 tee (doorway side)
H9_Y = 40.0
WALK_CLEAR = 5.0               # walking room inside the trunk around H9's footprint
TRUNK_WALL = 7.0


def foot_local_pts(h):
    pts = []
    for f in h["felt"]:
        pts += W.rect_corners(f["center"][0], f["center"][2], f["size"][0], f["size"][1], f["yaw"])
    for w in h["walls"]:
        pts += W.rect_corners(w["center"][0], w["center"][2], w["size"][0], w["size"][2], w["yaw"])
    return pts


# solve H9 so its footprint's minimal enclosing circle centre lands on TREE_TARGET and its tee
# sits on the doorway side.
h9 = HB[9]
mcx, mcz, mr = W.min_enclosing_circle(foot_local_pts(h9))
# world dir from MEC centre to tee must equal H9_DOOR_DIR. local vector centre->tee = (-mcx, -mcz)
th_l = math.atan2(-mcz, -mcx)
th_w = math.atan2(H9_DOOR_DIR[1], H9_DOOR_DIR[0])
yaw9 = round(math.degrees(th_l - th_w), 1)
ox, oz = W.rot(mcx, mcz, yaw9)
PLACE[9] = dict(origin=[round(TREE_TARGET[0] - ox, 2), H9_Y, round(TREE_TARGET[1] - oz, 2)], yaw_deg=yaw9)


def P(n):
    return PLACE[n]


def wpt(n, local):
    return W.to_world(PLACE[n], local)


def ground(n):
    """Hole pad ground at its tee = tee felt top - felt thickness."""
    return PLACE[n]["origin"][1] - 0.4


def cup(n):
    return wpt(n, HB[n]["cup"]["position"])


def tee(n):
    return wpt(n, HB[n]["tee"]["position"])


def gcup(n):
    """Ground just off the green = cup felt top - felt thickness."""
    return cup(n)[1] - 0.4


def behind_tee(n, d=5.0):
    return wpt(n, [0, 0, d])


# ------------------------------------------------------------------ paths
MAX_RISE = 0.8
TREAD = 1.5
FLIGHT_MAX = 10
LANDING = 4.0


def expand(leg_pts, kinds):
    """leg_pts: [(x,y,z)...]; kinds: per leg 'on_hole'|'walk'|'stairs'|'bridge'."""
    segs = []
    for (a, b, k) in zip(leg_pts[:-1], leg_pts[1:], kinds):
        a = [round(v, 2) for v in a]
        b = [round(v, 2) for v in b]
        if k != "stairs":
            dy = b[1] - a[1]
            L = math.hypot(b[0] - a[0], b[2] - a[2])
            g = dy / L if L else 0
            typ = k if k in ("on_hole", "bridge") else ("ramp" if abs(g) > 0.01 else "walk")
            segs.append(dict(type=typ, start=a, end=b, grade=round(g, 4)))
            continue
        dy = b[1] - a[1]
        L = math.hypot(b[0] - a[0], b[2] - a[2])
        n = max(1, math.ceil(abs(dy) / MAX_RISE - 1e-9))
        nf = math.ceil(n / FLIGHT_MAX)
        need = n * TREAD + (nf - 1) * LANDING
        tread = TREAD if L >= need else (L - (nf - 1) * LANDING) / n
        extra = max(0.0, L - need) / 2
        ux, uz = (b[0] - a[0]) / L, (b[2] - a[2]) / L
        s = 0.0
        y = a[1]

        def at(sv, yv):
            return [round(a[0] + ux * sv, 2), round(yv, 3), round(a[2] + uz * sv, 2)]

        if extra > 0.05:
            segs.append(dict(type="landing", start=at(0, y), end=at(extra, y), grade=0.0))
            s = extra
        steps_left = n
        rise = dy / n
        for fi in range(nf):
            k_ = min(FLIGHT_MAX, steps_left)
            e = s + k_ * tread
            segs.append(dict(type="stairs", start=at(s, y), end=at(e, y + k_ * rise), steps=k_,
                             rise=round(rise, 3), tread=round(tread, 3)))
            y += k_ * rise
            s = e
            steps_left -= k_
            if steps_left:
                segs.append(dict(type="landing", start=at(s, y), end=at(s + LANDING, y), grade=0.0))
                s += LANDING
        if L - s > 0.05:
            segs.append(dict(type="landing", start=at(s, y), end=at(L, y), grade=0.0))
    return segs


def mkpath(pid, frm, to, pts, kinds, width=6.0, name="", note=""):
    segs = expand(pts, kinds)
    L3 = sum(math.dist(s["start"], s["end"]) for s in segs)
    return dict(id=pid, name=name, from_hole=frm, to_hole=to, width=width, segments=segs,
                length=round(L3, 1), note=note)


paths = []
# spawn -> H1
SPAWN = [206.0, 23.6, 214.0]
b1 = behind_tee(1)
paths.append(mkpath("p_spawn_h1", None, 1,
                    [SPAWN, [198, 23.6, 196], [b1[0], ground(1), b1[2]], tee(1)],
                    ["walk", "walk", "on_hole"], width=8.0, name="Welcome Walk",
                    note="Spawn plaza -> under the lantern torii view to H1 tee"))
# H1 -> H2
c = cup(1)
b = behind_tee(2)
paths.append(mkpath("p_h1_h2", 1, 2,
                    [c, [181.0, gcup(1), 127.0], [199.0, gcup(1) + 0.3, 128.0], [205.0, gcup(1) + 0.9, 139.0], [b[0], ground(2), 139.0], [b[0], ground(2), b[2]], tee(2)],
                    ["on_hole", "walk", "ramp", "ramp", "walk", "on_hole"], name="Maple Lane"))
# H2 -> H3 (climb onto the village terrace: switchback stairs)
c = cup(2)
b = behind_tee(3)
paths.append(mkpath("p_h2_h3", 2, 3,
                    [c, [228.0, gcup(2), 92.0], [226.0, 24.4, 76.0], [196.0, 24.4, 72.0],
                     [160.0, 34.5, 72.0], [140.0, 34.5, 76.0], [138.0, ground(3), 52.0], [b[0], ground(3), b[2]], tee(3)],
                    ["on_hole", "ramp", "walk", "stairs", "walk", "stairs", "walk", "on_hole"],
                    name="Toadstool Stair", note="Two stair runs with a mid terrace up the village cliff (+20)"))
# H3 -> H4
c = cup(3)
b = behind_tee(4)
paths.append(mkpath("p_h3_h4", 3, 4,
                    [c, [168.0, gcup(3), 2.0], [176.0, gcup(3), 0.0], [b[0], ground(4), b[2] + 1], [b[0], ground(4), b[2]], tee(4)],
                    ["on_hole", "walk", "stairs", "walk", "on_hole"], name="Village Steps"))
# H4 -> H5 (via Lookout Rock, then down to the upper valley)
c = cup(4)
b = behind_tee(5)
paths.append(mkpath("p_h4_h5", 4, 5,
                    [c, [187.0, gcup(4), -61.0], [172.0, ground(4), -76.0], [158.0, ground(4), -82.0],
                     [134.0, ground(5), -100.0], [b[0] + 3, ground(5), b[2]], [b[0], ground(5), b[2]], tee(5)],
                    ["on_hole", "walk", "walk", "stairs", "walk", "walk", "on_hole"],
                    name="Lookout Descent", note="Passes Lookout Rock (village terrace NW corner) then 14 steps down"))
# H5 -> H6 (west bank, down beside Twin Falls)
c = cup(5)
b = behind_tee(6)
paths.append(mkpath("p_h5_h6", 5, 6,
                    [c, [56.0, gcup(5), -106.0], [54.0, gcup(5), -96.0], [54.0, ground(6), -78.0],
                     [b[0] + 4, ground(6), b[2]], [b[0], ground(6), b[2]], tee(6)],
                    ["on_hole", "walk", "stairs", "walk", "walk", "on_hole"],
                    name="Twin Falls Steps", note="Stairs down the Twin Falls cliff; plank step over the mill flume at z~-80"))
# H6 -> H7
c = cup(6)
b = behind_tee(7)
paths.append(mkpath("p_h6_h7", 6, 7,
                    [c, [19.0, gcup(6), -47.0], [19.0, gcup(6), -44.0], [22.0, ground(7), -36.0],
                     [b[0], ground(7), b[2]], tee(7)],
                    ["on_hole", "walk", "stairs", "walk", "on_hole"], name="Millrace Steps"))
# H7 -> H8 (climb to the root terrace)
c = cup(7)
b = behind_tee(8)
paths.append(mkpath("p_h7_h8", 7, 8,
                    [c, [27.0, gcup(7), 4.0], [22.0, gcup(7), -10.0], [6.0, ground(8), -34.0],
                     [b[0] + 2, ground(8), b[2]], [b[0], ground(8), b[2]], tee(8)],
                    ["on_hole", "walk", "stairs", "walk", "walk", "on_hole"],
                    name="Root Stair", note="Climbs between giant surface roots to the root terrace"))

# ------------------------------------------------------------------ hollow tree (from H9 placement)
pts9 = []
for r in W.footprint_rects(h9, PLACE[9]):
    pts9 += r
tcx, tcz, tr = W.min_enclosing_circle(pts9)
inner = tr + WALK_CLEAR
outer = inner + TRUNK_WALL
t9 = tee(9)
b9 = behind_tee(9, 4.0)
door_ang = math.degrees(math.atan2(b9[2] - tcz, b9[0] - tcx))
door_out = [tcx + (outer + 3) * math.cos(math.radians(door_ang)), tcz + (outer + 3) * math.sin(math.radians(door_ang))]
door_in = [tcx + (inner - 1.0) * math.cos(math.radians(door_ang)), tcz + (inner - 1.0) * math.sin(math.radians(door_ang))]
TREE_BASE = ground(9)
# H8 -> H9: out of H8 green, along the roots to the doorway, through it to H9 tee
c = cup(8)
paths.append(mkpath("p_h8_h9", 8, 9,
                    [c, [-24.5, gcup(8), c[2]], [door_out[0] + 16, gcup(8), door_out[1] + 2],
                     [door_out[0] + 7, TREE_BASE, door_out[1] + 4], [door_out[0], TREE_BASE, door_out[1]],
                     [door_in[0], TREE_BASE, door_in[1]], [b9[0], TREE_BASE, b9[2]], t9],
                    ["on_hole", "walk", "stairs", "walk", "walk", "walk", "on_hole"], width=7.0,
                    name="Heartwood Door", note="Root steps up to the arched doorway in the trunk; H9 is played inside"))

# ------------------------------------------------------------------ stream (north -> south)
# level = water surface. A short segment with a big level drop is a waterfall.
S = [
    (172, -392, 81.0, 6), (160, -330, 80.0, 7), (140, -268, 79.0, 8), (118, -214, 78.0, 9),
    (114, -205, 77.8, 9),                              # Grand Falls brink
    (112, -199, 39.0, 16),                             # plunge pool
    (100, -172, 38.6, 13), (86, -140, 38.2, 11), (80, -124, 38.0, 10),
    (79.5, -121, 37.0, 10),                            # H5 riffle (waterfall_bg anchor)
    (78.5, -105.5, 37.0, 10),                          # through H5's hazard (water level 37.0)
    (77.5, -90, 37.0, 9),                              # Twin Falls brink
    (76, -86, 29.8, 13),                               # Twin pool
    (70, -66, 29.7, 9), (64, -44, 29.5, 8),            # past the mill (flume take-off at the pool)
    (62, -36, 29.4, 7),                                # cascade step 1 brink
    (60, -32, 27.3, 7),                                # step 2
    (58, -26, 27.2, 7), (57, -22, 25.1, 7),            # step 3
    (56, -17, 25.0, 6), (54.5, -14, 23.0, 6),          # H7 pool
    (54.5, -4, 23.0, 6), (54, 8, 22.9, 7), (48, 30, 22.6, 8), (40, 52, 22.3, 8),
    (38, 57, 22.2, 8),                                 # Lantern Falls brink
    (36, 62, 9.2, 14),                                 # plunge pool
    (30, 80, 8.6, 10), (24, 96, 8.0, 12),              # into the lake
]
stream = dict(
    name="Lantern Brook",
    points=[dict(x=float(x), z=float(z), level=lv, width=float(w)) for (x, z, lv, w) in S],
    depth=3.0, bank_slope=0.8,
    note="Polyline north->south. level = water surface (studs), width = water width. Between vertices level/width are linear; "
         "terrain is carved to the channel profile (bed = level-depth, banks rise bank_slope per stud beyond the water edge). "
         "Fill Water from bed to `level` along the polyline.",
)
waterfalls = []
names = {4: "Grand Falls", 11: "Twin Falls", 15: "Cascade Step 1", 17: "Cascade Step 2", 19: "Cascade Step 3 (into H7 pool)",
         25: "Lantern Falls"}
for i in range(len(S) - 1):
    a, b_ = S[i], S[i + 1]
    if a[2] - b_[2] >= 1.5:
        waterfalls.append(dict(name=names.get(i, f"falls_{i}"), top=[a[0], a[2], a[1]], bottom=[b_[0], b_[2], b_[1]],
                               drop=round(a[2] - b_[2], 2), width=float(min(a[3], b_[3]))))
# decorative side springs from holes.json anchors
h6wf = wpt(6, [24, 0.25, -24])
waterfalls.append(dict(name="Mill Spring (H6 decor)", top=[h6wf[0] - 6, h6wf[1] + 11, h6wf[2]], bottom=[h6wf[0], h6wf[1], h6wf[2]],
                       drop=11.0, width=4.0, note="Rock outcrop spring west of H6 green (holes.json anchor `waterfall`); runoff rill to the stream"))
lakes = [dict(name="Lantern Mere", center=[14.0, 146.0], radii=[82.0, 52.0], level=8.0, depth=4.0, beach_width=10.0, beach_slope=0.12, bank_slope=1.0,
              note="Ellipse. Fill Water up to level 8. Sandy beach ring.")]
mill_flume = dict(name="Mill flume", points=[[73.0, 29.8, -84.0], [52.0, 29.6, -81.0], [37.5, 29.4, -79.0], [37.5, 29.3, -74.5]],
                  width=2.0, water_level_end=29.2,
                  note="Timber trough at ground level from Twin pool (29.8) into the mill house and H6 mill-race hazard (29.2). No terrain carve; plank step where p_h5_h6 crosses it.")

# ------------------------------------------------------------------ terrain regions
def poly(*pts):
    return dict(type="polygon", points=[list(map(float, p)) for p in pts])


TREE_PLATEAU_R = outer + 26
# highland cliff edge: wobbly line west->east with the Grand Falls notch at x~114
HIGHLAND_EDGE = [[-500.0, -500.0], [500.0, -500.0]]
for xe in range(500, -501, -20):
    ze = -226 + 9 * math.sin(xe / 37.0) + 6 * math.sin(xe / 13.0 + 1.0) + 12 * math.sin(xe / 140.0)
    if 70 <= xe <= 160:
        ze = -212 + 0.004 * (xe - 114) ** 2   # notch around the falls
    HIGHLAND_EDGE.append([float(xe), round(ze, 1)])
regions = [
    dict(id="highlands", op="set", height=84.0, falloff=12.0, edge="cliff",
         shape=dict(type="polygon", points=HIGHLAND_EDGE),
         material="rock face on the edge, grass/leafy on top"),
    dict(id="upper_valley", op="set", height=38.0, falloff=8.0, edge="cliff",
         shape=poly((40, -200), (150, -200), (165, -150), (140, -112), (120, -92), (80, -91), (40, -96), (25, -140)),
         material="grass; rocky lip at Twin Falls"),
    dict(id="mid_valley", op="set", height=27.0, falloff=8.0, edge="cliff",
         shape=poly((10, -90), (110, -86), (110, -20), (95, 30), (72, 54), (20, 54), (8, 10), (0, -40)),
         material="grass/leafy; cliff above Lantern Falls"),
    dict(id="mill_terrace", op="set", height=29.6, falloff=7.0, edge="soft",
         shape=poly((18, -78), (52, -80), (55, -40), (18, -40)), material="grass"),
    dict(id="south_lowland", op="set", height=11.0, falloff=40.0, edge="soft",
         shape=poly((-150, 70), (130, 70), (150, 330), (-170, 340)), material="grass + sand near the mere"),
    dict(id="east_meadow", op="set", height=23.6, falloff=40.0, edge="soft",
         shape=poly((150, 75), (300, 75), (320, 300), (165, 300), (140, 200)), material="grass (sunny forest edge)"),
    dict(id="acorn_knoll", op="set", height=25.6, falloff=18.0, edge="soft",
         shape=poly((203, 88), (228, 88), (228, 136), (203, 136)), material="grass"),
    dict(id="village_lower", op="set", height=43.6, falloff=8.0, edge="cliff",
         shape=poly((135, 58), (138, -4), (172, -6), (198, 6), (212, 40), (205, 62)), material="leafy ground; rock cliff faces"),
    dict(id="village_upper", op="set", height=47.6, falloff=6.0, edge="cliff",
         shape=poly((158, -4), (170, -66), (200, -72), (215, -40), (210, -2)), material="leafy ground; rock cliff faces"),
    dict(id="lookout_rock", op="hill", center=[160.0, -78.0], radius=12.0, peak=3.0, material="rock",
         note="Rocky knob at the village's NW corner; Lookout Rock viewing deck sits on the path beside it"),
    dict(id="root_terrace", op="set", height=35.6, falloff=8.0, edge="cliff",
         shape=poly((-28, -40), (18, -42), (20, 46), (-28, 48)), material="leafy ground + roots"),
    dict(id="tree_plateau", op="set", height=round(TREE_BASE, 2), falloff=14.0, edge="soft",
         shape=dict(type="circle", center=[round(tcx, 2), round(tcz, 2)], radius=round(TREE_PLATEAU_R, 1)),
         material="leafy ground, giant roots"),
    # organic forested hills instead of flat slabs (west behind the tree, east behind the village, valley knolls)
    dict(id="west_hills_1", op="hill", center=[-250.0, -150.0], radii=[120.0, 110.0], peak=34.0, material="forest"),
    dict(id="west_hills_2", op="hill", center=[-270.0, 10.0], radii=[110.0, 130.0], peak=40.0, material="forest"),
    dict(id="west_hills_3", op="hill", center=[-240.0, 170.0], radii=[120.0, 100.0], peak=30.0, material="forest"),
    dict(id="west_hills_4", op="hill", center=[-180.0, 290.0], radii=[130.0, 90.0], peak=24.0, material="forest"),
    dict(id="nw_knolls", op="hill", center=[-110.0, -150.0], radii=[60.0, 45.0], peak=12.0, material="forest"),
    dict(id="fern_knoll", op="hill", center=[-60.0, -120.0], radii=[35.0, 30.0], peak=7.0, material="forest"),
    dict(id="east_hills_1", op="hill", center=[320.0, -170.0], radii=[110.0, 90.0], peak=40.0, material="forest"),
    dict(id="east_hills_2", op="hill", center=[330.0, -40.0], radii=[100.0, 110.0], peak=36.0, material="forest"),
    dict(id="east_hills_3", op="hill", center=[350.0, 90.0], radii=[90.0, 80.0], peak=24.0, material="forest"),
    dict(id="ne_shoulder", op="hill", center=[230.0, -150.0], radii=[70.0, 60.0], peak=22.0, material="forest"),
    dict(id="south_knoll_w", op="hill", center=[-90.0, 250.0], radii=[60.0, 50.0], peak=10.0, material="grass"),
    dict(id="south_knoll_e", op="hill", center=[130.0, 300.0], radii=[70.0, 50.0], peak=12.0, material="grass"),
    dict(id="se_meadow_rise", op="hill", center=[290.0, 230.0], radii=[90.0, 80.0], peak=16.0, material="grass"),
    dict(id="highland_crags_w", op="hill", center=[-60.0, -300.0], radii=[90.0, 60.0], peak=20.0, material="rock/forest"),
    dict(id="highland_crags_e", op="hill", center=[260.0, -300.0], radii=[100.0, 70.0], peak=26.0, material="rock/forest"),
    dict(id="highland_crags_m", op="hill", center=[40.0, -340.0], radii=[60.0, 50.0], peak=14.0, material="forest"),
    dict(id="falls_buttress_w", op="hill", center=[92.0, -214.0], radius=16.0, peak=6.0, material="rock",
         note="Rock shoulders framing Grand Falls"),
    dict(id="falls_buttress_e", op="hill", center=[138.0, -214.0], radius=16.0, peak=6.0, material="rock"),
]

terrain = dict(
    method=("Deterministic heightfield h(x,z), evaluated in this order (see tools/worldlib.py height_at): "
            "(1) base: h = base.height + sum(amp*sin(2*pi*x/wx+px)*sin(2*pi*z/wz+pz)). "
            "(2) regions in list order. op 'set': w = 1-smoothstep(d/falloff) with d = distance outside the shape (0 inside); h += (height-h)*w. "
            "op 'hill': h += peak*cos^2(pi/2*q) for q = elliptical radius/radii < 1. "
            "(3) rim (then detail_noise, same formula as noise): q = superellipse radius ((|x-cx|/hx)^p+(|z-cz|/hz)^p)^(1/p); h += height*(1+variation*sin(lobes*atan2(z-cz,x-cx)+phase))*smoothstep((q-start)/(full-start)). "
            "(4) pads (one per hole, rules in terrain.pads). "
            "(5) paths: within width/2+1 of a path centreline (non on_hole/bridge segments) h = path profile (stairs: profile - stair_bed_drop), "
            "blended to the previous h over `shoulder` studs. "
            "(5b) felt clamp: under every non-bridge felt piece h = min(h, felt surface - felt_thickness). "
            "(6) water: h = min(h, stream/lake carve profile; lake: level+beach_slope*d within beach_width of the shore, then +bank_slope per stud). smoothstep(t)=t^2(3-2t) on t clamped to [0,1]."),
    base=dict(height=20.0, noise=[dict(amp=1.2, wx=97.0, wz=131.0, phase=[0.3, 1.1]),
                                  dict(amp=0.7, wx=41.0, wz=53.0, phase=[2.0, 0.4]),
                                  dict(amp=2.0, wx=310.0, wz=270.0, phase=[1.0, 2.2])],
              detail_noise=[dict(amp=0.3, wx=37.0, wz=-53.0, phase=[0.5, 1.7]), dict(amp=0.8, wx=113.0, wz=89.0, phase=[2.4, 0.2])],
              note="noise = before regions; detail_noise = added after regions+rim (before pads/paths/water), same formula"),
    regions=regions,
    rim=dict(center=[40.0, 0.0], half_size=[400.0, 400.0], exponent=4.0, start=0.78, full=0.98, height=46.0,
             variation=0.35, lobes=5.0, phase=0.7, note="Forested rim hills hide the terrain edge"),
    path_grading=dict(shoulder=5.0, stair_bed_drop=0.6),
    pads=dict(rule=("For each hole: felt pieces (non-overlay) transformed by its placement. Under any non-bridge felt piece the "
                    "terrain = min over covering pieces of (felt surface - felt_thickness). Elsewhere inside footprint (felt+walls) "
                    "+ margin: h = max(lowest floor, max_i(floor_i - cone_slope*dist_to_piece_i)), blended to the previous terrain over "
                    "`falloff` studs beyond the margin. Water/pit hazard rectangles are cut to (hazard surface - hazard_depth)."),
              felt_thickness=0.4, margin=3.0, falloff=10.0, cone_slope=0.25, hazard_depth={"water": 2.0, "pit": 1.5}),
)

# ------------------------------------------------------------------ holes block
holes_out = []
SURROUND = {
    1: "Sunny forest-edge meadow (y~24) south-east; red maples, lantern torii; Lantern Mere glitters to the west, the giant tree on the far side",
    2: "Acorn Knoll, a low grassy rise (y~26) beside the meadow; village cliffs rise to the north",
    3: "Mushroom Village lower tier (y~44) on a rock-faced terrace above the meadow; mushroom houses around the S-bend",
    4: "Mushroom Village upper tier (y~48), highest hole; looks west over the valley to Grand Falls and the tree",
    5: "Upper valley (y~38) where Lantern Brook leaves the Grand Falls plunge pool; Grand Falls 90 studs north",
    6: "Mill terrace (y~30) on the west bank below Twin Falls; mill flume from the Twin pool",
    7: "Cascade terraces (y~26->23.6) on the west bank beside the 3-step cascade and its pool",
    8: "Root terrace (y~36) among giant surface roots right at the trunk of the hollow tree",
    9: "INSIDE the hollow tree trunk (floor y~39.6), lantern-lit hollow opening to the crown",
}
for n in range(1, 10):
    h = HB[n]
    pl = PLACE[n]
    rects = W.footprint_rects(h, pl)
    xs = [c[0] for r in rects for c in r]
    zs = [c[1] for r in rects for c in r]
    fy = []
    for f in W.felt_world(h, pl):
        cy = W.felt_surface(f, __import__("numpy").array([c[0] for c in f["corners"]]), __import__("numpy").array([c[1] for c in f["corners"]]))
        fy += list(cy)
    holes_out.append(dict(
        number=n, id=h["id"], name=h["name"], par=h["par"], zone=h["zone"],
        placement=dict(origin=[round(v, 3) for v in pl["origin"]], yaw_deg=pl["yaw_deg"]),
        tee_world=[round(v, 2) for v in tee(n)], cup_world=[round(v, 2) for v in cup(n)],
        felt_y_range=[round(min(fy), 2), round(max(fy), 2)],
        pad_ground_y=round(min(fy) - 0.4, 2),
        footprint_bbox=dict(x=[round(min(xs), 1), round(max(xs), 1)], z=[round(min(zs), 1), round(max(zs), 1)]),
        surroundings=SURROUND[n],
    ))

# ------------------------------------------------------------------ hollow tree
tree = dict(
    name="Grandmother Lantern Tree (giant hollow golden tree)",
    center=[round(tcx, 2), round(TREE_BASE, 2), round(tcz, 2)],
    base_y=round(TREE_BASE, 2),
    trunk_outer_radius=round(outer, 2), trunk_inner_radius=round(inner, 2), wall_thickness=TRUNK_WALL,
    h9_footprint_circle=dict(center=[round(tcx, 2), round(tcz, 2)], radius=round(tr, 2),
                             note="Minimal enclosing circle of H9's transformed felt+walls; interior radius = this + walk clearance"),
    trunk_height=100.0, hollow_height=78.0,
    oculus=dict(y=round(TREE_BASE + 78.0, 1), radius=14.0, note="Opening at the top of the hollow above the heart; light shaft"),
    crown=dict(center_y=round(TREE_BASE + 100.0 + 34.0, 1), radius_xz=88.0, height=78.0, color="#F2B632/#E8862E"),
    root_flare_radius=round(outer + 20, 1),
    doorway=dict(angle_deg=round(door_ang, 1), width=14.0, height=20.0, outer_point=[round(door_out[0], 2), round(TREE_BASE, 2), round(door_out[1], 2)],
                 note="Angle measured atan2(dz, dx) in the map (x east, z south) from the trunk centre"),
    total_height=round(100.0 + 34.0 + 39.0, 1),
    note=("World-scale shell (NEW model; the existing 34x60x34 hollow_tree.fbx is too small to contain H9). "
          "H9 is played inside on the interior floor; H8 runs along its eastern roots."),
)

# ------------------------------------------------------------------ POIs
lk = lakes[0]
pois = [
    dict(id="spawn_plaza", name="Welcome Plaza", pos=[SPAWN[0], SPAWN[1], SPAWN[2]], radius=12.0, kind="plaza",
         note="Spawn. Course board, lantern arch facing north-west toward H1 and the far giant tree"),
    dict(id="lantern_torii", name="Lantern Torii (H1)", pos=wpt(1, [0, 0.25, -21]), kind="landmark"),
    dict(id="mere_view", name="Mere View bench", pos=[176.0, 23.6, 118.0], kind="viewpoint",
         note="Bench on Maple Lane looking west over Lantern Mere to the tree"),
    dict(id="village_square", name="Toadstool Square", pos=[192.0, 43.6, 16.0], radius=8.0, kind="plaza",
         note="Village green with a well and lantern strings between mushroom houses"),
    dict(id="lookout_rock", name="Lookout Rock", pos=[166.0, 47.6, -80.0], radius=6.0, kind="viewpoint",
         note="Deck at the village's NW corner, 10 studs above the upper valley: H5, Twin Falls, H6, H7, Grand Falls and the tree in one view"),
    dict(id="grand_falls", name="Grand Falls", pos=[113.0, 39.0, -202.0], kind="waterfall"),
    dict(id="twin_falls", name="Twin Falls", pos=[76.5, 33.0, -88.0], kind="waterfall"),
    dict(id="mill", name="Old Water Mill", pos=wpt(6, [7.5, 0, 0]), kind="landmark"),
    dict(id="cascade", name="Three-Step Cascade", pos=[58.0, 26.0, -26.0], kind="waterfall"),
    dict(id="lantern_falls", name="Lantern Falls", pos=[37.0, 15.0, 59.0], kind="waterfall"),
    dict(id="mere_dock", name="Lantern Boat Dock", pos=[80.0, 8.5, 128.0], kind="decor",
         note="Little dock with paper-lantern boats drifting on the mere (background only)"),
    dict(id="highland_tower", name="Old Lantern Tower", pos=[60.0, 84.0, -262.0], kind="background",
         note="Ruined stone lantern tower on the highlands, silhouette beside Grand Falls"),
    dict(id="root_gate", name="Root Stair arch", pos=[14.0, 30.0, -22.0], kind="landmark",
         note="Two giant surface roots arch over the Root Stair"),
    dict(id="tree_door", name="Heartwood Door", pos=tree["doorway"]["outer_point"], kind="landmark"),
    dict(id="firefly_glade", name="Firefly Glade", pos=[-22.0, 35.6, 72.0], radius=14.0, kind="decor",
         note="Mossy hollow south of the tree with glow mushrooms and fireflies"),
]
for p in pois:
    p["pos"] = [round(v, 2) for v in p["pos"]]

# ------------------------------------------------------------------ lanterns along paths
lanterns = []
SP = 10.0
for p in paths:
    side = 1
    carry = SP / 2
    for s in p["segments"]:
        if s["type"] == "on_hole":
            continue
        a, b = s["start"], s["end"]
        L = math.hypot(b[0] - a[0], b[2] - a[2])
        if L < 1e-6:
            continue
        ux, uz = (b[0] - a[0]) / L, (b[2] - a[2]) / L
        nx, nz = -uz, ux
        t = carry
        while t <= L:
            y = a[1] + (b[1] - a[1]) * t / L
            off = p["width"] / 2 + 1.0
            lanterns.append(dict(path=p["id"], pos=[round(a[0] + ux * t + nx * off * side, 2), round(y, 2),
                                                     round(a[2] + uz * t + nz * off * side, 2)],
                                 type="post" if s["type"] in ("walk", "ramp", "landing") else "stair_newel"))
            side = -side
            t += SP
        carry = t - L

# ------------------------------------------------------------------ backdrop rings
CX, CZ = 40.0, 0.0
backdrop = dict(
    center=[CX, CZ],
    rings=[
        dict(id="tree_line", name="Autumn forest tree line (on terrain)", radius=[300, 390], kind="tree clusters on rim hills",
             cluster_size=[40, 45, 40], count=56, colors=["#D2452A", "#E8862E", "#F2B632", "#7A9A3A"],
             note="Low-poly autumn tree clumps standing on the rim hills; continuous wall of canopy 35-55 studs tall"),
        dict(id="far_hills", name="Far forested hills", radius=[520, 650], kind="impostor hill shells (no terrain)",
             base_y=10, height=[70, 130], count=18,
             note="Rolling hills covered in autumn forest, slightly hazed; sit just outside the terrain edge"),
        dict(id="mountains", name="Distant mountains", radius=[1100, 1600], kind="silhouette mountain meshes", base_y=0,
             height=[220, 460], count=12, color="#7C7FA8 -> #A9A3C7 (atmospheric)",
             note="Tallest behind the highlands (north) and behind the tree (west, sunset side); lowest to the south-east"),
        dict(id="sky", name="Sky / horizon", radius=[1800, 2400], kind="skybox + cloud cards + sky lanterns",
             items=[dict(name="sun", azimuth_deg=242, elevation_deg=14,
                         note="Golden-hour sun from the WSW (ClockTime 16.8) so the giant tree is backlit when seen from H1-H4"),
                    dict(name="moon (night)", azimuth_deg=258, elevation_deg=22, note="Rises behind the hollow tree as seen from H1"),
                    dict(name="cloud banks", count=7, y=[500, 850], size=[600, 120]),
                    dict(name="sky lanterns", count=24, y=[150, 280], note="Drifting paper lanterns around the tree crown, slow upward drift")]),
    ],
)
pieces = []
# mountains
import random  # deterministic
rnd = random.Random(7)
for i in range(12):
    ang = i * 30 + rnd.uniform(-8, 8)
    r = rnd.uniform(1150, 1550)
    a = math.radians(ang)
    # map angle: atan2(z,x); north = -z -> ang 270
    north_w = max(0.0, -math.sin(a))
    west_w = max(0.0, -math.cos(a))
    hgt = 220 + 200 * max(north_w, 0.8 * west_w) + rnd.uniform(-20, 30)
    pieces.append(dict(id=f"mountain_{i+1:02d}", kind="distant_mountain", pos=[round(CX + r * math.cos(a)), 0, round(CZ + r * math.sin(a))],
                       size=[round(rnd.uniform(420, 700)), round(hgt), round(rnd.uniform(250, 400))],
                       yaw_deg=round(-ang + 90, 1)))
for i in range(18):
    ang = i * 20 + rnd.uniform(-5, 5)
    r = rnd.uniform(530, 640)
    a = math.radians(ang)
    pieces.append(dict(id=f"far_hill_{i+1:02d}", kind="far_forest_hill", pos=[round(CX + r * math.cos(a)), 10, round(CZ + r * math.sin(a))],
                       size=[round(rnd.uniform(240, 320)), round(rnd.uniform(70, 130)), 160], yaw_deg=round(-ang + 90, 1)))
backdrop["pieces"] = pieces

# ------------------------------------------------------------------ world
b = dict(x=[-360.0, 440.0], z=[-400.0, 400.0])
world = dict(
    name="Lantern Grove - continuous world",
    version="1.0",
    units="studs (1 stud = 0.3 m), +Y up, map view +X east/right, -Z north/up. Same axes as holes.json.",
    bounds=dict(x=b["x"], z=b["z"], size=[b["x"][1] - b["x"][0], b["z"][1] - b["z"][0]],
                y_range=[0.0, 140.0], note="Terrain extent. Backdrop meshes sit outside it."),
    placement_convention=dict(
        apply=("For every holes.json element of hole N: rotate its LOCAL x/z about +Y by placement.yaw_deg, then translate by "
               "placement.origin. x' = lx*cos(yaw) + lz*sin(yaw) + origin.x ; z' = -lx*sin(yaw) + lz*cos(yaw) + origin.z ; "
               "y' = ly + origin.y. Piece yaw_world = piece.yaw + yaw_deg. Positive yaw = counter-clockwise in the map view "
               "(e.g. yaw 90 turns local -Z (play direction) to world -X/west; yaw 180 to world +Z/south)."),
        roblox="holeRoot = CFrame.new(origin) * CFrame.Angles(0, math.rad(yaw_deg), 0); partCFrame = holeRoot * localCFrame. "
               "Moving-part pivots/axes and teleport points transform the same way (axes: rotate only).",
        supersedes="holes.json world_offset/world_yaw (the old flat layout) - ignore those, use world.json placements.",
    ),
    spawn=dict(pos=SPAWN, facing_deg=None, look_at=[round(v, 2) for v in tee(1)], note="SpawnLocation in Welcome Plaza, looking at H1 tee; giant tree visible beyond"),
    holes=holes_out,
    terrain=terrain,
    stream=stream,
    mill_flume=mill_flume,
    lakes=lakes,
    waterfalls=waterfalls,
    paths=paths,
    path_rules=dict(max_ramp_grade=0.10, max_step_rise=1.0, design_step_rise=MAX_RISE, tread=TREAD, max_steps_per_flight=FLIGHT_MAX,
                    landing_length=LANDING, min_width=5.0,
                    segment_types="on_hole (walk across the hole's own area from cup/to tee), walk (<1% grade), ramp (<=10%), stairs (flight: steps x rise, tread), landing (flat), bridge"),
    hollow_tree=tree,
    pois=pois,
    lanterns=dict(spacing=SP, offset="path width/2 + 1, alternating sides", count=len(lanterns), points=lanterns),
    backdrop=backdrop,
    heightmap=dict(file="heightmap.png", stud_per_px=1.0, y_min=0.0, y_max=140.0, bit_depth=16,
                   mapping="pixel (i=col, j=row) centre -> x = bounds.x[0] + (i+0.5)*stud_per_px, z = bounds.z[0] + (j+0.5)*stud_per_px "
                           "(row 0 = north edge, col 0 = west edge); y = y_min + gray/65535*(y_max-y_min) (16-bit) or gray/255 (8-bit preview)"),
    materials=dict(
        file="materials-map.png",
        legend=[
            dict(key="grass", roblox="Grass", rgb=[106, 127, 63], rule="default ground"),
            dict(key="leafy", roblox="LeafyGrass", rgb=[115, 132, 74], rule="inside material_zones (forest floor, village, roots)"),
            dict(key="rock", roblox="Rock", rgb=[102, 108, 111], rule="slope > 40 deg (cliffs, falls, terrace walls)"),
            dict(key="path", roblox="Ground", rgb=[102, 92, 59], rule="walkway corridors (width/2) and plazas"),
            dict(key="water", roblox="Water", rgb=[12, 84, 92], rule="terrain below a water surface (stream, mere, hazards): paint bed Mud, fill Water to level"),
            dict(key="sand", roblox="Sand", rgb=[143, 126, 95], rule="dry ground within 3 studs of the stream / 10 of the mere and < 1.5 above water"),
        ],
        note="RGB values are Roblox's default terrain material colours (the colormap convention of the Terrain Editor import). "
             "materials-legend.png shows the legend.",
        material_zones=[
            dict(name="village terraces", shape=dict(type="polygon", points=[[130, 64], [134, -10], [160, -76], [205, -80], [222, -40], [216, 66]])),
            dict(name="root terrace + tree plateau", shape=dict(type="circle", center=[round(tcx, 1), round(tcz, 1)], radius=round(TREE_PLATEAU_R + 12, 1))),
            dict(name="root terrace", shape=dict(type="polygon", points=[[-30, -44], [22, -44], [22, 50], [-30, 50]])),
            dict(name="west forest", shape=dict(type="polygon", points=[[-500, -240], [-170, -240], [-160, 330], [-500, 500]])),
            dict(name="east ridge forest", shape=dict(type="polygon", points=[[245, -240], [500, -240], [500, 60], [240, 50]])),
            dict(name="highland forest", shape=dict(type="polygon", points=[[-500, -500], [500, -500], [500, -250], [-500, -250]])),
            dict(name="rim forest", rim_q_min=0.8),
        ]),
)
# ------------------------------------------------------------------ scenery pieces (need terrain heights)
import numpy as np  # noqa: E402


def hgt(x, z):
    return round(float(W.height_at(world, holes, np.array([float(x)]), np.array([float(z)]))[0]), 1)


sc = []
rnd2 = random.Random(11)
for i in range(56):
    ang = i * (360 / 56) + rnd2.uniform(-2, 2)
    a = math.radians(ang)
    r = 0.88  # superellipse radius fraction on the rim
    # point on superellipse q=r
    cx_, cz_ = world["terrain"]["rim"]["center"]
    hx, hz = world["terrain"]["rim"]["half_size"]
    c_, s_ = math.cos(a), math.sin(a)
    k = (abs(c_) ** 4 + abs(s_) ** 4) ** -0.25
    x = cx_ + hx * r * k * c_
    z = cz_ + hz * r * k * s_
    x = min(max(x, b["x"][0] + 8), b["x"][1] - 8)
    z = min(max(z, b["z"][0] + 8), b["z"][1] - 8)
    sc.append(dict(id=f"treeline_{i+1:02d}", kind="tree_line_cluster", pos=[round(x, 1), hgt(x, z), round(z, 1)],
                   size=[40, rnd2.choice([35, 40, 45, 55]), 40], yaw_deg=round(rnd2.uniform(0, 360)),
                   colors=rnd2.choice(["red+orange", "gold+orange", "red+gold", "gold+green"])))
extra = [
    ("hollow_tree_world_shell", "hero_tree", [tcx, TREE_BASE, tcz], [2 * outer, 100, 2 * outer],
     "Trunk shell: outer radius %.1f, inner %.1f, hollow to y+78 with a 14-radius oculus, doorway 14x20 at angle %.0f deg; roots flare to r %.0f" % (outer, inner, door_ang, outer + 20)),
    ("hollow_tree_crown", "hero_tree", [tcx, TREE_BASE + 100, tcz], [176, 78, 176], "Golden/orange canopy, base at y+100 above trunk base; lumpy, 5-7 big leaf masses; sky lanterns drift around it"),
    ("grand_falls_curtain", "waterfall", [113, 39.0, -202], [12, 39, 6], "Waterfall mesh/beam curtain 77.8 -> 39, mist particles in the plunge pool"),
    ("twin_falls_curtain", "waterfall", [76.8, 29.8, -88], [10, 7.5, 4], "Two-strand falls 37 -> 29.8"),
    ("lantern_falls_curtain", "waterfall", [37, 9.2, 59.5], [9, 13, 4], "Falls 22.2 -> 9.2 into the mere inflow pool"),
    ("highland_cliff_kit", "rock", [40, 60, -222], [40, 30, 14], "Modular slate cliff faces (x10-12) dressing the 20-50 stud highland scarp along z ~ -205..-240"),
    ("terrace_rock_faces", "rock", [150, 34, 60], [24, 12, 6], "Rock facing pieces for the village terrace walls, mill terrace, root terrace and tree mound (x20)"),
    ("old_lantern_tower", "background", [60, 84, -262], [12, 38, 12], "Ruined stone tower with a big amber lantern at top; silhouette on the highlands"),
    ("sister_tree_nw", "background", [-190, 0, -110], [60, 90, 60], "Large golden tree (smaller cousin of the hero tree) in the NW forest"),
    ("sister_tree_sw", "background", [-150, 0, 230], [55, 80, 55], "Large red maple giant on the SW hills"),
    ("sister_tree_ne", "background", [260, 0, -150], [50, 75, 50], "Golden oak giant on the NE shoulder above the village"),
    ("hill_mushroom_houses", "background", [290, 0, -40], [30, 25, 30], "Cluster of 3-4 mushroom houses on the east hills (village continues into the distance), lit windows"),
    ("mere_lantern_boats", "decor", [14, 8, 146], [6, 3, 3], "8 tiny paper-lantern boats drifting on Lantern Mere (slow tween)"),
    ("mere_dock", "decor", [80, 8.5, 128], [14, 3, 5], "Plank dock with lanterns"),
    ("sky_lanterns", "sky", [tcx, 200, tcz], [1.5, 2, 1.5], "24 floating paper lanterns orbiting the crown, y 150-280"),
    ("cloud_banks", "sky", [CX, 650, CZ], [600, 120, 200], "7 soft golden cumulus cards at r 1800-2400"),
]
for (i_, k_, pos_, size_, note_) in extra:
    pos_ = [round(pos_[0], 1), pos_[1], round(pos_[2], 1)]
    if pos_[1] == 0:
        pos_[1] = hgt(pos_[0], pos_[2])
    sc.append(dict(id=i_, kind=k_, pos=pos_, size=[round(v, 1) for v in size_], note=note_))
world["backdrop"]["pieces"] = sc + world["backdrop"]["pieces"]
with open(W.WORLD_JSON, "w") as f:
    json.dump(world, f, indent=1)
print("wrote", W.WORLD_JSON)
print("H9 placement", PLACE[9], "tree centre", (round(tcx, 1), round(tcz, 1)), "inner", round(inner, 1), "outer", round(outer, 1))
for p in paths:
    print(p["id"], p["length"])
print("walk total (H1->H9):", round(sum(p["length"] for p in paths if p["from_hole"]), 1))
