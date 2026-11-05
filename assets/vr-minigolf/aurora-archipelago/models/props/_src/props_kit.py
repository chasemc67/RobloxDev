"""Reused kit (aa_kit_*) and world (aa_world_*) props. Instances: per-hole placements (hole-local) or world placements
(world.json, world coordinates) listed in extra.world_instances."""
import math
import bmesh
from mathutils import Vector, Matrix
import holesdata as D
import skins
from aalib import R, hbox, prism_y, lantern_head
from registry import prop

LANTERN_LIGHT = dict(range=14, brightness=0.8, color="#FFB861")


def _flag_places():
    return [dict(hole=n, pos=D.H[n]["cup"]["position"], yaw=0.0, note="cup.position; banner turns to face the tee")
            for n in sorted(D.H)]


@prop("aa_kit_flag", list(range(1, 19)), "P1", target=[2.0, 7.5, 0.15], placements=_flag_places(),
      origin="cup centre at felt level (pole base, pole sinks 0.3 into the cup)",
      notes="Pole 7.5 x dia 0.15 + separate banner mesh 2 x 1.2 x 0.05 #E03C31 (child aa_kit_flag__FlagRed, turns about the pole axis = origin Y to face the tee). Decoration only.",
      extra=dict(cls="flag", merge=False))
def flag(pb):
    pb.cyl("Brass", 0.075, 0.075, 7.8, 8, loc=tuple(R(0, 3.6, 0)), smooth=True)
    pb.sphere("Brass", 0.13, loc=tuple(R(0, 7.55, 0)), segs=8, rings=5)
    hbox(pb, "FlagRed", (1.075, 6.9, 0), (2.0, 1.2, 0.05))


def _rail(pb, L, rise=0.0):
    w = dict(id="kit", center=[0, 0.25, 0], size=[0.5, 1.5, L], yaw=0.0)
    skins.skin_wall(pb, 1, w)
    if rise:
        # slope follower: shear every vertex along the run (Blender -Y = Roblox +Z): dy = -z/L * rise
        for b in pb.bms.values():
            for v in b.verts:
                v.co.z += (v.co.y / L) * rise


for _L in (1, 2, 4, 8):
    prop(f"aa_kit_rail_straight_{_L}", [], "P1", target=[0.5, 1.5, float(_L)],
         origin="box centre x/z, felt level y 0 (collider y -0.5..1.0)",
         notes="Rail kit straight: snow-capped timber filling a 0.5 x 1.5 rail collider exactly (y -0.5..1.0), brass bolt plates every 2 studs. Per-hole rails are generated from holes.json walls with the same construction (aa_hNN_dressing).",
         extra=dict(cls="kit", merge=False))(lambda pb, L=_L: _rail(pb, L))


@prop("aa_kit_rail_slope_4", [], "P1", target=[0.5, 1.5, 4.0], origin="box centre, felt level",
      notes="Slope follower: 4-stud straight sheared 0.6 over its run (top/bottom follow a felt slope).",
      extra=dict(cls="kit", merge=False))
def rail_slope(pb):
    _rail(pb, 4.0, rise=0.6)


@prop("aa_kit_rail_corner", [], "P1", target=[2.0, 1.5, 2.0], origin="outer corner post centre, felt level",
      notes="90-degree corner: two 1.75 arms meeting on a brass-capped corner post.", extra=dict(cls="kit", merge=False))
def rail_corner(pb):
    skins.skin_wall(pb, 1, dict(id="a", center=[0, 0.25, -0.875], size=[0.5, 1.5, 1.75], yaw=0))
    skins.skin_wall(pb, 1, dict(id="b", center=[0.875, 0.25, 0], size=[0.5, 1.5, 1.75], yaw=90), 1)
    hbox(pb, "Brass", (0, 1.04, 0), (0.56, 0.08, 0.56), bevel=0.02)


@prop("aa_kit_rail_45", [], "P1", target=[1.9, 1.5, 1.9], origin="joint centre, felt level",
      notes="45-degree joint: two 1.5 arms at 135 degrees with a brass joint cap.", extra=dict(cls="kit", merge=False))
