"""Shared helpers for the Pro Shop pavilion v1 generator.

Procedural texture generation (numpy, deterministic seed), material setup,
and a bmesh MeshBuilder that keeps per-piece metadata so every export mesh
gets clean, non-degenerate UVs (box projection along each piece's long axis,
or explicit UVs for spheres / prints / palette cells).

Portable: no absolute paths. Imported by generate_pavilion.py from the same dir.
"""
import math
import os
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

# --------------------------------------------------------------------------- noise


def _value_noise(h, w, cx, cy, rng):
    """Tileable smooth value noise, cx cells across width (u), cy across height (v)."""
    g = rng.random((cy, cx))
    xs = np.arange(w) / w * cx
    ys = np.arange(h) / h * cy
    x0 = np.floor(xs).astype(int)
    y0 = np.floor(ys).astype(int)
    fx = xs - x0
    fy = ys - y0
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    x1 = (x0 + 1) % cx
    y1 = (y0 + 1) % cy
    a = g[np.ix_(y0, x0)]
    b = g[np.ix_(y0, x1)]
    c = g[np.ix_(y1, x0)]
    d = g[np.ix_(y1, x1)]
    top = a + (b - a) * fx[None, :]
    bot = c + (d - c) * fx[None, :]
    return top + (bot - top) * fy[:, None]


def fbm(h, w, cx, cy, rng, octaves=4, gain=0.5):
    out = np.zeros((h, w))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        out += amp * _value_noise(h, w, cx * 2 ** o, cy * 2 ** o, rng)
        tot += amp
        amp *= gain
    return out / tot


def _mix(c0, c1, t):
    c0 = np.array(c0)[None, None, :]
    c1 = np.array(c1)[None, None, :]
    return c0 + (c1 - c0) * t[:, :, None]


# --------------------------------------------------------------------------- textures (sRGB float arrays HxWx3)


def tex_wood(size, light, dark, rng):
    h = w = size
    grain = fbm(h, w, 3, 40, rng, octaves=3)
    fine = fbm(h, w, 6, 160, rng, octaves=2)
    warp = fbm(h, w, 2, 3, rng, octaves=2)
    rings = 0.5 + 0.5 * np.sin((np.arange(h)[:, None] / h * 9.0 + warp * 2.2) * 2 * math.pi)
    t = 0.5 * grain + 0.2 * rings ** 3 + 0.3 * fine
    t = np.clip((t - 0.3) * 1.15, 0, 1) * 0.75
    col = _mix(dark, light, 1.0 - t)
    tone = fbm(h, w, 2, 2, rng, octaves=2)
    col *= (0.92 + 0.16 * tone)[:, :, None]
    return np.clip(col, 0, 1)


def tex_paint(size, base, rng, streak=0.035, mottle=0.035):
    h = w = size
    s = fbm(h, w, 4, 90, rng, octaves=2) - 0.5
    m = fbm(h, w, 3, 3, rng, octaves=3) - 0.5
    col = np.ones((h, w, 3)) * np.array(base)[None, None, :]
    col *= (1.0 + streak * 2 * s + mottle * 2 * m)[:, :, None]
    return np.clip(col, 0, 1)


def tex_tile(size, base, rng):
    h = w = size
    m = fbm(h, w, 6, 6, rng, octaves=4) - 0.5
    lo = fbm(h, w, 2, 2, rng, octaves=2) - 0.5
    speck = (fbm(h, w, 64, 64, rng, octaves=1) > 0.82) * 0.04
    col = np.ones((h, w, 3)) * np.array(base)[None, None, :]
    col *= (1.0 + 0.16 * m + 0.16 * lo - speck)[:, :, None]
    # tiny warm/cool hue drift so courses are not one flat green
    col[:, :, 0] *= 1.0 + 0.05 * lo
    col[:, :, 2] *= 1.0 - 0.05 * lo
    return np.clip(col, 0, 1)


def tex_stone(size, base, rng):
    h = w = size
    m = fbm(h, w, 8, 8, rng, octaves=5) - 0.5
    speck = fbm(h, w, 96, 96, rng, octaves=1) - 0.5
    col = np.ones((h, w, 3)) * np.array(base)[None, None, :]
    col *= (1.0 + 0.22 * m + 0.08 * speck)[:, :, None]
    return np.clip(col, 0, 1)


