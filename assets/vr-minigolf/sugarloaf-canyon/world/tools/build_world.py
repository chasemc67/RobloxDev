"""Author Sugarloaf Canyon's world -> world/world.json (adapted from lantern-grove/world/tools/build_world.py).

Everything here is in WORLD studs (Y up, +X east, -Z north, 1 stud = 0.3 m). Holes are `concept_footprint`s: a placement
{origin, yaw_deg} of the hole's local frame (tee at the origin, play toward local -Z) plus flat pad boxes (tiers) in that frame.
Hole-by-hole geometry (holes.json) comes later and must fit inside these footprints.

Run:  python3 world/tools/build_world.py && python3 world/tools/validate.py "note" && python3 world/tools/make_maps.py
"""
import json
import math
import os
import random
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import worldlib as W  # noqa: E402

# ------------------------------------------------------------------ elevations (pad / ground y)
FLOOR = 18.0      # canyon floor (town, river crossing)
TAFFY = 70.0      # Taffy Mesa (east, first mesa) and the West Ledge
BENCH = 116.0     # Reservoir Bench (north): dam, reservoir
HOODOO = 150.0    # Hoodoo Bench (north-west)
CROWN = 190.0     # Sugarloaf Crown (south-west, the top tier)
RES_LEVEL = 108.0

# ------------------------------------------------------------------ holes (concept footprints)
# W x L = footprint width (local x) x length (local -z, from the tee) ; the box runs from local z +6 (tee pad) to -L.
# tiers: [(id, z_from, z_to, dy)] split the box into flat pads at origin.y + dy. spans: local z ranges bridged over a gap.
HOLES = [
    # n, id, name, zone, par, origin, yaw, W, L, cup_local(x, z), tiers, spans, gimmick, landmark
    dict(n=1, id="h01_trailhead_gate", name="Trailhead Gate", zone="Sugarloaf Junction", par=2,
         origin=[60.0, FLOOR, 470.0], yaw=0.0, W=18, L=40, cup=(0, -32),
         gimmick="One clean bank shot: a striped boulder with a 45-degree bank face turns the ball onto an offset green",
         landmark="Candy-striped trailhead arch with a hanging lollipop sign"),
    dict(n=2, id="h02_mine_cart_junction", name="Mine-Cart Junction", zone="Sugarloaf Junction", par=3,
         origin=[100.0, FLOOR, 410.0], yaw=0.0, W=26, L=52, cup=(6, -44),
         gimmick="Pick a mine tunnel: three timbered tunnel mouths, one short and tight, one long and safe, one dead-end that spits the ball back",
         landmark="Mine-head with ore carts and a candy-striped headframe"),
    dict(n=3, id="h03_rangers_riverbend", name="Ranger's Riverbend", zone="Sugarloaf Junction", par=3,
         origin=[-95.0, FLOOR, 330.0], yaw=-90.0, W=26, L=70, cup=(0, -62), spans=[(-58, -26, "Sugarloaf River")],
         gimmick="River crossing: a rail-less log plank straight over the river (risky) or the railed ranger footbridge (safe); misses respawn at the bridge entry",
         landmark="Ranger station with a fire-lookout cupola on the west bank"),
    dict(n=4, id="h04_crystal_corridor", name="Crystal Corridor", zone="Rock Candy Narrows", par=3,
         origin=[200.0, FLOOR, 330.0], yaw=-90.0, W=20, L=42, cup=(0, -34),
         gimmick="Pinball crystals: static rock-candy crystal bumpers with flat faces at set angles bounce the ball down the slot",
         landmark="Giant pink rock-candy geode wall"),
    dict(n=5, id="h05_echo_slot", name="Echo Slot", zone="Rock Candy Narrows", par=3,
         origin=[280.0, 22.0, 326.0], yaw=0.0, W=24, L=58, cup=(0, -48),
         gimmick="Half-pipe: an S-bend U-channel with banked felt walls; ride the wall high to carry the bend",
         landmark="Smooth wave-carved slot walls in pink and cream bands"),
    dict(n=6, id="h06_flash_flood", name="Flash Flood", zone="Rock Candy Narrows", par=3,
         origin=[280.0, 26.0, 255.0], yaw=0.0, W=24, L=58, cup=(0, -50),
         gimmick="Timing gate: a wooden sluice gate slides across the slot, pauses closed, then opens (slide with dwell)",
         landmark="Old sluice gate and flood-warning bell tower"),
    dict(n=7, id="h07_rope_bridge_run", name="Rope Bridge Run", zone="Taffy Mesa", par=4,
         origin=[340.0, TAFFY, 150.0], yaw=0.0, W=30, L=72, cup=(0, -64), spans=[(-58, -26, "Taffy Gap")],
         gimmick="Long par 4 across Taffy Gap on two railed rope-bridge felt spans; a mid-mesa island in between; falls off the island respawn at the bridge entry",
         landmark="Taffy Gap with two sagging rope bridges"),
    dict(n=8, id="h08_gumdrop_gulch", name="Gumdrop Gulch", zone="Taffy Mesa", par=3,
         origin=[360.0, TAFFY, 55.0], yaw=0.0, W=26, L=60, cup=(0, -46),
         gimmick="Rolling dips: three gumdrop humps and hollows built from opposing planar slopes; pace the ball through",
         landmark="Giant gumdrop boulders in candy colours"),
    dict(n=9, id="h09_lollipop_windmill", name="Lollipop Windmill", zone="Taffy Mesa", par=3,
         origin=[330.0, TAFFY, -110.0], yaw=-90.0, W=26, L=54, cup=(0, -46),
         gimmick="Prospector's windpump: lollipop-swirl vanes turn on a horizontal axle across the lane (vertical rotor)",
         landmark="Windpump with lollipop vanes and a water tank"),
    dict(n=10, id="h10_sluice_chute", name="Sluice Chute", zone="Sugarloaf Dam", par=2,
         origin=[290.0, BENCH, -300.0], yaw=180.0, W=20, L=44, cup=(0, -38),
         tiers=[("upper", 6, -22, 0.0), ("lower", -22, -44, -3.6)],
         gimmick="One-way slope: a steep sluice chute drops 4 studs into a basin green; felt arrows and chevrons show it is one-way",
         landmark="Timber sluice flume with peppermint-striped gates"),
    dict(n=11, id="h11_floodgate_lock", name="Floodgate Lock", zone="Sugarloaf Dam", par=3,
         origin=[150.0, BENCH, -252.0], yaw=0.0, W=26, L=54, cup=(0, -50),
         tiers=[("lower", 6, -26, 0.0), ("upper", -26, -54, 4.0)],
         gimmick="Ball elevator: a canal-lock platform rises 4 studs and lowers again; roll on when it is down",
         landmark="Canal lock with brass winches and a lock-keeper's hut"),
    dict(n=12, id="h12_intake_tower", name="Intake Tower", zone="Sugarloaf Dam", par=4,
         origin=[-200.0, BENCH, -270.0], yaw=-90.0, W=34, L=66, cup=(0, -58),
         gimmick="Pipe teleport: sink the ball in the intake grate and it shoots out of an outflow pipe near the green, or play the long shoreline route",
         landmark="Domed intake tower standing in the reservoir"),
    dict(n=13, id="h13_hoodoo_maze", name="Hoodoo Maze", zone="Hoodoo Garden", par=3,
         origin=[-300.0, HOODOO, -290.0], yaw=180.0, W=30, L=56, cup=(0, -48),
         gimmick="Maze of hoodoo pillars (static bumpers): three corridors of different length and risk",
         landmark="Cluster of striped hoodoo spires with balanced gumdrop caps"),
    dict(n=14, id="h14_ore_bucket_swing", name="Ore Bucket Swing", zone="Hoodoo Garden", par=3,
         origin=[-300.0, HOODOO, -200.0], yaw=180.0, W=24, L=54, cup=(0, -46),
         gimmick="Pendulum: an ore bucket swings from a cableway trestle across the lane",
         landmark="Cableway trestle with a swinging ore bucket"),
    dict(n=15, id="h15_sugar_dune", name="Sugar Dune", zone="Hoodoo Garden", par=4,
         origin=[-300.0, HOODOO, -115.0], yaw=180.0, W=36, L=66, cup=(0, -58),
         gimmick="Side-slope reading: a long green tilted across the line (dune face) with a crest to a two-tier green",
         landmark="Powdered-sugar dune with sand-sled tracks"),
    dict(n=16, id="h16_sinkhole_drop", name="Sinkhole Drop", zone="Sugarloaf Crown", par=2,
         origin=[-300.0, CROWN, 112.0], yaw=180.0, W=20, L=44, cup=(0, -38),
         tiers=[("upper", 6, -22, 0.0), ("lower", -22, -44, -3.6)],
         gimmick="Drop between levels: putt into a sinkhole in the upper deck and fall into a funnel bowl green below",
         landmark="Crystal-lined sinkhole with a rope railing"),
    dict(n=17, id="h17_sundial", name="Sundial", zone="Sugarloaf Crown", par=3,
         origin=[-345.0, CROWN, 232.0], yaw=0.0, W=30, L=56, cup=(0, -48),
         gimmick="Sweeper: the sundial's gnomon-shadow arm sweeps slowly round a circular green (horizontal rotor)",
         landmark="Giant stone sundial with candy-coloured hour stones"),
    dict(n=18, id="h18_sunset_arch", name="Sunset Arch", zone="Sugarloaf Crown", par=4,
         origin=[-420.0, CROWN, 236.0], yaw=0.0, W=36, L=76, cup=(0, -68),
         gimmick="Finale: bank around a hoodoo, climb a ramp under the natural arch, then a geode-shortcut teleport or the rim route to a cliff-edge green",
         landmark="Sunset Arch, a natural candy-striped stone arch on the west rim"),
]
BY = {h["n"]: h for h in HOLES}
# Hole-by-hole geometry now exists (../holes.json, built by ../tools/build_holes.py): take each hole's real cup position (local x, z) and
# par from it, so the walkways start at the real cups. The concept pads stay the footprint every felt/rail must fit inside.
HOLES_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "holes.json")
HJ = {}
if os.path.exists(HOLES_JSON):
    for _h in json.load(open(HOLES_JSON))["holes"]:
        HJ[_h["number"]] = _h
        BY[_h["number"]]["cup"] = (round(_h["cup"]["position"][0], 2), round(_h["cup"]["position"][2], 2))
        BY[_h["number"]]["par"] = _h["par"]