def rail_45(pb):
    skins.skin_wall(pb, 1, dict(id="a", center=[0, 0.25, 0.75], size=[0.5, 1.5, 1.5], yaw=0))
    ox, oz = D.yaw_rot(0, -0.75, 45)
    skins.skin_wall(pb, 1, dict(id="b", center=[ox, 0.25, oz], size=[0.5, 1.5, 1.5], yaw=45), 1)
    pb.cyl("Brass", 0.3, 0.3, 0.08, 8, loc=tuple(R(0, 1.04, 0)), smooth=False)


@prop("aa_kit_rail_endcap", [], "P1", target=[0.5, 1.6, 0.5], origin="cap centre, felt level",
      notes="End cap: rounded snow cap + brass band closing an open rail end.", extra=dict(cls="kit", merge=False))
def rail_end(pb):
    skins.skin_wall(pb, 1, dict(id="e", center=[0, 0.25, 0], size=[0.5, 1.5, 0.5], yaw=0))
    hbox(pb, "Brass", (0, 0.55, 0), (0.512, 0.12, 0.512))


@prop("aa_kit_lantern_post", [], "P1", target=[1.0, 7.0, 1.0],
      origin="post base centre (ground)",
      notes="Brass lantern on a chunky timber post (89 world posts, world.json lantern_posts.positions). PointLight #FFB861 range 14 brightness 0.8 at the ember core (lights[]).",
      extra=dict(cls="kit", merge=False, lights=[dict(pos=[0, 6.1, 0], **LANTERN_LIGHT)],
                 world_instances=[dict(pos=p["pos"], yaw=0.0, note=p["path"]) for p in D.WORLD["lantern_posts"]["positions"]]))
def lantern_post(pb):
    hbox(pb, "Timber", (0, 2.75, 0), (0.8, 5.5, 0.8), bevel=0.08)
    hbox(pb, "Brass", (0, 5.2, 0), (0.86, 0.14, 0.86))
    hbox(pb, "Snow", (0, 0.12, 0), (1.0, 0.24, 1.0), bevel=0.1)
    lantern_head(pb, (0, 5.5, 0), 0.95)


@prop("aa_kit_lantern_post9", [], "P1", target=[1.0, 9.0, 1.0], origin="post base centre",
      notes="9-stud hole lantern post (props.md 'hole posts 9 high'); same head, PointLight #FFB861 r 14 b 0.8.",
      extra=dict(cls="kit", merge=False, lights=[dict(pos=[0, 8.1, 0], **LANTERN_LIGHT)]))
def lantern_post9(pb):
    hbox(pb, "Timber", (0, 3.75, 0), (0.9, 7.5, 0.9), bevel=0.08)
    hbox(pb, "Brass", (0, 7.2, 0), (0.96, 0.14, 0.96))
    hbox(pb, "Snow", (0, 0.12, 0), (1.1, 0.24, 1.1), bevel=0.1)
    lantern_head(pb, (0, 7.5, 0), 1.0)


def sign(pb, kind, off=0):
    if kind == "plank":
        H, Wd, D_, bh = 2.6, 1.6, 0.2, 0.9
    else:
        H, Wd, D_, bh = 3.2, 1.8, 0.25, 0.9
    top = H if kind == "plank" else 2.45
    hbox(pb, "Timber", (0, top / 2, 0), (0.18, top, 0.18), bevel=0.03)
    yb = top - bh / 2 - 0.12
    bx = off * (Wd / 2 + 0.05)          # off = -1 / +1: board swung to the left / right of the post (away from felt/rails)
    hbox(pb, "Cream", (bx, yb, 0), (Wd, bh, D_ - 0.04), bevel=0.04)
    hbox(pb, "Timber", (bx, yb + bh / 2 + 0.03, 0), (Wd, 0.08, D_), bevel=0.02)
    hbox(pb, "Snow", (bx, yb + bh / 2 + 0.1, 0), (Wd - 0.06, 0.08, D_ - 0.02), bevel=0.03)
    # arrow glyph (Ink) on the front (+Z) face, pointing up = 'this way'; text goes on a SurfaceGui
    zf = (D_ - 0.04) / 2 + 0.004
    hbox(pb, "Ink", (bx, yb - 0.12, zf), (0.16, 0.42, 0.008))
    prism = [(-0.32, 0.0), (0.32, 0.0), (0.0, 0.34)]
    t = bmesh.new()
    vs = [t.verts.new(R(bx + x, yb + 0.08 + y, zf + 0.004)) for x, y in prism]
    t.faces.new(vs)
    pb.add("Ink", t)
    if kind == "lantern":
        lantern_head(pb, (0, top, 0), 0.42)


