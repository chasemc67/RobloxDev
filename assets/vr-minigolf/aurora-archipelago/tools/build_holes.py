#!/usr/bin/env python3
"""Source of truth for ../holes.json (Aurora Archipelago, 18 holes). Edit here, then: python3 tools/build_holes.py
Adapted from sugarloaf-canyon/tools/build_holes.py (itself from Lantern Grove). Every round's change is made in this file and logged in
playtest-log.md.

Placement: each hole's world_offset / world_yaw are read from ../world/world.json (holes[].placement = {origin, yaw_deg}), so
holes.json and the world layout can't drift apart. Local frame: tee at the origin, play toward local -Z. Every felt piece, rail
and moving part must fit inside the hole's world.json concept pads (checked at the end of this script: `fit` report).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from geom import Hole, arm_blockers, T, offset_polyline, turn_deg, rot
import math
r4 = lambda v: round(v, 4)
import sim as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("SC_OUT") or os.path.join(HERE, "..", "holes.json")
# Sweep hook (tools/sweep.py): SC_VARIANT='{"h11_dwell": [1.5, 2.0], ...}' overrides the tuning knobs below; SC_OUT writes elsewhere.
VAR = json.loads(os.environ.get("SC_VARIANT") or "{}")
WORLD = json.load(open(os.path.join(HERE, "..", "world", "world.json")))
PLACE = {h["number"]: h for h in WORLD["holes"]}
ICE_DECEL_SCALE = 0.35   # H4 ice felt: start value from course.md; NEEDS STUDIO CALIBRATION (fire a fixed putt, measure the roll)


def K(key, default):
    """tuning knob (default = the committed value)"""
    return VAR.get(key, default)


def collision_cut(h, ids, lo, hi, mover):
    """Subtract a hole-local AABB from axis-aligned boxes, retaining exact residual boxes (sliding-floe pocket, H11)."""
    h.d.setdefault("collision_cuts", []).append(dict(mover=mover, targets=ids, min=lo, max=hi, clearance=0.15))
    for collection in ("walls", "felt"):
        result = []
        for b in h.d[collection]:
            if b["id"].split("__cut")[0] not in ids:
                result.append(b); continue
            assert abs(b.get("yaw", 0) % 90) < .001
            c = b["center"]; felt = collection == "felt"
            sz = [b["size"][0], b.get("thickness", .4), b["size"][1]] if felt else b["size"][:]
            if int(round(b.get("yaw", 0) / 90)) % 2: sz[0], sz[2] = sz[2], sz[0]
            a = [c[k] - sz[k] / 2 for k in range(3)]; z = [c[k] + sz[k] / 2 for k in range(3)]
            if felt: a[1] = c[1] - sz[1]; z[1] = c[1]
            il = [max(a[k], lo[k]) for k in range(3)]; ih = [min(z[k], hi[k]) for k in range(3)]
            if any(il[k] >= ih[k] - 1e-8 for k in range(3)): result.append(b); continue
            chunks = []
            for k in range(3):
                if a[k] < il[k]:
                    end = z[:]; end[k] = il[k]; chunks.append((a[:], end)); a[k] = il[k]
                if z[k] > ih[k]:
                    start = a[:]; start[k] = ih[k]; chunks.append((start, z[:])); z[k] = ih[k]
            for q, (a, z) in enumerate(chunks):
                if any(z[k] - a[k] < 1e-6 for k in range(3)): continue
                n = dict(b, id=b["id"] + "__cut" + str(q), yaw=0.0)
                n["center"] = [r4((a[k] + z[k]) / 2) for k in range(3)]
                n["size"] = [r4(z[k] - a[k]) for k in range(3)]
                if felt:
                    n["center"][1] = z[1]; n["thickness"] = z[1] - a[1]; n["size"] = [n["size"][0], n["size"][2]]; n["edge_support"] = True
                result.append(n)
        h.d[collection] = result


SCHEMA = {
    "version": "1.1 (Aurora Archipelago: + felt.surface/decel_scale, felt.timed, moving_parts type 'toggle', teleports kind 'lift', vr_comfort)",
    "units": "studs (1 stud = 0.3 m). Speeds studs/s, angles degrees, angular speed deg/s, times seconds.",
    "axes": "Right-handed, +Y up. Each hole has its own local frame: tee at the origin, play generally toward -Z. "
            "Map/top-down view used in all docs and renders: +X to the right (east), -Z up ('north'). "
            "Facing -Z (Roblox LookVector default) the player's right is +X.",
    "world_placement": "world = R_y(world_yaw) * local + world_offset. world_offset [x,y,z] studs, world_yaw degrees. Both are copied from "
                       "world/world.json holes[].placement {origin, yaw_deg} (the source of truth for placement; it supersedes these copies). "
                       "Roblox: holeRoot = CFrame.new(world_offset) * CFrame.Angles(0, math.rad(world_yaw), 0); part.CFrame = holeRoot * localCFrame. "
                       "Check: yaw 90 turns local -Z to world -X.",
    "yaw": "Degrees about +Y, right-handed (Roblox CFrame.Angles(0, math.rad(yaw), 0)). Local->world: "
           "x' = lx*cos(yaw) + lz*sin(yaw); z' = -lx*sin(yaw) + lz*cos(yaw). Positive yaw = counter-clockwise in the map view.",
    "felt": "Playable surface pieces. {id, zone, center:[x,y,z] = TOP-surface centre, size:[sx,sz] footprint in local x/z, yaw, "
            "slope:null|{axis:'x'|'z', rise}}. rise = surface height at the +axis end minus the -axis end (local axes); the "
            "surface is a single plane so heights at the ends are center.y +- rise/2. Collision part = a box whose top face is that "
            "plane (thickness free, suggest 0.4; build sloped pieces as a box rotated by atan(rise/len) about the local axis "
            "perpendicular to `axis`, then shifted so the top-surface centre matches). Optional flags: overlay=true (banked plane laid "
            "on top of base felt; its low edge is flush with the base), kind='bank'|'bridge'|'tunnel'|'plate'|'pier', tunnel=true (felt runs "
            "inside a decorative enclosure; physics unchanged), solid=false + thickness (bridge deck: a ball on a lower level can roll "
            "underneath). kind='plate' (H10 only): a base plate that also runs under the bobsled-run snow walls; only the part "
            "between the rails is reachable or visible. Pieces join when edges meet/overlap at equal height (tolerance 0.05). "
            "AURORA: surface='ice' + decel_scale (H4 glassy ice felt: rolling deceleration = decel_scale * (0.5 + 0.25 v); start 0.35, "
            "CALIBRATE IN STUDIO: set the collider's CustomPhysicalProperties friction so a fixed putt rolls the sim's distance). "
            "AURORA: timed={part, period_s, solid:[t_on, t_off], phase_s} (H17 aurora light span): the piece's collider exists ONLY while "
            "(t + phase_s) mod period_s is in [t_on, t_off); otherwise a ball over it falls (hazard rule). Profile in moving_parts[part].",
    "walls": "Invisible collision blocks. {id, center:[x,y,z] = box centre, size:[sx,sy,sz] local box size, yaw, kind?}. kind='bumper' "
             "(static obstacle blocks: boulders, coral, crystals, hubs) uses bumper restitution 0.65; everything else is a wall (0.63). "
             "Authored rails have local Z along the run and local X = thickness 0.5; height is 1.0 above the highest felt they border "
             "(boxes along ramps are simply taller; visual rails can follow the slope). Rails sit OUTSIDE the felt edge (inner face on "
             "the edge).",
    "hazards": "Out-of-bounds volumes below felt level: {id, type:'water'|'pit', center:[x,y,z] (water/pit surface), size:[sx,sz], yaw, "
               "reset:'previous_position'|'respawn', respawn?:[x,y,z], penalty:1}. A ball that leaves the felt over a hazard gets +1 stroke and "
               "is returned to where its stroke started (reset='previous_position'), or, if reset='respawn', placed at rest on the "
               "`respawn` point (a felt point, e.g. a bridge entry). Any ball leaving all felt elsewhere goes back to its stroke start "
               "(and is flagged as an escape bug). Open-sky gaps (H3, H17): the pit volume reaches down to the cloud deck; in the game the "
               "ball crossing below the felt by 3 studs (or the y 40 respawn plane) triggers the rule.",
    "drops": "Intentional level changes: {id, from, to, edge, height}. The upper piece's edge is open (no rail) and the lower felt "
             "starts directly below/beyond it; the ball falls and keeps ~80% of horizontal speed. Lower felt may extend under the "
             "upper piece (the upper piece then acts as a cliff face for the lower level, unless it is a solid=false deck).",
    "moving_parts": "Separate parts. type 'swing' = pendulum: {id, type:'swing', pivot:[x,y,z] (hinge point above the felt), axis (unit "
                    "vector, horizontal; swing plane is perpendicular to it), amplitude_deg, period_s, phase (deg of the swing cycle at t=0), "
                    "blockers (relative to the pivot with the pendulum hanging straight down)}: angle(t) = amplitude_deg*sin(360*t/period_s + phase), "
                    "right-hand rule about axis; `speed` = peak angular speed at the bottom (info), range = [-amp, amp]. "
                    "Types 'rotate'|'slide': {id, type, pivot:[x,y,z], axis:[ax,ay,az] unit vector, speed (deg/s for rotate, "
                    "studs/s for slide, sign = direction, right-hand rule about axis), range:null (continuous) | [min,max] "
                    "(ping-pong between angles in deg or offsets in studs), phase (angle/offset at t=0), blockers:[{center:[dx,dy,dz] "
                    "relative to pivot at angle/offset 0, size:[sx,sy,sz], yaw, roll?}]} (roll = extra initial rotation in deg about the part axis, "
                    "applied to the blocker's centre and orientation, e.g. vanes at 0/90/180/270). At time t a blocker is "
                    "pivot + Rot(axis, angle(t)) * center (rotate) or pivot + center + axis*offset(t) (slide). "
                    "Slides may pause: dwell:[{at: offset, s: seconds}]. One cycle = range[0] -> range[1] -> range[0] at |speed|; "
                    "a stop at a range end pauses once per visit, an interior stop on both passes; phase = offset at t=0 on the "
                    "forward (min -> max) pass (if a stop sits at that offset, t=0 is the start of its pause). A slide with axis [0,1,0] "
                    "is a vertical piston (H5 geyser column). "
                    "AURORA type 'toggle' (H17 light span): {id, type:'toggle', pivot (info), period_s, phase_s, profile:[{state, s}] "
                    "(fade_in, solid, fade_out, gone), solid_window:[t_on, t_off], felt_ids:[...]}: no blockers; the listed felt pieces "
                    "collide only inside solid_window of each cycle. period_s = full cycle incl. pauses (info for other types). "
                    "The game script must reproduce every profile exactly (tween legs + waits), not a plain sine/ping-pong. All moving colliders: "
                    "CanCollide = true, moved every frame (CFrame per Heartbeat or a constraint), bumper restitution 0.65.",
    "teleports": "{id, entry:{center:[x,y,z], radius, half_size?:[hx,hz]}, exit:{center:[x,y,z], dir:[dx,dz]}, speed_factor, min_speed, max_speed, "
                 "kind?}. A ball whose centre enters the entry radius (or, with half_size, the axis-aligned rectangle centre +- half_size; same "
                 "level, within 0.5) reappears at exit moving along dir with speed = clamp(speed_in*speed_factor, min_speed, max_speed). "
                 "AURORA kind='lift' (H5 geyser): the rectangle is the platform top; lift={cycle_s, board:[t0,t1], release_s, column}: a ball "
                 "whose centre enters the rectangle while the platform is flush (cycle time in board) or from above (dropping in from the "
                 "upper tier; optional lift.drop_half_size [hx, hz] widens the rectangle for these drop-ins only) is HELD on the platform (script: anchor/weld it), carried up with the column, and at cycle time release_s set "
                 "moving along exit.dir from exit.center at clamp(entry speed * speed_factor, min, max). While the column is raised its "
                 "side faces block like a wall.",
    "cup": "{position:[x,y,z] (on felt), radius, flag}. Gameplay cup radius 0.5 stud (real cup 4.25 in = 0.36 stud diameter; enlarged ~2.8x for VR "
           "readability). Ball is holed when its centre is within radius and speed < 5.33 studs/s (1.6 m/s). "
           "flag = {pole_height 7.5 (studs above the cup felt), pole_diameter, banner_size [w,h,t], banner_color, top:[x,y,z] (pole top, "
           "the point the tee line-of-sight check aims at), collision:false}: visual only, the ball passes through it.",
    "ball": "radius 0.08 stud (~real 42.7 mm ball at 0.3 m/stud). Full physics constants in the top-level 'physics' block (= tools/sim.py).",
    "tee": "{position:[x,y,z], aim_hint:[dx,dz]}",
    "ai_waypoints": "{skill|'all': [{id, pos:[x,y,z], from:[zones], carry, power_scale}]} used by the sim golfer: from its current zone it "
                    "aims at the furthest allowed target with line of sight (cup first, then waypoints last->first) and hits for "
                    "distance + carry. cup_from (list of zones or null=all, or {skill: list|null}) limits when it goes straight for the cup. "
                    "A skill-specific list replaces the 'all' list for that skill.",
    "decoration_anchors": "{name, position:[x,y,z] (base centre), notes, landmark?, approx_size?, occluders?, facing?} - visual only, no collision. "
                          "occluders = [{center:[x,y,z] box centre, size:[sx,sy,sz], yaw}]: the solid parts of the prop, used only by the "
                          "tee->flag line-of-sight check (tools/sim.py flag_los).",
    "vr_comfort": "Player-only geometry (never collides with the ball): {player_guards:[box], player_deck:{...}, tier_steps:{...}, note}. "
                  "player_guards use CollisionGroup 'PlayerGuard' (collides with characters only), 4 studs high, along gap rims and both sides "
                  "of rail-less ball bridges; decks/stairs carry 3.5-stud railings with a solid lower board.",
    "line_of_sight": "Checked from the tee eye point (tee + 5.5 studs up) to the flag top against rails/blocks, felt and the ground under "
                     "it, prop occluders, and moving blockers (reported as % of their cycle).",
    "felt_widths": "Lanes 7-8 studs (2.1-2.4 m), greens 12-18 studs (3.6-5.4 m); rails 1 stud high (0.3 m), 0.5 thick (0.15 m).",
}

holes = []


def new_hole(n, hid, name, par, landmark, gimmick):
    w = PLACE[n]
    h = Hole(n, hid, name, par, w["zone"], landmark, gimmick, w["placement"]["origin"], w["placement"]["yaw_deg"])
    h.d["world_placement_source"] = "world/world.json holes[%d].placement" % (n - 1)
    return h


def sign(h, name, pos, text, facing, size=(1.8, 3.2, 0.25)):
    """route sign on a post outside the rails (decoration, occluder = the post)"""
    h.anchor(name, list(pos), text, size=list(size), facing=list(facing),
             occluders=[((pos[0], pos[1] + size[1] / 2, pos[2]), (0.25, size[1], 0.25))])


def felt_arrow(h, name, pos, text, size=(1.4, 0.01, 2.0), facing=None):
    h.anchor(name, list(pos), text, size=list(size), **({"facing": list(facing)} if facing else {}))


def snowpuffs(h, pos, text, size=(2.5, 2.2, 2.0)):
    """snowpuff whimsy figures (ink body, cream belly, orange beak, knitted scarf) watching the hole; always outside the rails"""
    h.anchor("snowpuffs", list(pos), "Snowpuffs (round penguin-puffin figures, ink #222233 body, cream #FFF4E2 belly, orange #FF9A3C beak, "
             "knitted scarves) " + text + "; heads turn to follow the ball (visual only)", size=list(size))


def lantern(h, name, pos, text, post=True):
    """brass lantern on a timber post outside the rails (PointLight #FFB861 r14 b0.8). Lanterns over felt hang >= 8 above it."""
    occ = [((pos[0], pos[1] + 4.0, pos[2]), (0.35, 8.0, 0.35))] if post else None
    h.anchor(name, list(pos), "Brass lantern (" + ("on a 9-stud warm-timber post, " if post else "") + "PointLight #FFB861, range 14, "
             "brightness 0.8) " + text, size=[0.9, 9.0 if post else 1.2, 0.9], occluders=occ)


def dedupe(pts, ys):
    """drop repeated and straight-through vertices from a rail polyline (wall_path needs non-zero segments)"""
    P, Y = [], []
    for p, y in zip(pts, ys):
        if P and abs(P[-1][0] - p[0]) < 1e-9 and abs(P[-1][1] - p[1]) < 1e-9:
            continue
        P.append(p); Y.append(y)
    return P, Y


def plane_h(x, x0, x1, y0, y1):
    """height on a plane that rises linearly from y0 at x0 to y1 at x1"""
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


# ================================================================ H1 Lantern Quay (par 2): bank shot
# A straight quay lane into a snow-capped boulder whose 45-degree face (a bumper block turned 45) banks the ball east onto an offset green.
H1_CUP = K("h1_cup", [6.0, 0.0, -30.5])
H1_B = K("h1_boulder", [-1.3, -35.8, 3.0])     # centre x, z, side of the 45-degree boulder block
h = new_hole(1, "h01", "Lantern Quay", 2, "Brass harbour lantern on a driftwood post at the quay head, the Starfrost Spire dead ahead",
             "Bank shot: a snow-capped boulder's 45-degree face turns the ball east onto an offset green")
h.rect("lane", -3.5, 3.5, 2, -26, 0.0, zone="lane")
h.rect("green", -3.5, 8.5, -26, -38, 0.0, zone="green")
h.wall_path([(-3.5, 2), (-3.5, -38), (8.5, -38), (8.5, -26), (3.5, -26), (3.5, 2)], 0.0, out="L", closed=True)
h.block("boulder", H1_B[0], H1_B[1], H1_B[2], H1_B[2], 0.0, height=2.5, yaw=45.0)
h.tee(0, 0, 0)
h.cup(*H1_CUP, flag_h=7.5)
h.d["cup_from"] = ["green"]
h.wp("all", "boulder_face", [K("h1_wp_x", -0.2), 0.0, -33.0], ["lane"], carry=K("h1_carry", 3.0))
lantern(h, "harbour_lantern", [-6.0, 0, -24.0], "beside the west rail where the lane meets the green: the hole's landmark. A big ship's "
        "lantern (1.2 x 1.6) hangs from a driftwood post with frosted rope; it never overhangs the felt", post=True)
h.d["decoration_anchors"][-1]["landmark"] = True
h.anchor("snow_boulder", [H1_B[0], 0, H1_B[1]], f"Chunky slate-violet boulder with a thick rounded snow cap dressing the {H1_B[2]:g}x{H1_B[2]:g} bumper "
         "turned 45 deg; its flat south-east face is the bank (a faint aurora-mint glow line marks it). Visual may rise to 5 studs but must "
         "cover the collider exactly at felt level", size=[4.4, 5, 4.4], occluders=[((H1_B[0], 2.5, H1_B[1]), (H1_B[2], 5, H1_B[2]), 45.0)])
h.anchor("quay_bollards", [5.5, 0, -12], "Two brass-capped timber mooring bollards with frosted rope coils outside the east rail", size=[1.2, 1.4, 4])
snowpuffs(h, [-6.5, 0, -8], "three of them on a snow drift outside the west rail, the smallest waving a flipper at the tee")
h.anchor("spire_view", [0, 0, -400], "Starfrost Spire straight up the lane (world landmark, tip y 340): the hole is aimed at it", size=[1, 1, 1])
felt_arrow(h, "bank_arrow", [0.0, 0.0, -22.0], "Glowing mint felt arrow decal curving right: 'bank it off the boulder'")
holes.append(h)

# ================================================================ H2 Snowpuff Burrows (par 3): tunnel choice
H2_CUP = K("h2_cup", [-9.75, 0.0, -46.0])
H2_LT = K("h2_left_x", (-11.0, -8.0))       # open-top shortcut burrow, 3-stud clear width
H2_MID_RISE = K("h2_mid_rise", 0.6)
H2_CROSS = K("h2_cross_z", -42.0)
h = new_hole(2, "h02", "Snowpuff Burrows", 3, "Snowpuff rookery: a long snow drift with three burrow mouths and snowpuffs peeking out",
             "Tunnel choice: three snow burrows - short and tight (left), a dead end that rolls the ball back (middle), long and safe (right)")
h.rect("lane", -5, 5, 2, -8, 0.0, zone="lane")
h.rect("plaza", -12, 12, -8, -16, 0.0, zone="plaza")
h.rect("left_burrow", H2_LT[0], H2_LT[1], -16, -34, 0.0, zone="ltun", tunnel=True, kind="tunnel")
h.rect("mid_burrow", -2, 2, -16, -28, zone="mtun", slope=("z", 0.0, H2_MID_RISE), tunnel=True, kind="tunnel")
h.rect("right_burrow", 7, 11, -16, H2_CROSS, 0.0, zone="rtun", tunnel=True, kind="tunnel")
h.rect("crossover", 3, 11, H2_CROSS, -51, 0.0, zone="cross")
h.rect("green", -12, 3, -34, -51, 0.0, zone="green")
h.wall_path([(-5, 2), (-5, -8), (-12, -8), (-12, -16), (H2_LT[0], -16), (H2_LT[0], -34), (-12, -34), (-12, -51), (11, -51), (11, -16),
             (12, -16), (12, -8), (5, -8), (5, 2)], 0.0, out="L", closed=True, top=2.4)
h.wall_path([(H2_LT[1], -16), (-2, -16), (-2, -28), (2, -28), (2, -16), (7, -16), (7, H2_CROSS), (3, H2_CROSS), (3, -34), (H2_LT[1], -34)],
            [0, 0, H2_MID_RISE, H2_MID_RISE, 0, 0, 0, 0, 0, 0], out="L", closed=True, name="drift", top=2.4)
h.tee(0, 0, 0)
h.cup(*H2_CUP, flag_h=7.5)
h.d["cup_from"] = ["green", "ltun", "cross"]
h.wp("good", "left_mouth", [(H2_LT[0] + H2_LT[1]) / 2, 0.0, -17.0], ["lane", "plaza"], carry=K("h2_good_carry", 12.0))
h.wp("good", "left_exit", [(H2_LT[0] + H2_LT[1]) / 2, 0.0, -36.0], ["ltun"], carry=4.0)
h.wp("average", "right_mouth", [9.0, 0.0, -17.0], ["lane", "plaza"], carry=K("h2_avg_carry", 30.0))
h.wp("average", "right_end", [8.5, 0.0, K("h2_avg_end_z", -46.0)], ["rtun"], carry=K("h2_avg_carry2", 1.0))
h.anchor("rookery_drift", [0.0, 0, -22], "The Snowpuff Rookery: a long rounded snow drift (2.4-high colliders are the burrow walls) along z -16..-42 "
         "with three round burrow mouths at z -16 (left 3 wide 'Short & tight', middle 4 wide 'Dead end - it rolls back!', right 4 wide "
         "'Long way round'). The burrows are OPEN-TOPPED snow cuts; only a frosted ice-arch lintel spans each mouth (underside y 8). "
         "Drift dressing stays below y 5 so the flag shows over it", landmark=True, size=[24, 5, 26],
         occluders=[((-5.0, 2.5, -24), (6.0, 5, 16)), ((5.0, 2.5, -22), (4, 5, 12))])
snowpuffs(h, [0.0, 2.4, -20], "peeking out of little side holes along the drift top and sliding down its back on their bellies", size=[14, 2, 6])
for nm, x, txt in (("lintel_left", (H2_LT[0] + H2_LT[1]) / 2, "Short & tight"), ("lintel_mid", 0.0, "Dead end - it rolls back!"),
                   ("lintel_right", 9.0, "Long way round")):
    h.anchor(nm, [x, 8.0, -16.0], f"Frosted ice-arch lintel over the {txt!r} burrow mouth with a painted plank sign; underside exactly y 8 "
             "(VR head clearance). The lintel itself is LEGLESS: each end rests on a basalt rock pillar standing outside the rail / on the drift "
             "wall top, never inside the clear burrow width", size=[5, 1.2, 1.2])
sign(h, "sign_left", (-13.9, 0, -12), "Arrow sign 'Short & tight!' pointing into the LEFT burrow", (0.3, -1.0))
sign(h, "sign_right", (13.9, 0, -12), "Arrow sign 'Long way round - firm putt' pointing into the RIGHT burrow", (-0.3, -1.0))
felt_arrow(h, "felt_arrow_left", [(H2_LT[0] + H2_LT[1]) / 2, 0.0, -14.0], "Glowing mint felt arrow decal (flush) pointing -Z into the left burrow")
felt_arrow(h, "felt_arrow_right", [9.0, 0.0, -14.0], "Glowing mint felt arrow decal (flush) pointing -Z into the right burrow")
felt_arrow(h, "felt_rollback_mid", [0.0, 0.3, -22.0], "Faint felt chevrons in the middle burrow pointing back +Z (its floor rises 0.6: the ball rolls back)")
lantern(h, "lantern_cue", [H2_CUP[0], 9.0, H2_CUP[2]], "hanging 9 studs over the cup (bottom y 9) from the hook of the lantern_crook arm: the "
        "visual cue when the drift hides the flag (no collision, 9 above the felt)", post=False)
# 2026-10-13: the hanging lantern gets a support: a shepherd's-crook post outside the west rail (rail7 outer face x -12.5)
H2_CROOK_X = K("h2_crook_x", -13.6)
h.anchor("lantern_crook", [H2_CROOK_X, 0, H2_CUP[2]], f"Shepherd's-crook lantern post (warm timber + brass, 0.35 thick) standing outside the "
         f"green's west rail at x {H2_CROOK_X:g}; it rises to y 11, then a curved arm reaches east over the rail and the green to x {H2_CUP[0]:g} "
         f"(arm underside y >= 10.4) and a short drop rod holds the lantern at y 9-10.2 over the cup. Nothing below y 10.4 over the felt; "
         f"visual only, no collision", size=[r4(H2_CUP[0] - H2_CROOK_X + 0.5), 11.0, 0.5],
         occluders=[((H2_CROOK_X, 5.5, H2_CUP[2]), (0.35, 11.0, 0.35))])
h.anchor("burrow_lanterns", [9, 8, -32], "Small brass lanterns on ice-arch crossbars every 6 studs over the right burrow; lantern bottom y 8; open top",
         size=[0.6, 0.8, 0.6])
h.d["vr_clearance"] = {"burrows": "open-top snow cuts; only ice-arch lintels at the mouths", "lintel_bottom_y": 8.0, "lantern_bottom_y": 8.0}
holes.append(h)

# ================================================================ H3 Glimmer Crossing (par 3): rail-less plank vs railed ice bridge over open sky
# Span z -24..-50 (world.json): the Glimmer Gap, open sky down to the cloud sea. Straight from the tee: a rail-less glowing ice plank.
# Off to the right (+x): the railed ice bridge, with the railed 4-wide player deck beside it. A ball in the gap respawns at the plank entry.
H3_HALF = K("h3_half", 1.0)          # half-width of the rail-less plank
H3_CUP = K("h3_cup", [-1.0, 0.0, -55.5])
H3_GAP = (-24.0, -50.0)
H3_BR = K("h3_bridge_x", (4.0, 8.0))  # safe ice bridge felt x range
H3_GX = (-8.0, 8.0)                   # shore / green x range
h = new_hole(3, "h03", "Glimmer Crossing", 3, "Glimmer Islet floating off to the east with its crystal cluster and the Glimmer Icefall",
             "Rail-less glowing ice plank straight over the open-sky Glimmer Gap (risky) or the railed ice bridge to the right (safe); "
             "a ball in the gap respawns at the plank entry (+1)")
g0, g1 = H3_GAP
bx0, bx1 = H3_BR
h.rect("shore", H3_GX[0], H3_GX[1], 2, g0, 0.0, zone="shore")
h.rect("plank", -H3_HALF, H3_HALF, g0, g1, 0.0, zone="plank", kind="bridge")
h.rect("ice_bridge", bx0, bx1, g0, g1, 0.0, zone="bridge", kind="bridge")
h.rect("green", H3_GX[0], H3_GX[1], g1, -69.5, 0.0, zone="green")
h.hazard("glimmer_gap", "pit", -13, 13, g0, g1, -30.0, respawn=K("h3_respawn", [0.0, 0.0, g0 + 1.5]))
# shore: west, south, east sides + the north edge outside the two crossings
h.wall_path([(-H3_HALF, g0), (H3_GX[0], g0), (H3_GX[0], 2), (H3_GX[1], 2), (H3_GX[1], g0)], 0.0, out="R", ext=(0.0, 0.0), name="shore_rail")
h.wall_path([(H3_HALF, g0), (bx0, g0)], 0.0, out="L", ext=(0.0, 0.0), name="shore_rail")
h.wall_path([(bx0, g0), (bx0, g1)], 0.0, out="L", ext=(0.0, 0.0), name="bridge_rail")
h.wall_path([(bx1, g1), (bx1, g0)], 0.0, out="L", ext=(0.0, 0.0), name="bridge_rail")
h.wall_path([(H3_GX[1], g1), (H3_GX[1], -69.5), (H3_GX[0], -69.5), (H3_GX[0], g1), (-H3_HALF, g1)], 0.0, out="R", ext=(0.0, 0.0), name="green_rail")
h.wall_path([(bx0, g1), (H3_HALF, g1)], 0.0, out="L", ext=(0.0, 0.0), name="green_rail")
h.tee(0, 0, 0)
h.cup(*H3_CUP, flag_h=7.5)
h.d["cup_from"] = ["green"]
h.wp("good", "plank_far", [0.0, 0.0, g1 - 1.0], ["shore", "plank"], carry=K("h3_good_carry", 4.0))
h.wp("average", "bridge_line", [(bx0 + bx1) / 2, 0.0, g0 + 6.0], ["shore"], carry=0.0)
h.wp("average", "bridge_out", [(bx0 + bx1) / 2, 0.0, g1 - 2.0], ["shore", "bridge"], carry=3.0)
h.anchor("glimmer_islet", [24, -20, -36], "Glimmer Islet: a small floating island 24 studs east of the gap, a glowing ice-crystal cluster on top and "
         "the Glimmer Icefall pouring off it into the clouds (world dressing; see world.json)", landmark=True, size=[20, 30, 20])
h.anchor("ice_plank", [0, 0, (g0 + g1) / 2], f"Rail-less glowing ice plank, felt on top, {2 * H3_HALF:g} wide, 26 long straight over the gap; translucent "
         "glacier-cyan with a crystal-core neon strip down each edge", size=[2 * H3_HALF + 0.4, 0.8, 26])
h.anchor("ice_bridge", [(bx0 + bx1) / 2, 0, (g0 + g1) / 2], "Railed ice bridge: glass deck under the felt, chunky snow-capped timber ball rails", size=[bx1 - bx0 + 1, 2, 26])
h.anchor("plank_respawn_stone", [0, 0, g0 + 1.5], "Glowing aurora-lime marker stone set flush in the felt at the plank entry: where a ball "
         "that falls into the gap reappears", size=[0.8, 0.02, 0.8])
sign(h, "sign_plank", (-2.2, 0, g0 + 2.5), "Sign 'Ice plank - no rails!' with a falling-ball icon beside the plank entry", (0, -1), size=(1.6, 2.6, 0.2))
sign(h, "sign_bridge", (8.6, 0, g0 + 5.0), "Lantern sign 'Ice bridge - the safe way' pointing to the railed bridge", (-0.4, -1))
felt_arrow(h, "route_arrow_plank", [0, 0, g0 + 4.0], "RISKY PLANK: straight north toward the narrow crossing", facing=(0, -1))
felt_arrow(h, "route_arrow_bridge", [(bx0 + bx1) / 2, 0, g0 + 4.0], "SAFE BRIDGE: north along the railed crossing", facing=(0, -1))
snowpuffs(h, [-10.5, 0, -12], "on a snow bank outside the shore's west rail, one with binoculars watching the plank")
H3_DECK = (bx1 + 0.5, min(bx1 + 4.5, 12.5))
h.d["vr_comfort"] = dict(
    player_guards=[dict(id="guard_south_rim", center=[0, 2.0, g0 + 0.25], size=[26, 4, 0.3], yaw=0, note="south gap rim, x -13..13 except where the ball crosses (the guard is PlayerGuard: the ball passes)"),
                   dict(id="guard_north_rim", center=[0, 2.0, g1 - 0.25], size=[26, 4, 0.3], yaw=0, note="north gap rim"),
                   dict(id="guard_plank_w", center=[-H3_HALF - 0.15, 2.0, (g0 + g1) / 2], size=[0.3, 4, 26], yaw=0, note="both sides of the rail-less plank"),
                   dict(id="guard_plank_e", center=[H3_HALF + 0.15, 2.0, (g0 + g1) / 2], size=[0.3, 4, 26], yaw=0, note="")],
    player_deck=dict(id="ice_walk_deck", x=list(H3_DECK), z=[g0, g1], y=0.0, width=round(H3_DECK[1] - H3_DECK[0], 2), rails="both, 3.5 high with solid lower board "
                     "(its inner railing replaces the ball bridge's east rail visually; the 1-high ball rail collider stays)",
                     note="railed walk-on ice deck beside the safe ball bridge so the player can follow the ball"),
    note="The ball sees only the felt, rails and the pit/respawn; every box here is player-only.")
holes.append(h)

# ================================================================ H4 Glissade (par 3): ice felt
# Snow-felt tee lane, then a long glassy ICE strip (rolling deceleration x0.35) into a wide snow-felt green: pace control.
H4_ICE = K("h4_ice_z", (-8.0, -40.0))
H4_ICE_HW = K("h4_ice_hw", 4.0)
H4_GREEN = K("h4_green", (-4.0, 11.5, -57.5))   # x0, x1, back z (dogleg: the green opens east of the ice exit)
H4_CUP = K("h4_cup", [9.0, 0.0, -54.0])
H4_RISE = K("h4_ice_rise", 0.15)   # the ice strip climbs this much toward the green; 2026-10-12 late: 0.6 -> 0.15 (0.6 over 32 = 0.019 > the game's 0.015 rest slope: balls ping-ponged ice <-> tee rail, Studio h4-biased-5 took 18.1 s)
h = new_hole(4, "h04", "Glissade", 3, "Frosted palms leaning over a long glassy ice slide, steam drifting from Steamwhistle Lagoon",
             "Ice felt: a glassy low-friction strip where the ball barely slows; pace control into a snow-felt green")
iz0, iz1 = H4_ICE
gx0, gx1, gz1 = H4_GREEN
yr = H4_RISE
h.rect("lane", -4, 4, 2, iz0, 0.0, zone="lane")
ice = h.rect("ice", -H4_ICE_HW, H4_ICE_HW, iz0, iz1, zone="ice", slope=("z", 0.0, yr) if yr else None, y=0.0,
             surface="ice", decel_scale=K("h4_decel_scale", 0.7))  # 2026-10-12 late: 0.35 -> 0.7 (every sim shot stops in ~12 s or less; still ~1.4x farther than felt)
h.rect("green", gx0, gx1, iz1, gz1, yr, zone="green")
h.wall_path(*dedupe([(-4, 2), (-4, iz0), (-H4_ICE_HW, iz0), (-H4_ICE_HW, iz1), (gx0, iz1), (gx0, gz1), (gx1, gz1), (gx1, iz1), (H4_ICE_HW, iz1),
                     (H4_ICE_HW, iz0), (4, iz0), (4, 2)], [0, 0, 0, yr, yr, yr, yr, yr, yr, 0, 0, 0]), out="L", closed=True)
h.tee(0, 0, 0)
h.cup(H4_CUP[0], yr, H4_CUP[2], flag_h=7.5)
h.d["cup_from"] = None
h.wp("all", "green_in", [0.0, yr, iz1 - 4.0], ["lane", "ice"], carry=K("h4_carry", 2.0))
h.anchor("frosted_palms", [-8.0, 0, -22], "Two frosted palms (teal fronds dusted white) leaning over the ice slide from outside the west rail; "
         "fronds stay >= 8 above the felt", landmark=True, size=[6, 12, 6], occluders=[((-8.0, 4, -22), (0.8, 8, 0.8))])
h.anchor("ice_sheen", [0, 0, (iz0 + iz1) / 2], f"Glassy ice felt #9FE3F2 (Glass look: Transparency 0.15, Reflectance 0.15) over the collider; "
         f"chevron frost lines every 4 studs; the strip is {2 * H4_ICE_HW:g} wide and {iz0 - iz1:g} long", size=[2 * H4_ICE_HW, 0.02, iz0 - iz1])
h.anchor("steam_vents", [9.0, 0, -20], "Little basalt steam vents puffing warm mist outside the east rail (particles only)", size=[2, 1.5, 6])
snowpuffs(h, [-9.0, 0, -44], "on a snow bank by the green, one sliding past on its belly in a bobble hat")
felt_arrow(h, "ice_warning", [0.0, 0.0, iz0 + 1.0], "Felt decal at the ice edge: a snowflake and three chevrons 'ICE - gentle!'", size=(3.0, 0.01, 1.2))
holes.append(h)

# ================================================================ H5 Geyser Hop (par 3): geyser lift (vertical piston with dwell)
# Lower tier (y 0): tee lane and a basin up to the 4-stud basalt cliff at z -28. A 3x3 basalt platform at the cliff foot rides the steam
# column: flush with the basin felt (boarding window), rises 4 to the upper green, pauses, sinks back. A ball that rolls onto it while it
# is flush is held, carried up, and puffed out onto the upper green at clamp(entry speed x factor, min, max).
H5_CUP = K("h5_cup", [-4.0, 4.0, -45.0])
H5_COL = K("h5_column", (0.0, -26.5, 1.5))     # x, z, half side
H5_SPEED = K("h5_speed", 2.0)                   # column rise/sink speed studs/s
H5_DW = K("h5_dwell", (8.0, 1.5))               # pause down (boarding window), pause up (s)
H5_LAUNCH = K("h5_launch", (0.9, 3.5, 12.0))    # speed factor, min, max
H5_EXIT_Z = K("h5_exit_z", -29.6)
H5_RAIL_CLEAR = K("h5_rail_clear", 0.15)        # upper_rail ends stop this far from the column faces (Round 3)
h = new_hole(5, "h05", "Geyser Hop", 3, "Steamwhistle Geyser: a basalt cone beside the green puffing steam to 60 studs and whistling like a kettle",
             "Geyser lift: a basalt platform rides a steam column up 4 studs to the upper green, pauses, and sinks back; roll on while it is down")
cx_, cz_, chs = H5_COL
h.rect("lane", -4, 4, 2, -12, 0.0, zone="lane")
h.rect("basin", -8, 8, -12, -28, 0.0, zone="basin")
h.rect("upper", -12.5, 12.5, -28, -55.5, 4.0, zone="upper")
h.drop("d1", "upper", "basin", f"upper south edge over the geyser shaft x[{cx_ - chs:g},{cx_ + chs:g}] (onto the platform: held, re-launched)", 4.0)
h.wall_path([(8, -28), (8, -12), (4, -12), (4, 2), (-4, 2), (-4, -12), (-8, -12), (-8, -28)], 0.0, out="L", ext=(0.0, 0.0), name="basin_rail")
h.wall_path([(cx_ - chs - H5_RAIL_CLEAR, -28), (-12.5, -28), (-12.5, -55.5), (12.5, -55.5), (12.5, -28), (cx_ + chs + H5_RAIL_CLEAR, -28)], 4.0, out="L", ext=(0.0, 0.0),
            name="upper_rail")
col_m = dict(id="geyser_column", type="slide", pivot=[cx_, 0.0, cz_], axis=[0, 1, 0], speed=H5_SPEED, speed_units="studs/s", range=[0.0, 4.0],
             phase=0.0, blockers=[dict(center=[0, -2.0, 0], size=[2 * chs, 4.0, 2 * chs], yaw=0.0)],
             dwell=[dict(at=0.0, s=float(H5_DW[0])), dict(at=4.0, s=float(H5_DW[1]))],
             visual=f"Basalt platform {2 * chs:g}x{2 * chs:g} on a steam column at the cliff foot. Collider = a {2 * chs:g}x4x{2 * chs:g} box whose top is the "
                    f"platform: offset 0 = top flush with the basin felt (y 0, box y -4..0, sunk in a shaft), offset 4 = top flush with the upper green "
                    f"(y 4). Profile: pause DOWN {H5_DW[0]:g} s (boarding window, steam simmering) -> rise 4 at {H5_SPEED:g} studs/s -> pause UP "
                    f"{H5_DW[1]:g} s (big puff + whistle) -> sink 4 at {H5_SPEED:g} studs/s.")
col_m["period_s"] = r4(S.cycle_period(col_m))
h.d["moving_parts"].append(col_m)
H5_T = S.cycle_period(col_m)
t_top = H5_DW[0] + 4.0 / H5_SPEED
h5_release = round(t_top + 0.1, 3)
gd = (H5_CUP[0] - cx_, H5_CUP[2] - H5_EXIT_Z)
h.teleport("geyser_lift", [cx_, 0.0, cz_], chs, [cx_, 4.0, H5_EXIT_Z], K("h5_exit_dir", gd), speed_factor=H5_LAUNCH[0], min_speed=H5_LAUNCH[1],
           max_speed=H5_LAUNCH[2], half_size=[chs, chs], kind="lift",
           lift=dict(cycle_s=round(H5_T, 4), board=[0.0, float(H5_DW[0])], release_s=h5_release, column="geyser_column", upper_y=4.0,
                     drop_half_size=[r4(chs + H5_RAIL_CLEAR), chs]),
           visual=f"Platform top = the trigger. Boarding: while the platform is flush (cycle t in [0, {H5_DW[0]:g}) s) a ball whose centre rolls onto "
                  f"it is held in its steam-vent dimple (script: anchor it, record its entry speed). It rides up; at t = {h5_release:g} s (0.1 s into "
                  f"the top pause) the geyser puffs it onto the upper green from [{cx_:g}, 4, {H5_EXIT_Z:g}] along exit.dir at clamp(entry speed x "
                  f"{H5_LAUNCH[0]:g}, {H5_LAUNCH[1]:g}, {H5_LAUNCH[2]:g}) studs/s. A ball that drops in from the upper green is held and puffed "
                  "out the same way at the next release. Drop-ins from the upper green use a trigger "
                  f"{H5_RAIL_CLEAR:g} wider each side (lift.drop_half_size, x +-{chs + H5_RAIL_CLEAR:g}) so a ball slipping past the trimmed upper-rail "
                  "ends into the clearance slot beside the column is held too.")
h.tee(0, 0, 0)
h.cup(*H5_CUP, flag_h=7.5)
h.d["cup_from"] = ["upper"]
h.wp("all", "geyser", [cx_, 0.0, cz_], ["lane", "basin"], carry=K("h5_carry", 1.5))
h.anchor("steamwhistle_geyser", [-16.75, 4.0, -36.0], "Steamwhistle Geyser: a 6-wide basalt cone outside the upper green's west rail; its steam column "
         "puffs to 60 studs every 20 s and whistles (visual only). A brass pressure gauge on the platform's side shows the cycle", landmark=True,
         size=[6, 7, 6], occluders=[((-16.75, 7.5, -36.0), (5, 7, 5))])  # 2026-10-13: was [-10.5,4,-33] (on the upper felt); base x -19.75..-13.75, clear of upper_rail9 (outer face x -13)
h.anchor("geyser_platform", [cx_, 0, cz_], f"Moving mesh: hexagonal basalt platform (top {2 * chs:g}x{2 * chs:g}, pivot = platform top centre at offset 0) "
         "riding a translucent steam column; a shallow steam-vent dimple in the top holds the ball. Visual must cover the collider box exactly",
         size=[2 * chs, 4, 2 * chs])
# 2026-10-13: the cliff face is the tier's south face under the upper felt (below the felt slab, y 0..3.5, z -28.05..-28.55), split
# either side of the 3.3-wide geyser shaft (x +-1.65); it was a 16x4x1 box at z -28 that overlapped the basin felt and upper_rail8/12.
for _nm, _x0, _x1 in (("cliff_face_w", -12.5, -1.65), ("cliff_face_e", 1.65, 12.5)):
    # 2026-10-13 02:45: z -28.3 -> -28.4 and top 3.5 -> 3.35 so it clears basin_rail7 / upper_rail8/12 (z face -28.0) and the
    # upper rails' underside (y 3.5) by 0.15
    h.anchor(_nm, [r4((_x0 + _x1) / 2), 0, -28.4], "Basalt cliff face between the tiers (skin on the upper tier's south face, under the felt slab, "
             "z -28.15..-28.65, top y 3.35, 0.15 clear of the rails above and beside it) with frost streaks; the shaft side next to the "
             "platform is lined with brass rivets", size=[r4(_x1 - _x0), 3.35, 0.5])
h.anchor("signal_lamp", [-9.5, 2.0, -27.6], "Green/amber steam lamp on the cliff face just outside the basin's west rail (base y 2, top y 3; off the "
         "felt, clear of basin_rail7 and below upper_rail8): green while the platform is flush (boarding window), amber while it rides; "
         "readable from the tee", size=[0.6, 1.0, 0.4])  # 2026-10-13: was [3,4.5,-28.3], inside the head room and upper_rail12
felt_arrow(h, "geyser_arrow", [0.0, 0.0, -18.0], "Glowing felt arrow decal pointing at the platform, with a little 'wait for the green lamp' icon")
h.anchor("geyser_steps", [15.0, 0, -23.0], "Timber steps for the player beside the cliff, outside the basin's east rail and the upper "
         "green's east rail: x 13.5..16.5, z -17..-29, rise 4 in 5 steps (1.5 tread) to a y-4 landing beside the upper green east of "
         "upper_rail11 (outer face x 13); 3.5-high railing with a solid lower board on the open (west) side. Clear of basin_rail1, "
         "upper_rail11/12 and all felt", size=[3, 4, 12])  # 2026-10-13: had no position; x 9..12 z -16..-28 clipped upper_rail12
h.d["vr_comfort"] = dict(tier_steps=dict(id="geyser_steps", position=[15.0, 0, -23.0], size=[3, 4, 12], where="outside the basin's and upper green's east rails, x 13.5..16.5, z -17..-29", rise=4.0, steps=5,
                                         tread=1.5, railing="3.5-high railing with solid lower board on the open (west) side; parapet along the "
                                         "upper green's south edge east of the shaft; landing at y 4 east of upper_rail11"),
                         note="the player walks up timber steps beside the cliff; the ball rides the geyser")
holes.append(h)

# ================================================================ H6 Palm Lagoon (par 3): side-slope green tilted toward a hot-spring pool
# One big snow-felt plane tilted east (falls 0.42 across 29 studs: the gentlest slope where a ball can still come to rest) runs from the
# tee lane to the back rail. The Kettle hot-spring pool cuts into its low (east) edge: a ball that breaks into it respawns beside it (+1).
H6_RISE = K("h6_rise", 0.42)                 # height drop across x -14.5..14.5 (west high)
H6_POOL = K("h6_pool", (8.5, -24.0, -48.5))  # pool west edge x, z0, z1 (pool runs to x 14.5); 2026-10-12 late: z1 -46 -> -48.5 (escape ended at z -47.47)
H6_CUP = K("h6_cup", [-5.0, -54.0])          # cup x, z (cup y follows the plane); 2026-10-12 late: x 0 -> -5 so the level cup stripe is off the tee line (x 0 stripe: good 1.82 / avg 2.23, 22% aces)
h = new_hole(6, "h06", "Palm Lagoon", 3, "Kettle Lagoon: a steaming turquoise hot spring with frosted palms on a warm basalt shelf",
             "Side-slope green: a snow-felt shelf tilted toward a turquoise hot-spring pool (hazard; misses respawn beside it)")
X0, X1 = -14.5, 14.5
# 2026-10-12 late (Playtest: 0/27 short putts, 0.0087 lip at the old 1.2 cup pad): the cup now sits on a level 3-wide stripe
# (x cup-1.5..cup+1.5) that runs the full shelf length, so there is no pad edge anywhere; the shelf falls east on both sides at
# h6_slope per stud (game stop rule: < 0.015 everywhere), so the old plane is kept outside the stripe.
H6_PAD_HW = K("h6_pad_hw", 1.5)
H6_SLOPE = K("h6_slope", H6_RISE / (X1 - X0))   # fall per stud east (0.42/29 = 0.01448 before)
cxp, czp = H6_CUP
def hp(x):
    """felt height: level stripe at 0 round the cup, falling east at H6_SLOPE on both sides"""
    lo, hi = cxp - H6_PAD_HW, cxp + H6_PAD_HW
    return r4(-H6_SLOPE * (x - min(max(x, lo), hi)))
px, pz0, pz1 = H6_POOL
h.rect("lane", -4, 4, 2, -12, 0.0, zone="lane")
h.rect("shelf", X0, cxp - H6_PAD_HW, -12, -59.5, zone="shelf", slope=("x", hp(X0), hp(cxp - H6_PAD_HW)))
h.rect("cup_pad", cxp - H6_PAD_HW, cxp + H6_PAD_HW, -12, -59.5, hp(cxp), zone="shelf")
h.rect("shelf_e", cxp + H6_PAD_HW, px, -12, -59.5, zone="shelf", slope=("x", hp(cxp + H6_PAD_HW), hp(px)))
h.rect("shelf_se", px, X1, -12, pz0, zone="shelf", slope=("x", hp(px), hp(X1)))
h.rect("shelf_ne", px, X1, pz1, -59.5, zone="shelf", slope=("x", hp(px), hp(X1)))
h.hazard("kettle_pool", "water", px, X1, pz0, pz1, round(hp(X1) - 0.6, 3), respawn=K("h6_respawn", [px - 3.0, hp(px - 3.0), (pz0 + pz1) / 2]))
h.wall_path([(-4, 2), (-4, -12), (X0, -12), (X0, -59.5), (X1, -59.5), (X1, -12), (4, -12), (4, 2)],
            [0, 0, hp(X0), hp(X0), hp(X1), hp(X1), 0, 0], out="L", closed=True)
h.tee(0, 0, 0)
h.cup(cxp, hp(cxp), czp, flag_h=7.5)
h.d["cup_from"] = None
h.anchor("kettle_pool", [(px + X1) / 2, hp(X1) - 0.6, (pz0 + pz1) / 2], f"Turquoise hot-spring pool #2FD6C8 set into the shelf's low east edge "
         f"({X1 - px:g} x {pz0 - pz1:g}), steam curling off it, basalt rim on its far (east) side under the rail; a ball that rolls in "
         "bubbles back up on the respawn stone beside it", landmark=True, size=[X1 - px, 1, pz0 - pz1])
h.anchor("pool_respawn_stone", h.d["hazards"][0]["respawn"], "Warm basalt marker stone flush in the felt beside the pool: where a pooled ball reappears",
         size=[0.8, 0.02, 0.8])
h.anchor("frosted_palms", [16.5, 0, -35], "Three frosted palms leaning over the pool from the east rim (fronds >= 8 above the felt)", size=[6, 12, 8],
         occluders=[((16.5, 4, -35), (0.8, 8, 0.8))])
felt_arrow(h, "slope_ripples", [0.0, 0.0, -36.0], "Faint wind-ripple chevrons printed across the shelf felt pointing east (down the fall line toward the "
           "pool): the reading aid", size=(20, 0.01, 2))
snowpuffs(h, [-16.0, 0.2, -30], "in a little steaming foot-bath outside the west rail, towels on their heads")
holes.append(h)

# ================================================================ H7 Mogul Meadow (par 3): rolling dips
H7_DH = K("h7_hi", 0.6)
H7_DL = K("h7_lo", -0.4)
H7_SEG = K("h7_seg", 3.5)
H7_HUMPS = K("h7_humps", 4)
H7_GW = K("h7_green_hw", 10.0)
H7_CUP = K("h7_cup", [6.0, 0.0, -53.0])
h = new_hole(7, "h07", "Mogul Meadow", 3, "Candy-bright coral-ice fans glowing along a snowy meadow",
             "Rolling dips: four snow moguls built from opposing planar slopes; pace the ball over the humps")
h.rect("lane", -4, 4, 2, -8, 0.0, zone="lane")
prof = [0.0] + [H7_DH, H7_DL] * (H7_HUMPS - 1) + [H7_DH, 0.0]
z = -8.0
for i in range(len(prof) - 1):
    h.rect(f"mogul{i + 1}", -4, 4, z, z - H7_SEG, zone="moguls", slope=("z", prof[i], prof[i + 1]))
    z -= H7_SEG
ZD = z
h.rect("run", -4, 4, ZD, ZD - 4, 0.0, zone="run")
GZ7 = -55.5
h.rect("green", -H7_GW, H7_GW, ZD - 4, GZ7, 0.0, zone="green")
nd = len(prof) - 1
pts = [(-4, 2), (-4, -8)] + [(-4, -8 - H7_SEG * (i + 1)) for i in range(nd)] + \
      [(-4, ZD - 4), (-H7_GW, ZD - 4), (-H7_GW, GZ7), (H7_GW, GZ7), (H7_GW, ZD - 4), (4, ZD - 4)] + \
      [(4, -8 - H7_SEG * (i + 1)) for i in range(nd)][::-1] + [(4, -8), (4, 2)]
yl = [0.0, 0.0] + prof[1:] + [0.0] * 6 + prof[1:][::-1] + [0.0, 0.0]
h.wall_path(*dedupe(pts, yl), out="L", closed=True)
h.tee(0, 0, 0)
h.cup(*H7_CUP, flag_h=7.5)
h.wp("all", "run", [0.0, 0.0, ZD - 2.0], ["lane", "moguls"], carry=K("h7_carry", 4.0))
h.anchor("coral_fans", [-12.0, 0, -24], "Candy coral-ice fans (bubblegum #FF6FB5, tangerine #FFA552, mint #6FFFD2, neon cores) in clumps outside "
         "both rails along the moguls; nothing over the felt. BRANCHING coral: each clump is a short trunk splitting 2-3 times into flattened, "
         "fan-like branches with rounded tips (not sticks or poles); clumps listed in coral_clumps", landmark=True, size=[3, 6, 30],
         occluders=[((-12.0, 3, -24), (2, 6, 20))])
# 2026-10-13: explicit clump positions both sides (east mirrored from the west and varied in z, height and colour); all base x >= 1.0 outside
# the rail outer faces (x +-4.5) and z > -36.5 (green rails start at z -39.5)
CORALS7 = [(-6.5, -11.0, 4.5, "bubblegum"), (-9.0, -18.0, 6.0, "tangerine"), (-6.0, -24.5, 3.5, "mint"), (-10.0, -30.0, 5.5, "bubblegum"),
           (-7.0, -35.0, 4.0, "tangerine"),
           (7.0, -13.5, 4.0, "mint"), (9.5, -20.5, 5.5, "bubblegum"), (6.0, -26.0, 3.0, "tangerine"), (8.5, -31.5, 6.0, "mint"),
           (6.5, -35.5, 4.5, "bubblegum")]
for _i, (_x, _z, _ht, _col) in enumerate(CORALS7, 1):
    h.anchor(f"coral_{'w' if _x < 0 else 'e'}{_i}", [_x, 0, _z], f"Branching coral-ice clump ({_col}), {_ht:g} tall, trunk 0.5 thick splitting "
             f"into 3-5 fan branches; footprint {round(_ht * 0.5, 2):g} wide", size=[round(_ht * 0.5, 2), _ht, round(_ht * 0.4, 2)])
h.anchor("mogul_trim", [0, 0, (ZD - 8) / 2], f"Snow-capped timber rail trim following the {H7_HUMPS} moguls (felt humps rise to +{H7_DH:g} and dip to "
         f"{H7_DL:g}); thick rounded snow on the hump crests", size=[9, 0.4, -8 - ZD])
snowpuffs(h, [11.5, 0, -46], "riding a tiny toboggan over a mogul-shaped drift outside the green's east rail")
holes.append(h)

# ================================================================ H8 Coral Pinball (par 3): static coral bumper field
H8_HW = K("h8_lane_hw", 6.0)
H8_GZ = K("h8_green_z", (-38.0, -53.5))
H8_CUP = K("h8_cup", [-3.5, 0.0, -48.5])
H8_C = K("h8_corals", [  # x, z, sx, sz, yaw
    [-2.0, -10.0, 1.8, 1.8, 45.0],
    [3.0, -15.5, 2.4, 1.0, -35.0],
    [-3.2, -20.5, 2.4, 1.0, 35.0],
    [1.5, -25.0, 1.8, 1.8, 45.0],
    [-1.5, -30.5, 2.2, 1.0, 60.0],
    [3.5, -34.5, 2.0, 1.0, -30.0],
    [2.0, -45.0, 1.6, 1.6, 45.0],
])
h = new_hole(8, "h08", "Coral Pinball", 3, "Giant pink and tangerine coral-ice branches glowing from inside",
             "Bumper field: static flat-faced coral-ice bumpers at set angles bounce the ball down the reef toward the cup")
gz0, gz1 = H8_GZ
h.rect("reef_a", -H8_HW, H8_HW, 2, -20, 0.0, zone="reef_a")
h.rect("reef_b", -H8_HW, H8_HW, -20, gz0, 0.0, zone="reef_b")
h.rect("green", -12.5, 12.5, gz0, gz1, 0.0, zone="green")
h.wall_path([(-H8_HW, 2), (-H8_HW, gz0), (-12.5, gz0), (-12.5, gz1), (12.5, gz1), (12.5, gz0), (H8_HW, gz0), (H8_HW, 2)], 0.0, out="L", closed=True)
for i, (cx, cz, sx, sz, yw) in enumerate(H8_C, 1):
    h.block(f"coral{i}", cx, cz, sx, sz, 0.0, height=1.6, yaw=yw)
h.tee(0, 0, 0)
h.cup(*H8_CUP, flag_h=7.5)
h.d["cup_from"] = ["green", "reef_b"]
h.wp("all", "mid", [K("h8_mid_x", 0.3), 0.0, -21.0], ["reef_a"], carry=K("h8_mid_carry", 4.0))
h.wp("all", "exit_e", [4.2, 0.0, gz0 + 1.0], ["reef_a", "reef_b"], carry=K("h8_exit_carry", 2.0))
h.wp("all", "exit_w", [-4.5, 0.0, gz0 + 1.0], ["reef_a", "reef_b"], carry=K("h8_exit_carry", 2.0))
for i, (cx, cz, sx, sz, yw) in enumerate(H8_C, 1):
    h.anchor(f"coral_{i}", [cx, 0, cz], f"Coral-ice branch cluster (candy colours, neon core) dressing bumper coral{i} ({sx:g}x{sz:g}, yaw {yw:g}); "
             "the collider is its flat-faced base (bumper restitution 0.65), branches rise to ~4 studs and never overhang the felt beyond the base",
             size=[sx + 0.4, 4, sz + 0.4], occluders=[((cx, 2.0, cz), (sx * 0.8, 4, sz * 0.8), yw)])
h.anchor("giant_coral", [-10.5, 0, -18], "Giant coral-ice tree (bubblegum and tangerine, glowing) outside the west rail: the hole's landmark",
         landmark=True, size=[7, 14, 7], occluders=[((-10.5, 7, -18), (4, 14, 4))])
snowpuffs(h, [10.0, 0, -12], "keeping score on a chalk board outside the east rail")
holes.append(h)

# ================================================================ H9 Conch Shortcut (par 4): conch teleport vs the long reef route
H9_CUP = K("h9_cup", [2.0, 0.0, -64.0])
H9_GR = K("h9_conch_r", 0.3)
H9_EXIT = K("h9_exit", [11.0, 0.0, -67.0])
H9_SPIT = K("h9_spit", (-1.5, 1.5, -35.0))
h = new_hole(9, "h09", "Conch Shortcut", 4, "Two giant spiral conch shells of candy coral-ice",
             "Teleport: sink the ball into a giant coral-ice conch at the end of a rail-less reef spit and it shoots out of a second shell "
             "by the green, or play the long reef route round the lagoon")
h.rect("lane", -4, 4, 2, -14, 0.0, zone="lane")
h.rect("junction", -16, 4, -14, -22, 0.0, zone="junction")
h.rect("spit", H9_SPIT[0], H9_SPIT[1], -22, H9_SPIT[2], 0.0, zone="spit", kind="pier")
h.rect("reef_route", -16, -11, -22, -56, 0.0, zone="shore")
h.rect("green", -16, 14, -56, -70, 0.0, zone="green")
h.hazard("reef_lagoon", "water", -11, 14, -22, -56, -1.2)
h.wall_path([(H9_SPIT[1], -22), (4, -22), (4, 2), (-4, 2), (-4, -14), (-16, -14), (-16, -70), (14, -70), (14, -56), (-11, -56), (-11, -22),
             (H9_SPIT[0], -22)], 0.0, out="L", ext=(0.0, 0.0), top=2.4)
h.bank_wall("route_bank", (-11.5, -14.7), (-15.3, -18.5), "L", zone="junction", ext_bank=0.2, ext_back=0.3)
h.bank_wall("green_bank", (-15.3, -65.7), (-11.4, -69.6), "L", zone="green", ext_bank=0.2, ext_back=0.3)
gdir = (H9_CUP[0] - H9_EXIT[0], H9_CUP[2] - H9_EXIT[2])
h.teleport("conch", [0.0, 0.0, H9_SPIT[2] + 2.0], H9_GR, H9_EXIT, K("h9_exit_dir", gdir), speed_factor=K("h9_sf", 0.7),
           min_speed=K("h9_vmin", 3.0), max_speed=K("h9_vmax", 7.0),
           visual="Glowing aurora-lime ring flush in the spit felt 2 studs from its open end, in the mouth of a giant spiral conch -> the twin "
                  "conch on the green's east side blows the ball out, aimed at the cup")
h.tee(0, 0, 0)
h.cup(*H9_CUP, flag_h=7.5)
h.d["cup_from"] = ["green"]
h.wp("good", "conch", [0.0, 0.0, H9_SPIT[2] + 2.0], ["lane", "junction", "spit"], carry=K("h9_conch_carry", 0.6))
h.wp("average", "route_in", [-12.5, 0.0, -18.0], ["lane", "junction"], carry=K("h9_avg_c1", 2.0))
h.wp("average", "route_top", [-13.5, 0.0, -54.0], ["junction"], carry=K("h9_avg_c2", 6.0))
h.wp("average", "green_w", [-13.5, 0.0, -63.0], ["shore"], carry=K("h9_avg_c3", 3.0))
h.anchor("conch_entry", [0.0, 0.0, H9_SPIT[2] + 1.0], "Giant spiral conch of candy coral-ice (pink/cream, glowing lip) lying at the end of the spit "
         "with its mouth over the ring: the ball rolls in. Shell body stays behind the ring and below 5 studs over the spit end", landmark=True,
         size=[5, 4.5, 5], occluders=[((0.0, 2.6, H9_SPIT[2] - 1.5), (4, 4, 3))])
# 2026-10-13 02:45: the shell mesh moved off the green (was [11,0,-67] 4x4x4 on the felt) to just outside the east rail (rail8 outer face
# x 14.5; shell x 14.65..18.65). The teleport exit point H9_EXIT is unchanged: a sparkle-puff ring flush in the felt marks it.
h.anchor("conch_exit", [16.65, 0.0, H9_EXIT[2]], "Twin conch outside the green's east rail, mouth turned over the rail toward the cup; the ball "
         f"pops out at the teleport exit [{H9_EXIT[0]:g}, {H9_EXIT[2]:g}] on the felt (flush sparkle ring decal there, a puff of sparkle "
         "from the conch mouth). Whole shell stays outside the rail, off the felt", size=[4, 4, 4],
         occluders=[((16.65, 2.0, H9_EXIT[2]), (3, 4, 3))])
felt_arrow(h, "conch_exit_ring", [H9_EXIT[0], 0.0, H9_EXIT[2]], "Flush aurora-lime sparkle ring decal where the ball pops out", size=(1.4, 0.01, 1.4))
h.anchor("coral_spit", [0.0, -1.2, (-22.8 + H9_SPIT[2]) / 2], "Coral-ice skirt under the rail-less spit's edges, from the felt underside "
         "down into the lagoon; starts at z -22.8, 0.3 clear of rail1 (face z -22.5), and stays inside the spit's x -1.5..1.5 footprint",
         size=[H9_SPIT[1] - H9_SPIT[0], 1.2, round(-22.8 - H9_SPIT[2], 3)])
h.anchor("reef_lagoon", [1.5, -1.2, -39], "Shallow turquoise reef lagoon with glowing coral-ice heads under the water (hazard: +1, back to the "
         "stroke start)", size=[25, 1, 34])
sign(h, "sign_spit", (2.2, 0, -20), "Sign 'Conch express - shoot the shell!' at the spit root", (0, -1), size=(1.6, 2.6, 0.2))
sign(h, "sign_route", (-16.6, 0, -24), "Sign 'Reef Walk - the long way' pointing north along the reef route", (0.3, -1))
felt_arrow(h, "felt_arrow_spit", [0.0, 0.0, -20.0], "Glowing felt arrow decal pointing -Z onto the spit")
felt_arrow(h, "felt_arrow_route", [-13.5, 0.0, -24.0], "Glowing felt arrow decal pointing -Z up the reef route")
snowpuffs(h, [-18.5, 0, -40], "snorkelling at the lagoon edge outside the reef route's west rail")
holes.append(h)

# ================================================================ H10 Bobsled Bend (par 3): half-pipe S-bend
H10_C = K("h10_center", [[0, 2], [0, -10], [6, -16], [6, -26], [-1, -33], [-1, -38]])
H10_HW = K("h10_hw", 3.5)        # channel half-width (rail inner face to centreline)
H10_BW = K("h10_bank_w", 1.5)    # bank width each side
H10_BR = K("h10_bank_rise", 0.3)  # bank rise
H10_CUP = K("h10_cup", [-0.5, 0.0, -42.0])
h = new_hole(10, "h10", "Bobsled Bend", 3, "Striped bobsled start hut with brass bells",
             "Half-pipe: an S-bend bobsled channel with banked felt walls; ride high to carry the bend")
xs = [p[0] for p in H10_C]
PX0, PX1 = min(xs) - H10_HW - 0.5, max(xs) + H10_HW + 0.5
H10_ZS = K("h10_zone_z", (-10.0, -26.0))
for zi, (za, zb) in enumerate([(2, H10_ZS[0]), (H10_ZS[0], H10_ZS[1]), (H10_ZS[1], H10_C[-1][1])]):
    h.rect(f"plate{zi + 1}", PX0, PX1, za, zb, 0.0, zone=f"s{zi + 1}", kind="plate")
GZ = H10_C[-1][1]
h.rect("green", -7, 6, GZ, GZ - 12, 0.0, zone="green")
h.wall_path([(PX0, 2), (PX0, GZ), (-7, GZ), (-7, GZ - 12), (6, GZ - 12), (6, GZ), (PX1, GZ), (PX1, 2)], 0.0, out="L", closed=True, name="snowwall",
            top=H10_BR + 1.0)
L = offset_polyline(H10_C, -H10_HW)
R = offset_polyline(H10_C, H10_HW)
h.d["plate_visible"] = [[(r4(x), r4(z)) for x, z in L + list(reversed(R))]]
h.wall_path(L, 0.0, out="L", ext=(0.0, 0.0), top=H10_BR + 1.0, name="run_rail")
h.wall_path(list(reversed(R)), 0.0, out="L", ext=(0.0, 0.0), top=H10_BR + 1.0, name="run_rail")
h.wall_free((R[-1][0], GZ + 0.25), (6.0, GZ + 0.25), 0.0, name="green_s_rail_e")
h.wall_free((-7.0, GZ + 0.25), (L[-1][0], GZ + 0.25), 0.0, name="green_s_rail_w")
nseg = len(H10_C) - 1


def h10_turn_side(j):
    ax_, az_ = H10_C[j][0] - H10_C[j - 1][0], H10_C[j][1] - H10_C[j - 1][1]
    bx_, bz_ = H10_C[j + 1][0] - H10_C[j][0], H10_C[j + 1][1] - H10_C[j][1]
    return "R" if (bx_ * (-az_) + bz_ * ax_) > 0 else "L"


for i in range(nseg):
    a, b = H10_C[i], H10_C[i + 1]
    dx, dz = b[0] - a[0], b[1] - a[1]
    Ls = math.hypot(dx, dz)
    ux, uz = dx / Ls, dz / Ls
    for side, out in (("L", "L"), ("R", "R")):
        ee = []
        for j in (i, i + 1):
            if j == 0 or j == nseg:
                ee.append(0.0)
                continue
            t = math.tan(math.radians(turn_deg(H10_C, j) / 2))
            ee.append(-(H10_HW - H10_BW) * t if h10_turn_side(j) == side else H10_HW * t)
        e0, e1 = ee
        nx, nz = (-uz, ux) if side == "R" else (uz, -ux)
        off = H10_HW - H10_BW
        A = (a[0] + nx * off - ux * e0, a[1] + nz * off - uz * e0)
        B = (b[0] + nx * off + ux * e1, b[1] + nz * off + uz * e1)
        h.bank(f"bank_{side}{i + 1}", A, B, H10_BW, H10_BR, out, zone=["s1", "s2", "s2", "s3", "s3"][min(i, 4)], ext=0.0)
h.tee(0, 0, 0)
h.cup(*H10_CUP, flag_h=7.5)
h.d["cup_from"] = ["green", "s3"]
h.wp("all", "bend1", [K("h10_wp1", [2.0, -13.0])[0], 0.0, K("h10_wp1", [2.0, -13.0])[1]], ["s1"], carry=K("h10_carry1", 16.0))
h.wp("all", "bend2", [K("h10_wp2", [3.5, -29.0])[0], 0.0, K("h10_wp2", [3.5, -29.0])[1]], ["s2"], carry=K("h10_carry2", 8.0))
h.wp("all", "mouth", [H10_C[-1][0], 0.0, GZ + 1.5], ["s3"], carry=3.0)
# 2026-10-13 12:30: RobloxDevBot's Studio checker (real mesh bounds) measured 0.125 to snowwall1; base moved to 0.30 clear in the box audit
h.anchor("bobsled_hut", [-7.8, 0, -6], "Striped red-and-cream bobsled start hut with brass bells and a parked toy bobsled, outside the run's west wall: "
         "the landmark", landmark=True, size=[5, 7, 5], occluders=[((-7.8, 3.5, -6), (4, 7, 4))])
# 2026-10-13 02:45: was one 16x4x46 box at [3,0,-22] over the whole run; split into two banks outside the outer snow walls, 0.15 clear
h.anchor("snow_walls_w", [-6.4, 0, -23.0], "Rounded packed-snow bobsled bank outside the west snow wall (x -7.15..-5.65, z -8.65..-37.35, up to 4 "
         "tall, ice-blue glaze); 0.15 clear of snowwall1/2 and the start hut; kept low so the flag stays visible", size=[1.5, 4, 28.7])
h.anchor("snow_walls_e", [11.4, 0, -16.175], "Rounded packed-snow bobsled bank outside the east snow wall (x 10.65..12.15, z 2.5..-34.85, up to 4 "
         "tall, ice-blue glaze); 0.15 clear of snowwall7 and the snowpuffs", size=[1.5, 4, 37.35])
h.anchor("run_lip", [3, H10_BR, -22], f"Rounded ice lip on top of both run rails following the S (felt banks {H10_BW:g} wide rise {H10_BR:g})",
         size=[1, 0.4, 46])
snowpuffs(h, [10.0, 0, -36], "in a row of bobsleds outside the east wall, cheering with tiny flags")
holes.append(h)

# ================================================================ H11 Floe Drift (par 3): drifting ice floe (slide with dwell, pointed ends)
H11_CUP = K("h11_cup", [-4.0, 0.0, -45.0])
H11_FLOE_LEN = K("h11_floe_len", 7.0)
H11_SPEED = K("h11_speed", 3.0)
H11_DW = K("h11_dwell", (1.2, 2.0))     # pause (s) blocking (offset 0, across the neck) / parked (offset -7, in the west pocket)
H11_TRAVEL = K("h11_travel", 7.0)
h = new_hole(11, "h11", "Floe Drift", 3, "Frozen Floe Pond with toy floes and a snowpuff ice-fishing hut",
             "Drifting ice floe: a flat floe slides across the neck, pauses, and drifts back (slide with dwell; pointed 45-degree ends); "
             "the side channel is the safe way round")
h.rect("lane", -4, 4, 2, -18, 0.0, zone="lane")
h.rect("pond", -11, 11, -18, -26, 0.0, zone="pond")
h.rect("neck", -3, 3, -26, -30, 0.0, zone="neck")
h.rect("spill", -3, 3, -30, -34, 0.0, zone="neck")
h.rect("side_channel", 8, 11, -26, -47, 0.0, zone="channel")
h.rect("crossover", 6, 11, -47, -50, 0.0, zone="channel")
h.rect("green", -11, 6, -34, -50, 0.0, zone="green")
h.wall_path([(-4, 2), (-4, -18), (-11, -18), (-11, -26), (-3, -26), (-3, -34), (-11, -34), (-11, -50), (11, -50), (11, -18), (4, -18), (4, 2)],
            0.0, out="L", closed=True, top=2.4)
h.wall_path([(3, -26), (8, -26), (8, -47), (6, -47), (6, -34), (3, -34)], 0.0, out="L", closed=True, name="berg", top=2.4)
cs = 0.6 / math.sqrt(2)
floe_bl = [dict(center=[0, 0.5, 0], size=[H11_FLOE_LEN - 0.6, 1.0, 0.636], yaw=0.0)] + \
          [dict(center=[sx * (H11_FLOE_LEN / 2 - 0.3), 0.5, 0], size=[r4(cs), 1.0, r4(cs)], yaw=45.0) for sx in (-1, 1)]
h.slider("ice_floe", [0, 0.0, -28.0], [1, 0, 0], H11_SPEED, [-H11_TRAVEL, 0.0], floe_bl, phase=0.0,
         dwell=[(0.0, H11_DW[0]), (-H11_TRAVEL, H11_DW[1])],
         visual=f"Ice floe slab {H11_FLOE_LEN:g} long, 0.6 thick, 1.0 tall with pointed 45-degree ends, gliding on a hidden track across the neck; "
                f"blocking = centred on the neck (offset 0), parked = drifted {H11_TRAVEL:g} west into a pocket in the snowbank")
H11_LINTEL = K("h11_lintel", 1.27)   # slot lintel underside (Round 4: 1.17 -> 1.27 = floe mesh top 1.12 + 0.15)
collision_cut(h, ["rail5", "berg18"], [-10.68, -0.15, -28.47], [3.68, H11_LINTEL, -27.53], "ice_floe")
h.rect("floe_pocket_floor", -10.68, 3.68, -27.53, -28.47, -.15, zone="neck", edge_support=True)
h.wall_path([(-3, -27.53), (-10.68, -27.53), (-10.68, -28.47), (-3, -28.47)], -.15, out="L", top=2.55, name="pocket_w")
h.wall_path([(3, -28.47), (3.68, -28.47), (3.68, -27.53), (3, -27.53)], -.15, out="L", top=2.55, name="pocket_e")
h.tee(0, 0, 0)
h.cup(*H11_CUP, flag_h=7.5)
h.d["cup_from"] = ["green", "neck", "channel"]
h.wp("all", "neck", [0.0, 0.0, -31.0], ["lane", "pond"], carry=K("h11_neck_carry", 6.0))
h.wp("average", "neck", [0.0, 0.0, -31.0], ["lane"], carry=K("h11_neck_carry", 6.0))
h.wp("average", "channel_in", [9.5, 0.0, -24.0], ["pond"], carry=0.0)
h.wp("average", "channel_far", [9.5, 0.0, -40.0], ["pond"], carry=K("h11_ch_carry", 6.0))
h.wp("average", "channel_top", [9.0, 0.0, -48.6], ["channel"], carry=K("h11_ch_carry2", 1.0))
h.anchor("ice_floe", [0, 0, -28], "Moving mesh: a chunky ice floe (glacier cyan, snow on top, a little snowpuff riding it) with pointed ends, pivot = "
         "floe centre at offset 0; must cover the collider exactly", size=[H11_FLOE_LEN, 1.2, 0.6])
# 2026-10-13 12:30: base moved to 0.30 clear of pocket_w20/21 (Studio mesh check flagged it at the settled 0.168)
h.anchor("fishing_hut", [-9.184, 0, -30.777], "Snowpuff ice-fishing hut (striped canvas, stove-pipe chimney puffing) on the berg between pond and green: "
         "the landmark", landmark=True, size=[3, 6, 3], occluders=[((-9.184, 3, -30.777), (3, 6, 3))])
# 2026-10-13 02:45: was one 24.6x3x1 box at [0,0,-28] (posts at x -12 and 4; the east post overlapped pocket_e23 and the floe's path).
# Split into one anchor per post; east post moved to x 4.65 (x 4.35..4.95, 0.17 clear of pocket_e23's face x 4.18, floe east tip <= 3.5)
# 2026-10-13 12:30: east post 4.65 -> 4.8 (0.32 clear of pocket_e22..24; Studio mesh check flagged 0.17)
for _nm, _x in (("floe_frame_w", -12.0), ("floe_frame_e", 4.8)):
    h.anchor(_nm, [_x, 0, -28], "Frosted timber marker post where the floe track meets the snowbank (no crossbeam), off the felt and clear of "
             "the pocket walls", size=[0.6, 3, 0.6], occluders=[((_x, 1.5, -28), (0.6, 3, 0.6))])
sign(h, "sign_channel", (11.6, 0, -21), "Painted arrow 'Side channel - the long way round' pointing into the channel", (-0.3, -1))
felt_arrow(h, "felt_arrow_channel", [9.5, 0.0, -23.5], "Glowing felt arrow decal pointing -Z into the side channel")
h.anchor("floe_pond", [0, -0.2, -22], "Floe Pond ice (terrain Ice at y 145.6) round the hole with toy floes frozen in", size=[30, 0.2, 20])
holes.append(h)

# ================================================================ H12 Icebreaker Wheel (par 3): vertical rotor (paddle wheel on a horizontal axle)
H12_CUP = K("h12_cup", [-1.5, 0.0, -42.0])
H12_VANES = K("h12_vanes", 4)
H12_SPEED = K("h12_speed", 30.0)
H12_VW = K("h12_vane_w", 2.4)
H12_R = (0.6, 4.1)
H12_LOW = K("h12_low", 0.06)   # lowest paddle edge over the felt (Round 3: 0.02 -> 0.06; ball is 0.16 tall)
H12_PY = round(H12_LOW + H12_R[1], 3)
h = new_hole(12, "h12", "Icebreaker Wheel", 3, "Beached toy icebreaker with a red funnel and a paddle wheel",
             "Vertical rotor: the icebreaker's paddle wheel turns across the channel on a horizontal axle; the signed bypass is the safe way")
h.rect("lane", -4, 4, 2, -10, 0.0, zone="lane")
h.rect("approach", -4, 11, -10, -18, 0.0, zone="approach")
h.rect("wheel_channel", -1.2, 1.2, -18, -24, 0.0, zone="tunnel", tunnel=True, kind="tunnel")
h.rect("spill", -2.5, 2.5, -24, -34, 0.0, zone="spill")
h.rect("bypass", 8, 11, -18, -34, 0.0, zone="bypass")
h.rect("green", -9, 11, -34, -48, 0.0, zone="green")
H12_MOUTH = K("h12_mouth_z", -18.01)   # wall line at the wheel (Round 4: -18 -> -18.01, paddle face z -17.95 -> 0.06 to rail2/3, hull13/18)
h.wall_path([(-4, 2), (-4, H12_MOUTH), (-1.2, H12_MOUTH), (-1.2, -24), (-2.5, -24), (-2.5, -34), (-9, -34), (-9, -48), (11, -48), (11, -10), (4, -10), (4, 2)],
            0.0, out="L", closed=True)
h.wall_path([(1.2, H12_MOUTH), (8, H12_MOUTH), (8, -34), (2.5, -34), (2.5, -24), (1.2, -24)], 0.0, out="L", closed=True, name="hull")
strips = K("h12_tip_strips", 6)
vanes = []
for k in range(H12_VANES):
    for j in range(strips):
        x0 = -H12_VW / 2 + j * H12_VW / strips
        x1 = x0 + H12_VW / strips
        rout = math.sqrt(H12_R[1] ** 2 - max(abs(x0), abs(x1)) ** 2)
        vanes.append(dict(center=[(x0 + x1) / 2, -(H12_R[0] + rout) / 2, 0], size=[H12_VW / strips, rout - H12_R[0], K("h12_depth", 0.4)],
                          yaw=0.0, roll=360 * k / H12_VANES))
h.rotor("paddle_wheel", [0, H12_PY, -17.75], [0, 0, 1], H12_SPEED, vanes,
        visual=f"{H12_VANES} broad timber paddles (width {H12_VW}, radius 0.6..4.1, tips clipped to a circle, built from {strips} strips each); "
               f"axle y={H12_PY}; lowest paddle edge {H12_LOW:g} over the felt")
h.tee(0, 0, 0)
h.cup(*H12_CUP, flag_h=7.5)
h.d["cup_from"] = ["green", "spill"]
h.wp("all", "wheel_far", [0.0, 0.0, -25.0], ["lane", "approach"], carry=K("h12_tun_carry", 5.0))
h.wp("average", "bypass_in", [9.5, 0.0, -16.0], ["lane"], carry=0.0)
h.wp("average", "bypass_top", [9.5, 0.0, -35.5], ["approach", "bypass"], carry=K("h12_bp_carry", 4.0))
h.anchor("icebreaker", [-3, 0, -21], "Beached toy icebreaker (red hull, cream deckhouse, red funnel puffing steam) straddling the channel; the "
         "'hull' block x 1.2..8 plus a matching west half; the paddle wheel turns in a 2.4-wide slot through its stern", landmark=True,
         size=[16, 8, 6], occluders=[((-3.925, 3, -21.005), (4.15, 6, 4.69)), ((4.6, 3, -21.005), (5.5, 6, 4.69))])
# 2026-10-13 02:45 hull_face_skins: hull blocks shrunk to sit 0.15 inside the rails (were x -6..-1.2 / 1.2..8, z -18..-24, on rail1-4 and
# hull13/14/17/18): west x -6..-1.85, east x 1.85..7.35, both z -18.66..-23.35. The rails' own faces stay bare timber/ice
h.anchor("paddle_wheel", [0, H12_PY, -17.75], f"Moving mesh: red-and-cream paddle wheel (pivot = hub, axis +Z), {H12_VANES} broad timber paddles "
         f"radius {H12_R[1]:g}", size=[2 * H12_R[1], 2 * H12_R[1], 0.4])
sign(h, "sign_bypass", (11.6, 0, -13), "Arrow sign 'Round the stern - no paddles' pointing into the bypass", (-0.3, -1))
felt_arrow(h, "felt_arrow_bypass", [9.5, 0.0, -20.0], "Glowing felt arrow decal pointing -Z into the bypass")
snowpuffs(h, [-7.5, 0, -40], "in sailor hats on a stack of crates beside the green")
holes.append(h)

# ================================================================ H13 Snowpuff Carousel (par 3): horizontal sweeper (4 arms round a solid hub)
H13_C = (0.0, -36.0)
H13_AP = 13.0
H13_ARMS = K("h13_arms", 4)
H13_SPEED = K("h13_speed", 15.0)
H13_ARM = K("h13_arm", (8.2, 11.5, 3.6))    # r_in, r_out, thickness
H13_CUP = K("h13_cup", [10.1, 0.0, -46.0])
h = new_hole(13, "h13", "Snowpuff Carousel", 3, "Brass-and-ice carousel canopy topped with a snowpuff weathervane",
             "Horizontal sweeper: a carousel of snowpuff sleds sweeps four arms round a solid central hub on a square green")
h.rect("lane", -7.5, 7.5, 2, H13_C[1] + H13_AP, 0.0, zone="lane")
h.rect("ring", H13_C[0] - H13_AP, H13_C[0] + H13_AP, H13_C[1] + H13_AP, H13_C[1] - H13_AP, 0.0, zone="dial")
zs = H13_C[1] + H13_AP
h.wall_path([(-7.5, 2), (-7.5, zs), (-H13_AP, zs), (-H13_AP, H13_C[1] - H13_AP), (H13_AP, H13_C[1] - H13_AP), (H13_AP, zs), (7.5, zs), (7.5, 2)],
            0.0, out="L", closed=True)
# A solid, stepped circular hub excludes every ball rest within seven studs: 48 strips enclose the circle of radius 7.5; their outside
# corners stay < 8.0, leaving > 0.15 clearance to the arms' 8.2 inner radius.
for j in range(48):
    z0 = -7.5 + j * 15 / 48
    z1 = z0 + 15 / 48
    zn = min(abs(z0), abs(z1)) if z0 * z1 > 0 else 0
    half = math.sqrt(7.5 ** 2 - zn ** 2)
    h.block(f"hub_plinth_{j:02d}", 0, H13_C[1] + (z0 + z1) / 2, 2 * half, z1 - z0, 0, height=1.2)
h.d["rest_exclusion"] = dict(center=[0, 0, H13_C[1]], radius=7.0, physical_plinth_radius=7.5,
                             method="48 solid circumscribed box strips (the carousel's round base); balls cannot occupy the central disk")
h.rotor("carousel_arms", [H13_C[0], 0.0, H13_C[1]], [0, 1, 0], H13_SPEED, arm_blockers(H13_ARMS, H13_ARM[0], H13_ARM[1], H13_ARM[2], 0.9),
        visual=f"Carousel sweep: {H13_ARMS} low sled-runner arms (r {H13_ARM[0]:g}..{H13_ARM[1]:g}, {H13_ARM[2]:g} wide, 0.9 tall), each carrying a "
               f"snowpuff on a little sled above the collider, sweeping round the hub at {abs(H13_SPEED):g} deg/s")
h.tee(0, 0, 0)
h.cup(*H13_CUP, flag_h=7.5)
h.d["cup_from"] = {"good": ["lane", "dial"], "average": ["dial"]}
h.wp("all", "ring_side", [K("h13_side", [9.5, -36.0])[0], 0.0, K("h13_side", [9.5, -36.0])[1]], ["lane"], carry=K("h13_carry", 2.0))
h.wp("all", "south_w", [-10.5, 0, -27.5], ["dial"], carry=0.0)
h.wp("all", "south_e", [10.5, 0, -27.5], ["dial"], carry=0.0)
h.wp("all", "ring_w", [-8.5, 0.0, -45.0], ["dial"], carry=0.5)
h.wp("all", "ring_e", [8.5, 0.0, -45.0], ["dial"], carry=0.5)
h.wp("average", "safe_east_approach", [8.0, 0, -27.0], ["lane"], carry=0.0)
for point in [p for p in h.d["ai_waypoints"]["all"] if "dial" in p["from"]]:
    h.d["ai_waypoints"]["average"].append(dict(point))
felt_arrow(h, "safe_east_wait", [8.0, 0, -27.0], "Safe-route waiting marker outside the arm sweep: play here first, then time the short east-side putt")
h.anchor("carousel_canopy", [H13_C[0], 0, H13_C[1]], "Brass-and-ice carousel: a striped canopy on a central brass pole, topped by a snowpuff "
         "weathervane. Canopy underside y 9 (>= 8 over the felt), pole inside the hub; the solid r 7.5 round base (collider 1.2 high) is "
         "the hub", landmark=True, size=[16, 12, 16], occluders=[((H13_C[0], 3.5, H13_C[1]), (1.2, 7, 1.2))])
h.anchor("hub_base", [0, 0, H13_C[1]], "Solid round carousel base: 48 circumscribed box strips enclose r 7.5; top y 1.2; not a playing surface",
         size=[15.0, 1.2, 15.0])
h.anchor("carousel_arms", [H13_C[0], 0, H13_C[1]], "Moving mesh (pivot = hub centre, axis +Y): four sled-runner arms with snowpuffs riding little "
         "sleds; mesh covers the collider boxes exactly", size=[2 * H13_ARM[1], 0.9, H13_ARM[2]])
h.anchor("music_lanterns", [-14.5, 0, -24], "Brass music-box lanterns on posts at the green's corners (outside the rails)", size=[1, 9, 1])
holes.append(h)

# ================================================================ H14 Bell Buoy (par 3): pendulum
H14_CUP = K("h14_cup", [1.0, 0.8, -44.0])
H14_LW = K("h14_lane_hw", 4.0)
H14_RISE = K("h14_rise", 0.8)
H14_L = K("h14_len", 9.0)
BELL = K("h14_bell", [2.0, 2.0, 2.0])
H14_AMP = K("h14_amp", 9.0)
H14_PER = K("h14_period", 4.0)
H14_FOOT = K("h14_foot", [2.1, 0.4, 0.15])
H14_Z = K("h14_z", -24.0)
H14_BELL_YAW = K("h14_bell_yaw", 30.0)
h = new_hole(14, "h14", "Bell Buoy", 3, "Timber bell gantry hung with icicles and a brass bell",
             "Pendulum: a brass icicle bell swings across the lane from a timber gantry, before a ramp up to a raised green")
_bhx = BELL[0] / 2
H14_GAP = round(max(K("h14_gap", 0.35), 0.02 + _bhx ** 2 / (2 * (H14_L + BELL[1] / 2))), 3)
H14_PIV = [K("h14_piv_x", 0.0), round(H14_GAP + BELL[1] / 2 + H14_L, 3), H14_Z]
_fhx = H14_FOOT[0] / 2
_fr = H14_L + BELL[1] / 2 + H14_GAP
H14_FOOT_MIN = K("h14_foot_min", 0.06)   # lowest foot corner over the felt at any swing angle (Round 3: 0.021 -> 0.06)
H14_FOOT_GAP = math.ceil(1000 * max(H14_FOOT_MIN, H14_FOOT_MIN + 0.001 + _fhx ** 2 / (2 * _fr))) / 1000
foot = dict(center=[0, round(-_fr + H14_FOOT_GAP + H14_FOOT[1] / 2, 3), 0], size=H14_FOOT, yaw=0.0)
H14_FOOT_STRIPS = K("h14_foot_strips", 9)   # >0: foot built from strips whose bottom corners sit on an arc H14_FOOT_MIN above the felt (like H12)
if H14_FOOT_STRIPS:
    H14_FOOT_GAP = round(H14_FOOT_MIN + 0.001, 3)   # +0.001 margin over the 4-dp rounding of the strip boxes
    _r0 = _fr - H14_FOOT_GAP; _top = -_r0 + H14_FOOT[1]
    foot = []
    for j in range(H14_FOOT_STRIPS):
        x0 = -_fhx + j * H14_FOOT[0] / H14_FOOT_STRIPS; x1 = x0 + H14_FOOT[0] / H14_FOOT_STRIPS
        bot = -math.sqrt(_r0 ** 2 - max(abs(x0), abs(x1)) ** 2)
        foot.append(dict(center=[r4((x0 + x1) / 2) + 0.0, r4((bot + _top) / 2), 0], size=[r4(x1 - x0), r4(_top - bot), H14_FOOT[2]], yaw=0.0))
else:
    foot = [foot]
h.rect("lane", -H14_LW, H14_LW, 2, H14_Z - 1.0, 0.0, zone="lane")
h.rect("lane2", -H14_LW, H14_LW, H14_Z - 1.0, -30, 0.0, zone="lane2")
h.rect("ramp", -H14_LW, H14_LW, -30, -36, zone="ramp", slope=("z", 0.0, H14_RISE))
h.rect("green", -8, 8, -36, -48, H14_RISE, zone="green")
h.wall_path([(-H14_LW, 2), (-H14_LW, -30), (-H14_LW, -36), (-8, -36), (-8, -48), (8, -48), (8, -36), (H14_LW, -36), (H14_LW, -30), (H14_LW, 2)],
            [0, 0, H14_RISE, H14_RISE, H14_RISE, H14_RISE, H14_RISE, H14_RISE, 0, 0], out="L", closed=True)
h.swing("icicle_bell", H14_PIV, [0, 0, 1], H14_AMP, H14_PER, [dict(center=[0, -H14_L, 0], size=BELL, yaw=H14_BELL_YAW)] + foot,
        visual=f"Brass bell ({BELL[0]:g}x{BELL[1]:g}x{BELL[2]:g} collider, turned {H14_BELL_YAW:g} deg to the swing plane so no face is square to it) "
               f"hung with icicles on a {H14_L:g}-stud hanger from the timber gantry, swinging east-west across the lane; blocker 2 = invisible "
               f"collider foot {H14_FOOT[0]:g}x{H14_FOOT[1]:g}x{H14_FOOT[2]:g} (yaw 0, its north/south faces square to the shot line) under the "
               f"bell lip, bottom {H14_FOOT_GAP:g} above the felt at rest (bell bottom {H14_GAP:g})"
               + (f", built from {H14_FOOT_STRIPS} strips whose bottom corners sit on an arc about the hinge (radius {_r0:g}), so "
                  f"no corner ever comes closer than {H14_FOOT_GAP:g} to the felt; blockers 2..{H14_FOOT_STRIPS + 1}" if H14_FOOT_STRIPS else "")
               + "; the bell mesh gets a matching brass clapper-skid plate over the foot (its underside follows the arc)")
h.tee(0, 0, 0)
h.cup(*H14_CUP, flag_h=7.5)
if K("h14_good_side", True):
    h.wp("good", "side_line", [K("h14_side_x", 2.7), 0.0, H14_Z - 5.0], ["lane"], carry=K("h14_side_carry", 2.0))
# 2026-10-12 late (Playtest: the side line was tagged good only, so average golfers only went straight at the bell): average gets it too
H14_AVG_SIDE = K("h14_avg_side", False)
if H14_AVG_SIDE:
    h.wp("average", "side_line", [K("h14_side_x", 2.7), 0.0, H14_Z - 5.0], ["lane"], carry=K("h14_side_carry", 2.0))
h.d["cup_from"] = {"good": ["green", "lane2", "ramp"] if K("h14_good_side", True) else None,
                   "average": ["green", "lane2", "ramp"] if H14_AVG_SIDE else None}
h.anchor("bell_gantry", [0, 0, H14_Z], f"Timber bell gantry hung with icicles (legs outside the rails at x +-5, beam at y {H14_PIV[1]:g}); the "
         "icicles hang from the beam only, >= 8 above the felt", landmark=True, size=[10, H14_PIV[1] + 1, 1.5],
         occluders=[((-5.0, H14_PIV[1] / 2, H14_Z), (0.8, H14_PIV[1], 0.8)), ((5.0, H14_PIV[1] / 2, H14_Z), (0.8, H14_PIV[1], 0.8)),
                    ((0, H14_PIV[1] + 0.5, H14_Z), (10, 1.0, 1.0))])
h.anchor("icicle_bell", [H14_PIV[0], H14_PIV[1] - H14_L, H14_Z], f"Moving mesh: brass bell with an icicle fringe (pivot at the hinge {H14_PIV}); "
         "base skid plate matches the collider foot; it rings softly at each end of its swing", size=BELL)
h.d["safe_route"] = dict(kind="intentional side line", note="Play down the east side of the lane outside the bell's touch band, or bank off the "
                         "west rail; the central line is timed.")
sign(h, "safe_side_sign", (-5.0, 0, -9), "SAFE SIDE: hug a rail past the bell. CENTRE: wait for the swing.", (0, -1))
felt_arrow(h, "timing_arrow", [0, 0, -16], "CENTRE: wait until the bell swings clear")
h.anchor("buoy_float", [9, 0.8, -42], "Striped harbour buoys and a coil of frosted rope outside the green's east rail", size=[3, 2, 3])
snowpuffs(h, [-10, 0.8, -42], "ringing hand-bells in time with the big bell, on a snow bank beside the green")
holes.append(h)

# ================================================================ H15 Frozen Falls (par 2): drop between levels
H15_LHW = K("h15_lane_hw", 3.5)
H15_LIP = -20.0                 # world.json tier step
H15_DROP = 4.0
H15_BACK = K("h15_back", (-34.0, 0.6))  # basin back slope: starts at z, rises by
H15_CUP = K("h15_cup", [3.5, -31.0])
h = new_hole(15, "h15", "Frozen Falls", 2, "The Great Frozen Falls pouring 146 studs off the terrace edge into the clouds, right beside the green",
             "Drop between levels: putt over the lip of a frozen waterfall and fall 4 studs into a basin green")
yl_ = -H15_DROP
bz, brise = H15_BACK
h.rect("lip_lane", -H15_LHW, H15_LHW, 2, H15_LIP, 0.0, zone="lane")
h.rect("basin", -9.5, 9.5, H15_LIP, bz, yl_, zone="basin")
h.rect("basin_back", -9.5, 9.5, bz, -39.5, zone="basin", slope=("z", yl_, yl_ + brise))
h.drop("d1", "lane", "basin", f"lane north edge z={H15_LIP:g} (the frozen-fall lip)", H15_DROP)
h.wall_path([(H15_LHW, H15_LIP), (H15_LHW, 2), (-H15_LHW, 2), (-H15_LHW, H15_LIP)], 0.0, out="L", ext=(0.0, 0.0), name="lane_rail")
h.wall_path([(-H15_LHW, H15_LIP), (-9.5, H15_LIP), (-9.5, bz), (-9.5, -39.5), (9.5, -39.5), (9.5, bz), (9.5, H15_LIP), (H15_LHW, H15_LIP)],
            [yl_, yl_, yl_, yl_ + brise, yl_ + brise, yl_, yl_, yl_], out="L", ext=(0.0, 0.0), name="basin_rail")
h.tee(0, 0, 0)
h.cup(H15_CUP[0], yl_, H15_CUP[1], flag_h=7.5)
h.d["cup_from"] = ["basin"]
h.wp("all", "lip", [K("h15_lip_x", 0.0), 0.0, H15_LIP + 1.0], ["lane"], carry=K("h15_carry", 6.0))
h.anchor("great_frozen_falls", [13.5, yl_, -30], "The Great Frozen Falls: a 26-wide frozen cascade pouring off the terrace edge east of the basin "
         "into the cloud sea (world.json waterfall); the hole's lip is a little frozen-fall of its own", landmark=True, size=[26, 40, 8])
# 2026-10-13 02:45: was [0,-2,-20] 7x4x1 (straddling both felts, touching basin_rail4/10). Now tucked under the lane's lip: z -19.35..-19.85,
# y -3.85..-0.4 (below the lane felt's head room, above the basin felt), x -3.35..3.35 (0.15 clear of the lane and basin rails)
h.anchor("lip_ice", [0, -3.85, H15_LIP + 0.4], "Frozen-fall lip: glassy icicle curtain on the 4-stud step face under the lane's open end, hanging "
         "from just under the felt edge to just above the basin", size=[2 * H15_LHW - 0.3, 3.45, 0.5])
h.anchor("ice_parapet", [0, 0, H15_LIP + 0.2], "Clear ice parapet across the open lip (mesh for the lip_parapet PlayerGuard; the ball passes "
         "through it, CanCollide off for the ball). x -3.35..3.35 between the lane rails, z -19.65..-19.95, 3.5 tall; keep it near-invisible "
         "glass with a frosted top edge", size=[2 * H15_LHW - 0.3, 3.5, 0.3])
h.anchor("steps", [-7.75, yl_, -15.675], "Player steps down the tier outside the lane's west rail: x -9.5..-6, z -12..-19.35, rise 4 in 5 steps "
         "(1.5 tread), from the lane pad (y 0) to a y -4 landing south of basin_rail4; 3.5-high railing on the open side. Clear of all felt and "
         "rails", size=[3.5, 4, 6.7])
for k, zz in enumerate((-12.0, -16.0)):
    felt_arrow(h, f"chevron_{k + 1}", [0.0, 0.0, zz], "Glowing felt chevron pointing -Z: one-way drop ahead (the ball won't come back up)",
               size=(2.4, 0.01, 1.2))
snowpuffs(h, [-12.0, yl_, -30], "on an ice ledge beside the basin, one about to slide down the frozen falls")
h.d["vr_comfort"] = dict(
    player_guards=[dict(id="lip_parapet", center=[0, 1.75, H15_LIP + 0.2], size=[2 * H15_LHW + 1.0, 3.5, 0.3], yaw=0,
                        note="clear ice parapet (PlayerGuard: the ball passes) across the open lip so nobody steps off the 4-stud drop")],
    tier_steps=dict(id="falls_steps", anchor="steps", position=[-7.75, yl_, -15.675], size=[3.5, 4, 6.7],
                    where="outside the west rail, x -6..-9.5 from z -12 to -19.35, landing south of basin_rail4", rise=4.0, steps=5,
                    tread=1.5, railing="3.5-high railing on the open side + parapet along the upper pad edge"),
    note="player-only; the ball sees felt, rails and the drop")
holes.append(h)

# ================================================================ H16 Moonwell (par 2): funnel bowl, cup off the funnel's exit line
H16_DEPTH = K("h16_depth", 0.8)       # well floor below the rim
H16_TW = K("h16_trough_hw", 1.5)      # flat trough half-width = the exit neck
H16_WELL_Z = K("h16_well_z", (-12.0, -30.0))
H16_CUP = K("h16_cup", [3.2, -35.5])
h = new_hole(16, "h16", "Moonwell", 2, "Moonstone well ringed with glowing ice crystals",
             "Funnel: a moonstone well bowl gathers the ball into its spout, with the cup set off the funnel's exit line")
wz0, wz1 = H16_WELL_Z
yd = -H16_DEPTH
h.rect("lane", -3, 3, 2, wz0, 0.0, zone="lane")
h.rect("well_floor", -H16_TW, H16_TW, wz0, wz1, yd, zone="well")
h.rect("well_w", -9.5, -H16_TW, wz0, wz1, zone="well", slope=("x", 0.0, yd))
h.rect("well_e", H16_TW, 9.5, wz0, wz1, zone="well", slope=("x", yd, 0.0))
h.rect("green", -9.5, 9.5, wz1, -39.5, yd, zone="green")
h.drop("d1", "lane", "well", f"lane north edge z={wz0:g}, onto the well floor and slopes", round(H16_DEPTH * (9.5 - 3) / (9.5 - H16_TW), 3))
h.wall_path([(-3, 2), (-3, wz0), (-9.5, wz0), (-9.5, -39.5), (9.5, -39.5), (9.5, wz0), (3, wz0), (3, 2)],
            [0, 0, 0, yd, yd, 0, 0, 0], out="L", closed=True, ybot=yd - 0.5)
h.wall_free((-9.5, wz1), (-H16_TW, wz1), 0.0, name="spout_w", ybot=yd - 0.5)
h.wall_free((H16_TW, wz1), (9.5, wz1), 0.0, name="spout_e", ybot=yd - 0.5)
h.tee(0, 0, 0)
h.cup(H16_CUP[0], yd, H16_CUP[1], flag_h=7.5)
h.d["cup_from"] = ["green", "well"]
h.wp("all", "spout", [0.0, yd, wz1 - 1.0], ["lane"], carry=K("h16_carry", 2.0))
h.anchor("moonwell", [0, yd, (wz0 + wz1) / 2], "Moonstone well: pale pearl stone coping round the funnel, the two felt slopes dressed as worn moonstone "
         "flags with silver inlay, glowing ice-crystal clusters on the rim (outside the rails), a crescent-moon spout at the exit (crescent_spout_w/e, outside the rails)",
         landmark=True, size=[20, 2, 18], occluders=[((-10.8, 1.0, -22), (1.5, 2.0, 10)), ((10.8, 1.0, -22), (1.5, 2.0, 10))])
for _nm, _x in (("crescent_spout_w", -10.9), ("crescent_spout_e", 10.9)):
    h.anchor(_nm, [_x, 0, wz1], "Moonstone crescent-moon horn standing outside the side rail in line with the spout walls, framing the exit "
             "(the pair reads as the crescent spout); x 10.15..11.65 from centre, 0.15 clear of rail3/rail5, off the felt", size=[1.5, 3, 1.5])
felt_arrow(h, "spout_glow", [0.0, yd, wz1 + 1.0], "Crescent-moon glow decal in the trough pointing at the spout", size=(2.0, 0.01, 2.0))
h.anchor("moon_view", [0, 0, -300], "The low moon sits behind the player (bearing 220); from the green you see it framed by the Spire", size=[1, 1, 1])
snowpuffs(h, [11.5, 0, -36], "gazing at the moon through a little brass telescope")
holes.append(h)

# ================================================================ H17 Aurora Bridge (par 3): timed light bridge vs fixed ice bridge
# Span z -16..-42 (world.json): the Aurora Gap, open sky. Straight on: railed crystal piers reach out from both rims, joined by an 8-stud
# aurora LIGHT SPAN that fades in, holds solid, dims away and is gone (collider only while fully solid). To the right: the fixed railed ice
# bridge (the long way), with the railed player deck beside it. A ball in the gap respawns at the light-route entry (+1).
H17_GAP = (-16.0, -42.0)
H17_SPAN = K("h17_span", (-25.0, -33.0))       # light span z range (the rest of the light route is fixed crystal pier)
H17_PHW = K("h17_pier_hw", 1.5)
H17_BR = K("h17_bridge_x", (4.0, 8.0))
H17_PROF = K("h17_profile", (0.6, 6.0, 0.6, 1.8))   # fade_in, solid, fade_out, gone (s)
H17_CUP = K("h17_cup", [2.2, 0.0, -56.0])
H17_GX = K("h17_green_x", (-8.0, 8.0))
H17_RAIL_CLEAR = K("h17_rail_clear", 0.15)   # pier rails stop this far from the light span (Round 3)
h = new_hole(17, "h17", "Aurora Bridge", 3, "An aurora ribbon pouring down from the sky to form the light span",
             "Timed light bridge: an aurora ribbon span fades in, holds solid, then dims away; or take the fixed ice bridge the long way; "
             "misses respawn at the gap edge (+1)")
g0, g1 = H17_GAP
s0, s1 = H17_SPAN
bx0, bx1 = H17_BR
fi, so, fo, go = H17_PROF
per17 = fi + so + fo + go
H17_RIM = K("h17_rim_z", g0 + 4.0)   # shore strip by the gap rim (respawn zone): from here a good golfer takes the safe bridge
h.rect("shore", -6, 8, 2, H17_RIM, 0.0, zone="shore")
h.rect("rim", -6, 8, H17_RIM, g0, 0.0, zone="rim")
h.rect("pier_s", -H17_PHW, H17_PHW, g0, s0, 0.0, zone="pier", kind="pier")
h.rect("light_span", -H17_PHW, H17_PHW, s0, s1, 0.0, zone="pier", kind="bridge",
       timed=dict(part="aurora_span", period_s=per17, solid=[fi, fi + so], phase_s=0.0))
h.rect("pier_n", -H17_PHW, H17_PHW, s1, g1, 0.0, zone="pier", kind="pier")
h.rect("ice_bridge", bx0, bx1, g0, g1, 0.0, zone="bridge", kind="bridge")
h.rect("green", H17_GX[0], H17_GX[1], g1, -63.5, 0.0, zone="green")
h.hazard("aurora_gap", "pit", -13, 13, g0, g1, -30.0, respawn=K("h17_respawn", [0.0, 0.0, g0 + 1.5]))
h.d["moving_parts"].append(dict(
    id="aurora_span", type="toggle", pivot=[0.0, 0.0, (s0 + s1) / 2], axis=[0, 1, 0], period_s=per17, phase_s=0.0,
    profile=[dict(state="fade_in", s=fi), dict(state="solid", s=so), dict(state="fade_out", s=fo), dict(state="gone", s=go)],
    solid_window=[fi, fi + so], felt_ids=["light_span"], blockers=[], speed=0.0, speed_units="-", range=None,
    visual=f"Aurora ribbon span {2 * H17_PHW:g} x {s0 - s1:g} (Neon, animated mint->violet gradient) between the crystal piers. Cycle {per17:g} s from t=0: "
           f"FADE IN {fi:g} s (Transparency 1 -> 0, CanCollide false) -> SOLID {so:g} s (Transparency 0, CanCollide TRUE) -> FADE OUT {fo:g} s "
           f"(0 -> 0.85, CanCollide false) -> GONE {go:g} s (Transparency 1, CanCollide false). The collider exists ONLY in the solid window "
           f"[{fi:g}, {fi + so:g}) s; a ball on it when it switches off falls into the gap (+1, respawn at the light-route entry)."))
h.wall_path([(-H17_PHW, g0), (-6, g0), (-6, 2), (8, 2), (8, g0)], 0.0, out="R", ext=(0.0, 0.0), name="shore_rail")
h.wall_path([(H17_PHW, g0), (bx0, g0)], 0.0, out="L", ext=(0.0, 0.0), name="shore_rail")
for nm, za, zb in (("pier_s", g0, s0 + H17_RAIL_CLEAR), ("pier_n", s1 - H17_RAIL_CLEAR, g1)):
    h.wall_path([(-H17_PHW, za), (-H17_PHW, zb)], 0.0, out="L", ext=(0.0, 0.0), name=nm + "_rail")
    h.wall_path([(H17_PHW, zb), (H17_PHW, za)], 0.0, out="L", ext=(0.0, 0.0), name=nm + "_rail")
h.wall_path([(bx0, g0), (bx0, g1)], 0.0, out="L", ext=(0.0, 0.0), name="bridge_rail")
h.wall_path([(bx1, g1), (bx1, g0)], 0.0, out="L", ext=(0.0, 0.0), name="bridge_rail")
h.wall_path([(H17_GX[1], g1), (H17_GX[1], -63.5), (H17_GX[0], -63.5), (H17_GX[0], g1), (-H17_PHW, g1)], 0.0, out="R", ext=(0.0, 0.0), name="green_rail")
h.wall_path([(bx0, g1), (H17_PHW, g1)], 0.0, out="L", ext=(0.0, 0.0), name="green_rail")
h.tee(0, 0, 0)
h.cup(*H17_CUP, flag_h=7.5)
h.d["cup_from"] = {"good": ["green", "shore", "pier"], "average": ["green"]}
for sk, zs_ in (("good", ["rim"]), ("average", ["shore", "rim"])):
    h.wp(sk, "bridge_line", [(bx0 + bx1) / 2, 0.0, g0 + 5.0], zs_, carry=0.0)
    h.wp(sk, "bridge_out", [(bx0 + bx1) / 2, 0.0, g1 - 2.0], zs_ + ["bridge"], carry=K("h17_avg_carry", 3.0))
h.anchor("aurora_ribbon", [0, 0, (s0 + s1) / 2], "An aurora ribbon pours down out of the sky (Neon, mint #5CFFB0 -> violet #B07CFF) and pools into the "
         "light span; it brightens as the span fades in and frays into sparkles as it dims. Ribbon above y 10 only", landmark=True, size=[3, 60, 8])
h.anchor("crystal_piers", [0, 0, (g0 + g1) / 2], f"Two glowing crystal piers ({2 * H17_PHW:g} wide, 9 long each) with frosted ice rails, reaching out "
         "from both rims toward each other; ends 0.15 short of the rim rails (z -16.65..-41.35)", size=[2 * H17_PHW + 1, 1.5, 24.7])
h.anchor("ice_bridge", [(bx0 + bx1) / 2, 0, (g0 + g1) / 2], "Fixed railed ice bridge (glass deck, snow-capped timber ball rails); ends 0.15 short of shore_rail5 and green_rail16 (z -16.65..-41.35)", size=[bx1 - bx0 + 1, 2, 24.7])
h.anchor("span_respawn_stone", h.d["hazards"][0]["respawn"], "Glowing aurora-lime marker stone flush in the felt at the light-route entry: where a ball "
         "that falls into the gap reappears", size=[0.8, 0.02, 0.8])
h.anchor("span_lamp", [-2.75, 0, g0 - 0.95], "Crystal timing lamp just past shore_rail1 beside the pier mouth (off the rim felt, over the gap edge): glows mint while the span is solid, violet while it fades, "
         "dark while it is gone (visual cue)", size=[0.6, 2.4, 0.6])
sign(h, "sign_light", (-2.6, 0, g0 + 3.0), "Sign 'Aurora span - wait for the glow!' beside the light route", (0, -1), size=(1.6, 2.6, 0.2))
sign(h, "sign_bridge", (8.6, 0, g0 + 5.0), "Lantern sign 'Ice bridge - the long, safe way' pointing to the fixed bridge", (-0.4, -1))
felt_arrow(h, "route_arrow_light", [0, 0, g0 + 4.0], "LIGHT SPAN: straight north (timed)", facing=(0, -1))
felt_arrow(h, "route_arrow_bridge", [(bx0 + bx1) / 2, 0, g0 + 4.0], "ICE BRIDGE: north along the railed crossing", facing=(0, -1))
H17_DECK = (bx1 + 0.5, min(bx1 + 4.5, 12.5))
h.d["vr_comfort"] = dict(
    player_guards=[dict(id="guard_south_rim", center=[0, 2.0, g0 + 0.25], size=[26, 4, 0.3], yaw=0, note="south gap rim (PlayerGuard: the ball passes)"),
                   dict(id="guard_north_rim", center=[0, 2.0, g1 - 0.25], size=[26, 4, 0.3], yaw=0, note="north gap rim"),
                   dict(id="guard_light_w", center=[-H17_PHW - 0.15, 2.0, (g0 + g1) / 2], size=[0.3, 4, 26], yaw=0, note="both sides of the light route"),
                   dict(id="guard_light_e", center=[H17_PHW + 0.15, 2.0, (g0 + g1) / 2], size=[0.3, 4, 26], yaw=0, note="")],
    player_deck=dict(id="ice_walk_deck", x=list(H17_DECK), z=[g0, g1], y=0.0, width=round(H17_DECK[1] - H17_DECK[0], 2),
                     rails="both, 3.5 high with solid lower board", note="railed walk-on ice deck beside the safe ball bridge"),
    note="player-only; the ball sees felt, rails and the pit/respawn")
holes.append(h)

# ================================================================ H18 Halo Arch (par 4): finale
# Tee lane north into a crystal bank (NE corner) that turns the ball west across the plaza; a second crystal bank (SW corner) turns it north
# up the ramp onto the raised green under the Halo Arch. Read the two banks; the cup sits east of the ramp line.
H18_RISE = K("h18_rise", 0.5)  # 2026-10-12 late: 0.8 -> 0.5 (ramp slope 0.08 -> 0.05); balls rolled back to the SW-bank foot at 40-50% power
H18_PLAZA = (-17.5, 4.0, -16.0, -28.0)    # x0, x1, z0, z1
H18_RAMP = (-17.5, -9.5, -38.0)           # x0, x1, top z
H18_GREEN = K("h18_green", (-17.5, 17.5, -60.0))
H18_CUP = K("h18_cup", [-4.0, -46.0])
h = new_hole(18, "h18", "Halo Arch", 4, "Halo Arch: a glowing translucent ice arch over the final green framing the aurora, Starfrost Spire to the south-east",
             "Finale: read two crystal banks round the plaza, climb the ramp onto the raised green under the Halo Arch")
px0, px1, pz0, pz1 = H18_PLAZA
rx0, rx1, rz1 = H18_RAMP
gx0, gx1, gz1 = H18_GREEN
y = H18_RISE
h.rect("lane", -4, 4, 2, pz0, 0.0, zone="lane")
h.rect("plaza_w", px0, rx1, pz0, pz1, 0.0, zone="plaza_w")
h.rect("plaza", rx1, px1, pz0, pz1, 0.0, zone="plaza")
h.rect("ramp", rx0, rx1, pz1, rz1, zone="ramp", slope=("z", 0.0, y))
h.rect("green", gx0, gx1, rz1, gz1, y, zone="green")
H18_CHUTE = K("h18_chute", (-7.3, -5.7))   # narrow crystal chute (x range) through the plaza's north wall: the risky ace line
cx0, cx1 = H18_CHUTE
h.rect("chute", cx0, cx1, pz1, rz1, zone="chute", slope=("z", 0.0, y))
h.wall_path(*dedupe([(-4, 2), (-4, pz0), (px0, pz0), (px0, pz1), (rx0, rz1), (gx0, gz1), (gx1, gz1), (gx1, rz1), (cx1, rz1), (cx1, pz1), (px1, pz1),
                     (px1, pz0), (4, pz0), (4, 2)], [0, 0, 0, 0, y, y, y, y, y, 0, 0, 0, 0, 0]), out="L", closed=True, top=y + 2.4)
h.wall_free(((rx1 + cx0) / 2, pz1), ((rx1 + cx0) / 2, rz1), y, name="chute_divider", height=2.4, ybot=-0.5, thick=cx0 - rx1)
h.bank_wall("crystal_bank_ne", (px1, pz0 - 4.0), (px1 - 8.0, pz1), "R", zone="plaza", ext_bank=0.3, ext_back=0.6)
h.bank_wall("crystal_bank_sw", (px0 + K("h18_sw_shift", 1.6), pz1), (px0 + K("h18_sw_shift", 1.6) + 12.0, pz0), "R", zone="plaza_w", ext_bank=0.3, ext_back=0.6)
h.tee(0, 0, 0)
h.cup(H18_CUP[0], y, H18_CUP[1], flag_h=7.5)
h.d["cup_from"] = ["green", "ramp", "plaza_w", "chute"]
h.wp("all", "ne_bank", [K("h18_wp1_x", 0.0), 0.0, -23.0], ["lane"], carry=K("h18_c1", 10.0))
h.wp("all", "ramp_foot", [-13.5, 0.0, -25.5], ["plaza"], carry=K("h18_c2", 1.0))
h.wp("all", "ramp_top", [-13.5, y, rz1 - 3.0], ["plaza_w", "ramp"], carry=K("h18_c3", 3.0), power_scale=K("h18_ps3", 1.2))
h.anchor("halo_arch", [0, y, -52], "Halo Arch: a translucent glowing ice arch (Glass 0.3 + crystal-core neon) 46 wide and 34 tall spanning the green "
         "east-west; its feet stand outside the footprint at x +-23 (world dressing), clear opening 18 high, so nothing is lower than 18 over "
         "the felt; it frames the aurora to the north", landmark=True, size=[46, 34, 4],
         occluders=[((-23.0, 17, -52), (4, 34, 4)), ((23.0, 17, -52), (4, 34, 4)), ((0, y + 18 + 8, -52), (46, 16, 4))])
for nm, at in (("crystal_bank_ne_deco", [px1 - 4.0, 0, pz1 + 2.0]), ("crystal_bank_sw_deco", [px0 + 6.0, 0, pz0 - 6.0])):
    h.anchor(nm, at, "Faceted ice-crystal wall dressing the 45-degree banked felt and its backing rail (crystal clusters 3-5 tall behind the rail, "
             "glowing cyan); the banked felt itself is frosted glass-green", size=[9, 4, 2])
# 2026-10-13: the ramp's east "rail" is the 2.2-wide chute_divider; the old 1x9 box stood inside it. Posts (0.6) now stand on the divider
# top (y 2.9), 0.3 clear of the ramp felt edge and of the crystal_chute dressing.
h.anchor("ramp_lanterns", [rx1 + 0.6, 2.9, (pz1 + rz1) / 2], "Brass lanterns on short posts standing on top of the chute divider along "
         "the ramp's east side (posts 0.6 wide, never over the ramp or chute felt)", size=[0.6, 6.1, 10], mounted_on="chute_divider")
felt_arrow(h, "felt_arrow_bank", [0.0, 0.0, -10.0], "Glowing felt arrow decal: 'off the crystals, round and up'", size=(2.0, 0.01, 2.6))
h.anchor("crystal_chute", [(cx0 + cx1) / 2, y / 2, (pz1 + rz1) / 2], f"The Halo Run: a narrow {cx1 - cx0:g}-wide crystal chute (rails dressed as "
         "glowing ice-crystal walls) straight up through the plaza's north wall onto the green: the risky shortcut / ace line", size=[cx1 - cx0 + 2, 3, 10])
felt_arrow(h, "ramp_chevrons", [-13.5, y / 2, (pz1 + rz1) / 2], "Felt chevrons up the ramp pointing -Z", size=(6, 0.01, 2))
snowpuffs(h, [21.3, y, -44], "in a grandstand of snow blocks beside the final green (outside the east rail), holding up score cards", size=[6, 3, 4])
holes.append(h)

# ---------------------------------------------------------------- course
course = {
    "course": "Aurora Archipelago",
    "schema": SCHEMA,
    "physics": {"source": "the builder's real game values (measured for Lantern Grove; mirrored as constants in tools/sim.py)",
                "stud_m": S.STUD_M, "gravity_studs_s2": S.GRAVITY,
                "rolling_decel": "0.5 + 0.25*speed studs/s^2 (x decel_scale on ice felt)", "rolling_decel_const": S.ROLL_DECEL_CONST,
                "rolling_decel_per_speed": S.ROLL_DECEL_PER_SPEED, "wall_restitution": S.WALL_RESTITUTION,
                "bumper_restitution": S.BUMPER_RESTITUTION, "cup_capture_speed_studs_s": S.CUP_CAPTURE_SPEED,
                "cup_radius": S.CUP_RADIUS, "ball_radius": S.BALL_RADIUS, "max_putt_speed_studs_s": S.V_MAX,
                "max_putt_flat_roll_studs": S.MAX_PUTT_STUDS,
                "max_putt_note": "V_MAX derived so a full putt rolls 60 studs (18 m) on flat felt",
                "drop_speed_keep": 0.8,
                "surfaces": {"felt": {"decel_scale": 1.0},
                             "ice": {"decel_scale": ICE_DECEL_SCALE, "status": "START VALUE - calibrate in Studio before tuning H4 further",
                                     "calibration": "Fire 5 putts at 5.0 studs/s on the H4 ice strip; the sim rolls 28.5 studs (felt: 10.0). Set the "
                                                    "ice collider's CustomPhysicalProperties friction until Studio matches, or report the measured "
                                                    "distance and the designer refits decel_scale (distance = v/k - a/k^2 ln(1 + k v/a), a = 0.5 s, k = 0.25 s)."}},
                "stroke_timeout_safety_net_s": 20, "stroke_cap": 8},
    "total_par": sum(x.d["par"] for x in holes),
    "holes": [x.d for x in holes],
}


# ---------------------------------------------------------------- fit check against the world.json concept pads
def fit_report(hole):
    """every felt corner, wall corner and moving-part blocker (over its motion) must lie inside the union of the hole's concept pads (x/z)."""
    pads = PLACE[hole["number"]]["concept"]["pads"]

    def inside(x, z, tol=0.02):
        return any(p["x"][0] - tol <= x <= p["x"][1] + tol and p["z"][0] - tol <= z <= p["z"][1] + tol for p in pads)

    bad = []
    for p in hole["felt"]:
        for lx, lz in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            dx, dz = rot(lx * p["size"][0] / 2, lz * p["size"][1] / 2, p["yaw"])
            x, z = p["center"][0] + dx, p["center"][2] + dz
            if not inside(x, z):
                bad.append(f"felt {p['id']} corner ({x:.2f},{z:.2f})")
    for w in hole["walls"]:
        for lx, lz in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            dx, dz = rot(lx * w["size"][0] / 2, lz * w["size"][2] / 2, w["yaw"])
            x, z = w["center"][0] + dx, w["center"][2] + dz
            if not inside(x, z):
                bad.append(f"wall {w['id']} corner ({x:.2f},{z:.2f})")
    for m in hole.get("moving_parts", []):
        piv = m["pivot"]
        for b in m.get("blockers", []):
            reach = math.hypot(abs(b["center"][0]) + b["size"][0] / 2, abs(b["center"][2]) + b["size"][2] / 2)
            if m["type"] == "rotate" and abs(m["axis"][1]) > 0.9:
                pts = [(piv[0] + reach * math.cos(a), piv[2] + reach * math.sin(a)) for a in [k * math.pi / 8 for k in range(16)]]
            elif m["type"] == "slide" and abs(m["axis"][1]) < 0.9:
                pts = [(piv[0] + b["center"][0] + m["axis"][0] * off + sx * b["size"][0] / 2, piv[2] + b["center"][2] + m["axis"][2] * off)
                       for off in m["range"] for sx in (-1, 1)]
            else:
                pts = [(piv[0] + b["center"][0], piv[2] + b["center"][2])]
            for x, z in pts:
                if not inside(x, z, tol=0.3):
                    bad.append(f"mover {m['id']} reach ({x:.2f},{z:.2f})")
    return bad


# 2026-10-13 decoration clearance pass (tools/deco_clearance.py): free-standing dressing props are nudged the least XZ distance
# that leaves 0.15 studs to every rail/wall, the felt head room (felt-0.4..+8) and other props. Visual anchors only; play geometry untouched.
from deco_clearance import settle as _deco_settle
DECO_SETTLE = [(3, "sign_plank"), (3, "sign_bridge"), (9, "sign_spit"), (9, "sign_route"), (11, "sign_channel"), (12, "sign_bypass"),
         (17, "sign_light"), (17, "sign_bridge"), (6, "snowpuffs"), (7, "snowpuffs"), (10, "snowpuffs"), (12, "snowpuffs"),
         (14, "buoy_float"), (11, "fishing_hut"), (10, "bobsled_hut"), (7, "coral_fans"), (14, "bell_gantry")]
_deco_settle(course, set(DECO_SETTLE))

fits = {}
for hd in course["holes"]:
    b = fit_report(hd)
    fits[hd["number"]] = b
    hd["footprint_fit"] = {"pads": PLACE[hd["number"]]["concept"]["pads"], "outside": len(b)}
with open(OUT, "w") as f:
    json.dump(course, f, indent=1)
print(f"wrote {os.path.normpath(OUT)}: {len(holes)} holes, total par {course['total_par']}")
for n, b in fits.items():
    if b:
        print(f"  FIT H{n}: {len(b)} points outside the world.json pads, e.g. {b[:3]}")
