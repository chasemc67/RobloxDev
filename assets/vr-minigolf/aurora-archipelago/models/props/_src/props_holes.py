"""Per-hole P1 props built in the HOLE-LOCAL frame (holes.json coordinates) with the prop origin at its anchor base.
Every instance is merged per material into aa_hNN_dressing (hole frame). Collider skins fill holes.json boxes exactly."""
import math
import bmesh
from mathutils import Matrix
import holesdata as D
import skins
import registry
from aalib import R, hbox, prism_y, lantern_head
from registry import prop

A = D.anchor


def hp(name, n, anchor=None, origin=None, cls="anchored", over_felt_ok=None, gap_ok=False, notes="", target=None,
       lights=None, kind="static", extra=None):
    pos = list(origin if origin is not None else A(n, anchor)["position"])
    tgt = target or (A(n, anchor)["approx_size"] if anchor else None)
    ex = dict(cls=cls, merge=True, anchor=anchor, over_felt_ok=over_felt_ok, gap_ok=gap_ok, lights=lights or [])
    ex.update(extra or {})

    def deco(fn):
        def build(pb):
            pb.set_origin_at(R(*pos))
            fn(pb)
        build.__name__ = fn.__name__
        prop(name, [n], "P1", target=tgt, kind=kind, notes=notes,
             placements=[dict(hole=n, pos=pos, yaw=0.0, anchor=anchor)],
             origin=f"anchor base {anchor} = hole-local {pos} (geometry authored in the hole frame)" if anchor else f"hole-local {pos}",
             extra=ex)(build)
        return fn
    return deco


# ============================================================================================ decals (conformed to felt)
def _piece_top(f, X, Z):
    c, s = f["center"], f["size"]
    lx, lz = D.yaw_rot(X - c[0], Z - c[2], -f.get("yaw", 0.0))
    if abs(lx) > s[0] / 2 + 1e-6 or abs(lz) > s[1] / 2 + 1e-6:
        return None
    sl = f.get("slope")
    return c[1] + (((lx / s[0]) if sl["axis"] == "x" else (lz / s[1])) * sl["rise"] if sl else 0.0)


def conform_poly(pb, n, mat, poly, at, yaw, lift=0.003, thick=0.01, dropped=None, piece=None):
    pts = []
    for x, z in poly:
        ox, oz = D.yaw_rot(x, z, yaw)
        X, Z = at[0] + ox, at[1] + oz
        y = _piece_top(D.felt(n, piece), X, Z) if piece else D.felt_top_at(n, X, Z)
        if y is None:
            if dropped is not None:
                dropped.append((round(X, 2), round(Z, 2)))
            return False
        pts.append((X, y, Z))
    t = bmesh.new()
    a = [t.verts.new(R(X, y + lift, Z)) for X, y, Z in pts]
    b = [t.verts.new(R(X, y + lift + thick, Z)) for X, y, Z in pts]
    t.faces.new(a)
    t.faces.new(b)
    k = len(pts)
    for i in range(k):
        t.faces.new((a[i], a[(i + 1) % k], b[(i + 1) % k], b[i]))
    bmesh.ops.recalc_face_normals(t, faces=t.faces)
    bmesh.ops.triangulate(t, faces=[f for f in t.faces if len(f.verts) > 4])
    pb.add(mat, t)
    return True


def shp_arrow(w=1.4, L=2.0):
    s, h = w * 0.16, L * 0.425
    return [[(-s, L / 2), (s, L / 2), (s, L / 2 - (L - h)), (-s, L / 2 - (L - h))],
            [(-w / 2, L / 2 - (L - h)), (w / 2, L / 2 - (L - h)), (0, -L / 2)]]


def shp_chevron(w=2.4, d=1.2, t=0.38):
    return [[(-w / 2, d / 2), (-w / 2 + t, d / 2), (0, -d / 2 + t * 0.9), (0, -d / 2)],
            [(w / 2, d / 2), (0, -d / 2), (0, -d / 2 + t * 0.9), (w / 2 - t, d / 2)]]


def shp_ring(r0, r1, seg=16):
    out = []
    for i in range(seg):
        a0, a1 = math.tau * i / seg, math.tau * (i + 1) / seg
        out.append([(r0 * math.cos(a0), r0 * math.sin(a0)), (r1 * math.cos(a0), r1 * math.sin(a0)),
                    (r1 * math.cos(a1), r1 * math.sin(a1)), (r0 * math.cos(a1), r0 * math.sin(a1))])
    return out


def shp_disc(r, seg=16):
    return [[(r * math.cos(math.tau * i / seg), r * math.sin(math.tau * i / seg)) for i in range(seg)]]


def shp_curve_arrow(side=1, w=0.4, scale=1.0):
    cl = [(0, 1.0), (0, 0.3), (0.12 * side, -0.15), (0.36 * side, -0.5), (0.62 * side, -0.68)]
    cl = [(x * scale, z * scale) for x, z in cl]
    out = []
    for (x0, z0), (x1, z1) in zip(cl, cl[1:]):
        dx, dz = x1 - x0, z1 - z0
        L = math.hypot(dx, dz)
        nx, nz = -dz / L * w / 2, dx / L * w / 2
        out.append([(x0 - nx, z0 - nz), (x0 + nx, z0 + nz), (x1 + nx, z1 + nz), (x1 - nx, z1 - nz)])
    (x0, z0), (x1, z1) = cl[-2], cl[-1]
    dx, dz = x1 - x0, z1 - z0
    L = math.hypot(dx, dz)
    ux, uz = dx / L, dz / L
    nx, nz = -uz, ux
    hw, hl = 0.55 * scale, 0.6 * scale
    out.append([(x1 + nx * hw, z1 + nz * hw), (x1 - nx * hw, z1 - nz * hw), (x1 + ux * hl, z1 + uz * hl)])
    return out


DECALS = {   # hole: [(anchor, shape-polys, material, yaw)]
    1: [("bank_arrow", shp_curve_arrow(1, 0.32, 1.0), "AuroraMint", 0.0)],
    2: [("felt_arrow_left", shp_arrow(), "AuroraMint", 0.0), ("felt_arrow_right", shp_arrow(), "AuroraMint", 0.0),
        ("felt_rollback_mid", [p for dz in (-0.5, 0.5) for p in [[(x, z + dz) for x, z in q] for q in shp_chevron(1.4, 0.8, 0.26)]], "AuroraTeal", 180.0)],
    3: [("route_arrow_plank", shp_arrow(), "AuroraMint", 0.0), ("route_arrow_bridge", shp_arrow(), "AuroraMint", 0.0),
        ("plank_respawn_stone", shp_disc(0.4), "Lime", 0.0)],
    4: [("ice_warning", [[(x - 0.9 + 0.0, z) for x, z in q] for q in
                         [[(-0.5, 0.06), (0.5, 0.06), (0.5, -0.06), (-0.5, -0.06)]] +
                         [[(x * math.cos(a) - z * math.sin(a), x * math.sin(a) + z * math.cos(a)) for x, z in [(-0.5, 0.06), (0.5, 0.06), (0.5, -0.06), (-0.5, -0.06)]] for a in (math.pi / 3, -math.pi / 3)]]
        + [[(x + 0.15 + 0.62 * k, z) for x, z in q] for k in range(3) for q in shp_chevron(0.5, 1.0, 0.16)], "AuroraMint", 0.0)],
    5: [("geyser_arrow", shp_arrow(), "AuroraMint", 0.0)],
    6: [("pool_respawn_stone", shp_disc(0.4), "Lime", 0.0),
        ("slope_ripples", [[(x, z + dx) for x, z in q] for dx in (-8.4, -5.6, -2.8, 0.0, 2.8, 5.6, 8.4) for q in shp_chevron(1.6, 0.8, 0.22)], "AuroraTeal", -90.0)],
    9: [("felt_arrow_spit", shp_arrow(), "AuroraMint", 0.0), ("felt_arrow_route", shp_arrow(), "AuroraMint", 0.0)],
    11: [("felt_arrow_channel", shp_arrow(), "AuroraMint", 0.0)],
    12: [("felt_arrow_bypass", shp_arrow(), "AuroraMint", 0.0)],
    13: [("safe_east_wait", shp_ring(0.5, 0.66, 16) + [[(-0.25, 0.3), (-0.1, 0.3), (-0.1, -0.3), (-0.25, -0.3)], [(0.1, 0.3), (0.25, 0.3), (0.25, -0.3), (0.1, -0.3)]], "AuroraMint", 0.0)],
    14: [("timing_arrow", shp_arrow(1.4, 1.6) + [[(-0.7, -0.95), (0.7, -0.95), (0.7, -1.0), (-0.7, -1.0)]], "AuroraMint", 0.0)],
    15: [("chevron_1", shp_chevron(), "AuroraMint", 0.0), ("chevron_2", shp_chevron(), "AuroraMint", 0.0)],
    17: [("span_respawn_stone", shp_disc(0.4), "Lime", 0.0), ("route_arrow_light", shp_arrow(), "AuroraMint", 0.0),
         ("route_arrow_bridge", shp_arrow(), "AuroraMint", 0.0)],
    18: [("felt_arrow_bank", shp_curve_arrow(-1, 0.42, 1.3), "AuroraMint", 0.0),
         ("ramp_chevrons", [p for dz in (-0.5, 0.5) for p in [[(x, z + dz) for x, z in q] for q in shp_chevron(6.0, 0.8, 0.32)]], "AuroraMint", 0.0)],
}
DECAL_DROPPED = {}