BEHIND = 9.0   # walk-in point behind the tee (local +z), outside the footprint (box ends at +6)


def place(n):
    return dict(origin=BY[n]["origin"], yaw_deg=BY[n]["yaw"])


def wpt(n, lx, lz, dy=0.0):
    return W.to_world(place(n), [lx, dy, lz])


def tier_y(n, lz):
    h = BY[n]
    for (_, z0, z1, dy) in h.get("tiers", []):
        if z1 <= lz <= z0:
            return h["origin"][1] + dy
    return h["origin"][1]


def cup(n):
    cx, cz = BY[n]["cup"]
    p = wpt(n, cx, cz, HJ[n]["cup"]["position"][1]) if n in HJ else wpt(n, cx, cz)
    if n not in HJ:
        p[1] = tier_y(n, cz)
    return p


def tee(n):
    return wpt(n, 0, 0)


def behind(n):
    return wpt(n, 0, BEHIND)


def concept(h):
    w2 = h["W"] / 2
    tiers = h.get("tiers") or [("pad", 6, -h["L"], 0.0)]
    pads = [dict(id=t[0], x=[-w2, w2], z=[t[2], t[1]], y=t[3]) for t in tiers]
    spans = [dict(z=[a, b], over=what) for (a, b, what) in h.get("spans", [])]
    return dict(pads=pads, spans=spans, cup_local=(list(HJ[h["n"]]["cup"]["position"]) if h["n"] in HJ else [h["cup"][0], tier_y(h["n"], h["cup"][1]) - h["origin"][1], h["cup"][1]]),
                size=[h["W"], h["L"] + 6])


# ------------------------------------------------------------------ paths
MAX_RISE = 0.8
TREAD = 1.5
FLIGHT_MAX = 10
LANDING = 4.0
PASS = ("on_hole", "bridge", "lift", "gondola", "dam_crest")


def expand(leg_pts, kinds):
    """leg_pts: [(x,y,z)...]; kinds per leg: 'on_hole'|'walk'|'stairs'|'bridge'|'lift'|'gondola'|'dam_crest' or (kind, name)."""
    segs = []
    for (a, b, k) in zip(leg_pts[:-1], leg_pts[1:], kinds):
        name = None
        if isinstance(k, tuple):
            k, name = k
        a = [round(v, 2) for v in a]
        b = [round(v, 2) for v in b]
        dy = b[1] - a[1]
        L = math.hypot(b[0] - a[0], b[2] - a[2])
        if k != "stairs":
            g = dy / L if L else 0
            typ = k if k in PASS else ("ramp" if abs(g) > 0.01 else "walk")
            s = dict(type=typ, start=a, end=b, grade=round(g, 4))
            if name:
                s["name"] = name
            if typ == "lift":
                s["rise"] = round(dy, 2)
            segs.append(s)
            continue
        n = max(1, math.ceil(abs(dy) / MAX_RISE - 1e-9))
        nf = math.ceil(n / FLIGHT_MAX)
        need = n * TREAD + (nf - 1) * LANDING
        tread = TREAD if L >= need else (L - (nf - 1) * LANDING) / n
        extra = max(0.0, L - need) / 2
        ux, uz = (b[0] - a[0]) / L, (b[2] - a[2]) / L
        s_ = 0.0
        y = a[1]

        def at(sv, yv):
            return [round(a[0] + ux * sv, 2), round(yv, 3), round(a[2] + uz * sv, 2)]

        if extra > 0.05:
            segs.append(dict(type="landing", start=at(0, y), end=at(extra, y), grade=0.0))
            s_ = extra
        left = n
        rise = dy / n
        for fi in range(nf):
            k_ = min(FLIGHT_MAX, left)
            e = s_ + k_ * tread
            segs.append(dict(type="stairs", start=at(s_, y), end=at(e, y + k_ * rise), steps=k_, rise=round(rise, 3), tread=round(tread, 3)))
            y += k_ * rise
            s_ = e
            left -= k_
            if left:
                segs.append(dict(type="landing", start=at(s_, y), end=at(s_ + LANDING, y), grade=0.0))
                s_ += LANDING
        if L - s_ > 0.05:
            segs.append(dict(type="landing", start=at(s_, y), end=at(L, y), grade=0.0))
    return segs


