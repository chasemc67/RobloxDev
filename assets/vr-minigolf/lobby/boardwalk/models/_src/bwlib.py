"""Golden Hour Boardwalk prop library (adapted from the Lantern Grove lglib, self-contained).

Conventions
-----------
* 1 Blender unit = 1 stud, scene unit system NONE, Z-up in Blender.
* Roblox (x, y-up, z-south) -> Blender (x, -z, y). Blender +Y = Roblox -Z = north. Blender -Y = Roblox +Z = south.
* FBX export axis_forward='-Z', axis_up='Y' maps Blender (x, y, z) -> Roblox (x, z, -y).
* Each prop = one mesh object per material, all with origin at the prop pivot (identity transform):
  <prop>__BW_Atlas, <prop>__BW_Neon, <prop>__BW_Backdrop, plus explicitly named faces (panel_1, card_face_1 ...).
* UVs: every atlas face is mapped into a region of textures/bw_atlas_1024.png (see atlas_def.py):
  ("flat", swatch) | ("fit", region) | ("trim", region, studs_per_repeat) | ("hband", region, studs) | ("deck", "a"|"b")
"""
import bpy, bmesh, math, os, time, random
from mathutils import Vector, Matrix, Euler, noise
import atlas_def as A

TAU = math.tau
SRC = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(SRC)
ATLAS_PATH = os.path.join(OUT, "textures", "bw_atlas_1024.png")
PROGRESS = os.path.join(SRC, "PROGRESS_pass2.md")
NEON_GOLD = "#FFC867"
NEON_CRYSTAL = "#9FE6F2"