def _decal_fn(n):
    def fn(pb):
        drop = []
        for an, polys, mat, yaw in DECALS[n]:
            a = A(n, an)
            if a.get("facing"):
                yaw = D.yaw_pointing(a["facing"])
            for q in polys:
                conform_poly(pb, n, mat, q, (a["position"][0], a["position"][2]), yaw, dropped=drop)
        if n == 9:      # conch entry ring: aurora-lime r 0.3 ring at the teleport entry
            for q in shp_ring(0.3, 0.45, 16):
                conform_poly(pb, n, "Lime", q, (0.0, -33.0), 0.0, dropped=drop)
        DECAL_DROPPED[n] = drop
    return fn


for _n in DECALS:
    _anchors = [d[0] for d in DECALS[_n]] + (["teleport conch entry ring"] if _n == 9 else [])
    prop(f"aa_h{_n:02d}_decals", [_n], "P1", target=None, placements=[dict(hole=_n, pos=[0, 0, 0], yaw=0.0)],
         origin="hole tee (0,0,0); every decal conformed to the holes.json felt top (+0.003..+0.013)",
         notes="Flush felt decals (0.01 thick, glow Neon, no collision): " + ", ".join(_anchors),
         extra=dict(cls="decal", merge=True, anchors=_anchors))(_decal_fn(_n))


# ============================================================================================ collider skins per hole
SKIN_NAMES = {2: "rookery drift wall skins (2.4 high)", 7: "mogul_trim (rails follow the moguls, snow humps)",
              9: "coral reef walls 2.4 + bank backings", 10: "snow walls 1.3 + run_lip ice caps", 11: "snowbank/berg 2.4 + floe pocket 3.2 + slot cuts",
              12: "icebreaker hull skins hull13-18 + rail2-5", 16: "moonstone coping (well rails -1.3..1.0)", 17: "frosted ice pier rails",
              18: "faceted crystal walls 3.2 + chute divider + bank backings"}


def _skin_fn(n):
    def fn(pb):
        skins.skin_hole(pb, n)
    return fn


for _n in sorted(D.H):
    prop(f"aa_h{_n:02d}_rails", [_n], "P1", target=None, placements=[dict(hole=_n, pos=[0, 0, 0], yaw=0.0)],
         origin="hole tee (0,0,0); every wall box skinned in place",
         notes="Rail kit / tall-wall skins for every holes.json wall box (faces = collider faces, bottom..top; cap inside the footprint). " + SKIN_NAMES.get(_n, "snow-capped timber rails, brass bolts"),
         extra=dict(cls="skin", merge=True))(_skin_fn(_n))


# ============================================================================================ H1
@hp("aa_h01_harbour_lantern", 1, "harbour_lantern", lights=[dict(pos=[-7.7, 7.2, -24.0], range=14, brightness=0.8, color="#FFB861")],
    notes="Landmark: 9-stud driftwood post (0.35 thick = its occluder) with a ship's lantern 1.2 x 1.6 hanging WEST of the post (away from the felt, >= 3 from the rail), frosted rope coil.")
def harbour_lantern(pb):
    hbox(pb, "Timber", (-6.0, 4.45, -24.0), (0.35, 8.9, 0.35), bevel=0.05)
    hbox(pb, "Timber", (-7.15, 8.6, -24.0), (2.3, 0.3, 0.3), bevel=0.05)
    pb.torus("Snow", 0.28, 0.07, 10, 4, loc=tuple(R(-6.0, 1.1, -24.0)), smooth=False)
    pb.torus("Snow", 0.28, 0.07, 10, 4, loc=tuple(R(-6.0, 1.28, -24.0)), smooth=False)
    hbox(pb, "Snow", (-6.0, 8.95, -24.0), (0.45, 0.1, 0.45), bevel=0.04)
    pb.cyl("Snow", 0.03, 0.03, 0.3, 4, loc=tuple(R(-7.7, 8.3, -24.0)), smooth=False)
    lantern_head(pb, (-7.7, 6.55, -24.0), 1.25, cap="Snow")


@hp("aa_h01_snow_boulder", 1, "snow_boulder", over_felt_ok="holes.json: bumper dressing may widen above the 3x3 box top (y 2.5), visual up to 5",
    notes="Flat-faced slate plinth = the 3x3x3 bumper (yaw 45) from y -0.5 to 2.5; boulder + thick snow cap above 2.5 (<= 4.4 wide, top 5); aurora-mint glow line on the SE bank face.",
    extra=dict(skin_walls=["boulder"]))
def snow_boulder(pb):
    w = D.wall(1, "boulder")
    hbox(pb, "Rock", w["center"], w["size"], w["yaw"])
    pb.rock("Rock", (3.9, 3.9, 1.6), loc=tuple(R(-1.3, 2.45, -35.8)), rot=(0, 0, 45), seed=4, amp=0.12, ico=1)
    pb.rock("Snow", (3.6, 3.6, 1.5), loc=tuple(R(-1.3, 3.35, -35.8)), rot=(0, 0, 20), seed=7, amp=0.1, ico=1, smooth=True)
    ox, oz = D.yaw_rot(0, 1.5 + 0.003, 45)
    hbox(pb, "AuroraMint", (-1.3 + ox, 0.62, -35.8 + oz), (2.6, 0.1, 0.006), 45)


# ============================================================================================ H2
def _pillar_on_wall(n, x, z0, z1):
    for dz in [i * 0.05 for i in range(0, int((z1 - z0) / 0.05) + 1)]:
        for dx in (0, 0.1, -0.1, 0.2, -0.2, 0.3, -0.3, 0.4, -0.4, 0.5, -0.5):
            px, pz = x + dx, z0 + dz
            for w in D.H[n]["walls"]:
                if all(D.in_box_xz(px + ex, pz + ez, w["center"], w["size"], w["yaw"], -0.005)
                       for ex in (-0.19, 0.19) for ez in (-0.19, 0.19)):
                    return px, pz, w
    return None


