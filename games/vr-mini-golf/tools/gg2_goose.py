#!/usr/bin/env python3
"""Stage gg2 (renumbered in gg3): the hidden Lantern Grove "Bonus Hole 10: The Goose" (a goose seen from above), built procedurally.

  uv run --with shapely python3 tools/gg2_goose.py            # write the spec + the Luau module, print checks
  uv run --with shapely python3 tools/gg2_goose.py --png      # ...and render h10-layout.png (needs pillow)

Writes
  assets/vr-mini-golf/lantern-grove/holes-bonus-h10.json   (holes.json schema, one hole, number 10, bonus = true)
  src/ServerStorage/CourseData/LanternGroveBonus.luau      (holes_to_lua.convert of that spec + world placement)

Geometry (hole-local studs, tee at the origin, head toward -Z "north", tail south):
  outline  = union(body ellipse, wing bulges, tail, S-curved neck band, head ellipse, beak), smoothed in shapely
  rails    = one 0.5-thick wall per outline edge, OUTSIDE the felt (inner face on the edge), lengthened at convex
             corners so the outer faces close
  felt     = axis-aligned rectangles only (no overlapping rotated felt: fx1 seams): a 0.25 grid of the cells touching
             the outline grown by 0.1, merged greedily into large rectangles per zone; every cell stays under the rail band
  zones    = constant-z cuts (body | neck | head | beak); all flat (BEAK_RISE 0), the beak felt is orange
  cup      = the goose's right eye, in its own 3.0 x 3.0 flat felt block
The 9-hole holes.json / LanternGrove.luau are not touched.
"""
import argparse
import json
import math
import os
import sys

from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(GAME))
ASSETS = os.path.join(REPO, "assets", "vr-mini-golf", "lantern-grove")
OUT = os.path.join(GAME, "src", "ServerStorage", "CourseData", "LanternGroveBonus.luau")

# The hole number: Lantern Grove has 9 holes, so the goose is "Bonus Hole 10" (stage gg3; gg2 called it 19). It is not
# part of the round (Courses.holes skips Bonus holes); players see "Bonus Hole 10: The Goose". This is the one constant.
NUMBER = 10
NAME = "The Goose"
SPEC = os.path.join(ASSETS, "holes-bonus-h%02d.json" % NUMBER)
# World placement: a cloud island above the Grandmother Tree's crown (crown y 137..218, sky lanterns <= y 263),
# head north. Nothing else in the place sits above y 263 here.
ORIGIN = [-74.0, 300.0, 34.0]
YAW = 0.0

G = 0.25  # felt grid (studs)
COVER = 0.1  # cells touch the outline grown by this: felt edges sit >= 0.1 outside it (> the 0.08 skin inset),
# and stick out <= COVER + G*sqrt(2) = 0.45 < the 0.5 rail band
RAIL_T = 0.5
RAIL_UP = 1.0  # rail top above the felt it borders (schema)
RAIL_DOWN = 0.6  # collider reaches this far below the felt top
BEAK_CUT, HEAD_CUT, NECK_CUT = -64.5, -55.5, -22.0  # zone cuts (multiples of G)
BEAK_RISE = 0.0  # flat beak (a 0.22 tilt left visible skin notches at the flat/sloped joint; a ball resting in the beak is a 4-stud putt)
CUP = (2.0, -61.0)  # the right eye
CUP_BLOCK = 3.0
NECK_A, NECK_W = 3.9, 6.0  # S-neck amplitude, lane width


def ellipse(cx, cz, a, b, rot=0.0):
    e = affinity.scale(Point(0, 0).buffer(1.0, quad_segs=32), a, b)
    if rot:
        e = affinity.rotate(e, rot, origin=(0, 0))
    return affinity.translate(e, cx, cz)


def neck_x(z):
    return NECK_A * math.sin(2 * math.pi * (-z - 20.0) / 36.0)


def outline():
    body = ellipse(0, -10, 11, 13)
    wings = [ellipse(8.2, -11.5, 4.6, 9.5, -8), ellipse(-8.2, -11.5, 4.6, 9.5, 8)]
    tail = Polygon([(-6.5, -2.0), (6.5, -2.0), (1.6, 9.2), (-1.6, 9.2)])
    zs = [-18.0 - i * 0.25 for i in range(int((58.5 - 18.0) / 0.25) + 1)]
    neck = LineString([(neck_x(z), z) for z in zs]).buffer(NECK_W / 2, quad_segs=16)
    head = ellipse(0, -60, 5.0, 4.6)
    beak = Polygon([(-1.95, -63.0), (1.95, -63.0), (1.15, -71.2), (-1.15, -71.2)])
    p = unary_union([body, *wings, tail, neck, head, beak])
    p = p.buffer(1.2, quad_segs=16).buffer(-1.2, quad_segs=16)  # close: round the concave joins
    p = p.buffer(-0.8, quad_segs=16).buffer(0.8, quad_segs=16)  # open: round the convex tips
    p = p.simplify(0.04, preserve_topology=True)
    return Polygon(p.exterior.coords)