def log(msg):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}"
    print(line)
    with open(PROGRESS, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ----------------------------------------------------------------------------- colour helpers
def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin(h):
    return tuple(srgb_to_lin(c) for c in hex_rgb(h))


# ----------------------------------------------------------------------------- atlas UV regions
def _rect_uv(rect, inset_px=2.0):
    x0, y0, x1, y1 = rect
    s = float(A.SIZE)
    return ((x0 + inset_px) / s, 1 - (y1 - inset_px) / s, (x1 - inset_px) / s, 1 - (y0 + inset_px) / s)


def region(name):
    if name in A.R:
        return _rect_uv(A.R[name])
    if name in A.SW:
        return _rect_uv(A.SW[name], 8)
    raise KeyError(name)


def _face_axes(n):
    """Horizontal tangent h and vertical-ish tangent v for a face normal (Blender space)."""
    up = Vector((0, 0, 1))
    if abs(n.z) > 0.85:          # top / bottom face: plan axes
        return Vector((1, 0, 0)), Vector((0, 1, 0))
    h = up.cross(n)
    h.normalize()
    v = n.cross(h)
    v.normalize()
    return h, v


def map_uvs(tbm, mapping):
    """Assign UVs (in a 'UVMap' loop layer) to every face of tbm, coordinates in prop space."""
    uvl = tbm.loops.layers.uv.get("UVMap") or tbm.loops.layers.uv.new("UVMap")
    kind = mapping[0]
    tbm.normal_update()
    if kind == "flat":
        u0, v0, u1, v1 = region(mapping[1])
        c = ((u0 + u1) / 2, (v0 + v1) / 2)
        for f in tbm.faces:
            for l in f.loops:
                l[uvl].uv = c
        return
    if kind == "stripes":
        # ("stripes", swatch_a, swatch_b, n_sectors[, phase_rad]): alternate flat swatches by face angle about Z
        ra, rb = region(mapping[1]), region(mapping[2])
        n = mapping[3]
        ph = mapping[4] if len(mapping) > 4 else 0.0
        for f in tbm.faces:
            c = f.calc_center_median()
            k = int(((math.atan2(c.y, c.x) - ph) % TAU) / TAU * n) % n
            r = ra if k % 2 == 0 else rb
            for l in f.loops:
                l[uvl].uv = ((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
        return
    if kind == "deck":
        u_start = A.DECK_U0[mapping[1]]
        u0, v0, u1, v1 = region("deck")
        _, v0, _, v1 = _rect_uv(A.R["deck"], 0)
        sw = region("plank_dark")
        for f in tbm.faces:
            if f.normal.z > 0.5:
                for l in f.loops:
                    x, y = l.vert.co.x, l.vert.co.y
                    # planks run along X (U); 8 planks across the 10-stud tile in V
                    l[uvl].uv = (u_start + (x + 5.0) / A.DECK_STRIP_STUDS, v0 + (y + 5.0) / 10.0 * (v1 - v0))
            else:
                c = ((sw[0] + sw[2]) / 2, (sw[1] + sw[3]) / 2)
                for l in f.loops:
                    l[uvl].uv = c
        return
    u0, v0, u1, v1 = region(mapping[1])
    for f in tbm.faces:
        h, v = _face_axes(f.normal)
        hs = [l.vert.co.dot(h) for l in f.loops]
        vs = [l.vert.co.dot(v) for l in f.loops]
        hmin, hmax, vmin, vmax = min(hs), max(hs), min(vs), max(vs)
        hr, vr = max(hmax - hmin, 1e-6), max(vmax - vmin, 1e-6)
        if kind == "fit":
            for l, a, b in zip(f.loops, hs, vs):
                l[uvl].uv = (u0 + (a - hmin) / hr * (u1 - u0), v0 + (b - vmin) / vr * (v1 - v0))
        elif kind == "trim":
            studs = mapping[2]
            off = mapping[3] if len(mapping) > 3 else 0.0
            along_h = hr >= vr
            for l, a, b in zip(f.loops, hs, vs):
                if along_h:
                    l[uvl].uv = (off + a / studs, v0 + (b - vmin) / vr * (v1 - v0))
                else:
                    l[uvl].uv = (off + b / studs, v0 + (a - hmin) / hr * (v1 - v0))
        elif kind == "hband":
            studs = mapping[2]
            off = mapping[3] if len(mapping) > 3 else 0.0
            for l, a, b in zip(f.loops, hs, vs):
                z = l.vert.co.z
                l[uvl].uv = (off + z / studs, v0 + (a - hmin) / hr * (v1 - v0))
        else:
            raise ValueError(kind)


# ----------------------------------------------------------------------------- coords / matrices
def RB(x, y, z):
    """Roblox local (x, y-up, z-south) -> Blender vector."""
    return Vector((x, -z, y))


def M(loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    S = Matrix.Diagonal((*scale, 1))
    Rm = Euler([math.radians(a) for a in rot], "XYZ").to_matrix().to_4x4()
    return Matrix.Translation(Vector(loc)) @ Rm @ S


# ----------------------------------------------------------------------------- materials
def mat_atlas():
    m = bpy.data.materials.get("BW_Atlas")
    if m:
        return m
    m = bpy.data.materials.new("BW_Atlas")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(ATLAS_PATH, check_existing=True)
    tex.interpolation = "Linear"
    tex.location = (-420, 200)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.8
    bsdf.inputs["Specular IOR Level"].default_value = 0.3
    m.diffuse_color = (*lin(A.PAL["plank"]), 1)
    return m


def mat_neon(hexv=NEON_GOLD, strength=4.0):
    m = bpy.data.materials.get("BW_Neon")
    if m:
        return m
    m = bpy.data.materials.new("BW_Neon")
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    rgb = lin(hexv)
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Emission Color"].default_value = (*rgb, 1)
    bsdf.inputs["Emission Strength"].default_value = strength
    bsdf.inputs["Roughness"].default_value = 0.5
    m.diffuse_color = (*rgb, 1)
    m["bw_hex"] = hexv
    return m


def mat_backdrop():
    m = bpy.data.materials.get("BW_Backdrop")
    if m:
        return m
    m = bpy.data.materials.new("BW_Backdrop")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    va = nt.nodes.new("ShaderNodeVertexColor")
    va.layer_name = "Col"
    nt.links.new(va.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.9
    return m


# ----------------------------------------------------------------------------- builder
class Part:
    __slots__ = ("verts", "faces", "uvs", "cols", "smooth", "mat")

    def __init__(self, mat):
        self.verts, self.faces, self.uvs, self.cols, self.smooth = [], [], [], [], []
        self.mat = mat


class PB:
    """Prop builder. Geometry goes into parts keyed by object name; each part = one mesh object.
    part 'atlas' -> <prop>__BW_Atlas, 'neon' -> <prop>__BW_Neon, 'backdrop' -> <prop>__BW_Backdrop,
    any other key -> an object with exactly that name (BW_Atlas material), e.g. 'panel_1'."""

    def __init__(self, name, neon_hex=NEON_GOLD):
        self.name = name
        self.parts = {}
        self.neon_hex = neon_hex
        self.frame = Matrix.Identity(4)
        self.meta = {}

    def _part(self, key):
        if key not in self.parts:
            mat = {"neon": "BW_Neon", "backdrop": "BW_Backdrop"}.get(key, "BW_Atlas")
            self.parts[key] = Part(mat)
        return self.parts[key]

    def add(self, tbm, mapping=("flat", "plank"), matrix=None, part="atlas", smooth=False, color=None):
        mtx = self.frame @ (matrix if matrix is not None else Matrix.Identity(4))
        bmesh.ops.transform(tbm, matrix=mtx, verts=tbm.verts)
        if mtx.determinant() < 0:
            bmesh.ops.reverse_faces(tbm, faces=tbm.faces)
        if part == "neon" or part == "backdrop":
            mapping = ("flat", "glow") if part == "neon" else ("flat", "awn_cream")
        map_uvs(tbm, mapping)
        uvl = tbm.loops.layers.uv["UVMap"]
        P = self._part(part)
        base = len(P.verts)
        tbm.verts.index_update()
        P.verts.extend(v.co.copy() for v in tbm.verts)
        col = (*lin(color), 1.0) if isinstance(color, str) else None
        for f in tbm.faces:
            P.faces.append([base + v.index for v in f.verts])
            P.uvs.append([tuple(l[uvl].uv) for l in f.loops])
            P.smooth.append(smooth)
            if part == "backdrop":
                if callable(color):
                    cs = []
                    for l in f.loops:
                        c = color(l.vert.co.copy())
                        c = lin(c) if isinstance(c, str) else tuple(srgb_to_lin(x) for x in c)
                        cs.append((*c, 1.0))
                    P.cols.append(cs)
                else:
                    P.cols.append([col or (1, 1, 1, 1)] * len(f.loops))
        tbm.free()

    # --- primitives (Blender-space) ---
    def box(self, size, loc=(0, 0, 0), rot=(0, 0, 0), mapping=("flat", "plank"), bevel=0.0, segs=2, part="atlas",
            matrix=None, smooth=False, color=None):
        t = bmesh.new()
        bmesh.ops.create_cube(t, size=1.0)
        bmesh.ops.scale(t, vec=Vector(size), verts=t.verts)
        if bevel > 0:
            bmesh.ops.bevel(t, geom=list(t.edges), offset=min(bevel, min(size) * 0.45), segments=segs,
                            affect="EDGES", profile=0.5, clamp_overlap=True)
        self.add(t, mapping, (matrix if matrix is not None else Matrix.Identity(4)) @ M(loc, rot), part, smooth, color)

    def box_minmax(self, mn, mx, **kw):
        mn, mx = Vector(mn), Vector(mx)
        self.box(tuple(mx - mn), loc=tuple((mn + mx) / 2), **kw)

    def cyl(self, r1, r2, depth, segs=10, loc=(0, 0, 0), rot=(0, 0, 0), mapping=("flat", "post"), part="atlas",
            matrix=None, smooth=True, caps=True, base_at_zero=False, color=None):
        t = bmesh.new()
        bmesh.ops.create_cone(t, cap_ends=caps, cap_tris=False, segments=segs, radius1=r1, radius2=r2, depth=depth)
        if base_at_zero:
            bmesh.ops.translate(t, vec=(0, 0, depth / 2), verts=t.verts)
        self.add(t, mapping, (matrix if matrix is not None else Matrix.Identity(4)) @ M(loc, rot), part, smooth, color)

    def sphere(self, r, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), segs=10, rings=6, ico=0,
               mapping=("flat", "plank"), part="atlas", matrix=None, smooth=True, color=None):
        t = bmesh.new()
        if ico:
            bmesh.ops.create_icosphere(t, subdivisions=ico, radius=r)
        else:
            bmesh.ops.create_uvsphere(t, u_segments=segs, v_segments=rings, radius=r)
        self.add(t, mapping, (matrix if matrix is not None else Matrix.Identity(4)) @ M(loc, rot, scale), part,
                 smooth, color)

    def blob(self, size, loc=(0, 0, 0), rot=(0, 0, 0), seed=0, amp=0.12, ico=2, freq=1.6, flat_bottom=None,
             mapping=("flat", "plank"), part="atlas", matrix=None, smooth=True, color=None):
        """Chunky rounded noise blob (leaf clusters, rocks). size = full extents."""
        t = bmesh.new()
        bmesh.ops.create_icosphere(t, subdivisions=ico, radius=0.5)
        off = Vector((seed * 3.17, seed * 1.71, seed * 2.33))
        for v in t.verts:
            v.co *= 1 + amp * noise.noise(v.co * freq * 2 + off) * 2
        bmesh.ops.scale(t, vec=Vector(size), verts=t.verts)
        if flat_bottom is not None:
            zmin = -size[2] * flat_bottom
            for v in t.verts:
                if v.co.z < zmin:
                    v.co.z = zmin
            bmesh.ops.remove_doubles(t, verts=t.verts, dist=0.01)
        self.add(t, mapping, (matrix if matrix is not None else Matrix.Identity(4)) @ M(loc, rot), part, smooth,
                 color)

    def lathe(self, profile, segs=12, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), mapping=("flat", "plank"),
              part="atlas", matrix=None, smooth=True, color=None, phase=0.0):
        """profile: list of (radius, z) bottom -> top; radius 0 -> pole."""
        t = bmesh.new()
        rings = []
        for (r, z) in profile:
            if r <= 1e-6:
                rings.append([t.verts.new((0, 0, z))])
            else:
                rings.append([t.verts.new((r * math.cos(TAU * i / segs + phase), r * math.sin(TAU * i / segs + phase),
                                           z)) for i in range(segs)])
        for a, b in zip(rings, rings[1:]):
            if len(a) == 1 and len(b) == 1:
                continue
            if len(a) == 1:
                for i in range(segs):
                    t.faces.new((a[0], b[i], b[(i + 1) % segs]))
            elif len(b) == 1:
                for i in range(segs):
                    t.faces.new((a[i], b[0], a[(i + 1) % segs]))
            else:
                for i in range(segs):
                    t.faces.new((a[i], a[(i + 1) % segs], b[(i + 1) % segs], b[i]))
        if len(rings[0]) > 1:
            t.faces.new(list(reversed(rings[0])))
        if len(rings[-1]) > 1:
            t.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(t, faces=t.faces)
        self.add(t, mapping, (matrix if matrix is not None else Matrix.Identity(4)) @ M(loc, rot, scale), part,
                 smooth, color)

    def tube(self, pts, radii, segs=6, mapping=("flat", "rope"), part="atlas", matrix=None, smooth=True, caps=True,
             flatten=1.0, color=None):
        pts = [Vector(p) for p in pts]
        if not isinstance(radii, (list, tuple)):
            radii = [radii] * len(pts)
        t = bmesh.new()
        tangents = []
        for i in range(len(pts)):
            a = pts[max(i - 1, 0)]
            b = pts[min(i + 1, len(pts) - 1)]
            tangents.append((b - a).normalized())
        up = Vector((0, 0, 1)) if abs(tangents[0].z) < 0.9 else Vector((1, 0, 0))
        n = tangents[0].cross(up).normalized()
        rings = []
        for i, (p, tg) in enumerate(zip(pts, tangents)):
            if i > 0:
                n = (n - tg * n.dot(tg)).normalized()
            bn = tg.cross(n).normalized()
            rings.append([t.verts.new(p + (n * math.cos(TAU * k / segs) * flatten + bn * math.sin(TAU * k / segs))
                                      * radii[i]) for k in range(segs)])
        for a, b in zip(rings, rings[1:]):
            for k in range(segs):
                t.faces.new((a[k], a[(k + 1) % segs], b[(k + 1) % segs], b[k]))
        if caps:
            t.faces.new(list(reversed(rings[0])))
            t.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(t, faces=t.faces)
        self.add(t, mapping, matrix, part, smooth, color)

    def torus(self, R_, r, segs=16, rsegs=6, loc=(0, 0, 0), rot=(0, 0, 0), mapping=("flat", "brass"), part="atlas",
              matrix=None, smooth=True, color=None):
        t = bmesh.new()
        rings = []
        for i in range(segs):
            a = TAU * i / segs
            c = Vector((math.cos(a), math.sin(a), 0))
            rings.append([t.verts.new(c * (R_ + r * math.cos(TAU * k / rsegs)) +
                                      Vector((0, 0, r * math.sin(TAU * k / rsegs)))) for k in range(rsegs)])
        for i in range(segs):
            a, b = rings[i], rings[(i + 1) % segs]
            for k in range(rsegs):
                t.faces.new((a[k], b[k], b[(k + 1) % rsegs], a[(k + 1) % rsegs]))
        bmesh.ops.recalc_face_normals(t, faces=t.faces)
        self.add(t, mapping, (matrix if matrix is not None else Matrix.Identity(4)) @ M(loc, rot), part, smooth,
                 color)

    def prism(self, poly, depth, loc=(0, 0, 0), rot=(0, 0, 0), mapping=("flat", "plank"), part="atlas", matrix=None,
              smooth=False, bevel=0.0, segs=2, color=None):
        """Extrude a 2D polygon (x, y) along +Z by depth (centred on z=0)."""
        t = bmesh.new()
        bot = [t.verts.new((x, y, -depth / 2)) for x, y in poly]
        top = [t.verts.new((x, y, depth / 2)) for x, y in poly]
        n = len(poly)
        t.faces.new(list(reversed(bot)))
        t.faces.new(top)
        for i in range(n):
            t.faces.new((bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i]))
        bmesh.ops.recalc_face_normals(t, faces=t.faces)
        if bevel > 0:
            bmesh.ops.bevel(t, geom=list(t.edges), offset=bevel, segments=segs, affect="EDGES", profile=0.5,
                            clamp_overlap=True)
        self.add(t, mapping, (matrix if matrix is not None else Matrix.Identity(4)) @ M(loc, rot), part, smooth,
                 color)

    def loft(self, sections, mapping=("flat", "plank"), part="atlas", matrix=None, smooth=False, caps=True,
             color=None, closed=True):
        """sections: list of equal-length vertex loops (Blender vectors)."""
        t = bmesh.new()
        rings = [[t.verts.new(Vector(p)) for p in sec] for sec in sections]
        n = len(sections[0])
        for a, b in zip(rings, rings[1:]):
            for k in range(n if closed else n - 1):
                t.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
        if caps:
            t.faces.new(list(reversed(rings[0])))
            t.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(t, faces=t.faces)
        self.add(t, mapping, matrix, part, smooth, color)

    def quad(self, pts, mapping=("fit", "parch"), part="atlas", matrix=None, color=None):
        """Single face from explicit points (counter-clockwise seen from the front)."""
        t = bmesh.new()
        vs = [t.verts.new(Vector(p)) for p in pts]
        t.faces.new(vs)
        self.add(t, mapping, matrix, part, False, color)

    def custom(self, verts, faces, mapping=("flat", "plank"), part="atlas", matrix=None, smooth=False, color=None,
               recalc=True):
        t = bmesh.new()
        vs = [t.verts.new(Vector(p)) for p in verts]
        for f in faces:
            try:
                t.faces.new([vs[i] for i in f])
            except ValueError:
                pass
        if recalc:
            bmesh.ops.recalc_face_normals(t, faces=t.faces)
        self.add(t, mapping, matrix, part, smooth, color)

    # --- finalize ---
    def finalize(self, collection, smooth_angle=50.0):
        objs = []
        order = sorted(self.parts.items(), key=lambda kv: (kv[0] not in ("atlas", "neon", "backdrop"), kv[0]))
        for key, P in order:
            if key in ("atlas", "neon", "backdrop"):
                oname = f"{self.name}__{P.mat}"
            else:
                oname = key
            me = bpy.data.meshes.new(oname)
            b = bmesh.new()
            bv = [b.verts.new(v) for v in P.verts]
            uvl = b.loops.layers.uv.new("UVMap")
            cl = b.loops.layers.float_color.new("Col") if key == "backdrop" else None
            for i, f in enumerate(P.faces):
                try:
                    bf = b.faces.new([bv[j] for j in f])
                except ValueError:
                    continue     # duplicate face
                bf.smooth = P.smooth[i]
                for l, uv in zip(bf.loops, P.uvs[i]):
                    l[uvl].uv = uv
                if cl is not None:
                    for l, c in zip(bf.loops, P.cols[i]):
                        l[cl] = c
            bmesh.ops.remove_doubles(b, verts=b.verts, dist=0.0005)
            bmesh.ops.triangulate(b, faces=[f for f in b.faces if len(f.verts) > 3], quad_method="BEAUTY",
                                  ngon_method="BEAUTY")
            # drop degenerate faces
            bad = [f for f in b.faces if f.calc_area() < 1e-9]
            if bad:
                bmesh.ops.delete(b, geom=bad, context="FACES")
            b.to_mesh(me)
            b.free()
            try:
                me.set_sharp_from_angle(angle=math.radians(smooth_angle))
            except Exception:
                pass
            if P.mat == "BW_Neon":
                me.materials.append(mat_neon(self.neon_hex))
            elif P.mat == "BW_Backdrop":
                me.materials.append(mat_backdrop())
            else:
                me.materials.append(mat_atlas())
            ob = bpy.data.objects.new(oname, me)
            collection.objects.link(ob)
            objs.append(ob)
        self.parts = {}
        return objs


# ----------------------------------------------------------------------------- measurement
def tri_count(objs):
    return sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs if o.type == "MESH")


def bbox_blender(objs):
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        if o.type != "MESH":
            continue
        mw = o.matrix_world
        for v in o.data.vertices:
            w = mw @ v.co
            mn = Vector(map(min, mn, w))
            mx = Vector(map(max, mx, w))
    return mn, mx


def to_roblox_bbox(mn, mx):
    size = [mx.x - mn.x, mx.z - mn.z, mx.y - mn.y]
    c = (mn + mx) / 2
    return size, [c.x, c.z, -c.y]


def recenter_base(objs):
    """Move geometry so the pivot is at bbox centre XY (Blender), min Z = 0. Returns the applied offset."""
    mn, mx = bbox_blender(objs)
    off = Vector((-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z))
    if off.length > 1e-6:
        for o in objs:
            o.data.transform(Matrix.Translation(off))
    return off


# ----------------------------------------------------------------------------- export
def export_fbx(objs, path):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.export_scene.fbx(
        filepath=path, use_selection=True, apply_scale_options="FBX_SCALE_UNITS", global_scale=1.0,
        apply_unit_scale=True, bake_space_transform=True,
        axis_forward="-Z", axis_up="Y", path_mode="COPY", embed_textures=True, add_leaf_bones=False,
        bake_anim=False, mesh_smooth_type="FACE", use_mesh_modifiers=True, object_types={"MESH"},
        use_custom_props=False, colors_type="SRGB", use_metadata=False, use_tspace=False)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "NONE"
    sc.unit_settings.scale_length = 1.0
    return sc


# ----------------------------------------------------------------------------- shape helpers
def arch_curve(width, height, n=12, rise=None):
    """Points of a round-topped opening outline (half-ellipse on top of vertical sides), Blender XZ (y=0)."""
    pts = []
    r = width / 2
    rise = r if rise is None else rise
    spring = height - rise
    for i in range(n + 1):
        a = math.pi * i / n
        pts.append((r * math.cos(a), spring + rise * math.sin(a)))
    return pts


def superellipse_ring(rx, ry, n, segs, z=0.0, wob=None):
    pts = []
    for i in range(segs):
        a = TAU * i / segs
        c, s = math.cos(a), math.sin(a)
        x = rx * math.copysign(abs(c) ** (2 / n), c)
        y = ry * math.copysign(abs(s) ** (2 / n), s)
        k = wob(a, z) if wob else 1.0
        pts.append(Vector((x * k, y * k, z)))
    return pts


def rnd(seed):
    return random.Random(seed)