def mkpath(pid, frm, to, pts, kinds, width=6.0, name="", note=""):
    segs = expand(pts, kinds)
    L3 = sum(math.dist(s["start"], s["end"]) for s in segs if s["type"] != "gondola")
    return dict(id=pid, name=name, from_hole=frm, to_hole=to, width=width, segments=segs, length=round(L3, 1), note=note)


def P(x, y, z):
    return [float(x), float(y), float(z)]


SPAWN = P(75, FLOOR, 505)
paths = []
paths.append(mkpath("p_spawn_h1", None, 1, [SPAWN, P(60, FLOOR, 484), behind(1), tee(1)], ["walk", "walk", "on_hole"],
                    width=8.0, name="Junction Walk", note="Junction Plaza (spawn) north to H1, under the trailhead arch view"))
paths.append(mkpath("p_h1_h2", 1, 2, [cup(1), P(74, FLOOR, 438), P(80, FLOOR, 424), behind(2), tee(2)],
                    ["on_hole", "walk", "walk", "on_hole"], name="Boardwalk", note="Plank boardwalk past the general store"))
paths.append(mkpath("p_h2_h3", 2, 3, [cup(2), P(84, FLOOR, 366), P(60, FLOOR, 350), P(-30, FLOOR, 350), P(-84, FLOOR, 350),
                                      P(-108, FLOOR, 345), behind(3), tee(3)],
                    ["on_hole", "walk", "walk", ("bridge", "Ranger Footbridge"), "walk", "walk", "on_hole"],
                    name="Ranger Footbridge", note="West across the Sugarloaf River on the railed ranger footbridge to the ranger station"))
paths.append(mkpath("p_h3_h4", 3, 4, [cup(3), P(-19, FLOOR, 330), P(0, FLOOR, 312), P(150, FLOOR, 312), P(172, FLOOR, 320), behind(4), tee(4)],
                    ["on_hole", "walk", "walk", "walk", "walk", "on_hole"], name="Narrows Trail",
                    note="East across the canyon floor into the mouth of the Rock Candy Narrows slot canyon"))
paths.append(mkpath("p_h4_h5", 4, 5, [cup(4), P(246, FLOOR, 330), P(250, FLOOR, 344), P(264, 22, 344), P(280, 22, 340), behind(5), tee(5)],
                    ["on_hole", "walk", "stairs", "walk", "walk", "on_hole"], name="Geode Steps"))
paths.append(mkpath("p_h5_h6", 5, 6, [cup(5), P(296, 22, 278), P(297, 22, 276), P(297, 26, 266), behind(6), tee(6)],
                    ["on_hole", "walk", "stairs", "walk", "on_hole"], name="Slot Steps"))
paths.append(mkpath("p_h6_h7", 6, 7, [cup(6), P(280, 26, 192), P(298, 26, 178), P(314, TAFFY, 178), P(330, TAFFY, 166), behind(7), tee(7)],
                    ["on_hole", "walk", ("lift", "Rock Candy Lift"), "walk", "walk", "on_hole"], name="Rock Candy Lift",
                    note="Mine-cage lift up the slot wall (+44) onto Taffy Mesa"))
paths.append(mkpath("p_h7_h8", 7, 8, [cup(7), P(322, TAFFY, 86), P(322, TAFFY, 68), P(360, TAFFY, 68), behind(8), tee(8)],
                    ["on_hole", "walk", "walk", "walk", "on_hole"], name="Gap Rim Trail"))
paths.append(mkpath("p_h8_h9", 8, 9, [cup(8), P(360, TAFFY, -8), P(360, TAFFY, -26), P(360, TAFFY, -80), P(360, TAFFY, -88),
                                      P(316, TAFFY, -88), behind(9), tee(9)],
                    ["on_hole", "walk", ("bridge", "Licorice Rope Bridge"), "walk", "walk", "walk", "on_hole"], name="Licorice Rope Bridge",
                    note="Rope bridge over Licorice Slot and its creek"))
paths.append(mkpath("p_h9_h10", 9, 10, [cup(9), P(390, TAFFY, -110), P(400, TAFFY, -130), P(400, TAFFY, -218), P(400, BENCH, -246),
                                        P(330, BENCH, -312), behind(10), tee(10)],
                    ["on_hole", "walk", "walk", ("lift", "Taffy Cliff Lift"), "walk", "walk", "on_hole"], name="Taffy Cliff Lift",
                    note="Cliff elevator (+46) from Taffy Mesa up to the Reservoir Bench"))
paths.append(mkpath("p_h10_h11", 10, 11, [cup(10), P(290, cup(10)[1], -250), P(272, BENCH, -246), P(170, BENCH, -243), behind(11), tee(11)],
                    ["on_hole", "stairs", "walk", "walk", "on_hole"], name="Bench Rim Walk"))
paths.append(mkpath("p_h11_h12", 11, 12, [cup(11), P(150, BENCH + 4, -312), P(128, BENCH, -312), P(100, BENCH, -308), P(46, BENCH, -305),
                                          P(-46, BENCH, -305), P(-100, BENCH, -303), P(-214, BENCH, -298), P(-214, BENCH, -278), behind(12), tee(12)],
                    ["on_hole", "stairs", "walk", "walk", ("dam_crest", "Peppermint Dam crest"), "walk", "walk", "walk", "walk", "on_hole"],
                    name="Dam Crest Walk", width=8.0, note="Across the crest of Peppermint Dam: reservoir on the right, spillway falls and the gorge on the left"))
paths.append(mkpath("p_h12_h13", 12, 13, [cup(12), P(-142, BENCH, -248), P(-224, BENCH, -246), P(-254, HOODOO, -246), P(-264, HOODOO, -306),
                                          P(-290, HOODOO, -304), behind(13), tee(13)],
                    ["on_hole", "walk", ("lift", "Gumdrop Lift"), "walk", "walk", "walk", "on_hole"], name="Gumdrop Lift",
                    note="Lift (+34) up onto the Hoodoo Bench"))
paths.append(mkpath("p_h13_h14", 13, 14, [cup(13), P(-280, HOODOO, -242), P(-278, HOODOO, -212), behind(14), tee(14)],
                    ["on_hole", "walk", "walk", "on_hole"], name="Hoodoo Lane"))
paths.append(mkpath("p_h14_h15", 14, 15, [cup(14), P(-282, HOODOO, -154), P(-278, HOODOO, -128), behind(15), tee(15)],
                    ["on_hole", "walk", "walk", "on_hole"], name="Cableway Walk"))
paths.append(mkpath("p_h15_h16", 15, 16, [cup(15), P(-300, cup(15)[1], -44), P(-300, HOODOO, -26), P(-300, HOODOO, 66), P(-300, CROWN, 92), behind(16), tee(16)],
                    ["on_hole", "stairs", "walk", ("lift", "Crown Lift"), "walk", "on_hole"], name="Crown Lift",
                    note="Lift (+40) up the north face of Sugarloaf Crown"))
