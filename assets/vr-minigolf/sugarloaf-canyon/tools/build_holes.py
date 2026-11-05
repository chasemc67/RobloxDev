#!/usr/bin/env python3
"""Source of truth for ../holes.json (Sugarloaf Canyon, 18 holes). Edit here, then: python3 tools/build_holes.py
Adapted from lantern-grove/tools/build_holes.py. Every playtest-round change is made in this file and logged in playtest-log.md.

Placement: each hole's world_offset / world_yaw are read from ../world/world.json (holes[].placement = {origin, yaw_deg}), so
holes.json and the world layout can't drift apart. Local frame: tee at the origin, play toward local -Z. Every felt piece, rail
and moving part must fit inside the hole's world.json concept pads (checked at the end of this script: `fit` report).
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from geom import Hole, arm_blockers, T, offset_polyline, turn_deg, octagon_pts, rot
import math
r4 = lambda v: round(v, 4)
import sim as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("SC_OUT") or os.path.join(HERE, "..", "holes.json")
# Sweep hook (tools/sweep.py): SC_VARIANT='{"h6_dwell": [1.5, 2.0], ...}' overrides the tuning knobs below; SC_OUT writes elsewhere.
VAR = json.loads(os.environ.get("SC_VARIANT") or "{}")
WORLD = json.load(open(os.path.join(HERE, "..", "world", "world.json")))
PLACE = {h["number"]: h for h in WORLD["holes"]}


def K(key, default):
    """tuning knob (default = the committed value)"""
    return VAR.get(key, default)


def collision_cut(h, ids, lo, hi, mover):
    """Subtract a hole-local AABB from axis-aligned boxes, retaining exact residual boxes."""
    h.d.setdefault("collision_cuts", []).append(dict(mover=mover, targets=ids, min=lo, max=hi, clearance=0.15))
    for collection in ("walls", "felt"):
        result=[]
        for b in h.d[collection]:
            if b["id"].split("__cut")[0] not in ids:
                result.append(b); continue
            assert abs(b.get("yaw",0) % 90) < .001
            c=b["center"]; felt=collection=="felt"
            sz=[b["size"][0], b.get("thickness",.4), b["size"][1]] if felt else b["size"][:]
            if int(round(b.get("yaw",0)/90))%2: sz[0],sz[2]=sz[2],sz[0]
            a=[c[k]-sz[k]/2 for k in range(3)]; z=[c[k]+sz[k]/2 for k in range(3)]
            if felt: a[1]=c[1]-sz[1];z[1]=c[1]
            il=[max(a[k],lo[k]) for k in range(3)]; ih=[min(z[k],hi[k]) for k in range(3)]
            if any(il[k]>=ih[k]-1e-8 for k in range(3)): result.append(b);continue
            chunks=[]
            for k in range(3):
                if a[k]<il[k]:
                    end=z[:];end[k]=il[k];chunks.append((a[:],end));a[k]=il[k]
                if z[k]>ih[k]:
                    start=a[:];start[k]=ih[k];chunks.append((start,z[:]));z[k]=ih[k]
            for q,(a,z) in enumerate(chunks):
                if any(z[k]-a[k] < 1e-6 for k in range(3)): continue
                n=dict(b,id=b["id"]+"__cut"+str(q),yaw=0.0)
                n["center"]=[r4((a[k]+z[k])/2) for k in range(3)]
                n["size"]=[r4(z[k]-a[k]) for k in range(3)]
                if felt:
                    n["center"][1]=z[1];n["thickness"]=z[1]-a[1];n["size"]=[n["size"][0],n["size"][2]];n["edge_support"]=True
                result.append(n)
        h.d[collection]=result


SCHEMA = {
    "version": "1.0",
    "units": "studs (1 stud = 0.3 m). Speeds studs/s, angles degrees, angular speed deg/s.",
    "axes": "Right-handed, +Y up. Each hole has its own local frame: tee at the origin, play generally toward -Z. "
            "Map/top-down view used in all docs and renders: +X to the right (east), -Z up ('north'). "
            "Facing -Z (Roblox LookVector default) the player's right is +X.",
    "world_placement": "world = R_y(world_yaw) * local + world_offset. world_offset [x,y,z] studs, world_yaw degrees. Both are copied from "
                       "world/world.json holes[].placement {origin, yaw_deg} (the source of truth for placement). Roblox: holeRoot = "
                       "CFrame.new(world_offset) * CFrame.Angles(0, math.rad(world_yaw), 0); part.CFrame = holeRoot * localCFrame.",
    "yaw": "Degrees about +Y, right-handed (Roblox CFrame.Angles(0, math.rad(yaw), 0)). Local->world: "
           "x' = lx*cos(yaw) + lz*sin(yaw); z' = -lx*sin(yaw) + lz*cos(yaw). Positive yaw = counter-clockwise in the map view.",
    "felt": "Playable surface pieces. {id, zone, center:[x,y,z] = TOP-surface centre, size:[sx,sz] footprint in local x/z, yaw, "
            "slope:null|{axis:'x'|'z', rise}}. rise = surface height at the +axis end minus the -axis end (local axes); the "
            "surface is a single plane so heights at the ends are center.y +- rise/2. Collision part = a box whose top face is that "
            "plane (thickness free, suggest 0.4; build sloped pieces as a box rotated by atan(rise/len) about the local axis "
            "perpendicular to `axis`, then shifted so the top-surface centre matches). Optional flags: overlay=true (banked plane laid "
            "on top of base felt; its low edge is flush with the base), kind='bank'|'bridge'|'tunnel'|'plate', tunnel=true (felt runs "
            "inside a decorative enclosure; physics unchanged), solid=false + thickness (bridge deck: a ball on a lower level can roll "
            "underneath). kind='plate' (H5 only): a base plate that also runs under the slot rock between the rails; only the part "
            "between the rails is reachable or visible. Pieces join when edges meet/overlap at equal height (tolerance 0.05).",
    "walls": "Invisible collision blocks. {id, center:[x,y,z] = box centre, size:[sx,sy,sz] local box size, yaw, kind?}. kind='bumper' "
             "(static obstacle blocks: boulders, crystals, hoodoos, hubs) uses bumper restitution 0.65; everything else is a wall (0.63). "
             "Authored rails have local Z along the run and local X = thickness 0.5; height is 1.0 above the highest felt they border "
             "(boxes along ramps are simply taller; visual rails can follow the slope). Rails sit OUTSIDE the felt edge (inner face on "
             "the edge).",
    "hazards": "Out-of-bounds volumes below felt level: {id, type:'water'|'pit', center:[x,y,z] (water/pit surface), size:[sx,sz], yaw, "
               "reset:'previous_position'|'respawn', respawn?:[x,y,z], penalty:1}. A ball that leaves the felt over a hazard gets +1 stroke and "
               "is returned to where its stroke started (reset='previous_position'), or, if reset='respawn', placed at rest on the "
               "`respawn` point (a felt point, e.g. a bridge entry). Any ball leaving all felt elsewhere goes back to its stroke start "
               "(and is flagged as an escape bug).",
    "drops": "Intentional level changes: {id, from, to, edge, height}. The upper piece's edge is open (no rail) and the lower felt "
             "starts directly below/beyond it; the ball falls and keeps ~80% of horizontal speed. Lower felt may extend under the "
             "upper piece (the upper piece then acts as a cliff face for the lower level, unless it is a solid=false deck).",
    "moving_parts": "Separate parts. type 'swing' = pendulum: {id, type:'swing', pivot:[x,y,z] (hinge point above the felt), axis (unit "
                    "vector, horizontal; swing plane is perpendicular to it), amplitude_deg, period_s, phase (deg of the swing cycle at t=0), "
                    "blockers (relative to the pivot with the pendulum hanging straight down)}: angle(t) = amplitude_deg*sin(360*t/period_s + phase), "
                    "right-hand rule about axis; `speed` = peak angular speed at the bottom (info), range = [-amp, amp]. "
                    "Other types: {id, type:'rotate'|'slide', pivot:[x,y,z], axis:[ax,ay,az] unit vector, speed (deg/s for rotate, "
                    "studs/s for slide, sign = direction, right-hand rule about axis), range:null (continuous) | [min,max] "
                    "(ping-pong between angles in deg or offsets in studs), phase (angle/offset at t=0), blockers:[{center:[dx,dy,dz] "
                    "relative to pivot at angle/offset 0, size:[sx,sy,sz], yaw, roll?}]} (roll = extra initial rotation in deg about the part axis, "
                    "applied to the blocker's centre and orientation, e.g. vanes at 0/120/240). At time t a blocker is "
                    "pivot + Rot(axis, angle(t)) * center (rotate) or pivot + center + axis*offset(t) (slide). "
                    "Slides may pause: dwell:[{at: offset, s: seconds}]. One cycle = range[0] -> range[1] -> range[0] at |speed|; "
                    "a stop at a range end pauses once per visit, an interior stop on both passes; phase = offset at t=0 on the "
                    "forward (min -> max) pass (if a stop sits at that offset, t=0 is the start of its pause). "
                    "period_s = full cycle incl. pauses (info). The game script must reproduce this "
                    "profile (e.g. tween legs + waits), not a plain sine/ping-pong. All moving colliders: CanCollide = true, moved every "
                    "frame (CFrame per Heartbeat or a constraint), bumper restitution 0.65.",
    "teleports": "{id, entry:{center:[x,y,z], radius, half_size?:[hx,hz]}, exit:{center:[x,y,z], dir:[dx,dz]}, speed_factor, min_speed, max_speed, "
                 "kind?}. A ball whose centre enters the entry radius (or, with half_size, the axis-aligned rectangle centre +- half_size; same "
                 "level, within 0.5) reappears at exit moving along dir with speed = clamp(speed_in*speed_factor, min_speed, max_speed). "
                 "kind='lift' (H11): the trigger is the lock chamber floor; in the game the platform carries the ball up (ride time and "
                 "platform motion in `ride`) and releases it at the exit with that speed. The sim waits for the scheduled release, then transfers it (no other moving part "
                 "on that hole depends on the ride time).",
    "cup": "{position:[x,y,z] (on felt), radius, flag}. Gameplay cup radius 0.5 stud (real cup 4.25 in = 0.36 stud diameter; enlarged ~2.8x for VR "
           "readability). Ball is holed when its centre is within radius and speed < 5.33 studs/s (1.6 m/s). "
           "flag = {pole_height (studs above the cup felt), pole_diameter, banner_size [w,h,t], banner_color, top:[x,y,z] (pole top, "
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


def felt_arrow(h, name, pos, text, size=(1.4, 0.01, 2.0)):
    h.anchor(name, list(pos), text, size=list(size))


# ================================================================ H1 Trailhead Gate (par 2)
# A straight lane into a candy-striped boulder whose 45-degree face (a bumper block turned 45) banks the ball east onto an offset green.
H1_CUP = K("h1_cup", [6.0, 0.0, -30.5])
H1_B = K("h1_boulder", [-1.3, -35.8, 3.0])     # centre x, z, side of the 45-degree boulder block
h = new_hole(1, "h01", "Trailhead Gate", 2, "Candy-striped trailhead arch and the striped bank boulder",
             "Bank shot: a striped boulder's 45-degree face turns the ball east onto an offset green")
h.rect("lane", -3.5, 3.5, 2, -26, 0.0, zone="lane")
h.rect("green", -3.5, 8.5, -26, -38, 0.0, zone="green")
h.wall_path([(-3.5, 2), (-3.5, -38), (8.5, -38), (8.5, -26), (3.5, -26), (3.5, 2)], 0.0, out="L", closed=True)
h.block("boulder", H1_B[0], H1_B[1], H1_B[2], H1_B[2], 0.0, height=2.5, yaw=45.0)
h.tee(0, 0, 0)
h.cup(*H1_CUP, flag_h=7.5)
h.d["cup_from"] = ["green"]
h.wp("all", "boulder_face", [K("h1_wp_x", -0.2), 0.0, -33.0], ["lane"], carry=K("h1_carry", 3.0))
h.anchor("trailhead_arch", [0, 0, -12], "Candy-striped timber trailhead arch over the lane with a hanging swirl-lollipop sign "
         "'Sugarloaf Canyon - Hole 1'; posts outside the rails at x +-4.25, crossbeam bottom 8 above the felt", landmark=True, size=[9.5, 10, 1.2],
         occluders=[((-4.25, 4.5, -12), (0.6, 9, 0.6)), ((4.25, 4.5, -12), (0.6, 9, 0.6)), ((0, 9.25, -12), (9.5, 1.5, 1.2))])
h.anchor("striped_boulder", [H1_B[0], 0, H1_B[1]], f"Striped sandstone boulder (pink/cream bands) dressing the {H1_B[2]:g}x{H1_B[2]:g} bumper turned 45 deg; "
         "its flat south-east face is the bank. Visual may rise to 6 studs but must cover the collider exactly at felt level", size=[4.4, 6, 4.4],
         occluders=[((H1_B[0], 3.0, H1_B[1]), (H1_B[2], 6, H1_B[2]), 45.0)])
h.anchor("lollipop_cactus_1", [6, 0, -18], "Saguaro wearing a swirl lollipop, outside the green's south rail", size=[4, 12, 4],
         occluders=[((6, 6, -18), (1.4, 12, 1.4))])
h.anchor("hitching_post", [-6, 0, -4], "Hitching post and water trough outside the west rail", size=[3, 2, 1])
holes.append(h)

# ================================================================ H2 Mine-Cart Junction (par 3)
H2_CUP = K("h2_cup", [-11.0, 0.0, -46.0])
H2_LT = K("h2_left_x", (-11.0, -8.0))       # open-top shortcut, 3-stud clear width
H2_MID_RISE = K("h2_mid_rise", 0.6)
H2_CROSS = K("h2_cross_z", -42.0)
h = new_hole(2, "h02", "Mine-Cart Junction", 3, "Mine-head with a candy-striped headframe and three timbered tunnel mouths",
             "Tunnel choice: open-top 3-wide shortcut (left), gentle dead end (middle), shorter forgiving long haul (right)")
h.rect("lane", -5, 5, 2, -8, 0.0, zone="lane")
h.rect("plaza", -12, 12, -8, -16, 0.0, zone="plaza")
h.rect("left_tunnel", H2_LT[0], H2_LT[1], -16, -34, 0.0, zone="ltun", tunnel=True, kind="tunnel")
h.rect("mid_tunnel", -2, 2, -16, -28, zone="mtun", slope=("z", 0.0, H2_MID_RISE), tunnel=True, kind="tunnel")
h.rect("right_tunnel", 7, 11, -16, H2_CROSS, 0.0, zone="rtun", tunnel=True, kind="tunnel")
h.rect("crossover", 3, 11, H2_CROSS, -51, 0.0, zone="cross")
h.rect("green", -12, 3, -34, -51, 0.0, zone="green")
h.wall_path([(-5, 2), (-5, -8), (-12, -8), (-12, -16), (H2_LT[0], -16), (H2_LT[0], -34), (-12, -34), (-12, -51), (11, -51), (11, -16),
             (12, -16), (12, -8), (5, -8), (5, 2)], 0.0, out="L", closed=True, top=2.4)
h.wall_path([(H2_LT[1], -16), (-2, -16), (-2, -28), (2, -28), (2, -16), (7, -16), (7, H2_CROSS), (3, H2_CROSS), (3, -34), (H2_LT[1], -34)],
            [0, 0, H2_MID_RISE, H2_MID_RISE, 0, 0, 0, 0, 0, 0], out="L", closed=True, name="rock", top=2.4)
h.tee(0, 0, 0)
h.cup(*H2_CUP, flag_h=7.5)
h.d["cup_from"] = ["green", "ltun", "cross"]
h.wp("good", "left_mouth", [(H2_LT[0] + H2_LT[1]) / 2, 0.0, -17.0], ["lane", "plaza"], carry=K("h2_good_carry", 12.0))
h.wp("good", "left_exit", [(H2_LT[0] + H2_LT[1]) / 2, 0.0, -36.0], ["ltun"], carry=4.0)
h.wp("average", "right_mouth", [9.0, 0.0, -17.0], ["lane", "plaza"], carry=K("h2_avg_carry", 30.0))
h.wp("average", "right_end", [8.5, 0.0, K("h2_avg_end_z", -46.0)], ["rtun"], carry=K("h2_avg_carry2", 1.0))
h.anchor("headframe", [1.0, 0, -22], "Candy-striped timber mine headframe (pulley wheel on top) above the middle tunnel; the three tunnel "
         "portals are timber-framed openings in a striped rock face along z -16 (left 3 wide, middle 4 wide with a 'DEAD END - NO GOLD' "
         "plank sign, right 4 wide). All overhead beams/roof undersides y>=8; headframe legs stay outside the clear middle channel", landmark=True, size=[8, 16, 6],
         occluders=[((1.0, 12, -22), (8, 8, 4))])
h.anchor("rock_face", [0, 0, -17], "Striped rock face flanking the three open-top channels; no roof except portal lintels with underside y=8. "
         "Solid side piers stay outside the clear channel widths; fade dressing between camera and ball", size=[26, 5, 2],
         occluders=[((-5.0, 4.0, -17), (6.0, 2, 2)), ((4.5, 4.0, -17), (5, 2, 2))])
sign(h, "sign_left", (-12.6, 0, -12), "Arrow sign 'Short Cut - tight!' pointing into the LEFT tunnel", (0.3, -1.0))
sign(h, "sign_mid", (-1.2, 8, -15.4), "Plank sign 'DEAD END - NO GOLD' above the middle portal; sign bottom y=8", (0, 1), size=(3.0, 1.0, 0.2))
sign(h, "sign_right", (12.6, 0, -12), "Arrow sign 'Long Haul - safe; firm putt' pointing into the RIGHT tunnel", (-0.3, -1.0))
felt_arrow(h, "felt_arrow_left", [(H2_LT[0] + H2_LT[1]) / 2, 0.0, -14.0], "Glowing sour-apple felt arrow decal (flush) pointing -Z into the left tunnel")
felt_arrow(h, "felt_arrow_right", [9.0, 0.0, -14.0], "Glowing sour-apple felt arrow decal (flush) pointing -Z into the right tunnel")
h.anchor("ore_carts", [-14.5, 0, -42], "Two parked ore carts heaped with rock candy on a short rail spur outside the green and concept pad west edge; visual only, no ball/player collision; fade if occluding camera", size=[3, 2.5, 6], collidable=False, ball_collision=False, player_collision=False)
h.anchor("tunnel_lanterns", [9, 8, -32], "Lanterns on overhead portal-style crossbars every 6 studs; anchor is lantern bottom y=8 (top y=8.8); channel stays open-top", size=[0.6, 0.8, 0.6])
h.anchor("left_open_cut", [(H2_LT[0]+H2_LT[1])/2, 0, -25], "Open-top mine cut: no roof over z=-16..-34. Portal lintel only at z=-16; underside y=8; no camera obstruction down the channel", size=[H2_LT[1]-H2_LT[0], 8, 18])
h.d["vr_clearance"] = {"left_channel": {"open_top": True, "clear_width": H2_LT[1] - H2_LT[0], "x_range": list(H2_LT), "z_range": [-34, -16]}, "all_channel_roofs": "none except portal lintels", "portal_lintel_bottom_y": 8.0, "right_lantern_bottom_y": 8.0}
holes.append(h)

# ================================================================ H3 Ranger's Riverbend (par 3)
H3_HALF = K("h3_half", 1.0)          # half-width of the rail-less log plank
H3_CUP = K("h3_cup", [1.0, 0.0, -55.5])
H3_RIV = (-30.0, -52.0)              # river (water hazard) z range under the plank / footbridge
h = new_hole(3, "h03", "Ranger's Riverbend", 3, "Ranger station with a fire-lookout cupola on the west bank",
             "River crossing: a rail-less log plank straight over the river (risky) or the railed ranger footbridge (safe); a ball in the river respawns at the plank entry")
h.rect("shore", -12.5, 6.5, 2, H3_RIV[0], 0.0, zone="shore")
h.rect("plank", -H3_HALF, H3_HALF, H3_RIV[0], H3_RIV[1], 0.0, zone="plank", kind="bridge")
h.rect("footbridge", -11, -6, H3_RIV[0], H3_RIV[1], 0.0, zone="bridge", kind="bridge")
h.rect("north", -12.5, 8, H3_RIV[1], -69.5, 0.0, zone="green")
h.hazard("river", "water", -13, 13, H3_RIV[0], H3_RIV[1], -1.5, respawn=K("h3_respawn", [0.0, 0.0, -28.5]))
h.wall_path([(H3_HALF, H3_RIV[0]), (6.5, H3_RIV[0]), (6.5, 2), (-12.5, 2), (-12.5, H3_RIV[0]), (-11, H3_RIV[0])], 0.0, out="L", ext=(0.0, 0.0))
h.wall_path([(-6, H3_RIV[0]), (-H3_HALF, H3_RIV[0])], 0.0, out="L", ext=(0.0, 0.0))
h.wall_path([(-11, H3_RIV[0]), (-11, H3_RIV[1])], 0.0, out="L", ext=(0.0, 0.0), name="bridge_rail")
h.wall_path([(-6, H3_RIV[1]), (-6, H3_RIV[0])], 0.0, out="L", ext=(0.0, 0.0), name="bridge_rail")
h.wall_path([(-11, H3_RIV[1]), (-12.5, H3_RIV[1]), (-12.5, -69.5), (8, -69.5), (8, H3_RIV[1]), (H3_HALF, H3_RIV[1])], 0.0, out="L", ext=(0.0, 0.0))
h.wall_path([(-H3_HALF, H3_RIV[1]), (-6, H3_RIV[1])], 0.0, out="L", ext=(0.0, 0.0))
h.tee(0, 0, 0)
h.cup(*H3_CUP, flag_h=7.5)
h.d["cup_from"] = ["green"]
h.wp("good", "plank_far", [0.0, 0.0, H3_RIV[1] - 1.0], ["shore", "plank"], carry=K("h3_good_carry", 4.0))
h.wp("average", "bridge_line", [-8.5, 0.0, -24.0], ["shore"], carry=0.0)
h.wp("average", "bridge_out", [-8.5, 0.0, H3_RIV[1] - 2.0], ["shore", "bridge"], carry=3.0)
h.anchor("ranger_station", [-19, 0, -20], "Ranger station on stilts with a fire-lookout cupola, west of the shore (outside the footprint, "
         "in the world dressing)", landmark=True, size=[10, 18, 10])
h.anchor("log_plank", [0, 0, (H3_RIV[0] + H3_RIV[1]) / 2], f"Rail-less peeled-log plank, felt on top, {2 * H3_HALF:g} wide, straight over the river", size=[2 * H3_HALF + 0.6, 1.2, 22])
h.anchor("ranger_footbridge", [-8.5, 0, (H3_RIV[0] + H3_RIV[1]) / 2], "Railed timber footbridge with rope railings and lantern posts at both ends", size=[6, 3, 22],
         occluders=[((-11.25, 1.5, H3_RIV[0] - 0.3), (0.5, 3, 0.5)), ((-5.75, 1.5, H3_RIV[0] - 0.3), (0.5, 3, 0.5))])
h.anchor("plank_respawn_stone", [0, 0, -28.5], "Glowing turquoise marker stone set flush in the felt at the plank entry: where a ball "
         "that falls in the river reappears", size=[0.8, 0.02, 0.8])
sign(h, "sign_plank", (2.2, 0, -27.5), "Sign 'Log Plank - no rails!' with a splash icon beside the plank entry", (0, -1), size=(1.6, 2.6, 0.2))
sign(h, "sign_bridge", (-13.1, 0, -24), "Ranger sign 'Footbridge - the safe way' pointing to the footbridge", (0.4, -1))
felt_arrow(h, "route_arrow_plank", [0, 0, -25], "RISKY PLANK: straight north toward the narrow crossing")
h.d["decoration_anchors"][-1]["facing"] = [0, -1]
felt_arrow(h, "route_arrow_bridge", [-8.5, 0, -25], "SAFE FOOTBRIDGE: north along the railed crossing")
h.d["decoration_anchors"][-1]["facing"] = [0, -1]
h.anchor("river_rocks", [5, -1.5, -41], "Turquoise river with foam, stepping stones and a sunken canoe downstream", size=[6, 1, 8])
holes.append(h)

# ================================================================ H4 Crystal Corridor (par 3)
H4_CUP = K("h4_cup", [4.5, 0.0, -39.0])
H4_CRY = K("h4_crystals", [  # x, z, sx, sz, yaw
    [-1.8, -11.0, 1.6, 1.6, 45.0],
    [2.6, -16.0, 2.2, 1.0, -35.0],
    [-3.0, -21.0, 2.2, 1.0, 35.0],
    [1.4, -25.5, 1.6, 1.6, 45.0],
    [-1.2, -31.0, 2.0, 1.0, 60.0],
])
h = new_hole(4, "h04", "Crystal Corridor", 3, "Giant pink rock-candy geode wall along the slot",
             "Pinball crystals: static flat-faced rock-candy bumpers bounce the ball down the slot")
h.rect("slot_a", -6, 6, 2, -20, 0.0, zone="slot_a")
h.rect("slot_b", -6, 6, -20, -41, 0.0, zone="slot_b")
h.wall_path([(-6, 2), (-6, -41), (6, -41), (6, 2)], 0.0, out="L", closed=True)
for i, (cx, cz, sx, sz, yw) in enumerate(H4_CRY, 1):
    h.block(f"crystal{i}", cx, cz, sx, sz, 0.0, height=1.6, yaw=yw)
h.tee(0, 0, 0)
h.cup(*H4_CUP, flag_h=7.5)
h.wp("all", "mid", [K("h4_mid_x", 0.3), 0.0, -21.0], ["slot_a"], carry=K("h4_mid_carry", 4.0))
h.wp("all", "c5_east", [3.8, 0.0, -32.5], ["slot_b"], carry=0.5)
h.wp("all", "c5_west", [-4.2, 0.0, -33.5], ["slot_b"], carry=0.5)
for i, (cx, cz, sx, sz, yw) in enumerate(H4_CRY, 1):
    h.anchor(f"crystal_{i}", [cx, 0, cz], f"Rock-candy crystal cluster (pink/amber glass, faint neon core) dressing bumper crystal{i} "
             f"({sx:g}x{sz:g}, yaw {yw:g}); the collider is its flat-faced base, the spikes rise to ~4 studs", size=[sx + 0.4, 4, sz + 0.4],
             occluders=[((cx, 2.0, cz), (sx * 0.8, 4, sz * 0.8), yw)])
h.anchor("geode_wall", [-9, 0, -20], "Giant pink geode cracked open in the west slot wall, glowing", landmark=True, size=[3, 14, 18])
h.anchor("slot_walls", [0, 0, -20], "Slot canyon walls (sage-shadowed sandstone, banded) rise 44 studs either side, beyond the footprint", size=[20, 44, 48])
holes.append(h)

# ================================================================ H5 Echo Slot (par 3): half-pipe S-bend
H5_C = K("h5_center", [[0, 2], [0, -10], [6, -16], [6, -26], [-1, -33], [-1, -38]])
H5_HW = K("h5_hw", 3.5)        # channel half-width (rail inner face to centreline)
H5_BW = K("h5_bank_w", 1.5)    # bank width each side
H5_BR = K("h5_bank_rise", 0.3)  # bank rise
H5_CUP = K("h5_cup", [-0.5, 0.0, -42.0])
h = new_hole(5, "h05", "Echo Slot", 3, "Smooth wave-carved slot walls in pink and cream bands",
             "Half-pipe: an S-bend U-channel with banked felt walls; ride high to carry the bend")
xs = [p[0] for p in H5_C]
PX0, PX1 = min(xs) - H5_HW - 0.5, max(xs) + H5_HW + 0.5
H5_ZS = K("h5_zone_z", (-10.0, -26.0))   # plate split into three zones (one per bend) for the AI waypoints
for zi, (za, zb) in enumerate([(2, H5_ZS[0]), (H5_ZS[0], H5_ZS[1]), (H5_ZS[1], H5_C[-1][1])]):
    h.rect(f"plate{zi + 1}", PX0, PX1, za, zb, 0.0, zone=f"s{zi + 1}", kind="plate")
GZ = H5_C[-1][1]   # green starts where the channel ends
h.rect("green", -7, 6, GZ, GZ - 12, 0.0, zone="green")
h.wall_path([(PX0, 2), (PX0, GZ), (-7, GZ), (-7, GZ - 12), (6, GZ - 12), (6, GZ), (PX1, GZ), (PX1, 2)], 0.0, out="L", closed=True, name="rock",
            top=H5_BR + 1.0)
L = offset_polyline(H5_C, -H5_HW)
R = offset_polyline(H5_C, H5_HW)
h.d["plate_visible"] = [[(r4(x), r4(z)) for x, z in L + list(reversed(R))]]   # render/builder info: the felt part of the plates
h.wall_path(L, 0.0, out="L", ext=(0.0, 0.0), top=H5_BR + 1.0, name="pipe_rail")
h.wall_path(list(reversed(R)), 0.0, out="L", ext=(0.0, 0.0), top=H5_BR + 1.0, name="pipe_rail")
# close the plate between the channel mouth and the green: rails along the green's south edge outside the channel opening
h.wall_free((R[-1][0], GZ + 0.25), (6.0, GZ + 0.25), 0.0, name="green_s_rail_e")
h.wall_free((-7.0, GZ + 0.25), (L[-1][0], GZ + 0.25), 0.0, name="green_s_rail_w")
LB = offset_polyline(H5_C, -(H5_HW - H5_BW))
RB = offset_polyline(H5_C, H5_HW - H5_BW)
nseg = len(H5_C) - 1


def h5_turn_side(j):
    """side ('R' or 'L', map view) toward which the centreline turns at vertex j"""
    ax_, az_ = H5_C[j][0] - H5_C[j - 1][0], H5_C[j][1] - H5_C[j - 1][1]
    bx_, bz_ = H5_C[j + 1][0] - H5_C[j][0], H5_C[j + 1][1] - H5_C[j][1]
    return "R" if (bx_ * (-az_) + bz_ * ax_) > 0 else "L"


for i in range(nseg):
    a, b = H5_C[i], H5_C[i + 1]
    dx, dz = b[0] - a[0], b[1] - a[1]
    Ls = math.hypot(dx, dz)
    ux, uz = dx / Ls, dz / Ls
    for side, out in (("L", "L"), ("R", "R")):
        # at a bend the bank on the OUTSIDE of the turn runs on to the rail mitre (+hw tan(t/2)); the bank on the INSIDE stops at
        # its low-edge mitre (-(hw - bw) tan(t/2)) so it never pokes into the next segment's channel
        ee = []
        for j in (i, i + 1):
            if j == 0 or j == nseg:
                ee.append(0.0)
                continue
            t = math.tan(math.radians(turn_deg(H5_C, j) / 2))
            ee.append(-(H5_HW - H5_BW) * t if h5_turn_side(j) == side else H5_HW * t)
        e0, e1 = ee
        nx, nz = (-uz, ux) if side == "R" else (uz, -ux)
        off = H5_HW - H5_BW
        A = (a[0] + nx * off - ux * e0, a[1] + nz * off - uz * e0)
        B = (b[0] + nx * off + ux * e1, b[1] + nz * off + uz * e1)
        h.bank(f"bank_{side}{i + 1}", A, B, H5_BW, H5_BR, out, zone=["s1", "s2", "s2", "s3", "s3"][min(i, 4)], ext=0.0)
h.tee(0, 0, 0)
h.cup(*H5_CUP, flag_h=7.5)
h.d["cup_from"] = ["green", "s3"]
h.wp("all", "bend1", [K("h5_wp1", [2.0, -13.0])[0], 0.0, K("h5_wp1", [2.0, -13.0])[1]], ["s1"], carry=K("h5_carry1", 16.0))
h.wp("all", "bend2", [K("h5_wp2", [3.5, -29.0])[0], 0.0, K("h5_wp2", [3.5, -29.0])[1]], ["s2"], carry=K("h5_carry2", 8.0))
h.wp("all", "mouth", [H5_C[-1][0], 0.0, GZ + 1.5], ["s3"], carry=3.0)
h.anchor("echo_walls", [3, 0, -22], "Wave-carved slot walls: smooth curving pink/cream sandstone hugging the half-pipe outside the rails, "
         "rising 44 studs; the sky is a pink ribbon overhead. They hide the flag from the tee by design (see the crystal cue)", landmark=True,
         size=[16, 44, 46], occluders=[((3.5, 6, -24), (6, 12, 8))])
h.anchor("pipe_lip", [3, H5_BR, -22], f"Rounded sandstone lip on top of both half-pipe rails following the S (felt banks {H5_BW:g} wide rise {H5_BR:g})",
         size=[1, 0.4, 46])
h.anchor("crystal_cue", [H5_CUP[0], 9.5, H5_CUP[2]], "Glowing pink rock-candy crystal hanging 9.5 studs over the cup from a rope "
         "between the slot walls: the visual cue for the hidden flag (decoration only, no collision, 8+ studs above the felt)", size=[1.2, 2, 1.2])
holes.append(h)

# ================================================================ H6 Flash Flood (par 3): sliding sluice gate with dwell
H6_CUP = K("h6_cup", [-4.0, 0.0, -45.0])
H6_GATE_LEN = K("h6_gate_len", 7.0)
H6_GATE_SPEED = K("h6_gate_speed", 3.0)
H6_DW = K("h6_dwell", (1.2, 2.0))     # pause (s) closed (offset 0, across the neck) / open (offset -7, in the west pocket)
H6_TRAVEL = K("h6_travel", 7.0)
h = new_hole(6, "h06", "Flash Flood", 3, "Old timber sluice gate and a flood-warning bell tower",
             "Timing gate: a sluice gate slides across the slot neck, pauses closed, then opens (slide with dwell); the overflow channel is the safe way round")
h.rect("lane", -4, 4, 2, -18, 0.0, zone="lane")
h.rect("basin", -11, 11, -18, -26, 0.0, zone="basin")
h.rect("neck", -3, 3, -26, -30, 0.0, zone="neck")
h.rect("spill", -3, 3, -30, -34, 0.0, zone="neck")
h.rect("overflow", 8, 11, -26, -47, 0.0, zone="overflow")
h.rect("crossover", 6, 11, -47, -50, 0.0, zone="overflow")
h.rect("green", -11, 6, -34, -50, 0.0, zone="green")
h.wall_path([(-4, 2), (-4, -18), (-11, -18), (-11, -26), (-3, -26), (-3, -34), (-11, -34), (-11, -50), (11, -50), (11, -18), (4, -18), (4, 2)],
            0.0, out="L", closed=True, top=2.4)
h.wall_path([(3, -26), (8, -26), (8, -47), (6, -47), (6, -34), (3, -34)], 0.0, out="L", closed=True, name="rock", top=2.4)
cs = 0.6 / math.sqrt(2)
gate_bl = [dict(center=[0, 0.5, 0], size=[H6_GATE_LEN - 0.6, 1.0, 0.636], yaw=0.0)] + \
          [dict(center=[sx * (H6_GATE_LEN / 2 - 0.3), 0.5, 0], size=[r4(cs), 1.0, r4(cs)], yaw=45.0) for sx in (-1, 1)]
h.slider("sluice_gate", [0, 0.0, -28.0], [1, 0, 0], H6_GATE_SPEED, [-H6_TRAVEL, 0.0], gate_bl, phase=0.0,
         dwell=[(0.0, H6_DW[0]), (-H6_TRAVEL, H6_DW[1])],
         visual=f"Timber sluice gate board {H6_GATE_LEN:g} long, 0.6 thick, 1.0 tall (pointed 45-degree ends) on a hidden rail across the neck; "
                f"closed = centred on the neck (offset 0), open = slid {H6_TRAVEL:g} west into a pocket in the slot wall")
collision_cut(h, ["rail5", "rock18"], [-10.68, -0.15, -28.47], [3.68, 1.17, -27.53], "sluice_gate")
# Enclose the slide pocket: these return walls sit outside the full board sweep.
h.rect("gate_pocket_floor", -10.68, 3.68, -27.53, -28.47, -.15, zone="neck", edge_support=True)
h.wall_path([(-3, -27.53), (-10.68, -27.53), (-10.68, -28.47), (-3, -28.47)], -.15, out="L", top=2.55, name="pocket_w")
h.wall_path([(3, -28.47), (3.68, -28.47), (3.68, -27.53), (3, -27.53)], -.15, out="L", top=2.55, name="pocket_e")
h.tee(0, 0, 0)
h.cup(*H6_CUP, flag_h=7.5)
h.d["cup_from"] = ["green", "neck", "overflow"]
h.wp("all", "neck", [0.0, 0.0, -31.0], ["lane", "basin"], carry=K("h6_neck_carry", 6.0))
h.wp("average", "neck", [0.0, 0.0, -31.0], ["lane"], carry=K("h6_neck_carry", 6.0))
h.wp("average", "overflow_in", [9.5, 0.0, -24.0], ["basin"], carry=0.0)
h.wp("average", "overflow_far", [9.5, 0.0, -40.0], ["basin"], carry=K("h6_of_carry", 6.0))
h.wp("average", "overflow_top", [9.0, 0.0, -48.6], ["overflow"], carry=K("h6_of_carry2", 1.0))
h.anchor("sluice_gate", [0, 0, -28], "Timber sluice gate with peppermint-striped bands and a big hand-wheel winch on the west wall (moving mesh, "
         "pivot = gate centre at offset 0)", size=[H6_GATE_LEN, 1.2, 0.6])
h.anchor("bell_tower", [-9, 0, -30], "Little timber flood-warning bell tower on the rock between basin and green (rings when the gate closes)",
         landmark=True, size=[3, 9, 3], occluders=[((-9, 4.5, -30), (3, 9, 3))])
h.anchor("gate_frame", [0, 0, -28], "Timber frame: west post x=-12, east post x=4.65 (2026-10-13: moved out of rock wall pocket_e23 to 0.15 clear on its far side, away from the gate), beam 8 above felt; mesh pivot stays [0,0,-28]", size=[24.6, 9, 1],
         occluders=[((-12, 4.5, -28), (0.6, 9, 0.6)), ((4.65, 4.5, -28), (0.6, 9, 0.6))])
sign(h, "sign_overflow", (11.6, 0, -21), "Painted arrow 'Overflow - the long way round' pointing into the overflow channel", (-0.3, -1))
felt_arrow(h, "felt_arrow_overflow", [9.5, 0.0, -23.5], "Glowing felt arrow decal pointing -Z into the overflow channel")
h.anchor("flood_marks", [-11.5, 0, -22], "High-water marks and a 'Flash Flood Zone' enamel sign on the basin wall", size=[0.3, 4, 3])
holes.append(h)

# ================================================================ H7 Rope Bridge Run (par 4)
H7_CUP = K("h7_cup", [3.0, 0.0, -60.0])
H7_B1 = K("h7_b1", (-2.0, 2.0))
H7_B2 = K("h7_b2", (1.8, 5.8))
H7_IS = K("h7_island", (-9.0, 9.0, -37.0, -45.0))   # x0, x1, z0, z1
h = new_hole(7, "h07", "Rope Bridge Run", 4, "Taffy Gap with two sagging rope bridges and a hoodoo island between",
             "Rope-bridge spans: two railed rope bridges over Taffy Gap with an island between whose ends are open to the gap; a fall respawns at the island")
xi0, xi1, zi0, zi1 = H7_IS
h.rect("lane", -5, 5, 2, -26, 0.0, zone="lane")
h.rect("bridge1", H7_B1[0], H7_B1[1], -26, zi0, 0.0, zone="bridge1", kind="bridge")
h.rect("island", xi0, xi1, zi0, zi1, 0.0, zone="island")
h.rect("bridge2", H7_B2[0], H7_B2[1], zi1, -58, 0.0, zone="bridge2", kind="bridge")
h.rect("green", -6, 10, -58, -71, 0.0, zone="green")
h.hazard("taffy_gap", "pit", -15, 15, -26, -58, -30.0, respawn=K("h7_respawn", [0.0, 0.0, zi0 - 1.5]))
h.wall_path([(H7_B1[1], -26), (5, -26), (5, 2), (-5, 2), (-5, -26), (H7_B1[0], -26)], 0.0, out="L", ext=(0.0, 0.0))
h.wall_path([(H7_B1[0], -26), (H7_B1[0], zi0)], 0.0, out="L", ext=(0.0, 0.0), name="rope_rail", top=3.5)
h.wall_path([(H7_B1[1], zi0), (H7_B1[1], -26)], 0.0, out="L", ext=(0.0, 0.0), name="rope_rail", top=3.5)
# island: rope rail along its north edge except the bridge-2 mouth; ends (and, unless H7_SRAIL, the south edge) open to the gap
H7_SRAIL = K("h7_south_rail", True)
if H7_SRAIL:
    h.wall_path([(H7_B1[0], zi0), (xi0, zi0)], 0.0, out="L", ext=(0.0, 0.0), name="island_s_rail")
    h.wall_path([(xi1, zi0), (H7_B1[1], zi0)], 0.0, out="L", ext=(0.0, 0.0), name="island_s_rail")
h.wall_path([(xi0, zi1), (H7_B2[0], zi1)], 0.0, out="L", ext=(0.0, 0.0), name="island_rail")
h.wall_path([(H7_B2[1], zi1), (xi1, zi1)], 0.0, out="L", ext=(0.0, 0.0), name="island_rail")
h.wall_path([(H7_B2[0], zi1), (H7_B2[0], -58)], 0.0, out="L", ext=(0.0, 0.0), name="rope_rail", top=3.5)
h.wall_path([(H7_B2[1], -58), (H7_B2[1], zi1)], 0.0, out="L", ext=(0.0, 0.0), name="rope_rail", top=3.5)
h.wall_path([(H7_B2[0], -58), (-6, -58), (-6, -71), (10, -71), (10, -58), (H7_B2[1], -58)], 0.0, out="L", ext=(0.0, 0.0))
h.tee(0, 0, 0)
h.cup(*H7_CUP, flag_h=7.5)
h.d["cup_from"] = ["green", "bridge2"]
h.wp("all", "island", [K("h7_isl_x", 1.0), 0.0, (zi0 + zi1) / 2], ["lane", "bridge1"], carry=K("h7_isl_carry", 0.0))
h.wp("all", "b2_far", [(H7_B2[0] + H7_B2[1]) / 2, 0.0, -59.5], ["island", "bridge2"], carry=K("h7_b2_carry", 3.0))
h.anchor("rope_bridges", [0, 0, -42], "Two flat-felt bridges with solid 3.5-stud sandstone parapets, rope trim, opaque side skirts and optional endpoint player teleports",
         landmark=True, size=[8, 4, 32])
h.anchor("island_hoodoo", [-6.5, 0, -41], "Striped hoodoo with a gumdrop cap on the island's west end (outside the play line; decoration only)",
         size=[3, 12, 3], occluders=[((-6.5, 6, -41), (2.4, 12, 2.4))])
h.anchor("island_respawn_stone", [0, 0, zi0 - 1.5], "Glowing marker stone flush in the island felt at the bridge-1 landing: where a ball that "
         "falls into the gap reappears", size=[0.8, 0.02, 0.8])
h.anchor("gap_view", [0, -4.25, -42], "Opaque sandstone comfort floor and mist hide the 30-stud gap; the original pit respawn remains authoritative for balls", size=[30, 0.5, 32])
h.anchor("island_edge_lip", [0, 0, zi0], "Low crumbly sandstone lip (0.2, visual only) along the open island edges so they read as edges", size=[18, 0.2, 0.4])
# VR comfort geometry uses local [x,y,z] centres/sizes, just like the hole.
# Parapet inner faces are the existing rail faces: only their tops are raised.
h.d["vr_comfort"] = dict(
    boxes=[dict(id=w["id"], center=w["center"][:], size=w["size"][:], yaw=w["yaw"],
                role="solid_parapet", solid=True, collidable=True, collision_source="walls")
           for w in h.d["walls"] if w["id"].startswith("rope_rail")],
    note="Opaque side skirts meet solid parapets at deck height. Player teleport points never transport the ball. "
         "The shallow visual floor/mist hide the deep chasm; ball hazard/respawn semantics remain unchanged.")
for bridge_id, limits, z_start, z_end in (("bridge1", H7_B1, -26, zi0), ("bridge2", H7_B2, zi1, -58)):
    for side, x in (("west", limits[0] - 0.25), ("east", limits[1] + 0.25)):
        box = dict(id=f"{bridge_id}_skirt_{side}", center=[x, -2.0, (z_start + z_end)/2],
                   size=[0.5, 4.0, abs(z_end-z_start)], yaw=0, role="solid_side_skirt",
                   solid=True, collidable=False, ball_collision=False)
        h.d["vr_comfort"]["boxes"].append(box)
        h.anchor(box["id"], box["center"], "Opaque sandstone side skirt, exactly outside bridge felt, extends down to comfort floor",
                 size=box["size"], exact_box=box)
comfort_floor = dict(id="gap_comfort_floor", center=[0, -4.25, -42], size=[30, 0.5, 32], yaw=0,
                     role="opaque_gap_floor", solid=True, collidable=False, ball_collision=False,
                     note="Visual top y=-4. Original taffy_gap ball hazard at -30 and island respawn are unchanged.")
h.d["vr_comfort"]["boxes"].append(comfort_floor)
h.d["vr_comfort"]["mist"] = dict(id="gap_mist", center=[0, -3.5, -42], size=[30, 1, 32],
                                      yaw=0, collidable=False, ball_collision=False)
h.d["player_teleport_points"] = []
# p9: bridge1_island moved off the island respawn stone [0,0,zi0-1.5] (was [0,0,zi0-1], .5 away) to the clear felt just east of the
# bridge-1 landing; bridge2_exit moved east (was x 3.8, its 3-wide footprint covered the cup at x 3) so its west edge clears the cup rim by .15.
H7_TP_B1_ISLAND = K("h7_tp_b1_island", [4.5, -38.5])
H7_TP_B2_EXIT_X = K("h7_tp_b2_exit_x", round(H7_CUP[0] + 0.5 + 0.15 + 1.5, 3))
for tid, x, z, support, note in (
        ("bridge1_entry", sum(H7_B1)/2, -25, "lane", "one stud back from the bridge-1 end"),
        ("bridge1_island", H7_TP_B1_ISLAND[0], H7_TP_B1_ISLAND[1], "island",
         "on island felt just east of the bridge-1 landing, clear of the respawn stone (p9: moved from [0,0,-38])"),
        ("bridge2_island", sum(H7_B2)/2, zi1+1, "island", "one stud back from the bridge-2 end"),
        ("bridge2_exit", H7_TP_B2_EXIT_X, -59, "green",
         "on green felt at the bridge-2 exit, east of the cup (west edge .15 outside the cup rim; p9: moved from x 3.8)")):
    tp = dict(id=tid, position=[x, 0, z], size=[3, 0.02, 2], yaw=0, support_felt=support,
              player_only=True, ball_teleport=False, optional=True,
              note=f"Flush player teleport marker on solid felt, {note}; paired crossing is optional.")
    h.d["player_teleport_points"].append(tp)
    h.anchor("player_tp_" + tid, tp["position"], tp["note"], size=tp["size"], player_only=True,
             teleport_point=tid)
holes.append(h)

# ================================================================ H8 Gumdrop Gulch (par 3): rolling dips
H8_DH = K("h8_dip_hi", 0.12)  # 2026-10-12 (game stop rule 0.015): was 0.3, before that 0.5; 2026-10-12 rest-timing fix
H8_DL = K("h8_dip_lo", 0.0)  # was -0.3: hollows are now level floors at lane height, no opposing-slope trough
H8_SEG = K("h8_seg", 0.3)  # 2026-10-12: short steep ramps (slope 0.4), was 2.3125; before that 3.8125 (4.0 before); 8 ramps + 3 x 4.5 floors keep the 32-stud dip run (ZD = -40)
H8_HUMPS = K("h8_humps", 4)
H8_CUP = K("h8_cup", [5.0, 0.0, -55.0])
h = new_hole(8, "h08", "Gumdrop Gulch", 3, "Giant gumdrop boulders in candy colours",
             "Rolling humps: four gumdrop humps (planar ramps) with level hollow floors between them; pace the ball through")
h.rect("lane", -4, 4, 2, -8, 0.0, zone="lane")
prof = [0.0] + [H8_DH, H8_DL] * (H8_HUMPS - 1) + [H8_DH, 0.0]
H8_FLAT = K("h8_flat", (32.0 - 8 * H8_SEG) / 3)  # 2026-10-12 late: 9.8667 (8x0.3 ramps + 3 floors = 32 run); then 4.5 (was 0.5; Studio tail p90 5.17 s). Earlier: flat crease floor (studs along z) at the bottom of each hollow; was 0 (sharp V, ball rocked ~3 s before counting as stopped)
z = -8.0
yz = [(z, prof[0])]
for i in range(len(prof) - 1):
    h.rect(f"dip{i + 1}", -4, 4, z, z - H8_SEG, zone="dips", slope=("z", prof[i], prof[i + 1]))
    z -= H8_SEG
    yz.append((z, prof[i + 1]))
    if H8_FLAT > 0 and 0 < i + 1 < len(prof) - 1 and prof[i + 1] == H8_DL:
        h.rect(f"crease{(i + 1) // 2}", -4, 4, z, z - H8_FLAT, prof[i + 1], zone="dips")
        z -= H8_FLAT
        yz.append((z, prof[i + 1]))
ZD = z
h.rect("run", -4, 4, ZD, ZD - 4, 0.0, zone="run")
h.rect("green", -9, 9, ZD - 4, ZD - 18, 0.0, zone="green")
pts = [(-4, 2)] + [(-4, zz) for zz, _ in yz] + \
      [(-4, ZD - 4), (-9, ZD - 4), (-9, ZD - 18), (9, ZD - 18), (9, ZD - 4), (4, ZD - 4)] + \
      [(4, zz) for zz, _ in yz][::-1] + [(4, 2)]
yl = [0.0] + [yy for _, yy in yz] + [0.0] * 6 + [yy for _, yy in yz][::-1] + [0.0]
h.wall_path(pts, yl, out="L", closed=True)
for i, (gx, gz) in enumerate(K("h8_gumdrops", [(1.5, ZD - 11.0), (-3.5, ZD - 14.0)]), 1):
    h.block(f"gumdrop{i}", gx, gz, 1.8, 1.8, 0.0, height=1.5, yaw=22.5)
h.tee(0, 0, 0)
h.cup(*H8_CUP, flag_h=7.5)
h.wp("all", "run", [0.0, 0.0, ZD - 2.0], ["lane", "dips"], carry=K("h8_carry", 4.0))
h.anchor("gumdrops", [0, 0, ZD - 10], "Giant sugar-dusted gumdrops (cherry, lemon, lime) dressing the two gumdrop bumpers on the green "
         "(1.8 x 1.8 octagon-ish bases turned 22.5 deg)", landmark=True, size=[2.4, 2.4, 2.4])
h.anchor("dip_trim", [0, 0, (ZD - 8) / 2], f"Taffy-striped rail trim following the {H8_HUMPS} humps (felt humps rise to +{H8_DH:g}; hollow floors at "
         f"{H8_DL:g})", size=[9, 0.4, -8 - ZD])
h.anchor("big_gumdrop_bg", [11, 0, -18], "Car-sized gumdrop boulders outside the east rail", size=[6, 5, 6], occluders=[((11, 2.5, -18), (5, 5, 5))])
holes.append(h)

# ================================================================ H9 Lollipop Windmill (par 3): vertical rotor
H9_CUP = K("h9_cup", [-1.5, 0.0, -42.0])
H9_VANES = K("h9_vanes", 4)
H9_SPEED = K("h9_speed", 20.0)
H9_VW = K("h9_vane_w", 2.4)
H9_R = (0.6, K("h9_r_out", 4.1))
H9_CLEAR = K("h9_clear", 0.15)          # p9: tip clearance over the felt at every phase (was .02)
# p9b: the hub stays at the p8 height; the collision strips are shortened instead (visual mesh keeps radius H9_R[1]).
H9_PY = K("h9_py", 4.12)
H9_RC = round(K("h9_r_coll", H9_PY - H9_CLEAR), 4)   # collision outer radius: tip clearance = H9_PY - H9_RC
H9_CC = K("h9_centre_clear", 0.06)     # p9b: centre strips hang low enough to block; tip strips keep 0.15
H9_CHW = K("h9_centre_hw", 1.2)        # p9b: full vane width at centre_clear (outer tip strips at 0.15 cannot block a 0.16-tall ball)
h = new_hole(9, "h09", "Lollipop Windmill", 3, "Prospector's windpump with lollipop vanes and a water tank",
             "Vertical rotor: a windpump's lollipop vanes turn across the tunnel mouth; the bypass round the pump house is the safe way")
h.rect("lane", -4, 4, 2, -10, 0.0, zone="lane")
h.rect("approach", -4, 11, -10, -18, 0.0, zone="approach")
h.rect("pump_tunnel", -1.2, 1.2, -18, -24, 0.0, zone="tunnel", tunnel=True, kind="tunnel")
h.rect("spill", -2.5, 2.5, -24, -34, 0.0, zone="spill")
h.rect("bypass", 8, 11, -18, -34, 0.0, zone="bypass")
h.rect("green", -9, 11, -34, -48, 0.0, zone="green")
h.wall_path([(-4, 2), (-4, -18), (-1.2, -18), (-1.2, -24), (-2.5, -24), (-2.5, -34), (-9, -34), (-9, -48), (11, -48), (11, -10), (4, -10), (4, 2)],
            0.0, out="L", closed=True)
h.wall_path([(1.2, -18), (8, -18), (8, -34), (2.5, -34), (2.5, -24), (1.2, -24)], 0.0, out="L", closed=True, name="house")
# Clip the wide vane tip to a circular envelope; widening a square tip raises the
# axle and actually reduces contact with the ball at the middle of each vane.
vanes = []
for k in range(H9_VANES):
    for j in range(K("h9_tip_strips", 12)):
        strips = K("h9_tip_strips", 12)
        x0 = -H9_VW / 2 + j * H9_VW / strips
        x1 = x0 + H9_VW / strips
        rc = H9_PY - H9_CC if H9_CC is not None and max(abs(x0), abs(x1)) <= H9_CHW + 1e-9 else H9_RC
        rout = math.sqrt(rc ** 2 - max(abs(x0), abs(x1)) ** 2) if K("h9_round_tip", True) else rc
        vanes.append(dict(center=[(x0+x1)/2, -(H9_R[0]+rout)/2, 0],
                          size=[H9_VW/strips, rout-H9_R[0], K("h9_depth", 0.4)], yaw=0.0, roll=360*k/H9_VANES))
h.rotor("windpump", [0, H9_PY, -17.75], [0, 0, 1], H9_SPEED, vanes,
        visual=f"{H9_VANES} lollipop vanes, width {H9_VW}, visual radius {H9_R[0]:g}..{H9_R[1]:g}; collision strips radius {H9_R[0]:g}..{H9_PY - H9_CC:g}, "
               f"circular clipped tips built from {strips} strips; axle y={H9_PY}; collision tip clearance {H9_CC:g} (p9b: 0.15 tip clearance "
               f"cannot block a 0.16-tall ball; 0.06 is the highest clearance that stays in the 35-50% stop band). Visual tip may extend "
               f"to r {H9_R[1]:g} ({H9_PY - H9_R[1]:.3f} above the felt) past the collider")
h.tee(0, 0, 0)
h.cup(*H9_CUP, flag_h=7.5)
h.d["cup_from"] = ["green", "spill"]
h.wp("all", "tunnel_far", [0.0, 0.0, -25.0], ["lane", "approach"], carry=K("h9_tun_carry", 5.0))
h.wp("good", "tunnel_far", [0.0, 0.0, -25.0], ["lane", "approach"], carry=K("h9_tun_carry", 5.0))
h.wp("average", "bypass_in", [9.5, 0.0, -16.0], ["lane"], carry=0.0)
h.wp("average", "bypass_top", [9.5, 0.0, -35.5], ["approach", "bypass"], carry=K("h9_bp_carry", 4.0))
h.anchor("pump_house", [-3, 0, -21], "Timber pump house (the rock 'house' block x 1.2..8 plus a matching west half) with the windpump tower on "
         "its roof; the tunnel through it is 2.4 wide, 6 long", landmark=True, size=[16, 8, 6],
         occluders=[((-3.6, 4, -21), (4.8, 8, 6)), ((4.6, 4, -21), (6.8, 8, 6))])
h.anchor("windpump_wheel", [0, H9_PY, -17.75], f"Windpump wheel mesh (moving part, pivot = hub, axis +Z): {H9_VANES} swirl-lollipop vanes "
         f"radius {H9_R[1]:g}", size=[2 * H9_R[1], 2 * H9_R[1], 0.4])
h.anchor("water_tank", [-7, 0, -40], "Striped water tank on stilts beside the green", size=[4, 8, 4])
sign(h, "sign_bypass", (11.6, 0, -13), "Arrow sign 'Round the back - no vanes' pointing into the bypass", (-0.3, -1))
felt_arrow(h, "felt_arrow_bypass", [9.5, 0.0, -20.0], "Glowing felt arrow decal pointing -Z into the bypass")
holes.append(h)

# ================================================================ H10 Sluice Chute (par 2): one-way chute
H10_CUP = K("h10_cup", [7.0, -3.6, -33.5])
H10_CH = K("h10_chute", (-14.0, -30.0))     # chute z range
H10_DROP = 3.6
H10_BACK = K("h10_back_rise", 0.8)
h = new_hole(10, "h10", "Sluice Chute", 2, "Timber sluice flume with peppermint-striped gates",
             "One-way slope: a steep sluice chute drops 3.6 studs into a basin green; felt arrows and chevrons show it is one-way")
h.rect("deck", -3.5, 3.5, 2, H10_CH[0], 0.0, zone="deck")
h.rect("chute", -1.5, 1.5, H10_CH[0], H10_CH[1], zone="chute", slope=("z", 0.0, -H10_DROP))
h.rect("basin", -9, 9, H10_CH[1], -37, -H10_DROP, zone="basin")
h.rect("basin_back", -9, 9, -37, -43, zone="basin", slope=("z", -H10_DROP, -H10_DROP + H10_BACK))
y0, y1, y2 = 0.0, -H10_DROP, -H10_DROP + H10_BACK
h.wall_path([(-3.5, 2), (-3.5, H10_CH[0]), (-1.5, H10_CH[0]), (-1.5, H10_CH[1]), (-9, H10_CH[1]), (-9, -37), (-9, -43), (9, -43), (9, -37),
             (9, H10_CH[1]), (1.5, H10_CH[1]), (1.5, H10_CH[0]), (3.5, H10_CH[0]), (3.5, 2)],
            [y0, y0, y0, y1, y1, y1, y2, y2, y1, y1, y1, y0, y0, y0], out="L", closed=True)
h.tee(0, 0, 0)
h.cup(*H10_CUP, flag_h=7.5)
h.d["cup_from"] = ["basin"]
h.wp("all", "chute_mouth", [0.0, 0.0, H10_CH[0] - 1.0], ["deck"], carry=K("h10_carry", 1.0))
for k, zz in enumerate(range(int(H10_CH[0]) - 2, int(H10_CH[1]) + 1, -4)):
    yy = round(-H10_DROP * (H10_CH[0] - zz) / (H10_CH[0] - H10_CH[1]), 3)
    felt_arrow(h, f"chevron_{k + 1}", [0.0, yy, float(zz)], "Glowing felt chevron decal on the chute pointing -Z (one-way: the ball won't come back up)",
               size=(2.4, 0.01, 1.2))
felt_arrow(h, "felt_arrow_deck", [0.0, 0.0, -10.0], "Big glowing 'ONE WAY' felt arrow on the deck pointing into the chute", size=(2.4, 0.01, 3.0))
h.anchor("sluice_flume", [0, -1.8, (H10_CH[0] + H10_CH[1]) / 2], "Timber sluice flume casing over the chute (open top), peppermint-striped "
         "gate frames at the top and bottom, a thin sheet of turquoise water running beside the felt (visual only)", landmark=True,
         size=[5, 4, 16])
h.anchor("basin_bank", [0, -3.6, -40], "Spillway-basin back wall of peppermint concrete behind the uphill back slope", size=[19, 3, 1])
h.anchor("dam_view", [0, 0, -60], "The Peppermint Dam and reservoir beyond the basin (world dressing)", size=[80, 100, 10])
holes.append(h)

# ================================================================ H11 Floodgate Lock (par 3): lock elevator (gate + lift)
H11_CUP = K("h11_cup", [0.0, 4.0, -43.0])
H11_DW = K("h11_dwell", (5.5, 4.6))       # gate open (down) / closed (up) pause, s
H11_GS = K("h11_gate_speed", 1.3 / .3)
H11_TRAVEL = 1.0
H11_TOP_DWELL = 2.0
H11_MARGIN = .3
H11_SLOPE = K("h11_side_rise", 0.0)       # upper green: height rise toward +x (east) (0 = flat)
H11_EXIT = K("h11_exit", (1.5, 7.0, 0.5))  # lift exit speed clamp min, max, factor
h = new_hole(11, "h11", "Floodgate Lock", 3, "Canal lock with brass winches and a lock-keeper's hut",
             "Ball elevator: a canal-lock platform lifts the ball 4 studs and comes back down; roll in while the lock gate is down")
# P8 option 3: wider return lane and longer broad approach for easy re-putts.
h.rect("lane", -5.5, 5.5, 2, -6, 0.0, zone="lane")
h.rect("approach", -6, 6, -6, -21, 0.0, zone="approach")

# P8: .4-wide lip-end waiting pockets prevent opposing rail/lip contacts.
h.rect("quay", -2.2, 2.2, -25, -30, 4.0, zone="quay")
h.rect("green", -11, 11, -30, -52, zone="green", slope=("x", 4.0 - H11_SLOPE / 2, 4.0 + H11_SLOPE / 2) if H11_SLOPE else None, y=4.0)
h.wall_path([(-5.5, 2), (-5.5, -6), (-6, -6), (-6, -21), (-1.6, -21), (-1.6, -25), (1.6, -25), (1.6, -21), (6, -21), (6, -6), (5.5, -6), (5.5, 2)],
            0.0, out="L", closed=True, top=2.4)
yw, ye = 4.0 - H11_SLOPE / 2, 4.0 + H11_SLOPE / 2
h.wall_path([(-2.2, -25), (-2.2, -30), (-11, -30), (-11, -52), (11, -52), (11, -30), (2.2, -30), (2.2, -25)],
            [4.0, 4.0, yw, yw, ye, ye, 4.0, 4.0], out="L", closed=True, name="quay_rail")
h.bank_wall("funnel_w", (-6.0, -17.0), (-2.3, -20.7), "L", zone="approach", ext_bank=0.0)
h.bank_wall("funnel_e", (2.3, -20.7), (6.0, -17.0), "L", zone="approach", ext_bank=0.0)
# Chamber side walls contain a ball at every deck elevation, not only the bottom.
for wall in h.d["walls"]:
    if wall["id"] in ("rail5", "rail7"):
        wall["center"][1]=2.05;wall["size"][1]=5.1  # bottom -.5, top 4.6
H11_OPEN = -1.3
h.slider("lock_gate", [0, 0.0, -21.25], [0, 1, 0], H11_GS, [H11_OPEN, 0.0],
         [dict(center=[0, 0.6, 0], size=[3.6, 1.2, 0.5], yaw=0.0)], phase=H11_OPEN,
         dwell=[(H11_OPEN, H11_DW[0]), (0.0, H11_DW[1])],
         visual="Mitre-style lock gate (one leaf, 3.6 wide, 1.2 tall, 0.5 thick) that sinks into a slot in the felt to open (offset -1.3: top 0.1 "
                "below the felt) and rises to close (offset 0). It is down while the platform waits at the bottom and up while the platform rides")
h.d["moving_parts"][-1]["felt"] = [dict(id="gate_top", zone="lock", center=[0,1.2,-21.25], size=[3.6,.5], yaw=0, slope=None, thickness=1.2, edge_support=True)]
h.d["removed_static_felt"] = ["lock"]
h.d["moving_floor_slot"] = dict(owner="lock_lift_deck", min=[-1.6,-.15,-21.65], max=[1.6,0,-21],
    explanation="Remove this south strip from the nominal 3.2 x 4 deck; remaining moving felt and collision is 3.2 x 3.35. No static felt_lock.")
# Approved model apertures expanded to 0.15 minimum clearance.
collision_cut(h, ["rail4", "rail5", "rail7", "rail8", "approach"], [-1.95, -1.45, -21.65], [1.95, 1.35, -20.85], "lock_gate")
collision_cut(h, ["rail4", "rail5", "rail6", "rail7", "rail8", "quay_rail20", "quay", "approach"], [-1.75, -.30, -25.15], [1.75, 4.43, -20.85], "lock_lift_deck")
# Clear the complete quay rail height; the synchronized moving lip closes this aperture.
collision_cut(h, ["quay_rail20"], [-1.95, 3.35, -25.15], [1.95, 5.15, -24.35], "quay_lip")
# Raised lip sits north of deck sweep, with a matching slot through the quay felt.
collision_cut(h, ["quay", "rail4", "rail5", "rail6", "rail7", "rail8"], [-1.95, 2.35, -25.70], [1.95, 5.15, -25.20], "quay_lip")
lock_period = S.cycle_period(h.d["moving_parts"][-1])
h11_rise = round(H11_DW[0] + abs(H11_OPEN) / H11_GS + H11_MARGIN, 6)
h11_top = round(h11_rise + H11_TRAVEL, 6)
h11_down = round(h11_top + H11_TOP_DWELL, 6)
h11_bottom = round(h11_down + H11_TRAVEL, 6)
h11_flush = [round(h11_top - .1, 6), round(h11_down + .1, 6)]
assert lock_period - abs(H11_OPEN) / H11_GS - h11_bottom >= H11_MARGIN - 1e-8
# Keep the shoulder waiting pocket wide enough that a ball cannot be pinched by the closing lip.
collision_cut(h, ["rail5", "rail7"], [-1.95,2.35,-25.20], [1.95,5.15,-25.0], "quay_lip")
# A square slot's diagonal corner gap exceeds the ball diameter even when each
# axis gap is .15. Box-only 45-degree felt patches maintain .15 Euclidean clearance.
for slot, y, zs in (("gate",0.0,[-21.0]), ("lip",4.0,[-25.55,-25.35])):
    for zc in zs:
        sz=1 if slot=="gate" or zc>-25.45 else -1
        for sx in (-1,1):
            h.d["felt"].append(dict(id=f"{slot}_corner_{sx}_{zc}",zone="approach" if slot=="gate" else "quay",
                center=[r4(sx*(1.8+.225/math.sqrt(2))),y,r4(zc+sz*.225/math.sqrt(2))],
                size=[.15,.4],yaw=-math.degrees(math.atan2(sz,sx)),slope=None,thickness=.4,edge_support=True))
# Keep incoming balls out of the narrow gate-side service clearance.
for sx in (-1,1):
    h.d["walls"].append(dict(id="gate_approach_guide_"+str(sx),center=[sx*1.85,.5,-20.70],size=[.2,1,.3],yaw=0))
# Fixed quay shoulder curbs stop a ball outside the narrower deck from falling off at lip ends.
for sx in (-1,1):
    h.d["walls"].append(dict(id="quay_shoulder_"+str(sx),center=[sx*1.85,4.5,-24.95],size=[.2,1,.2],yaw=0))
deck_felt=dict(id="lock_deck_felt",zone="lock",center=[0,0,-23.325],size=[3.2,3.35],yaw=0,slope=None,thickness=.15,edge_support=True)
h.d["moving_parts"].append(dict(id="lock_lift_deck",type="lift",axis=[0,1,0],pivot=[0,0,-25],speed=4/H11_TRAVEL,period_s=lock_period,
    felt=[deck_felt], blockers=[dict(center=[0,-.075,1.675],size=[3.2,.15,3.35],yaw=0)],
    schedule=dict(rise=[h11_rise,h11_top],release=[h11_top,h11_down],return_=[h11_down,h11_bottom],height=4,tilt_deg=0),
    visual="Moving timber deck carries felt and solid collision; south gate slot ends at z=-21.65; deck stays level throughout rise, top dwell, and descent."))
h.d["moving_parts"].append(dict(id="quay_lip",type="quay_lip",axis=[0,1,0],pivot=[0,4.25,-25.45],speed=10,period_s=lock_period,
    blockers=[dict(center=[0,0,0],size=[3.6,1.5,.2],yaw=0)],
    felt=[dict(id="lip_top",zone="quay",center=[0,5,-25.45],size=[3.6,.2],yaw=0,slope=None,thickness=1.5,edge_support=True)],
    visual=f"Visible red/cream striped moving lip: top y=5 (same as quay rail20); sinks to top y=4 during interval {h11_flush}, surrounding the level top dwell [{h11_top},{h11_down}].",
    schedule=dict(flush=h11_flush),
    interlock="flush from 0.1s before reaching top until 0.1s after descent starts", clearance=.15,
    appearance=dict(pattern="alternating_bands",colors=["#B83A35","#FFF0C9"],axis="x",band_width=.6)))
h.teleport("lock_lift", [0.0, 0.0, -23.0], 1.5, [0.0, 4.0, -27.0], (0.0, -1.0), speed_factor=H11_EXIT[2], min_speed=H11_EXIT[0],
           max_speed=H11_EXIT[1], half_size=[1.9, 2.08], kind="lift",
           ride=dict(rise=4.0, platform="lock_lift_deck carries its own felt and solid collision; no static lock felt",
                     motion=f"while the gate is up: rise 4.0 at {4/H11_TRAVEL:g} studs/s ({H11_TRAVEL:g} s), stay level for {H11_TOP_DWELL:g}s and push the ball onto the quay at "
                            f"(0, 4, -27) heading -Z at clamp(entry speed x {H11_EXIT[2]:g}, {H11_EXIT[0]:g}, {H11_EXIT[1]:g}) studs/s, then "
                            f"drop back ({H11_TRAVEL:g} s) before the gate sinks again",
                     cycle_s=round(lock_period, 3), release_window=[h11_top,h11_down], handoff_z=-21.52, admission_until=H11_DW[0],
                     gate_sill_retention=dict(when="gate-top rider north crossing below raised deck", x_clamp=[-1.72,1.72], y=1.2, z=-21.49, velocity=[0,0,0], hold_until_phase=h11_bottom, next_release_phase=h11_top, engine_requirement="Physical or scripted retainer must clamp the rider on the gate top until the deck returns, then retain on deck for next ride."),
                     capture="Retain any ball crossing the gate north face onto or above the deck, including elevated gate-top riders during initial rise; the enclosed chamber catches the drop, then releases at the scheduled quay exit. Late gate-top riders below a raised deck are held on the gate sill until the deck returns and take the NEXT ride. This gate-sill retention is an explicit transport abstraction that the engine implementation must reproduce."),
           visual="Lock chamber floor = lift platform: a ball that rolls onto it (past the sunken gate) is lifted to the quay and pushed out by "
                  "the sluice rush (exit speed scales with the entry speed)")
h.tee(0, 0, 0)
h.cup(*H11_CUP, flag_h=7.5)
h.d["cup_from"] = ["green", "quay"]
h.wp("all", "lock", [0.0, 0.0, -23.0], ["lane", "approach"], carry=K("h11_carry", 2.0))
h.anchor("lock_keeper_hut", [9, 0, -10], "Lock-keeper's hut with a brass winch and a striped barber-pole gauge (outside the east rail)", landmark=True,
         size=[5, 7, 5], occluders=[((9, 3.5, -10), (5, 7, 5))])
h.anchor("lock_chamber", [0, 0, -23], "Peppermint-concrete lock chamber walls (4 tall, up to the quay) with brass bollards; the platform is a timber "
         "raft-deck that rides up inside it; approved wall centers x=+-3, z=-23, run 2.8; collision containment reaches y=4.6", size=[6.6, 4.6, 2.8])
h.anchor("gate_winches", [-3.0, 0, -23.0], "Brass winch posts either side of the lock gate (outside the chamber walls)", size=[0.8, 2.5, 0.8],
         occluders=[((-3.0, 1.25, -23.0), (0.8, 2.5, 0.8)), ((3.0, 1.25, -23.0), (0.8, 2.5, 0.8))])
felt_arrow(h, "felt_arrow_lock", [0.0, 0.0, -18.0], "Glowing felt arrow decal pointing into the lock (with a little 'wait for the gate' clock icon)")
h.anchor("gate_light", [0, 5.0, -25.4], "Red/green lock signal lamp on the quay face above the chamber: green while the gate is down "
         "(visual timing cue)", size=[0.8, 1.2, 0.4])
holes.append(h)

# ================================================================ H12 Intake Tower (par 4): pipe teleport vs shoreline route
H12_CUP = K("h12_cup", [2.0, 0.0, -58.0])
H12_GR = K("h12_grate_r", 0.3)
H12_EXIT = K("h12_exit", [11.0, 0.0, -61.0])
H12_PIER = K("h12_pier", (-1.5, 1.5, -35.0))
h = new_hole(12, "h12", "Intake Tower", 4, "Domed intake tower standing in the reservoir",
             "Pipe teleport: sink the ball in the intake grate at the end of a rail-less pier and it shoots out of an outflow pipe by the green, or play the long shoreline route")
h.rect("lane", -4, 4, 2, -14, 0.0, zone="lane")
h.rect("junction", -16, 4, -14, -22, 0.0, zone="junction")
h.rect("pier", H12_PIER[0], H12_PIER[1], -22, H12_PIER[2], 0.0, zone="pier", kind="bridge")
h.rect("shoreline", -16, -11, -22, -50, 0.0, zone="shore")
h.rect("green", -16, 14, -50, -64, 0.0, zone="green")
h.hazard("reservoir", "water", -11, 14, -22, -50, -1.2)
h.wall_path([(H12_PIER[1], -22), (4, -22), (4, 2), (-4, 2), (-4, -14), (-16, -14), (-16, -64), (14, -64), (14, -50), (-11, -50), (-11, -22),
             (H12_PIER[0], -22)], 0.0, out="L", ext=(0.0, 0.0), top=2.4)
h.bank_wall("shore_bank", (-11.5, -14.7), (-15.3, -18.5), "L", zone="junction", ext_bank=0.2, ext_back=0.3)
h.bank_wall("green_bank", (-15.3, -59.7), (-11.4, -63.6), "L", zone="green", ext_bank=0.2, ext_back=0.3)
gdir = (H12_CUP[0] - H12_EXIT[0], H12_CUP[2] - H12_EXIT[2])
h.teleport("intake_pipe", [0.0, 0.0, H12_PIER[2] + 2.0], H12_GR, H12_EXIT, K("h12_exit_dir", gdir), speed_factor=K("h12_sf", 0.7),
           min_speed=K("h12_vmin", 3.0), max_speed=K("h12_vmax", 7.0),
           visual="Brass intake grate (glowing lime ring) set in the pier deck 2 studs from its open end -> outflow pipe mouth on the green's east side")
h.tee(0, 0, 0)
h.cup(*H12_CUP, flag_h=7.5)
h.d["cup_from"] = ["green"]
h.wp("good", "grate", [0.0, 0.0, H12_PIER[2] + 2.0], ["lane", "junction", "pier"], carry=K("h12_grate_carry", 0.6))
h.wp("average", "shore_in", [-12.5, 0.0, -18.0], ["lane", "junction"], carry=K("h12_avg_c1", 2.0))
h.wp("average", "shore_top", [-13.5, 0.0, -48.0], ["junction"], carry=K("h12_avg_c2", 6.0))
h.wp("average", "green_w", [-13.5, 0.0, -57.0], ["shore"], carry=K("h12_avg_c3", 3.0))
h.anchor("intake_tower", [6, -1.2, -38], "Domed peppermint intake tower standing in the water east of the pier (visual), a pipe running under the "
         "water from the grate to the outflow on the green", landmark=True, size=[7, 16, 7], occluders=[((6, 6.8, -38), (6, 16, 6))])
h.anchor("intake_grate", [0.0, 0.0, H12_PIER[2] + 2.0], f"Round brass intake grate flush in the pier deck with a glowing lime ring ({2 * H12_GR:g} across)",
         size=[1.4, 0.02, 1.4])
h.anchor("outflow_pipe", H12_EXIT, "Big riveted outflow pipe mouth on the green's east edge, angled at the cup (teleport exit, splash particles)",
         size=[2.5, 2.5, 3])
h.anchor("pier_posts", [0, -1.2, -28], "Timber pier on posts (no railings: the open sides and end drop into the reservoir)", size=[3.2, 1.4, 13])
sign(h, "sign_pier", (2.2, 0, -20), "Sign 'Intake - shoot the pipe!' at the pier root", (0, -1), size=(1.6, 2.6, 0.2))
sign(h, "sign_shore", (-16.6, 0, -24), "Sign 'Shoreline Trail' pointing north along the shore", (0.3, -1))
felt_arrow(h, "felt_arrow_pier", [0.0, 0.0, -20.0], "Glowing felt arrow decal pointing -Z onto the pier")
felt_arrow(h, "felt_arrow_shore", [-13.5, 0.0, -24.0], "Glowing felt arrow decal pointing -Z up the shoreline")
holes.append(h)

# ================================================================ H13 Hoodoo Maze (par 3)
# A foyer feeds three walled corridors between striped rock: CENTRE (short, 4 wide, staggered hoodoos: the risky birdie/ace line),
# EAST (medium, hoodoos, ends far from the cup) and WEST (long and safe, round the west rock to the green).
H13_CUP = K("h13_cup", [0.5, 0.0, -51.0])
H13_P = K("h13_pillars", [  # x, z, side, yaw
    [-1.1, -24.0, 1.0, 45.0], [1.1, -32.0, 1.0, 45.0],        # centre corridor
    [-13.0, -30.0, 1.4, 45.0],                                # west corridor
    [11.5, -24.0, 1.4, 45.0], [10.2, -33.0, 1.2, 0.0],         # east corridor
])
h = new_hole(13, "h13", "Hoodoo Maze", 3, "Cluster of striped hoodoo spires with balanced gumdrop caps",
             "Pillar maze: hoodoo pillars and striped rock make three corridors of different length and risk")
H13_FZ = K("h13_foyer_z", -4.0)   # where the tee lane opens into the foyer
h.rect("lane", -4, 4, 2, H13_FZ, 0.0, zone="lane")
h.rect("foyer", -14, 14, H13_FZ, -16, 0.0, zone="foyer")
H13_WJ = K("h13_west_join", -40.0)   # z where the west corridor opens into the green
h.rect("west", -14, -9, -16, H13_WJ, 0.0, zone="west")
h.rect("centre", -2, 2, -16, -40, 0.0, zone="centre")
h.rect("east", 9, 14, -16, -40, 0.0, zone="east")
h.rect("green", -9, 14, -40, -54, 0.0, zone="green")
h.rect("green_w", -14, -9, H13_WJ, -54, 0.0, zone="green")
h.wall_path([(-4, 2), (-4, H13_FZ), (-14, H13_FZ), (-14, -54), (14, -54), (14, H13_FZ), (4, H13_FZ), (4, 2)], 0.0, out="L", closed=True)
h.wall_path([(-9, -16), (-2, -16), (-2, -40), (-9, -40)], 0.0, out="L", closed=True, name="rock_w")
h.wall_path([(2, -16), (9, -16), (9, -40), (2, -40)], 0.0, out="L", closed=True, name="rock_e")
for i, (px, pz, s_, yw) in enumerate(H13_P, 1):
    h.block(f"hoodoo{i}", px, pz, s_, s_, 0.0, height=1.5, yaw=yw)
h.tee(0, 0, 0)
h.cup(*H13_CUP, flag_h=7.5)
h.d["cup_from"] = ["green", "centre", "west"]
h.wp("good", "centre_far", [K("h13_wpx", 0.0), 0.0, -41.0], ["lane", "foyer", "centre"], carry=K("h13_good_carry", 4.0))
h.wp("average", "west_mouth", [-11.5, 0.0, -18.5], ["lane", "foyer"], carry=1.0)
h.wp("average", "west_top", [-11.5, 0.0, H13_WJ - 2.5], ["foyer", "west"], carry=K("h13_avg_carry", 3.0))
for i, (px, pz, s_, yw) in enumerate(H13_P, 1):
    h.anchor(f"hoodoo_{i}", [px, 0, pz], f"Striped hoodoo spire ({s_:g} base collider, yaw {yw:g}) 8-14 studs tall with a balanced gumdrop cap",
             size=[s_ + 0.6, 12, s_ + 0.6], occluders=[((px, 6, pz), (s_ * 0.9, 12, s_ * 0.9), yw)])
h.anchor("maze_rock", [-5.5, 0, -28], "Striped hoodoo-rock walls between the corridors (colliders 1 tall on the rails; dressed as 3-5 tall banded rock "
         "and hoodoo clusters, kept below the tee->flag sightline over the centre corridor)", landmark=True, size=[7, 4, 24])
h.anchor("lantern_cue", [H13_CUP[0], 9.0, H13_CUP[2]], "Gumdrop-glass lantern hanging 9 studs over the cup from a rope between two hoodoos: "
         "the visual cue when the hoodoos hide the flag", size=[1.0, 1.5, 1.0])
sign(h, "sign_west", (-14.6, 0, -10), "Sign 'Long & easy' pointing into the west corridor", (0.3, -1))
sign(h, "sign_centre", (-2.6, 0, -15.5), "Sign 'Straight through (mind the hoodoos!)' at the centre corridor", (0.1, -1))
sign(h, "sign_east", (14.6, 0, -10), "Sign 'Scenic route' pointing into the east corridor", (-0.3, -1))
for aid, ax, label in (("west", -11.5, "SAFE WEST"), ("centre", 0, "SHORT CENTRE"), ("east", 11.5, "SCENIC EAST")):
    felt_arrow(h, "route_arrow_" + aid, [ax, 0, -13], label + ": north from foyer into the marked corridor")
    h.d["decoration_anchors"][-1]["facing"] = [0, -1]
holes.append(h)

# ================================================================ H14 Ore Bucket Swing (par 3): pendulum
H14_CUP = K("h14_cup", [1.0, 0.8, -44.0])
H14_LW = K("h14_lane_hw", 4.0)
H14_RISE = K("h14_rise", 0.8)
H14_L = K("h14_len", 9.0)
BUCKET = K("h14_bucket", [2.1, 2.0, 1.8])
H14_AMP = K("h14_amp", 9.0)
H14_PER = K("h14_period", 4.0)
H14_FOOT = K("h14_foot", [2.1, 0.4, 0.15])
H14_Z = K("h14_z", -24.0)
h = new_hole(14, "h14", "Ore Bucket Swing", 3, "Cableway trestle with a swinging ore bucket",
             "Pendulum: an ore bucket swings from a cableway trestle across the lane, before a ramp up to the raised loading-dock green")
_bhx = BUCKET[0] / 2
H14_GAP = round(max(K("h14_gap", 0.35), 0.02 + _bhx ** 2 / (2 * (H14_L + BUCKET[1] / 2))), 3)
H14_PIV = [K("h14_piv_x", 0.0), round(H14_GAP + BUCKET[1] / 2 + H14_L, 3), H14_Z]
_fhx = H14_FOOT[0] / 2
_fr = H14_L + BUCKET[1] / 2 + H14_GAP
H14_FOOT_CLEAR = K("h14_foot_clear", 0.15)   # p9: lowest foot corner above the felt at every angle of the swing (was ~.02)
H14_FOOT_STRIPS = K("h14_foot_strips", 14)    # p9b: 14 strips of .15 (was 6 of .35)
# p9 chamfer: the foot is split into yaw-0 strips whose outer bottom corners lie on a circle about the hinge (radius = hinge
# height - clearance), so its underside is a polygonal arc and the clearance is the same at every swing angle (north/south faces
# stay square to the shot line). Strip tops all sit at the legacy foot top (bucket bottom + .125, inside the bucket).
_frc = _fr - H14_FOOT_CLEAR - 0.0002          # .0002 margin absorbs the 4-decimal rounding of the strip boxes
# p9b: only the outer strips are chamfered to H14_FOOT_CLEAR; strips within |x| <= h14_centre_hw stay low (their corners on a
# circle of radius hinge height - h14_centre_clear) so the centre still blocks a 0.16-tall ball.
H14_CC = K("h14_centre_clear", 0.06)
H14_CHW = K("h14_centre_hw", 0.9)             # p9b: only the outermost .15 strip each side is chamfered
_frcc = _fr - H14_CC - 0.0002
_ftop = -_fr + 0.075 + H14_FOOT[1]
feet = []
for j in range(H14_FOOT_STRIPS):
    x0 = -_fhx + j * H14_FOOT[0] / H14_FOOT_STRIPS
    x1 = x0 + H14_FOOT[0] / H14_FOOT_STRIPS
    _xo = max(abs(x0), abs(x1))
    fb = -math.sqrt((_frcc if _xo <= H14_CHW + 1e-9 else _frc) ** 2 - _xo ** 2)
    feet.append(dict(center=[round((x0 + x1) / 2, 4), round((fb + _ftop) / 2, 4), 0], size=[round(x1 - x0, 4), round(_ftop - fb, 4), H14_FOOT[2]],
                     yaw=0.0))
H14_FOOT_GAP = round(_fr + min(f["center"][1] - f["size"][1] / 2 for f in feet), 4)   # gap at rest (centre strips)
h.rect("lane", -H14_LW, H14_LW, 2, H14_Z - 1.0, 0.0, zone="lane")
h.rect("lane2", -H14_LW, H14_LW, H14_Z - 1.0, -30, 0.0, zone="lane2")
H14_RHW = K("h14_ramp_hw", 4.0)          # ramp half-width (narrower than the 7-wide lane = a precise approach)
h.rect("ramp", -H14_RHW, H14_RHW, -30, -36, zone="ramp", slope=("z", 0.0, H14_RISE))
h.rect("green", -8, 8, -36, -48, H14_RISE, zone="green")
if H14_RHW < H14_LW:
    h.wall_path([(-H14_LW, 2), (-H14_LW, -30), (-H14_RHW, -30), (-H14_RHW, -36), (-8, -36), (-8, -48), (8, -48), (8, -36), (H14_RHW, -36),
                 (H14_RHW, -30), (H14_LW, -30), (H14_LW, 2)],
                [0, 0, 0, H14_RISE, H14_RISE, H14_RISE, H14_RISE, H14_RISE, H14_RISE, 0, 0, 0], out="L", closed=True)
else:
    h.wall_path([(-H14_LW, 2), (-H14_LW, -30), (-H14_LW, -36), (-8, -36), (-8, -48), (8, -48), (8, -36), (H14_LW, -36), (H14_LW, -30), (H14_LW, 2)],
                [0, 0, H14_RISE, H14_RISE, H14_RISE, H14_RISE, H14_RISE, H14_RISE, 0, 0], out="L", closed=True)
h.swing("ore_bucket", H14_PIV, [0, 0, 1], H14_AMP, H14_PER, [dict(center=[0, -H14_L, 0], size=BUCKET, yaw=0.0)] + feet,
        visual=f"Ore bucket ({BUCKET[0]:g}x{BUCKET[1]:g}x{BUCKET[2]:g}) on a {H14_L:g}-stud hanger from the cableway trestle, swinging east-west across "
               f"the lane; blockers 2..{1 + H14_FOOT_STRIPS} = invisible collider foot {H14_FOOT[0]:g} wide x {H14_FOOT[2]:g} deep in "
               f"{H14_FOOT_STRIPS} yaw-0 strips (north/south faces square to the shot line) under the bucket. Centre strips (|x| <= {H14_CHW:g}) "
               f"hang low on an arc of radius {_frcc:.3f} about the hinge ({H14_CC:g} min clearance, {H14_FOOT_GAP:g} at rest) so they block the ball; "
               f"the outer strips are chamfered to an arc of radius {_frc:.3f}: outer corners {H14_FOOT_CLEAR:g} above the felt at every angle of the "
               f"+-{H14_AMP:g} deg swing (bucket bottom {H14_GAP:g}); the bucket mesh gets a matching base skid plate")
h.tee(0, 0, 0)
h.cup(*H14_CUP, flag_h=7.5)
if K("h14_good_side", True):
    h.wp("good", "side_line", [K("h14_side_x", 2.7), 0.0, H14_Z - 5.0], ["lane"], carry=K("h14_side_carry", 2.0))
h.d["cup_from"] = {"good": ["green", "lane2", "ramp"] if K("h14_good_side", True) else None, "average": None}
h.anchor("cableway_trestle", [0, 0, H14_Z], f"Timber cableway trestle (legs outside the rails at x +-5, beam at y {H14_PIV[1]:g}) with the ore-bucket "
         "hanger; the main ore cableway continues overhead to the Hoodoo Garden", landmark=True, size=[10, H14_PIV[1] + 1, 1.5],
         occluders=[((-5.0, H14_PIV[1] / 2, H14_Z), (0.8, H14_PIV[1], 0.8)), ((5.0, H14_PIV[1] / 2, H14_Z), (0.8, H14_PIV[1], 0.8)),
                    ((0, H14_PIV[1] + 0.5, H14_Z), (10, 1.0, 1.0))])
h.anchor("ore_bucket", [H14_PIV[0], H14_PIV[1] - H14_L, H14_Z], f"Riveted ore bucket heaped with rock candy (moving mesh, pivot at the hinge "
         f"{H14_PIV}); base skid plate matches the collider foot", size=BUCKET)
h.d["safe_route"] = dict(kind="intentional bank bypass", legacy_ace_aim_deg=256.5,
                         note="Bank off the west rail to pass west of the bucket; right edge is also safe. Central line is timed.")
sign(h, "safe_bank_sign", (-5.0,0,-9), "SAFE BANK: left rail, then outside the bucket. CENTRE: wait for swing.", (0,-1))
felt_arrow(h, "safe_bank_arrow", [-2,0,-7], "Arrow southwest toward west rail: SAFE BANK")
felt_arrow(h, "timing_arrow", [0,0,-16], "CENTRE: wait until bucket swings clear")
h.anchor("ore_piles", [10, 0.8, -42], "Spilled rock-candy ore piles outside the green's east rail", size=[3, 1.5, 3])
h.anchor("loading_dock", [0, 0, -33], f"Timber ore-loading ramp (felt rises {H14_RISE:g} over 6) up to the raised loading-dock green", size=[8, 1, 6])
holes.append(h)

# ================================================================ H15 Sugar Dune (par 3; course.md planned 4, the sim plays it as a 3): side-slope reading
# The tee lane drops onto one big tilted dune face: a single plane, yawed off the hole axis, whose fall line runs mostly ACROSS the
# line of play (east) and partly down-hole (north), like a sand-sled run. Its north edge drops onto a two-tier green that runs on
# under the face's lower end (the face is a cliff for balls on the green).
H15_YAW = K("h15_yaw", 25.0)            # dune plane yaw (deg); its local +x = the downhill direction
H15_SZ = K("h15_size", (24.0, 30.0))
H15_C = K("h15_center", (0.0, -24.0))
H15_DY = K("h15_dune_y", -2.2)          # dune height at its centre
H15_RISE = K("h15_rise", -2.4)          # height change across the dune's local x (negative = falls toward local +x)
H15_G = K("h15_green_y", -4.0)          # upper tier
H15_T2 = K("h15_tier", 0.6)             # lower tier step
H15_CUP = K("h15_cup", [6.0, -4.6, -57.0])
h = new_hole(15, "h15", "Sugar Dune", 3, "Powdered-sugar dune with sand-sled tracks",
             "Side-slope reading: a long dune face tilted across the line, dropping to a two-tier green")
h.rect("lane", -4, 4, 2, -10, 0.0, zone="lane")
dune = h.rect("dune", H15_C[0] - H15_SZ[0] / 2, H15_C[0] + H15_SZ[0] / 2, H15_C[1] + H15_SZ[1] / 2, H15_C[1] - H15_SZ[1] / 2,
              zone="dune", slope=("x", H15_DY - H15_RISE / 2, H15_DY + H15_RISE / 2))
dune["yaw"] = H15_YAW
h.rect("upper_tier", -17.5, 17.5, -32, -48, H15_G, zone="green")
h.rect("tier_ramp", -17.5, 17.5, -48, -51, zone="green", slope=("z", H15_G, H15_G - H15_T2))
h.rect("lower_tier", -17.5, 17.5, -51, -62, H15_G - H15_T2, zone="green")


def dune_pt(lx, lz):
    dx, dz = rot(lx, lz, H15_YAW)
    return (r4(H15_C[0] + dx), r4(H15_C[1] + dz))


def dune_h(lx):
    return H15_DY + H15_RISE * lx / H15_SZ[0]


hx, hz = H15_SZ[0] / 2, H15_SZ[1] / 2
SW, SE, NE, NW = dune_pt(-hx, hz), dune_pt(hx, hz), dune_pt(hx, -hz), dune_pt(-hx, -hz)
h.drop("d1", "lane", "dune", "lane north edge z=-10 (onto the tilted dune face)", round(-dune_h(0), 2))
h.drop("d2", "dune", "green", "dune north (local -z) edge, onto the upper tier", round(dune_h(hx) - H15_G, 2))
# dune rails: west and east edges, and the south edge outside the lane (under the lane the lane deck itself is the cliff)
yW, yE = dune_h(-hx), dune_h(hx)
h.wall_path([SW, NW], [yW, yW], out="L", ext=(0.5, 0.0), name="dune_rail", ybot=yW - 0.45)
H15_PIT = K("h15_pit", False)
if H15_PIT:   # open low (east) edge over a sugar-sand pit: +1 and back to the stroke start
    pc = dune_pt(hx + 1.0, 0.0)
    h.d["hazards"].append(dict(id="sugar_pit", type="pit", center=[pc[0], round(yE - 1.0, 3), pc[1]], size=[2.0, r4(H15_SZ[1] + 1.0)],
                               yaw=H15_YAW, reset="previous_position", penalty=1))
else:
    # 2026-10-12 late (Studio: 3 of 8 random shots wedged where the dune felt met dune_rail2): the dune falls only across local x
    # (slope 0.1), so a ball pressed into an east rail running along local z had no slope along it and sat there (game 2 s wedge
    # rule). The east rail now leans in by h15_rail_in at its south end, so it runs downhill toward the north-east corner: a ball
    # pressed into it slides along it (gravity along the rail 32.7 x 0.1 x sin(atan(d/30)) > RollDecel 0.5) and drops onto the green.
    # The dune felt east of that line is behind the rail (trim it in the mesh; it is unreachable).
    H15_RIN = K("h15_rail_in", 8.0)
    SEi = dune_pt(hx - H15_RIN, hz)
    yEi = dune_h(hx - H15_RIN)
    # The original edge rails stay (they enclose the dead triangle behind the lean rail, so nothing is open).
    h.wall_path([NE, SE], [yE, yE], out="L", ext=(0.0, 0.5), name="dune_rail", ybot=yE - 0.45)
    h.wall_path([NE, SEi], [yE, yEi], out="L", ext=(0.0, 0.0), name="dune_lean", ybot=K("h15_rail_bot", yE - 0.45))


def south_cut(xc):
    """point on the dune's south edge with world x = xc"""
    t = (xc - SW[0]) / (SE[0] - SW[0])
    return (r4(xc), r4(SW[1] + t * (SE[1] - SW[1]))), t


