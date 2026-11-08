"""Pro Shop pavilion v1 — first detailed model of selected Art concept A (sage / timber park pavilion).

Builds an editable, packed .blend: named, grouped, split meshes; UVs on every mesh; packed
procedural textures; anchors; hidden collision proxies; render-only environment + cameras.

Usage (portable; no absolute paths baked in):
  blender --background --factory-startup --python generate_pavilion.py -- \
          --output <pro_shop_pavilion_v1.blend> [--texdir <dir>] [--font <ttf>] [--seed 7]

Units: 1 Blender unit = 1 Roblox stud, Z up. Open shop front faces -Y. Asset origin is the
ground centre of the plinth footprint (0,0,0). Every mesh has identity rotation/scale; each
object's origin is its bounding-box base centre (static-prop pivot).
"""
import argparse
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pavilion_lib as L  # noqa: E402

# ----------------------------------------------------------------------------- key dimensions
PL = 0.12            # plinth top = floor the player stands on at the counter (approach ramps to it)
CT = 3.15            # counter top (3.03 above approach at the counter)
PX = 9.3             # post centre |x|
PH = 0.425           # post half size (0.85 chunky posts)
FY, RY = -4.1, 3.8   # front / rear post centre y
POST_TOP = 6.35
TH = math.radians(28.0)
TN, CO, SN = math.tan(TH), math.cos(TH), math.sin(TH)
ZU0 = 12.12          # roof deck underside at ridge
EAVE_X = 10.9        # deck edge |x|
ROOF_Y0, ROOF_Y1 = -5.4, 5.1
DECK_T, T0, TILE_T = 0.12, 0.16, 0.10
RW_IN = 3.62         # rear wall interior face y
S_EAVE = EAVE_X / CO


def zu(x):
    return ZU0 - TN * abs(x)


def slope_pt(side, s, t, y):
    """Roof frame: s along slope from ridge (down), t perpendicular up from deck underside."""
    x = s * CO + t * SN
    z = ZU0 - s * SN + t * CO
    return (side * x, y, z)


# ----------------------------------------------------------------------------- helpers
def coll(name, parent, export=True, hide_render=False):
    c = bpy.data.collections.new(name)
    parent.children.link(c)
    c["ps_export"] = export
    c.hide_render = hide_render
    return c


def board_spans(a0, a1, rng, target=0.55, breaks=()):
    pts = sorted([a0, a1] + [b for b in breaks if a0 + 1e-6 < b < a1 - 1e-6])
    out = []
    for s0, s1 in zip(pts[:-1], pts[1:]):
        n = max(1, round((s1 - s0) / target))
        ws = [rng.uniform(0.84, 1.16) for _ in range(n)]
        tot, x = sum(ws), s0
        for w in ws:
            x1 = x + (s1 - s0) * w / tot
            out.append((x, x1))
            x = x1
    return out


def wall_boards(mb, orient, plane, thick, a0, a1, z0, ztop, rng, holes=(), breaks=(), bevel=0.018,
                target=0.55):
    """Vertical boards. orient 'x': along x on plane y=plane; 'y': along y on plane x=plane.
    ztop: float or f(coord along wall). holes: (a0, a1, z0, z1) openings aligned to breaks."""
    zt = ztop if callable(ztop) else (lambda a, v=ztop: v)
    for b0, b1 in board_spans(a0, a1, rng, target, breaks):
        d = rng.uniform(-0.012, 0.012)
        segs = [(z0, None)]
        for (h0, h1, hz0, hz1) in holes:
            if b0 >= h0 - 1e-6 and b1 <= h1 + 1e-6:
                segs = [(z0, hz0), (hz1, None)]
        for zs, ze in segs:
            if orient == "x":
                f = None if ze else (lambda x, y: zt(x))
                mb.box(b0, b1, plane - thick / 2 + d, plane + thick / 2 + d, zs, ze or 0, ztop=f,
                       long_axis=2, bevel=bevel)
            else:
                f = None if ze else (lambda x, y: zt(y))
                mb.box(plane - thick / 2 + d, plane + thick / 2 + d, b0, b1, zs, ze or 0, ztop=f,
                       long_axis=2, bevel=bevel)


def leaf(mb, base, yaw, pitch, length, width, cell, droop=0.08):
    d = Vector((math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), math.sin(pitch)))
    s = Vector((-math.sin(yaw), math.cos(yaw), 0))
    n = d.cross(s).normalized()
    if n.z < 0:
        n = -n
    B = Vector(base)
    Lp = B + d * length * 0.42 + s * width / 2
    Rp = B + d * length * 0.42 - s * width / 2
    T = B + d * length - Vector((0, 0, droop))
    V = B + d * length * 0.45 + n * 0.035
    front = [B, V, Lp, Rp, T]
    back = [p - n * 0.006 for p in front]
    pts = [tuple(p) for p in front + back]
    faces = [(0, 2, 1), (0, 1, 3), (2, 4, 1), (1, 4, 3),
             (5, 6, 7), (5, 8, 6), (7, 6, 9), (6, 8, 9)]
    mb.faces(pts, faces, cell=cell, long_axis=None, smooth=False)


def plant(mb, base, rng, n_leaves=10, scale=1.0, pot=True, cells=("leaf_a", "leaf_b")):
    bx, by, bz = base
    xf = Matrix.Translation(base) @ Matrix.Scale(scale, 4)
    soil_z = bz
    if pot:
        prof = [(0.15, 0), (0.19, 0.03), (0.22, 0.32), (0.255, 0.335), (0.255, 0.40), (0.215, 0.40),
                (0.205, 0.37)]
        mb.lathe(prof, 14, xf, cap_bottom=True, cap_top=False, cell=L.pal_cell("pot_cream"))
        mb.lathe([(0.205, 0.355), (0.0, 0.356)], 14, xf, cap_bottom=False, cell=L.pal_cell("soil"),
                 smooth=False)
        soil_z = bz + 0.355 * scale
    for i in range(n_leaves):
        yaw = 2 * math.pi * i / n_leaves + rng.uniform(-0.25, 0.25)
        pitch = math.radians(rng.uniform(32, 68))
        leaf(mb, (bx + rng.uniform(-0.02, 0.02), by + rng.uniform(-0.02, 0.02), soil_z), yaw, pitch,
             rng.uniform(0.38, 0.52) * scale, rng.uniform(0.15, 0.2) * scale,
             L.pal_cell(cells[i % 2]), droop=0.09 * scale)