def merge_short(coords, min_len=0.7):
    """Drop vertices so no edge is shorter than min_len (keeps the shape within a few hundredths)."""
    pts = list(coords[:-1])
    changed = True
    while changed:
        changed = False
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            if math.dist(a, b) < min_len and len(pts) > 8:
                c = pts[(i + 2) % len(pts)]
                # remove b if the triangle a-b-c is thin, else merge a-b at the midpoint
                pts.pop((i + 1) % len(pts))
                changed = True
                break
    return pts + [pts[0]]


def beak_k():
    return BEAK_RISE / (71.4 + BEAK_CUT)  # height gain per stud north of the cut


def height_at(z):
    return beak_k() * (BEAK_CUT - z) if z < BEAK_CUT else 0.0


def zone_of(z):
    if z < BEAK_CUT:
        return "beak"
    if z < HEAD_CUT:
        return "head"
    if z < NECK_CUT:
        return "neck"
    return "body"


def rails(poly):
    ring = list(poly.exterior.coords)
    if not Polygon(ring).exterior.is_ccw:
        ring = ring[::-1]
    ring = merge_short(ring)
    n = len(ring) - 1
    out = []
    pts = ring[:-1]
    # CCW in (x, z) with z drawn "up"... interior is to the LEFT of each edge in the (x, z) plane
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        prev, nxt = pts[i - 1], pts[(i + 2) % n]
        dx, dz = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dz)
        ux, uz = dx / L, dz / L
        nx, nz = uz, -ux  # right of the edge = outside for a CCW ring

        def turn(p, q, r):
            v1 = (q[0] - p[0], q[1] - p[1])
            v2 = (r[0] - q[0], r[1] - q[1])
            cr = v1[0] * v2[1] - v1[1] * v2[0]
            ang = math.atan2(cr, v1[0] * v2[0] + v1[1] * v2[1])
            return ang  # > 0: left turn = convex corner of a CCW ring

        e0 = e1 = 0.0
        t0 = turn(prev, a, b)
        t1 = turn(a, b, nxt)
        if t0 > 0:
            e0 = RAIL_T * math.tan(min(abs(t0), 1.3) / 2)
        if t1 > 0:
            e1 = RAIL_T * math.tan(min(abs(t1), 1.3) / 2)
        s0, s1 = -e0, L + e1
        mid = (s0 + s1) / 2
        cx = a[0] + ux * mid + nx * RAIL_T / 2
        cz = a[1] + uz * mid + nz * RAIL_T / 2
        fh = max(height_at(a[1]), height_at(b[1]))
        top, bot = fh + RAIL_UP, -RAIL_DOWN
        yaw = math.degrees(math.atan2(ux, uz))
        out.append({
            "id": "goose_rail%d" % (i + 1),
            "center": [round(cx, 4), round((top + bot) / 2, 4), round(cz, 4)],
            "size": [RAIL_T, round(top - bot, 4), round(s1 - s0, 4)],
            "yaw": round(yaw, 3),
            "_quad": [(a[0] + ux * s0, a[1] + uz * s0), (a[0] + ux * s1, a[1] + uz * s1),
                      (a[0] + ux * s1 + nx * RAIL_T, a[1] + uz * s1 + nz * RAIL_T), (a[0] + ux * s0 + nx * RAIL_T, a[1] + uz * s0 + nz * RAIL_T)],
        })
    return out, Polygon(ring)


def largest_rect(grid, rows, cols):
    """Largest all-true axis rectangle (histogram method). Returns (area, r0, r1, c0, c1) inclusive-exclusive."""
    best = (0, 0, 0, 0, 0)
    h = [0] * cols
    for r in range(rows):
        row = grid[r]
        for c in range(cols):
            h[c] = h[c] + 1 if row[c] else 0
        stack = []
        for c in range(cols + 1):
            cur = h[c] if c < cols else 0
            start = c
            while stack and stack[-1][1] >= cur:
                s, hh = stack.pop()
                area = hh * (c - s)
                if area > best[0]:
                    best = (area, r - hh + 1, r + 1, s, c)
                start = s
            stack.append((start, cur))
    return best