pW, tW = south_cut(-3.8)
pE, tE = south_cut(3.8)
h.wall_path([SW, pW], [yW, dune_h(-hx + tW * 2 * hx)], out="R", ext=(0.5, 0.0), name="dune_rail")
h.wall_path([pE, SE], [dune_h(-hx + tE * 2 * hx), yE], out="R", ext=(0.0, 0.5), name="dune_rail")
h.wall_path([(-4, -10), (-4, 2), (4, 2), (4, -10)], 0.0, out="R", ext=(0.0, 0.0), name="lane_rail", ybot=-0.5)
g2 = H15_G - H15_T2
# green rails; the south edge is low (0.55) because the dune face overhangs part of it
h.wall_path([(-17.5, -32), (-17.5, -62), (17.5, -62), (17.5, -32)], [H15_G, g2, g2, H15_G], out="L", ext=(0.0, 0.0), name="green_rail")
h.wall_free((-17.75, -31.75), (17.75, -31.75), H15_G, name="green_s_rail", height=0.55, ybot=H15_G - 0.5)
h.tee(0, 0, 0)
h.cup(*H15_CUP, flag_h=7.5)
h.d["cup_from"] = ["green", "dune"]
h.wp("all", "dune_far", [K("h15_aim", (-8.0, -30.0))[0], 0.0, K("h15_aim", (-8.0, -30.0))[1]], ["lane"], carry=K("h15_c1", 4.0))
h.wp("all", "green_in", [K("h15_g_x", -6.0), H15_G, -42.0], ["dune"], carry=K("h15_c2", 3.0))
h.anchor("sugar_dune", [H15_C[0], H15_DY, H15_C[1]], f"Powdered-sugar dune face (the tilted felt plane, yaw {H15_YAW:g}, falling {abs(H15_RISE):g} toward the "
         "east-north-east), sled tracks, a striped sand-sled propped on the lane lip; dune dressing beyond the rails", landmark=True, size=[30, 6, 34])