# palette cells: name -> (srgb, metallic, roughness). 8x8 grid on a 256 px map.
PALETTE = [
    ("metal_silver", (0.80, 0.81, 0.83), 1.0, 0.28),
    ("metal_gun", (0.30, 0.31, 0.34), 1.0, 0.32),
    ("metal_brass", (0.82, 0.64, 0.34), 1.0, 0.35),
    ("head_white", (0.93, 0.93, 0.92), 0.0, 0.35),
    ("head_violet", (0.50, 0.33, 0.74), 0.0, 0.35),
    ("black", (0.09, 0.09, 0.10), 0.0, 0.45),
    ("grip_purple", (0.56, 0.30, 0.82), 0.0, 0.7),
    ("grip_blue", (0.18, 0.40, 0.86), 0.0, 0.7),
    ("grip_yellow", (0.97, 0.82, 0.18), 0.0, 0.7),
    ("grip_black", (0.13, 0.13, 0.14), 0.0, 0.75),
    ("grip_pink", (0.94, 0.38, 0.60), 0.0, 0.7),
    ("grip_teal", (0.16, 0.66, 0.68), 0.0, 0.7),
    ("felt_sage", (0.25, 0.38, 0.26), 0.0, 1.0),
    ("felt_charcoal", (0.14, 0.15, 0.15), 0.0, 1.0),
    ("leaf_a", (0.27, 0.48, 0.22), 0.0, 0.65),
    ("leaf_b", (0.40, 0.60, 0.27), 0.0, 0.65),
    ("pot_cream", (0.86, 0.81, 0.69), 0.0, 0.8),
    ("pot_clay", (0.72, 0.44, 0.30), 0.0, 0.85),
    ("letter_brown", (0.22, 0.13, 0.07), 0.0, 0.55),
    ("glass", (0.48, 0.62, 0.64), 0.0, 0.08),
    ("soil", (0.22, 0.15, 0.10), 0.0, 1.0),
    ("ui_dark", (0.06, 0.09, 0.13), 0.0, 0.3),
    ("ui_tab_on", (0.60, 0.78, 0.58), 0.0, 0.5),
    ("ui_tab_off", (0.22, 0.27, 0.33), 0.0, 0.5),
    ("ui_card_blue", (0.26, 0.38, 0.56), 0.0, 0.5),
    ("ui_card_violet", (0.36, 0.33, 0.52), 0.0, 0.5),
    ("ui_card_green", (0.24, 0.56, 0.34), 0.0, 0.5),
    ("ui_text", (0.96, 0.96, 0.94), 0.0, 0.5),
    ("ui_strip", (0.12, 0.16, 0.21), 0.0, 0.5),
    ("flower_yellow", (0.98, 0.80, 0.28), 0.0, 0.6),
    ("flower_white", (0.97, 0.95, 0.90), 0.0, 0.6),
    ("sage_trim", (0.33, 0.45, 0.33), 0.0, 0.7),
    ("underlay", (0.20, 0.21, 0.18), 0.0, 0.9),
    ("tile_dark", (0.30, 0.42, 0.29), 0.0, 0.7),
    ("sign_board", (0.80, 0.62, 0.40), 0.0, 0.6),
    ("screen_back", (0.10, 0.10, 0.11), 0.0, 0.5),
]
PAL_INDEX = {p[0]: i for i, p in enumerate(PALETTE)}
PAL_GRID = 8


def pal_cell(name):
    i = PAL_INDEX[name]
    c, r = i % PAL_GRID, i // PAL_GRID
    inset = 0.18 / PAL_GRID
    u0 = c / PAL_GRID + inset
    v0 = 1.0 - (r + 1) / PAL_GRID + inset
    return (u0, v0, u0 + 1.0 / PAL_GRID - 2 * inset, v0 + 1.0 / PAL_GRID - 2 * inset)


def tex_palette(size):
    col = np.zeros((size, size, 3))
    met = np.zeros((size, size, 3))
    rou = np.ones((size, size, 3)) * 0.6
    cs = size // PAL_GRID
    for i, (_, c, m, r) in enumerate(PALETTE):
        cx, cy = i % PAL_GRID, i // PAL_GRID
        y0 = cy * cs  # image row 0 = top in our arrays (flipped on upload)
        col[y0:y0 + cs, cx * cs:(cx + 1) * cs] = c
        met[y0:y0 + cs, cx * cs:(cx + 1) * cs] = m
        rou[y0:y0 + cs, cx * cs:(cx + 1) * cs] = r
    return col, met, rou