def felt_pieces(poly, rail_union):
    x0, x1 = math.floor(poly.bounds[0] / G) - 1, math.ceil(poly.bounds[2] / G) + 1
    z0, z1 = math.floor(poly.bounds[1] / G) - 1, math.ceil(poly.bounds[3] / G) + 1
    cols, rows = x1 - x0, z1 - z0
    cover = poly.union(rail_union)
    grown = poly.buffer(COVER, quad_segs=16)
    inside = [[False] * cols for _ in range(rows)]
    bad = 0
    for r in range(rows):
        for c in range(cols):
            cell = box((x0 + c) * G, (z0 + r) * G, (x0 + c + 1) * G, (z0 + r + 1) * G)
            if cell.intersection(grown).area > 1e-6:
                inside[r][c] = True
                if cell.difference(cover).area > 1e-5:
                    bad += 1
    # the cup block: its own flat piece
    cb = (CUP[0] - CUP_BLOCK / 2, CUP[1] - CUP_BLOCK / 2, CUP[0] + CUP_BLOCK / 2, CUP[1] + CUP_BLOCK / 2)
    cc0, cc1 = round(cb[0] / G) - x0, round(cb[2] / G) - x0
    cr0, cr1 = round(cb[1] / G) - z0, round(cb[3] / G) - z0
    assert abs((cc0 + x0) * G - cb[0]) < 1e-6 and abs((cr0 + z0) * G - cb[1]) < 1e-6, "cup block not on the grid"
    pieces = []
    for r in range(cr0, cr1):
        for c in range(cc0, cc1):
            assert inside[r][c]
            inside[r][c] = False
    pieces.append(("cup", cr0, cr1, cc0, cc1))
    cuts = sorted(round(v / G) - z0 for v in (BEAK_CUT, HEAD_CUT, NECK_CUT))
    bands = [(0, cuts[0]), (cuts[0], cuts[1]), (cuts[1], cuts[2]), (cuts[2], rows)]
    for b0, b1 in bands:
        sub = [inside[r][:] for r in range(b0, b1)]
        while True:
            area, r0, r1, c0, c1 = largest_rect(sub, b1 - b0, cols)
            if area == 0:
                break
            for r in range(r0, r1):
                for c in range(c0, c1):
                    sub[r][c] = False
            pieces.append(("", r0 + b0, r1 + b0, c0, c1))
    felt = []
    counts = {}
    for tag, r0, r1, c0, c1 in pieces:
        xa, xb = (x0 + c0) * G, (x0 + c1) * G
        za, zb = (z0 + r0) * G, (z0 + r1) * G
        zc, xc = (za + zb) / 2, (xa + xb) / 2
        zone = zone_of(zc)
        counts[zone] = counts.get(zone, 0) + 1
        d = {"id": "cup_eye" if tag == "cup" else "%s%d" % (zone, counts[zone]), "zone": zone,
             "center": [round(xc, 4), round(height_at(zc), 4), round(zc, 4)],
             "size": [round(xb - xa, 4), round(zb - za, 4)], "yaw": 0.0, "slope": None}
        if zone == "beak":
            if BEAK_RISE:
                d["slope"] = {"axis": "z", "rise": round(-beak_k() * (zb - za), 5)}
            d["color"] = "#FFA33B"
        else:
            d["color"] = GOOSE_FELT
        felt.append(d)
    union = unary_union([box(f["center"][0] - f["size"][0] / 2, f["center"][2] - f["size"][1] / 2,
                             f["center"][0] + f["size"][0] / 2, f["center"][2] + f["size"][1] / 2) for f in felt])
    return felt, union, bad


GOOSE_FELT = "#D8E4B0"  # pale cream-green goose body (reads white from above, the white ball still shows)


