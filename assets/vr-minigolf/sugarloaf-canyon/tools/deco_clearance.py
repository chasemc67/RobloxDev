"""Decoration-anchor clearance: audit + settle (shared by Aurora and Sugarloaf; keep both copies identical).
Audit:  python3 tools/deco_clearance.py holes.json [--json out.json] [--all]
Boxes per anchor: occluders (yawed) when present, else approx_size at the base position; signs also get their
panel (approx_size, turned to face `facing`). Checks with gap G=0.15: anchor vs rail/wall, vs felt head room
(felt-0.4 .. felt+8), vs other anchors, and exact coplanar faces (z-fighting) against walls.
Classes: exception (Chase-accepted structures), dressing (wraps play geometry: moving meshes, collider skins,
terrain/water under the felt, rail lips, bridge decks), flat (<=0.05 tall decals), envelope (scenery volume whose
approx_size is a loose bound: > 120 sq studs footprint or > 20 tall), prop (free-standing dressing: must be clear).
settle(course, names) nudges the named free-standing anchors (rigidly, then per occluder) by the smallest
XZ move that clears everything; play geometry is never touched."""
import json, sys, math
G = 0.15
EXC = {(17, "crystal_piers"), (17, "ice_bridge"), (15, "ice_parapet"), (9, "coral_spit")}
DRESS = ("moving mesh", "moving part", "(moving", "covers the collider", "dressing bumper", "dressing the", "dresses the", "must cover",
         "collider exactly", "felt on top", "deck under the felt", "under the water", "terrain", "on top of both", "rails dressed",
         "is the hub", "not a playing surface", "coping round", "dressed as", "base collider", "on the 1.6 bumper", "collision on",
         "rail trim", "lip trim", "felt rises", "tilted felt", "flush in the", "teleport exit", "exactly outside bridge felt",
         "deck slab", "flush with the deck", "rides up inside", "chamber walls", "circumscribed", "felt banks")


def corners(c, sx, sz, yaw):
    a = math.radians(yaw or 0); ca, sa = math.cos(a), math.sin(a)
    return [(c[0] + dx * ca + dz * sa, c[2] - dx * sa + dz * ca) for dx, dz in ((-sx/2, -sz/2), (sx/2, -sz/2), (sx/2, sz/2), (-sx/2, sz/2))]


def sep2(p, q):
    best = -1e9
    for poly in (p, q):
        for i in range(len(poly)):
            x1, z1 = poly[i]; x2, z2 = poly[(i + 1) % len(poly)]
            nx, nz = z2 - z1, -(x2 - x1); L = math.hypot(nx, nz) or 1; nx /= L; nz /= L
            pa = [x * nx + z * nz for x, z in p]; qa = [x * nx + z * nz for x, z in q]
            best = max(best, min(qa) - max(pa), min(pa) - max(qa))
    return best


def yov(a0, a1, b0, b1): return min(a1, b1) - max(a0, b0)


def boxes(a):
    out = []
    p = a["position"]; s = a.get("approx_size")
    if a.get("occluders"):
        out += [(corners(o["center"], o["size"][0], o["size"][2], o.get("yaw", 0)), o["center"][1] - o["size"][1]/2, o["center"][1] + o["size"][1]/2)
                for o in a["occluders"]]
        if a["name"].startswith("sign") and s:      # the panel at the top of the post
            f = a.get("facing") or [0, -1]
            yaw = math.degrees(math.atan2(-f[0], -f[1]))
            out.append((corners(p, s[0], s[2], yaw), p[1] + s[1] - 1.2, p[1] + s[1]))
    elif s:
        out.append((corners(p, s[0], s[2], a.get("yaw", 0)), p[1], p[1] + s[1]))
    return out


def classify(n, a):
    if (n, a["name"]) in EXC: return "exception"
    t = a.get("notes", "").lower()
    if any(w in t for w in DRESS): return "dressing"
    s = a.get("approx_size") or [0, 0, 0]
    if s[1] <= 0.05: return "flat"
    if (s[0] * s[2] > 120 or s[1] > 20) and not a.get("occluders"): return "envelope"
    return "prop"


def _scene(h):
    walls = [(w["id"], corners(w["center"], w["size"][0], w["size"][2], w.get("yaw", 0)), w["center"][1] - w["size"][1]/2, w["center"][1] + w["size"][1]/2) for w in h["walls"]]
    felts = []
    for f in h["felt"]:
        fy = f["center"][1] + abs((f.get("slope") or {}).get("rise", 0)) / 2
        felts.append((f["id"], corners(f["center"], f["size"][0], f["size"][1], f.get("yaw", 0)), fy))
    return walls, felts


def box_hits(box, walls, felts, others, mount=None):
    """problems for one box; others = [(name, cls, boxes)]"""
    poly, y0, y1 = box; hits = []
    for wid, wp, wy0, wy1 in walls:
        if wid == mount: continue                           # anchor deliberately stands on this wall's top
        if yov(y0, y1, wy0, wy1) <= -G + 1e-6: continue
        s = sep2(poly, wp)
        if s < G - 1e-6: hits.append(("wall", wid, s))
        if abs(s) < 1e-4 and yov(y0, y1, wy0, wy1) > 1e-6: hits.append(("coplanar", wid, 0.0))
    for fid, fp, fy in felts:
        if y1 > fy - 0.4 + 1e-6 and y0 < fy + 8 - 1e-6:
            s = sep2(poly, fp)
            if s < -1e-6: hits.append(("felt", fid, s))
    for nm, cl, bs in others:
        for p2, z0, z1 in bs:
            if yov(y0, y1, z0, z1) <= -G + 1e-6: continue
            if z1 <= y0 + 0.05 or y1 <= z0 + 0.05: continue      # standing on / under a ground-level skin (pond, deck)
            s = sep2(poly, p2)
            if s < G - 1e-6: hits.append(("prop", nm, s))
    return hits