@hp("aa_h02_rookery_drift", 2, "rookery_drift", extra=dict(hugs_rails=True),
    notes="Snowpuff Rookery drift masses filling the two occluder envelopes between the open-topped burrows (y 0..2.4 between the burrow walls, rounded mounds to <= 4.6 so the flag shows); the 2.4-high wall faces are the aa_h02_rails drift skins.")
def rookery(pb):
    for (x0, x1, z0, z1) in ((-7.5, -2.5, -16.5, -33.5), (2.5, 6.5, -16.5, -28.0)):
        cx, cz, sx, sz = (x0 + x1) / 2, (z0 + z1) / 2, x1 - x0, abs(z1 - z0)
        hbox(pb, "SnowShadow", (cx, 1.2, cz), (sx, 2.4, sz))
        hbox(pb, "Snow", (cx, 2.95, cz), (sx - 0.4, 1.3, sz - 0.4), bevel=0.45, segs=2)
        hbox(pb, "Snow", (cx, 3.9, cz), (sx - 1.6, 1.4, sz - 2.0), bevel=0.5, segs=2)


def _lintel(name, x):
    @hp(f"aa_h02_{name}", 2, name, over_felt_ok="underside exactly y 8 (VR head clearance) per holes.json; pillars stand on the drift wall tops",
        notes="Frosted ice-arch lintel 5 x 1.2 x 1.2, underside y 8, painted plank sign on its south face; ice pillars stand on the burrow wall tops (inside the wall footprints).")
    def lintel(pb):
        hbox(pb, "Ice", (x, 8.6, -16.0), (5.0, 1.2, 1.2), bevel=0.12)
        hbox(pb, "IceCore", (x, 8.6, -16.0), (4.6, 0.25, 0.25))
        hbox(pb, "Snow", (x, 9.3, -16.0), (4.9, 0.25, 1.15), bevel=0.1)
        hbox(pb, "Cream", (x, 8.55, -15.35), (2.4, 0.55, 0.1), bevel=0.02)
        for ex in (x - 2.5 + 0.35, x + 2.5 - 0.35):
            r = _pillar_on_wall(2, ex, -16.55, -15.45)
            if r:
                px, pz, w = r
                top = w["center"][1] + w["size"][1] / 2
                hbox(pb, "Ice", (px, (top + 8.0) / 2, pz), (0.38, 8.0 - top, 0.38))
    return lintel


for _nm, _x in (("lintel_left", -9.5), ("lintel_mid", 0.0), ("lintel_right", 9.0)):
    _lintel(_nm, _x)


@hp("aa_h02_lantern_cue", 2, "lantern_cue", over_felt_ok="holes.json: brass lantern hangs 9 studs over the cup (>= 8)",
    lights=[dict(pos=[-11.0, 9.6, -46.0], range=14, brightness=0.8, color="#FFB861")],
    notes="Brass lantern hanging at y 9 over the cup from a timber crane arm (y 10.6) on a post 3.5 studs outside the west green rail (the frosted pines are P2).")
def lantern_cue(pb):
    hbox(pb, "Timber", (-16.5, 5.4, -46.0), (0.5, 10.8, 0.5), bevel=0.05)
    hbox(pb, "Timber", (-13.7, 10.6, -46.0), (6.1, 0.3, 0.3), bevel=0.05)
    hbox(pb, "Snow", (-13.7, 10.8, -46.0), (6.1, 0.1, 0.34), bevel=0.04)
    pb.cyl("Snow", 0.03, 0.03, 0.42, 4, loc=tuple(R(-11.0, 10.24, -46.0)), smooth=False)
    lantern_head(pb, (-11.0, 9.0, -46.0), 0.82, cap=None)


# ============================================================================================ H3 / H17 crossings
@hp("aa_h03_ice_plank", 3, "ice_plank", gap_ok=True,
    notes="Rail-less glowing ice plank 2.4 x 0.8 x 26 (top y 0 = felt top; hides the 2 x 0.4 felt slab): felt strip 2 wide on top, glacier glass body, crystal-core edge strips. No rails (PlayerGuards are invisible).")
def ice_plank(pb):
    hbox(pb, "Ice", (0, -0.41, -37.0), (2.4, 0.78, 26.0))
    hbox(pb, "Felt", (0, -0.01, -37.0), (2.0, 0.02, 26.0))
    for side in (-1, 1):
        hbox(pb, "Ice", (side * 1.1, -0.01, -37.0), (0.2, 0.02, 26.0))
        hbox(pb, "IceCore", (side * 1.203, -0.3, -37.0), (0.006, 0.12, 25.8))
    for k in range(6):
        pb.cyl("IceCore", 0.18, 0.0, 1.4, 5, loc=tuple(R(0.4 * (-1) ** k, -1.5, -26.0 - 4.4 * k)), rot=(180, 0, 0), smooth=False)


def _ice_deck_places():
    return [dict(hole=3, pos=A(3, "ice_bridge")["position"], yaw=0.0, anchor="ice_bridge"),
            dict(hole=17, pos=A(17, "ice_bridge")["position"], yaw=0.0, anchor="ice_bridge")]


@prop("aa_kit_ice_bridge_deck", [3, 17], "P1", target=[5, 2, 26], placements=_ice_deck_places(),
      origin="deck top centre (felt level, y 0)",
      notes="Glass ice bridge deck 5 x 0.6 x 26 under the 4-wide bridge felt (top -0.02), crystal-core keel and icicles; the snow-capped timber ball rails are the bridge_rail skins in aa_hNN_rails (rail bottoms y -0.5 hidden by the 0.6 deck). H3 and H17.",
      extra=dict(cls="anchored", merge=True, gap_ok=True))
def ice_bridge_deck(pb):
    hbox(pb, "Ice", (0, -0.32, 0), (5.0, 0.6, 26.0))
    hbox(pb, "IceCore", (0, -0.63, 0), (1.2, 0.02, 25.6))
    for k in range(7):
        pb.cyl("Ice", 0.25, 0.0, 1.8, 5, loc=tuple(R(1.6 * (-1) ** k, -1.5, 11.0 - 3.6 * k)), rot=(180, 0, 0), smooth=False)


@hp("aa_h17_crystal_piers", 17, "crystal_piers", gap_ok=True,
    notes="Two glowing crystal pier decks (3 felt + 0.5 rails = 4 wide, 9 long, 1.5 deep under the felt) with hanging crystal shards; frosted ice rails are the pier rail skins.")
def crystal_piers(pb):
    for zc in (-20.5, -37.5):
        hbox(pb, "Ice", (0, -0.76, zc), (4.0, 1.48, 9.0))
        hbox(pb, "IceCore", (0, -1.51, zc), (1.6, 0.02, 8.6))
        for k in range(4):
            pb.cyl("IceCore", 0.3, 0.0, 2.2, 6, loc=tuple(R(1.1 * (-1) ** k, -2.6, zc - 3.3 + 2.2 * k)), rot=(180, 0, 0), smooth=False)


@hp("aa_h17_aurora_ribbon", 17, "aurora_ribbon", gap_ok=True, over_felt_ok="holes.json: ribbon above y 10 only (envelope 3 x 60 x 8)",
    notes="Aurora ribbon curtain pouring down out of the sky into the light span: mint (y 10-40) -> violet (40-70), wavy 0.1-thick sheet inside x +-1.5, z +-4.")
