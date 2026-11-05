"""Author Aurora Archipelago's world -> world/world.json (adapted from sugarloaf-canyon/world/tools/build_world.py).

Everything here is in WORLD studs (Y up, +X east, -Z north, 1 stud = 0.3 m). Holes are `concept_footprint`s: a placement
{origin, yaw_deg} of the hole's local frame (tee at the origin, play toward local -Z) plus flat pad boxes (tiers) in that frame.
Hole-by-hole geometry (holes.json) comes later and must fit inside these footprints.

The world is a ring of floating islands climbing anticlockwise (map view) round the Starfrost Spire:
  Lanternfall Landing 60 -> Steamwhistle Lagoons 84 -> Candyfrost Reef 112 -> Driftfloe Shelf 146 -> Icefall Terraces 182 -> Skylight Summit 222
Islands are generated from the holes and walkways they carry (box lobes round every footprint, capsule lobes round every walk leg,
discs round every hub), so pads always sit >= 11 studs inside a cliff edge and walkways run on solid ground or on railed bridges.
Below them is the cloud floor (y 0): no terrain voxels under void.terrain_fill_min_y, a cloud-deck mesh and a respawn plane.

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
LANDING = 60.0    # Lanternfall Landing (spawn, H1-H3)
LAGOON = 84.0     # Steamwhistle Lagoons (H4-H6)
REEF = 112.0      # Candyfrost Reef (H7-H9)
FLOE = 146.0      # Driftfloe Shelf (H10-H12)
ICEFALL = 182.0   # Icefall Terraces (H13-H15) and the Aurora Landing pinnacle
SUMMIT = 222.0    # Skylight Summit (H16-H18)
SPIRE_ISLE = 100.0
LAGOON_LEVEL = 82.8
CLOUD_FLOOR = 0.0
FILL_MIN = 30.0   # no terrain voxels below this (void over the cloud deck)
CLOUD_DECK = 36.0
RESPAWN_Y = 40.0
HOLE_MARGIN = 14.0  # island lobe margin round every footprint (pads stay >= 11 inside the cliff edge after wobble)

SPIRE = dict(x=0.0, z=-40.0, base_y=SPIRE_ISLE, height=240.0)
SPIRE_TOP = SPIRE["base_y"] + SPIRE["height"]

# ------------------------------------------------------------------ holes (concept footprints)
# W x L = footprint width (local x) x length (local -z, from the tee); the box runs from local z +6 (tee pad) to -L.
# tiers: [(id, z_from, z_to, dy)]; spans: [(z_from, z_to, name)] local z ranges bridged over a gap (no ground below).
HOLES = [
    dict(n=1, id="h01_lantern_quay", name="Lantern Quay", zone="Lanternfall Landing", par=2,
         origin=[-150.0, LANDING, 545.0], yaw=0.0, W=18, L=40, cup=(0, -32),
         gimmick="Bank shot: a snow-capped boulder with a 45-degree bank face turns the ball onto an offset green",
         family="static", motion=None,
         landmark="Brass harbour lantern on a driftwood post, Starfrost Spire straight ahead"),
    dict(n=2, id="h02_snowpuff_burrows", name="Snowpuff Burrows", zone="Lanternfall Landing", par=3,
         origin=[-115.0, LANDING, 480.0], yaw=-90.0, W=26, L=52, cup=(6, -44),
         gimmick="Tunnel choice: three snow burrows under a drift (short and tight, long and safe, one dead end that rolls the ball back)",
         family="route choice", motion=None,
         landmark="Snowpuff rookery: round penguin-puffin figures peeking out of the burrow mouths"),
    dict(n=3, id="h03_glimmer_crossing", name="Glimmer Crossing", zone="Lanternfall Landing", par=3,
         origin=[-40.0, LANDING, 470.0], yaw=-45.0, W=26, L=70, cup=(0, -62), spans=[(-50, -24, "Glimmer Gap (open sky to the cloud sea)")],
         gimmick="Rail-less glowing ice plank straight over the Glimmer Gap (risky) or the railed ice bridge round the side (safe); misses respawn at the bridge entry",
         family="route choice", motion=None,
         landmark="Glimmer Islet: a small floating island with a crystal cluster and a frozen waterfall"),
    dict(n=4, id="h04_glissade", name="Glissade", zone="Steamwhistle Lagoons", par=3,
         origin=[185.0, LAGOON, 470.0], yaw=0.0, W=24, L=58, cup=(0, -50),
         gimmick="Ice felt: a glassy low-friction ice strip where the ball barely slows; pace control into a snow-felt green",
         family="surface", motion=None,
         landmark="Frosted palms leaning over a long ice slide, steam drifting from the lagoons"),
    dict(n=5, id="h05_geyser_hop", name="Geyser Hop", zone="Steamwhistle Lagoons", par=3,
         origin=[215.0, LAGOON, 420.0], yaw=-90.0, W=26, L=56, cup=(0, -48),
         tiers=[("lower", 6, -28, 0.0), ("upper", -28, -56, 4.0)],
         gimmick="Geyser lift: a basalt platform rides a steam column up 4 studs to the upper green, pauses, and sinks back; roll on while it is down",
         family="level change / timing", motion="vertical lift (piston with dwell)",
         landmark="Steamwhistle Geyser puffing beside the green"),
    dict(n=6, id="h06_palm_lagoon", name="Palm Lagoon", zone="Steamwhistle Lagoons", par=3,
         origin=[305.0, LAGOON, 478.0], yaw=0.0, W=30, L=60, cup=(0, -52),
         gimmick="Side-slope green: a warm stone shelf tilted toward a turquoise hot-spring pool (hazard; misses respawn beside it)",
         family="static", motion=None,
         landmark="Kettle Lagoon with frosted palms and a steaming turquoise pool"),
    dict(n=7, id="h07_mogul_meadow", name="Mogul Meadow", zone="Candyfrost Reef", par=3,
         origin=[365.0, REEF, 330.0], yaw=0.0, W=26, L=56, cup=(0, -48),
         gimmick="Rolling dips: four snow moguls built from opposing planar slopes; pace the ball over the humps",
         family="static", motion=None,
         landmark="Candy-bright coral-ice fans along the meadow edge"),
    dict(n=8, id="h08_coral_pinball", name="Coral Pinball", zone="Candyfrost Reef", par=3,
         origin=[430.0, REEF, 300.0], yaw=0.0, W=26, L=54, cup=(0, -46),
         gimmick="Bumper field: static flat-faced coral-ice bumpers at set angles bounce the ball toward the cup",
         family="static", motion=None,
         landmark="Giant pink and tangerine coral-ice branches glowing from inside"),
    dict(n=9, id="h09_conch_shortcut", name="Conch Shortcut", zone="Candyfrost Reef", par=4,
         origin=[535.0, REEF, 230.0], yaw=0.0, W=34, L=72, cup=(0, -64),
         gimmick="Teleport: sink the ball into a giant coral-ice conch and it shoots out of a second shell near the green, or play the long reef route",
         family="route choice", motion=None,
         landmark="Two giant spiral conch shells of candy coral-ice"),
    dict(n=10, id="h10_bobsled_bend", name="Bobsled Bend", zone="Driftfloe Shelf", par=3,
         origin=[510.0, FLOE, 60.0], yaw=90.0, W=24, L=58, cup=(0, -50),
         gimmick="Half-pipe: an S-bend bobsled channel with banked felt walls; ride high to carry the bend",
         family="static", motion=None,
         landmark="Striped bobsled start hut with brass bells"),
    dict(n=11, id="h11_floe_drift", name="Floe Drift", zone="Driftfloe Shelf", par=3,
         origin=[410.0, FLOE, 40.0], yaw=0.0, W=26, L=56, cup=(0, -48),
         gimmick="Drifting ice floe: a flat floe slides across the lane, pauses, and drifts back (slide with dwell; pointed 45-degree ends)",
         family="timing", motion="linear slide with dwell",
         landmark="Frozen Floe Pond with a snowpuff ice-fishing hut"),
    dict(n=12, id="h12_icebreaker_wheel", name="Icebreaker Wheel", zone="Driftfloe Shelf", par=3,
         origin=[370.0, FLOE, -60.0], yaw=90.0, W=26, L=54, cup=(0, -46),
         gimmick="Vertical rotor: a little icebreaker boat's paddle wheel turns across the lane on a horizontal axle; signed bypass lane",
         family="timing", motion="vertical rotor (horizontal axle)",
         landmark="Beached toy icebreaker with a red funnel and a paddle wheel"),
    dict(n=13, id="h13_snowpuff_carousel", name="Snowpuff Carousel", zone="Icefall Terraces", par=3,
         origin=[120.0, ICEFALL, -230.0], yaw=0.0, W=30, L=56, cup=(0, -48),
         gimmick="Horizontal sweeper: a carousel of snowpuff figures sweeps four arms round a solid central hub",
         family="timing", motion="horizontal rotor (vertical axle)",
         landmark="Brass-and-ice carousel canopy topped with a snowpuff weathervane"),
    dict(n=14, id="h14_bell_buoy", name="Bell Buoy", zone="Icefall Terraces", par=3,
         origin=[85.0, ICEFALL, -300.0], yaw=90.0, W=24, L=54, cup=(0, -46),
         gimmick="Pendulum: a brass icicle bell swings across the lane from a timber gantry",
         family="timing", motion="pendulum swing",
         landmark="Timber bell gantry hung with icicles and a brass bell"),
    dict(n=15, id="h15_frozen_falls", name="Frozen Falls", zone="Icefall Terraces", par=2,
         origin=[12.0, ICEFALL, -334.0], yaw=0.0, W=20, L=40, cup=(0, -32),
         tiers=[("upper", 6, -20, 0.0), ("lower", -20, -40, -4.0)],
         gimmick="Drop between levels: putt over the lip of a frozen waterfall and fall 4 studs into a basin green",
         family="level change", motion=None,
         landmark="Frozen waterfalls pouring off the island edge into the cloud sea"),
    dict(n=16, id="h16_moonwell", name="Moonwell", zone="Skylight Summit", par=2,
         origin=[-110.0, SUMMIT, -300.0], yaw=0.0, W=20, L=40, cup=(0, -32),
         gimmick="Funnel: a moonstone well bowl gathers the ball toward the cup, with the cup set off the funnel's exit line",
         family="static", motion=None,
         landmark="Moonstone well ringed with glowing ice crystals"),
    dict(n=17, id="h17_aurora_bridge", name="Aurora Bridge", zone="Skylight Summit", par=3,
         origin=[-165.0, SUMMIT, -262.0], yaw=0.0, W=26, L=64, cup=(0, -56), spans=[(-42, -16, "Aurora Gap (open sky)")],
         gimmick="Timed light bridge: an aurora ribbon bridge fades in solid, holds, then dims away; or take the fixed ice bridge the long way; misses respawn at the gap edge",
         family="timing / route choice", motion="appear-vanish toggle (fade with dwell)",
         landmark="Aurora ribbon pouring down from the sky to form the bridge"),
    dict(n=18, id="h18_halo_arch", name="Halo Arch", zone="Skylight Summit", par=4,
         origin=[-235.0, SUMMIT, -232.0], yaw=0.0, W=36, L=76, cup=(0, -68),
         gimmick="Finale: a ramp up onto a raised green under the Halo Arch, a translucent ice arch framing the aurora, with a crystal bank to read on the way",
         family="level change (finale)", motion=None,
         landmark="Halo Arch: a glowing ice arch over the final green, Starfrost Spire to the south-east"),
]
BY = {h["n"]: h for h in HOLES}
# Phase 2: hole-by-hole geometry exists (../holes.json, built by ../tools/build_holes.py). Take each hole's real cup position (local x, z)
# and par from it so the walkways start at the real cups. The concept pads stay the footprint every felt piece and rail must fit inside.
HOLES_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "holes.json")
HJ = {}
if os.path.exists(HOLES_JSON):
    for _h in json.load(open(HOLES_JSON))["holes"]:
        HJ[_h["number"]] = _h
        BY[_h["number"]]["cup"] = (round(_h["cup"]["position"][0], 2), round(_h["cup"]["position"][2], 2))
        BY[_h["number"]]["cup_y"] = _h["cup"]["position"][1]
        BY[_h["number"]]["par"] = _h["par"]
BEHIND = 9.0   # walk-in point behind the tee (local +z), outside the footprint (box ends at +6)


def place(n):
    return dict(origin=BY[n]["origin"], yaw_deg=BY[n]["yaw"])


def wpt(n, lx, lz, dy=0.0):
    return W.to_world(place(n), [lx, dy, lz])


def tier_dy(n, lz):
    for (_, z0, z1, dy) in BY[n].get("tiers", []):
        if z1 <= lz <= z0:
            return dy
    return 0.0


def cup(n):
    cx, cz = BY[n]["cup"]
    return wpt(n, cx, cz, BY[n].get("cup_y", tier_dy(n, cz)))


def tee(n):
    return wpt(n, 0, 0)


def behind(n):
    return wpt(n, 0, BEHIND)


def concept(h):
    w2 = h["W"] / 2
    tiers = h.get("tiers") or [("pad", 6, -h["L"], 0.0)]
    pads = [dict(id=t[0], x=[-w2, w2], z=[t[2], t[1]], y=t[3]) for t in tiers]
    spans = []
    for (a, b, what) in h.get("spans", []):
        spans.append(dict(z=[a, b], over=what,
                          player_guard=dict(kind="player-only barrier (CollisionGroup 'PlayerGuard': collides with players, not the ball)",
                                            height=4.0, where="both gap rims across the pad width + both sides of every ball bridge over the gap"),
                          player_deck=dict(side="right", width=4.0, rails="both", rail_height=3.5,
                                           note="railed walk-on ice deck beside the safe ball bridge so the player can follow the ball")))
    return dict(pads=pads, spans=spans, cup_local=[h["cup"][0], h.get("cup_y", tier_dy(h["n"], h["cup"][1])), h["cup"][1]], size=[h["W"], h["L"] + 6])


# ------------------------------------------------------------------ paths
MAX_RISE = 0.8
TREAD = 1.5
FLIGHT_MAX = 10
LANDING_LEN = 4.0
PASS = ("on_hole", "bridge", "lift", "gondola", "deck")


def expand(leg_pts, kinds):
    """leg_pts: [(x,y,z)...]; kinds per leg: 'on_hole'|'walk'|'stairs'|'bridge'|'lift'|'gondola' or (kind, name[, style])."""
    segs = []
    for (a, b, k) in zip(leg_pts[:-1], leg_pts[1:], kinds):
        name = style = None
        if isinstance(k, tuple):
            k, name, style = (k + (None,))[:3]
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
            if style:
                s["style"] = style
            if typ == "lift":
                s["rise"] = round(dy, 2)
            segs.append(s)
            continue
        n = max(1, math.ceil(abs(dy) / MAX_RISE - 1e-9))
        nf = math.ceil(n / FLIGHT_MAX)
        need = n * TREAD + (nf - 1) * LANDING_LEN
        tread = TREAD if L >= need else (L - (nf - 1) * LANDING_LEN) / n
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
            sd = dict(type="stairs", start=at(s_, y), end=at(e, y + k_ * rise), steps=k_, rise=round(rise, 3), tread=round(tread, 3))
            if name:
                sd["name"] = name
            segs.append(sd)
            y += k_ * rise
            s_ = e
            left -= k_
            if left:
                segs.append(dict(type="landing", start=at(s_, y), end=at(s_ + LANDING_LEN, y), grade=0.0))
                s_ += LANDING_LEN
        if L - s_ > 0.05:
            segs.append(dict(type="landing", start=at(s_, y), end=at(L, y), grade=0.0))
    return segs


def mkpath(pid, frm, to, pts, kinds, width=6.0, name="", note=""):
    segs = expand(pts, kinds)
    L3 = sum(math.dist(s["start"], s["end"]) for s in segs if s["type"] not in ("gondola", "lift"))
    return dict(id=pid, name=name, from_hole=frm, to_hole=to, width=width, segments=segs, length=round(L3, 1), note=note)


def P(x, y, z):
    return [float(x), float(y), float(z)]


SPAWN = P(-182, LANDING, 590)
paths = []
paths.append(mkpath("p_spawn_h1", None, 1, [SPAWN, P(-160, LANDING, 568), behind(1), tee(1)], ["walk", "walk", "on_hole"],
                    width=8.0, name="Quay Walk", note="Lantern Quay Plaza (spawn) to H1, lantern posts both sides, the Spire dead ahead"))
paths.append(mkpath("p_h1_h2", 1, 2, [cup(1), wpt(1, 0, -46), P(-136, LANDING, 488), behind(2), tee(2)],
                    ["on_hole", "walk", "walk", "on_hole"], name="Burrow Lane", note="Past the snowpuff rookery"))
paths.append(mkpath("p_h2_h3", 2, 3, [cup(2), P(-71, LANDING, 499), P(-56, LANDING, 494), behind(3), tee(3)],
                    ["on_hole", "walk", "walk", "on_hole"], name="Drift Path"))
paths.append(mkpath("p_h3_h4", 3, 4, [cup(3), wpt(3, 19, -62), P(44, LANDING, 438), P(96, LANDING, 438), P(104, LANDING, 438),
                                      P(164, LAGOON, 438), P(164, LAGOON, 474), P(172, LAGOON, 482), behind(4), tee(4)],
                    ["on_hole", "walk", ("bridge", "Glimmer Ice Bridge", "ice"), "walk", ("stairs", "Lantern Stair"), "walk", "walk", "walk", "on_hole"],
                    name="Glimmer Ice Bridge + Lantern Stair",
                    note="Off Glimmer Islet over a railed translucent ice bridge, then up the Lantern Stair (a lantern-lit rock spine, +24) onto the lagoon island"))
paths.append(mkpath("p_h4_h5", 4, 5, [cup(4), P(203, LAGOON, 420), behind(5), tee(5)],
                    ["on_hole", "walk", "on_hole"], name="Palm Step"))
paths.append(mkpath("p_h5_h6", 5, 6, [cup(5), P(263, cup(5)[1], 439), P(263, LAGOON, 447), P(280, LAGOON, 490), behind(6), tee(6)],
                    ["on_hole", "stairs", "walk", "walk", "on_hole"], name="Steam Walk", note="Down from the geyser green past Steamwhistle Lagoon"))
paths.append(mkpath("p_h6_h7", 6, 7, [cup(6), P(326, LAGOON, 426), P(340, LAGOON, 410), P(340, REEF, 384), P(352, REEF, 352), behind(7), tee(7)],
                    ["on_hole", "walk", ("lift", "Steam Lift"), "walk", "walk", "on_hole"], name="Steam Lift",
                    note="Brass steam-driven open cage (+28) up the cliff onto the reef island"))
paths.append(mkpath("p_h7_h8", 7, 8, [cup(7), P(384, REEF, 282), P(400, REEF, 312), behind(8), tee(8)],
                    ["on_hole", "walk", "walk", "on_hole"], name="Coral Walk"))
paths.append(mkpath("p_h8_h9", 8, 9, [cup(8), P(449, REEF, 254), P(458, REEF, 254), P(508, REEF, 254), P(520, REEF, 246), behind(9), tee(9)],
                    ["on_hole", "walk", ("bridge", "Coral Ice Bridge", "ice"), "walk", "walk", "on_hole"], name="Coral Ice Bridge",
                    note="Railed ice bridge out to the conch islet"))
paths.append(mkpath("p_h9_h10", 9, 10, [cup(9), wpt(9, 0, -78), P(535, REEF, 118), P(535, FLOE, 92), P(525, FLOE, 80), behind(10), tee(10)],
                    ["on_hole", "walk", ("lift", "Coral Lift"), "walk", "walk", "on_hole"], name="Coral Lift",
                    note="Open cage lift (+34) from the conch islet up to the Driftfloe Shelf"))
paths.append(mkpath("p_h10_h11", 10, 11, [cup(10), wpt(10, 0, -64), P(430, FLOE, 56), behind(11), tee(11)],
                    ["on_hole", "walk", "walk", "on_hole"], name="Floe Walk"))
paths.append(mkpath("p_h11_h12", 11, 12, [cup(11), wpt(11, 0, -62), P(392, FLOE, -48), behind(12), tee(12)],
                    ["on_hole", "walk", "walk", "on_hole"], name="Pond Path"))
paths.append(mkpath("p_h12_h13", 12, 13, [cup(12), wpt(12, 0, -60), P(290, FLOE, -60), P(264, ICEFALL, -60), P(250, ICEFALL, -80),
                                          P(160, ICEFALL, -180), P(138, ICEFALL, -206), behind(13), tee(13)],
                    ["on_hole", "walk", ("lift", "Icefall Lift"), "walk", ("bridge", "Aurora Skybridge", "aurora"), "walk", "walk", "on_hole"],
                    name="Icefall Lift + Aurora Skybridge",
                    note="Lift (+36) onto the Aurora Landing pinnacle, then the long railed Aurora Skybridge (glowing green/violet deck) to the Icefall Terraces"))
paths.append(mkpath("p_h13_h14", 13, 14, [cup(13), wpt(13, -21, -48), P(96, ICEFALL, -290), behind(14), tee(14)],
                    ["on_hole", "walk", "walk", "on_hole"], name="Carousel Walk"))
paths.append(mkpath("p_h14_h15", 14, 15, [cup(14), P(39, ICEFALL, -318), P(26, ICEFALL, -322), behind(15), tee(15)],
                    ["on_hole", "walk", "walk", "on_hole"], name="Icefall Rim"))
paths.append(mkpath("p_h15_h16", 15, 16, [cup(15), P(-4, cup(15)[1], -366), P(-12, ICEFALL, -366), P(-40, ICEFALL, -350), P(-66, SUMMIT, -350),
                                          P(-86, SUMMIT, -320), P(-92, SUMMIT, -290), behind(16), tee(16)],
                    ["on_hole", "stairs", "walk", ("lift", "Crystal Lift"), "walk", "walk", "walk", "on_hole"], name="Crystal Lift",
                    note="Up from the frozen-falls basin and the Crystal Lift (+40), an ice-crystal cage, onto Skylight Summit"))
paths.append(mkpath("p_h16_h17", 16, 17, [cup(16), P(-126, SUMMIT, -332), P(-134, SUMMIT, -300), P(-142, SUMMIT, -252), behind(17), tee(17)],
                    ["on_hole", "walk", "walk", "walk", "on_hole"], name="Moonwell Path"))
paths.append(mkpath("p_h17_h18", 17, 18, [cup(17), P(-184, SUMMIT, -318), P(-200, SUMMIT, -300), P(-204, SUMMIT, -218), behind(18), tee(18)],
                    ["on_hole", "walk", "walk", "walk", "on_hole"], name="Summit Walk"))
GONDOLA_TOP = P(-278, SUMMIT, -262)
GONDOLA_BOTTOM = P(-204, LANDING, 604)
paths.append(mkpath("p_h18_hub", 18, None, [cup(18), P(-259, SUMMIT, -300), P(-276, SUMMIT, -280), GONDOLA_TOP, GONDOLA_BOTTOM, P(-188, LANDING, 594)],
                    ["on_hole", "walk", "walk", ("gondola", "Snowpuff Sky Gondola"), "walk"], name="Snowpuff Sky Gondola",
                    note="From Skylight Point a slow enclosed lantern-lit gondola glides 162 studs down over the cloud sea back to Lantern Quay Plaza"))

# ------------------------------------------------------------------ teleport pads (zone hubs + rides)
teleports = [
    dict(id="tp_quay", name="Lantern Quay Plaza", pos=[-190.0, LANDING, 580.0], zone="Lanternfall Landing", hub=True),
    dict(id="tp_lagoons", name="Lantern Stair Top", pos=[152.0, LAGOON, 456.0], zone="Steamwhistle Lagoons", hub=True),
    dict(id="tp_reef", name="Steam Lift Top", pos=[330.0, REEF, 382.0], zone="Candyfrost Reef", hub=True),
    dict(id="tp_floe", name="Coral Lift Top", pos=[546.0, FLOE, 90.0], zone="Driftfloe Shelf", hub=True),
    dict(id="tp_landing", name="Aurora Landing", pos=[248.0, ICEFALL, -62.0], zone="Icefall Terraces", hub=False),
    dict(id="tp_icefall", name="Skybridge West", pos=[150.0, ICEFALL, -204.0], zone="Icefall Terraces", hub=True),
    dict(id="tp_summit", name="Crystal Lift Top", pos=[-70.0, SUMMIT, -362.0], zone="Skylight Summit", hub=True),
    dict(id="tp_skylight", name="Skylight Point", pos=[-286.0, SUMMIT, -284.0], zone="Skylight Summit", hub=False),
]

# ------------------------------------------------------------------ water: hot-spring lagoons + warm runoff falls
lakes = [
    dict(name="Steamwhistle Lagoon", kind="hot_spring", center=[232.0, 474.0], radii=[22.0, 13.0], level=LAGOON_LEVEL, depth=3.0,
         beach_width=3.0, beach_slope=0.3, bank_slope=1.0, bank_reach=8.0,
         note="Warm turquoise hot spring (Water colour #2FD6C8), steam particles; spills south over Steamwhistle Falls"),
    dict(name="Kettle Lagoon", kind="hot_spring", center=[348.0, 454.0], radii=[15.0, 24.0], level=LAGOON_LEVEL, depth=3.0,
         beach_width=3.0, beach_slope=0.3, bank_slope=1.0, bank_reach=8.0,
         note="Hot spring beside H6 with frosted palms; scenery only (H6's hazard pool is a holes.json element inside the pad)"),
]
RUNOFF = [(232, 487, LAGOON_LEVEL, 6), (232, 512, 82.4, 6), (232, 522, CLOUD_DECK, 6)]
streams = [dict(name="Steamwhistle Runoff", points=[dict(x=float(x), z=float(z), level=lv, width=float(w)) for (x, z, lv, w) in RUNOFF],
                depth=1.5, bank_slope=0.8, bank_reach=6.0,
                note="Warm runoff from Steamwhistle Lagoon to the island's south rim, then a steaming fall into the cloud sea")]
waterfalls = []
for i in range(len(RUNOFF) - 1):
    a, b = RUNOFF[i], RUNOFF[i + 1]
    if a[2] - b[2] >= 1.5:
        waterfalls.append(dict(name="Steamwhistle Falls", stream="Steamwhistle Runoff", frozen=False, top=[a[0], a[2], a[1]],
                               bottom=[b[0], b[2], b[1]], drop=round(a[2] - b[2], 2), width=float(min(a[3], b[3])),
                               note="Warm, steaming turquoise ribbon off the rim into the cloud deck (Beam + steam particles)"))
FROZEN_FALLS = [  # name, top [x, y, z], width, note
    ("Glimmer Icefall", [40.0, LANDING, 404.0], 10.0, "Off Glimmer Islet's north rim, beside H3's green"),
    ("Great Frozen Falls", [20.0, ICEFALL, -398.0], 26.0, "Hero icefall off the north rim of the Icefall Terraces, right beside H15"),
    ("Twin Icefalls west", [-34.0, ICEFALL, -392.0], 12.0, "Smaller icefall west of the Great Frozen Falls"),
    ("Summit Icefall", [-150.0, SUMMIT, -356.0], 14.0, "Off Skylight Summit's north rim below H17's green"),
    ("Reef Icefall", [575.0, REEF, 200.0], 10.0, "Off the conch islet's east rim"),
]
for name, top, wdt, note in FROZEN_FALLS:
    waterfalls.append(dict(name=name, stream=None, frozen=True, top=top, bottom=[top[0], CLOUD_DECK, top[2]], drop=round(top[1] - CLOUD_DECK, 1),
                           width=wdt, note=note + ". Frozen: translucent glowing ice mesh pouring over the edge into the clouds (no water)."))

# ------------------------------------------------------------------ islands (terrain regions)
WOB = [dict(amp=1.6, wx=37.0, wz=29.0, phase=[0.4, 1.3]), dict(amp=0.9, wx=13.0, wz=17.0, phase=[2.1, 0.2])]
lobes = []   # (height, shape, id, material_id or None)


def hole_lobes(h):
    """Box lobes round a footprint in the hole frame, split at spans so the gap stays open."""
    pl = place(h["n"])
    w2 = h["W"] / 2 + HOLE_MARGIN
    z_hi, z_lo = 6 + HOLE_MARGIN, -h["L"] - HOLE_MARGIN
    cuts = sorted(h.get("spans", []), key=lambda s: -s[1])
    pieces, top = [], z_hi
    for (a, b, _) in cuts:          # span (a < b): keep [b - 3, top] then continue below a + 3 (3 studs into the span so the
        pieces.append((b - 3, top))  # edge wobble can never pull the cliff back into the pad)
        top = a + 3
    pieces.append((z_lo, top))
    out = []
    for i, (z0, z1) in enumerate(pieces):
        c = W.to_world(pl, [0.0, 0.0, (z0 + z1) / 2])
        out.append((h["origin"][1] + min(dy for (_, _, _, dy) in h.get("tiers", [("", 0, 0, 0.0)])),
                    dict(type="box", center=[round(c[0], 2), round(c[2], 2)], size=[2 * w2, z1 - z0], yaw=h["yaw"]),
                    f"isle_h{h['n']:02d}_{i}"))
    return out


for h in HOLES:
    for (y, shp, iid) in hole_lobes(h):
        lobes.append((y, shp, iid, None))
# walk legs (graded walk/ramp/landing at a constant height) get capsule lobes so walkways have ground under them
for p in paths:
    for i, s in enumerate(p["segments"]):
        if s["type"] == "walk" and abs(s["start"][1] - s["end"][1]) < 1e-6:
            lobes.append((s["start"][1], dict(type="capsule", a=[s["start"][0], s["start"][2]], b=[s["end"][0], s["end"][2]], radius=9.0),
                          f"walk_{p['id']}_{i}", None))
for tp in teleports:
    lobes.append((tp["pos"][1], dict(type="circle", center=[tp["pos"][0], tp["pos"][2]], radius=11.0), f"hub_{tp['id']}", None))
EXTRA = [  # hand-placed island lobes: plazas, shelves and the bits that make islands read as islands
    (LANDING, dict(type="circle", center=[-190.0, 592.0], radius=28.0), "quay_plaza"),
    (LANDING, dict(type="capsule", a=[-200.0, 540.0], b=[-110.0, 520.0], radius=26.0), "landing_main_body"),
    (LANDING, dict(type="circle", center=[-96.0, 438.0], radius=22.0), "rookery_knoll"),
    (LAGOON, dict(type="circle", center=[232.0, 478.0], radius=36.0), "lagoon_basin_steamwhistle"),
    (LAGOON, dict(type="circle", center=[348.0, 452.0], radius=36.0), "lagoon_basin_kettle"),
    (LAGOON, dict(type="circle", center=[262.0, 380.0], radius=26.0), "geyser_flat"),
    (REEF, dict(type="circle", center=[400.0, 240.0], radius=30.0), "reef_garden"),
    (FLOE, dict(type="circle", center=[456.0, 6.0], radius=40.0), "floe_pond_shelf"),
    (FLOE, dict(type="circle", center=[340.0, -10.0], radius=26.0), "floe_hut_flat"),
    (ICEFALL, dict(type="circle", center=[256.0, -70.0], radius=16.0), "aurora_landing_pinnacle"),
    (ICEFALL, dict(type="circle", center=[60.0, -360.0], radius=36.0), "icefall_north_shelf"),
    (ICEFALL, dict(type="circle", center=[10.0, -392.0], radius=18.0), "great_falls_lip"),
    (SUMMIT, dict(type="circle", center=[-150.0, -350.0], radius=18.0), "summit_icefall_lip"),
    (SUMMIT, dict(type="circle", center=[-300.0, -250.0], radius=24.0), "skylight_point"),
    (SPIRE_ISLE, dict(type="circle", center=[SPIRE["x"], SPIRE["z"]], radius=62.0), "spire_isle"),
    # zone bodies: fatten each island so it reads as a real island, not a strip (gaps, islets and the pinnacle stay separate)
    (LANDING, dict(type="capsule", a=[-170.0, 530.0], b=[-70.0, 485.0], radius=34.0), "landing_body"),
    (LANDING, dict(type="circle", center=[-120.0, 600.0], radius=30.0), "landing_south_cove"),
    (LAGOON, dict(type="capsule", a=[200.0, 445.0], b=[320.0, 445.0], radius=48.0), "lagoon_body"),
    (REEF, dict(type="capsule", a=[365.0, 310.0], b=[425.0, 265.0], radius=42.0), "reef_body"),
    (FLOE, dict(type="capsule", a=[400.0, -40.0], b=[470.0, 40.0], radius=46.0), "floe_body"),
    (ICEFALL, dict(type="capsule", a=[110.0, -270.0], b=[40.0, -330.0], radius=40.0), "icefall_body"),
    (SUMMIT, dict(type="circle", center=[-92.0, -318.0], radius=30.0), "summit_east_body"),
    (SUMMIT, dict(type="circle", center=[-268.0, -302.0], radius=22.0), "summit_west_body"),
]
for (y, shp, iid) in EXTRA:
    lobes.append((y, shp, iid, None))
lobes.sort(key=lambda t: t[0])
regions = [dict(id=iid, op="set", height=y, falloff=6.0, edge="cliff", shape=shp, wobble=WOB, material="snow-capped rock island top",
                **({"material_id": mid} if mid else {})) for (y, shp, iid, mid) in lobes]
# frozen ponds / glacier rims (set slightly below the island so they read as ice sheets)
regions += [
    dict(id="floe_pond", op="set", height=FLOE - 0.4, falloff=2.0, shape=dict(type="circle", center=[462.0, 8.0], radius=17.0),
         material="frozen pond (ice sheet), drifting toy floes as scenery", material_id="Ice"),
    dict(id="icefall_glacier_rim", op="set", height=ICEFALL - 0.3, falloff=2.0, shape=dict(type="capsule", a=[-30.0, -386.0], b=[34.0, -388.0], radius=7.0),
         material="glacier lip where the frozen falls pour over", material_id="Glacier"),
]

terrain = dict(
    method=("Deterministic heightfield h(x,z) (tools/worldlib.py height_at), evaluated in order: "
            "(1) base: the cloud floor, h = base.height (0). "
            "(2) regions in list order (islands sorted low -> high so higher islands sit on lower ones where they touch). 'set': "
            "d = distance outside the shape (0 inside; shape 'union'/'box'/'capsule'/'circle'), plus the edge wobble "
            "sum(amp*sin(2*pi*x/wx+px)*sin(2*pi*z/wz+pz)) clamped at 0; w = 1-smoothstep(d/falloff); h += (height-h)*w. "
            "'hill': h += peak*cos^2(pi/2*q), q = elliptical radius/radii < 1 (snowdrifts and crags on island tops). "
            "(3) detail_noise where h > detail_min_y (island tops only). (4) pads: every concept pad box flattened to its y, blended back "
            "over `falloff` beyond `margin`; along a declared span strip the blend may never raise the ground (the gap stays open). "
            "(5) paths: within width/2+1 of a graded segment h = profile (stairs: profile - stair_bed_drop), blended over `shoulder`; "
            "on_hole/bridge/lift/gondola don't grade. (5a) flats: teleport/viewpoint discs flattened to y within radius, blended over falloff. (5b) pad clamp: pad boxes (outside spans) = pad y. (6) water: h = min(h, lagoon/runoff "
            "carve profile), banks only out to bank_reach. smoothstep(t) = t^2(3-2t), t clamped to [0,1]. "
            "VOID: h < void.terrain_fill_min_y means no terrain at all (air over the cloud deck)."),
    base=dict(height=CLOUD_FLOOR, noise=[],
              detail_noise=[dict(amp=0.35, wx=37.0, wz=-53.0, phase=[0.5, 1.7]), dict(amp=0.45, wx=113.0, wz=89.0, phase=[2.4, 0.2])]),
    detail_min_y=FILL_MIN,
    regions=regions,
    rim=dict(height=0.0, note="No rim: the archipelago is open to the horizon; far island rings and the cloud sea hide the terrain edge"),
    path_grading=dict(shoulder=4.0, stair_bed_drop=0.6),
    pads=dict(rule="Concept pads are flat at their y (felt is built on top later). margin 3 then blend over falloff.", margin=3.0, falloff=8.0),
    flats=[dict(id=tp["id"], center=[tp["pos"][0], tp["pos"][2]], y=tp["pos"][1], radius=5.0, falloff=4.0) for tp in teleports],
)

# ------------------------------------------------------------------ assemble the world (needed by height_at below)
SURROUND = {
    1: "Lantern Quay on the lowest island (y 60): brass lanterns on driftwood posts, snowpuff figures, the cloud sea 24 studs below the rim; Starfrost Spire dead ahead",
    2: "Snowpuff rookery under a long snowdrift; the Spire rises over the drift to the north-east",
    3: "Plays north-east off the main island over the 26-stud Glimmer Gap onto Glimmer Islet; the Glimmer Icefall pours off the islet",
    4: "Lagoon island (y 84): frosted palms, steam from two turquoise hot springs, the Lantern Stair below to the west",
    5: "Beside Steamwhistle Geyser; the green sits 4 studs up on a basalt shelf",
    6: "Edge of Kettle Lagoon; the reef island's cliffs rise 28 studs to the north",
    7: "Reef island (y 112): coral-ice fans in candy colours, the lagoon island below to the south",
    8: "Coral garden in the middle of the reef island; the conch islet floats to the east",
    9: "Conch islet, reached over the Coral Ice Bridge; the Driftfloe Shelf cliff rises 34 studs to the north",
    10: "Driftfloe Shelf (y 146), east end; bobsled hut at the tee, big sky to the east",
    11: "Floe Pond beside the green; snowpuff ice-fishing hut",
    12: "West end of the shelf; the Aurora Landing pinnacle and the Skybridge ahead to the west",
    13: "Icefall Terraces (y 182), arrived over the Aurora Skybridge; carousel canopy over the green",
    14: "Timber bell gantry on the terrace; Spire to the south",
    15: "North rim beside the Great Frozen Falls pouring into the cloud sea",
    16: "Skylight Summit (y 222), the highest island; moonstone well",
    17: "Plays north over the Aurora Gap; aurora ribbon bridge, Summit Icefall below the green",
    18: "Finale under the Halo Arch; Spire to the south-east, every earlier island spread below",
}
holes_out = []
for h in HOLES:
    n = h["n"]
    hj = dict(number=n, id=h["id"], name=h["name"], par=h["par"], zone=h["zone"], status="specced" if n in HJ else "concept_footprint",
              holes_json=(f"holes.json holes[{n - 1}] ({HJ[n]['id']})" if n in HJ else None),
              gimmick=h["gimmick"], gimmick_family=h["family"], motion_type=h["motion"], landmark=h["landmark"],
              placement=dict(origin=[round(v, 3) for v in h["origin"]], yaw_deg=h["yaw"]),
              play_bearing_deg=round(W.bearing(*W.play_dir(h["yaw"])), 1),
              concept=concept(h), tee_world=[round(v, 2) for v in tee(n)], cup_world_approx=[round(v, 2) for v in cup(n)],
              tee_teleport=dict(pos=[round(v, 2) for v in behind(n)], radius=2.0, note="standard next-tee teleport arrival pad, 3 studs behind the tee box"),
              surroundings=SURROUND[n], enclosed=False)
    pw = W.pads_world(hj)
    xs = [c[0] for p in pw for c in p["corners"]]
    zs = [c[1] for p in pw for c in p["corners"]]
    hj["footprint_bbox"] = dict(x=[round(min(xs), 1), round(max(xs), 1)], z=[round(min(zs), 1), round(max(zs), 1)])
    holes_out.append(hj)

b = dict(x=[-660.0, 660.0], z=[-660.0, 660.0])
world = dict(
    name="Aurora Archipelago - world layout",
    version="0.1-concept",
    course_number=3,
    units="studs (1 stud = 0.3 m), +Y up, map view +X east/right, -Z north/up. Same axes as Lantern Grove / Sugarloaf Canyon.",
    bounds=dict(x=b["x"], z=b["z"], size=[b["x"][1] - b["x"][0], b["z"][1] - b["z"][0]], y_range=[0.0, 300.0],
                note="Terrain extent (1320 x 1320). Far island rings, the cloud sea and the sky sit outside it."),
    placement_convention=dict(
        apply=("For every (future) holes.json element of hole N: rotate its LOCAL x/z about +Y by placement.yaw_deg, then translate by "
               "placement.origin. x' = lx*cos(yaw) + lz*sin(yaw) + origin.x ; z' = -lx*sin(yaw) + lz*cos(yaw) + origin.z ; y' = ly + origin.y. "
               "Piece yaw_world = piece.yaw + yaw_deg. Positive yaw = counter-clockwise in the map view: yaw 0 plays north, 90 west, "
               "180 south, -90 east. Check: yaw 90 turns local -Z to world -X. The local origin is the tee; play is toward local -Z."),
        roblox="holeRoot = CFrame.new(origin) * CFrame.Angles(0, math.rad(yaw_deg), 0); partCFrame = holeRoot * localCFrame. Axes rotate only.",
        concept_footprint=("Until holes.json exists each hole is concept.pads: flat boxes in the local frame (x range, z range, y offset "
                           "from origin.y). The future hole geometry (felt + rails + props within 2 studs) must stay inside them. "
                           "concept.spans = local z ranges where the hole bridges open sky; the ground is not flattened there."),
        legacy=("holes.json exists (Phase 2): it copies these placements into world_offset/world_yaw; world.json placement supersedes them. "
                "Walkways start at the real holes.json cups."),
    ),
    moon=dict(bearing_deg=220.0, elevation_deg=14.0, kind="low moon + twilight glow (the brightest light source)",
              note="Night-ish lighting. No tee plays within 45 deg of bearing 220 (validated). The moon and the lilac twilight band are the "
                   "back/side view from tees and the set-piece view from greens, the Skybridge and Skylight Point."),
    aurora=dict(bearing_range_deg=[300.0, 60.0], elevation_range_deg=[25.0, 75.0], colors=["#5CFFB0", "#3DE2C8", "#B07CFF", "#FF7AD9"],
                note="Animated ribbon meshes/Beams high in the north sky; most tees play north into them. They light nothing (emissive only)."),
    spawn=dict(pos=SPAWN, look_at=[round(v, 2) for v in tee(1)], note="SpawnLocation on Lantern Quay Plaza facing north up H1; Starfrost Spire on the skyline"),
    void=dict(cloud_floor_y=CLOUD_FLOOR, terrain_fill_min_y=FILL_MIN, cloud_deck_y=CLOUD_DECK, respawn_plane_y=RESPAWN_Y, walkable=False,
              material="Air (no voxels); the cloud deck is a soft emissive cloud mesh + particles at y 36",
              player_respawn="any character below y 40 is faded out and placed on the last tee-teleport pad it used (no fall animation)",
              ball_respawn="a ball below its felt by > 6 studs or below y 40 resets per the hole's hazard rule (+1 stroke)",
              note="Heightfield values below 30 are the cloud floor: build NO terrain there. Island cliffs disappear into the cloud deck at y 36; "
                   "the builder hangs tapering underside rock meshes (backdrop island_underside) below each island for the floating look."),
    zones=[
        dict(name="Lanternfall Landing", holes=[1, 2, 3], ground_y=LANDING, note="Lowest island: harbour quay, snowpuff rookery, Glimmer Islet. Teaches bank, tunnels, risk/safe bridge"),
        dict(name="Steamwhistle Lagoons", holes=[4, 5, 6], ground_y=LAGOON, note="Geothermal island: hot springs, frosted palms, geyser. Ice felt, first mover, side slope"),
        dict(name="Candyfrost Reef", holes=[7, 8, 9], ground_y=REEF, note="Coral-ice reef island + conch islet. Moguls, bumpers, teleport"),
        dict(name="Driftfloe Shelf", holes=[10, 11, 12], ground_y=FLOE, note="Frozen shelf with Floe Pond. Half-pipe, floe slider, paddle wheel"),
        dict(name="Icefall Terraces", holes=[13, 14, 15], ground_y=ICEFALL, note="Over the Aurora Skybridge; frozen falls. Carousel, bell pendulum, icefall drop"),
        dict(name="Skylight Summit", holes=[16, 17, 18], ground_y=SUMMIT, note="Showpiece: moonwell, timed aurora bridge, Halo Arch finale, gondola home"),
    ],
    holes=holes_out,
    terrain=terrain,
    streams=streams,
    lakes=lakes,
    waterfalls=waterfalls,
    paths=paths,
    path_rules=dict(max_ramp_grade=0.10, max_step_rise=1.0, design_step_rise=MAX_RISE, tread=TREAD, max_steps_per_flight=FLIGHT_MAX,
                    landing_length=LANDING_LEN, min_width=5.0, max_lift_rise=60.0, max_lift_offset=30.0, rail_drop=4.0, rail_reach=5.5,
                    railing_height=3.5, head_clearance=8.0,
                    segment_types="on_hole (across the hole's own area), walk (<1% grade), ramp (<=10%), stairs (flight: steps x rise, tread), "
                                  "landing (flat), bridge (railed, style ice|aurora; <=5%), lift (vertical cage: start/end = boarding points), gondola (cable car)",
                    rails="seg.rails = ['left'|'right'...]: sides that need a railing because the ground drops > rail_drop studs within "
                          "rail_reach (5.5) studs of the walkway edge (stricter than the recipe's 2.5; left/right relative to walking direction). Bridges: both, always. Railings are "
                          "chunky snow-capped timber, 3.5 studs (1.05 m) high, with a solid lower board so nothing slips under."),
    teleport_points=teleports,
    heightmap=dict(file="heightmap.png", stud_per_px=1.0, y_min=0.0, y_max=300.0, bit_depth=16,
                   mapping="pixel (i=col, j=row) centre -> x = bounds.x[0] + (i+0.5), z = bounds.z[0] + (j+0.5) (row 0 = north edge); "
                           "y = gray/65535*300; y < 30 = void (no terrain)"),
)

# ------------------------------------------------------------------ rails at drops (needs the heightfield)
RAIL_DROP = 4.0
RAIL_REACH = 5.5   # stricter than the recipe's 2.5: any cliff within 5.5 studs of a walkway edge gets a railing


def RAIL_OFFSETS(width):
    return [width / 2 + o for o in (1.0, 2.5, 4.0, RAIL_REACH)]


def seg_rails(seg, width):
    if seg["type"] in ("bridge", "deck"):
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
        for off in RAIL_OFFSETS(width):
            h = W.height_at(world, px + sg * lx * off, pz + sg * lz * off)
            if (py - h > RAIL_DROP).any():
                out.append(side)
                break
    return out


for p in world["paths"]:
    for s in p["segments"]:
        r = seg_rails(s, p["width"])
        if r:
            s["rails"] = r
            s["railing_height"] = 3.5


def hgt(x, z):
    return round(float(W.height_at(world, np.array([float(x)]), np.array([float(z)]))[0]), 1)


class FastH:
    """Bilinear lookup on a 2-stud grid of the current heightfield (scenery placement only; exact height_at elsewhere)."""
    def __init__(self):
        self.xs, self.zs, X, Z = W.grid(world, 2.0)
        self.H = W.height_at(world, X, Z)

    def __call__(self, x, z):
        x = np.atleast_1d(np.asarray(x, float))
        z = np.atleast_1d(np.asarray(z, float))
        fi = np.clip((x - self.xs[0]) / 2.0, 0, len(self.xs) - 1.001)
        fj = np.clip((z - self.zs[0]) / 2.0, 0, len(self.zs) - 1.001)
        i, j = fi.astype(int), fj.astype(int)
        ti, tj = fi - i, fj - j
        H = self.H
        return (H[j, i] * (1 - ti) * (1 - tj) + H[j, i + 1] * ti * (1 - tj) + H[j + 1, i] * (1 - ti) * tj + H[j + 1, i + 1] * ti * tj)


def drop_ring(x, z, y, r):
    """Max drop below y on a ring of radius r (16 samples)."""
    th = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    return float((y - W.height_at(world, x + r * np.cos(th), z + r * np.sin(th))).max())


for tp in teleports:   # pads near a cliff get a parapet on the drop side
    tp["size"] = [4.0, 0.1, 4.0]
    tp["parapet"] = drop_ring(tp["pos"][0], tp["pos"][2], tp["pos"][1], 2.0 + 2.5) > RAIL_DROP

# ------------------------------------------------------------------ lifts / gondola
lifts = []
for p in paths:
    for s in p["segments"]:
        if s["type"] in ("lift", "gondola"):
            lo, hi = (s["start"], s["end"]) if s["start"][1] < s["end"][1] else (s["end"], s["start"])
            L2 = math.hypot(hi[0] - lo[0], hi[2] - lo[2])
            d = dict(name=s.get("name"), type=s["type"], path=p["id"], bottom=lo, top=hi, rise=round(hi[1] - lo[1], 1),
                     horizontal=round(L2, 1), railed=True, teleport_alternative=True, accel_jolts=False)
            if s["type"] == "lift":
                d.update(speed_studs_s=3.0, ride_s=round((hi[1] - lo[1]) / 3.0, 1), cage="open-sided cage, 10 x 10 floor, 3.5-stud railings all round, solid floor",
                         note="Constant 3 studs/s (0.9 m/s), eased 1 s start/stop, the player stands still and sees the horizon; "
                              "short railed gangways from each boarding point to the shaft. 'Teleport instead' pads at both ends.")
            else:
                d.update(speed_studs_s=5.0, ride_s=round(math.dist(lo, hi) / 5.0, 1), cabin="enclosed seated lantern cabin, glazed, 6 x 6",
                         cable_height_above_station=16.0,
                         note="Seated enclosed cabin at a constant 5 studs/s along a straight cable; skippable by teleport at both stations.")
            lifts.append(d)

# ------------------------------------------------------------------ POIs
pois = [
    dict(id="lantern_quay_plaza", name="Lantern Quay Plaza", pos=SPAWN, radius=14.0, kind="plaza",
         note="Spawn + hub: course board, gondola arrival, teleport kiosk, cosy brass-lantern boathouse clubhouse"),
    dict(id="snowpuff_rookery", name="Snowpuff Rookery", pos=[-96.0, LANDING, 438.0], kind="landmark", note="Round penguin-puffin snowpuff figures and their burrows"),
    dict(id="glimmer_islet", name="Glimmer Islet", pos=[8.0, LANDING, 418.0], kind="landmark", note="H3's green island with a crystal cluster and the Glimmer Icefall"),
    dict(id="steamwhistle_geyser", name="Steamwhistle Geyser", pos=[262.0, LAGOON, 380.0], kind="landmark",
         note="Basalt cone; a steam column puffs to 60 studs every 20 s (visual only, no collision), whistles like a kettle"),
    dict(id="kettle_lagoon", name="Kettle Lagoon", pos=[348.0, LAGOON, 454.0], kind="landmark", note="Turquoise hot spring with frosted palms"),
    dict(id="reef_garden", name="Candyfrost Coral Garden", pos=[400.0, REEF, 240.0], kind="decor", note="Pink, tangerine and mint coral-ice branches"),
    dict(id="floe_pond", name="Floe Pond", pos=[462.0, FLOE, 8.0], kind="landmark", note="Frozen pond with toy ice floes and a snowpuff ice-fishing hut"),
    dict(id="aurora_landing", name="Aurora Landing", pos=[256.0, ICEFALL, -70.0], kind="viewpoint", note="Railed pinnacle top at the Icefall Lift; start of the Aurora Skybridge"),
    dict(id="great_frozen_falls", name="Great Frozen Falls", pos=[20.0, ICEFALL, -392.0], kind="landmark", note="Hero icefall off the north rim"),
    dict(id="starfrost_spire", name="Starfrost Spire", pos=[SPIRE["x"], SPIRE_ISLE, SPIRE["z"]], kind="landmark",
         note=f"Giant floating aurora-crystal spire on Spire Isle, base y {SPIRE_ISLE:.0f}, tip y {SPIRE_TOP:.0f}; skyline anchor"),
    dict(id="skylight_point", name="Skylight Point", pos=[-290.0, SUMMIT, -258.0], radius=8.0, kind="viewpoint", note="Gondola top station; course finish board; moon view"),
    dict(id="halo_arch", name="Halo Arch", pos=W.to_world(place(18), [0.0, 0.0, -60.0]), kind="landmark", note="Glowing ice arch over H18's green"),
]
for p_ in pois:
    p_["pos"] = [round(float(v), 2) for v in p_["pos"]]
    if p_["kind"] == "viewpoint":
        p_["parapet"] = drop_ring(p_["pos"][0], p_["pos"][2], p_["pos"][1], 8.0) > RAIL_DROP or p_["id"] == "aurora_landing"
        if p_["id"] == "aurora_landing":
            p_["note"] += ". Small pinnacle: full perimeter parapet (3.5 high) round its rim regardless of the drop test"

# ------------------------------------------------------------------ movers plan (one motion type each)
movers_plan = [dict(hole=h["n"], name=h["name"], motion_type=h["motion"], gimmick=h["gimmick"]) for h in HOLES if h["motion"]]

# ------------------------------------------------------------------ backdrop + scenery
rnd = random.Random(31)
pieces = []
SPIRE_PIECE = dict(id="starfrost_spire", kind="hero_landmark", pos=[SPIRE["x"], SPIRE_ISLE, SPIRE["z"]], size=[64, SPIRE["height"], 64], yaw_deg=0,
                   note="Faceted aurora-crystal spire, mint-to-violet inner glow, slowly turning crystal shards orbiting it at r 50-90; "
                        f"tip y {SPIRE_TOP:.0f}. Aurora ribbons appear to stream off its tip.")
pieces.append(SPIRE_PIECE)
halo = W.to_world(place(18), [0.0, 0.0, -60.0])
named = [
    ("halo_arch", "hero_landmark", [halo[0], SUMMIT, halo[2]], [46, 34, 8], 0.0, 18.0,
     "Translucent glowing ice arch spanning H18's green across the hole (legs outside the footprint x +-23); clear opening 18 high x 40 wide"),
    ("steamwhistle_geyser", "set_piece", [262.0, LAGOON, 380.0], [14, 10, 14], 0.0, None, "Basalt geyser cone; steam column visual only"),
    ("spire_isle_underside", "island_underside", [SPIRE["x"], CLOUD_DECK, SPIRE["z"]], [124, 60, 124], 0.0, None, "Tapering rock root under Spire Isle, wrapped in glowing crystal veins"),
    ("gondola_top_station", "structure", [GONDOLA_TOP[0] - 6, SUMMIT, GONDOLA_TOP[2]], [12, 12, 12], 0.0, 9.0, "Snowpuff Sky Gondola top station (Skylight Point), lantern roof; walk-through, roof 9+ clear"),
    ("gondola_bottom_station", "structure", [GONDOLA_BOTTOM[0], LANDING, GONDOLA_BOTTOM[2] + 4], [12, 12, 12], 0.0, 9.0, "Gondola bottom station on Lantern Quay Plaza; walk-through"),
    ("moon_disc", "sky", [round(2600 * math.sin(math.radians(220)), 1), round(2600 * math.tan(math.radians(14)), 1), round(-2600 * math.cos(math.radians(220)), 1)],
     [300, 300, 1], 0.0, None, "Big soft moon at bearing 220, elevation 14, with a lilac twilight band along the SW horizon"),
    ("aurora_ribbons", "sky", [0, 900, -1600], [2600, 500, 200], 0.0, None, "5 animated aurora curtains, mint #5CFFB0 to violet #B07CFF, bearings 300-60, elevations 25-75"),
    ("star_field", "sky", [0, 2000, 0], [5000, 1, 5000], 0.0, None, "Skybox stars, denser to the north"),
    ("cloud_sea", "cloud", [0, CLOUD_DECK, 0], [5200, 8, 5200], 0.0, None, "Soft lilac-white cloud deck to the horizon (emissive underlight), slow drifting puffs"),
]
for (i_, k_, pos_, size_, yaw_, clear_, note_) in named:
    d = dict(id=i_, kind=k_, pos=[float(v) for v in pos_], size=size_, yaw_deg=yaw_, note=note_)
    if clear_ is not None:
        d["clear_height"] = clear_
    pieces.append(d)
for l in lifts:  # lift shafts (the ride itself; walk-through)
    if l["type"] == "lift":
        mx, mz = (l["bottom"][0] + l["top"][0]) / 2, (l["bottom"][2] + l["top"][2]) / 2
        pieces.append(dict(id="shaft_" + l["name"].lower().replace(" ", "_"), kind="lift_shaft", pos=[mx, l["bottom"][1], mz],
                           size=[10, l["rise"] + 12, 10], yaw_deg=0, walk_through=True,
                           note=f"{l['name']}: cage shaft against the cliff, railed gangways to both boarding points"))
# island undersides: one per island cluster (zone), hung below the cliff into the cloud deck
for zn, (cx, cz, r, y) in {"Lanternfall Landing": (-120, 510, 110, LANDING), "Steamwhistle Lagoons": (250, 440, 90, LAGOON),
                           "Candyfrost Reef": (400, 290, 70, REEF), "Conch islet": (535, 190, 45, REEF), "Driftfloe Shelf": (430, 10, 90, FLOE),
                           "Icefall Terraces": (70, -310, 80, ICEFALL), "Skylight Summit": (-170, -300, 95, SUMMIT), "Glimmer Islet": (10, 418, 32, LANDING)}.items():
    pieces.append(dict(id="underside_" + zn.lower().replace(" ", "_"), kind="island_underside", pos=[cx, CLOUD_DECK, cz], size=[2 * r, round(y - CLOUD_DECK - 4), 2 * r],
                       yaw_deg=0, below_terrain=True, note=f"Tapering snow-streaked rock root under {zn}; fitted inside the cliff outline, top 4 below the island top; tip dips into the cloud deck"))
# far island rings + cloud rings
for i in range(16):
    ang = i * 22.5 + rnd.uniform(-7, 7)
    r = rnd.uniform(760, 960)
    a = math.radians(ang)
    pieces.append(dict(id=f"far_isle_{i+1:02d}", kind="far_island", pos=[round(r * math.cos(a)), round(rnd.uniform(60, 260)), round(r * math.sin(a))],
                       size=[round(rnd.uniform(70, 160)), round(rnd.uniform(60, 140)), round(rnd.uniform(60, 140))], yaw_deg=round(rnd.uniform(0, 360)),
                       note="Floating snow-capped island with pines, a few with a frozen waterfall or a lantern hut; hazed lilac-blue"))
for i in range(12):
    ang = i * 30 + rnd.uniform(-10, 10)
    r = rnd.uniform(1150, 1600)
    a = math.radians(ang)
    pieces.append(dict(id=f"far_peak_{i+1:02d}", kind="far_silhouette", pos=[round(r * math.cos(a)), 0, round(r * math.sin(a))],
                       size=[round(rnd.uniform(300, 600)), round(rnd.uniform(200, 420)), round(rnd.uniform(200, 400))], yaw_deg=round(-ang + 90, 1),
                       note="Distant snowy island-mountain silhouette rising out of the cloud sea; impostor card, deep violet-blue with height haze"))
for i in range(3):
    pieces.append(dict(id=f"cloud_ring_{i+1}", kind="cloud_ring", pos=[0, CLOUD_DECK + 10 + 18 * i, 0], size=[2 * (700 + 350 * i), 30, 2 * (700 + 350 * i)],
                       yaw_deg=0, note="Ring of billowing cloud banks (card clusters) that softens the horizon"))
pieces.append(dict(id="ice_arch_isle", kind="sister_landmark", pos=[-560.0, 140.0, 300.0], size=[90, 110, 40], yaw_deg=40,
                   note="Sister landmark on the SW horizon: a floating island pierced by a natural ice arch, lit by the moon behind it"))
pieces.append(dict(id="sky_lanterns", kind="sky", pos=[0, 260, 0], size=[6, 8, 6], yaw_deg=0,
                   note="12 warm paper sky-lanterns drifting slowly on loops r 300-700, y 240-380 (never over play below y 240)"))


def clear_of_play(x, z, r, gap=6.0):
    """True if a scenery piece of radius r at (x,z) keeps >= gap studs from every footprint and walkway (and gap+4 from the walkway edge)."""
    for h in world["holes"]:
        for p in W.pads_world(h):
            if float(W.rect_dist(np.array(x), np.array(z), p["cx"], p["cz"], p["sx"], p["sz"], p["yaw"])) < r + gap:
                return False
    for p in world["paths"]:
        for s in p["segments"]:
            if s["type"] == "gondola":
                continue
            d, _ = W.seg_dist(np.array(x), np.array(z), (s["start"][0], s["start"][2]), (s["end"][0], s["end"][2]))
            if float(d) < r + p["width"] / 2 + 4:
                return False
    for tp in teleports:
        if math.hypot(x - tp["pos"][0], z - tp["pos"][2]) < r + 6:
            return False
    return True


# --- decorative floating islets in the gaps (terrain), kept off play, walkways, the gondola and every tee->Spire sightline
TEES = [(h["tee_world"][0], h["tee_world"][1] + 5.5, h["tee_world"][2]) for h in world["holes"]]


def blocks_spire(x, z, r, top):
    for (ex, ey, ez) in TEES:
        for ty in (SPIRE_TOP, SPIRE_ISLE + 120):
            dx, dz = SPIRE["x"] - ex, SPIRE["z"] - ez
            L2 = dx * dx + dz * dz
            t = max(0.0, min(1.0, ((x - ex) * dx + (z - ez) * dz) / L2))
            px, pz = ex + t * dx, ez + t * dz
            ly = ey + (ty - ey) * t
            if math.hypot(x - px, z - pz) < r + 14 and ly < top + 10:
                return True
    return False


def near_gondola(x, z, r):
    d, _ = W.seg_dist(np.array(x), np.array(z), (GONDOLA_TOP[0], GONDOLA_TOP[2]), (GONDOLA_BOTTOM[0], GONDOLA_BOTTOM[2]))
    return float(d) < r + 30


FH = FastH()
islets = []
tries = 0
while len(islets) < 16 and tries < 6000:
    tries += 1
    x, z = rnd.uniform(-600, 600), rnd.uniform(-600, 600)
    r = rnd.uniform(12, 34)
    top = rnd.choice([rnd.uniform(48, 80), rnd.uniform(90, 160), rnd.uniform(160, 250)])
    th = np.linspace(0, 2 * np.pi, 16, endpoint=False)
    if FH(x + (r + 20) * np.cos(th), z + (r + 20) * np.sin(th)).max() > FILL_MIN or float(FH(x, z)[0]) > FILL_MIN:
        continue
    if not clear_of_play(x, z, r + 24, gap=10) or near_gondola(x, z, r) or blocks_spire(x, z, r, top):
        continue
    if any(math.hypot(x - ix, z - iz) < r + ir + 24 for (ix, iz, ir, _) in islets) or math.hypot(x - SPIRE["x"], z - SPIRE["z"]) < r + 100:
        continue
    islets.append((x, z, r, top))
for i, (x, z, r, top) in enumerate(islets):
    world["terrain"]["regions"].append(dict(id=f"islet_{i+1:02d}", op="set", height=round(top, 1), falloff=5.0, edge="cliff",
                                            shape=dict(type="circle", center=[round(x, 1), round(z, 1)], radius=round(r, 1)), wobble=WOB,
                                            material="decorative floating islet (not reachable): snow, 1-4 pines, a crystal or a lantern hut"))
    pieces.append(dict(id=f"underside_islet_{i+1:02d}", kind="island_underside", pos=[round(x, 1), CLOUD_DECK, round(z, 1)],
                       size=[round(2 * r), round(top - CLOUD_DECK - 3), round(2 * r)], yaw_deg=0, below_terrain=True, note="Islet root, fitted inside the islet's cliff outline"))

# --- snowdrifts and crags on island tops (hills), off play and off every tee->Spire sightline
FH = FastH()
hills = []
tries = 0
while len(hills) < 26 and tries < 8000:
    tries += 1
    x, z = rnd.uniform(-600, 600), rnd.uniform(-600, 600)
    hy = float(FH(x, z)[0])
    if hy < LANDING - 0.5:
        continue
    r = rnd.uniform(7, 16)
    peak = rnd.uniform(4, 9) if rnd.random() < 0.6 else rnd.uniform(12, 26)
    # whole hill on the island top, clear of play
    th = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    ring = FH(x + (r + 4) * np.cos(th), z + (r + 4) * np.sin(th))
    if near_gondola(x, z, r) or np.abs(ring - hy).max() > 1.6 or not clear_of_play(x, z, r, gap=4) or blocks_spire(x, z, r, hy + peak):
        continue
    if any(math.hypot(x - hx, z - hz) < r + hr + 4 for (hx, hz, hr, _) in hills):
        continue
    hills.append((x, z, r, peak))
for i, (x, z, r, peak) in enumerate(hills):
    world["terrain"]["regions"].append(dict(id=f"drift_{i+1:02d}", op="hill", center=[round(x, 1), round(z, 1)], radius=round(r, 1), peak=round(peak, 1),
                                            material="snowdrift" if peak < 10 else "snow-capped rock crag"))

# --- small scenery (decoration only, no collision): pines, crystals, frosted palms, coral-ice, snowpuffs
FH = FastH()
WS = W.water_surface(world, *np.meshgrid(FH.xs, FH.zs))
for kind, n, box, ylev, size, note in (
        ("snowy_pine", 60, ((-600, 600), (-600, 600)), None, ([4, 8], [12, 26]), "Snow-laden pine (teaser style), chunky stylised"),
        ("ice_crystal_cluster", 30, ((-600, 600), (-600, 600)), None, ([3, 7], [5, 16]), "Glowing pale-cyan ice-crystal cluster, faint inner light"),
        ("frosted_palm", 16, ((150, 400), (360, 520)), LAGOON, ([5, 8], [14, 20]), "Palm with frost-tipped fronds and icicle coconuts, leaning over the lagoons"),
        ("coral_ice", 22, ((340, 590), (130, 380)), REEF, ([4, 9], [5, 14]), "Candy-bright coral-ice branch (pink #FF6FB5 / tangerine #FFA552 / mint #6FFFD2), lit from inside"),
        ("snowpuff_group", 12, ((-600, 600), (-600, 600)), None, ([3, 5], [2, 4]), "Group of 2-5 snowpuffs (round penguin-puffin whimsy figures) watching the play"),
        ("lantern_hut", 6, ((-600, 600), (-600, 600)), None, ([6, 9], [7, 10]), "Little timber hut with a brass lantern in the window"),
):
    placed = 0
    tries = 0
    while placed < n and tries < 6000:
        tries += 1
        x = rnd.uniform(*box[0])
        z = rnd.uniform(*box[1])
        w_ = rnd.uniform(*size[0])
        hy = round(float(FH(x, z)[0]), 1)
        if hy < LANDING - 0.5:
            continue
        if ylev is not None and abs(hy - ylev) > 1.0:
            continue
        th = np.linspace(0, 2 * np.pi, 8, endpoint=False)
        if np.abs(FH(x + (w_ / 2 + 2) * np.cos(th), z + (w_ / 2 + 2) * np.sin(th)) - hy).max() > 1.2:
            continue
        ii, jj = int((x - FH.xs[0]) / 2), int((z - FH.zs[0]) / 2)
        if np.isfinite(WS[max(0, jj - 3):jj + 4, max(0, ii - 3):ii + 4]).any():
            continue
        if not clear_of_play(x, z, w_ / 2):
            continue
        placed += 1
        pieces.append(dict(id=f"{kind}_{placed:02d}", kind=kind, pos=[round(x, 1), hy, round(z, 1)], size=[round(w_, 1), round(rnd.uniform(*size[1]), 1), round(w_, 1)],
                           yaw_deg=round(rnd.uniform(0, 360)), note=note))

# --- brass lanterns on wooden posts along every walkway (beside the edge, never overhead)
lanterns = []
for p in world["paths"]:
    k = 0
    for s in p["segments"]:
        if s["type"] in ("on_hole", "lift", "gondola"):
            continue
        L = W.segment_len2(s)
        if L < 1e-6:
            continue
        ux, uz = (s["end"][0] - s["start"][0]) / L, (s["end"][2] - s["start"][2]) / L
        nstep = max(1, int(L // 16))
        for j in range(nstep):
            t = (j + 0.5) / nstep
            side = 1 if (k % 2 == 0) else -1
            off = p["width"] / 2 + 0.75
            x = s["start"][0] + (s["end"][0] - s["start"][0]) * t + side * uz * off
            z = s["start"][2] + (s["end"][2] - s["start"][2]) * t - side * ux * off
            y = s["start"][1] + (s["end"][1] - s["start"][1]) * t
            ok = True
            for s2 in p["segments"]:
                if s2["type"] in ("lift", "gondola"):
                    continue
                d2, _ = W.seg_dist(np.array(x), np.array(z), (s2["start"][0], s2["start"][2]), (s2["end"][0], s2["end"][2]))
                if float(d2) < p["width"] / 2 + 0.6:
                    ok = False
            if not ok:
                continue
            lanterns.append(dict(path=p["id"], pos=[round(x, 2), round(y, 2), round(z, 2)]))
            k += 1
world["lantern_posts"] = dict(size=[1.0, 7.0, 1.0], note="Brass lantern on a chunky wooden post, warm #FFB861 PointLight (range 14, brightness 0.8). "
                              "Posts stand 0.75 outside the walkway edge (on bridges: on the railing posts); the lamp sits on top, nothing overhangs the walkway.",
                              positions=lanterns)

world["lifts"] = lifts
world["pois"] = pois
world["movers_plan"] = dict(rule="One motion type per hole; no repeats. Run timing checks at 96+ phases (also verify 120) once holes.json exists.",
                            movers=movers_plan)
world["comfort"] = dict(
    head_clearance=8.0, railing_height=3.5, rail_drop=4.0,
    next_tee_teleport=dict(enabled=True, note="Standard hole-to-hole teleport to holes[].tee_teleport (3 studs behind each tee box)."),
    forced_locomotion=False,
    lift_max_speed=4.0, gondola_max_speed=6.0,
    decoration_rule="Nothing hangs lower than 8 studs over felt or walkways (lanterns over greens, arches, aurora ribbons, sky lanterns). "
                    "Moving obstacles are the only exception and stay below 4 studs.",
    span_rule="Every hole span over open sky has a player-only guard (4 high) on both gap rims and along any rail-less ball bridge, "
              "plus a railed 4-wide walk-on deck beside the safe ball route.",
)
world["backdrop"] = dict(
    rings=[
        dict(id="islets", name="Decorative floating islets (terrain)", count=len(islets), note="Unreachable islets at y 48-250 in the gaps"),
        dict(id="far_islands", name="Far floating islands", radius=[760, 960], count=16, color="hazed lilac-blue #8C8FD6 -> #5B5FA8"),
        dict(id="far_silhouettes", name="Distant island-mountains", radius=[1150, 1600], count=12, color="deep violet #3A3470 with haze"),
        dict(id="cloud_rings", name="Cloud banks", radius=[700, 1400], count=3),
        dict(id="sky", name="Night sky", radius=[1800, 2600], note="Moon bearing 220 / elevation 14, aurora curtains to the north, star field, sky lanterns"),
    ],
    pieces=pieces,
)

# ------------------------------------------------------------------ vistas (image prompts; see README / vistas/prompts.json)
STYLE = ("Stylized soft 3D render, cozy and whimsical, same art style and palette as the Aurora Archipelago menu card: chunky hand-made shapes, "
         "snow-capped floating rock islands over a lilac-white cloud sea at twilight-night, green and violet aurora ribbons, warm brass lanterns on "
         "wooden posts, chunky snow-capped timber railings, translucent glowing ice, soft bloom, original design, no text, no logos, no UI.")
VISTAS = [
    dict(id="V1", file="vistas/V1-first-tee-spire.png", camera=dict(pos=[-150.0, LANDING + 5.5, 551.0], look_at=[SPIRE["x"], 230.0, SPIRE["z"]], fov=70),
         prompt=("First-person VR view at standing eye height from the first tee of a mini golf course on the lowest floating island, looking north. "
                 "Directly ahead a short straight putting green of soft green felt, framed by chunky snow-capped wooden rails, runs 40 studs to a "
                 "small offset green behind a big snow-capped boulder with one flat angled face; a tall red flag marks the cup. Brass lanterns on "
                 "driftwood posts glow warm orange along a cobbled snowy walkway on the right, and a cluster of round penguin-puffin snowpuff figures "
                 "watches from a snowdrift on the left. Beyond the island's snowy rim the ground simply ends at a 24-stud cliff above a sea of soft "
                 "lilac-white clouds. Far ahead, rising out of the clouds on its own little island, the Starfrost Spire: an enormous faceted "
                 "aurora-crystal spire glowing mint to violet from inside, with crystal shards orbiting it, towering into the night sky. Green and "
                 "violet aurora curtains ripple across the northern sky above it. On the right, higher, a second island with steam rising from "
                 "turquoise hot springs and frosted palms; in the distance more floating islands at different heights, one with a frozen waterfall. "
                 "A big soft moon glows low behind the viewer to the left, outside the frame, lighting snow edges lilac. " + STYLE)),
    dict(id="V2", file="vistas/V2-skylight-overlook.png", camera=dict(pos=[-292.0, SUMMIT + 5.5, -272.0], look_at=[-100.0, 190.0, -238.0], fov=75),
         prompt=("High overlook from Skylight Point on the west rim of the highest floating island (the summit, y 222), standing beside a small "
                 "lantern-roofed gondola station and looking east across the summit plateau. Across the left half of the view, three mini golf "
                 "holes on snowy ground linked by cobbled walkways with brass lantern posts: nearest, a long par 4 that climbs a ramp to a raised "
                 "green under the Halo Arch, a huge translucent glowing ice arch spanning the hole; beyond it a green that leaps a narrow crevasse "
                 "open to the clouds on a shimmering green-violet aurora ribbon bridge, beside a sturdier railed ice bridge; furthest, a round "
                 "moonstone well bowl ringed with glowing ice crystals. Every green has a tall red flag. Past the summit's cliff edge and lower "
                 "down, the Icefall Terraces island with great frozen waterfalls pouring off its north rim into the cloud sea. On the right side "
                 "of the view the giant Starfrost Spire rises out of the clouds on its own island, glowing mint and violet with orbiting crystal "
                 "shards, and far beyond it, much lower, the reef and lagoon islands with turquoise hot springs and wisps of steam. Green and "
                 "violet aurora curtains fill the upper sky; snowy pines and snowpuff figures dot the plateau. " + STYLE)),
    dict(id="V3", file="vistas/V3-aurora-skybridge.png", camera=dict(pos=[244.0, ICEFALL + 5.5, -87.0], look_at=[150.0, 186.0, -121.0], fov=80),
         prompt=("First-person view walking onto the Aurora Skybridge, a long straight railed footbridge with a glowing translucent deck that shifts "
                 "between mint green and violet like the aurora, chunky snow-capped timber railings on both sides with brass lanterns on every "
                 "second post. It leaps 130 studs across open sky from a small snowy pinnacle to the Icefall Terraces island ahead, where a carousel "
                 "canopy with a snowpuff weathervane stands over a mini golf green and a timber bell gantry hung with icicles stands beyond it. "
                 "Far below the bridge lies the soft lilac cloud sea; a small decorative floating islet with snowy pines hangs in the open sky just "
                 "left of the bridge's far end, a little below eye level. Further left, in the middle distance, the giant Starfrost Spire rises "
                 "out of the clouds on its own island, glowing mint and violet with orbiting crystal shards; aurora curtains fill the sky above "
                 "the terraces, and a lilac twilight glow brightens the far left horizon. " + STYLE)),
    dict(id="V4", file="vistas/V4-aerial-overview.png", camera=dict(pos=[260.0, 520.0, 760.0], look_at=[60.0, 120.0, 40.0], fov=60),
         prompt=("Aerial three-quarter overview of the whole archipelago from high above the south-east, at night under aurora: a ring of floating "
                 "snow-capped rock islands at six different heights spiralling up anticlockwise around a central floating island that holds the "
                 "giant glowing Starfrost Spire. Lowest, in the south-west foreground, a harbour island with a lantern-lit quay, three mini golf "
                 "holes and a small islet across a gap; a railed glowing ice bridge and a lantern stair climb to the next island, a geothermal "
                 "island with two steaming turquoise hot-spring lagoons, frosted palms and a geyser; behind it to the east a coral-ice reef island "
                 "in candy pink, tangerine and mint with a conch islet reached by an ice bridge; then north a frozen shelf with a frozen pond; a "
                 "slender pinnacle and a long glowing aurora skybridge lead west to a terraced island with great frozen waterfalls pouring into the "
                 "clouds; highest, in the north-west, the summit island with a translucent ice arch over its final green and a gondola cable "
                 "sweeping all the way back down to the harbour. Small open-cage lifts cling to the cliffs between islands. Every green has a red "
                 "flag. The cloud sea glows lilac-white below, more distant floating islands and a pierced ice-arch island on the horizon, a low "
                 "moon to the south-west. " + STYLE)),
]
world["vistas"] = VISTAS

with open(W.WORLD_JSON, "w") as f:
    json.dump(world, f, indent=1)
os.makedirs(os.path.join(W.WORLD_DIR, "vistas"), exist_ok=True)
with open(os.path.join(W.WORLD_DIR, "vistas", "prompts.json"), "w") as f:
    json.dump([dict(id=v["id"], file=v["file"].split("/", 1)[1], prompt=v["prompt"]) for v in VISTAS], f, indent=1)
print("wrote", W.WORLD_JSON)
for p in paths:
    print(f"{p['id']:12s} {p['length']:7.1f}")
print("walk total (spawn->H18 cup, excluding lifts/gondola):", round(sum(p["length"] for p in paths if p["to_hole"]), 1))
print("pieces", len(pieces), "| islets", len(islets), "| hills", len(hills), "| lanterns", len(lanterns), "| total par", sum(h["par"] for h in HOLES))