@prop("aa_kit_sign_plank", [3, 9, 17], "P1", target=[1.6, 2.6, 0.2], origin="post base centre",
      front="+Z faces the approaching player (yaw from the anchor 'facing' = direction the sign points)",
      notes="Plank sign 1.6 x 2.6 x 0.2: timber post, cream board, snow cap, ink 'this way' arrow; wording on a SurfaceGui (front face).",
      extra=dict(cls="kit", merge=False))
def sign_plank(pb):
    sign(pb, "plank")


for _k, _o in (("plank", -1), ("plank", 1), ("lantern", -1), ("lantern", 1)):
    prop(f"aa_kit_sign_{_k}_{'L' if _o < 0 else 'R'}", [], "P1", target=[1.6, 2.6, 0.2] if _k == "plank" else [1.8, 3.2, 0.25],
         origin="post base centre", front="+Z faces the approaching player",
         notes=f"{_k} sign variant with the board swung to the {'left (-X)' if _o < 0 else 'right (+X)'} of the post, used where a centred board would cut a rail or overhang the felt.",
         extra=dict(cls="kit", merge=True, lights=[dict(pos=[0, 2.75, 0], range=8, brightness=0.4, color="#FFB861")] if _k == "lantern" else []))(lambda pb, k=_k, o=_o: sign(pb, k, o))


@prop("aa_kit_sign_lantern", [2, 3, 9, 11, 12, 14, 17], "P1", target=[1.8, 3.2, 0.25], origin="post base centre",
      front="+Z faces the approaching player",
      notes="Lantern sign 1.8 x 3.2 x 0.25 with a small brass lantern on top (PointLight #FFB861 r 8 b 0.4).",
      extra=dict(cls="kit", merge=False, lights=[dict(pos=[0, 2.75, 0], range=8, brightness=0.4, color="#FFB861")]))
def sign_lantern(pb):
    sign(pb, "lantern")


# ---------------------------------------------------------------------------------------------- geyser (one model, 2 uses)
def _geyser_world_scale():
    return [14 / 6.0, 10 / 7.0, 14 / 6.0]


GEYSER_H5 = [-19.0, 4.0, -33.0]       # holes.json anchor [-10.5, 4, -33] lies ON the upper felt; moved 8.5 west (see summary)


@prop("aa_kit_geyser_cone", [5], "P1", target=[6, 7, 6],
      placements=[dict(hole=5, pos=GEYSER_H5, yaw=0.0, note="H5 steamwhistle_geyser (moved west off the felt; holes.json anchor x -10.5)")],
      origin="cone base centre",
      notes="Steamwhistle Geyser basalt cone (ONE model). H5 instance at true size + aa_kit_geyser_puff_small on top; world instance (world.json steamwhistle_geyser [262,84,380], 14 x 10 x 14) = same mesh scaled [2.333,1.429,2.333] + aa_world_geyser_puff60 (60-stud steam column).",
      extra=dict(cls="kit", merge=True, anchor="steamwhistle_geyser",
                 world_instances=[dict(pos=[262.0, 84.0, 380.0], yaw=0.0, scale=_geyser_world_scale(), note="world.json backdrop steamwhistle_geyser (P2 set piece), runs the 60-stud puff")]))