def aurora_ribbon(pb):
    for m, y0, y1 in (("AuroraMint", 10.0, 40.0), ("AuroraViolet", 40.0, 70.0)):
        rows = 6
        for j in range(rows):
            ya, yb = y0 + (y1 - y0) * j / rows, y0 + (y1 - y0) * (j + 1) / rows
            for i in range(8):
                za, zb = -29.0 - 4 + i, -29.0 - 4 + i + 1
                def xo(y, z):
                    return 1.25 * math.sin(z * 1.1 + y * 0.08)
                q = [(xo(ya, za), ya, za), (xo(ya, zb), ya, zb), (xo(yb, zb), yb, zb), (xo(yb, za), yb, za)]
                t = bmesh.new()
                v0 = [t.verts.new(R(x - 0.05, y, z)) for x, y, z in q]
                v1 = [t.verts.new(R(x + 0.05, y, z)) for x, y, z in q]
                t.faces.new(v0)
                t.faces.new(list(reversed(v1)))
                bmesh.ops.recalc_face_normals(t, faces=t.faces)
                pb.add(m, t)


@hp("aa_h17_span_lamp", 17, "span_lamp", over_felt_ok="holes.json anchor: crystal timing lamp beside the pier mouth on the rim felt (felt cue)",
    lights=[dict(pos=[-2.4, 2.1, -15.0], range=8, brightness=0.6, color="#5CFFB0", note="script: mint solid / violet fading / off gone")],
    notes="Crystal timing lamp 0.6 x 2.4: ice post + mint lens (script tints the AuroraMint part violet while fading, dark while gone).")
def span_lamp(pb):
    hbox(pb, "Ice", (-2.4, 0.85, -15.0), (0.36, 1.7, 0.36), bevel=0.05)
    pb.sphere("AuroraMint", 0.29, loc=tuple(R(-2.4, 2.05, -15.0)), segs=8, rings=5, ico=0)
    pb.cyl("Ice", 0.22, 0.0, 0.35, 6, loc=tuple(R(-2.4, 2.22, -15.0)), smooth=False)


# ============================================================================================ H4
@hp("aa_h04_ice_sheen", 4, "ice_sheen", cls="decal",
    notes="Glassy ice felt #9FE3F2 skin (0.01 thick, conformed to the sloped ice felt) with snow frost chevrons every 4 studs. Glass look: Transparency 0.15, Reflectance 0.15.")
def ice_sheen(pb):
    f = D.felt(4, "ice")
    c, s = f["center"], f["size"]
    for j in range(8):
        z0, z1 = c[2] + s[1] / 2 - 4 * j, c[2] + s[1] / 2 - 4 * (j + 1)
        conform_poly(pb, 4, "IceSheen", [(-s[0] / 2, z0), (s[0] / 2, z0), (s[0] / 2, z1), (-s[0] / 2, z1)], (c[0], 0), 0.0, lift=0.003, thick=0.008, piece="ice")
    for j in range(1, 8):
        zc = c[2] + s[1] / 2 - 4 * j
        for q in shp_chevron(3.2, 0.9, 0.12):
            conform_poly(pb, 4, "Snow", q, (c[0], zc), 0.0, lift=0.011, thick=0.003, piece="ice")


# ============================================================================================ H5
@hp("aa_h05_cliff_face", 5, "cliff_face",
    notes="Basalt cliff face 16 x 4 x 1 between the tiers (front face on the step at z -28, body under the upper green, top 3.98), frost streaks; brass shaft lining 3.7 x 3.7 x 4 (spec 3.2; widened for >= 0.15 sweep clearance incl. the gauge) set into the basin under the platform (open box, top -0.01).")
def cliff_face(pb):
    hbox(pb, "Basalt", (0, 1.99, -28.7), (16.0, 3.98, 1.0))     # front face 0.2 behind the step (platform sweep clearance)
    for k, x in enumerate((-6.2, -3.1, 1.4, 5.6)):
        hbox(pb, "Snow", (x, 2.4 + 0.3 * (k % 2), -28.197), (0.35, 2.2 - 0.4 * (k % 2), 0.006))
    hbox(pb, "Snow", (0, 3.9, -28.75), (15.9, 0.16, 0.9))
    for side in (-1, 1):
        hbox(pb, "Brass", (side * 1.8, -2.01, -26.5), (0.1, 4.0, 3.7))
        hbox(pb, "Brass", (0, -2.01, -26.5 + side * 1.8), (3.5, 4.0, 0.1))


@hp("aa_h05_signal_lamp", 5, "signal_lamp", over_felt_ok="holes.json anchor [3,4.5,-28.3] is on the upper green edge above the cliff (felt cue)",
    extra=dict(envelope=[dict(center=[3.0, 4.8, -28.3], size=[0.7, 1.6, 0.5], yaw=0.0)]),
    lights=[dict(pos=[3.0, 5.0, -28.1], range=8, brightness=0.7, color="#5CFF7A", note="script: green while flush (t 0-8 s), amber #FFB861 otherwise")],
    notes="Steam signal lamp 0.6 x 1 x 0.4 on a short brass bracket; the SignalGreen lens part is tinted green/amber by the script.")
def signal_lamp(pb):
    hbox(pb, "Brass", (3.0, 4.25, -28.3), (0.14, 0.5, 0.14))
    hbox(pb, "Brass", (3.0, 5.0, -28.3), (0.6, 1.0, 0.4), bevel=0.06)
    hbox(pb, "SignalGreen", (3.0, 5.0, -28.097), (0.4, 0.5, 0.006))
    hbox(pb, "Snow", (3.0, 5.56, -28.3), (0.62, 0.12, 0.42), bevel=0.05)


# ============================================================================================ H6
@hp("aa_h06_kettle_pool", 6, "kettle_pool",
    notes="Turquoise hot-spring pool 6 x 22 set into the shelf's low east edge: water surface #2FD6C8 at y -0.81, basalt basin, basalt rim under rail5 covering the box bottom (y -0.71); steam is particles (P2).")
def kettle_pool(pb):
    hbox(pb, "Lagoon", (11.5, -0.82, -35.0), (6.0, 0.02, 22.0))
    hbox(pb, "Basalt", (11.5, -1.65, -35.0), (6.0, 0.1, 22.0))
    for zc in (-24.1, -45.9):
        hbox(pb, "Basalt", (11.5, -1.0, zc), (6.0, 1.2, 0.2))
    hbox(pb, "Basalt", (8.6, -1.0, -35.0), (0.2, 1.2, 21.6))
    hbox(pb, "Basalt", (14.75, -1.155, -35.0), (0.5, 0.89, 22.0))
    for k in range(5):
        pb.rock("Basalt", (0.8, 0.8, 0.4), loc=tuple(R(9.5 + 0.9 * (k % 3), -1.6, -27.0 - 4.0 * k)), seed=k, amp=0.2, ico=1)


# ============================================================================================ H8 corals
def _coral(n, idx):
    name = f"coral_{idx}"
    wid = f"coral{idx}"

    @hp(f"aa_h08_{name}", 8, name, over_felt_ok="holes.json: bumper dressing may widen above the box top y 1.6 (envelope ~2.2-2.8 x 4)",
        notes=f"Coral-ice cluster dressing bumper {wid}: flat-faced coral plinth = the box footprint from y -0.5 to 1.6 (mint glow band), candy branches + neon tips above 1.6 (< 4).",
        extra=dict(skin_walls=[wid]))
    def coral(pb):
        w = D.wall(8, wid)
        c, s, yaw = w["center"], w["size"], w["yaw"]
        top = c[1] + s[1] / 2
        hbox(pb, "CoralPink", c, s, yaw)
        for side in (-1, 1):
            ox, oz = D.yaw_rot(0, side * (s[2] / 2 + 0.003), yaw)
            hbox(pb, "CoralMint", (c[0] + ox, 0.9, c[2] + oz), (s[0] - 0.1, 0.1, 0.006), yaw)
        rnd = [(0.0, 0.0), (0.22, 0.12), (-0.25, -0.12)]
        for k, (dx, dz) in enumerate(rnd):
            ox, oz = D.yaw_rot(dx * s[0], dz * s[2], yaw)
            bx, bz = c[0] + ox, c[2] + oz
            h = 1.4 + 0.3 * ((idx + k) % 3)
            tip = (bx + 0.12 * math.sin(idx + k), top + h, bz + 0.12 * math.cos(idx * 2 + k))
            pb.cyl("CoralPink", 0.3, 0.3, 0.17, 6, loc=tuple(R(bx, top + 0.085, bz)), smooth=False)
            pb.tube("CoralOrange" if (idx + k) % 2 else "CoralPink", [R(bx, top + 0.16, bz), R((bx + tip[0]) / 2, top + h * 0.55, (bz + tip[2]) / 2), R(*tip)],
                    [0.3, 0.22, 0.13], segs=6, smooth=True)
            pb.sphere("CoralMint", 0.2, loc=tuple(R(*tip)), segs=6, rings=4)
    return coral