paths.append(mkpath("p_h16_h17", 16, 17, [cup(16), P(-300, cup(16)[1], 162), P(-312, CROWN, 176), P(-320, CROWN, 244), behind(17), tee(17)],
                    ["on_hole", "stairs", "walk", "walk", "on_hole"], name="Crown Steps"))
paths.append(mkpath("p_h17_h18", 17, 18, [cup(17), P(-366, CROWN, 184), P(-382, CROWN, 190), P(-382, CROWN, 250), behind(18), tee(18)],
                    ["on_hole", "walk", "walk", "walk", "on_hole"], name="Rim Walk"))
paths.append(mkpath("p_h18_hub", 18, None, [cup(18), P(-420, CROWN, 154), P(-420, CROWN, 136), P(130, FLOOR, 540), P(84, FLOOR, 514)],
                    ["on_hole", "walk", ("gondola", "Sunset Gondola"), "walk"], name="Sunset Gondola",
                    note="From Sunset Point a slow gondola glides back down to Junction Plaza (seated, enclosed cabin, ~3 min)"))

# ------------------------------------------------------------------ water
RIVER = [  # x, z, level, width (north -> south)
    (0, -298, 16.8, 22), (0, -270, 16.7, 16), (-5, -200, 16.5, 14), (-20, -100, 16.2, 14), (-35, 0, 15.9, 16),
    (-50, 100, 15.6, 16), (-55, 200, 15.3, 18), (-52, 300, 15.0, 18), (-60, 400, 14.7, 18), (-80, 500, 14.4, 20), (-100, 700, 14.0, 20)]
LICORICE = [(540, -100, 46.5, 6), (420, -60, 46.0, 6), (300, -48, 45.5, 7), (192, -45, 45.0, 7),
            (178, -44, 16.5, 12), (120, -40, 16.3, 8), (40, -35, 16.1, 8), (-29, -32, 16.0, 8)]
FIZZ = [(-470, -430, 148.6, 6), (-330, -420, 148.3, 7), (-248, -416, 148.0, 8), (-236, -416, 113.6, 12),
        (-205, -417, 109.0, 10), (-180, -418, 108.0, 10)]


def stream(name, pts, depth=3.0, bank=0.8, note=""):
    return dict(name=name, points=[dict(x=float(x), z=float(z), level=lv, width=float(w)) for (x, z, lv, w) in pts],
                depth=depth, bank_slope=bank, bank_reach=10.0, note=note)


streams = [
    stream("Sugarloaf River", RIVER, note="From the Peppermint Dam plunge pool south through the canyon floor past the town"),
    stream("Licorice Creek", LICORICE, depth=2.0, note="Runs west in Licorice Slot, drops off Taffy Mesa as Licorice Falls, joins the river"),
    stream("Fizzwater Creek", FIZZ, depth=2.0, note="Crosses the Hoodoo Bench, drops as Fizzwater Falls onto the Reservoir Bench, feeds the reservoir"),
]
lakes = [dict(name="Sugarloaf Reservoir", center=[0.0, -425.0], radii=[190.0, 112.0], level=RES_LEVEL, depth=8.0,
              beach_width=4.0, beach_slope=0.3, bank_slope=1.0, bank_reach=12.0, note="Ellipse. Fill Water to y 108. Held at its south tip by Peppermint Dam.")]
DAM = dict(name="Peppermint Dam", crest_y=BENCH + 2.0, x=[-44.0, 44.0], z_center=-305.0, thickness=10.0, base_y=FLOOR - 1.0,
           spillway=dict(x=[-10.0, 10.0], lip_y=RES_LEVEL),
           note="Arched concrete dam with peppermint stripes across the notch in the bench. Crest walkway (path p_h11_h12) "
                "at y 116 with solid 3.5-stud parapets and 8-stud side skirts. Spillway in the middle drops into the gorge (Spillway Falls).")
# Exact world-space box geometry; clear walking width excludes the parapets.
DAM["crest_walk"] = dict(path="p_h11_h12", clear_width=8.0, length=92.0, surface_y=BENCH,
    boxes=[dict(id="crest_deck", center=[0, 115.7, -305], size=[92, 0.6, 8], yaw_deg=0, collidable=True)] +
          [dict(id=f"crest_landing_{side}", center=[x, 115.7, -305], size=[8, 0.6, 8], yaw_deg=0,
                collidable=True) for side,x in (("east", 46), ("west", -46))] +
          [dict(id=f"crest_parapet_{side}", center=[0, 117.75, z], size=[92, 3.5, 0.6], yaw_deg=0,
                collidable=True, solid=True) for side,z in (("north", -309.3), ("south", -300.7))] +
          [dict(id=f"crest_skirt_{side}", center=[0, 112, z], size=[92, 8, 0.6], yaw_deg=0,
                collidable=True, solid=True) for side,z in (("north", -309.3), ("south", -300.7))],
    teleport_points=["tp_dam_crest_east", "tp_dam_crest_west"],
    note="All boxes are visible peppermint-striped solids. Skirts meet parapets at deck surface; eight clear studs between parapets.")
waterfalls = []
for sname, pts, names in (("Sugarloaf River", RIVER, {}), ("Licorice Creek", LICORICE, {3: "Licorice Falls"}),
                          ("Fizzwater Creek", FIZZ, {2: "Fizzwater Falls", 3: "Fizzwater Cascade"})):
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        if a[2] - b[2] >= 1.5:
            waterfalls.append(dict(name=names.get(i, f"{sname} falls {i}"), stream=sname, top=[a[0], a[2], a[1]], bottom=[b[0], b[2], b[1]],
                                   drop=round(a[2] - b[2], 2), width=float(min(a[3], b[3]))))
waterfalls.append(dict(name="Spillway Falls", stream="Peppermint Dam", top=[0.0, RES_LEVEL, -309.0], bottom=[0.0, 16.8, -298.0],
                       drop=round(RES_LEVEL - 16.8, 2), width=20.0, note="Spillway sheet down the dam face into the river's plunge pool"))


# ------------------------------------------------------------------ terrain regions
def poly(*pts):
    return dict(type="polygon", points=[[float(a), float(b)] for a, b in pts])


def wobble(x, a=6.0, b=4.0):
    return a * math.sin(x / 37.0) + b * math.sin(x / 13.0 + 1.0)


BENCH_EDGE = [[800.0, -800.0], [-800.0, -800.0]]
for xe in range(-800, 801, 20):
    if -60 < xe < 60:
        continue
    BENCH_EDGE.append([float(xe), round(-232 + wobble(xe), 1)])
    if xe == -60:
        BENCH_EDGE += [[-44.0, -232.0], [-40.0, -305.0], [40.0, -305.0], [44.0, -232.0]]