felt_arrow(h, "slope_arrows", [H15_C[0], H15_DY, H15_C[1]], "Faint wind-ripple chevrons printed across the dune felt pointing down the fall line "
           "(east-north-east): the reading aid", size=(20, 0.01, 2))
felt_arrow(h, "lip_chevrons", [0, 0, -9.5], "Felt chevrons at the lane lip pointing -Z: the dune face below is one-way (the ball won't come back up)",
           size=(7, 0.01, 1))
h.anchor("tier_lip", [0, H15_G, -48], "Sugar-sandstone lip trim along the two-tier step", size=[32, 0.3, 0.5])
h.anchor("dune_cliff", [6, H15_G, -37], "Sugar-sandstone cliff face where the dune's lower end overhangs the upper tier (visual skirt down to the green)",
         size=[16, 2, 1])
holes.append(h)

# ================================================================ H16 Sinkhole Drop (par 2)
H16_HOLE = K("h16_hole", (-1.2, 1.2, -15.0, -17.4))
H16_LOW = -3.6
H16_SIDE = K("h16_side_rise", 0.6)
H16_CUP = K("h16_cup", [1.8, H16_LOW, -38.5])
h = new_hole(16, "h16", "Sinkhole Drop", 2, "Crystal-lined sinkhole with a rope railing",
             "Drop between levels: putt into a sinkhole in the upper deck and fall 3.6 studs into a funnel bowl")