for _i in range(1, 8):
    _coral(8, _i)


@hp("aa_h08_giant_coral", 8, "giant_coral",
    lights=[dict(pos=[-11.0, 9.0, -18.0], range=12, brightness=0.6, color="#6FFFD2")],
    notes="Landmark: giant coral-ice tree (bubblegum + tangerine, neon tips). Trunk inside its 4 x 14 x 4 occluder; branches above 2 studs keep >= 3 studs from the west rail (lean west).")
def giant_coral(pb):
    pb.tube("CoralPink", [R(-10.5, 0, -18), R(-10.6, 4, -18.1), R(-10.8, 8, -18.0), R(-10.9, 11.5, -18.0)], [1.4, 1.0, 0.8, 0.5], segs=8, smooth=True)
    pb.cyl("Rock", 2.0, 1.6, 0.6, 8, loc=tuple(R(-10.5, 0.3, -18.0)), smooth=False)
    branches = [((-10.7, 5.0, -18.0), (-13.6, 9.0, -16.4), "CoralOrange"), ((-10.7, 6.5, -18.0), (-13.8, 11.0, -19.8), "CoralPink"),
                ((-10.8, 8.5, -18.0), (-9.7, 13.0, -18.6), "CoralOrange"), ((-10.6, 3.5, -18.0), (-12.8, 6.0, -20.6), "CoralPink"),
                ((-10.9, 10.0, -18.0), (-12.4, 13.6, -16.6), "CoralPink"), ((-10.7, 7.0, -18.0), (-10.2, 10.5, -15.8), "CoralOrange")]
    for a, b, m in branches:
        mid = ((a[0] + b[0]) / 2 - 0.3, (a[1] + b[1]) / 2 + 0.6, (a[2] + b[2]) / 2)
        pb.tube(m, [R(*a), R(*mid), R(*b)], [0.5, 0.36, 0.2], segs=6, smooth=True)
        pb.sphere("CoralMint", 0.36, loc=tuple(R(*b)), segs=8, rings=5)


# ============================================================================================ H9
@prop("aa_h09_conch", [9], "P1", target=[5, 4.5, 5],
      placements=[dict(hole=9, pos=A(9, "conch_entry")["position"], yaw=0.0, anchor="conch_entry", note="entry: mouth over the ring at [0,0,-33]"),
                  dict(hole=9, pos=A(9, "conch_exit")["position"], yaw=round(math.degrees(math.atan2(-0.9487, 0.3162)), 3), scale=0.8,
                       anchor="conch_exit", note="exit: same mesh x0.8, mouth along the exit dir [-0.9487,0.3162] (exit point inside the mouth), body east")],
      origin="shell base centre; mouth opens toward local +Z, lip arch centred 1.0 in front of the origin, body behind (-Z)",
      notes="Giant spiral conch of candy coral-ice (pink shell, cream lip, glowing mint lip line). Entry: the lip arch frames the aurora-lime ring (opening 2.8 wide x 1.9 high over the spit), body behind the ring under 5 studs. Exit: same mesh scaled 0.8.",
      extra=dict(cls="anchored", merge=True, over_felt_ok="holes.json: conch mouth over the teleport ring at the spit end (entry); exit mouth at the exit point",
                 lights=[dict(pos=[0, 1.2, 0.6], range=8, brightness=0.5, color="#6FFFD2")]))
def conch(pb):
    # body: tapering spiral cone lying along -Z, from z -0.4 to -4.4, apex up-back
    prof = []
    for i in range(9):
        t = i / 8
        r = 2.0 * (1 - t) ** 0.9 + 0.15
        prof.append((r, t))
    pts = [R(0.25 * math.sin(t * 5), 1.9 * (1 - t) + 0.6 + 1.0 * t, -0.6 - 2.8 * t) for r, t in prof]
    pb.tube("CoralPink", pts, [r for r, t in prof], segs=10, smooth=True)
    for k in range(5):
        t = 0.1 + k * 0.18
        pb.torus("Cream", 2.0 * (1 - t) ** 0.9 + 0.12, 0.09, 12, 4, loc=tuple(R(0.25 * math.sin(t * 5), 1.9 * (1 - t) + 0.6 + 1.0 * t, -0.6 - 2.8 * t)), rot=(90, 0, 0), smooth=True)
    # flared lip arch over the mouth (legs outside the 3-wide spit, crown 2.4)
    arch = [R(1.55 * math.cos(math.pi * i / 10), 0.0 + 2.35 * math.sin(math.pi * i / 10), 1.0 - 0.6 * math.sin(math.pi * i / 10)) for i in range(11)]
    pb.tube("Cream", arch, [0.28] * 11, segs=8, smooth=True)
    arch2 = [R(1.55 * math.cos(math.pi * i / 10), 0.0 + 2.35 * math.sin(math.pi * i / 10), 0.92 - 0.6 * math.sin(math.pi * i / 10)) for i in range(11)]
    pb.tube("CoralMint", arch2, [0.08] * 11, segs=5, smooth=True)
    for x in (-1.55, 1.55):
        pb.cyl("CoralPink", 0.42, 0.3, 0.6, 8, loc=tuple(R(x, 0.3, 0.6)), smooth=True)


@hp("aa_h09_reef_lagoon", 9, "reef_lagoon", gap_ok=True,
    notes="Shallow turquoise reef lagoon 25 x 34 (water surface y -1.2) with glowing coral-ice heads under the water; coral-rock spit plinth under the 3 x 13 spit felt (top -0.02, no lip) down into the water.")
def reef_lagoon(pb):
    hbox(pb, "Lagoon", (1.5, -1.21, -39.0), (25.0, 0.02, 34.0))
    hbox(pb, "CoralPink", (0.0, -0.82, -28.5), (3.0, 1.6, 13.0))
    for k in range(9):
        x = -8.0 + 2.6 * k
        z = -26.0 - 3.3 * ((k * 5) % 8)
        if abs(x) < 2.2 and -35.5 < z < -21.5:
            x += 4.0
        pb.sphere("CoralMint" if k % 2 else "CoralOrange", 0.7, loc=tuple(R(x, -1.75, z)), scale=(1, 1, 0.55), segs=8, rings=4)


# ============================================================================================ H10
_PV = D.H[10]["plate_visible"][0]


@hp("aa_h10_snow_walls", 10, "snow_walls", extra=dict(hugs_rails=True),
    notes="Rounded packed-snow bobsled walls covering the 15-wide plate felt everywhere OUTSIDE holes.json plate_visible (two side masses, stepped rounded to <= 3.5); the run rails carry the run_lip ice caps (aa_h10_rails).")