def geyser_cone(pb):
    prof = [(3.0, 0.0), (2.75, 0.8), (2.35, 2.0), (1.95, 3.3), (1.55, 4.6), (1.15, 5.9), (0.95, 6.75), (0.9, 7.0), (0.55, 6.9), (0.5, 6.55)]
    pb.lathe("Basalt", prof, 10, wobble=0.08, seed=3, smooth=False)
    pb.lathe("Snow", [(2.62, 1.2), (2.42, 1.75), (2.36, 1.95), (2.0, 2.05)], 10, wobble=0.08, seed=3, smooth=True)
    pb.lathe("Snow", [(1.84, 3.7), (1.66, 4.25), (1.6, 4.45), (1.3, 4.55)], 10, wobble=0.08, seed=5, smooth=True)
    pb.cyl("Steam", 0.5, 0.5, 0.05, 8, loc=tuple(R(0, 6.6, 0)), smooth=False)
    # brass pressure pipe + gauge on the south flank
    pb.cyl("Brass", 0.12, 0.12, 2.2, 6, loc=tuple(R(0, 2.2, 2.45)), smooth=False)
    pb.cyl("Brass", 0.32, 0.32, 0.12, 10, loc=tuple(R(0, 3.35, 2.25)), rot=(90, 0, 0), smooth=False)
    pb.cyl("Ink", 0.25, 0.25, 0.02, 10, loc=tuple(R(0, 3.35, 2.32)), rot=(90, 0, 0), smooth=False)


@prop("aa_kit_geyser_puff_small", [5], "P1", target=[2.6, 6, 2.6],
      placements=[dict(hole=5, pos=[GEYSER_H5[0], GEYSER_H5[1] + 6.9, GEYSER_H5[2]], yaw=0.0, note="on the H5 cone vent")],
      origin="vent (bottom centre of the puff)", kind="animated",
      notes="Small steam puff for the H5 cone (separate mesh; script scales/fades it). Steam #E9FBFF, Transparency 0.5; particles in game.",
      extra=dict(cls="mover_aux", merge=False, anchor="steamwhistle_geyser"))
def puff_small(pb):
    for i, (r, y) in enumerate([(0.75, 0.6), (1.0, 1.9), (1.2, 3.3), (1.0, 4.8)]):
        pb.rock("Steam", (2 * r, 2 * r, 1.6 * r), loc=tuple(R(0.2 * math.sin(i), y - 0.6 * r, 0.2 * math.cos(i))), seed=i, amp=0.12, ico=1, flat_bottom=False, smooth=True)


@prop("aa_world_geyser_puff60", [], "P1", target=[14, 60, 14], origin="vent (bottom centre)", kind="animated",
      notes="60-stud steam column for the WORLD geyser cone instance (puffs every 20 s; visual only).",
      extra=dict(cls="world", merge=False,
                 world_instances=[dict(pos=[262.0, 84.0 + 10.0, 380.0], yaw=0.0, note="on the world cone vent (cone top 84+10)")]))
def puff60(pb):
    y = 0.0
    k = 0
    while y < 60:
        r = 1.6 + 5.4 * (y / 60) ** 0.8
        pb.rock("Steam", (2 * r, 2 * r, 1.7 * r), loc=tuple(R(1.2 * math.sin(k * 1.7), y + 0.7 * r, 1.2 * math.cos(k * 1.3))), seed=10 + k, amp=0.15, ico=1, flat_bottom=False, smooth=True)
        y += r * 1.05
        k += 1


# ---------------------------------------------------------------------------------------------- teleports, lifts, gondola
@prop("aa_kit_teleport_pad", [], "P1", target=[4, 0.1, 4], origin="pad top centre",
      notes="Teleport pad 4 x 0.1 x 4 with an aurora-lime ring (8 pads, world.json teleport_points).",
      extra=dict(cls="world", merge=False, lights=[dict(pos=[0, 0.6, 0], range=8, brightness=0.5, color="#D8FF6A")],
                 world_instances=[dict(pos=t["pos"], yaw=0.0, note=t["id"]) for t in D.WORLD["teleport_points"]]))