# ---- ball skins: 4 x 2 atlas, each cell an equirect map of one sphere
BALL_SKINS = [
    ("classic_white", "white"),
    ("royal_blue", "blue"),
    ("violet_swirl", "violet"),
    ("lime_pop", "lime"),
    ("coral_split", "coral"),
    ("sunny_dots", "yellow"),
    ("teal_band", "teal"),
    ("pink_quarters", "pink"),
]


def _ball_cell(n, kind):
    v, u = np.mgrid[0:n, 0:n] / float(n)  # v: 0 top -> 1 bottom (image rows)
    lat = (0.5 - v) * math.pi
    lon = u * 2 * math.pi
    # faint printed dimple dots (texture only, no geometry)
    dots = (np.sin(lon * 18) * np.sin(lat * 18 + 0.5) > 0.86) * 0.05
    white = np.array((0.95, 0.95, 0.93))

    def solid(c):
        return np.ones((n, n, 3)) * np.array(c)[None, None, :]

    if kind == "white":
        col = solid(white)
    elif kind == "blue":
        col = solid((0.16, 0.33, 0.84))
    elif kind == "violet":
        s = np.sin(lon * 3 + lat * 5) > 0.15
        col = _mix((0.48, 0.26, 0.74), (0.72, 0.56, 0.92), s.astype(float))
    elif kind == "lime":
        col = solid((0.56, 0.80, 0.24))
    elif kind == "coral":
        col = _mix((0.96, 0.44, 0.36), white, (lat < 0).astype(float))
        seam = np.abs(lat) < 0.06
        col[seam] = (0.30, 0.18, 0.15)
    elif kind == "yellow":
        dd = (np.sin(lon * 8) * np.sin(lat * 8) > 0.72)
        col = _mix((0.98, 0.78, 0.18), white, dd.astype(float))
    elif kind == "teal":
        band = np.abs(lat) < 0.28
        col = _mix((0.14, 0.60, 0.64), white, band.astype(float))
    else:  # pink quarters
        q = (np.floor(lon / (math.pi / 2)) % 2) == 0
        col = _mix((0.96, 0.52, 0.70), white, q.astype(float))
    col = col * (1.0 - dots)[:, :, None]
    return np.clip(col, 0, 1)


def tex_balls(cell):
    out = np.zeros((cell * 2, cell * 4, 3))
    for i, (_, kind) in enumerate(BALL_SKINS):
        c, r = i % 4, i // 4
        out[r * cell:(r + 1) * cell, c * cell:(c + 1) * cell] = _ball_cell(cell, kind)
    return out


def ball_cell_uv(i):
    c, r = i % 4, i // 4
    # image row r counted from top; blender v from bottom
    return (c / 4.0, 1.0 - (r + 1) / 2.0, 0.25, 0.5)


def tex_prints(h):
    """Two framed golf motifs side by side (each h x h): flag-on-green, ball-on-tee."""
    w = h * 2
    yy, xx = np.mgrid[0:h, 0:h] / float(h)
    out = np.zeros((h, w, 3))
    # --- left: green with hole and flag
    bg = _mix((0.93, 0.89, 0.78), (0.86, 0.90, 0.88), yy)
    green = ((xx - 0.5) / 0.42) ** 2 + ((yy - 0.72) / 0.20) ** 2 < 1
    bg[green] = (0.36, 0.58, 0.32)
    fringe = (((xx - 0.5) / 0.46) ** 2 + ((yy - 0.72) / 0.235) ** 2 < 1) & ~green
    bg[fringe] = (0.28, 0.46, 0.26)
    hole = ((xx - 0.56) / 0.07) ** 2 + ((yy - 0.74) / 0.03) ** 2 < 1
    bg[hole] = (0.10, 0.12, 0.10)
    stick = (np.abs(xx - 0.56) < 0.012) & (yy > 0.22) & (yy < 0.74)
    bg[stick] = (0.97, 0.96, 0.92)
    flag = (xx > 0.568) & (xx < 0.80) & (yy > 0.22) & (yy < 0.36) & ((yy - 0.22) < (0.80 - xx) * 0.62 + 0.0) & \
        ((0.36 - yy) < (0.80 - xx) * 0.62)
    bg[flag] = (0.86, 0.30, 0.24)
    out[:, :h] = bg
    # --- right: ball on tee over a green swoosh
    bg = _mix((0.90, 0.92, 0.86), (0.93, 0.89, 0.78), yy)
    hill = yy > 0.70 + 0.05 * np.sin(xx * 6.0)
    bg[hill] = (0.38, 0.60, 0.33)
    tee = ((np.abs(xx - 0.5) < 0.025) & (yy > 0.52) & (yy < 0.76)) | \
          ((np.abs(xx - 0.5) < 0.07 - (yy - 0.47) * 0.9) & (yy > 0.47) & (yy < 0.53))
    bg[tee] = (0.80, 0.60, 0.34)
    ball = ((xx - 0.5) ** 2 + (yy - 0.36) ** 2) < 0.115 ** 2
    shade = np.clip(1.0 - ((xx - 0.46) ** 2 + (yy - 0.31) ** 2) * 18, 0.72, 1.0)
    for k in range(3):
        bg[:, :, k] = np.where(ball, 0.97 * shade, bg[:, :, k])
    out[:, h:] = bg
    # thin inner keyline so each print reads as a printed card
    for x0 in (0, h):
        out[:4, x0:x0 + h] = out[-4:, x0:x0 + h] = (0.40, 0.32, 0.22)
        out[:, x0:x0 + 4] = out[:, x0 + h - 4:x0 + h] = (0.40, 0.32, 0.22)
    return np.clip(out, 0, 1)