hx0, hx1, hz0, hz1 = H16_HOLE
h.rect("deck_s", -4, 4, 2, -12, 0.0, zone="deck")
h.rect("deck_m", -4, 4, -12, hz0, 0.0, zone="deck", solid=False, thickness=0.4)
h.rect("deck_w", -4, hx0, hz0, hz1, 0.0, zone="deck", solid=False, thickness=0.4)
h.rect("deck_e", hx1, 4, hz0, hz1, 0.0, zone="deck", solid=False, thickness=0.4)
h.rect("deck_n", -4, 4, hz1, -24, 0.0, zone="deck", solid=False, thickness=0.4)
h.rect("bowl_mid", -2, 2, -12, -40, H16_LOW, zone="bowl")
h.rect("bowl_w", -8, -2, -12, -40, zone="bowl", slope=("x", H16_LOW + H16_SIDE, H16_LOW))
h.rect("bowl_e", 2, 8, -12, -40, zone="bowl", slope=("x", H16_LOW, H16_LOW + H16_SIDE))
h.drop("d1", "deck", "bowl", f"sinkhole x[{hx0:g},{hx1:g}] z[{hz1:g},{hz0:g}] in the deck", -H16_LOW)
h.wall_path([(-4, 2), (-4, -24), (4, -24), (4, 2)], 0.0, out="L", closed=True, name="deck_rail")
yb = H16_LOW + H16_SIDE
h.wall_path([(-8, -12), (-8, -40), (8, -40), (8, -12)], [yb, yb, yb, yb], out="L", closed=True, name="bowl_rail", ybot=H16_LOW - 0.5)
h.tee(0, 0, 0)
h.cup(*H16_CUP, flag_h=7.5)
h.d["cup_from"] = ["bowl"]
h.wp("all", "sinkhole", [(hx0 + hx1) / 2, 0.0, (hz0 + hz1) / 2], ["deck"], carry=K("h16_carry", 10.0), power_scale=K("h16_ps", 1.0))
h.anchor("sinkhole_rim", [(hx0 + hx1) / 2, 0, (hz0 + hz1) / 2], "Crystal-lined sinkhole rim flush with the deck (rock-candy crystals inside the shaft "
         "glowing pink), a low rope railing on posts outside the deck rails", landmark=True, size=[3.4, 0.3, 3.4])