def snow_walls(pb):
    east = [(2.5, -38.0), (10.0, -38.0), (10.0, 2.0), (3.5, 2.0), (3.5, -8.5503), (9.5, -14.5503), (9.5, -27.4497), (2.5, -34.4497)]
    west = [(-5.0, 2.0), (-3.5, 2.0), (-3.5, -11.4497), (2.5, -17.4497), (2.5, -24.5503), (-4.5, -31.5503), (-4.5, -38.0), (-5.0, -38.0)]
    for poly in (west, east):
        prism_y(pb, "SnowShadow", poly, 0.0, 1.6)
    # rounded upper tiers kept inside each mass (derived from the plate_visible polygon; never over the run)
    hbox(pb, "Snow", (-4.25, 2.0, -6.0), (1.3, 0.9, 14.0), bevel=0.35)
    hbox(pb, "Snow", (-1.6, 2.2, -21.0), (6.0, 1.3, 9.0), bevel=0.5, segs=2)
    hbox(pb, "Snow", (7.0, 2.0, -3.5), (4.4, 0.9, 9.0), bevel=0.35)
    hbox(pb, "Snow", (7.3, 2.0, -35.0), (4.6, 0.9, 4.8), bevel=0.35)


@hp("aa_h10_bobsled_hut", 10, "bobsled_hut",
    notes="Landmark: bobsled start hut (violet & snow-white boards - red/cream is reserved for moving parts), snow roof, brass bells, a parked toy bobsled; inside the 4 x 7 x 4 occluder.")
def bobsled_hut(pb):
    x, z = -7.5, -6.0
    for k in range(5):
        hbox(pb, "Canvas" if k % 2 == 0 else "Snow", (x, 0.5 + k * 1.0, z), (3.6, 1.0, 3.6))
    pb.cyl("Snow", 2.75, 0.2, 1.8, 4, loc=tuple(R(x, 5.9, z)), rot=(0, 0, 45), smooth=False)
    hbox(pb, "Ink", (x, 1.3, z + 1.81), (1.2, 2.2, 0.02))
    for dx in (-0.9, 0.9):
        pb.lathe("Brass", [(0.0, 0.0), (0.18, 0.05), (0.22, 0.3), (0.12, 0.45), (0.0, 0.48)], 8, loc=tuple(R(x + dx, 3.7, z + 1.9)))
    hbox(pb, "Canvas", (x + 0.9, 0.35, z - 0.9), (0.9, 0.4, 1.7), bevel=0.15)
    hbox(pb, "Brass", (x + 0.9, 0.06, z - 0.9), (1.0, 0.08, 1.9))


# ============================================================================================ H11
@hp("aa_h11_fishing_hut", 11, "fishing_hut",
    lights=[dict(pos=[-9.0, 1.6, -28.6], range=8, brightness=0.5, color="#FFB861")],
    notes="Landmark: snowpuff ice-fishing hut (violet canvas, snow roof, brass stove-pipe chimney to 6), on the berg; inside its 3 x 6 x 3 occluder.")
def fishing_hut(pb):
    x, z = -9.0, -30.25            # 0.25 south of the anchor: clears pocket_w21 (z >= -28.97), still inside the occluder
    hbox(pb, "Canvas", (x, 1.4, z), (2.3, 2.8, 2.3), bevel=0.1)
    pb.cyl("Snow", 1.7, 0.15, 1.6, 4, loc=tuple(R(x, 3.6, z)), rot=(0, 0, 45), smooth=False)
    pb.cyl("Brass", 0.18, 0.18, 2.4, 8, loc=tuple(R(x + 0.6, 4.7, z - 0.4)), smooth=False)
    pb.cyl("Ink", 0.28, 0.22, 0.25, 8, loc=tuple(R(x + 0.6, 5.88, z - 0.4)), smooth=False)
    hbox(pb, "Glow", (x, 1.6, z + 1.152), (0.6, 0.5, 0.006))
    hbox(pb, "Snow", (x, 0.1, z), (2.5, 0.2, 2.5), bevel=0.08)


# ============================================================================================ H12
@hp("aa_h12_icebreaker", 12, "icebreaker",
    lights=[dict(pos=[4.6, 4.0, -21.0], range=10, brightness=0.5, color="#FFB861")],
    notes="Landmark: beached toy icebreaker straddling the channel (deep-teal hull - red is reserved for moving parts - cream deckhouse, brass funnel puffing steam). Hull faces = hull13-18 / rail2-5 skins (aa_h12_rails); the ship body fills its two occluders either side of the 2.4-wide wheel slot.")
def icebreaker(pb):
    hbox(pb, "HullTeal", (-3.6, 2.0, -21.1), (4.7, 2.0, 5.8), bevel=0.15)
    hbox(pb, "HullTeal", (4.6, 2.0, -21.1), (6.7, 2.0, 5.8), bevel=0.15)
    hbox(pb, "Snow", (-3.6, 3.08, -21.1), (4.6, 0.16, 5.7))
    hbox(pb, "Snow", (4.6, 3.08, -21.1), (6.6, 0.16, 5.7))
    hbox(pb, "Cream", (4.6, 4.3, -21.0), (4.0, 2.3, 3.6), bevel=0.1)
    hbox(pb, "Snow", (4.6, 5.55, -21.0), (4.3, 0.2, 3.9), bevel=0.08)
    for k in range(3):
        hbox(pb, "Glow", (4.6 - 1.2 + 1.2 * k, 4.5, -19.198), (0.6, 0.6, 0.006))
    pb.cyl("Brass", 0.55, 0.5, 1.6, 10, loc=tuple(R(-3.6, 3.95, -21.0)), smooth=False)
    pb.cyl("Ink", 0.58, 0.58, 0.25, 10, loc=tuple(R(-3.6, 4.85, -21.0)), smooth=False)
    pb.cyl("Brass", 0.12, 0.12, 2.6, 6, loc=tuple(R(6.4, 4.2, -21.0)), smooth=False)
    hbox(pb, "Brass", (-1.25, 1.2, -21.1), (0.08, 0.2, 5.8))
    hbox(pb, "Brass", (1.25, 1.2, -21.1), (0.08, 0.2, 5.8))


# ============================================================================================ H13
@hp("aa_h13_hub_base", 13, "hub_base",
    notes="Solid round carousel base: 48-sided cylinder, apothem r 7.5, y -0.5..1.2 (the 48 hub_plinth strips), packed-snow body with a brass top band and ice-core ring; top is not a playing surface.",
    extra=dict(skin_walls=["hub_plinth_%02d" % i for i in range(48)]))
def hub_base(pb):
    rr = 7.5 / math.cos(math.pi / 48)
    pb.lathe("SnowShadow", [(rr, -0.5), (rr, 0.9)], 48, loc=tuple(R(0, 0, -36.0)), smooth=False, phase=math.pi / 48)
    pb.lathe("Brass", [(rr, 0.9), (rr, 1.2), (6.0, 1.2), (6.0, 1.15)], 48, loc=tuple(R(0, 0, -36.0)), smooth=False, phase=math.pi / 48)
    pb.lathe("Ice", [(6.0, 1.15), (6.0, 1.2), (0.0, 1.2)], 24, loc=tuple(R(0, 0, -36.0)), smooth=False)
    pb.torus("IceCore", 4.2, 0.06, 32, 3, loc=tuple(R(0, 1.16, -36.0)), smooth=False)


@hp("aa_h13_carousel_canopy", 13, "carousel_canopy", over_felt_ok="holes.json: canopy underside y 9 (>= 8 over the felt), pole inside the hub",
    lights=[dict(pos=[0, 8.6, -36.0], range=16, brightness=0.8, color="#FFB861")],
    notes="Landmark: brass pole r 0.5 (inside the hub, its occluder) from the hub top to the canopy; violet/snow striped canopy, underside y 9, r 8, scalloped brass rim, snowpuff weathervane on top (12).")