regions = [
    dict(id="west_ledge", op="set", height=TAFFY, falloff=4.0, edge="cliff",
         shape=poly((-800, -240), (-140, -240), (-150, -140), (-135, -40), (-150, 60), (-140, 160), (-155, 260), (-145, 360),
                    (-165, 460), (-150, 560), (-170, 800), (-800, 800)),
         material="sandstone ledge, pink/cream strata on the cliff"),
    dict(id="taffy_mesa", op="set", height=TAFFY, falloff=4.0, edge="cliff",
         shape=poly((175, -240), (200, -150), (185, -60), (195, 40), (190, 140), (205, 240), (190, 330), (200, 420), (220, 520),
                    (260, 800), (800, 800), (800, -240)),
         material="sandstone mesa top (sand, scrub); striped cliff faces"),
    dict(id="butterscotch_butte", op="set", height=104.0, falloff=5.0, edge="cliff",
         shape=dict(type="ellipse", center=[520.0, 140.0], radii=[80.0, 64.0]), material="second tier on Taffy Mesa"),
    dict(id="gumball_butte", op="set", height=96.0, falloff=5.0, edge="cliff",
         shape=dict(type="ellipse", center=[560.0, -150.0], radii=[56.0, 46.0]), material="second tier on Taffy Mesa"),
    dict(id="reservoir_bench", op="set", height=BENCH, falloff=4.0, edge="cliff", shape=dict(type="polygon", points=BENCH_EDGE),
         material="bench top; notch at x -44..44 holds Peppermint Dam"),
    dict(id="hoodoo_bench", op="set", height=HOODOO, falloff=4.0, edge="cliff",
         shape=poly((-800, -800), (-240, -800), (-238, -420), (-242, -320), (-238, -240), (-244, -140), (-240, -40),
                    (-246, 95), (-800, 95)),
         material="third tier: hoodoo garden, powdered-sugar dunes"),
    dict(id="sugarloaf_crown", op="set", height=CROWN, falloff=4.0, edge="cliff",
         shape=dict(type="ellipse", center=[-370.0, 165.0], radii=[125.0, 105.0]), material="top tier: Sugarloaf Crown"),
    dict(id="old_sugarloaf", op="superellipse_dome", type="superellipse_dome", center=[80.0, 18.0, -130.0], radius=72.0,
         formula="y = 18 + 110*sqrt(max(0, 1-(r/72)^4))",
         params=dict(base=18, height=110, radius=72, exponent=4), material="rock",
         note="Addendum 5: exact superellipse dome, base y18, summit y128; r is horizontal distance from (80,-130)."),
    dict(id="floor_knoll_s", op="hill", center=[220.0, 640.0], radii=[90.0, 50.0], peak=8.0, material="sand"),
    dict(id="floor_knoll_w", op="hill", center=[-110.0, 560.0], radii=[40.0, 30.0], peak=5.0, material="sand"),
    dict(id="rock_candy_narrows", op="slot", wall=3.0, note="Slot canyon cut into Taffy Mesa: holes H4-H6. points = [x, z, floor y, width]",
         points=[[150, 330, FLOOR, 44], [248, 330, FLOOR, 44], [280, 330, 22, 48], [280, 266, 22, 44], [280, 258, 26, 44], [280, 150, 26, 44]]),
    dict(id="taffy_gap", op="slot", wall=3.0, note="Dead-end slot under H7's rope bridges",
         points=[[300, 108, 40, 22], [420, 100, 40, 22], [520, 60, 42, 24]]),
    dict(id="licorice_slot", op="slot", wall=3.0, note="Slot carrying Licorice Creek west to Licorice Falls",
         points=[[180, -45, 46, 22], [300, -48, 47, 22], [420, -60, 47.5, 22], [540, -100, 48, 22]]),
]

terrain = dict(
    method=("Deterministic heightfield h(x,z) (tools/worldlib.py height_at), evaluated in order: "
            "(1) base: h = base.height + sum(amp*sin(2*pi*x/wx+px)*sin(2*pi*z/wz+pz)). "
            "(2) regions in list order. 'set': w = 1-smoothstep(d/falloff), d = distance outside the shape (0 inside); h += (height-h)*w. "
            "'hill': h += peak*cos^2(pi/2*q), q = elliptical radius/radii < 1. 'superellipse_dome': within radius use exact base+height*sqrt(max(0,1-(r/radius)^exponent)); detail noise is suppressed on this feature. 'slot': along the polyline [x,z,floor,width] (linear between "
            "vertices) h = min(h, h + (floor-h)*(1-smoothstep((d-width/2)/wall))). "
            "(3) rim: q = superellipse radius; t = smoothstep((q-start)/(full-start)); h = max(h, height*(1+variation*sin(lobes*atan2+phase))*t + (1-t)*h); "
            "then detail_noise. (4) pads: every concept pad box flattened to its y, blended back over `falloff` beyond `margin`; inside a "
            "declared span h = min(natural, pad). (5) paths: within width/2+1 of a graded segment h = profile (stairs: profile - stair_bed_drop), "
            "blended over `shoulder`; segments on_hole/bridge/lift/gondola/dam_crest don't grade. (5b) pad clamp: pad boxes (outside spans) = pad y. "
            "(6) water: h = min(h, stream/lake carve profile); stream bank: level + bank_slope*(d - width/2) out to bank_reach, lake: beach then bank_slope out to bank_reach (no carve beyond). smoothstep(t) = t^2(3-2t), t clamped to [0,1]."),
    base=dict(height=FLOOR, noise=[dict(amp=0.5, wx=97.0, wz=131.0, phase=[0.3, 1.1]), dict(amp=0.3, wx=41.0, wz=53.0, phase=[2.0, 0.4])],
              detail_noise=[dict(amp=0.25, wx=37.0, wz=-53.0, phase=[0.5, 1.7]), dict(amp=0.4, wx=113.0, wz=89.0, phase=[2.4, 0.2])]),
    regions=regions,
    rim=dict(center=[0.0, 0.0], half_size=[640.0, 640.0], exponent=4.0, start=0.86, full=0.99, height=150.0,
             variation=0.3, lobes=7.0, phase=0.4, note="Outer canyon walls hide the terrain edge"),
    path_grading=dict(shoulder=4.0, stair_bed_drop=0.6),
    pads=dict(rule="Concept pads are flat at their y (felt is built on top later). margin 3 then blend over falloff.", margin=3.0, falloff=8.0),
    strata=dict(band=6.0, colors=["#E8736B", "#F6E3C8", "#D9534F", "#F2B48A", "#C8463F", "#FBEAD6"],
                note="Visual only: cliff faces are painted in horizontal bands by world y (band height 6 studs), candy-stripe sandstone"),
)