def audit(course):
    out = []
    for h in course["holes"]:
        n = h["number"]; walls, felts = _scene(h)
        M = {a["name"]: a.get("mounted_on") for a in h.get("decoration_anchors", [])}
        A = [(a["name"], classify(n, a), boxes(a)) for a in h.get("decoration_anchors", []) if not a["name"].startswith("cup_flag")]
        for i, (nm, cl, bs) in enumerate(A):
            for b in bs:
                for kind, other, s in box_hits(b, walls, felts, A[i+1:], M.get(nm)):
                    ocl = next((c for m, c, _ in A if m == other), None) if kind == "prop" else None
                    out.append(dict(hole=n, anchor=nm, cls=cl, kind=kind, other=other, other_cls=ocl, sep=round(s, 3)))
    # de-duplicate (sign post + panel can both report the same rail)
    seen, res = set(), []
    for x in out:
        k = (x["hole"], x["anchor"], x["kind"], x["other"])
        if k not in seen: seen.add(k); res.append(x)
    return res


def is_real(x):
    """a problem counts as real when a free-standing prop is involved and the other side is not a loose envelope/flat decal"""
    if x["cls"] != "prop": return False
    return x["kind"] != "prop" or x["other_cls"] in ("prop", "dressing", "exception")


def _shift(a, dx, dz, only=None):
    if only is None:
        a["position"] = [round(a["position"][0] + dx, 3), a["position"][1], round(a["position"][2] + dz, 3)]
        for o in a.get("occluders", []):
            o["center"] = [round(o["center"][0] + dx, 3), o["center"][1], round(o["center"][2] + dz, 3)]
    else:
        o = a["occluders"][only]; o["center"] = [round(o["center"][0] + dx, 3), o["center"][1], round(o["center"][2] + dz, 3)]


def _clear(n, a, walls, felts, others):
    return not [x for b in boxes(a) for x in box_hits(b, walls, felts, others, a.get("mounted_on"))]


def _search(test, maxd):
    steps = [round(0.05 * i, 3) for i in range(1, int(maxd / 0.05) + 1)]
    for d in steps:
        for k in range(32):
            t = 2 * math.pi * k / 32; dx, dz = round(d * math.cos(t), 3), round(d * math.sin(t), 3)
            if test(dx, dz): return dx, dz
    return None


def settle(course, names, maxd=6.0, log=print):
    """names: {(hole, anchor): note}. Moves each named anchor the least XZ distance that clears it."""
    moved = []
    for h in course["holes"]:
        n = h["number"]; walls, felts = _scene(h)
        for a in h["decoration_anchors"]:
            if (n, a["name"]) not in names: continue
            others = [(b["name"], classify(n, b), boxes(b)) for b in h["decoration_anchors"]
                      if b is not a and not b["name"].startswith("cup_flag") and classify(n, b) in ("prop", "dressing", "exception")]
            if _clear(n, a, walls, felts, others): continue
            p0 = list(a["position"])
            def rigid(dx, dz):
                _shift(a, dx, dz); ok = _clear(n, a, walls, felts, others); _shift(a, -dx, -dz); return ok
            r = _search(rigid, maxd)
            if r:
                _shift(a, *r); moved.append((n, a["name"], f"moved {r[0]:+.2f},{r[2-1]:+.2f} (x,z) from {p0}"))
                continue
            # per-occluder (e.g. gantry/arch legs either side of the lane)
            if a.get("occluders") and len(a["occluders"]) > 1:
                ok = True; notes = []
                for i, o in enumerate(a["occluders"]):
                    bx = (corners(o["center"], o["size"][0], o["size"][2], o.get("yaw", 0)), o["center"][1] - o["size"][1]/2, o["center"][1] + o["size"][1]/2)
                    if not box_hits(bx, walls, felts, others): continue
                    def one(dx, dz, i=i, o=o):
                        c = o["center"]; b2 = (corners([c[0] + dx, c[1], c[2] + dz], o["size"][0], o["size"][2], o.get("yaw", 0)), bx[1], bx[2])
                        return not box_hits(b2, walls, felts, others)
                    r = _search(one, 1.0)
                    if not r: ok = False; break
                    _shift(a, r[0], r[1], only=i); notes.append(f"occluder{i} {r[0]:+.2f},{r[1]:+.2f}")
                    if a.get("approx_size"):
                        s = a["approx_size"]; a["approx_size"] = [round(s[0] + 2 * abs(r[0]), 3), s[1], round(s[2] + 2 * abs(r[1]), 3)]
                if ok and _clear(n, a, walls, felts, others):
                    moved.append((n, a["name"], "legs " + "; ".join(notes))); continue
            moved.append((n, a["name"], "UNRESOLVED"))
    for m in moved: log("  settle H%d %s: %s" % m)
    return moved


if __name__ == "__main__":
    from collections import Counter
    c = json.load(open(sys.argv[1])); r = audit(c)
    real = [x for x in r if is_real(x)]
    for x in (r if "--all" in sys.argv else real): print(x)
    print("TOTAL raw", len(r), dict(Counter(x["cls"] for x in r)), "| REAL", len(real),
          "| coplanar(any class)", sum(x["kind"] == "coplanar" for x in r))
    if "--json" in sys.argv: json.dump(r, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
