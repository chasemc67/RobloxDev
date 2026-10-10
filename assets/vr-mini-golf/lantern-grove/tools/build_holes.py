#!/usr/bin/env python3
"""Source of truth for ../holes.json. Edit here, then: python3 tools/build_holes.py
Every playtest-round change is made in this file and logged in playtest-log.md."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from geom import Hole, arm_blockers, T
import sim as S

OUT = os.path.join(os.path.dirname(__file__), "..", "holes.json")

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
               "reset:'previous_position', penalty:1}. A ball that leaves the felt over a hazard is returned to where its "
               "stroke started and +1 stroke is added. Any ball leaving all felt elsewhere is treated the same (and flagged as an escape bug).",
    "drops": "Intentional level changes: {id, from, to, edge, height}. The upper piece's edge is open (no rail) and the lower felt "
             "starts directly below/beyond it; the ball falls and keeps ~80% of horizontal speed. Lower felt may extend under the "
             "upper piece (the upper piece then acts as a cliff face for the lower level).",
    "moving_parts": "Separate parts. {id, type:'rotate'|'slide', pivot:[x,y,z], axis:[ax,ay,az] unit vector, speed (deg/s for rotate, "
                    "studs/s for slide, sign = direction, right-hand rule about axis), range:null (continuous) | [min,max] "
                    "(ping-pong between angles in deg or offsets in studs), phase (angle/offset at t=0), blockers:[{center:[dx,dy,dz] "
                    "relative to pivot at angle/offset 0, size:[sx,sy,sz], yaw, roll?}]} (roll = extra initial rotation in deg about the part axis, "
                    "applied to the blocker's centre and orientation, e.g. wheel paddles at 0/120/240). At time t a blocker is "
                    "pivot + Rot(axis, angle(t)) * center (rotate) or pivot + center + axis*offset(t) (slide).",
    "teleports": "{id, entry:{center:[x,y,z], radius}, exit:{center:[x,y,z], dir:[dx,dz]}, speed_factor, min_speed, max_speed}. A ball "
                 "whose centre enters the entry radius (same level) reappears at exit moving along dir with "
                 "speed = clamp(speed_in*speed_factor, min_speed, max_speed).",
    "cup": "{position:[x,y,z] (on felt), radius}. Gameplay cup radius 0.5 stud (real cup 4.25 in = 0.36 stud diameter; enlarged ~2.8x for VR "
           "readability). Ball is holed when its centre is within radius and speed < 5.33 studs/s (1.6 m/s).",
    "ball": "radius 0.08 stud (~real 42.7 mm ball at 0.3 m/stud). Full physics constants in the top-level 'physics' block (= tools/sim.py).",
    "tee": "{position:[x,y,z], aim_hint:[dx,dz]}",
    "ai_waypoints": "{skill|'all': [{id, pos:[x,y,z], from:[zones], carry, power_scale}]} used by the sim golfer: from its current zone it "
                    "aims at the furthest allowed target with line of sight (cup first, then waypoints last->first) and hits for "
                    "distance + carry. cup_from (list of zones or null=all) limits when it goes straight for the cup.",
    "decoration_anchors": "{name, position:[x,y,z], notes, landmark?, approx_size?} - visual only, no collision.",
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
h.cup(-9.5, 0.5, -26.5)
h.wp("all", "deflect", [0.0, 0.5, -32.0], ["lane"], carry=8.0)
h.anchor("lantern_gate", [0, 0.25, -21], "Torii-style timber arch over the ramp, 2 paper lanterns hanging inside", landmark=True, size=[9, 7, 1.2])
h.anchor("mossy_boulder", [-8, 0.5, -21], "Big mossy boulder outside the green's front-left rail", size=[4, 3, 4])
h.anchor("welcome_sign", [-6, 0, 1], "Carved 'Lantern Grove - Hole 1' sign post", size=[2, 3, 0.4])
h.anchor("maple_tree", [8, 0, -15], "Red maple outside right rail", size=[10, 16, 10])
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
h.cup(2.5, -1.5, -35)
h.wp("good", "chute_left", [-2.75, 0.0, -20.0], ["lane"], carry=5.0)
h.wp("average", "chute_right", [2.75, 0.0, -20.0], ["lane"], carry=5.0)
h.anchor("giant_acorn", [0, 0.0, -19.5], "Giant acorn (cap + nut) sitting on the stump between the chutes", landmark=True, size=[3, 4, 3])
h.anchor("rabbit_hole_rim", [-5, -1.5, -30], "Rabbit-hole rim of roots and moss around the pit", size=[3, 0.5, 3])
h.anchor("squirrel_hut", [11, -1.5, -28], "Tiny squirrel hut on a post outside the right rail", size=[3, 5, 3])
h.anchor("ledge_lanterns", [-4.5, 0, -19.5], "Lantern posts at both chute edges", size=[0.5, 3, 0.5])
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
h.cup(15.5, 0.0, -30.5)
h.wp("good", "corner1", [-1.0, 0.0, -11.5], ["lane"], carry=16.0)
h.wp("average", "corner1", [-1.0, 0.0, -11.5], ["lane"], carry=14.0)
h.wp("all", "corner2", [18.0, 0.0, -12.0], ["cross"], carry=12.0)
h.wp("all", "green_in", [17.5, 0.0, -24.5], ["leg"], carry=1.0)
h.anchor("stem_house", [8.5, 0, -12], "Red-cap mushroom house; felt tunnel runs through its stem (5 long, 3 high opening)", landmark=True, size=[10, 12, 10])
h.anchor("small_toadstools", [-6, 0, -6], "Cluster of 3 small toadstools", size=[3, 2.5, 3])
h.anchor("house_2", [26, 0, -14], "Second mushroom house with round window", size=[7, 9, 7])
h.anchor("toadstool_stool_deco", [17.0, 0, -28.8], "Fat spotted toadstool stool guarding the cup (bumper block 1.6x1.5x1.6)", size=[2, 1.8, 2])
h.anchor("lantern_string", [17.5, 4, -22], "Lantern string across green entrance", size=[12, 1, 0.3])
holes.append(h)

# ---------------------------------------------------------------- H4
h = Hole(4, "h04", "Spore Spinner", 3, "Mushroom Village", "Spinning puffball carousel",
         "Rotating 2-arm spinner bar in a plaza, then ramp up to a raised green", (52, 1, -60))
h.rect("lane", -4, 4, 2, -14, 0.0, zone="lane")
h.rect("plaza", -7, 7, -14, -28, 0.0, zone="plaza")
h.rect("ramp", -5, 5, -28, -36, zone="ramp", slope=("z", 0.0, 0.6))
h.rect("green", -6, 6, -36, -46, 0.6, zone="green")
h.wall_path([(-4, 2), (-4, -14), (-7, -14), (-7, -28), (-5, -28), (-5, -36), (-6, -36), (-6, -46), (6, -46), (6, -36),
             (5, -36), (5, -28), (7, -28), (7, -14), (4, -14), (4, 2)],
            [0, 0, 0, 0, 0, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0, 0, 0, 0, 0], out="L", closed=True)
h.block("hub", 0, -21, 1.4, 1.4, 0.0, height=2.0)
h.rotor("spinner", [0, 0, -21], [0, 1, 0], 36.0, arm_blockers(2, 0.7, 4.5, 0.7, 1.0), visual="2 puffball-stalk arms (one long bar) on a toadstool hub")
h.tee(0, 0, 0)
h.cup(2.5, 0.6, -42.0)
h.wp("all", "ramp", [1.8, 0.3, -32.0], ["lane", "plaza"], carry=11.0)
h.anchor("puffball_carousel", [0, 0, -21], "Toadstool hub with a 2-arm puffball bar (moving mesh, pivot at hub centre)", landmark=True, size=[9, 4, 9])
h.anchor("mushroom_house_L", [-12, 0, -21], "Mushroom house beside plaza", size=[8, 10, 8])
h.anchor("mushroom_house_R", [12, 0, -24], "Mushroom house beside plaza", size=[7, 9, 7])
h.anchor("green_lanterns", [-7, 0.6, -41], "Lantern posts flanking raised green", size=[0.5, 3.5, 0.5])
holes.append(h)

# ---------------------------------------------------------------- H5
h = Hole(5, "h05", "Rootbridge Crossing", 3, "Stream Crossing", "Arched root bridge over the stream",
         "Split path: narrow rail-less root bridge straight from the tee (risk) vs covered plank bridge (safe), water hazard", (96, -1, -10))
h.rect("shore", -15, 6, 2, -15, 0.0, zone="shore")
h.rect("root1", -0.9, 0.9, -15, -21.5, zone="root", slope=("z", 0.0, 0.4), kind="bridge")
h.rect("root2", -0.9, 0.9, -21.5, -28, zone="root", slope=("z", 0.4, 0.0), kind="bridge")
h.rect("covered", -13, -8, -15, -28, 0.0, zone="covered", kind="bridge")
h.rect("north", -15, 6, -28, -42, 0.0, zone="north")
h.hazard("stream", "water", -17, 8, -15, -28, -1.0)
h.wall_path([(-8, -15), (-0.9, -15)], 0.0, out="L", ext=(0.0, 0.0))
h.wall_path([(0.9, -15), (6, -15), (6, 2), (-15, 2), (-15, -15), (-13, -15)], 0.0, out="L", ext=(0.0, 0.0))
h.wall_path([(-13, -15), (-13, -28)], 0.0, out="L")
h.wall_path([(-8, -28), (-8, -15)], 0.0, out="L")
h.wall_path([(-13, -28), (-15, -28), (-15, -42), (6, -42), (6, -28), (0.9, -28)], 0.0, out="L", ext=(0.0, 0.0))
h.wall_path([(-0.9, -28), (-8, -28)], 0.0, out="L", ext=(0.0, 0.0))
h.tee(0, 0, 0)
h.cup(1.5, 0.0, -37.0)
h.d["cup_from"] = ["north"]
h.wp("good", "root_far", [0.0, 0.0, -29.0], ["shore", "root"], carry=4.0)
h.wp("average", "covered_line", [-10.5, 0.0, -9.0], ["shore"], carry=0.0)
h.wp("average", "covered_out", [-10.5, 0.0, -29.0], ["shore", "covered"], carry=3.0)
h.anchor("root_bridge", [0, 0.2, -21.5], "Gnarled arched root bridge (no rails), felt on top, 1.8 wide", landmark=True, size=[3.5, 3, 14])
h.anchor("covered_bridge", [-10.5, 0, -21.5], "Plank covered bridge with shingle roof and lanterns", size=[7, 6, 14])
h.anchor("stream_rocks", [4, -1, -21], "Mossy stepping stones in the stream", size=[2, 1, 2])
h.anchor("waterfall_bg", [10, -1, -21], "Small waterfall feeding the stream (upstream, right side)", size=[6, 8, 3])
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
h.cup(16.5, 0.25, -22.5)
h.wp("good", "board1", [0.0, 0.0, -8.0], ["lane"], carry=40.0)
h.wp("average", "board1", [0.0, 0.0, -8.0], ["lane"], carry=14.0)
h.wp("all", "board2", [15.0, 0.0, -9.0], ["channel"], carry=12.0, power_scale=1.25)
h.anchor("water_mill", [7.5, 0, 0], "Timber mill house on the south side; wheel axle enters it", landmark=True, size=[9, 10, 8])
h.anchor("mill_wheel", [7.5, 3.6, -8.5], "Wheel mesh (moving part) radius 3.6, axle along Z", size=[1, 7.2, 8])
h.anchor("waterfall", [24, 0.25, -24], "Waterfall cascading down rocks east of the green", size=[6, 12, 4])
h.anchor("sacks", [-6, 0, -6], "Flour sacks & crates", size=[2, 1.5, 2])
holes.append(h)

# ---------------------------------------------------------------- H7
h = Hole(7, "h07", "Cascade Steps", 3, "Waterfall Terraces", "Three-tier waterfall beside stepped greens",
         "Two drops down terraces, sliding log on the middle tier, waterfall-pool hazard, side-sloped bottom green", (144, -3, -40))
h.rect("t1", -4, 4, 2, -14, 0.0, zone="t1")
h.rect("t2", -10, 10, -14, -27, -1.2, zone="t2")
h.rect("t3", -8, 1, -27, -40, -2.4, zone="t3")
h.rect("t3_slope", 1, 10, -27, -40, zone="t3", slope=("x", -2.4, -2.0))
h.hazard("pool", "water", -14, -10, -16, -26, -3.0)
h.drop("d1", "t1", "t2", "t1 north edge z=-14, full width", 1.2)
h.drop("d2", "t2", "t3", "t2 north edge z=-27, gap x[3.5,7] (lands on the sloped east half of t3)", 1.0)
h.wall_path([(4, -14), (4, 2), (-4, 2), (-4, -14)], 0.0, out="L", ybot=-1.7)
h.wall_path([(-4, -14), (-10, -14), (-10, -18)], -1.2, out="L", ext=(0.5, 0.0))
h.wall_path([(-10, -24), (-10, -27), (3.5, -27)], -1.2, out="L", ext=(0.0, 0.0), ybot=-2.9)
h.wall_path([(7, -27), (10, -27), (10, -14), (4, -14)], -1.2, out="L", ext=(0.0, 0.5), ybot=-2.9)
h.wall_path([(-8, -27), (-8, -40), (10, -40), (10, -27)], [-2.4, -2.4, -2.0, -2.0], out="L", ext=(0.5, 0.5))
h.slider("log", [0, -1.2, -20.5], [1, 0, 0], 5.0, [-6.0, 6.0],
         [dict(center=[0, 0.4, 0], size=[5.0, 0.8, 0.8], yaw=0.0)], visual="Floating log on a hidden rail")
h.tee(0, 0, 0)
h.cup(-2.5, -2.4, -31.0)
h.wp("all", "gap", [5.25, -1.2, -27.0], ["t1", "t2"], carry=5.0)
h.anchor("cascade", [-16, -3, -18], "Three-step waterfall dropping into the pool on the left", landmark=True, size=[8, 14, 10])
h.anchor("log_rail", [0, -1.2, -20.5], "Floating log (moving mesh) on a hidden rail across the middle tier", size=[5, 0.8, 0.8])
h.anchor("ferns", [12, -2.4, -34], "Fern clumps and red leaves", size=[3, 2, 3])
h.anchor("step_lanterns", [4.5, -1.2, -27], "Lanterns flanking the lower gap", size=[0.5, 3, 0.5])
holes.append(h)

# ---------------------------------------------------------------- H8
h = Hole(8, "h08", "Firefly Hollow", 4, "Hollow Tree Roots", "Firefly ring in a giant root knot",
         "Teleport ring shortcut in a dead-end alcove vs long route (banked corners, long ramp)", (190, 0, -10))
h.rect("lane", -3.5, 3.5, 2, -8, 0.0, zone="lane")
h.rect("junction", -20, 9, -8, -15, 0.0, zone="junction")
h.rect("c1", -20, -13, -15, -24, 0.0, zone="climb")
h.rect("c2", -20, -13, -24, -38, zone="climb", slope=("z", 0.0, 1.5))
h.rect("c3", -20, -13, -38, -52, 1.5, zone="top")
h.rect("conn", -13, -6, -45, -52, 1.5, zone="top")
h.rect("green", -6, 10, -41, -57, 1.5, zone="green")
h.bank_wall("bank1", (-13.5, -8.0), (-20.0, -14.5), "L", zone="junction")
h.bank_wall("bank2", (-20.0, -45.5), (-13.5, -52.0), "L", base_y=1.5, zone="top")
h.wall_path([(-3.5, 2), (-3.5, -8), (-20, -8), (-20, -52), (-6, -52), (-6, -57), (10, -57), (10, -41), (-6, -41),
             (-6, -45), (-13, -45), (-13, -15), (9, -15), (9, -8), (3.5, -8), (3.5, 2)],
            [0, 0, 0, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0, 0, 0, 0, 0], out="L", closed=True, ybot=-0.5, top=3.9)
h.teleport("ring", [7.0, 0.0, -11.5], 0.35, [-4.0, 1.5, -56.0], (12, 12.5), speed_factor=1.2, min_speed=4.0, max_speed=8.5,
           visual="Glowing firefly ring in a root knot (entry) -> ring of fireflies on the green (exit)")
h.slider("root_door", [4.75, 0.0, -11.5], [0, 0, 1], 2.0, [-2.5, 2.5],
         [dict(center=[0, 0.5, 0], size=[0.7, 1.0, 3.2], yaw=0.0)], visual="Sliding root door across the alcove mouth")
h.tee(0, 0, 0)
h.cup(8.0, 1.5, -43.5)
h.d["cup_from"] = ["green", "top"]
h.wp("good", "ring_bank", [5.69, 0.0, -14.6], ["lane"], carry=14.0)
h.wp("good", "ring", [7.0, 0.0, -11.5], ["junction"], carry=14.0)
h.wp("average", "lane_top", [-2.5, 0.0, -12.0], ["lane"], carry=0.0)
h.wp("average", "corner", [-16.0, 0.0, -11.5], ["junction"], carry=18.0)
h.wp("average", "climb", [-16.5, 0.0, -30.0], ["junction", "climb"], carry=12.0, power_scale=1.1)
h.wp("average", "top", [-16.0, 1.5, -48.0], ["climb"], carry=6.0, power_scale=1.1)
h.wp("average", "conn", [-9.5, 1.5, -48.5], ["top"], carry=6.0)
h.anchor("root_knot_ring", [8.5, 0, -11.5], "Root knot arch with a glowing firefly ring (teleport entry)", landmark=True, size=[3, 4, 4])
h.anchor("exit_ring", [-4.0, 1.5, -56.0], "Matching firefly ring on the upper green (teleport exit)", size=[2.5, 3, 1])
h.anchor("hollow_tree_base", [20, 0, -35], "Base of the giant hollow tree, roots arching over the course", size=[30, 40, 30])
h.anchor("glow_shrooms", [-17, 0, -20], "Glowing mushrooms along the climb", size=[2, 1.5, 2])
holes.append(h)

# ---------------------------------------------------------------- H9
h = Hole(9, "h09", "Heart of the Grove", 4, "Inside the Hollow Tree", "The giant hollow tree's lantern-lit heart",
         "Ramp + banked corner, rising root gate in a trunk tunnel, deflector, rotating lantern bar over the heart well, drop to a sloped heart green", (214, 2, -70))
h.rect("lane", -3.5, 3.5, 2, -12, 0.0, zone="lane")
h.rect("ramp", -3.5, 3.5, -12, -22, zone="lane", slope=("z", 0.0, 1.0))
h.rect("landing", -3.5, 3.5, -22, -29, 1.0, zone="landing")
h.rect("corr1", 3.5, 8, -22, -29, 1.0, zone="corridor")
h.rect("tunnel", 8, 14, -22, -29, 1.0, zone="corridor", tunnel=True, kind="tunnel")
h.rect("chamber", 14, 30, -18, -40, 1.0, zone="chamber")
h.rect("heart_slope", 14, 32, -40, -45, zone="heart", slope=("z", -0.5, -0.8))
h.rect("heart", 14, 32, -45, -54, -0.8, zone="heart")
h.bank_wall("bank1", (-3.5, -22.5), (3.0, -29.0), "L", base_y=1.0, zone="landing")
h.drop("d1", "chamber", "heart", "chamber north edge z=-40, x[18,26]", 1.5)
h.wall_path([(18, -40), (14, -40), (14, -29), (-3.5, -29), (-3.5, 2), (3.5, 2), (3.5, -22), (14, -22), (14, -18),
             (30, -18), (30, -40), (26, -40)], [1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1],
            out="R", ext=(0.0, 0.0), ybot=-1.0, top=3.4)
h.wall_path([(14, -40), (14, -54), (32, -54), (32, -40), (30, -40)], [-0.5, -0.8, -0.8, -0.5, -0.5], out="L", ext=(0.5, 0.5))
h.wall_free((16, -20), (30, -34), 1.0, name="root_deflector", ext=0.5)
h.slider("root_gate", [6, 1.0, -25.5], [0, 1, 0], 0.6, [0.0, 1.2],
         [dict(center=[0, 0.4, 0], size=[0.8, 1.4, 7.4], yaw=0.0)], visual="Root portcullis rising/falling in the tunnel mouth (open ~62% of the cycle)")
h.block("lantern_post", 25.0, -36.5, 0.8, 0.8, 1.0, height=2.5)
h.rotor("lantern_bar", [25.0, 1.0, -36.5], [0, 1, 0], 40.0,
        [dict(center=[0, 0.5, 0], size=[6.0, 1.0, 0.6], yaw=0.0)], visual="Rotating bar on the lantern post guarding the heart well, lanterns at both ends")
h.teleport("lantern_knot", [6.5, 1.0, -23.0], 0.3, [15.0, -0.8, -52.0], (7, 2), speed_factor=1.0, min_speed=4.0,
           max_speed=10.0, visual="Secret: a glowing knot-hole low in the corridor's south-west corner drops you onto the heart green")
h.tee(0, 0, 0)
h.cup(22.0, -0.8, -50.0)
h.d["cup_from"] = ["heart"]
h.wp("all", "bank", [-1.0, 1.0, -25.0], ["lane"], carry=24.0)
h.wp("all", "deflect", [21.0, 1.0, -26.0], ["landing", "corridor"], carry=15.0)
h.wp("all", "drop", [21.5, 1.0, -40.0], ["chamber"], carry=3.0)
h.anchor("hollow_tree", [22, -0.5, -36], "Giant hollow tree: trunk ~34 across, chamber is inside it, opening above the heart", landmark=True, size=[34, 60, 34])
h.anchor("trunk_tunnel", [11, 1.0, -25.5], "Arched tunnel through a root buttress", size=[7, 5, 8])
h.anchor("heart_lanterns", [23, 4, -47], "Dozens of hanging lanterns inside the heart", size=[16, 6, 12])
h.anchor("lantern_knot", [6.5, 1.0, -23.0], "Secret glowing knot-hole in the corridor floor just past the root gate (teleport entry); exit is a knot in the heart's south-west corner", size=[1.2, 1.2, 0.6])
h.anchor("well_rim", [22, 1.0, -40], "Carved root rim along the heart-well drop edge", size=[8, 0.6, 1])
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