h.anchor("deck_overhang", [0, -1.8, -18], "Sandstone deck slab over the bowl's south end (the bowl runs 12 studs back under it, lit by "
         "the crystals); deck underside 3.2 above the bowl felt", size=[8.5, 3.6, 12])
felt_arrow(h, "felt_arrow_sink", [0.0, 0.0, -10.0], "Glowing felt arrow decal pointing at the sinkhole")
h.anchor("bowl_rim", [0, H16_LOW, -40], "Crystal-studded bowl rim behind the north rail", size=[17, 1.5, 1])
holes.append(h)

# ================================================================ H17 Sundial (par 3): horizontal sweeper
H17_C = (0.0, -36.0)
H17_AP = 13.0
H17_ARMS = K("h17_arms", 4)
H17_SPEED = K("h17_speed", 12.0)
H17_ARM = K("h17_arm", (8.2, 11.5, 3.6))    # r_in, r_out, thickness
H17_CUP = K("h17_cup", [10.1, 0.0, -43.0])
h = new_hole(17, "h17", "Sundial", 3, "Giant stone sundial with candy-coloured hour stones",
             "Four timed shadow arms sweep around a solid central plinth on a square green")
h.rect("lane", -7.5, 7.5, 2, H17_C[1] + H17_AP, 0.0, zone="lane")
h.rect("dial_a", H17_C[0] - H17_AP, H17_C[0] + H17_AP, H17_C[1] + H17_AP, H17_C[1] - H17_AP, 0.0, zone="dial")
zs=H17_C[1]+H17_AP
h.wall_path([(-7.5,2),(-7.5,zs),(-H17_AP,zs),(-H17_AP,H17_C[1]-H17_AP),(H17_AP,H17_C[1]-H17_AP),(H17_AP,zs),(7.5,zs),(7.5,2)],0.0,out="L",closed=True)
# A solid, stepped circular plinth excludes every ball rest within seven studs.
# Each strip encloses the circle of radius 7.5; the outside corners remain <8.0,
# leaving >.15 clearance to the 8.2 inner radius of the arms.
for j in range(48):
    z0 = -7.5 + j * 15 / 48
    z1 = z0 + 15 / 48
    zn = min(abs(z0),abs(z1)) if z0*z1 > 0 else 0
    half = math.sqrt(7.5**2-zn**2)
    h.block(f"gnomon_plinth_{j:02d}", 0, H17_C[1]+(z0+z1)/2,
            2*half,z1-z0,0,height=1.2)
