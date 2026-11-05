#!/usr/bin/env python3
"""Source of truth for ../holes.json. Edit here, then: python3 tools/build_holes.py
Every playtest-round change is made in this file and logged in playtest-log.md."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from geom import Hole, arm_blockers, T
import math
r4 = lambda v: round(v, 4)
import sim as S

OUT = os.environ.get("LG_OUT") or os.path.join(os.path.dirname(__file__), "..", "holes.json")
# Sweep hook (tools/sweep_r5.py): LG_VARIANT='{"h4_speed": 30, ...}' overrides the tuning knobs below; LG_OUT writes elsewhere.
VAR = json.loads(os.environ.get("LG_VARIANT") or "{}")


def K(key, default):
    """tuning knob (default = the committed value)"""
    return VAR.get(key, default)

SCHEMA = {
    "version": "1.0",
    "units": "studs (1 stud = 0.3 m). Speeds studs/s, angles degrees, angular speed deg/s.",
    "axes": "Right-handed, +Y up. Each hole has its own local frame: tee near the origin, play generally toward -Z. "
            "Map/top-down view used in all docs and renders: +X to the right, -Z up ('north'). "
            "Facing -Z (Roblox LookVector default) the player's right is +X.",
    "world_placement": "world = R_y(world_yaw) * local + world_offset. world_offset [x,y,z] studs, world_yaw degrees.",
    "yaw": "Degrees about +Y, right-handed (Roblox CFrame.Angles(0, math.rad(yaw), 0)). Local->world: "
           "x' = lx*cos(yaw) + lz*sin(yaw); z' = -lx*sin(yaw) + lz*cos(yaw). Positive yaw = counter-clockwise in the map view.",
    "felt": "Playable surface pieces. {id, zone, center:[x,y,z] = TOP-surface centre, size:[sx,sz] footprint in local x/z, yaw, "
            "slope:null|{axis:'x'|'z', rise}}. rise = surface height at the +axis end minus the -axis end (local axes); the "
            "surface is a single plane so heights at the ends are center.y +- rise/2. Collision part = a box whose top face is that "
            "plane (thickness free, suggest 0.4; build sloped pieces as a box rotated by atan(rise/len) about the local axis "
            "perpendicular to `axis`, then shifted so the top-surface centre matches). Optional flags: overlay=true (banked plane laid "
            "on top of base felt; its low edge is flush with the base), kind='bank'|'bridge'|'tunnel', tunnel=true (felt runs "
            "inside a decorative enclosure; physics unchanged), solid=false + thickness (bridge deck: a ball on a lower level can roll "
            "underneath). Pieces join when edges meet/overlap at equal height (tolerance 0.05).",
    "walls": "Invisible collision blocks. {id, center:[x,y,z] = box centre, size:[sx,sy,sz] local box size, yaw, kind?}. kind='bumper' (static obstacle blocks: hub, stump, posts) uses bumper restitution 0.65; everything else is a wall (0.63). Authored rails "
             "have local Z along the run and local X = thickness 0.5; height is 1.0 above the highest felt they border (boxes "
             "along ramps are simply taller; visual rails can follow the slope). Rails sit OUTSIDE the felt edge (inner face on "
             "the edge). Blocks named hub/stump/rock are static obstacles.",
    "hazards": "Out-of-bounds volumes below felt level: {id, type:'water'|'pit', center:[x,y,z] (water/pit surface), size:[sx,sz], yaw, "
               "reset:'previous_position'|'respawn', respawn?:[x,y,z], penalty:1}. A ball that leaves the felt over a hazard gets +1 stroke and "
               "is returned to where its stroke started (reset='previous_position'), or, if reset='respawn', placed at rest on the "
               "`respawn` point (a felt point, e.g. a bridge entry). Any ball leaving all felt elsewhere goes back to its stroke start "
               "(and is flagged as an escape bug).",
    "drops": "Intentional level changes: {id, from, to, edge, height}. The upper piece's edge is open (no rail) and the lower felt "
             "starts directly below/beyond it; the ball falls and keeps ~80% of horizontal speed. Lower felt may extend under the "
             "upper piece (the upper piece then acts as a cliff face for the lower level).",
    "moving_parts": "Separate parts. type 'swing' = pendulum: {id, type:'swing', pivot:[x,y,z] (hinge point above the felt), axis (unit "
                    "vector, horizontal; swing plane is perpendicular to it), amplitude_deg, period_s, phase (deg of the swing cycle at t=0), "
                    "blockers (relative to the pivot with the pendulum hanging straight down)}: angle(t) = amplitude_deg*sin(360*t/period_s + phase), "
                    "right-hand rule about axis; `speed` = peak angular speed at the bottom (info), range = [-amp, amp]. "
                    "Other types: {id, type:'rotate'|'slide', pivot:[x,y,z], axis:[ax,ay,az] unit vector, speed (deg/s for rotate, "
                    "studs/s for slide, sign = direction, right-hand rule about axis), range:null (continuous) | [min,max] "
                    "(ping-pong between angles in deg or offsets in studs), phase (angle/offset at t=0), blockers:[{center:[dx,dy,dz] "
                    "relative to pivot at angle/offset 0, size:[sx,sy,sz], yaw, roll?}]} (roll = extra initial rotation in deg about the part axis, "
                    "applied to the blocker's centre and orientation, e.g. wheel paddles at 0/120/240). At time t a blocker is "
                    "pivot + Rot(axis, angle(t)) * center (rotate) or pivot + center + axis*offset(t) (slide). "
                    "Slides may pause: dwell:[{at: offset, s: seconds}]. One cycle = range[0] -> range[1] -> range[0] at |speed|; "
                    "a stop at a range end pauses once per visit, an interior stop on both passes; phase = offset at t=0 on the "
                    "forward (min -> max) pass (if a stop sits at that offset, t=0 is the start of its pause). "
                    "period_s = full cycle incl. pauses (info). The game script must reproduce this "
                    "profile (e.g. tween legs + waits), not a plain sine/ping-pong.",
    "teleports": "{id, entry:{center:[x,y,z], radius}, exit:{center:[x,y,z], dir:[dx,dz]}, speed_factor, min_speed, max_speed}. A ball "
                 "whose centre enters the entry radius (same level) reappears at exit moving along dir with "
                 "speed = clamp(speed_in*speed_factor, min_speed, max_speed).",
    "cup": "{position:[x,y,z] (on felt), radius, flag}. Gameplay cup radius 0.5 stud (real cup 4.25 in = 0.36 stud diameter; enlarged ~2.8x for VR "
           "readability). Ball is holed when its centre is within radius and speed < 5.33 studs/s (1.6 m/s). "
           "flag = {pole_height (studs above the cup felt), pole_diameter, banner_size [w,h,t], banner_color, top:[x,y,z] (pole top, "
           "the point the tee line-of-sight check aims at), collision:false}: visual only, the ball passes through it.",
    "ball": "radius 0.08 stud (~real 42.7 mm ball at 0.3 m/stud). Full physics constants in the top-level 'physics' block (= tools/sim.py).",
    "tee": "{position:[x,y,z], aim_hint:[dx,dz]}",
    "ai_waypoints": "{skill|'all': [{id, pos:[x,y,z], from:[zones], carry, power_scale}]} used by the sim golfer: from its current zone it "
                    "aims at the furthest allowed target with line of sight (cup first, then waypoints last->first) and hits for "
                    "distance + carry. cup_from (list of zones or null=all, or {skill: list|null}) limits when it goes straight for the cup.",
    "decoration_anchors": "{name, position:[x,y,z] (base centre), notes, landmark?, approx_size?, occluders?, facing?} - visual only, no collision. "
                          "occluders = [{center:[x,y,z] box centre, size:[sx,sy,sz], yaw}]: the solid parts of the prop, used only by the "
                          "tee->flag line-of-sight check (tools/sim.py flag_los).",
    "line_of_sight": "Checked from the tee eye point (tee + 5.5 studs up) to the flag top against rails/blocks, felt and the ground under "
                     "it, prop occluders, and moving blockers (reported as % of their cycle).",
    "felt_widths": "Lanes 7-8 studs (2.1-2.4 m), greens 12-18 studs (3.6-5.4 m); rails 1 stud high (0.3 m), 0.5 thick (0.15 m).",
}

holes = []

# ---------------------------------------------------------------- H1
h = Hole(1, "h01", "Lantern Gate", 2, "Sunny Forest Edge", "Lantern torii gate over the ramp",
         "Gentle ramp + 45-degree deflector bank onto an offset green", (0, 0, 0))
h.rect("tee", -3.5, 3.5, 2, -18, 0.0, zone="lane")
h.rect("ramp", -3.5, 3.5, -18, -24, zone="lane", slope=("z", 0.0, 0.5))
h.rect("green", -11, 3.5, -24, -36, 0.5, zone="green")
h.wall_path([(-3.5, 2), (-3.5, -24), (-11, -24), (-11, -36), (3.5, -36), (3.5, 2)],
            [0, 0.5, 0.5, 0.5, 0.5, 0], out="L", closed=True)
h.wall_free((4.0, -28.5), (-4.0, -36.5), 0.5, name="deflector")
h.tee(0, 0, 0)
h.cup(-9.5, 0.5, -26.5, flag_h=7.5)
h.wp("all", "deflect", [0.0, 0.5, -32.0], ["lane"], carry=8.0)
h.anchor("lantern_gate", [0, 0.25, -21], "Torii-style timber arch over the ramp, 2 paper lanterns hanging inside", landmark=True, size=[9, 7, 1.2],
         occluders=[((-4.25, 3.75, -21), (0.6, 7, 0.6)), ((4.25, 3.75, -21), (0.6, 7, 0.6)), ((0, 6.75, -21), (9, 1.0, 1.2))])
h.anchor("mossy_boulder", [-8, 0.5, -21], "Big mossy boulder outside the green's front-left rail", size=[4, 3, 4],
         occluders=[((-8, 2.0, -21), (4, 3, 4))])
h.anchor("welcome_sign", [-6, 0, 1], "Carved 'Lantern Grove - Hole 1' sign post", size=[2, 3, 0.4])
h.anchor("maple_tree", [8, 0, -15], "Red maple outside right rail", size=[10, 16, 10],
         occluders=[((8, 3, -15), (1.5, 6, 1.5)), ((8, 11, -15), (10, 10, 10))])
holes.append(h)

# ---------------------------------------------------------------- H2
h = Hole(2, "h02", "Acorn Ledge", 2, "Sunny Forest Edge", "Giant acorn on a stump splitting the ledge",
         "Drop between levels through one of two chutes either side of a stump; rabbit-hole pit punishes overcooking the left chute", (34, 0, 4))
h.rect("lane", -4, 4, 2, -20, 0.0, zone="lane")
# lower green split around the rabbit-hole pit x[-6,-4] z[-29,-31]
h.rect("lower_a", -8, 8, -20, -29, -1.5, zone="lower")
h.rect("lower_b", -8, -6, -29, -31, -1.5, zone="lower")
h.rect("lower_c", -4, 8, -29, -31, -1.5, zone="lower")
h.rect("lower_d", -8, 8, -31, -38, -1.5, zone="lower")
h.hazard("rabbit_hole", "pit", -6, -4, -29, -31, -2.5)
h.wall_path([(4, -20), (4, 2), (-4, 2), (-4, -20)], 0.0, out="L", ybot=-2.0, ext=(0.5, 0.5))
h.block("stump", 0, -19.5, 3.0, 1.0, 0.0, height=1.2, ybot=-2.0)
h.drop("d1", "lane", "lower", "lane north edge z=-20, chutes x[-4,-1.5] & x[1.5,4]", 1.5)
h.wall_path([(-4, -20), (-8, -20), (-8, -38), (8, -38), (8, -20), (4, -20)], -1.5, out="L", ext=(0.5, 0.5))
h.tee(0, 0, 0)
h.cup(2.5, -1.5, -35, flag_h=7.5)
h.wp("good", "chute_left", [-2.75, 0.0, -20.0], ["lane"], carry=5.0)
h.wp("average", "chute_right", [2.75, 0.0, -20.0], ["lane"], carry=5.0)
h.anchor("giant_acorn", [0, 0.0, -19.5], "Giant acorn (cap + nut) sitting on the stump between the chutes (size incl. the 1.2 stump)", landmark=True, size=[3, 4, 3],
         occluders=[((0, 2.6, -19.5), (3, 2.8, 3))])
h.anchor("rabbit_hole_rim", [-5, -1.5, -30], "Rabbit-hole rim of roots and moss around the pit", size=[3, 0.5, 3])
h.anchor("squirrel_hut", [11, -1.5, -28], "Tiny squirrel hut on a post outside the right rail", size=[3, 5, 3])
h.anchor("ledge_lanterns", [-4.5, 0, -19.5], "Lantern posts at both chute edges (x -4.5 and +4.5, on the rail line)", size=[0.5, 3, 0.5],
         occluders=[((-4.5, 1.5, -19.5), (0.5, 3, 0.5)), ((4.5, 1.5, -19.5), (0.5, 3, 0.5))])
# Round 5: wayfinding for the two chutes (decoration only, no collision)
h.anchor("chute_sign_left", [-5.2, 0, -16.5], "Carved arrow sign on a post outside the left rail, arrow board angled to point "
         "through the LEFT chute; text 'Bold Line' + small rabbit icon (warns of the rabbit hole)", size=[1.8, 3.2, 0.25],
         facing=[0.35, -1.0], occluders=[((-5.2, 1.6, -16.5), (0.25, 3.2, 0.25))])
h.anchor("chute_sign_right", [5.2, 0, -16.5], "Carved arrow sign on a post outside the right rail, arrow board angled to point "
         "through the RIGHT chute; text 'Safe Line'", size=[1.8, 3.2, 0.25], facing=[-0.35, -1.0],
         occluders=[((5.2, 1.6, -16.5), (0.25, 3.2, 0.25))])
h.anchor("chute_arrow_left", [-2.75, 0.0, -17.0], "Glowing leaf-arrow decal flush on the felt (0.01 thick), pointing -Z into the left chute", size=[1.4, 0.01, 2.0])
h.anchor("chute_arrow_right", [2.75, 0.0, -17.0], "Glowing leaf-arrow decal flush on the felt (0.01 thick), pointing -Z into the right chute", size=[1.4, 0.01, 2.0])
holes.append(h)

# ---------------------------------------------------------------- H3
h = Hole(3, "h03", "Toadstool Row", 3, "Mushroom Village", "Mushroom house with a tunnel through its stem",
         "S-bend with two steep banked-plane corners and a stem tunnel", (4, 1, -66))
h.rect("lane", -3.5, 3.5, 2, -15.5, 0.0, zone="lane")
h.rect("cross1", 3.5, 6, -8.5, -15.5, 0.0, zone="cross")
h.rect("tunnel", 6, 11, -8.5, -15.5, 0.0, zone="cross", tunnel=True, kind="tunnel")
h.rect("cross2", 11, 14, -8.5, -15.5, 0.0, zone="cross")
h.rect("leg", 14, 21, -8.5, -22, 0.0, zone="leg")
h.rect("green", 11.5, 23.5, -22, -33, 0.0, zone="green")
h.bank_wall("bank1", (-3.5, -9.0), (3.0, -15.5), "L", zone="lane")
h.bank_wall("bank2", (14.5, -8.5), (21.0, -15.0), "R", zone="cross")
h.wall_path([(-3.5, 2), (-3.5, -15.5), (14, -15.5), (14, -22), (11.5, -22), (11.5, -33), (23.5, -33), (23.5, -22),
             (21, -22), (21, -8.5), (3.5, -8.5), (3.5, 2)], 0.0, out="L", closed=True, top=2.4)
h.block("toadstool_stool", 17.0, -28.8, 1.6, 1.6, 0.0, height=1.5)
h.tee(0, 0, 0)
h.cup(15.5, 0.0, -30.5, flag_h=7.5)
h.wp("good", "corner1", [-1.0, 0.0, -11.5], ["lane"], carry=16.0)
h.wp("average", "corner1", [-1.0, 0.0, -11.5], ["lane"], carry=14.0)
h.wp("all", "corner2", [18.0, 0.0, -12.0], ["cross"], carry=12.0)
h.wp("all", "green_in", [17.5, 0.0, -24.5], ["leg"], carry=1.0)
h.anchor("stem_house", [8.5, 0, -12], "Red-cap mushroom house; felt tunnel runs through its stem (5 long, 3 high opening)", landmark=True, size=[10, 12, 10],
         occluders=[((8.5, 4.0, -12), (5, 2, 8)), ((8.5, 8.5, -12), (10, 7, 10))])
h.anchor("small_toadstools", [-6, 0, -6], "Cluster of 3 small toadstools", size=[3, 2.5, 3])
h.anchor("house_2", [26, 0, -14], "Second mushroom house with round window", size=[7, 9, 7], occluders=[((26, 4.5, -14), (7, 9, 7))])
h.anchor("toadstool_stool_deco", [17.0, 0, -28.8], "Fat spotted toadstool stool guarding the cup (bumper block 1.6x1.5x1.6)", size=[2, 1.8, 2],
         occluders=[((17.0, 0.9, -28.8), (2, 1.8, 2))])
h.anchor("lantern_string", [17.5, 4, -22], "Lantern string across green entrance", size=[12, 1, 0.3])
holes.append(h)

# ---------------------------------------------------------------- H4
# Round 5: spinner 36 -> 30 deg/s, padded puffball arms (bumper restitution 0.65, like every moving blocker), arms shortened so the
# side gaps beside the carousel are a reliable (but ~1 stroke longer) route; skilled golfers take it.
H4_ARM = K("h4_arm", 3.0)
H4_PLAZA = K("h4_plaza", 7.0)
h = Hole(4, "h04", "Spore Spinner", 3, "Mushroom Village", "Spinning puffball carousel",
         "Rotating 2-arm spinner bar in a plaza (time it for a birdie, or take a side gap for a safe par), then ramp up to a raised green", (52, 1, -60))
h.rect("lane", -4, 4, 2, -14, 0.0, zone="lane")
h.rect("plaza", -H4_PLAZA, H4_PLAZA, -14, -28, 0.0, zone="plaza")
h.rect("ramp", -5, 5, -28, -36, zone="ramp", slope=("z", 0.0, 0.6))
h.rect("green", -6, 6, -36, -46, 0.6, zone="green")
h.wall_path([(-4, 2), (-4, -14), (-H4_PLAZA, -14), (-H4_PLAZA, -28), (-5, -28), (-5, -36), (-6, -36), (-6, -46), (6, -46), (6, -36),
             (5, -36), (5, -28), (H4_PLAZA, -28), (H4_PLAZA, -14), (4, -14), (4, 2)],
            [0, 0, 0, 0, 0, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0, 0, 0, 0, 0], out="L", closed=True)
h.block("hub", 0, -21, 1.4, 1.4, 0.0, height=2.0)
h.rotor("spinner", [0, 0, -21], [0, 1, 0], K("h4_speed", 30.0), arm_blockers(2, 0.7, H4_ARM, 0.7, 1.0),
        visual=f"2 padded puffball-stalk arms (one {2 * H4_ARM:g}-stud bar) on a toadstool hub; arms are soft bumpers (restitution 0.65)")
h.tee(0, 0, 0)
h.cup(2.5, 0.6, -42.0, flag_h=7.5)
h.wp("all", "ramp", [1.8, 0.3, -32.0], ["lane", "plaza"], carry=11.0)
# skilled golfers skip the carousel: tee shot down the east side gap (aim point between the arm tips and the rail)
h.wp("good", "ramp", [1.8, 0.3, -32.0], ["plaza"], carry=11.0)
h.wp("good", "side_gap", [K("h4_gap_x", 4.3), 0.0, K("h4_gap_z", -25.0)], ["lane"], carry=K("h4_gap_carry", 0.0))
h.d["cup_from"] = {"good": ["plaza", "ramp", "green"], "average": None}  # good golfers don't fire at the flag through the carousel
h.anchor("puffball_carousel", [0, 0, -21], "Toadstool hub with a 2-arm padded puffball bar (moving mesh, pivot at hub centre)", landmark=True,
         size=[2 * H4_ARM, 4, 2 * H4_ARM])
h.anchor("mushroom_house_L", [-12, 0, -21], "Mushroom house beside plaza", size=[8, 10, 8], occluders=[((-12, 5, -21), (8, 10, 8))])
h.anchor("mushroom_house_R", [12, 0, -24], "Mushroom house beside plaza", size=[7, 9, 7], occluders=[((12, 4.5, -24), (7, 9, 7))])
h.anchor("green_lanterns", [-7, 0.6, -41], "Lantern posts flanking raised green", size=[0.5, 3.5, 0.5])
h.anchor("side_gap_lanterns", [H4_PLAZA + 0.25, 0, -17], "Pair of small lantern posts on the plaza rails marking the east and west side gaps "
         f"(x = +-{H4_PLAZA + 0.25:g}, on the rail tops)", size=[0.4, 2.5, 0.4])
holes.append(h)

# ---------------------------------------------------------------- H5
# Round 5: a ball that falls off the root bridge respawns at the bridge entry (+1), not back at the tee.
H5_HALF = K("h5_half", 0.9)
h = Hole(5, "h05", "Rootbridge Crossing", 3, "Stream Crossing", "Arched root bridge over the stream",
         "Split path: narrow rail-less root bridge straight from the tee (risk) vs covered plank bridge (safe); a fall respawns at the bridge entry", (96, -1, -10))
h.rect("shore", -15, 6, 2, -15, 0.0, zone="shore")
h.rect("root1", -H5_HALF, H5_HALF, -15, -21.5, zone="root", slope=("z", 0.0, 0.4), kind="bridge")
h.rect("root2", -H5_HALF, H5_HALF, -21.5, -28, zone="root", slope=("z", 0.4, 0.0), kind="bridge")
h.rect("covered", -13, -8, -15, -28, 0.0, zone="covered", kind="bridge")
h.rect("north", -15, 6, -28, -42, 0.0, zone="north")
h.hazard("stream", "water", -17, 8, -15, -28, -1.0, respawn=K("h5_respawn", [0.0, 0.0, -13.5]))
h.wall_path([(-8, -15), (-H5_HALF, -15)], 0.0, out="L", ext=(0.0, 0.0))
h.wall_path([(H5_HALF, -15), (6, -15), (6, 2), (-15, 2), (-15, -15), (-13, -15)], 0.0, out="L", ext=(0.0, 0.0))
h.wall_path([(-13, -15), (-13, -28)], 0.0, out="L")
h.wall_path([(-8, -28), (-8, -15)], 0.0, out="L")
h.wall_path([(-13, -28), (-15, -28), (-15, -42), (6, -42), (6, -28), (H5_HALF, -28)], 0.0, out="L", ext=(0.0, 0.0))
h.wall_path([(-H5_HALF, -28), (-8, -28)], 0.0, out="L", ext=(0.0, 0.0))
h.tee(0, 0, 0)
h.cup(1.5, 0.0, -37.0, flag_h=7.5)
h.d["cup_from"] = ["north"]
h.wp("good", "root_far", [0.0, 0.0, -29.0], ["shore", "root"], carry=4.0)
h.wp("average", "covered_line", [-10.5, 0.0, -9.0], ["shore"], carry=0.0)
h.wp("average", "covered_out", [-10.5, 0.0, -29.0], ["shore", "covered"], carry=3.0)
h.anchor("root_bridge", [0, 0.2, -21.5], f"Gnarled arched root bridge (no rails), felt on top, {2 * H5_HALF:g} wide", landmark=True, size=[3.5, 3, 14])
h.anchor("covered_bridge", [-10.5, 0, -21.5], "Plank covered bridge with shingle roof and lanterns", size=[7, 6, 14],
         occluders=[((-10.5, 4.5, -21.5), (7, 3, 14))])
h.anchor("stream_rocks", [4, -1, -21], "Mossy stepping stones in the stream", size=[2, 1, 2])
h.anchor("waterfall_bg", [10, -1, -21], "Small waterfall feeding the stream (upstream, right side)", size=[6, 8, 3])
h.anchor("bridge_respawn_stone", [0, 0, -13.5], "Glowing mossy marker stone set flush in the felt at the root-bridge entry: "
         "where a ball that falls in the stream reappears", size=[0.8, 0.02, 0.8])
holes.append(h)

# ---------------------------------------------------------------- H6
h = Hole(6, "h06", "Mill Wheel Run", 3, "Stream Crossing", "Water mill with a turning paddle wheel",
         "Paddle wheel (horizontal axle) dips across the flume; timber deflector boards; mill-race water hazard; ramp to green", (84, -2, -70))
h.rect("lane", -3.5, 3.5, 2, -12, 0.0, zone="lane")
h.rect("channel", 3.5, 18, -5, -12, 0.0, zone="channel")
h.rect("ramp", 11, 18, -12, -18, zone="ramp", slope=("z", 0.0, 0.25))
h.rect("green", 8, 21, -18, -28, 0.25, zone="green")
h.hazard("millrace", "water", 4.5, 9.5, -5, -1, -0.8)
h.wall_path([(6, -5), (3.5, -5), (3.5, 2), (-3.5, 2), (-3.5, -12), (11, -12), (11, -18), (8, -18), (8, -28),
             (21, -28), (21, -18), (18, -18), (18, -5), (8.5, -5)],
            [0, 0, 0, 0, 0, 0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0, 0], out="L", ext=(0.0, 0.0), ybot=-0.5)
h.wall_free((-4.0, -5.0), (3.0, -12.0), 0.0, name="board1", ext=0.5)
h.wall_free((11.5, -4.5), (18.5, -11.5), 0.0, name="board2", ext=0.5)
h.rotor("millwheel", [7.5, 3.6, -8.5], [0, 0, 1], 30.0,
        [dict(center=[0, -2.9, 0], size=[0.6, 1.4, 7.6], yaw=0.0, roll=r) for r in (0, 180)],
        visual="Water-mill wheel, radius 3.6, 2 opposed paddle boards spanning the flume; felt has a 0.8-wide slot under it")
h.tee(0, 0, 0)
h.cup(16.5, 0.25, -22.5, flag_h=7.5)
h.wp("good", "board1", [0.0, 0.0, -8.0], ["lane"], carry=40.0)
h.wp("average", "board1", [0.0, 0.0, -8.0], ["lane"], carry=14.0)
h.wp("all", "board2", [15.0, 0.0, -9.0], ["channel"], carry=12.0, power_scale=1.25)
h.anchor("water_mill", [7.5, 0, 0], "Timber mill house on the south side; wheel axle enters it", landmark=True, size=[9, 10, 8],
         occluders=[((7.5, 5, 0), (9, 10, 8))])
h.anchor("mill_wheel", [7.5, 3.6, -8.5], "Wheel mesh (moving part) radius 3.6, axle along Z", size=[1, 7.2, 8])
h.anchor("waterfall", [24, 0.25, -24], "Waterfall cascading down rocks east of the green", size=[6, 12, 4])
h.anchor("sacks", [-6, 0, -6], "Flour sacks & crates", size=[2, 1.5, 2])
holes.append(h)

# ---------------------------------------------------------------- H7
# Round 5: the log is built to stop 0.5 studs short of each rail (rail inner faces x=+-10, log half-length 2.5 -> travel +-7.0).
# Round 7 (timing obstacle): log 5 -> 6 long with pointed 45-degree ends (an end hit kicks the ball out of the log's track: fixes the
# 'batted along the track' soft-lock), 5 -> 3.5 studs/s, pauses 1.0 s at the west end (gap line open) and 1.5 s at the east end
# (log across the gap line), end gap 0.5 -> 1.0.
H7_GAP = K("h7_gap", (4.0, 6.5))
h = Hole(7, "h07", "Cascade Steps", 3, "Waterfall Terraces", "Three-tier waterfall beside stepped greens",
         "Two drops down terraces, sliding log on the middle tier, waterfall-pool hazard, side-sloped bottom green", (144, -3, -40))
h.rect("t1", -4, 4, 2, -14, 0.0, zone="t1")
h.rect("t2", -10, 10, -14, -27, -1.2, zone="t2")
h.rect("t3", -8, 1, -27, -40, -2.4, zone="t3")
h.rect("t3_slope", 1, 10, -27, -40, zone="t3", slope=("x", -2.4, K("h7_slope_hi", -2.0)))
h.hazard("pool", "water", -14, -10, -16, -26, -3.0)
h.drop("d1", "t1", "t2", "t1 north edge z=-14, full width", 1.2)
h.drop("d2", "t2", "t3", f"t2 north edge z=-27, gap x[{H7_GAP[0]:g},{H7_GAP[1]:g}] (lands on the sloped east half of t3)", 1.0)
h.wall_path([(4, -14), (4, 2), (-4, 2), (-4, -14)], 0.0, out="L", ybot=-1.7)
h.wall_path([(-4, -14), (-10, -14), (-10, -18)], -1.2, out="L", ext=(0.5, 0.0))
h.wall_path([(-10, -24), (-10, -27), (H7_GAP[0], -27)], -1.2, out="L", ext=(0.0, 0.0), ybot=-2.9)
h.wall_path([(H7_GAP[1], -27), (10, -27), (10, -14), (4, -14)], -1.2, out="L", ext=(0.0, 0.5), ybot=-2.9)
h.wall_path([(-8, -27), (-8, -40), (10, -40), (10, -27)], [-2.4, -2.4, -2.0, -2.0], out="L", ext=(0.5, 0.5))
H7_LOG = K("h7_log_len", 6.0)            # log length (pointed ends included)
H7_EG = K("h7_end_gap", 1.0)             # log end -> rail inner face at the ends of travel
H7_TRAVEL = 10.0 - H7_EG - H7_LOG / 2
H7_DW = K("h7_dwell", (1.0, 1.5))        # pause (s) at the west / east end of travel
H7_CAPS = K("h7_caps", True)            # pointed (45-degree) log ends: an end hit kicks the ball out of the log's track
if H7_CAPS:
    cs = 0.8 / math.sqrt(2)
    log_bl = [dict(center=[0, 0.4, 0], size=[H7_LOG - 0.8, 0.8, 0.8], yaw=0.0)] + \
             [dict(center=[sx * (H7_LOG / 2 - 0.4), 0.4, 0], size=[r4(cs), 0.8, r4(cs)], yaw=45.0) for sx in (-1, 1)]
else:
    log_bl = [dict(center=[0, 0.4, 0], size=[H7_LOG, 0.8, 0.8], yaw=0.0)]
h.slider("log", [0, -1.2, -20.5], [1, 0, 0], K("h7_log_speed", 3.5), [-H7_TRAVEL, H7_TRAVEL], log_bl,
         dwell=[(o, d) for o, d in zip((-H7_TRAVEL, H7_TRAVEL), H7_DW) if d > 0],
         visual=f"Floating log on a hidden rail; log ends stop {H7_EG:g} studs short of each rail line (x=+-10): travel +-{H7_TRAVEL:g}")
h.d["moving_parts"][-1]["end_clearance"] = H7_EG
h.tee(0, 0, 0)
h.cup(*K("h7_cup", [-2.5, -2.4, -36.5]), flag_h=7.5)
h.wp("all", "gap", [(H7_GAP[0] + H7_GAP[1]) / 2, -1.2, -27.0], ["t1", "t2"], carry=5.0)
h.anchor("cascade", [-16, -3, -18], "Three-step waterfall dropping into the pool on the left", landmark=True, size=[8, 14, 10])
h.anchor("log_rail", [0, -1.2, -20.5], f"Floating log (moving mesh) on a hidden rail across the middle tier; stops {H7_EG:g} short of each rail", size=[H7_LOG, 0.8, 0.8])
h.anchor("ferns", [12, -2.4, -34], "Fern clumps and red leaves", size=[3, 2, 3])
h.anchor("step_lanterns", [H7_GAP[0] + 1.0, -1.2, -27], "Lanterns flanking the lower gap", size=[0.5, 3, 0.5],
         occluders=[((H7_GAP[0] - 0.25, 0.3, -27.5), (0.5, 3, 0.5)), ((H7_GAP[1] + 0.25, 0.3, -27.5), (0.5, 3, 0.5))])
holes.append(h)

# ---------------------------------------------------------------- H8
# Round 5: ring 0.35 -> 0.55; long route shortened (the flat c1 run removed: climb + top + green moved 9 studs south);
# banked plane on the alcove back wall feeds misses back out; exit checked with tools/teleport_check.py.
S8 = K("h8_shift", 9.0)          # how far the upper level moved toward the tee
R8 = K("h8_ring", 0.45)          # Round 7: 0.55 -> 0.45 (the gated door lets more ring shots through; keeps good >= par-1)
h = Hole(8, "h08", "Firefly Hollow", 4, "Hollow Tree Roots", "Firefly ring in a giant root knot",
         "Teleport ring shortcut in a dead-end alcove (back-wall bank feeds misses out) vs long route (banked corners, climb)", (190, 0, -10))
h.rect("lane", -3.5, 3.5, 2, -8, 0.0, zone="lane")
h.rect("junction", -20, 9, -8, -15, 0.0, zone="junction")
if S8 < 9.0:
    h.rect("c1", -20, -13, -15, -24 + S8, 0.0, zone="climb")
h.rect("c2", -20, -13, -24 + S8, -38 + S8, zone="climb", slope=("z", 0.0, 1.5))
h.rect("c3", -20, -13, -38 + S8, -52 + S8, 1.5, zone="top")
h.rect("conn", -13, -6, -45 + S8, -52 + S8, 1.5, zone="top")
h.rect("green", -6, 10, -41 + S8, -57 + S8, 1.5, zone="green")
h.bank_wall("bank1", (-13.5, -8.0), (-20.0, -14.5), "L", zone="junction")
h.bank_wall("bank2", (-20.0, -45.5 + S8), (-13.5, -52.0 + S8), "L", base_y=1.5, zone="top")
H8_BANK_X = K("h8_bank_x", 7.7)
if H8_BANK_X:
    # alcove back-wall bank: low edge along x=H8_BANK_X, rising east to the back rail
    p = h.bank("alcove_bank", (H8_BANK_X, -8.0), (H8_BANK_X, -15.0), 9.0 - H8_BANK_X, K("h8_bank_rise", 0.5), "R", zone="junction", ext=0.0)
h.wall_path([(-3.5, 2), (-3.5, -8), (-20, -8), (-20, -52 + S8), (-6, -52 + S8), (-6, -57 + S8), (10, -57 + S8), (10, -41 + S8), (-6, -41 + S8),
             (-6, -45 + S8), (-13, -45 + S8), (-13, -15), (9, -15), (9, -8), (3.5, -8), (3.5, 2)],
            [0, 0, 0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0, 0, 0, 0, 0], out="L", closed=True, ybot=-0.5, top=3.9)
H8_EXIT = K("h8_exit", [9.0, 1.5, -56.0 + S8])
H8_CUP = K("h8_cup", [4.0, 1.5, -46.0 + S8])
h.teleport("ring", [7.0, 0.0, -11.5], R8, H8_EXIT, K("h8_exit_dir", (H8_CUP[0] - H8_EXIT[0], H8_CUP[2] - H8_EXIT[2])), speed_factor=K("h8_sf", 0.7), min_speed=K("h8_vmin", 4.0), max_speed=K("h8_vmax", 8.5),
           visual="Glowing firefly ring in a root knot (entry) -> ring of fireflies on the green (exit)")
# Round 7: the door is a gate: closed (centred on the ring line z=-11.5, offset 0) for 1.8 s, slides 4.0 south into the root-knot
# pocket at 3 studs/s, open for 2.2 s, slides back. 3.2 -> 3.6 long.
H8_DR = K("h8_door_range", (0.0, 4.0))  # door offset range along +Z (south); slides into a pocket in the root-knot wall
h.slider("root_door", [4.75, 0.0, -11.5], [0, 0, 1], K("h8_door_speed", 3.0), list(H8_DR),
         [dict(center=[0, 0.5, 0], size=[0.7, 1.0, K("h8_door_len", 3.6)], yaw=0.0)], phase=K("h8_door_phase", 0.0),
         dwell=K("h8_door_dwell", [(0.0, 1.8), (4.0, 2.2)]), visual="Sliding root door across the alcove mouth")
h.tee(0, 0, 0)
h.cup(*H8_CUP, flag_h=7.5)
h.d["cup_from"] = ["green", "top"]
h.wp("good", "ring_bank", [5.69, 0.0, -14.6], ["lane"], carry=14.0)
h.wp("good", "ring", [7.0, 0.0, -11.5], ["junction"], carry=K("h8_ring_carry", 14.0))
h.wp("average", "lane_top", [-2.5, 0.0, -12.0], ["lane"], carry=0.0)
h.wp("average", "corner", [-16.0, 0.0, -11.5], ["junction"], carry=K("h8_corner_carry", 6.0))
h.wp("average", "top", [-16.5, 1.5, K("h8_top_z", -46.0) + S8], ["junction", "climb"], carry=K("h8_top_carry", 12.0),
     power_scale=K("h8_top_ps", 1.1))
h.wp("average", "conn", [-9.5, 1.5, -48.5 + S8], ["top"], carry=6.0)
h.anchor("root_knot_ring", [8.5, 0, -11.5], "Root knot arch with a glowing firefly ring (teleport entry); the ring's glow disc is "
         f"{2 * R8:g} studs across", landmark=True, size=[3, 4, 4])
h.anchor("alcove_bank_cladding", [(H8_BANK_X + 9.0) / 2, 0, -11.5], "Root-bark cladding on the alcove back-wall bank (banked plane "
         f"x {H8_BANK_X:g}..9, rising east), 7 long", size=[9.0 - H8_BANK_X, 0.6, 7])
h.anchor("exit_ring", H8_EXIT, "Matching firefly ring on the upper green (teleport exit)", size=[2.5, 3, 1])
h.anchor("hollow_tree_base", [20, 0, -35], "Base of the giant hollow tree, roots arching over the course", size=[30, 40, 30])
h.anchor("glow_shrooms", [-17, 0, -20], "Glowing mushrooms along the climb", size=[2, 1.5, 2])
holes.append(h)

# ---------------------------------------------------------------- H9
# Round 5: the rotating lantern bar + post are replaced by a swinging lantern pendulum over the course's first rolling dip
# (two opposing planar slopes) in front of the heart well.
H9_DIP = K("h9_dip", 0.4)               # rolling dip through the trunk tunnel: depth below the corridor floor (y 1.0)
H9_X0, H9_XM, H9_X1 = K("h9_dip_x", (8.0, 11.0, 14.0))     # tunnel start, crease, tunnel end (= chamber edge)
yt = 1.0 - H9_DIP                       # crease height
H9_L = K("h9_len", 7.0)                 # pivot -> bob centre
BOB = K("h9_bob", [1.6, 1.8, 1.6])      # lantern bob box [x, y, z] (Round 7: 1.0 -> 1.6 deep, square lantern)
# bob bottom above the felt at rest: the tilted bob's lower corner dips (w/2)^2 / (2 (L + h/2)) below its rest height mid-swing
# (0.04 for the old 1.6-wide bob), so keep >= 0.02 of air under the corner at the deepest point
H9_BYAW = K("h9_bob_yaw", 30.0)          # bob turned about the vertical (45 = diamond in plan: hits kick the ball out of the swing plane)
H9_HX = BOB[0] / 2 * math.cos(math.radians(H9_BYAW)) + BOB[2] / 2 * math.sin(math.radians(H9_BYAW))  # bob half-extent along the swing
H9_GAP = round(max(0.06, 0.02 + H9_HX ** 2 / (2 * (H9_L + BOB[1] / 2))), 3)
# Round 8: hinge x 22.0 -> 21.2, right over the chamber shot line (in-engine the ball crosses z -38.5 at x 21.18), so the
# bob's low middle, not its rising edge, meets the ball
H9_PIV = [K("h9_piv_x", 21.2), round(1.0 + H9_GAP + BOB[1] / 2 + H9_L, 3), K("h9_piv_z", -38.5)]
# Round 8: invisible collider "foot" under the lantern body (same yaw, inside its footprint): narrow along the swing, so its
# corners dip only ~0.035 mid-swing and its bottom can hang 0.055 above the felt (below the ball centre, 0.08); the body's own
# bottom (0.096) is above the ball centre, and in-engine a bob that meets only the top of the ball lets it roll under
# Round 9: foot turned square to the swing (yaw 0) and widened 0.8 -> 0.9 along it: with no yaw its corners rise less over the
# swing, so it hangs 0.034 above the felt (was 0.055) and meets the ball lower; studio line 45% blocked (was 42% / 40% at 24 / 80 phases)
# Round 10: 1.0 x 0.4 x 1.6 = the foot as built in Studio v131 (blocked 15/48). Widening it doesn't help: the extra blocks are
# side/corner shoves that Studio carries on through. Only a face square to the shot line stops the ball reliably.
H9_FOOT = K("h9_foot", [1.0, 0.4, 1.6])
H9_FOOT_YAW = K("h9_foot_yaw", 0.0)
H9_FOOT_B, H9_FOOT_GAP = [], None
if H9_FOOT:
    _fhx = abs(H9_FOOT[0] / 2 * math.cos(math.radians(H9_FOOT_YAW))) + abs(H9_FOOT[2] / 2 * math.sin(math.radians(H9_FOOT_YAW)))
    _fr = H9_L + BOB[1] / 2 + H9_GAP  # hinge -> felt at rest
    H9_FOOT_GAP = math.ceil(1000 * max(0.03, 0.021 + _fhx ** 2 / (2 * _fr))) / 1000  # Round 9: +0.001 so rounding can't dip below 0.02
    H9_FOOT_B = [dict(center=[0, round(-_fr + H9_FOOT_GAP + H9_FOOT[1] / 2, 3), 0], size=H9_FOOT, yaw=H9_FOOT_YAW)]
h = Hole(9, "h09", "Heart of the Grove", 4, "Inside the Hollow Tree", "The giant hollow tree's lantern-lit heart",
         "Ramp + banked corner, rising root gate, rolling dip through the trunk tunnel, deflector, swinging lantern pendulum at the heart well, drop to a sloped heart green", (214, 2, -70))
h.rect("lane", -3.5, 3.5, 2, -12, 0.0, zone="lane")
h.rect("ramp", -3.5, 3.5, -12, -22, zone="lane", slope=("z", 0.0, 1.0))
h.rect("landing", -3.5, 3.5, -22, -29, 1.0, zone="landing")
h.rect("corr1", 3.5, 8, -22, -29, 1.0, zone="corridor")
h.rect("tunnel_in", H9_X0, H9_XM, -22, -29, zone="corridor", slope=("x", 1.0, yt), tunnel=True, kind="tunnel")
h.rect("tunnel_out", H9_XM, H9_X1, -22, -29, zone="corridor", slope=("x", yt, 1.0), tunnel=True, kind="tunnel")
h.rect("chamber", 14, 30, -18, -40, 1.0, zone="chamber")
h.rect("heart_slope", 14, 32, -40, -45, zone="heart", slope=("z", -0.5, -0.8))
h.rect("heart", 14, 32, -45, -54, -0.8, zone="heart")
h.bank_wall("bank1", (-3.5, -22.5), (3.0, -29.0), "L", base_y=1.0, zone="landing")
H9_M = K("h9_mouth", (18.0, 26.0))      # heart-well mouth (open drop edge) x range
h.drop("d1", "chamber", "heart", f"chamber north edge z=-40, x[{H9_M[0]:g},{H9_M[1]:g}]", 1.5)
h.wall_path([(H9_M[0], -40), (14, -40), (14, -29), (-3.5, -29), (-3.5, 2), (3.5, 2), (3.5, -22), (14, -22), (14, -18),
             (30, -18), (30, -40), (H9_M[1], -40)], [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
            out="R", ext=(0.0, 0.0), ybot=-1.0, top=3.4)
h.wall_path([(14, -40), (14, -54), (32, -54), (32, -40), (30, -40)], [-0.5, -0.8, -0.8, -0.5, -0.5], out="L", ext=(0.5, 0.5))
h.wall_free((16, -20), (30, -34), 1.0, name="root_deflector", ext=0.5)
H9_GATE = K("h9_gate", (0.9, 1.8))     # (speed studs/s, top of travel)
h.slider("root_gate", [6, 1.0, -25.5], [0, 1, 0], H9_GATE[0], [0.0, H9_GATE[1]],
         [dict(center=[0, 0.4, 0], size=[0.8, 1.4, 7.4], yaw=0.0)], visual="Root portcullis rising/falling 0..1.8 in the tunnel mouth (open ~70% of its 4 s cycle)")
# Round 10: swing 13 -> 11 deg (period 4 s): the foot's square north face sits over the shot line longer (18% -> 22% of
# the cycle), so more balls are stopped head-on. Studio-calibrated estimate (sweep_r10.py) 35% (Studio measured 31%) -> 44%
H9_AMP = K("h9_amp", 11.0)
h.swing("lantern_pendulum", H9_PIV, [0, 0, 1], H9_AMP, K("h9_period", 4.0),
        [dict(center=[0, -H9_L, 0], size=BOB, yaw=H9_BYAW)] + H9_FOOT_B,
        visual=f"Great lantern on a {H9_L:g}-stud chain from a root beam, swinging east-west across the heart-well mouth "
               f"(1.5 studs before the drop edge); the bob ({BOB[0]:g}x{BOB[1]:g}x{BOB[2]:g} box turned {H9_BYAW:g} deg about the vertical, "
               f"{2 * H9_HX:.2f} across the swing) skims the felt at the bottom of its swing and swings clear of the shot line (x 21.2) near the ends"
               + (f"; blocker 2 = invisible collider foot {H9_FOOT[0]:g}x{H9_FOOT[1]:g}x{H9_FOOT[2]:g} (yaw {H9_FOOT_YAW:g}: square to the swing) under "
                  f"the lantern body, bottom {H9_FOOT_GAP:g} above the felt at rest (body bottom {H9_GAP:g}); its corners poke out past the "
                  f"lantern's faces, so the lantern mesh gets a matching base plinth" if H9_FOOT_B else ""))
if K("h9_pend2", None):  # Round 10 sweep only: second pendulum [dx, dz, phase_deg] off the first hinge (same lantern + foot)
    _d = K("h9_pend2", None)
    h.swing("lantern_pendulum_2", [H9_PIV[0] + _d[0], H9_PIV[1], H9_PIV[2] + _d[1]], [0, 0, 1], H9_AMP, K("h9_period", 4.0),
            [dict(center=[0, -H9_L, 0], size=BOB, yaw=H9_BYAW)] + H9_FOOT_B, visual="second lantern pendulum (sweep variant)", phase=_d[2])
H9_CUP = K("h9_cup", [26.0, -0.8, -52.0])
H9_KX = [15.0, -0.8, -52.0]             # knot exit, aimed at the cup
h.teleport("lantern_knot", [6.5, 1.0, -23.0], 0.3, H9_KX, (H9_CUP[0] - H9_KX[0], H9_CUP[2] - H9_KX[2]), speed_factor=1.0, min_speed=4.0,
           max_speed=10.0, visual="Secret: a glowing knot-hole in the corridor floor at (6.5, 1.0, -23.0), 0.5 stud past (east of) the root gate "
                                  "and 1 stud in from the corridor's south rail (z=-22); exit knot in the heart green's north-west corner (15, -52)")
h.tee(0, 0, 0)
h.cup(*H9_CUP, flag_h=8.0)
h.d["cup_from"] = ["heart"]
h.wp("all", "bank", [-1.0, 1.0, -25.0], ["lane"], carry=24.0)
h.wp("all", "deflect", [21.0, 1.0, -26.0], ["landing", "corridor"], carry=15.0)
h.wp("all", "drop", [21.5, 1.0, -40.0], ["chamber"], carry=3.0)
h.anchor("hollow_tree", [22, -0.5, -36], "Giant hollow tree: trunk ~34 across, chamber is inside it, opening above the heart", landmark=True, size=[34, 60, 34])
h.anchor("trunk_tunnel", [11, 1.0, -25.5], "Arched tunnel through a root buttress (opening 7 wide x 3 high above the corridor level, solid above y 4 up to y 6); "
         "the felt inside dips 0.4 (rolling dip)", size=[7, 5, 8],
         occluders=[((11, 5.0, -25.5), (6, 2, 8))])
# Round 7: the heart green is lit by 3 hanging amber lanterns (decoration only, no collision). Bottoms 8 studs above the green felt
# (y 7.2 local = 2.4 m: above a VR player's head, the ball and the flag top), >= 3.9 studs (box edge) from the tee->flag sightline,
# >= 7.6 from the pendulum bob's sweep and >= 6.3 north of its swing plane (z -38.5), so nothing can touch them.
H9_LANT = [(18.5, -47.5), (28.5, -46.5), (20.0, -51.5)]
H9_LANT_BOT = -0.8 + 8.0
for i, (lx, lz) in enumerate(H9_LANT, 1):
    h.anchor(f"amber_lantern_{i}", [lx, H9_LANT_BOT, lz], f"Hanging amber paper lantern {i}/3 lighting the heart green (warm PointLight); "
             f"bottom at y {H9_LANT_BOT:g} = 8 studs above the green felt, chain up into the trunk canopy (y ~16). Decoration only, no collision",
             size=[1.2, 1.8, 1.2], occluders=[((lx, H9_LANT_BOT + 0.9, lz), (1.2, 1.8, 1.2))])
h.anchor("lantern_knot", [6.5, 1.0, -23.0], "Secret glowing knot-hole in the corridor floor at (6.5, 1.0, -23.0): 0.5 stud past (east of) "
         "the root gate at x=6 and 1 stud in from the corridor's south rail (z=-22). Teleport entry r 0.3; the exit knot is in the heart "
         "green's north-west corner (15, -0.8, -52)", size=[1.2, 1.2, 0.6])
h.anchor("lantern_knot_exit", [15.0, -0.8, -52.0], "Matching small glowing knot on the heart green's north-west corner (teleport exit)", size=[1.0, 0.3, 1.0])
h.anchor("well_rim", [(H9_M[0] + H9_M[1]) / 2, 1.0, -40], "Carved root rim along the heart-well drop edge", size=[H9_M[1] - H9_M[0], 0.6, 1])
h.anchor("pendulum_beam", [22.0, H9_PIV[1], H9_PIV[2]], "Root beam spanning the chamber high above the heart-well mouth (x 14..30), "
         f"hinge of the lantern pendulum on it at x {H9_PIV[0]:g}", size=[16, 1.2, 1.2])
h.anchor("dip_cladding", [H9_XM, yt, -25.5], f"Root-and-moss trim on the tunnel rails following the rolling dip (felt dips {H9_DIP:g} studs: "
         f"down x {H9_X0:g}..{H9_XM:g}, back up {H9_XM:g}..{H9_X1:g})", size=[H9_X1 - H9_X0, 0.4, 7])
h.anchor("glow_mushrooms", [30, -0.5, -52], "Bioluminescent mushrooms ring", size=[3, 2, 3])
holes.append(h)

course = {
    "course": "Lantern Grove",
    "schema": SCHEMA,
    "physics": {"source": "RobloxDevBot real game values (mirrored as constants in tools/sim.py)",
                "stud_m": S.STUD_M, "gravity_studs_s2": S.GRAVITY,
                "rolling_decel": "0.5 + 0.25*speed studs/s^2", "rolling_decel_const": S.ROLL_DECEL_CONST,
                "rolling_decel_per_speed": S.ROLL_DECEL_PER_SPEED, "wall_restitution": S.WALL_RESTITUTION,
                "bumper_restitution": S.BUMPER_RESTITUTION, "cup_capture_speed_studs_s": S.CUP_CAPTURE_SPEED,
                "cup_radius": S.CUP_RADIUS, "ball_radius": S.BALL_RADIUS, "max_putt_speed_studs_s": S.V_MAX,
                "max_putt_flat_roll_studs": S.MAX_PUTT_STUDS,
                "max_putt_note": "V_MAX derived so a full putt rolls 60 studs (18 m) on flat felt = longest single-stroke run any hole needs (H6/H9 ace lines)",
                "drop_speed_keep": 0.8},
    "total_par": sum(x.d["par"] for x in holes),
    "holes": [x.d for x in holes],
}
with open(OUT, "w") as f:
    json.dump(course, f, indent=1)
print(f"wrote {os.path.normpath(OUT)}: {len(holes)} holes, total par {course['total_par']}")