def teleport_pad(pb):
    hbox(pb, "Basalt", (0, -0.05, 0), (4, 0.1, 4), bevel=0.03)
    pb.torus("Lime", 1.5, 0.12, 24, 4, loc=tuple(R(0, 0.0, 0)), smooth=False)
    for k in range(4):
        x, z = D.yaw_rot(1.8, 0, 90 * k + 45)
        hbox(pb, "Brass", (x, 0.02, z), (0.3, 0.04, 0.3), 90 * k + 45)


@prop("aa_kit_tee_arrival_pad", [], "P1", target=[4, 0.05, 4], origin="pad centre at ground",
      notes="Next-tee teleport arrival pad r 2, flush glow ring (world.json holes[].tee_teleport, 3 studs behind each tee).",
      extra=dict(cls="world", merge=False,
                 world_instances=[dict(pos=D.tee_teleport(n)["pos"], yaw=0.0, note=f"H{n} tee_teleport") for n in sorted(D.H) if D.tee_teleport(n)]))
def tee_pad(pb):
    pb.cyl("SnowShadow", 2.0, 2.0, 0.04, 24, loc=tuple(R(0, 0.02, 0)), smooth=False)
    pb.torus("Lime", 1.72, 0.1, 24, 4, loc=tuple(R(0, 0.04, 0)), smooth=False)


def _lift_instances():
    out = []
    for L in D.WORLD["lifts"]:
        out.append(dict(pos=L["bottom"], yaw=0.0, note=L["name"] + " cage at the bottom stop (rides to top " + str(L["top"]) + ")"))
    return out


@prop("aa_kit_lift_cage", [], "P1", target=[10, 9, 10], origin="floor top centre",
      notes="Open-sided lift cage, 10 x 10 solid floor, 3.5-stud railings all round, brass frame and snowy roof (x4 lifts; builder animates bottom->top).",
      extra=dict(cls="world", merge=False, lights=[dict(pos=[0, 8.0, 0], range=12, brightness=0.6, color="#FFB861")],
                 world_instances=_lift_instances()))
def lift_cage(pb):
    hbox(pb, "Timber", (0, -0.2, 0), (10, 0.4, 10), bevel=0.05)
    for dx in (-1, 1):
        for dz in (-1, 1):
            hbox(pb, "Brass", (dx * 4.8, 4.4, dz * 4.8), (0.4, 8.8, 0.4))
    for k in range(4):
        for y, h in ((3.5, 0.3), (1.2, 0.2)):
            x, z = D.yaw_rot(0, 4.8, 90 * k)
            hbox(pb, "Timber", (x, y, z), (9.2, h, 0.3), 90 * k, bevel=0.04)
        x, z = D.yaw_rot(0, 4.8, 90 * k)
        hbox(pb, "Snow", (x, 3.72, z), (9.2, 0.14, 0.34), 90 * k, bevel=0.05)
        hbox(pb, "Brass", (x, 8.7, z), (10, 0.25, 0.3), 90 * k)
    hbox(pb, "Snow", (0, 9.0, 0), (10.4, 0.35, 10.4), bevel=0.15)
    pb.torus("Brass", 0.6, 0.1, 10, 4, loc=tuple(R(0, 9.6, 0)), rot=(90, 0, 0), smooth=False)
    lantern_head(pb, (0, 7.3, 0), 0.6, cap=None)


@prop("aa_kit_gondola_cabin", [], "P1", target=[6, 8, 6], origin="cabin floor centre",
      notes="Snowpuff Sky Gondola cabin: enclosed glazed lantern cabin 6 x 6 with a brass hanger arm and cable grip (y 8).",
      extra=dict(cls="world", merge=False, lights=[dict(pos=[0, 4.2, 0], range=10, brightness=0.6, color="#FFB861")],
                 world_instances=[dict(pos=[-204.0, 60.0, 604.0], yaw=0.0, note="bottom terminal (path p_gondola start)")]))