def decor_parts(poly):
    """Visual-only primitives (no collision/query/touch): the cloud the goose stands on, its two orange feet, a few
    golden sky lanterns. Hole-local; y = part centre."""
    out = []
    minx, minz, maxx, maxz = poly.bounds
    lawn = -1.5  # CourseBuilder lawnTopLocal (felt min - 1.5): rails and bases end here
    top = lawn - 0.08
    m = 5.0
    out.append({"name": "Cloud", "shape": "Block", "center": [(minx + maxx) / 2, top - 1.5, (minz + maxz) / 2 + 1.0],
                "size": [maxx - minx + 2 * m, 3.0, maxz - minz + 2 * m + 2.0], "color": "#F4F6FA", "material": "SmoothPlastic"})
    # puffs: spheres around and under the slab edge, all below the slab top so nothing pokes up beside the rails
    import random
    rnd = random.Random(19)
    cx0, cx1 = minx - m, maxx + m
    cz0, cz1 = minz - m, maxz + m + 2.0
    k = 0
    for side in range(4):
        for i in range(6):
            t = (i + 0.5) / 6
            if side == 0:
                x, z = cx0 + (cx1 - cx0) * t, cz0
            elif side == 1:
                x, z = cx0 + (cx1 - cx0) * t, cz1
            elif side == 2:
                x, z = cx0, cz0 + (cz1 - cz0) * t
            else:
                x, z = cx1, cz0 + (cz1 - cz0) * t
            d = rnd.uniform(7, 12)
            k += 1
            out.append({"name": "CloudPuff", "shape": "Ball", "center": [round(x, 2), round(top - 0.6 - d / 2, 2), round(z, 2)],
                        "size": [round(d, 2)] * 3, "color": "#FFFFFF", "material": "SmoothPlastic"})
    for i in range(8):
        x, z = rnd.uniform(cx0 + 4, cx1 - 4), rnd.uniform(cz0 + 6, cz1 - 6)
        d = rnd.uniform(12, 18)
        out.append({"name": "CloudPuff", "shape": "Ball", "center": [round(x, 2), round(top - 2.5 - d / 2, 2), round(z, 2)],
                    "size": [round(d, 2)] * 3, "color": "#FFFFFF", "material": "SmoothPlastic"})
    # webbed feet: three toes + web, orange, lying on the cloud beside the tail (outside the rails)
    # (tops staggered 0.085 apart where pieces overlap: web, side toes, middle toe; bottoms sunk 0.02 into the cloud)
    for sx in (-1, 1):
        fx, fz = sx * 9.6, 4.6
        y = top + 0.08
        for ang in (-28, 0, 28):
            a = math.radians(ang)
            out.append({"name": "GooseToe", "shape": "Block", "center": [round(fx + math.sin(a) * 1.1 * sx, 3), round(y + (0.17 if ang == 0 else 0.085), 3),
                        round(fz + math.cos(a) * 1.1, 3)], "size": [0.35, 0.2, 2.2], "yaw": ang * sx, "color": "#FFA33B", "material": "SmoothPlastic"})
        out.append({"name": "GooseWeb", "shape": "Block", "center": [fx, round(y, 3), fz + 0.9], "size": [1.6, 0.2, 1.3],
                    "color": "#E8862E", "material": "SmoothPlastic"})
    return out


def secret():
    """Hole 9 secret (H9 hole-local studs, spec frame of holes.json h09): golden goose footprints from the tee up the
    lane, across the landing and the corridor's north side (away from the Lantern Knot at (6.5, -23), which sits by the
    south rail), then north-east through the chamber, parallel to the root deflector, to the chamber's north-east
    corner by rail12. Below that cliff, in the heart green's south-east pocket (rail12 / rail16 / rail15), sits the
    golden egg: the trigger. All flat felt except the egg pocket (heart_slope). [x, y, z, walk yaw] (180 = north)."""
    prints = []
    # lane (y 0): beside the tee, walking north on the east half
    for i in range(6):
        prints.append([2.1 + (0.32 if i % 2 else -0.32), 0.0, -1.6 - i * 1.45, 180])
    # landing (y 1.0): up from the ramp top, then turning east along the corridor's north side (z -27.6)
    prints += [[2.2, 1.0, -23.2, 180], [2.75, 1.0, -24.6, 180], [3.4, 1.0, -27.3, 120], [4.9, 1.0, -27.9, 90],
               [6.3, 1.0, -27.3, 90], [7.6, 1.0, -27.9, 90]]
    # chamber (y 1.0): from the tunnel mouth north-east (parallel to the deflector) to the corner by rail12
    a = math.radians(135)  # walk direction in hole-local (sin, cos) = (0.71, -0.71): north-east
    x0, z0 = 15.4, -28.2
    for i in range(9):
        t = i * 1.45
        side = 0.3 if i % 2 else -0.3
        prints.append([round(x0 + math.sin(a) * t + math.cos(a) * side * -1, 3), 1.0,
                       round(z0 + math.cos(a) * t + math.sin(a) * side, 3), 135])
    prints += [[25.0, 1.0, -37.4, 120], [26.4, 1.0, -38.3, 110], [27.7, 1.0, -38.9, 100], [28.9, 1.0, -39.3, 95]]
    feathers = [[29.2, 1.0, -37.4, 60], [30.9, -0.8, -45.9, 20]]
    return {
        "hole": 9,
        "print_color": "#C9A14A",  # muted gold, no glow (subtle on H9's dark felt)
        "feather_color": "#F4E9D2",
        "prints": prints,
        "feathers": feathers,
        # the egg: trigger in the pocket's corner (ball centre within radius), the visual egg tucked behind it
        "egg": {"trigger": [31.3, -0.55, -40.7], "radius": 0.42, "pos": [31.55, -0.5, -40.4], "size": [0.6, 0.8, 0.6],
                "color": "#E8A92B"},
        # where the ball comes back after the goose: flat heart felt beside the pocket (no penalty, H9 strokes kept)
        "return_pos": [29.6, -0.8, -47.0],
    }