def canopy(pb):
    pb.cyl("Brass", 0.5, 0.5, 8.0, 12, loc=tuple(R(0, 5.2, -36.0)), smooth=True)
    pb.lathe("Brass", [(8.0, 9.0), (8.0, 9.35)], 24, loc=tuple(R(0, 0, -36.0)), smooth=False)
    for k in range(12):
        a0 = 30 * k
        m = "Canvas" if k % 2 == 0 else "Snow"
        t = bmesh.new()
        p0 = t.verts.new(R(0, 11.2, -36.0))
        q = [t.verts.new(R(8.0 * math.cos(math.radians(a0 + d)), 9.35, -36.0 + 8.0 * math.sin(math.radians(a0 + d)))) for d in (0, 30)]
        b = [t.verts.new(R(8.0 * math.cos(math.radians(a0 + d)), 9.0, -36.0 + 8.0 * math.sin(math.radians(a0 + d)))) for d in (0, 30)]
        t.faces.new((p0, q[0], q[1]))
        t.faces.new((b[0], b[1], q[1], q[0]))
        t.faces.new((p0, b[1], b[0]))
        bmesh.ops.recalc_face_normals(t, faces=t.faces)
        pb.add(m, t)
    pb.cyl("Brass", 0.1, 0.1, 0.8, 6, loc=tuple(R(0, 11.5, -36.0)), smooth=False)
    pb.sphere("Ink", 1.0, loc=tuple(R(0, 12.05, -36.0)), scale=(0.25, 0.25, 0.32), segs=8, rings=5)
    pb.sphere("Cream", 1.0, loc=tuple(R(0, 12.0, -35.83)), scale=(0.16, 0.08, 0.2), segs=6, rings=4)
    pb.cyl("Beak", 0.06, 0.0, 0.18, 5, loc=tuple(R(0, 12.2, -35.7)), rot=(90, 0, 0), smooth=False)


# ============================================================================================ H14
@hp("aa_h14_bell_gantry", 14, "bell_gantry", over_felt_ok="holes.json: gantry beam y 10.35 (>= 8), icicles from the beam only (>= 8 over the felt)",
    notes="Landmark: timber bell gantry, legs 0.8 x 10.35 at x +-5 (= occluders), beam 10 x 1 x 1 at y 10.35..11.35 with a snow cap, icicles hanging from the beam to y 8.6, brass hinge bracket at [0,10.35,-24].")
def gantry(pb):
    for x in (-5.0, 5.0):
        hbox(pb, "Timber", (x, 5.175, -24.0), (0.8, 10.35, 0.8), bevel=0.06)
        hbox(pb, "Snow", (x, 0.1, -24.0), (0.8, 0.2, 0.8), bevel=0.06)
    hbox(pb, "Timber", (0, 10.85, -24.0), (10.0, 1.0, 1.0), bevel=0.08)
    hbox(pb, "Snow", (0, 11.45, -24.0), (9.9, 0.2, 0.98), bevel=0.08)
    for k in range(9):
        x = -4.0 + k
        if abs(x) < 0.9:
            continue
        L = 0.9 + 0.7 * ((k * 3) % 4) / 3
        pb.cyl("Ice", 0.12, 0.0, L, 5, loc=tuple(R(x, 10.35 - L / 2, -24.0 + 0.3 * (-1) ** k)), rot=(180, 0, 0), smooth=False)
    hbox(pb, "Brass", (0, 10.25, -24.0), (0.9, 0.2, 0.9))


# ============================================================================================ H15
@hp("aa_h15_lip_ice", 15, "lip_ice", over_felt_ok="holes.json anchor: icicle curtain on the 4-stud step face under the lane end (z -20..-20.5)",
    extra=dict(envelope=[dict(center=[0.0, -2.0, -20.25], size=[7.2, 4.1, 1.0], yaw=0.0)]),
    notes="Frozen-fall lip: glassy icicle curtain 7 wide down the 4-stud step (y -4..-0.02) on the face at z -20, the open lip itself stays clear (the parapet is aa_h15_lip_parapet).")
def lip_ice(pb):
    hbox(pb, "Ice", (0, -2.01, -20.12), (7.0, 3.98, 0.24))
    for k in range(9):
        x = -3.2 + 0.8 * k
        L = 1.2 + 0.9 * ((k * 5) % 3)
        pb.cyl("IceCore", 0.14, 0.0, L, 5, loc=tuple(R(x, -0.02 - L / 2, -20.3)), rot=(180, 0, 0), smooth=False)


@hp("aa_h15_lip_parapet", 15, origin=[0.0, 0.0, -19.8], target=[8.0, 3.5, 0.3],
    over_felt_ok="holes.json vr_comfort PlayerGuard lip_parapet 8 x 3.5 x 0.3 at [0,1.75,-19.8] (player-only; the ball passes through)",
    notes="Clear ice parapet visual over the PlayerGuard (Transparency 0.6 in Studio, thin, no timber look).",
    extra=dict(allow_inwall=True, envelope=[dict(center=[0.0, 1.75, -19.8], size=[8.0, 3.5, 0.3], yaw=0.0)]))
def lip_parapet(pb):
    hbox(pb, "Ice", (0, 1.75, -19.8), (8.0, 3.5, 0.3))


# ============================================================================================ H16
@hp("aa_h16_moonwell", 16, "moonwell",
    lights=[dict(pos=[0.0, -0.4, -29.5], range=8, brightness=0.5, color="#BFF6FF")],
    notes="Landmark: moonstone flags with silver inlay dressing the two felt slopes (conformed 0.01 skins), glowing ice-crystal clusters on the rim inside the occluders (x +-10.8, <= 2 high), silver crescent-moon spout ornaments on the spout walls; the coping = moonstone rail skins (aa_h16_rails).")
def moonwell(pb):
    for fid in ("well_w", "well_e"):
        f = D.felt(16, fid)
        c, s = f["center"], f["size"]
        for j in range(6):
            z0, z1 = c[2] + s[1] / 2 - 3 * j, c[2] + s[1] / 2 - 3 * (j + 1)
            z1 = max(z1, -29.7)          # stop short of the spout walls at z -30
            conform_poly(pb, 16, "Moonstone", [(-s[0] / 2 + 0.01, z0 - 0.01), (s[0] / 2 - 0.01, z0 - 0.01), (s[0] / 2 - 0.01, z1), (-s[0] / 2 + 0.01, z1)], (c[0], 0), 0.0, lift=0.003, thick=0.008, piece=fid)
    for x in (-10.8, 10.8):
        for k in range(4):
            z = -18.0 - 2.6 * k
            h = 1.2 + 0.25 * (k % 3)
            pb.cyl("Ice", 0.42, 0.0, h, 6, loc=tuple(R(x + 0.15 * (-1) ** k, h / 2, z)), smooth=False)
            pb.cyl("IceCore", 0.18, 0.0, h * 0.8, 5, loc=tuple(R(x + 0.15 * (-1) ** k, h * 0.4, z)), smooth=False)
    for xs in (-5.5, 5.5):
        w = D.wall(16, "spout_w" if xs < 0 else "spout_e")
        top = w["center"][1] + w["size"][1] / 2
        cx = xs + (2.2 if xs < 0 else -2.2)
        pts = [R(cx + 0.9 * math.cos(math.radians(a)), top + 0.9 + 0.9 * math.sin(math.radians(a)), -30.0) for a in range(-60, 241, 30)]
        pb.tube("Silver", pts, [0.1] * len(pts), segs=6, smooth=True)