# ------------------------------------------------------------------ holes block
holes_out = []
SURROUND = {
    1: "Canyon floor at Sugarloaf Junction (y 18); boardwalk town to the east, Old Sugarloaf dome rising on the northern skyline",
    2: "Junction mine-head against a rock outcrop; Taffy Mesa's striped cliffs 80 studs east",
    3: "Both banks of the Sugarloaf River; ranger station and lookout cupola on the west bank, West Ledge cliffs behind",
    4: "Mouth of the Rock Candy Narrows: 52-stud slot walls, rock-candy crystals in the walls",
    5: "Deep in the Narrows at the slot's bend; only a ribbon of sunset sky overhead",
    6: "Upper Narrows below the slot head; the Rock Candy Lift cage hangs on the wall",
    7: "Taffy Mesa top (y 70), crossing Taffy Gap; Old Sugarloaf and the dam in view",
    8: "Open mesa top among gumdrop boulders, Butterscotch Butte to the east",
    9: "North end of Taffy Mesa by Licorice Slot; the Reservoir Bench cliff rises 46 studs to the north",
    10: "East end of the Reservoir Bench (y 116), looking south over the whole canyon",
    11: "Reservoir shore east of the dam; lock gates and the reservoir behind the green",
    12: "West shore beyond the dam; intake tower stands in the reservoir to the north-east",
    13: "Hoodoo Bench (y 150) among striped hoodoo spires, Fizzwater Falls to the north",
    14: "Hoodoo Bench, under the old cableway that once carried ore buckets to the dam",
    15: "Powdered-sugar dunes at the south end of the Hoodoo Bench; Sugarloaf Crown's north face ahead",
    16: "Top of Sugarloaf Crown (y 190), the highest ground in the world",
    17: "Crown summit plateau; panorama over every zone",
    18: "West rim of the Crown with Sunset Arch framing the setting sun beside the green",
}
for h in HOLES:
    n = h["n"]
    pl = place(n)
    hj = dict(number=n, id=h["id"], name=h["name"], par=h["par"], zone=h["zone"],
              status="specced" if n in HJ else "concept_footprint",
              holes_json=(f"holes.json holes[{n - 1}] ({HJ[n]['id']})" if n in HJ else None),
              gimmick=HJ.get(n, {}).get("gimmick", h["gimmick"]), landmark=h["landmark"],
              placement=dict(origin=[round(v, 3) for v in h["origin"]], yaw_deg=h["yaw"]),
              play_bearing_deg=round(W.bearing(*W.play_dir(h["yaw"])), 1),
              concept=concept(h), tee_world=[round(v, 2) for v in tee(n)], cup_world_approx=[round(v, 2) for v in cup(n)],
              surroundings=SURROUND[n], enclosed=h["zone"] == "Rock Candy Narrows")
    pw = W.pads_world(hj)
    xs = [c[0] for p in pw for c in p["corners"]]
    zs = [c[1] for p in pw for c in p["corners"]]
    hj["footprint_bbox"] = dict(x=[round(min(xs), 1), round(max(xs), 1)], z=[round(min(zs), 1), round(max(zs), 1)])
    holes_out.append(hj)

# ------------------------------------------------------------------ POIs, lifts, teleports
pois = [
    dict(id="junction_plaza", name="Junction Plaza", pos=SPAWN, radius=14.0, kind="plaza",
         note="Spawn and hub: course board, gondola arrival, teleport kiosk, saloon-style clubhouse"),
    dict(id="general_store", name="Junction General Store", pos=[150, FLOOR, 455], kind="landmark", note="Boardwalk storefronts, candy barrels"),
    dict(id="mine-head", name="Mine-head", pos=[134, FLOOR, 392], kind="landmark",
         note="East of H2: candy-striped headframe, winding house and ore cart; ground sampled from terrain."),
    dict(id="water_tower", name="Candy-striped Water Tower", pos=[14, FLOOR, 440], kind="landmark"),
    dict(id="ranger_station", name="Ranger Station", pos=[-135, FLOOR, 372], radius=10.0, kind="landmark",
         note="Timber station with a fire-lookout cupola; flagpole; ranger's map table"),
    dict(id="narrows_mouth", name="Narrows Mouth", pos=[165, FLOOR, 340], kind="viewpoint", note="Entrance to the slot canyon, crystal arch"),
    dict(id="taffy_overlook", name="Taffy Gap Overlook", pos=[300, TAFFY, 70], kind="viewpoint"),
    dict(id="old_sugarloaf", name="Old Sugarloaf", pos=[80, 18, -130], kind="landmark", note="Free-standing striped dome, base y18 and summit y128; superellipse terrain feature"),
    dict(id="dam", name="Peppermint Dam", pos=[0, BENCH, -305], kind="landmark"),
    dict(id="intake_tower", name="Intake Tower", pos=[-120, RES_LEVEL, -345], kind="landmark", note="Domed tower in the reservoir (H12 teleport theme)"),
    dict(id="hoodoo_garden", name="Hoodoo Garden", pos=[-380, HOODOO, -200], kind="decor", note="Dense cluster of hoodoo spires west of H13-H15"),
    dict(id="sunset_point", name="Sunset Point", pos=[-420, CROWN, 136], radius=8.0, kind="viewpoint", note="Gondola top station; course finish board"),
    dict(id="sunset_arch", name="Sunset Arch", pos=[-478, CROWN, 205], kind="landmark",
         note="Natural arch on the Crown's west rim beside H18; frames the setting sun from the H18 green"),
]
for poi_id, hole_num, anchor_name in (("ranger_station", 3, "ranger_station"), ("intake_tower", 12, "intake_tower")):
    if hole_num in HJ:
        anchor = next(a for a in HJ[hole_num]["decoration_anchors"] if a["name"] == anchor_name)
        poi = next(p for p in pois if p["id"] == poi_id)
        poi.update(pos=W.to_world(place(hole_num), anchor["position"]),
                   source=f"holes.json H{hole_num}.decoration_anchors[{anchor_name}]",
                   size=anchor["approx_size"], instantiate=False,
                   note="Locator only: instantiate the hole anchor once; no separate world mesh.")
for p in pois:
    p["pos"] = [round(float(v), 2) for v in p["pos"]]

lifts = []
for p in paths:
    for s in p["segments"]:
        if s["type"] in ("lift", "gondola"):
            lifts.append(dict(name=s.get("name"), type=s["type"], path=p["id"], bottom=s["start"] if s["start"][1] < s["end"][1] else s["end"],
                              top=s["end"] if s["start"][1] < s["end"][1] else s["start"], rise=round(abs(s["end"][1] - s["start"][1]), 1),
                              speed_studs_s=4.0 if s["type"] == "lift" else 6.0,
                              note=("Open-sided mine-cage lift, constant 4 studs/s (1.2 m/s), no acceleration jolts; railings all round; "
                                    "the player stands still. Teleport alternative at both ends." if s["type"] == "lift" else
                                    "Seated enclosed gondola cabin, 6 studs/s, straight cable; skip-able by teleport")))
teleports = [
    dict(id="tp_junction", name="Junction Plaza", pos=[86, FLOOR, 510], zone="Sugarloaf Junction"),
    dict(id="tp_narrows", name="Narrows Mouth", pos=[160, FLOOR, 322], zone="Rock Candy Narrows"),
    dict(id="tp_taffy", name="Taffy Lift Top", pos=[322, TAFFY, 184], zone="Taffy Mesa"),
    dict(id="tp_dam", name="Dam East Overlook", pos=[64, BENCH, -296], zone="Sugarloaf Dam"),
    dict(id="tp_dam_crest_east", name="Dam crest east end", pos=[46, BENCH, -305], size=[4, 0.1, 4], support_box="crest_landing_east", zone="Sugarloaf Dam"),
    dict(id="tp_dam_crest_west", name="Dam crest west end", pos=[-46, BENCH, -305], size=[4, 0.1, 4], support_box="crest_landing_west", zone="Sugarloaf Dam"),
    dict(id="tp_hoodoo", name="Hoodoo Lift Top", pos=[-262, HOODOO, -236], zone="Hoodoo Garden"),
    dict(id="tp_crown", name="Crown Lift Top", pos=[-290, CROWN, 96], zone="Sugarloaf Crown"),
]