# --------------------------------------------------------------------------- images & materials


def make_image(name, arr, texdir, non_color=False):
    """arr: HxWx3 float sRGB, row 0 = top. Saves PNG to texdir (if given) and packs it."""
    h, w, _ = arr.shape
    img = bpy.data.images.new(name, w, h, alpha=False)
    if non_color:  # must precede pixel upload: changing colorspace regenerates a generated image
        img.colorspace_settings.name = "Non-Color"
    rgba = np.concatenate([arr[::-1], np.ones((h, w, 1))], axis=2).astype(np.float32)
    img.pixels.foreach_set(rgba.ravel())
    path = os.path.join(texdir, name + ".png")
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    img.filepath = path
    img.pack()
    return img


def _bsdf(m):
    return next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def material(name, image=None, color=None, rough=0.7, metal=0.0, metal_img=None, rough_img=None,
             emission=0.0, export=True):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    nt = m.node_tree
    b = _bsdf(m)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if image is not None:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = image
        t.location = (-420, 260)
        nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
        if emission > 0:
            nt.links.new(t.outputs["Color"], b.inputs["Emission Color"])
            b.inputs["Emission Strength"].default_value = emission
    elif color is not None:
        lin = tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in color) + (1.0,)
        b.inputs["Base Color"].default_value = lin
        m.diffuse_color = lin
        if emission > 0:
            b.inputs["Emission Color"].default_value = lin
            b.inputs["Emission Strength"].default_value = emission
    for img, sock, y in ((metal_img, "Metallic", -40), (rough_img, "Roughness", -300)):
        if img is not None:
            t = nt.nodes.new("ShaderNodeTexImage")
            t.image = img
            t.location = (-420, y)
            nt.links.new(t.outputs["Color"], b.inputs[sock])
    m["ps_export"] = export
    return m


# --------------------------------------------------------------------------- mesh builder


def _dominant(n):
    a = [abs(n.x), abs(n.y), abs(n.z)]
    return a.index(max(a))