# ============================================================================================ H18
@hp("aa_h18_halo_arch", 18, "halo_arch", over_felt_ok="holes.json: arch opening >= 18 over the felt (beam y 18.8..34.8), legs at x +-23 outside the footprint",
    lights=[dict(pos=[0.0, 30.0, -52.0], range=30, brightness=0.6, color="#BFF6FF")],
    notes="Landmark (holes.json anchor [0,0.8,-52], depth 4; world.json's [-235,222,-292] depth 8 is stale): translucent glowing ice arch 46 wide x 34 tall - legs x 21..25 from the felt level up, arch underside >= 18.8 everywhere over the felt, crystal-core neon line along the inner curve.")
def halo_arch(pb):
    def ring(rx_in, rx_out, y_spring, top_in, top_out, z0, z1, m, nseg=20):
        for i in range(nseg):
            a0, a1 = math.pi * i / nseg, math.pi * (i + 1) / nseg
            def P(a, rx, top):
                return (rx * math.cos(a), y_spring + (top - y_spring) * math.sin(a))
            pi0, pi1 = P(a0, rx_in, top_in), P(a1, rx_in, top_in)
            po0, po1 = P(a0, rx_out, top_out), P(a1, rx_out, top_out)
            t = bmesh.new()
            v = [[t.verts.new(R(x, y, z)) for x, y in (pi0, po0, po1, pi1)] for z in (z0, z1)]
            t.faces.new(v[0])
            t.faces.new(list(reversed(v[1])))
            for k in range(4):
                t.faces.new((v[0][k], v[0][(k + 1) % 4], v[1][(k + 1) % 4], v[1][k]))
            bmesh.ops.recalc_face_normals(t, faces=t.faces)
            pb.add(m, t)
    ring(21.0, 25.0, 18.8, 30.8, 34.8, -50.0, -54.0, "Ice")
    ring(20.9, 21.05, 18.8, 30.7, 30.85, -51.8, -52.2, "IceCore")
    for x in (-23.0, 23.0):
        hbox(pb, "Ice", (x, 9.8, -52.0), (4.0, 18.0, 4.0), bevel=0.2)
        hbox(pb, "IceCore", (x, 9.8, -49.997), (0.4, 17.0, 0.006))
        hbox(pb, "Snow", (x, 1.0, -52.0), (4.2, 0.4, 4.2), bevel=0.15)


def _bank_deco(n, name, wid):
    @hp(f"aa_h18_{name}", 18, name, notes=f"Faceted ice-crystal spikes (3-5 tall, glowing cores) rising from the top of {wid} (inside its footprint), dressing the 45-degree crystal bank; the backing faces are the crystal skins.",
        extra=dict(skin_walls=[wid], on_wall=wid))
    def deco(pb):
        w = D.wall(18, wid)
        c, s, yaw = w["center"], w["size"], w["yaw"]
        top = c[1] + s[1] / 2
        L = s[2]
        k = 0
        z = -L / 2 + 0.6
        while z < L / 2 - 0.5:
            ox, oz = D.yaw_rot(0, z, yaw)
            h = 1.0 + 1.6 * ((k * 7) % 5) / 4
            pb.cyl("Ice", 0.22, 0.0, h, 5, loc=tuple(R(c[0] + ox, top + h / 2, c[2] + oz)), smooth=False)
            pb.cyl("IceCore", 0.1, 0.0, h * 0.8, 4, loc=tuple(R(c[0] + ox, top + h * 0.4, c[2] + oz)), smooth=False)
            z += 1.1
            k += 1
    return deco


_bank_deco(18, "crystal_bank_ne_deco", "crystal_bank_ne_backing")
_bank_deco(18, "crystal_bank_sw_deco", "crystal_bank_sw_backing")


@hp("aa_h18_crystal_chute", 18, "crystal_chute",
    notes="The Halo Run chute dressing: glowing crystal inlay strips + crystal-core caps on the chute_divider and rail9 (the 1.6-wide chute walls); faces = the crystal skins in aa_h18_rails (top <= 3.2).",
    extra=dict(skin_walls=["chute_divider", "rail9"], on_wall="chute_divider"))
def chute(pb):
    for wid in ("chute_divider", "rail9"):
        w = D.wall(18, wid)
        c, s = w["center"], w["size"]
        top = c[1] + s[1] / 2
        for k in range(4):
            z = c[2] - s[2] / 2 + 1.25 + 2.5 * k
            hbox(pb, "IceCore", (c[0], top - 0.004, z), (s[0] * 0.6, 0.008, 0.5))


# ============================================================================================ kit instances into holes
def _sign_score(n, pos, yaw, off, W, H):
    """penalty for a sign board: 10 per sample inside a wall box, 1 per sample over felt."""
    pen = 0
    bx = off * (W / 2 + 0.05)
    for i in range(13):
        for zz in (-0.12, 0.12):
            lx = bx - W / 2 + W * i / 12
            ox, oz = D.yaw_rot(lx, zz, yaw)
            X, Z = pos[0] + ox, pos[2] + oz
            for y in (H - 1.1, H - 0.2):
                for w in D.H[n]["walls"]:
                    if D.in_box_xz(X, Z, w["center"], w["size"], w["yaw"]) and abs(pos[1] + y - w["center"][1]) <= w["size"][1] / 2:
                        pen += 10
            if D.felt_top_at(n, X, Z) is not None:
                pen += 1
    return pen


SIGN_CHOICE = []


def _sign_places(kind, kind_size):
    W, H = (1.6, 2.6) if kind == "plank" else (1.8, 2.45)
    out = {0: [], -1: [], 1: []}
    for n in sorted(D.H):
        for a in D.H[n]["decoration_anchors"]:
            if ("sign" in a["name"]) and [round(v, 2) for v in a["approx_size"]] == kind_size:
                yaw = D.yaw_facing(a["facing"]) if a.get("facing") else 0.0
                sc = {o: _sign_score(n, a["position"], yaw, o, W, H) for o in (0, -1, 1)}
                best = min(sc, key=lambda o: (sc[o], abs(o)))
                bx = best * (W / 2 + 0.05)
                ox, oz = D.yaw_rot(bx, 0, yaw)
                env = [dict(center=[a["position"][0] + ox, a["position"][1] + a["approx_size"][1] / 2 + 0.05, a["position"][2] + oz], size=[W + 0.2, a["approx_size"][1] + 0.2, 0.6], yaw=yaw)]
                env += [dict(center=o["center"], size=o["size"], yaw=o.get("yaw", 0.0)) for o in a.get("occluders", [])]
                pl = dict(hole=n, pos=a["position"], yaw=round(yaw, 3), anchor=a["name"], envelope=env,
                          over_felt_ok=("holes.json sign anchor: residual board overhang of the felt (felt samples %d)" % sc[best]) if sc[best] else None)
                out[best].append(pl)
                SIGN_CHOICE.append((n, a["name"], kind, best, sc))
    return out


_SP = {"plank": _sign_places("plank", [1.6, 2.6, 0.2]), "lantern": _sign_places("lantern", [1.8, 3.2, 0.25])}
for _p in registry.PROPS:
    for _k in ("plank", "lantern"):
        for _o, _sfx in ((0, ""), (-1, "_L"), (1, "_R")):
            if _p["name"] == f"aa_kit_sign_{_k}{_sfx}":
                _p["placements"] = _SP[_k][_o]
                _p["holes"] = sorted({q["hole"] for q in _SP[_k][_o]})
                _p["extra"]["merge"] = True
    if False:
        pass
    elif _p["name"] == "aa_kit_flag":
        for pl in _p["placements"]:
            pl["anchor"] = "cup_flag"
    elif _p["name"] in ("aa_kit_geyser_cone",):
        _p["placements"][0]["anchor"] = "steamwhistle_geyser"