# ------------------------------------------------------------------ world
b = dict(x=[-640.0, 640.0], z=[-640.0, 640.0])
world = dict(
    name="Sugarloaf Canyon - world layout",
    version="0.1-concept",
    units="studs (1 stud = 0.3 m), +Y up, map view +X east/right, -Z north/up. Same axes as Lantern Grove holes.json/world.json.",
    bounds=dict(x=b["x"], z=b["z"], size=[b["x"][1] - b["x"][0], b["z"][1] - b["z"][0]], y_range=[0.0, 260.0],
                note="Terrain extent. Backdrop meshes sit outside it."),
    placement_convention=dict(
        apply=("For every (future) holes.json element of hole N: rotate its LOCAL x/z about +Y by placement.yaw_deg, then translate by "
               "placement.origin. x' = lx*cos(yaw) + lz*sin(yaw) + origin.x ; z' = -lx*sin(yaw) + lz*cos(yaw) + origin.z ; y' = ly + origin.y. "
               "Piece yaw_world = piece.yaw + yaw_deg. Positive yaw = counter-clockwise in the map view: yaw 0 plays north, 90 west, "
               "180 south, -90 east. The local origin is the tee; play is toward local -Z."),
        roblox="holeRoot = CFrame.new(origin) * CFrame.Angles(0, math.rad(yaw_deg), 0); partCFrame = holeRoot * localCFrame. Axes rotate only.",
        concept_footprint=("Until holes.json exists each hole is concept.pads: flat boxes in the local frame (x range, z range, y offset "
                           "from origin.y). The future hole geometry (felt + rails + props within 2 studs) must stay inside them. "
                           "concept.spans = local z ranges where the hole bridges a gap or river and the ground is not flattened."),
    ),
    sun=dict(bearing_deg=277.0, elevation_deg=25.0, clock_time=16.3,
             note="IN-GAME golden hour. ClockTime is approximate: calibrate geographic latitude/time in Studio to bearing 277, elevation 25. No tee plays within 45 deg of this bearing."),
    hero_render_sun=dict(bearing_deg=277.0, elevation_deg=2.0, hero_render_only=True,
                         arch_bearing_deg=277.0, arch_elevation_range_deg=[-12.0, 1.0],
                         alignment_warning="Requested +2 deg is 1 deg ABOVE the arch top (+1), not inside the opening. Use only for hero renders; never override game lighting."),
    spawn=dict(pos=SPAWN, look_at=[round(v, 2) for v in tee(1)], note="SpawnLocation in Junction Plaza facing north to H1; Old Sugarloaf on the skyline"),
    zones=[
        dict(name="Sugarloaf Junction", holes=[1, 2, 3], ground_y=FLOOR, note="Canyon-floor frontier town, river, ranger station"),
        dict(name="Rock Candy Narrows", holes=[4, 5, 6], ground_y=[FLOOR, 26.0], note="Slot canyon cut into Taffy Mesa"),
        dict(name="Taffy Mesa", holes=[7, 8, 9], ground_y=TAFFY, note="First mesa top; rope bridges over slots"),
        dict(name="Sugarloaf Dam", holes=[10, 11, 12], ground_y=BENCH, note="Reservoir Bench, Peppermint Dam, reservoir"),
        dict(name="Hoodoo Garden", holes=[13, 14, 15], ground_y=HOODOO, note="Third tier, hoodoo spires and sugar dunes"),
        dict(name="Sugarloaf Crown", holes=[16, 17, 18], ground_y=CROWN, note="Top tier finale, Sunset Arch, gondola home"),
    ],
    holes=holes_out,
    terrain=terrain,
    streams=streams,
    lakes=lakes,
    dam=DAM,
    waterfalls=waterfalls,
    paths=paths,
    path_rules=dict(max_ramp_grade=0.10, max_step_rise=1.0, design_step_rise=MAX_RISE, tread=TREAD, max_steps_per_flight=FLIGHT_MAX,
                    landing_length=LANDING, min_width=5.0, max_lift_rise=60.0, max_lift_offset=30.0, rail_drop=4.0,
                    segment_types="on_hole (across the hole's own area), walk (<1% grade), ramp (<=10%), stairs (flight: steps x rise, tread), "
                                  "landing (flat), bridge (rope/plank bridge, railed), dam_crest (railed walkway on the dam), "
                                  "lift (vertical cage lift: start/end = boarding points), gondola (cable car)",
                    rails="seg.rails = ['left'|'right'...]: sides that need a railing because the ground drops > rail_drop studs within "
                          "2.5 studs of the walkway edge (left/right relative to walking direction). Bridges and dam crest: both."),
    lifts=lifts,
    teleport_points=teleports,
    pois=pois,
    heightmap=dict(file="heightmap.png", stud_per_px=1.0, y_min=0.0, y_max=260.0, bit_depth=16,
                   mapping="pixel (i=col, j=row) centre -> x = bounds.x[0] + (i+0.5), z = bounds.z[0] + (j+0.5) (row 0 = north edge); "
                           "y = gray/65535*260"),
)

# ------------------------------------------------------------------ rails at drops (needs the heightfield)
RAIL_DROP = 4.0


def seg_rails(seg, width):
    if seg["type"] in ("bridge", "dam_crest"):
        return ["left", "right"]
    if seg["type"] in ("on_hole", "lift", "gondola"):
        return []
    a, b_ = seg["start"], seg["end"]
    L = math.hypot(b_[0] - a[0], b_[2] - a[2])
    if L < 1e-6:
        return []
    ux, uz = (b_[0] - a[0]) / L, (b_[2] - a[2]) / L
    lx, lz = uz, -ux          # left of the walking direction (map: x east, z south)
    t = np.linspace(0, 1, max(2, int(L / 1.5) + 1))
    px = a[0] + (b_[0] - a[0]) * t
    pz = a[2] + (b_[2] - a[2]) * t
    py = a[1] + (b_[1] - a[1]) * t
    out = []
    for side, sg in (("left", 1), ("right", -1)):
        off = width / 2 + 2.5
        h = W.height_at(world, px + sg * lx * off, pz + sg * lz * off)
        if (py - h > RAIL_DROP).any():
            out.append(side)
    return out


for p in world["paths"]:
    for s in p["segments"]:
        r = seg_rails(s, p["width"])
        if r:
            s["rails"] = r


def hgt(x, z):
    return round(float(W.height_at(world, np.array([float(x)]), np.array([float(z)]))[0]), 1)


for poi in pois:
    if poi["id"] == "mine-head":
        poi["pos"][1] = hgt(134, 392)

# ------------------------------------------------------------------ backdrop + scenery pieces
rnd = random.Random(19)
pieces = []
for i in range(14):    # distant mesas / buttes outside the terrain
    ang = i * (360 / 14) + rnd.uniform(-8, 8)
    r = rnd.uniform(1000, 1500)
    a = math.radians(ang)
    west = max(0.0, -math.cos(a))
    pieces.append(dict(id=f"far_mesa_{i+1:02d}", kind="distant_mesa", pos=[round(r * math.cos(a)), 0, round(r * math.sin(a))],
                       size=[round(rnd.uniform(300, 600)), round(140 + 160 * west + rnd.uniform(-20, 40)), round(rnd.uniform(200, 350))],
                       yaw_deg=round(-ang + 90, 1), note="Flat-topped striped mesa silhouette; hazed lilac to peach"))