h.d["rest_exclusion"] = dict(center=[0,0,-36], radius=7.0, physical_plinth_radius=7.5,
                            method="48 solid circumscribed sandstone strips; balls cannot occupy the central disk")
h.rotor("shadow_arm", [H17_C[0], 0.0, H17_C[1]], [0, 1, 0], H17_SPEED, arm_blockers(H17_ARMS, H17_ARM[0], H17_ARM[1], H17_ARM[2], 0.9),
        visual=f"Sundial shadow arm{'s' if H17_ARMS > 1 else ''}: {H17_ARMS} low slate bar{'s' if H17_ARMS > 1 else ''} (r {H17_ARM[0]:g}..{H17_ARM[1]:g}, "
               f"{H17_ARM[2]:g} thick, 0.9 tall) sweeping round the gnomon at {abs(H17_SPEED):g} deg/s")
h.tee(0, 0, 0)
h.cup(*H17_CUP, flag_h=7.5)
h.d["cup_from"] = ["lane", "dial"]
h.wp("all", "dial_side", [K("h17_side", [9.5, -36.0])[0], 0.0, K("h17_side", [9.5, -36.0])[1]], ["lane"], carry=K("h17_carry", 2.0))
h.wp("all", "south_w", [-10.5,0,-27.5], ["dial"], carry=0.0)
h.wp("all", "south_e", [10.5,0,-27.5], ["dial"], carry=0.0)
h.wp("all", "dial_w", [-8.5, 0.0, -45.0], ["dial"], carry=0.5)
h.wp("all", "dial_e", [8.5, 0.0, -45.0], ["dial"], carry=0.5)
if K("h17_avg_safe", True):
    h.d["cup_from"] = {"good": ["lane", "dial"], "average": ["dial"]}
    h.wp("average", "safe_east_approach", [8.0,0,-27.0], ["lane"], carry=0.0)
    for point in h.d["ai_waypoints"]["all"]:
        if "dial" in point["from"]:
            h.d["ai_waypoints"]["average"].append(dict(point))