def gondola(pb):
    hbox(pb, "Timber", (0, 0.4, 0), (6, 0.8, 6), bevel=0.1)
    hbox(pb, "Timber", (0, 4.6, 0), (6, 0.6, 6), bevel=0.1)
    for dx in (-1, 1):
        for dz in (-1, 1):
            hbox(pb, "Brass", (dx * 2.85, 2.6, dz * 2.85), (0.3, 3.6, 0.3))
    for k in range(4):
        x, z = D.yaw_rot(0, 2.9, 90 * k)
        hbox(pb, "Ice", (x, 2.6, z), (5.4, 3.4, 0.12), 90 * k)
        hbox(pb, "Timber", (x, 1.25, z), (5.4, 0.9, 0.2), 90 * k)
    pb.cyl("Snow", 4.3, 0.6, 1.0, 4, loc=tuple(R(0, 5.4, 0)), rot=(0, 0, 45), smooth=False)
    hbox(pb, "Brass", (0, 6.9, 0), (0.3, 2.2, 0.3))
    hbox(pb, "Brass", (0, 8.0, 0), (1.6, 0.4, 0.6))
    lantern_head(pb, (0, 3.4, 0), 0.6, cap=None)


@prop("aa_kit_gondola_station", [], "P1", target=[12, 12, 12], origin="platform top centre",
      notes="Gondola station 12 x 12 x 12, walk-through (roof frame >= 9.5 clear), bullwheel, lantern roof (x2).",
      extra=dict(cls="world", merge=False, lights=[dict(pos=[0, 8.6, 0], range=16, brightness=0.8, color="#FFB861")],
                 world_instances=[dict(pos=b["pos"], yaw=0.0, note=b["id"]) for b in D.WORLD["backdrop"]["pieces"] if b["id"].startswith("gondola_")]))
def station(pb):
    hbox(pb, "Timber", (0, -0.2, 0), (12, 0.4, 12), bevel=0.05)
    for dx in (-1, 1):
        for dz in (-1, 1):
            hbox(pb, "Timber", (dx * 5.5, 4.9, dz * 5.5), (1.0, 9.8, 1.0), bevel=0.08)
            hbox(pb, "Snow", (dx * 5.5, 0.15, dz * 5.5), (1.2, 0.3, 1.2), bevel=0.1)
    for k in range(4):
        x, z = D.yaw_rot(0, 5.5, 90 * k)
        hbox(pb, "Timber", (x, 9.9, z), (12, 0.6, 0.6), 90 * k)
    pb.cyl("Snow", 9.3, 0.8, 2.3, 4, loc=tuple(R(0, 11.0, 0)), rot=(0, 0, 45), smooth=False)
    pb.torus("Brass", 3.4, 0.25, 20, 6, loc=tuple(R(0, 9.4, 0)), smooth=False)
    lantern_head(pb, (0, 7.6, 0), 0.9, cap=None)


# ---------------------------------------------------------------------------------------------- bridges and stairs
def _bridge_instances(style):
    out = []
    for p in D.WORLD["paths"]:
        for s in p["segments"]:
            if s["type"] == "bridge" and s.get("style") == style:
                a, b = s["start"], s["end"]
                dx, dz = b[0] - a[0], b[2] - a[2]
                L = math.hypot(dx, dz)
                ux, uz = dx / L, dz / L
                yaw = round(math.degrees(math.atan2(-ux, -uz)), 3)
                n = int(math.ceil(L / 4 - 1e-6))
                for i in range(n):
                    seg = min(4.0, L - 4 * i)
                    c = 4 * i + seg / 2
                    out.append(dict(pos=[round(a[0] + ux * c, 3), a[1], round(a[2] + uz * c, 3)], yaw=yaw,
                                    scale=[1, 1, round(seg / 4, 4)], note=s.get("name", p["id"])))
    return out


def _bridge(pb, deck):
    hbox(pb, deck, (0, -0.3, 0), (6, 0.6, 4))
    for side in (-1, 1):
        hbox(pb, "Timber", (side * 3.05, 1.75, 1.85), (0.4, 3.5, 0.3), bevel=0.04)
        hbox(pb, "Timber", (side * 3.05, 3.4, 0), (0.3, 0.3, 4))
        hbox(pb, "Snow", (side * 3.05, 3.6, 0), (0.36, 0.12, 4), bevel=0.04)
        hbox(pb, "Timber", (side * 3.05, 0.8, 0), (0.15, 1.0, 4))
    hbox(pb, "IceCore", (0, -0.61, 0), (1.0, 0.02, 4))