def text_curve(name, body, size, loc, coll_, mat, font, extrude=0.0, align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.align_x = align
    cu.align_y = "CENTER"
    cu.extrude = extrude
    if font:
        cu.font = font
    cu.materials.append(mat)
    ob = bpy.data.objects.new(name, cu)
    ob.location = loc
    ob.rotation_euler = (math.pi / 2, 0, 0)  # text faces -Y, reads left->right from the front
    coll_.objects.link(ob)
    return ob


def text_to_mesh(src, name, coll_, mat, cell):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(src.evaluated_get(dg))
    me.transform(src.matrix_world)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    mb = L.MB(name, mat)
    pts = [tuple(v.co) for v in bm.verts]
    idx = {v: i for i, v in enumerate(bm.verts)}
    mb.faces(pts, [tuple(idx[v] for v in f.verts) for f in bm.faces], cell=cell, long_axis=0)
    bm.free()
    bpy.data.meshes.remove(me)
    return mb.build(coll_)


# ----------------------------------------------------------------------------- main build
def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--texdir", default=None)
    ap.add_argument("--font", default=None)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args(argv)
    out = os.path.abspath(a.output)
    texdir = os.path.abspath(a.texdir or os.path.join(os.path.dirname(out), "textures"))
    os.makedirs(texdir, exist_ok=True)

    bpy.ops.wm.read_factory_settings(use_empty=True)
    rng = random.Random(a.seed)
    nrng = L.np.random.default_rng(a.seed)
    scene = bpy.context.scene
    scene.name = "ProShop_Pavilion_v1"
    scene.unit_settings.system = "NONE"

    # ---------------- textures + materials
    I = {}
    I["wood_warm"] = L.make_image("T_Wood_Warm", L.tex_wood(512, (0.74, 0.50, 0.29), (0.55, 0.35, 0.19), nrng), texdir)
    I["wood_dark"] = L.make_image("T_Wood_Dark", L.tex_wood(512, (0.50, 0.32, 0.18), (0.34, 0.21, 0.11), nrng), texdir)
    I["cream"] = L.make_image("T_Paint_Cream", L.tex_paint(512, (0.93, 0.87, 0.72), nrng), texdir)
    I["sage"] = L.make_image("T_Paint_Sage", L.tex_paint(512, (0.47, 0.58, 0.41), nrng), texdir)
    I["tile"] = L.make_image("T_Roof_Tile_Sage", L.tex_tile(512, (0.43, 0.57, 0.38), nrng), texdir)
    I["stone"] = L.make_image("T_Stone_Flag", L.tex_stone(512, (0.70, 0.66, 0.58), nrng), texdir)
    pc, pm, pr = L.tex_palette(256)
    I["pal_c"] = L.make_image("T_Props_Palette_Color", pc, texdir)
    I["pal_m"] = L.make_image("T_Props_Palette_Metalness", pm, texdir, non_color=True)
    I["pal_r"] = L.make_image("T_Props_Palette_Roughness", pr, texdir, non_color=True)
    I["balls"] = L.make_image("T_Ball_Skins_Atlas", L.tex_balls(256), texdir)
    I["prints"] = L.make_image("T_Art_Prints_Golf", L.tex_prints(256), texdir)

    M = {
        "wood": L.material("M_Wood_Warm", I["wood_warm"], rough=0.74),
        "wood_dark": L.material("M_Wood_Dark", I["wood_dark"], rough=0.7),
        "cream": L.material("M_Paint_Cream", I["cream"], rough=0.72),
        "sage": L.material("M_Paint_Sage", I["sage"], rough=0.72),
        "tile": L.material("M_Roof_Tile_Sage", I["tile"], rough=0.78),
        "stone": L.material("M_Stone_Flag", I["stone"], rough=0.88),
        "pal": L.material("M_Props_Palette", I["pal_c"], metal_img=I["pal_m"], rough_img=I["pal_r"]),
        "balls": L.material("M_Ball_Skins", I["balls"], rough=0.38),
        "prints": L.material("M_Art_Prints", I["prints"], rough=0.55),
        "display": L.material("M_UI_Display_Placeholder", color=(0.07, 0.11, 0.16), rough=0.25, emission=0.6),
        "ui_pal": L.material("M_UI_Overlay_ILLUSTRATIVE", I["pal_c"], rough=0.5, emission=0.9, export=False),
        "ui_balls": L.material("M_UI_Icons_ILLUSTRATIVE", I["balls"], rough=0.5, emission=0.9, export=False),
        "ui_text": L.material("M_UI_Text_ILLUSTRATIVE", color=(0.96, 0.96, 0.94), emission=1.2, export=False),
        "ui_text_dark": L.material("M_UI_TextDark_ILLUSTRATIVE", color=(0.07, 0.10, 0.12), export=False),
        "ui_note": L.material("M_UI_Note_ILLUSTRATIVE", color=(0.62, 0.66, 0.70), emission=0.7, export=False),
        "col": L.material("M_Collision_Proxy", color=(1.0, 0.2, 0.6), export=False),
    }

    font = None
    cands = [a.font] if a.font else []
    cands += [os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", f) for f in ("segoeuib.ttf", "arialbd.ttf")]
    for fp in cands:
        if fp and os.path.exists(fp):
            font = bpy.data.fonts.load(fp)
            font.pack()
            break

    # ---------------- collections
    root = coll("PS_Pavilion_v1", scene.collection)
    C = {k: coll(k, root) for k in ("PS_Structure", "PS_Walls", "PS_Windows", "PS_Roof", "PS_Counter",
                                     "PS_BallTray", "PS_Dish", "PS_ClubRack", "PS_Items_Balls",
                                     "PS_Items_Clubs", "PS_Decor", "PS_UI_Display")}
    C["ui"] = coll("PS_UI_Placeholder_ILLUSTRATIVE", root, export=False)
    C["anchors"] = coll("PS_Anchors", root, export=False)
    C["col"] = coll("PS_Collision_Proxy", root, export=False, hide_render=True)
    C["src"] = coll("PS_Source_EditableText", root, export=False, hide_render=True)
    env = coll("ENV_RenderOnly", scene.collection, export=False)

    def mb(name, m, scale=4.0):
        return L.MB(name, M[m], uv_scale=scale, seed=a.seed)

    S = C["PS_Structure"]
    # ================================================================== STRUCTURE
    p = mb("Plinth_Stone", "stone", 3.0)
    p.box(-10.0, 10.0, -4.85, 4.55, 0.0, PL, bevel=0.03)
    p.build(S)

    # level approach: ramp 0 -> PL over 3.35 studs (~2 deg) + flagstones
    def ramp(x, y):
        return PL * (y + 8.2) / (8.2 - 4.85)
    p = mb("Approach_Base", "pal")
    p.box(-7.0, 7.0, -8.2, -4.85, -0.08, 0, ztop=lambda x, y: ramp(x, y), cell=L.pal_cell("underlay"))
    p.build(S)
    p = mb("Approach_Flagstones", "stone", 3.0)
    cols, rows = 7, 3
    for i in range(cols):
        for j in range(rows):
            x0, x1 = -7.0 + 14.0 * i / cols, -7.0 + 14.0 * (i + 1) / cols
            y0, y1 = -8.2 + 3.35 * j / rows, -8.2 + 3.35 * (j + 1) / rows
            if j % 2:
                x0, x1 = x0 + 1.0, x1 + 1.0
                if i == cols - 1:
                    x1 = 7.0
            if j % 2 and i == 0:
                p.box(-7.0 + 0.04, x0 - 0.04, y0 + 0.04, y1 - 0.04, 0, 0,
                      zbot=lambda x, y: ramp(x, y) - 0.02, ztop=lambda x, y: ramp(x, y) + 0.03, bevel=0.02)
            jit = [rng.uniform(-0.1, 0.1) for _ in range(4)]
            c = [(x0 + 0.05 + jit[0], y0 + 0.05), (x1 - 0.05 + jit[1], y0 + 0.05),
                 (x1 - 0.05 + jit[2], y1 - 0.05), (x0 + 0.05 + jit[3], y1 - 0.05)]
            c = [(min(max(x, -6.96), 6.96), y) for x, y in c]
            pts = [(x, y, ramp(x, y) - 0.02) for x, y in c] + [(x, y, ramp(x, y) + 0.03) for x, y in c]
            p.hexa(pts, bevel=0.02, long_axis=None)
    p.build(S)

    posts = {}
    for nm, sx, py in (("FL", -1, FY), ("FR", 1, FY), ("RL", -1, RY), ("RR", 1, RY)):
        p = mb(f"Post_{nm}", "wood", 4.0)
        p.box(sx * PX - PH, sx * PX + PH, py - PH, py + PH, PL, POST_TOP, bevel=0.06, long_axis=2)
        posts[nm] = p.build(S)
        p = mb(f"PostShoe_{nm}", "wood_dark", 2.0)
        p.box(sx * PX - 0.53, sx * PX + 0.53, py - 0.53, py + 0.53, PL, 0.44, bevel=0.035)
        p.build(S)

    p = mb("Beam_FrontTie", "wood", 4.0)
    p.box(-9.76, 9.76, FY - PH, FY + PH, 6.25, 6.95, bevel=0.05, long_axis=0)
    p.build(S)
    p = mb("Beam_RearTie", "wood", 4.0)
    p.box(-9.76, 9.76, 3.80, RY + PH, 6.25, 6.95, bevel=0.05, long_axis=0)
    p.build(S)
    for nm, sx in (("L", -1), ("R", 1)):
        p = mb(f"Beam_SidePlate_{nm}", "wood", 4.0)
        p.box(sx * PX - PH, sx * PX + PH, -5.15, 4.85, 6.3, 6.9, bevel=0.05, long_axis=1)
        p.build(S)
    p = mb("Braces_Front", "wood", 3.0)
    for sx in (-1, 1):
        poly = [(sx * 8.9, 4.85), (sx * 8.9, 5.35), (sx * 7.95, 6.27), (sx * 7.45, 6.27)]
        p.prism(poly, FY - 0.17, FY + 0.17, axis="y", bevel=0.03, long_axis=0)
    p.build(S)
    p = mb("KingPost_Front", "wood", 4.0)
    p.box(-0.3, 0.3, -4.5, -4.18, 6.95, zu(0.3) - 0.01, bevel=0.04, long_axis=2)
    p.build(S)
    p = mb("KingPost_Rear", "wood", 4.0)
    p.box(-0.3, 0.3, 3.80, 4.12, 6.95, zu(0.3) - 0.01, bevel=0.04, long_axis=2)
    p.build(S)
    p = mb("Beam_Ridge", "wood", 4.0)
    p.box(-0.25, 0.25, -5.22, 4.92, 11.45, zu(0.25) - 0.005, bevel=0.04, long_axis=1)
    p.build(S)
    # rafters (incl. top chords of both gables) + mid collar truss
    p = mb("Rafters", "wood", 4.0)
    for ry in (FY, -2.1, 0.0, 2.1, RY):
        for sx in (-1, 1):
            x0, x1 = 0.25, 10.85
            poly = [(sx * x0, zu(x0) - 0.45), (sx * x1, zu(x1) - 0.45), (sx * x1, zu(x1) - 0.005),
                    (sx * x0, zu(x0) - 0.005)]
            p.prism(poly, ry - 0.15, ry + 0.15, axis="y", bevel=0.025, long_axis=0)
    p.build(S)
    p = mb("Truss_Mid_Collar", "wood", 4.0)
    p.box(-5.3, 5.3, -0.18, 0.18, 8.55, 9.0, bevel=0.035, long_axis=0)
    p.box(-0.22, 0.22, -0.18, 0.18, 9.0, 11.46, bevel=0.03, long_axis=2)
    p.build(S)

    # trims: base sill, waist rail (sage/cream boundary), eave frieze blocking
    p = mb("Trim_Base", "wood_dark", 4.0)
    for sx in (-1, 1):
        p.box(sx * PX - 0.17, sx * PX + 0.17, FY + PH, RY - PH, PL, 0.5, bevel=0.03, long_axis=1)
    p.box(-PX + PH, PX - PH, 3.54, 3.88, PL, 0.5, bevel=0.03, long_axis=0)
    p.build(S)
    p = mb("Trim_Waist", "wood", 4.0)
    for sx in (-1, 1):
        p.box(sx * PX - 0.15, sx * PX + 0.15, FY + PH, RY - PH, 3.15, 3.38, bevel=0.03, long_axis=1)
    p.box(-PX + PH, PX - PH, 3.56, 3.86, 3.15, 3.38, bevel=0.03, long_axis=0)
    p.build(S)
    p = mb("Trim_EaveFrieze", "wood", 4.0)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (PX - 0.09), sx * (PX + 0.09)))
        p.box(x0, x1, -5.15, 4.85, 6.9, 0, ztop=lambda x, y: zu(x) - 0.006, bevel=0.0, long_axis=1)
    p.build(S)
    p = mb("Floor_Planks", "wood", 4.0)
    y = -3.05
    while y < 3.53:
        y1 = min(y + rng.uniform(0.46, 0.56), 3.54)
        cut = rng.uniform(-4.0, 4.0)
        for xa, xb in ((-9.13, cut - 0.01), (cut + 0.01, 9.13)):
            p.box(xa, xb, y + 0.008, y1 - 0.008, PL, 0.2, bevel=0.012, long_axis=0)
        y = y1
    p.build(S)

    # ================================================================== WALLS
    W = C["PS_Walls"]
    WIN = (-1.0, 1.0, 3.95, 5.85)   # window opening along y, z
    for nm, sx in (("L", -1), ("R", 1)):
        p = mb(f"Wall_Side_{nm}_LowerSage", "sage", 4.0)
        wall_boards(p, "y", sx * PX, 0.18, FY + PH, RY - PH, 0.5, 3.15, rng, breaks=(WIN[0], WIN[1]))
        p.build(W)
        p = mb(f"Wall_Side_{nm}_UpperCream", "cream", 4.0)
        wall_boards(p, "y", sx * PX, 0.18, FY + PH, RY - PH, 3.38, 6.3, rng, breaks=(WIN[0], WIN[1]),
                    holes=[(WIN[0], WIN[1], WIN[2], WIN[3])])
        p.build(W)
    p = mb("Wall_Rear_LowerSage", "sage", 4.0)
    wall_boards(p, "x", 3.71, 0.18, -PX + PH, PX - PH, 0.5, 3.15, rng)
    p.build(W)
    p = mb("Wall_Rear_UpperCream", "cream", 4.0)
    wall_boards(p, "x", 3.71, 0.18, -PX + PH, PX - PH, 3.38, lambda x: zu(x) - 0.006, rng)
    p.build(W)
    p = mb("Gable_Front_Cream", "cream", 4.0)
    wall_boards(p, "x", FY, 0.16, -9.6, 9.6, 6.95, lambda x: zu(x) - 0.006, rng, breaks=(-0.3, 0.3))
    p.build(W)

    # ================================================================== WINDOWS (both side walls)
    WN = C["PS_Windows"]
    for nm, sx in (("L", -1), ("R", 1)):
        P0 = sx * PX
        ox = lambda a, b: tuple(sorted((P0 + sx * a, P0 + sx * b)))  # offsets outward (+) / inward (-)
        p = mb(f"Window_{nm}_Frame", "wood_dark", 2.0)
        xa, xb = ox(-0.22, 0.22)
        p.box(xa, xb, -1.0, -0.82, 3.95, 5.85, bevel=0.02, long_axis=2)
        p.box(xa, xb, 0.82, 1.0, 3.95, 5.85, bevel=0.02, long_axis=2)
        p.box(xa, xb, -0.82, 0.82, 5.67, 5.85, bevel=0.02, long_axis=1)
        p.box(xa, xb, -0.82, 0.82, 3.95, 4.13, bevel=0.02, long_axis=1)
        xa, xb = ox(-0.05, 0.05)
        p.box(xa, xb, -0.035, 0.035, 4.13, 5.67, bevel=0.01, long_axis=2)
        p.box(xa, xb, -0.82, 0.82, 4.865, 4.935, bevel=0.01, long_axis=1)
        p.build(WN)
        p = mb(f"Window_{nm}_Casing", "wood", 3.0)
        for a0, a1 in ((0.09, 0.17), (-0.17, -0.09)):
            xa, xb = ox(a0, a1)
            p.box(xa, xb, -1.2, -1.0, 3.95, 5.85, bevel=0.015, long_axis=2)
            p.box(xa, xb, 1.0, 1.2, 3.95, 5.85, bevel=0.015, long_axis=2)
        for a0, a1 in ((0.09, 0.2), (-0.2, -0.09)):
            xa, xb = ox(a0, a1)
            p.box(xa, xb, -1.28, 1.28, 5.85, 6.08, bevel=0.02, long_axis=1)
        p.build(WN)
        p = mb(f"Window_{nm}_Sill", "wood", 3.0)
        xa, xb = ox(-0.3, 0.38)
        p.box(xa, xb, -1.3, 1.3, 3.78, 3.95, bevel=0.03, long_axis=1)
        p.build(WN)
        p = mb(f"Window_{nm}_Glass", "pal")
        xa, xb = ox(-0.012, 0.012)
        p.box(xa, xb, -0.82, 0.82, 4.13, 5.67, cell=L.pal_cell("glass"))
        p.build(WN)
    # flower box under the left (front-three-quarter facing) window, on brackets
    p = mb("WindowBox_L", "wood", 2.0)
    p.box(-9.95, -9.39, -1.1, 1.1, 3.40, 3.75, bevel=0.025, long_axis=1)
    for by in (-0.8, 0.8):
        p.prism([(-9.39, 3.40), (-9.39, 2.98), (-9.88, 3.40)], by - 0.05, by + 0.05, axis="y", bevel=0.01)
    p.build(WN)
    p = mb("WindowBox_L_Plants", "pal")
    p.box(-9.9, -9.44, -1.05, 1.05, 3.6, 3.71, cell=L.pal_cell("soil"))
    for i in range(14):
        by = -0.95 + 1.9 * i / 13
        leaf(p, (-9.67 + rng.uniform(-0.1, 0.1), by, 3.70), rng.uniform(0, 2 * math.pi),
             math.radians(rng.uniform(35, 65)), rng.uniform(0.26, 0.36), 0.13,
             L.pal_cell("leaf_a" if i % 2 else "leaf_b"), droop=0.06)
    for i in range(6):
        cx, cy, cz = -9.67 + rng.uniform(-0.12, 0.12), -0.85 + 1.7 * i / 5, 3.86 + rng.uniform(0, 0.08)
        r = 0.06
        pts = [(cx, cy, cz + r), (cx, cy, cz - r), (cx + r, cy, cz), (cx - r, cy, cz), (cx, cy + r, cz),
               (cx, cy - r, cz)]
        fl = [(0, 2, 4), (0, 4, 3), (0, 3, 5), (0, 5, 2), (1, 4, 2), (1, 3, 4), (1, 5, 3), (1, 2, 5)]
        p.faces(pts, fl, cell=L.pal_cell("flower_yellow" if i % 2 else "flower_white"), long_axis=None)
        p.cyl(0.012, cz - 0.17, cz - r + 0.01, 4, Matrix.Translation((cx, cy, 0)), cell=L.pal_cell("leaf_a"))
    p.build(WN)

    # ================================================================== ROOF
    R = C["PS_Roof"]
    dsS = S_EAVE / 20
    for nm, sx in (("L", -1), ("R", 1)):
        p = mb(f"Roof_Deck_Soffit_{nm}", "wood", 4.0)
        for i in range(20):
            s0, s1 = i * dsS + 0.012, (i + 1) * dsS - 0.012
            if i == 0:
                s0 = 0.0
            pts = [slope_pt(sx, s0, 0, ROOF_Y0), slope_pt(sx, s1, 0, ROOF_Y0), slope_pt(sx, s1, 0, ROOF_Y1),
                   slope_pt(sx, s0, 0, ROOF_Y1)]
            pts += [slope_pt(sx, s0, DECK_T, ROOF_Y0), slope_pt(sx, s1, DECK_T, ROOF_Y0),
                    slope_pt(sx, s1, DECK_T, ROOF_Y1), slope_pt(sx, s0, DECK_T, ROOF_Y1)]
            p.hexa(pts, long_axis=1)
        p.build(R)
        p = mb(f"Roof_Underlay_{nm}", "pal")
        pts = [slope_pt(sx, 0, DECK_T, ROOF_Y0), slope_pt(sx, S_EAVE, DECK_T, ROOF_Y0),
               slope_pt(sx, S_EAVE, DECK_T, ROOF_Y1), slope_pt(sx, 0, DECK_T, ROOF_Y1)]
        pts += [slope_pt(sx, 0, T0, ROOF_Y0), slope_pt(sx, S_EAVE, T0, ROOF_Y0),
                slope_pt(sx, S_EAVE, T0, ROOF_Y1), slope_pt(sx, 0, T0, ROOF_Y1)]
        p.hexa(pts, cell=L.pal_cell("underlay"), long_axis=1)
        p.build(R)
        # tiles: 12 overlapping courses, staggered half-tile, each tile tilted onto the course below
        p = mb(f"Roof_Tiles_{nm}", "tile", 3.0)
        n_c = 12
        s_bot0 = S_EAVE + 0.25
        e = (s_bot0 - 0.6) / (n_c - 1)
        Lt = 1.6 * e
        lift = TILE_T * (1 + (Lt - e) / Lt)
        # starter strip under the first course (gives the eave its convincing thickness)
        pts = [slope_pt(sx, s_bot0 - 0.55, T0, ROOF_Y0), slope_pt(sx, s_bot0, T0, ROOF_Y0),
               slope_pt(sx, s_bot0, T0, ROOF_Y1), slope_pt(sx, s_bot0 - 0.55, T0, ROOF_Y1)]
        pts += [slope_pt(sx, s_bot0 - 0.55, T0 + lift, ROOF_Y0), slope_pt(sx, s_bot0, T0 + lift, ROOF_Y0),
                slope_pt(sx, s_bot0, T0 + lift, ROOF_Y1), slope_pt(sx, s_bot0 - 0.55, T0 + lift, ROOF_Y1)]
        p.hexa(pts, long_axis=1, bevel=0.015)
        w = (ROOF_Y1 - ROOF_Y0) / 8
        for k in range(n_c):
            sb = s_bot0 - k * e
            st = max(sb - Lt, 0.03)
            edges = [ROOF_Y0 + j * w for j in range(9)]
            if k % 2:
                edges = [ROOF_Y0] + [ROOF_Y0 + w / 2 + j * w for j in range(8)] + [ROOF_Y1]
            for j in range(len(edges) - 1):
                y0, y1 = edges[j], edges[j + 1]
                y0 = y0 + (0.025 if j > 0 else 0.0)
                y1 = y1 - (0.025 if j < len(edges) - 2 else 0.0)
                sbj = sb + rng.uniform(-0.03, 0.03)
                lb = T0 + lift + rng.uniform(-0.01, 0.012)
                tt = TILE_T + rng.uniform(-0.01, 0.01)
                pts = [slope_pt(sx, st, T0, y0), slope_pt(sx, sbj, lb, y0), slope_pt(sx, sbj, lb, y1),
                       slope_pt(sx, st, T0, y1)]
                pts += [slope_pt(sx, st, T0 + tt, y0), slope_pt(sx, sbj, lb + tt, y0),
                        slope_pt(sx, sbj, lb + tt, y1), slope_pt(sx, st, T0 + tt, y1)]
                p.hexa(pts, long_axis=None, bevel=0.022)
        p.build(R)
        # layered side eave: fascia board + lower trim board
        p = mb(f"Roof_Fascia_{nm}", "wood", 4.0)
        xa, xb = sorted((sx * 10.9, sx * 11.04))
        p.box(xa, xb, ROOF_Y0, ROOF_Y1, 5.95, 6.42, bevel=0.025, long_axis=1)
        xa, xb = sorted((sx * 10.84, sx * 10.98))
        p.box(xa, xb, ROOF_Y0, ROOF_Y1, 5.82, 6.0, bevel=0.02, long_axis=1)
        p.build(R)

    # ridge cap: overlapping inverted-V pieces, each tilted so ends step over the next
    p = mb("Roof_RidgeCap", "tile", 3.0)
    wcap = 0.75 * CO
    tb, tt = 0.40, 0.51
    yk = ROOF_Y0
    while yk < ROOF_Y1 - 0.05:
        y0, y1 = yk, min(yk + 1.12, ROOF_Y1)
        for sx in (-1, 1):
            def P(x, t, y, rise):
                return (sx * x, y, zu(x) + t / CO + rise)
            r0, r1 = 0.0, 0.045
            pts = [P(0, tb, y0, r0), P(wcap, tb, y0, r0), P(wcap, tb, y1, r1), P(0, tb, y1, r1),
                   P(0, tt, y0, r0), P(wcap, tt, y0, r0), P(wcap, tt, y1, r1), P(0, tt, y1, r1)]
            p.hexa(pts, long_axis=1, bevel=0.02)
        yk += 1.05
    p.build(R)

    # gable barge boards: outer thick barge + stepped inner barge, front and rear
    XE = 11.25
    for nm, (yo0, yo1, yi0, yi1, fy0, fy1) in (("Front", (-5.65, ROOF_Y0, ROOF_Y0, -5.22, -5.72, -5.33)),
                                                 ("Rear", (ROOF_Y1, 5.35, 4.92, ROOF_Y1, 5.03, 5.42))):
        p = mb(f"Roof_Barge_{nm}", "wood", 4.0)
        for sx in (-1, 1):
            poly = [(0, zu(0) - 0.2), (sx * XE, zu(XE) - 0.2), (sx * XE, zu(XE) + 0.566), (0, zu(0) + 0.566)]
            p.prism(poly, yo0, yo1, axis="y", bevel=0.03, long_axis=0)
        p.build(R)
        p = mb(f"Roof_BargeInner_{nm}", "wood_dark", 4.0)
        for sx in (-1, 1):
            poly = [(0, zu(0) - 0.45), (sx * 10.84, zu(10.84) - 0.45), (sx * 10.84, zu(10.84) - 0.004),
                    (0, zu(0) - 0.004)]
            p.prism(poly, yi0, yi1, axis="y", bevel=0.02, long_axis=0)
        p.build(R)
        p = mb(f"Roof_Finial_{nm}", "wood_dark", 2.0)
        p.box(-0.22, 0.22, fy0, fy1, 12.55, 13.05, bevel=0.04, long_axis=2)
        p.build(R)

    # ================================================================== COUNTER (open walk-up front)
    CN = C["PS_Counter"]
    CX0, CX1 = -PX + PH, 4.55
    p = mb("Counter_Front_SageBoards", "sage", 4.0)
    wall_boards(p, "x", -4.48, 0.14, CX0, CX1, 0.42, 2.62, rng, target=0.5)
    p.build(CN)
    p = mb("Counter_Trim_Kick", "wood_dark", 4.0)
    p.box(CX0, CX1, -4.6, -4.38, PL, 0.42, bevel=0.03, long_axis=0)
    p.build(CN)
    p = mb("Counter_Trim_Apron", "wood", 4.0)
    p.box(CX0, CX1, -4.6, -4.38, 2.62, 2.9, bevel=0.025, long_axis=0)
    p.build(CN)
    p = mb("Counter_Lip", "wood", 4.0)
    p.box(CX0, CX1, -4.75, -4.38, 2.78, CT + 0.02, bevel=0.07, long_axis=0)
    p.build(CN)
    p = mb("Counter_Back", "wood_dark", 4.0)
    p.box(CX0, CX1, -2.75, -2.62, 0.2, 2.9, bevel=0.02, long_axis=0)
    p.build(CN)
    TRX = (-8.45, -3.65)
    DSX = (-0.75, 1.35)
    p = mb("Counter_Top_Planks", "wood", 4.0)
    p.box(CX0, TRX[0], -4.4, -2.75, 2.9, CT, bevel=0.02, long_axis=1)
    for xa, xb in ((TRX[1], DSX[0]), (DSX[1], CX1)):
        for ya, yb in ((-4.4, -3.85), (-3.85, -3.3), (-3.3, -2.75)):
            p.box(xa, xb, ya, yb, 2.9, CT, bevel=0.02, long_axis=0)
    p.build(CN)

    # ---- LEFT ball tray: rim, felt, shallow dividers, 8 ball skins
    BT = C["PS_BallTray"]
    p = mb("BallTray_Rim", "wood_dark", 2.0)
    p.box(TRX[0], TRX[1], -4.4, -4.28, 2.7, CT + 0.01, bevel=0.02, long_axis=0)
    p.box(TRX[0], TRX[1], -2.87, -2.75, 2.7, CT + 0.01, bevel=0.02, long_axis=0)
    p.box(TRX[0], TRX[0] + 0.12, -4.28, -2.87, 2.7, CT + 0.01, bevel=0.02, long_axis=1)
    p.box(TRX[1] - 0.12, TRX[1], -4.28, -2.87, 2.7, CT + 0.01, bevel=0.02, long_axis=1)
    p.build(BT)
    fx0, fx1, fy0, fy1, fz = TRX[0] + 0.12, TRX[1] - 0.12, -4.28, -2.87, 2.97
    p = mb("BallTray_Felt", "pal")
    p.box(fx0, fx1, fy0, fy1, 2.7, fz, cell=L.pal_cell("felt_sage"))
    p.build(BT)
    p = mb("BallTray_Dividers", "wood", 2.0)
    cw = (fx1 - fx0) / 4
    for k in (1, 2, 3):
        p.box(fx0 + k * cw - 0.025, fx0 + k * cw + 0.025, fy0, fy1, fz, fz + 0.09, bevel=0.012, long_axis=1)
    ym = (fy0 + fy1) / 2
    p.box(fx0, fx1, ym - 0.025, ym + 0.025, fz, fz + 0.085, bevel=0.012, long_axis=0)
    p.build(BT)
    BALL_R = 0.27
    tray_slots = []
    order = [1, 0, 2, 3, 4, 5, 6, 7]
    for idx in range(8):
        col_, row = idx % 4, idx // 4
        cx = fx0 + cw * (col_ + 0.5)
        cy = (fy0 + ym) / 2 if row == 0 else (ym + fy1) / 2
        skin = order[idx]
        p = L.MB(f"Ball_Tray_{idx + 1:02d}_{L.BALL_SKINS[skin][0]}", M["balls"])
        p.sphere((cx, cy, fz + BALL_R), BALL_R, 16, 10, L.ball_cell_uv(skin))
        ob = p.build(C["PS_Items_Balls"], props={"ps_skin": L.BALL_SKINS[skin][0]})
        tray_slots.append((cx, cy, fz))

    # ---- CENTRE inspection dish: square inset -> rounded rim -> shallow bowl
    DS = C["PS_Dish"]
    dcx, dcy = (DSX[0] + DSX[1]) / 2, (-4.4 - 2.75) / 2
    hw, hd = (DSX[1] - DSX[0]) / 2, (4.4 - 2.75) / 2
    corner = [math.atan2(hd, hw), math.pi - math.atan2(hd, hw), math.pi + math.atan2(hd, hw),
              2 * math.pi - math.atan2(hd, hw)]
    angs = sorted(set([2 * math.pi * i / 40 for i in range(40)] + corner))
    n = len(angs)

    def sq(a):
        c, s = math.cos(a), math.sin(a)
        k = min(hw / abs(c) if abs(c) > 1e-9 else 1e9, hd / abs(s) if abs(s) > 1e-9 else 1e9)
        return (dcx + k * c, dcy + k * s)

    def ring(r, z):
        return [(dcx + r * math.cos(a), dcy + r * math.sin(a), z) for a in angs]
    p = mb("Dish_Surround", "wood", 2.0)
    pts, faces, sm = [], [], []
    top = [(x, y, CT) for x, y in (sq(a) for a in angs)]
    bot = [(x, y, 2.9) for x, y in (sq(a) for a in angs)]
    prof = [(0.80, CT), (0.785, CT + 0.035), (0.74, CT + 0.05), (0.69, CT + 0.035), (0.665, CT),
            (0.64, CT - 0.07)]
    rings = [bot, top] + [ring(r, z) for r, z in prof]
    for rg in rings:
        pts += rg
    for k in range(len(rings) - 1):
        for i in range(n):
            j = (i + 1) % n
            faces.append((k * n + i, k * n + j, (k + 1) * n + j, (k + 1) * n + i))
            sm.append(k >= 2)
    p.faces(pts, faces, long_axis=0, smooth=sm)
    p.build(DS)
    p = mb("Dish_Bowl", "pal")
    bprof = [(0.64, CT - 0.07), (0.61, CT - 0.15), (0.52, CT - 0.22), (0.38, CT - 0.27), (0.21, CT - 0.295),
             (0.0, CT - 0.30)]
    pts, faces = [], []
    for r, z in bprof:
        pts += ring(max(r, 0.0), z) if r > 0 else [(dcx, dcy, z)]
    for k in range(len(bprof) - 1):
        for i in range(n):
            j = (i + 1) % n
            if k == len(bprof) - 2:
                faces.append((k * n + i, k * n + j, (k + 1) * n))
            else:
                faces.append((k * n + i, k * n + j, (k + 1) * n + j, (k + 1) * n + i))
    p.faces(pts, faces, cell=L.pal_cell("felt_charcoal"), smooth=True, long_axis=None)
    p.build(DS)
    p = L.MB("Ball_Display_ActivePreview_classic_white", M["balls"])
    p.sphere((dcx, dcy, CT - 0.30 + 0.30), 0.30, 18, 12, L.ball_cell_uv(0))
    p.build(C["PS_Items_Balls"], props={"ps_skin": "classic_white", "ps_role": "active_preview"})

    # ---- RIGHT club rack: cheek, base, back panel, slotted comb rail, 6 putters
    RK = C["PS_ClubRack"]
    RX0, RX1 = 4.75, PX - PH
    club_x = [5.3 + 0.6 * i for i in range(6)]
    club_y = -4.0
    p = mb("ClubRack_Cheek", "wood", 3.0)
    p.box(CX1, RX0, -4.6, -2.75, PL, CT, bevel=0.03, long_axis=2)
    p.build(RK)
    p = mb("ClubRack_Base", "wood_dark", 3.0)
    p.box(RX0, RX1, -4.6, -3.05, PL, 0.5, bevel=0.03, long_axis=0)
    p.build(RK)
    p = mb("ClubRack_BaseLip", "wood", 3.0)
    p.box(RX0, RX1, -4.6, -4.5, 0.5, 0.6, bevel=0.015, long_axis=0)
    p.build(RK)
    p = mb("ClubRack_BackPanel", "sage", 3.0)
    wall_boards(p, "x", -3.125, 0.15, RX0, RX1, 0.5, 2.95, rng, target=0.5)
    p.build(RK)
    p = mb("ClubRack_SlottedRail", "wood", 3.0)
    p.box(RX0, RX1, -3.92, -3.05, 2.95, CT, bevel=0.02, long_axis=0)
    edges = [RX0] + [v for x in club_x for v in (x - 0.07, x + 0.07)] + [RX1]
    for i in range(0, len(edges), 2):
        p.box(edges[i], edges[i + 1], -4.35, -3.92, 2.95, CT, bevel=0.015, long_axis=1)
    p.build(RK)
    heads = [("blade", "metal_silver", "grip_purple"), ("mallet", "metal_gun", "grip_blue"),
             ("blade", "head_white", "grip_yellow"), ("fang", "metal_silver", "grip_black"),
             ("blade", "metal_gun", "grip_pink"), ("mallet", "head_violet", "grip_teal")]
    for i, (kind, hc, gc) in enumerate(heads):
        cx = club_x[i]
        p = mb(f"Club_{i + 1:02d}_{kind}_{gc.split('_')[1]}", "pal")
        xf = Matrix.Translation((cx, club_y, 0.5)) @ Matrix.Rotation(math.radians(-105), 4, "Z")
        hcell = L.pal_cell(hc)

        def hb(x0, x1, y0, y1, z0, z1, cell=hcell, bev=0.025):
            p.box(x0, x1, y0, y1, z0, z1, xf=xf, cell=cell, bevel=bev, long_axis=None)
        if kind == "blade":
            hb(-0.12, 0.5, -0.09, 0.09, 0.0, 0.2)
            hb(-0.08, 0.46, 0.09, 0.17, 0.0, 0.09, bev=0.015)
            hb(0.17, 0.21, -0.02, 0.02, 0.2, 0.208, cell=L.pal_cell("head_white"), bev=0.0)
            hosel = 0.42
        elif kind == "mallet":
            poly = [(-0.3, -0.12), (0.3, -0.12)] + [(0.3 * math.cos(t), -0.12 + 0.3 * math.sin(t))
                                                   for t in [math.pi * k / 8 for k in range(1, 8)]]
            poly2 = [tuple(xf @ Vector((x, y, 0))) for x, y in poly]
            # extrude mallet in local z (transform afterwards)
            pts = [tuple(xf @ Vector((x, y, 0.0))) for x, y in poly] + \
                  [tuple(xf @ Vector((x, y, 0.2))) for x, y in poly]
            m_ = len(poly)
            fcs = [tuple(range(m_ - 1, -1, -1)), tuple(range(m_, 2 * m_))]
            fcs += [(k, (k + 1) % m_, m_ + (k + 1) % m_, m_ + k) for k in range(m_)]
            p.faces(pts, fcs, cell=hcell, bevel=0.025, long_axis=None)
            del poly2
            hb(-0.015, 0.015, -0.1, 0.16, 0.2, 0.212, cell=L.pal_cell("head_white"), bev=0.0)
            hosel = 0.34
        else:  # fang / heel-toe weighted
            hb(-0.3, 0.3, -0.07, 0.06, 0.0, 0.2)
            hb(-0.3, -0.13, 0.06, 0.33, 0.0, 0.17)
            hb(0.13, 0.3, 0.06, 0.33, 0.0, 0.17)
            hb(-0.012, 0.012, 0.06, 0.3, 0.17, 0.18, cell=L.pal_cell("head_white"), bev=0.0)
            hosel = 0.36
        T = Matrix.Translation((cx, club_y, 0.5))
        p.cyl(0.032, 0.18, hosel, 8, T, cell=hcell)
        p.cyl(0.045, hosel - 0.02, hosel + 0.07, 8, T, cell=L.pal_cell("black"))
        p.cyl(0.033, hosel + 0.07, CT - 0.5, 8, T, cell=L.pal_cell("metal_silver"))
        gprof = [(0.085, CT - 0.5), (0.089, CT - 0.5 + 0.15), (0.098, CT - 0.5 + 0.9), (0.1, CT - 0.5 + 1.03),
                 (0.088, CT - 0.5 + 1.09), (0.0, CT - 0.5 + 1.1)]
        p.lathe(gprof, 10, T, cap_bottom=True, cell=L.pal_cell(gc))
        p.build(C["PS_Items_Clubs"], props={"ps_head": kind, "ps_grip": gc})

    # ================================================================== REAR WALL DECOR
    D = C["PS_Decor"]
    p = mb("Shelf_Rear", "wood", 3.0)
    p.box(-5.6, 5.6, 3.12, RW_IN, 3.48, 3.62, bevel=0.025, long_axis=0)
    p.build(D)
    p = mb("Shelf_Rear_Brackets", "wood_dark", 2.0)
    for bx in (-5.2, -3.2, 3.2, 5.2):
        p.prism([(RW_IN + 0.01, 3.48), (RW_IN + 0.01, 3.0), (3.22, 3.48)], bx - 0.06, bx + 0.06, axis="x",
                bevel=0.01)
    p.build(D)
    # screen: bezel frame + backing (fixed) and replaceable display surface (separate)
    p = mb("Screen_Bezel", "wood_dark", 3.0)
    bx0, bx1, bz0, bz1, bw = -2.75, 2.75, 3.85, 6.65, 0.28
    yb0 = RW_IN - 0.30
    p.box(bx0, bx1, yb0, RW_IN, bz0, bz0 + bw, bevel=0.04, long_axis=0)
    p.box(bx0, bx1, yb0, RW_IN, bz1 - bw, bz1, bevel=0.04, long_axis=0)
    p.box(bx0, bx0 + bw, yb0, RW_IN, bz0 + bw, bz1 - bw, bevel=0.04, long_axis=2)
    p.box(bx1 - bw, bx1, yb0, RW_IN, bz0 + bw, bz1 - bw, bevel=0.04, long_axis=2)
    p.build(D)
    p = mb("Screen_Backing", "pal")
    p.box(bx0 + bw, bx1 - bw, RW_IN - 0.12, RW_IN, bz0 + bw, bz1 - bw, cell=L.pal_cell("screen_back"))
    p.build(D)
    dx0, dx1, dz0, dz1, dy = bx0 + bw, bx1 - bw, bz0 + bw, bz1 - bw, RW_IN - 0.14
    p = L.MB("UI_Display_Surface_REPLACEABLE", M["display"])
    p.faces([(dx0, dy, dz0), (dx1, dy, dz0), (dx1, dy, dz1), (dx0, dy, dz1)], [(0, 1, 2, 3)],
            uvs=[[(0, 0), (1, 0), (1, 1), (0, 1)]], long_axis=None)
    disp = p.build(C["PS_UI_Display"], props={"ps_note": "Replaceable world-UI surface. Front face = -Y. "
                                                         "UV 0..1 across the display; attach SurfaceGui here."})
    # sign: framed PRO SHOP plaque above the screen
    p = mb("Sign_Board", "wood", 3.0)
    p.box(-2.1, 2.1, RW_IN - 0.12, RW_IN, 6.93, 7.83, bevel=0.03, long_axis=0)
    p.build(D)
    p = mb("Sign_Frame", "wood_dark", 2.0)
    fy = RW_IN - 0.18
    p.box(-2.24, 2.24, fy, RW_IN, 6.79, 6.93, bevel=0.03, long_axis=0)
    p.box(-2.24, 2.24, fy, RW_IN, 7.83, 7.97, bevel=0.03, long_axis=0)
    p.box(-2.24, -2.1, fy, RW_IN, 6.93, 7.83, bevel=0.03, long_axis=2)
    p.box(2.1, 2.24, fy, RW_IN, 6.93, 7.83, bevel=0.03, long_axis=2)
    p.build(D)
    src = text_curve("Sign_Lettering_TEXTSOURCE", "PRO SHOP", 0.62, (0, RW_IN - 0.12 - 0.025, 7.38), C["src"],
                     M["pal"], font, extrude=0.025)
    src.data.space_character = 1.05
    src.data.resolution_u = 5
    lettering = text_to_mesh(src, "Sign_Lettering", D, M["pal"], L.pal_cell("letter_brown"))
    lettering["ps_text"] = "PRO SHOP"
    lettering["ps_source"] = src.name
    # framed golf motifs flanking the screen
    for nm, cx, half in (("L", -4.4, 0), ("R", 4.4, 1)):
        p = mb(f"Art_Frame_{nm}", "wood_dark", 2.0)
        x0, x1, z0, z1, fw, fy0 = cx - 0.625, cx + 0.625, 4.65, 6.15, 0.12, RW_IN - 0.14
        p.box(x0, x1, fy0, RW_IN, z0, z0 + fw, bevel=0.025, long_axis=0)
        p.box(x0, x1, fy0, RW_IN, z1 - fw, z1, bevel=0.025, long_axis=0)
        p.box(x0, x0 + fw, fy0, RW_IN, z0 + fw, z1 - fw, bevel=0.025, long_axis=2)
        p.box(x1 - fw, x1, fy0, RW_IN, z0 + fw, z1 - fw, bevel=0.025, long_axis=2)
        p.build(D)
        p = mb(f"Art_Mat_{nm}", "pal")
        p.box(x0 + fw, x1 - fw, RW_IN - 0.06, RW_IN, z0 + fw, z1 - fw, cell=L.pal_cell("pot_cream"))
        p.build(D)
        p = L.MB(f"Art_Print_{nm}", M["prints"])
        u0 = 0.5 * half
        py = RW_IN - 0.065
        p.faces([(cx - 0.4, py, 5.0), (cx + 0.4, py, 5.0), (cx + 0.4, py, 5.8), (cx - 0.4, py, 5.8)],
                [(0, 1, 2, 3)], uvs=[[(u0, 0), (u0 + 0.5, 0), (u0 + 0.5, 1), (u0, 1)]], long_axis=None)
        p.build(D)
    for nm, cx in (("L", -4.4), ("R", 4.4)):
        p = mb(f"Plant_Shelf_{nm}", "pal")
        plant(p, (cx, 3.37, 3.62), rng, n_leaves=11)
        p.build(D)

    # ================================================================== UI PLACEHOLDER (illustrative only)
    U = C["ui"]
    uy = dy - 0.012
    p = mb("UI_Panels_ILLUSTRATIVE", "ui_pal")

    def quad(x0, x1, z0, z1, cell, yy=uy):
        p.faces([(x0, yy, z0), (x1, yy, z0), (x1, yy, z1), (x0, yy, z1)], [(0, 1, 2, 3)], cell=cell, long_axis=None)
    quad(-2.32, -1.42, 5.98, 6.3, L.pal_cell("ui_tab_on"))
    quad(-1.36, -0.46, 5.98, 6.3, L.pal_cell("ui_tab_off"))
    cards = [(-2.32, -1.22, "ui_card_blue", "Buy"), (-1.12, -0.02, "ui_card_violet", "Owned / Equip"),
             (0.08, 1.18, "ui_card_green", "Equipped")]
    for x0, x1, cc, _ in cards:
        quad(x0, x1, 4.25, 5.86, L.pal_cell(cc))
    quad(1.28, 2.38, 4.25, 5.86, L.pal_cell("ui_strip"))
    # check mark on the Equipped card
    cxk, czk = 0.98, 5.68
    yy = uy - 0.004
    p.faces([(cxk - 0.12, yy, czk), (cxk - 0.08, yy, czk + 0.04), (cxk - 0.02, yy, czk - 0.03),
             (cxk - 0.04, yy, czk - 0.08)], [(0, 3, 2, 1)], cell=L.pal_cell("ui_text"), long_axis=None)
    p.faces([(cxk - 0.04, yy, czk - 0.08), (cxk - 0.02, yy, czk - 0.03), (cxk + 0.12, yy, czk + 0.12),
             (cxk + 0.12, yy, czk + 0.06)], [(0, 3, 2, 1)], cell=L.pal_cell("ui_text"), long_axis=None)
    # equipped club icon (flat putter silhouette)
    quad(2.06, 2.1, 4.88, 5.36, L.pal_cell("metal_silver"), yy)
    quad(2.045, 2.115, 5.18, 5.4, L.pal_cell("grip_purple"), uy - 0.008)
    quad(1.96, 2.16, 4.84, 4.92, L.pal_cell("metal_silver"), yy)
    p.build(U)
    # ball icons: flat discs showing real skins from the atlas
    p = L.MB("UI_Icons_ILLUSTRATIVE", M["ui_balls"])
    for (cx, cz, r, skin) in ((-1.77, 5.25, 0.3, 1), (-0.57, 5.25, 0.3, 2), (0.63, 5.25, 0.3, 0),
                              (1.6, 5.1, 0.19, 0)):
        u0, v0, du, dv = L.ball_cell_uv(skin)
        seg = 20
        pts = [(cx, uy - 0.004, cz)]
        uv_c = (u0 + du * 0.25, v0 + dv * 0.5)
        uvp = []
        for k in range(seg):
            t = 2 * math.pi * k / seg
            pts.append((cx + r * math.cos(t), uy - 0.004, cz + r * math.sin(t)))
            lat = math.asin(max(-1, min(1, math.sin(t) * 0.98)))
            lon = math.asin(max(-1, min(1, math.cos(t) * 0.98 / max(math.cos(lat), 1e-3))))
            uvp.append((u0 + du * (0.25 + lon / (2 * math.pi)), v0 + dv * (0.5 + lat / math.pi)))
        faces, uvs = [], []
        for k in range(seg):
            j = (k + 1) % seg
            faces.append((0, k + 1, j + 1))
            uvs.append([uv_c, uvp[k], uvp[j]])
        p.faces(pts, faces, uvs=uvs, long_axis=None)
    p.build(U)
    tz = uy - 0.01
    text_curve("UI_Text_Tab_Balls", "Balls", 0.2, (-1.87, tz, 6.14), U, M["ui_text_dark"], font)
    text_curve("UI_Text_Tab_Clubs", "Clubs", 0.2, (-0.91, tz, 6.14), U, M["ui_text"], font)
    text_curve("UI_Text_Note", "UI PLACEHOLDER - illustrative only", 0.11, (0.98, tz, 6.14), U,
               M["ui_note"], font)
    for x0, x1, _, lab in cards:
        text_curve(f"UI_Text_Card_{lab.split()[0]}", lab, 0.15 if len(lab) > 8 else 0.2,
                   ((x0 + x1) / 2, tz, 4.55), U, M["ui_text"], font)
    text_curve("UI_Text_EquippedHeader", "Equipped", 0.15, (1.83, tz, 5.62), U, M["ui_text"], font)
    text_curve("UI_Text_EquippedBall", "Ball", 0.13, (1.6, tz, 4.62), U, M["ui_note"], font)
    text_curve("UI_Text_EquippedClub", "Club", 0.13, (2.08, tz, 4.62), U, M["ui_note"], font)

    # ================================================================== ANCHORS
    A = C["anchors"]

    def anchor(name, loc, rot=(0, 0, 0), size=0.35, kind="ARROWS", **props):
        e = bpy.data.objects.new(name, None)
        e.empty_display_type = kind
        e.empty_display_size = size
        e.location = loc
        e.rotation_euler = rot
        for k, v in props.items():
            e[k] = v
        A.objects.link(e)
        return e
    anchor("ANCHOR_Root_BaseCentre", (0, 0, 0), size=1.0, ps_note="Asset origin, ground centre")
    anchor("ANCHOR_UI_ScreenPanel", (0, dy, (dz0 + dz1) / 2), rot=(math.pi / 2, 0, 0),
           ps_width=dx1 - dx0, ps_height=dz1 - dz0, ps_face="-Y", ps_note="World UI panel centre (placeholder)")
    anchor("ANCHOR_UI_EquippedBall", (1.6, dy, 5.1), size=0.15, ps_note="Equipped ball readout (separate)")
    anchor("ANCHOR_UI_EquippedClub", (2.08, dy, 5.1), size=0.15, ps_note="Equipped club readout (separate)")
    anchor("ANCHOR_Display_ActivePreview", (dcx, dcy, CT - 0.30), size=0.3,
           ps_note="Bottom of inspection dish; preview item rests here")
    for i, (x, y_, z) in enumerate(tray_slots):
        anchor(f"ANCHOR_BallTray_Slot_{i + 1:02d}", (x, y_, z), size=0.15, kind="PLAIN_AXES")
    for i, x in enumerate(club_x):
        anchor(f"ANCHOR_ClubRack_Slot_{i + 1:02d}", (x, club_y, CT), size=0.15, kind="PLAIN_AXES",
               ps_note="Shaft axis at rail top; grip rests here, head on base at z 0.5")
    anchor("ANCHOR_Prompt_Counter", (dcx, -4.75, CT + 0.05), size=0.25, ps_note="Interaction prompt at lip")
    anchor("ANCHOR_Player_StandSpot", (dcx, -6.4, 0.06), size=0.5, kind="CIRCLE", ps_note="Walk-up spot")
    anchor("ANCHOR_Sign", (0, RW_IN - 0.15, 7.38), size=0.3)

    # ================================================================== COLLISION PROXIES (hidden)
    def colbox(name, *b, prism=None, axis="y", rng_=None):
        q = L.MB(name, M["col"])
        if prism:
            q.prism(prism, b[0], b[1], axis=axis)
        else:
            q.box(*b)
        o = q.build(C["col"])
        o.display_type = "WIRE"
        o.hide_render = True
        o["ps_collision"] = True
        return o
    colbox("COL_Plinth", -10.0, 10.0, -4.85, 4.55, 0.0, PL)
    q = L.MB("COL_ApproachRamp", M["col"])
    q.box(-7.0, 7.0, -8.2, -4.85, -0.08, 0, ztop=lambda x, y: ramp(x, y))
    o = q.build(C["col"])
    o.display_type, o.hide_render, o["ps_collision"] = "WIRE", True, True
    colbox("COL_Counter", CX0, CX1, -4.75, -2.62, PL, CT + 0.02)
    colbox("COL_ClubRack", CX1, RX1, -4.6, -3.05, PL, CT + 1.12)
    for nm, sx, py in (("FL", -1, FY), ("FR", 1, FY), ("RL", -1, RY), ("RR", 1, RY)):
        colbox(f"COL_Post_{nm}", sx * PX - PH, sx * PX + PH, py - PH, py + PH, PL, POST_TOP)
    for nm, sx in (("L", -1), ("R", 1)):
        colbox(f"COL_Wall_{nm}", sx * PX - 0.17, sx * PX + 0.17, FY + PH, RY - PH, PL, 6.9)
    colbox("COL_Wall_Rear", -PX + PH, PX - PH, 3.54, RY + PH, PL, 7.4)
    colbox("COL_Gable_Front", FY - PH, FY + PH,
           prism=[(-9.76, 6.25), (9.76, 6.25), (9.76, 6.95), (0, ZU0), (-9.76, 6.95)])
    for nm, sx in (("L", -1), ("R", 1)):
        colbox(f"COL_Roof_{nm}", -5.65, 5.35,
               prism=[(0, ZU0 - 0.2), (sx * 11.25, zu(11.25) - 0.2), (sx * 11.25, zu(11.25) + 0.6),
                      (0, ZU0 + 0.6)])

    # ================================================================== ENV (render only)
    envm_g = L.material("ENV_Grass", color=(0.36, 0.52, 0.25), rough=0.95, export=False)
    nt = envm_g.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.35
    ramp_n = nt.nodes.new("ShaderNodeValToRGB")
    ramp_n.color_ramp.elements[0].color = (0.07, 0.17, 0.035, 1)
    ramp_n.color_ramp.elements[1].color = (0.17, 0.30, 0.06, 1)
    nt.links.new(nz.outputs["Fac"], ramp_n.inputs["Fac"])
    nt.links.new(ramp_n.outputs["Color"], b.inputs["Base Color"])
    g = L.MB("ENV_Ground", envm_g)
    g.box(-70, 70, -70, 70, -0.2, 0.0, long_axis=None)
    g.build(env)
    env_trunk = L.material("ENV_Trunk", color=(0.40, 0.28, 0.18), export=False)
    env_leaf = L.material("ENV_Foliage", color=(0.26, 0.45, 0.20), rough=0.8, export=False)
    for k, (tx, ty, s) in enumerate(((-17, 13, 1.25), (25, 13, 1.1), (-5, 24, 1.4), (27, -6, 1.0), (-24, -2, 0.95),
                                     (8, 26, 1.2))):
        t = L.MB(f"ENV_Tree_{k}_Trunk", env_trunk)
        t.cyl(0.45 * s, 0, 6 * s, 8, Matrix.Translation((tx, ty, 0)))
        t.build(env)
        f = L.MB(f"ENV_Tree_{k}_Foliage", env_leaf)
        for (ox, oy, oz, r) in ((0, 0, 7.5, 3.2), (1.6, 0.6, 6.2, 2.4), (-1.5, -0.4, 6.4, 2.5), (0.2, 1.2, 9.0, 2.2)):
            tb = bmesh.new()
            bmesh.ops.create_icosphere(tb, subdivisions=1, radius=r * s)
            pts = [(v.co.x + tx + ox * s, v.co.y + ty + oy * s, v.co.z + oz * s) for v in tb.verts]
            idx = {v: i for i, v in enumerate(tb.verts)}
            f.faces(pts, [tuple(idx[v] for v in fc.verts) for fc in tb.faces], long_axis=None)
            tb.free()
        f.build(env)
    # light + world
    sun_d = bpy.data.lights.new("ENV_Sun", "SUN")
    sun_d.energy = 4.2
    sun_d.color = (1.0, 0.93, 0.83)
    sun_d.angle = math.radians(3.0)
    sun = bpy.data.objects.new("ENV_Sun", sun_d)
    env.objects.link(sun)
    sun.rotation_euler = L.look_at_quat((0, 0, 0), (0.55, 0.62, -0.75)).to_euler()
    # soft warm bounce under the roof (stands in for sky/ground bounce into the open front)
    fill_d = bpy.data.lights.new("ENV_InteriorFill", "AREA")
    fill_d.energy = 550
    fill_d.color = (1.0, 0.86, 0.68)
    fill_d.shape = "RECTANGLE"
    fill_d.size, fill_d.size_y = 14.0, 5.0
    fill = bpy.data.objects.new("ENV_InteriorFill", fill_d)
    fill.location = (0, -1.5, 8.6)
    fill.rotation_euler = L.look_at_quat((0, -1.5, 8.6), (0, 0.8, 3.5)).to_euler()
    env.objects.link(fill)
    world = bpy.data.worlds.new("ENV_World")
    scene.world = world
    try:
        world.use_nodes = True
    except Exception:
        pass
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.42, 0.58, 0.86, 1.0)
    bg.inputs["Strength"].default_value = 0.85

    # cameras. sun_dir: direction light travels for that shot (render script applies it)
    def cam(name, loc, target, lens, res, sun_dir):
        cd = bpy.data.cameras.new(name)
        cd.lens = lens
        cd.sensor_fit = "HORIZONTAL"
        cd.sensor_width = 36
        cd.clip_start = 0.05
        o = bpy.data.objects.new(name, cd)
        o.location = loc
        o.rotation_euler = L.look_at_quat(loc, target).to_euler()
        o["ps_res"] = list(res)
        o["ps_sun_dir"] = list(sun_dir)
        env.objects.link(o)
        return o
    front_sun = (0.55, 0.62, -0.75)
    cam("CAM_Front34", (-15.5, -24.0, 7.4), (0.4, 0.2, 5.3), 35, (1600, 1000), front_sun)
    eye = PL + 5.0
    cam("CAM_Eye_Counter", (-0.2, -8.4, eye), (0.0, 0.0, eye - 8.4 * math.tan(math.radians(7.5))), 28,
        (1600, 1100), front_sun)
    cam("CAM_Eye_BallTray", (-5.4, -8.6, eye), (-5.9, -2.0, eye - 6.6 * math.tan(math.radians(22))), 32,
        (1600, 1100), front_sun)
    cam("CAM_Eye_ClubRack", (4.4, -8.7, eye), (6.8, -3.8, eye - 5.5 * math.tan(math.radians(31))), 32,
        (1600, 1100), front_sun)
    cam("CAM_Rear34", (18.0, 20.5, 8.0), (0.0, 0.6, 5.4), 35, (1600, 1000), (-0.45, -0.70, -0.58))

    # ---------------- render settings (Cycles, CPU-safe)
    try:
        scene.render.engine = "CYCLES"
    except TypeError:
        pass
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True
    scene.cycles.device = "CPU"
    scene.render.resolution_x, scene.render.resolution_y = 1600, 1000
    scene.render.resolution_percentage = 100
    vt = [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items]
    if "AgX" in vt:
        scene.view_settings.view_transform = "AgX"
        looks = [i.identifier for i in scene.view_settings.bl_rna.properties["look"].enum_items]
        for want in ("AgX - Medium High Contrast", "Medium High Contrast", "AgX - Punchy"):
            if want in looks:
                scene.view_settings.look = want
                break
    scene.view_settings.exposure = 0.15
    scene.camera = bpy.data.objects["CAM_Front34"]

    scene["ps_asset"] = "pro_shop_pavilion_v1"
    scene["ps_status"] = "FIRST DETAILED MODEL - for Art + Chase review, not accepted final"
    scene["ps_units"] = "1 BU = 1 stud, Z up, open front faces -Y, origin ground centre"
    # hide the editable-text source in viewport too (it duplicates the lettering mesh)
    for o in C["src"].objects:
        o.hide_set(True) if bpy.context.view_layer.objects.get(o.name) else None
        o.hide_render = True
    for o in C["col"].objects:
        o.hide_render = True

    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=out, compress=True)
    print("SAVED", out, flush=True)


if __name__ == "__main__":
    main()