felt_arrow(h, "safe_east_wait", [8.0,0,-27.0], "Safe-route waiting marker outside the arm annulus: play here first, then time the short east-side putt to the cup")
h.anchor("gnomon", [H17_C[0], 0, H17_C[1]], "Tall candy-striped sundial gnomon (triangular fin, 9 tall) on a solid radius-7.5 sandstone plinth, height 1.2, at the dial centre; "
         "hour stones in candy colours on a radius-12.5 ring inside the square perimeter (see hour_stone_* anchors)", landmark=True, size=[1.6, 9, 6],
         occluders=[((H17_C[0], 3.5, H17_C[1]), (1.2, 7, 1.2))])
h.anchor("gnomon_plinth", [0,0,-36], "Solid sandstone central plinth: 48 circumscribed box strips enclose radius 7.5; top y=1.2; no walkable or playable surface on top; keeps every ball outside the seven-stud rest exclusion", size=[15.0,1.2,15.0])
h.anchor("shadow_arm", [H17_C[0], 0, H17_C[1]], "Slate shadow-arm mesh(es) (moving, pivot = dial centre, axis +Y)", size=[2 * H17_ARM[1], 0.9, H17_ARM[2]])
# p9 hour stones: 12 positions on a radius-12.5 ring about the gnomon (arms reach 11.5), 30 deg apart, XII toward local -Z, III toward +X.
# Each 1.2 x 0.8 x 1.2 (sx, sy, sz), sitting on the felt (centre y .4, top .8). Decorative, collision off, except the three whose
# footprint reaches .1 over a rail inner face (XII south, III east, IX west): those are rail-mounted solid stones with collision.
# Dropped: II (footprint covers the cup), V (good tee line and ace line roll through it), VI (centre of the lane mouth, the only approach).
H17_STONE_R = K("h17_stone_r", 12.5)
H17_STONE = (1.2, 0.8, 1.2)
H17_STONE_DROP = K("h17_stone_drop", {"II": "footprint covers the cup [10.1,0,-43]",
                                      "V": "the good golfer's planned tee line and the ace line roll through it",
                                      "VI": "centre of the 15-wide lane mouth, the only approach into the dial"})