class MB:
    """Accumulate primitives (world coords) into one bmesh with per-piece UV metadata."""

    def __init__(self, name, mat, uv_scale=4.0, seed=0):
        self.name = name
        self.mat = mat
        self.bm = bmesh.new()
        self.pid = self.bm.faces.layers.int.new("pid")
        self.uvl = self.bm.loops.layers.uv.new("UVMap")
        self.pieces = []
        self.uv_scale = uv_scale
        self.rng = random.Random(hash(name) & 0xFFFF ^ seed)
        self.explicit = {}

    # ---- piece registration
    def _piece(self, long_axis=None, cell=None, scale=None):
        self.pieces.append(dict(long=long_axis, cell=cell, scale=scale or self.uv_scale,
                                off=(self.rng.random(), self.rng.random())))
        return len(self.pieces) - 1

    def faces(self, pts, faces, long_axis=None, cell=None, bevel=0.0, smooth=None, scale=None,
              uvs=None):
        """pts: world points; faces: index tuples. uvs: optional per-face list of uv tuples."""
        pid = self._piece(long_axis, cell, scale)
        vs = [self.bm.verts.new(Vector(p)) for p in pts]
        new_faces = []
        for fi, f in enumerate(faces):
            try:
                face = self.bm.faces.new([vs[j] for j in f])
            except ValueError:
                continue
            face[self.pid] = pid
            if smooth is not None:
                face.smooth = smooth[fi] if isinstance(smooth, (list, tuple)) else bool(smooth)
            if uvs is not None:
                self.explicit[face] = uvs[fi]
            new_faces.append(face)
        if bevel > 0:
            edges = list({e for f in new_faces for e in f.edges})
            res = bmesh.ops.bevel(self.bm, geom=edges, offset=bevel, offset_type="OFFSET", segments=1,
                                  profile=0.5, affect="EDGES", clamp_overlap=True)
            for f in res["faces"]:
                f[self.pid] = pid
        return pid

    def hexa(self, p8, **kw):
        """8 points: bottom ring 0-3 then top ring 4-7 (same winding)."""
        f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        # make outward winding robust: if volume negative, flip
        c = sum((Vector(p) for p in p8), Vector()) / 8
        n = (Vector(p8[1]) - Vector(p8[0])).cross(Vector(p8[3]) - Vector(p8[0]))
        if n.dot(c - Vector(p8[0])) < 0:  # default winding assumes CCW bottom ring; flip for CW
            f = [tuple(reversed(x)) for x in f]
        return self.faces(p8, f, **kw)

    def box(self, x0, x1, y0, y1, z0, z1, ztop=None, zbot=None, xf=None, **kw):
        c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        pts = [(x, y, zbot(x, y) if zbot else z0) for x, y in c]
        pts += [(x, y, ztop(x, y) if ztop else z1) for x, y in c]
        if xf is not None:
            pts = [tuple(xf @ Vector(p)) for p in pts]
        if kw.get("long_axis", "auto") == "auto":
            d = [abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)]
            kw["long_axis"] = d.index(max(d))
        return self.hexa(pts, **kw)

    def prism(self, poly, a0, a1, axis="y", **kw):
        """Extrude a convex 2D polygon. axis='y': poly in (x,z), extrude y a0..a1.
        axis='x': poly in (y,z); axis='z': poly in (x,y)."""
        n = len(poly)

        def P(p, a):
            if axis == "y":
                return (p[0], a, p[1])
            if axis == "x":
                return (a, p[0], p[1])
            return (p[0], p[1], a)
        pts = [P(p, a0) for p in poly] + [P(p, a1) for p in poly]
        faces = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
        for i in range(n):
            j = (i + 1) % n
            faces.append((i, j, n + j, n + i))
        # orientation fix via signed area
        c = sum((Vector(p) for p in pts), Vector()) / len(pts)
        v0, v1, v2 = (Vector(pts[k]) for k in faces[0][:3])
        if (v1 - v0).cross(v2 - v0).dot(c - v0) > 0:
            faces = [tuple(reversed(f)) for f in faces]
        if kw.get("long_axis", "auto") == "auto":
            kw["long_axis"] = {"y": 1, "x": 0, "z": 2}[axis] if abs(a1 - a0) > 1.5 else None
        return self.faces(pts, faces, **kw)

    def lathe(self, prof, seg, xf, cap_bottom=True, cap_top=False, smooth=True, **kw):
        """prof: [(r, z)] bottom->top; revolved around local Z; xf: Matrix to world."""
        pts, faces, sm = [], [], []
        rings = []
        for (r, z) in prof:
            ring = []
            if r < 1e-6:
                ring = [len(pts)] * seg
                pts.append(tuple(xf @ Vector((0, 0, z))))
            else:
                for i in range(seg):
                    a = 2 * math.pi * i / seg
                    ring.append(len(pts))
                    pts.append(tuple(xf @ Vector((r * math.cos(a), r * math.sin(a), z))))
            rings.append(ring)
        for k in range(len(rings) - 1):
            A, B = rings[k], rings[k + 1]
            for i in range(seg):
                j = (i + 1) % seg
                q = [A[i], A[j], B[j], B[i]]
                q2 = []
                for v in q:
                    if v not in q2:
                        q2.append(v)
                if len(q2) >= 3:
                    faces.append(tuple(q2))
                    sm.append(smooth)
        if cap_bottom and prof[0][0] > 1e-6:
            faces.append(tuple(reversed(rings[0])))
            sm.append(False)
        if cap_top and prof[-1][0] > 1e-6:
            faces.append(tuple(rings[-1]))
            sm.append(False)
        return self.faces(pts, faces, smooth=sm, **kw)

    def cyl(self, r, z0, z1, seg, xf, **kw):
        return self.lathe([(r, z0), (r, z1)], seg, xf, cap_bottom=True, cap_top=True, **kw)

    def sphere(self, center, r, useg, vseg, cell):
        """UV sphere with equirect UVs into atlas cell (u0, v0, du, dv)."""
        u0, v0, du, dv = cell
        cx, cy, cz = center
        grid = []
        pts = []
        for k in range(vseg + 1):
            th = math.pi * k / vseg
            row = []
            for i in range(useg + 1):
                ph = 2 * math.pi * i / useg
                row.append(len(pts))
                pts.append((cx + r * math.sin(th) * math.cos(ph), cy + r * math.sin(th) * math.sin(ph),
                            cz + r * math.cos(th)))
            grid.append(row)
        # merge duplicate seam/pole verts geometrically but keep uv per loop
        key = {}
        uniq = []
        remap = []
        for p in pts:
            kk = (round(p[0], 6), round(p[1], 6), round(p[2], 6))
            if kk not in key:
                key[kk] = len(uniq)
                uniq.append(p)
            remap.append(key[kk])
        faces, uvs = [], []
        for k in range(vseg):
            for i in range(useg):
                idx = [grid[k][i], grid[k + 1][i], grid[k + 1][i + 1], grid[k][i + 1]]
                uv = [(u0 + du * (i / useg), v0 + dv * (1 - k / vseg)),
                      (u0 + du * (i / useg), v0 + dv * (1 - (k + 1) / vseg)),
                      (u0 + du * ((i + 1) / useg), v0 + dv * (1 - (k + 1) / vseg)),
                      (u0 + du * ((i + 1) / useg), v0 + dv * (1 - k / vseg))]
                f, fu = [], []
                for v, t in zip(idx, uv):
                    if remap[v] not in f:
                        f.append(remap[v])
                        fu.append(t)
                faces.append(tuple(f))
                uvs.append(fu)
        return self.faces(uniq, faces, smooth=True, uvs=uvs)

    # ---- finalize
    def build(self, collection, pivot="base", props=None):
        bm = self.bm
        bm.normal_update()
        # UVs
        by_pid = {}
        for f in bm.faces:
            by_pid.setdefault(f[self.pid], []).append(f)
        for pid, fs in by_pid.items():
            pc = self.pieces[pid]
            vs = {v for f in fs for v in f.verts}
            mn = Vector((min(v.co.x for v in vs), min(v.co.y for v in vs), min(v.co.z for v in vs)))
            mx = Vector((max(v.co.x for v in vs), max(v.co.y for v in vs), max(v.co.z for v in vs)))
            ext = mx - mn
            for f in fs:
                if f in self.explicit:
                    for l, t in zip(f.loops, self.explicit[f]):
                        l[self.uvl].uv = t
                    continue
                ax = _dominant(f.normal)
                others = [i for i in range(3) if i != ax]
                if pc["long"] in others:
                    ua = pc["long"]
                    va = [i for i in others if i != ua][0]
                else:
                    ua, va = others
                for l in f.loops:
                    co = l.vert.co
                    if pc["cell"] is not None:
                        u0, v0, u1, v1 = pc["cell"]
                        su = (co[ua] - mn[ua]) / ext[ua] if ext[ua] > 1e-6 else 0.5
                        sv = (co[va] - mn[va]) / ext[va] if ext[va] > 1e-6 else 0.5
                        l[self.uvl].uv = (u0 + (u1 - u0) * su, v0 + (v1 - v0) * sv)
                    else:
                        s = pc["scale"]
                        l[self.uvl].uv = ((co[ua] - mn[ua]) / s + pc["off"][0],
                                          (co[va] - mn[va]) / s + pc["off"][1])
        # pivot
        xs = [v.co for v in bm.verts]
        mn = Vector((min(c.x for c in xs), min(c.y for c in xs), min(c.z for c in xs)))
        mx = Vector((max(c.x for c in xs), max(c.y for c in xs), max(c.z for c in xs)))
        if pivot == "base":
            pv = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
        elif pivot == "world":
            pv = Vector((0, 0, 0))
        else:
            pv = Vector(pivot)
        for v in bm.verts:
            v.co -= pv
        me = bpy.data.meshes.new(self.name)
        bm.to_mesh(me)
        bm.free()
        if "pid" in me.attributes:
            me.attributes.remove(me.attributes["pid"])
        me.materials.append(self.mat)
        ob = bpy.data.objects.new(self.name, me)
        ob.location = pv
        collection.objects.link(ob)
        for k, v in (props or {}).items():
            ob[k] = v
        return ob


def look_at_quat(loc, target):
    d = Vector(target) - Vector(loc)
    return d.to_track_quat("-Z", "Y")