@prop("aa_kit_bridge_ice_4", [], "P1", target=[6.4, 3.7, 4], origin="deck top centre of a 4-stud module (run along local Z)",
      notes="Glass-ice bridge module (deck 6 wide x 0.6, railings 3.5 both sides). Instanced every 4 studs along Glimmer and Coral Ice Bridges; last module scale Z = remainder/4.",
      extra=dict(cls="world", merge=False, world_instances=_bridge_instances("ice")))
def bridge_ice(pb):
    _bridge(pb, "Ice")


@prop("aa_kit_bridge_aurora_4", [], "P1", target=[6.4, 3.7, 4], origin="deck top centre of a 4-stud module",
      notes="Aurora Skybridge module: Neon aurora-teal deck, same railings; instanced along the 134.5-stud skybridge.",
      extra=dict(cls="world", merge=False, world_instances=_bridge_instances("aurora")))
def bridge_aurora(pb):
    _bridge(pb, "AuroraTeal")


def _stairs_instances(nsteps):
    out = []
    for p in D.WORLD["paths"]:
        for s in p["segments"]:
            if s["type"] == "stairs" and s["steps"] == nsteps:
                a, b = s["start"], s["end"]
                if b[1] < a[1]:
                    a, b = b, a
                dx, dz = b[0] - a[0], b[2] - a[2]
                L = math.hypot(dx, dz)
                yaw = round(math.degrees(math.atan2(-dx / L, -dz / L)), 3)
                out.append(dict(pos=a, yaw=yaw, note=s.get("name", p["id"])))
    return out


def _stairs(pb, n):
    for i in range(n):
        y = 0.8 * (i + 1)
        z = -1.5 * i - 0.75
        hbox(pb, "Timber", (0, y / 2, z), (6, y, 1.5))
        hbox(pb, "Snow", (0, y + 0.04, z + 0.6), (5.9, 0.08, 0.3))
    L = 1.5 * n
    for side in (-1, 1):
        for i in range(0, n + 1, 2):
            hbox(pb, "Timber", (side * 3.05, 0.8 * i + 1.75, -1.5 * i + (0.15 if i == 0 else 0)), (0.3, 3.5, 0.3))
        rail_len = math.hypot(L, 0.8 * n)
        ang = math.degrees(math.atan2(0.8 * n, L))
        hbox(pb, "Timber", (side * 3.05, 0.4 * n + 3.4, -L / 2), (0.3, 0.3, rail_len), pitch=-ang)
        hbox(pb, "Snow", (side * 3.05, 0.4 * n + 3.6, -L / 2), (0.36, 0.12, rail_len), pitch=-ang)


@prop("aa_kit_stair_flight_10", [], "P1", target=[6.6, 11.5, 15], origin="bottom of the flight (first riser), centre; climbs toward local -Z",
      notes="Lantern Stair flight: 10 steps x rise 0.8 x tread 1.5, width 6, railings 3.5 both sides.",
      extra=dict(cls="world", merge=False, world_instances=_stairs_instances(10)))
def stairs10(pb):
    _stairs(pb, 10)


@prop("aa_kit_stair_flight_5", [], "P1", target=[6.6, 7.5, 7.5], origin="bottom of the flight, centre; climbs toward local -Z",
      notes="5-step flight (Steam Walk, Crystal Lift stairs).", extra=dict(cls="world", merge=False, world_instances=_stairs_instances(5)))
def stairs5(pb):
    _stairs(pb, 5)


# ---------------------------------------------------------------------------------------------- world heroes
@prop("aa_world_starfrost_spire", [], "P1", target=[64, 240, 64], origin="spire base centre (world [0,100,-40])",
      notes="Faceted aurora-crystal spire (glass ice shell + crystal-core neon + mint/violet bands). Visible from all tees; tip y 340. Orbiting shards = aa_world_spire_shards.",
      extra=dict(cls="world", merge=False, lights=[dict(pos=[0, 120, 0], range=60, brightness=1.0, color="#8FE3FF")],
                 world_instances=[dict(pos=[0.0, 100.0, -40.0], yaw=0.0, note="world.json backdrop starfrost_spire")]))