H17_STONE_RAIL = ("XII", "III", "IX")
_roman = ["XII", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI"]
h.d["hour_stones"] = dict(ring_center=[H17_C[0], 0, H17_C[1]], ring_radius=H17_STONE_R, size=list(H17_STONE), stones=[],
                          note="XII toward local -Z, clockwise seen from above (III toward +X). Centre y = half-height .4 (stone sits on the felt, top .8).")
for k, hr in enumerate(_roman):
    a = math.radians(30 * k)
    c = [r4(H17_C[0] + H17_STONE_R * math.sin(a)), H17_STONE[1] / 2, r4(H17_C[1] - H17_STONE_R * math.cos(a))]
    rec = dict(hour=hr, center=c, size=list(H17_STONE))
    if hr in H17_STONE_DROP:
        rec.update(placed=False, dropped=H17_STONE_DROP[hr])
    elif hr in H17_STONE_RAIL:
        rec.update(placed=True, collidable=True, ball_collision=True, rail_mounted=True,
                   note="Footprint reaches .1 over the rail inner face: rail-mounted solid stone, collision on (static bumper block)")
        h.block(f"hour_stone_{hr}", c[0], c[2], H17_STONE[0], H17_STONE[2], 0.0, height=H17_STONE[1], ybot=0.0, hour_stone=hr)
    else:
        rec.update(placed=True, collidable=False, ball_collision=False, rail_mounted=False)
    h.d["hour_stones"]["stones"].append(rec)
    if rec["placed"]:
        h.anchor(f"hour_stone_{hr}", c, f"Candy-coloured hour stone '{hr}' (roman numeral on top), {H17_STONE[0]:g} x {H17_STONE[1]:g} x {H17_STONE[2]:g}, "
                 + ("rail-mounted, collision ON (holes.json static block)" if rec["collidable"] else "decorative, collision OFF"),
                 size=list(H17_STONE), exact_box=dict(center=c, size=list(H17_STONE), yaw=0, collidable=rec["collidable"],
                                                     ball_collision=rec["ball_collision"]))
h.anchor("hour_stones", [H17_C[0], 0, H17_C[1]], f"Hour-stone ring (radius {H17_STONE_R:g}, outside the 11.5 arm sweep): "
         f"{sum(s['placed'] for s in h.d['hour_stones']['stones'])} placed stones, exact boxes in the hour_stone_* anchors and hole.hour_stones; "
         "dropped (not built): " + "; ".join(f"{q['hour']} at {q['center']} ({q['dropped']})" for q in h.d["hour_stones"]["stones"] if not q["placed"]), size=[2 * H17_STONE_R + 1.2, 0.8, 2 * H17_STONE_R + 1.2])
holes.append(h)

# ================================================================ H18 Sunset Arch (par 4): finale
# Lane north into a junction; a banked NE corner turns the ball west past a hoodoo, a banked NW corner turns it north up the ramp under
# the arch onto the plateau. The geode (teleport shortcut) sits in the plateau straight up the ramp line; past it, the rim lane runs
# north to the cliff-edge green.
H18_CUP = K("h18_cup", [8.0, 0.8, -64.0])
H18_GEO = K("h18_geode", [-9.5, 0.8, -32.0])
H18_GR = K("h18_geode_r", 0.55)
H18_EXIT = K("h18_exit", [13.0, 0.8, -59.0])
H18_HOO = K("h18_hoodoo", [0.0, -11.0])
H18_RISE = 0.8
h = new_hole(18, "h18", "Sunset Arch", 4, "A natural candy-striped stone arch over the ramp, the great Sunset Arch on the rim beyond",
             "Finale: bank round a hoodoo, ramp up under the arch, then a geode-shortcut teleport or the rim route to a cliff-edge green")
h.rect("lane", -4, 4, 2, -14, 0.0, zone="lane")
h.rect("junction", -12, 4, -14, -22, 0.0, zone="junction")
h.rect("ramp", -12, -6, -22, -30, zone="ramp", slope=("z", 0.0, H18_RISE))
h.rect("plateau", -12, -2, -30, -40, H18_RISE, zone="plateau")
h.rect("rim", -12, -6, -40, -56, H18_RISE, zone="rim")
h.rect("green", -12, 14, -56, -70, H18_RISE, zone="green")
y = H18_RISE
h.wall_path([(-4, 2), (-4, -14), (-12, -14), (-12, -70), (14, -70), (14, -56), (-6, -56), (-6, -40), (-2, -40), (-2, -30), (-6, -30), (-6, -22),
             (4, -22), (4, 2)], [0, 0, 0, y, y, y, y, y, y, y, y, 0, 0, 0], out="L", closed=True, top=y + 2.4)
h.block("hoodoo", H18_HOO[0], H18_HOO[1], 1.6, 1.6, 0.0, height=2.0, yaw=45.0)
h.bank_wall("bank_ne", (4.0, -16.5), (-1.5, -22.0), "R", zone="junction", ext_bank=0.3, ext_back=0.6)
h.bank_wall("bank_nw", (-12.0, -16.5), (-8.5, -22.0), "L", zone="junction", ext_bank=0.3, ext_back=0.6)
h.bank_wall("bank_green", (-12.0, -65.0), (-7.0, -70.0), "L", base_y=y, zone="green", ext_bank=0.3, ext_back=0.6)
gdir = (H18_CUP[0] - H18_EXIT[0], H18_CUP[2] - H18_EXIT[2])
h.teleport("geode", H18_GEO, H18_GR, H18_EXIT, K("h18_exit_dir", gdir), speed_factor=K("h18_sf", 0.7), min_speed=K("h18_vmin", 1.5),
           max_speed=K("h18_vmax", 7.0), visual="Cracked-open amethyst-and-rock-candy geode set in the plateau felt straight up the ramp line "
                                                "(entry) -> twin geode on the cliff-edge green (exit), aimed at the cup")
h.tee(0, 0, 0)
h.cup(*H18_CUP, flag_h=7.5)
h.d["cup_from"] = ["green"]
h.wp("all", "ne_bank", [K("h18_wp1_x", 3.0), 0.0, -20.5], ["lane"], carry=K("h18_c1", 8.0))
h.wp("all", "junction_w", K("h18_jw", [-5.0, 0.0, -18.0]), ["junction"], carry=K("h18_c2", 2.0))
h.wp("all", "plateau", [-9.0, y, -32.5], ["junction", "ramp"], carry=K("h18_c3", 4.0), power_scale=K("h18_ps3", 1.4))
h.wp("good", "ne_bank", [K("h18_wp1_x", 3.0), 0.0, -20.5], ["lane"], carry=K("h18_c1", 8.0))
h.wp("good", "junction_w", K("h18_jw", [-5.0, 0.0, -18.0]), ["junction"], carry=K("h18_c2", 2.0))
h.wp("good", "plateau", [-9.0, y, -32.5], ["junction", "ramp"], carry=K("h18_c3", 4.0), power_scale=K("h18_ps3", 1.4))
h.wp("good", "geode", H18_GEO, ["plateau"], carry=K("h18_geo_carry", 0.8))
h.wp("good", "rim_top", [-9.0, y, -57.5], ["rim"], carry=K("h18_c4", 4.0))
h.wp("average", "ne_bank", [K("h18_wp1_x", 3.0), 0.0, -20.5], ["lane"], carry=K("h18_c1", 8.0))
h.wp("average", "junction_w", K("h18_jw", [-5.0, 0.0, -18.0]), ["junction"], carry=K("h18_c2", 2.0))
h.wp("average", "plateau", [-9.0, y, -32.5], ["junction", "ramp"], carry=K("h18_c3", 4.0), power_scale=K("h18_ps3", 1.4))
h.wp("average", "rim_top", [-9.0, y, -57.5], ["plateau", "rim"], carry=K("h18_c4", 4.0))
h.anchor("arch_gate", [-9, 0, -26], "Natural candy-striped sandstone arch spanning the ramp (feet outside the rails at x -13.25 and -4.75, opening 7.5 wide x "
         "10 high), framing the sunset to the west", landmark=True, size=[10, 13, 4],
         occluders=[((-13.25, 6, -26), (1.5, 12, 3)), ((-4.75, 6, -26), (1.5, 12, 3)), ((-9.0, 11.5, -26), (10, 2, 3))])
h.anchor("hoodoo_deco", [H18_HOO[0], 0, H18_HOO[1]], "Striped hoodoo with a gumdrop cap on the 1.6 bumper (turned 45) at the end of the tee lane: "
         "play round it into the banked corner", size=[2.2, 10, 2.2], occluders=[((H18_HOO[0], 5, H18_HOO[1]), (1.6, 10, 1.6), 45.0)])
h.anchor("geode_entry", H18_GEO, f"Cracked geode bowl flush in the plateau felt, glowing violet (trigger radius {H18_GR:g})", size=[1.6, 0.3, 1.6])
h.anchor("geode_exit", H18_EXIT, "Twin geode on the green's east side (teleport exit)", size=[1.6, 0.6, 1.6])
h.anchor("cliff_edge", [0, y, -70], "Cliff-edge rope railing on carved posts along the green's north and east rails; the Crown drops away to the "
         "canyon beyond (the sunset view)", size=[26, 2, 1])
sign(h, "sign_rim", (-12.6, y, -42), "Sign 'Rim Trail' pointing north along the rim", (0.3, -1))
felt_arrow(h, "felt_arrow_bank", [1.0, 0.0, -10.0], "Glowing felt arrow decal curving right-then-left: 'bank it round the hoodoo'", size=(2.0, 0.01, 2.6))
holes.append(h)

# ---------------------------------------------------------------- course
course = {
    "course": "Sugarloaf Canyon",
    "schema": SCHEMA,
    "physics": {"source": "the builder's real game values (measured for Lantern Grove; mirrored as constants in tools/sim.py)",
                "stud_m": S.STUD_M, "gravity_studs_s2": S.GRAVITY,
                "rolling_decel": "0.5 + 0.25*speed studs/s^2", "rolling_decel_const": S.ROLL_DECEL_CONST,
                "rolling_decel_per_speed": S.ROLL_DECEL_PER_SPEED, "wall_restitution": S.WALL_RESTITUTION,
                "bumper_restitution": S.BUMPER_RESTITUTION, "cup_capture_speed_studs_s": S.CUP_CAPTURE_SPEED,
                "cup_radius": S.CUP_RADIUS, "ball_radius": S.BALL_RADIUS, "max_putt_speed_studs_s": S.V_MAX,
                "max_putt_flat_roll_studs": S.MAX_PUTT_STUDS,
                "max_putt_note": "V_MAX derived so a full putt rolls 60 studs (18 m) on flat felt",
                "drop_speed_keep": 0.8},
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
    return bad


# 2026-10-13 decoration clearance pass (tools/deco_clearance.py): free-standing dressing props are nudged the least XZ distance
# that leaves 0.15 studs to every rail/wall, the felt head room (felt-0.4..+8) and other props. Visual anchors only; play geometry untouched.
from deco_clearance import settle as _deco_settle
DECO_SETTLE = [(2, "sign_left"), (2, "sign_right"), (3, "sign_plank"), (3, "sign_bridge"), (6, "sign_overflow"),
         (9, "sign_bypass"), (12, "sign_pier"), (12, "sign_shore"), (13, "sign_west"), (13, "sign_centre"), (13, "sign_east"), (18, "sign_rim"),
         (1, "trailhead_arch"), (11, "lock_keeper_hut"), (14, "ore_piles"), (14, "cableway_trestle"), (18, "arch_gate"), (9, "water_tank"),
         (6, "bell_tower"), (6, "flood_marks"),]
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