def build(png=False):
    poly = outline()
    rl, poly = rails(poly)
    rail_union = unary_union([Polygon(r["_quad"]) for r in rl])
    felt, felt_union, bad = felt_pieces(poly, rail_union)
    # checks
    uncovered = poly.difference(felt_union).area
    outside = felt_union.difference(poly.union(rail_union)).area
    rail_in = rail_union.intersection(poly.buffer(-0.01)).area
    cupd = poly.exterior.distance(Point(CUP))
    minx, minz, maxx, maxz = poly.bounds
    # narrowest lane: smallest inscribed width along the neck centreline
    neck_min = min(poly.exterior.distance(Point(neck_x(z), z)) for z in [-24 - i * 0.5 for i in range(60)]) * 2
    beak_w = min(poly.exterior.distance(Point(0, z)) for z in [-68.5, -69.5]) * 2
    checks = {
        "outline_area": round(poly.area, 1), "length": round(maxz - minz, 2), "width": round(maxx - minx, 2),
        "bounds_x": [round(minx, 2), round(maxx, 2)], "bounds_z": [round(minz, 2), round(maxz, 2)],
        "felt_pieces": len(felt), "rails": len(rl), "cells_outside_rails": bad,
        "uncovered_area": round(uncovered, 5), "felt_outside_rail_band": round(outside, 5),
        "rail_inside_felt_area": round(rail_in, 5), "cup_clearance": round(cupd, 3),
        "neck_min_width": round(neck_min, 2), "beak_width_near_tip": round(beak_w, 2),
        "min_felt_dim": min(min(f["size"]) for f in felt),
    }
    tee = {"position": [0, 0, 0], "aim_hint": [0, -1], "sign": [-9.0, 7.5]}
    hole = {
        "number": NUMBER, "id": "h%02d" % NUMBER, "name": NAME, "par": 3, "bonus": True,
        "zone": "Goose Cloud (hidden)",
        "landmark": "A goose seen from above, on a cloud above the Grandmother Tree",
        "gimmick": "Long S-curved neck: bank through two bends to the head; the cup is the goose's eye",
        "world_offset": ORIGIN, "world_yaw": YAW,
        "tee": tee,
        "cup": {"position": [CUP[0], 0.0, CUP[1]], "radius": 0.5,
                "flag": {"pole_height": 7.5, "pole_diameter": 0.15, "banner_size": [2.0, 1.2, 0.05], "banner_color": "#e03c31",
                         "top": [CUP[0], 7.5, CUP[1]], "collision": False}},
        "felt": felt,
        "walls": [{k: v for k, v in r.items() if not k.startswith("_")} for r in rl],
        "hazards": [], "drops": [], "moving_parts": [], "teleports": [],
        "ai_waypoints": {"all": [
            {"id": "neck_base", "pos": [0.0, 0.0, -21.0], "from": ["body"], "carry": 2.0, "power_scale": 1.0},
            {"id": "neck_bend1", "pos": [round(neck_x(-29.0), 2), 0.0, -29.0], "from": ["body", "neck"], "carry": 0.0, "power_scale": 1.0},
            {"id": "neck_mid", "pos": [round(neck_x(-38.0), 2), 0.0, -38.0], "from": ["neck"], "carry": 0.0, "power_scale": 1.0},
            {"id": "neck_bend2", "pos": [round(neck_x(-47.0), 2), 0.0, -47.0], "from": ["neck"], "carry": 0.0, "power_scale": 1.0},
            {"id": "throat", "pos": [0.0, 0.0, -56.5], "from": ["neck"], "carry": 2.0, "power_scale": 1.0},
        ]},
        "cup_from": ["head", "beak", "neck"],
        "decoration_anchors": [],
        "decor_parts": decor_parts(poly),
        "notes": "Stage gg2 bonus hole, generated by games/vr-mini-golf/tools/gg2_goose.py. HoleNumber %d is a label only (Bonus Hole %d): "
                 "the hole is not part of the 9-hole round (Courses.holes skips Bonus holes)." % (NUMBER, NUMBER),
    }
    spec = {
        "course": "Lantern Grove (bonus)",
        "schema": {"version": "1.0", "note": "Same schema as holes.json. Extra keys: hole.bonus, hole.felt[].color (felt tint), "
                   "hole.tee.sign ([x, z] tee-sign spot), hole.decor_parts (visual-only primitives), placement (world origin/yaw)."},
        "physics": json.load(open(os.path.join(ASSETS, "holes.json")))["physics"],
        "placement": {"origin": ORIGIN, "yaw": YAW},
        "secret": secret(),
        "total_par": hole["par"],
        "holes": [hole],
    }
    with open(SPEC, "w") as fh:
        json.dump(spec, fh, indent=1)
        fh.write("\n")
    sys.path.insert(0, HERE)
    import holes_to_lua
    src, _ = holes_to_lua.convert(SPEC)
    src = src.replace("tools/holes_to_lua.py from", "tools/gg2_goose.py (holes_to_lua.convert) from")
    src = src.replace("(python3 tools/holes_to_lua.py --push --build)", "(uv run --with shapely python3 tools/gg2_goose.py)")
    with open(OUT, "w") as fh:
        fh.write(src)
    print(json.dumps(checks, indent=1))
    print("wrote", os.path.relpath(SPEC, REPO), "and", os.path.relpath(OUT, REPO), "(%d bytes)" % len(src))
    if png:
        render(poly, felt, rl, hole)
    return checks