def spire(pb):
    prof = [(32, 0), (27, 30), (21, 110), (15, 170), (8, 215), (3, 236), (0, 240)]
    pb.lathe("Ice", prof, 8, smooth=False, phase=math.pi / 8)
    pb.lathe("IceCore", [(r * 0.55, y) for r, y in prof[:-1]] + [(0, 232)], 8, smooth=False)
    def rad_at(y):
        for (ra, ya), (rb, yb) in zip(prof, prof[1:]):
            if ya <= y <= yb:
                return ra + (rb - ra) * (y - ya) / (yb - ya)
        return 0.0
    for y0, y1, m in ((40, 46, "AuroraMint"), (120, 125, "AuroraTeal"), (190, 194, "AuroraViolet")):
        pb.lathe(m, [(rad_at(y0) + 0.5, y0), (rad_at(y1) + 0.5, y1)], 8, smooth=False, phase=math.pi / 8)
    for k in range(6):
        a = k * 60 + 15
        x, z = D.yaw_rot(0, 26, a)
        pb.lathe("Ice", [(5, 0), (4, 22), (0, 34)], 6, loc=tuple(R(x, 0, z)), smooth=False)


@prop("aa_world_spire_shards", [], "P1", target=[180, 160, 180], origin="spire base centre (spin about Y)", kind="animated",
      notes="Orbiting crystal shards r 50-90 (separate mesh, slow spin about the spire axis).",
      extra=dict(cls="world", merge=False, world_instances=[dict(pos=[0.0, 100.0, -40.0], yaw=0.0, note="spin 2 deg/s about +Y")]))
def shards(pb):
    for k in range(10):
        a = k * 36 + (k % 3) * 7
        r = 50 + 40 * ((k * 37) % 10) / 10
        y = 60 + 14 * k
        L = 8 + (k % 4) * 2
        x, z = D.yaw_rot(0, r, a)
        mtx = Matrix.Translation(R(x, y, z)) @ Matrix.Rotation(math.radians(25 + k * 11), 4, "X")
        pb.cyl("Ice", L * 0.22, 0.0, L, 6, matrix=mtx, smooth=False)
        pb.cyl("IceCore", L * 0.1, 0.0, L * 0.7, 6, matrix=mtx, smooth=False)


@prop("aa_world_great_frozen_falls", [15], "P1", target=[26, 146, 8], origin="top centre of the falls (world.json [20,182,-398])",
      notes="The Great Frozen Falls: 26-wide frozen cascade pouring north off the Icefall Terraces rim into the clouds (world.json waterfalls 'Great Frozen Falls' top y 182 -> bottom y 36). The H15 anchor [13.5,-4,-30] is a view cue.",
      extra=dict(cls="world", merge=False, lights=[dict(pos=[0, -20, -3], range=30, brightness=0.6, color="#8FE3FF")],
                 world_instances=[dict(pos=[20.0, 182.0, -398.0], yaw=0.0, note="world.json waterfalls Great Frozen Falls")]))
def frozen_falls(pb):
    for k in range(9):
        x = -12 + 3 * k
        r = 1.6 + 0.9 * math.sin(k * 1.9) ** 2
        pts = []
        rad = []
        for j in range(9):
            y = -146 * (j / 8) ** 1.0
            bulge = -2.0 - 2.0 * math.sin(math.pi * j / 8) - 0.6 * math.sin(k * 2.3 + j)
            pts.append(R(x + 0.4 * math.sin(j + k), y, bulge))
            rad.append(r * (1.0 + 0.25 * math.sin(j * 1.3 + k)))
        pb.tube("Ice", pts, rad, segs=6, smooth=False)
        pb.tube("IceCore", pts, [q * 0.35 for q in rad], segs=5, smooth=False)
    hbox(pb, "Ice", (0, -73, -0.5), (26, 146, 1.0))
    hbox(pb, "Snow", (0, 0.2, -1.5), (27, 0.6, 3.0), bevel=0.2)