for i in range(10):
    ang = i * 36 + rnd.uniform(-10, 10)
    r = rnd.uniform(720, 900)
    a = math.radians(ang)
    pieces.append(dict(id=f"butte_spire_{i+1:02d}", kind="butte_spire", pos=[round(r * math.cos(a)), 0, round(r * math.sin(a))],
                       size=[round(rnd.uniform(50, 110)), round(rnd.uniform(150, 260)), round(rnd.uniform(50, 110))], yaw_deg=round(rnd.uniform(0, 360)),
                       note="Tall striped butte/spire just outside the canyon rim"))
named = [
    ("far_arch_west", "far_arch", [-1250, 0, 60], [420, 300, 80], "Huge natural arch on the western horizon; hero sun is horizontally aligned at bearing 277; requested elevation +2 is 1 degree above the opening top"),
    ("sugarloaf_twins", "far_butte", [-900, 0, -700], [260, 380, 260], "Two rounded sugarloaf domes far to the north-west"),
    ("hot_air_balloons", "sky", [0, 320, 0], [24, 30, 24], "6 candy-striped hot-air balloons drifting slowly on loops r 500-900, y 260-420"),
    ("sun_disc", "sky", [round(2400 * math.sin(math.radians(277)), 2), round(2400 * math.tan(math.radians(25)), 2), round(-2400 * math.cos(math.radians(277)), 2)], [260, 260, 1], "In-game sun direction bearing 277, elevation 25; orient sky disc to camera. Hero lighting uses separate hero_render_sun."),
    ("cloud_streaks", "sky", [0, 700, 0], [800, 60, 200], "8 long pink-orange cloud streaks at r 1800-2400"),
    ("old_sugarloaf_dome", "hero_landmark", [80, 18, -130], [144, 110, 144], "Mesh dressing over the terrain dome: candy-striped strata bands, a lone lollipop cactus on top"),
    ("peppermint_dam", "hero_structure", [0, 17, -305], [88, 101, 10], "Curved dam with red/white stripes, crest walkway + railings, spillway slot 20 wide"),
    ("junction_town", "building_set", [150, 18, 455], [30, 14, 80], "Row of 5 false-front shops (candy store, saloon-clubhouse, assay office)"),
    ("mine-head", "building", [134, 18, 392], [14, 18, 12], "Candy-striped mine headframe and winding house east of H2"),
    ("water_tower", "building", [14, 18, 440], [10, 30, 10], "Candy-striped water tower"),
    ("gondola_top_station", "structure", [-420, 190, 128], [16, 14, 12], "Sunset Gondola top station"),
    ("gondola_bottom_station", "structure", [132, 18, 544], [16, 14, 12], "Sunset Gondola bottom station"),
    ("sunset_arch", "hero_landmark", [-478, 190, 205], [16, 46, 50], "Natural arch on the Crown's west rim, opening 30 wide x 34 high, faces west"),
    ("cableway_trestles", "structure", [-330, 150, -200], [6, 30, 6], "3 old ore-cableway trestles across the Hoodoo Bench (H14 theme), one per 60 studs"),
]
for (i_, k_, pos_, size_, note_) in named:
    pos_ = [float(v) for v in pos_]
    if i_ != "old_sugarloaf_dome" and k_ in ("building", "building_set", "structure", "hero_landmark") and abs(pos_[0]) < 640 and abs(pos_[2]) < 640:
        pos_[1] = hgt(pos_[0], pos_[2])
    pieces.append(dict(id=i_, kind=k_, pos=pos_, size=size_, note=note_))


def clear_of_play(x, z, r):
    """True if a scenery piece of radius r at (x,z) keeps >= 6 studs from every footprint and walkway."""
    for h in world["holes"]:
        for p in W.pads_world(h):
            if float(W.rect_dist(np.array(x), np.array(z), p["cx"], p["cz"], p["sx"], p["sz"], p["yaw"])) < r + 6:
                return False
    for p in world["paths"]:
        for s in p["segments"]:
            if s["type"] == "gondola":
                continue
            d, _ = W.seg_dist(np.array(x), np.array(z), (s["start"][0], s["start"][2]), (s["end"][0], s["end"][2]))
            if float(d) < r + p["width"] / 2 + 4:
                return False
    return True


# hoodoo spires on the Hoodoo Bench, crystals in the Narrows, lollipop cacti on mesa tops
for kind, n, box, ylev, size, note in (
        ("hoodoo_spire", 34, ((-520, -260), (-430, 60)), HOODOO, ([6, 12], [18, 40]), "Striped hoodoo spire with a gumdrop cap"),
        ("rock_candy_crystal", 16, ((170, 300), (140, 352)), None, ([3, 7], [5, 14]), "Pink/amber rock-candy crystal cluster at the slot walls"),
        ("lollipop_cactus", 40, ((210, 600), (-220, 600)), TAFFY, ([4, 6], [8, 16]), "Saguaro-style cactus topped with swirl lollipops and gumball fruit"),
        ("lollipop_cactus", 18, ((-120, 200), (380, 620)), FLOOR, ([4, 6], [8, 14]), "Cactus on the canyon floor"),
        ("lollipop_cactus", 14, ((-480, -260), (90, 250)), CROWN, ([4, 6], [8, 14]), "Cactus on the Crown"),
):
    placed = 0
    tries = 0
    while placed < n and tries < 4000:
        tries += 1
        x = rnd.uniform(*box[0])
        z = rnd.uniform(*box[1])
        w_ = rnd.uniform(*size[0])
        hy = hgt(x, z)
        if ylev is not None and abs(hy - ylev) > 1.0:
            continue
        if ylev is None and not (FLOOR - 1 <= hy <= 27):
            continue
        if not math.isnan(float(W.water_surface(world, np.array([x]), np.array([z]))[0])):
            continue
        if not clear_of_play(x, z, w_ / 2):
            continue
        placed += 1
        pieces.append(dict(id=f"{kind}_{placed:02d}" if kind != "lollipop_cactus" else f"cactus_{ylev:.0f}_{placed:02d}",
                           kind=kind, pos=[round(x, 1), hy, round(z, 1)], size=[round(w_, 1), round(rnd.uniform(*size[1]), 1), round(w_, 1)],
                           yaw_deg=round(rnd.uniform(0, 360)), note=note))

world["backdrop"] = dict(
    rings=[
        dict(id="canyon_rim", name="Outer canyon walls (terrain rim)", note="Rim rises to y ~150-200 at the terrain edge, striped cliffs"),
        dict(id="butte_spires", name="Butte spires", radius=[720, 900], count=10),
        dict(id="far_mesas", name="Distant mesas", radius=[1000, 1500], count=14, color="lilac #B49AC9 -> peach #F2B48A with height haze"),
        dict(id="sky", name="Sunset sky", radius=[1800, 2400], note="In-game sun at bearing 277 / elevation 25, pink-orange cloud streaks, balloons"),
    ],
    pieces=pieces,
)

with open(W.WORLD_JSON, "w") as f:
    json.dump(world, f, indent=1)
print("wrote", W.WORLD_JSON)
for p in paths:
    print(f"{p['id']:12s} {p['length']:7.1f}")
print("walk total (spawn->H18 cup, excluding gondola):", round(sum(p["length"] for p in paths if p["to_hole"]), 1))
print("pieces", len(pieces), "| total par", sum(h["par"] for h in HOLES))