def render(poly, felt, rl, hole):
    from PIL import Image, ImageDraw
    s = 12
    minx, minz, maxx, maxz = poly.bounds
    pad = 6
    W, H = int((maxx - minx + 2 * pad) * s), int((maxz - minz + 2 * pad) * s)
    img = Image.new("RGB", (W, H), (226, 236, 246))
    d = ImageDraw.Draw(img)

    def P(x, z):
        return ((x - minx + pad) * s, (z - minz + pad) * s)

    for f in felt:
        x, z = f["center"][0], f["center"][2]
        sx, sz = f["size"]
        d.rectangle([P(x - sx / 2, z - sz / 2), P(x + sx / 2, z + sz / 2)], fill=f["color"])
    for r in rl:
        a = math.radians(r["yaw"])
        ux, uz = math.sin(a), math.cos(a)
        nx, nz = uz, -ux
        cx, cz = r["center"][0], r["center"][2]
        hl, ht = r["size"][2] / 2, r["size"][0] / 2
        q = [P(cx + ux * i * hl + nx * j * ht, cz + uz * i * hl + nz * j * ht) for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        d.polygon(q, fill=(184, 175, 160), outline=(120, 110, 100))
    cx, cz = hole["cup"]["position"][0], hole["cup"]["position"][2]
    d.ellipse([P(cx - 0.5, cz - 0.5), P(cx + 0.5, cz + 0.5)], fill=(30, 30, 30))
    d.ellipse([P(-1.1, -1.1), P(1.1, 1.1)], outline=(255, 255, 255), width=2)
    for w in hole["ai_waypoints"]["all"]:
        x, z = w["pos"][0], w["pos"][2]
        d.ellipse([P(x - 0.4, z - 0.4), P(x + 0.4, z + 0.4)], fill=(60, 90, 200))
    d.text((8, 8), "Bonus Hole %d: %s  par %d  (north up, 1 grid = 5 studs)" % (NUMBER, NAME, hole["par"]), fill=(20, 20, 20))
    for gx in range(int(minx // 5) * 5, int(maxx) + 5, 5):
        d.line([P(gx, minz - pad), P(gx, maxz + pad)], fill=(200, 210, 220))
    out = os.path.join(ASSETS, "h%02d-layout.png" % NUMBER)
    img.save(out)
    print("wrote", os.path.relpath(out, REPO))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", action="store_true")
    a = ap.parse_args()
    build(a.png)
