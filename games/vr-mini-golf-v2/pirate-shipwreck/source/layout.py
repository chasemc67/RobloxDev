"""Shared layout definitions for the Pirate Shipwreck blockout (world only, no holes).

Frame: studs. X east, Y up, Z south (map y grows downward). Origin = centre of the
819x461 map image from /workspace/gameart/pirate-shipwreck/r1/raw/map_base1.png.
"""
import math
import numpy as np

MAP_W, MAP_H = 819, 461           # map_base1.png resized to this (same frame as make_map.py pad coords)
S = 3.0                           # studs per map pixel (see README: why 3)
CX, CZ = MAP_W / 2, MAP_H / 2     # map px of the world origin

# terrain grid: 1 cell = 4 studs (AGENTS.md 6b: 1 px = 4 studs)
CELL = 4
GW, GH = 1024, 640
X0, Z0 = -(GW * CELL) // 2, -(GH * CELL) // 2     # -2048, -1280 (world coords of grid corner)
MINY = -36                         # lowest voxel layer bottom
LAYERS = 42                        # top = MINY + 4*LAYERS = 132
HMIN, HMAX = -40.0, 150.0          # 16-bit heightmap range (studs)
WATER_Y = 0.0

def px2w(x, y):
    return ((x - CX) * S, (y - CZ) * S)

def w2px(X, Z):
    return (X / S + CX, Z / S + CZ)

# (n, zone, map px x, map px y) -- from make_map.py (Game Art Bot)
PADS_PX = [(1,'wreck',230,310),(2,'wreck',283,312),(3,'wreck',377,334),(4,'wreck',469,347),
(5,'beach',560,358),(6,'beach',656,369),(7,'beach',721,343),(8,'beach',713,276),(9,'beach',654,211),
(10,'jungle',541,284),(11,'jungle',470,227),(12,'jungle',367,199),(13,'jungle',287,172),(14,'jungle',211,107),
(15,'cave',290,47),(16,'cave',446,59),(17,'cave',541,114),(18,'cave',604,70)]
REST_PX = [(1,199,45),(2,360,73),(3,620,156)]

# felt-top elevation (studs above water level 0) per pad
PAD_ELEV = {1:24.0, 2:4.5,3:4.5,4:4.5,5:4.5,6:4.5,7:4.5,8:4.5,9:4.5,
            10:8,11:11,12:14,13:18,14:24,15:40,16:54,17:72,18:90}

# v9: ground raise under each pad (studs). The felt top is PAD_ELEV + PAD_RAISE; the trail corridor stays at PAD_ELEV (the pad stands as a plinth).
# v10: pad 1 (wreck deck) gets a 3 stud wooden plinth on the deck and pad 18 a 4 stud slate plinth on the cave plateau (the stair ramp stays at the old height, so the plinth edge is the drop-off).
PAD_RAISE = {1:3.0, 2:4.5, 3:5.5, 4:4.5, 5:6.5, 6:4.5, 7:5.5, 8:6.5, 9:4.5,
             10:5.5, 11:4.5, 12:6.5, 13:5.5, 14:4.5, 15:4.5, 16:5.5, 17:4.5, 18:4.0}
# Roblox renders flat voxel terrain about 1.97 studs above the heightmap value, so the plateau is written at PAD_TOP - PLATEAU_BELOW to put the
# rendered ground about 0.5 under the felt top. The trail corridor (written at elev - 1) renders at about elev + 1, so the net raise over the old
# pad ground is PAD_RAISE - 1.5 = 3 to 5 studs.
PLATEAU_BELOW = 2.5
PAD_TOP = {n: PAD_ELEV[n] + PAD_RAISE[n] for n in PAD_ELEV}

# pad geometry (studs)
FELT = (30.0, 60.0)               # width x length (length runs along the trail)
RIM = 4.0                         # rim width (handoff: 3-4 studs)
OUTER = (FELT[0] + 2*RIM, FELT[1] + 2*RIM)      # 38 x 68
ART_CLEAR = 8.0                   # empty space around each pad (handoff)
CLEAR = (OUTER[0] + 2*ART_CLEAR, OUTER[1] + 2*ART_CLEAR)   # 54 x 84
REST_SIZE = 40.0                  # rest-stop clearing, square

# trail polyline (Catmull-Rom through pad centres, map px)
def catmull(pts, per=24):
    ext = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(ext) - 2):
        p0, p1, p2, p3 = ext[i-1], ext[i], ext[i+1], ext[i+2]
        for k in range(per):
            t = k / per
            out.append(tuple(0.5*((2*p1[c]) + (-p0[c]+p2[c])*t + (2*p0[c]-5*p1[c]+4*p2[c]-p3[c])*t*t
                               + (-p0[c]+3*p1[c]-3*p2[c]+p3[c])*t**3) for c in range(2)))
    out.append(pts[-1])
    return out

def pad_pos_w():
    return {n: px2w(x, y) for n, z, x, y in PADS_PX}

# wreck (room decision, wreck v2 mesh): 320 long x 90 wide x 60 tall, mast tip about Y 161. Ship axis ~15 deg off east (from map).
# Stern toward the beach, bow (duck) toward the lagoon. Local frame: Y 0 water line, X 0 centreline, Z 0 midship, +Z bow.
WRECK_AXIS = np.array([0.965, 0.262]); WRECK_AXIS /= np.linalg.norm(WRECK_AXIS)   # bow -> stern, world (X,Z)
WRECK_LEN, WRECK_WID, HULL_H, MAST_H = 320.0, 90.0, 60.0, 161.0
MAST_H_V2 = 138.8                 # actual main mast tip of wreck_v2 (manifest); 161 was the v1 / room-decision figure
WRECK_STERN_Z = 160.0             # stern end is at local z = -160 (hull bbox z -160.2 .. 166.4)
PAD1_LOCAL_Z = -110.0             # pad 1 deck centre, local (0, 24, -110): 54 x 84 flat deck, top Y 24
PAD1_FROM_STERN = 50.0            # pad 1 centre is this far from the stern end, along the ship

# cave cliff stand-in
CLIFF_W, CLIFF_D, CLIFF_H = 240.0, 140.0, 150.0
CLIFF_FRONT_GAP = 55.0            # cliff front face sits this far north of pad 18's centre
CLIFF_BASE_Y = 66.0
MOUTH_W, MOUTH_H = 40.0, 60.0     # cave v1 mouth: 40 wide, arch apex 60 above its floor (floor world Y 94). Cave v2 mouth will be ~1.5x bigger, same floor.
CAVE_MOUTH_FLOOR_Y = 94.0

def rect_corners(cx, cz, w, l, yaw_deg):
    """corners of a w (local X) x l (local Z) rect rotated like CFrame.Angles(0, yaw, 0)."""
    th = math.radians(yaw_deg)
    ax = np.array([math.cos(th), -math.sin(th)])     # local +X in world (X,Z)
    az = np.array([math.sin(th), math.cos(th)])      # local +Z in world (X,Z)
    c = np.array([cx, cz])
    return [c + sx*w/2*ax + sz*l/2*az for sx, sz in ((-1,-1),(1,-1),(1,1),(-1,1))]

def sat_overlap(a, b):
    for poly in (a, b):
        for i in range(4):
            e = poly[(i+1) % 4] - poly[i]
            n = np.array([-e[1], e[0]])
            pa = [p @ n for p in a]; pb = [p @ n for p in b]
            if max(pa) < min(pb) or max(pb) < min(pa):
                return False
    return True
