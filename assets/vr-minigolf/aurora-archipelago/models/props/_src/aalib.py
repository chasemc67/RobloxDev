"""Aurora Archipelago prop library (adapted from lantern-grove/models/_src/lglib.py): shared helpers for all prop generators.

Conventions
-----------
* 1 Blender unit = 1 stud, scene unit system NONE.
* Modelled Z-up in Blender. Roblox/holes.json coords (x, y, z) map to Blender (x, -z, y):
  Roblox +X = Blender +X, Roblox +Y (up) = Blender +Z, Roblox -Z ("north", play direction) = Blender +Y.
* FBX export axis_forward='-Z', axis_up='Y' maps Blender (x, y, z) -> FBX (x, z, -y) = Roblox (x, y, z) exactly.
* Every prop = one root Empty (named <prop>) at the prop origin + one child mesh per material
  (named <prop>__<Material>) whose origin is also the prop origin (identity local transform).
  In Roblox each child becomes a MeshPart; colour/material come from the manifest (and from the FBX material).
"""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, noise

TAU = math.tau

# ----------------------------------------------------------------------------- palette
# name: (hex, roblox_material, emission_strength, transparency, note)
MATS = {
    # course.md palette (Aurora Archipelago); timber/felt follow terrain pass 2b (#8A5A3C) / pass 2g felt (#36997A; 2d #3EA886, 2c #45B892, 2b #4FC29E)
    "Timber":      ("#8A5A3C", "WoodPlanks", 0, 0, "snow-capped timber rails/posts (pass 2b warm timber)"),
    "Snow":        ("#F4F6FF", "Snow", 0, 0, "thick rounded snow caps, drifts"),
    "SnowShadow":  ("#C9C3EC", "Snow", 0, 0, "shaded snow / packed snow walls"),
    "Rock":        ("#5E6177", "Slate", 0, 0, "slate-violet rock"),
    "Basalt":      ("#3A3550", "Basalt", 0, 0, "dark basalt (geyser, cliff, rims)"),
    "Brass":       ("#C9A04A", "Metal", 0, 0, "brass fittings, bolts, lanterns, gauge"),
    "Glow":        ("#FFB861", "Neon", 4.0, 0, "ember lantern core (PointLight #FFB861)"),
    "Ice":         ("#8FE3FF", "Glass", 0.3, 0.3, "glass-look glacier ice (Transparency 0.3, Reflectance 0.1)"),
    "IceCore":     ("#BFF6FF", "Neon", 3.0, 0, "crystal-core neon inside glass ice"),
    "IceSheen":    ("#9FE3F2", "Glass", 0, 0.15, "H4 glassy ice felt (Transparency 0.15, Reflectance 0.15)"),
    "AuroraMint":  ("#5CFFB0", "Neon", 3.0, 0, "aurora mint: decals, cues, ribbons"),
    "AuroraViolet": ("#B07CFF", "Neon", 3.0, 0, "aurora violet: ribbon gradient end"),
    "AuroraTeal":  ("#3DE2C8", "Neon", 2.0, 0, "aurora teal accents"),
    "Lime":        ("#D8FF6A", "Neon", 4.0, 0, "teleport / respawn aurora-lime glow"),
    "Lagoon":      ("#2FD6C8", "Glass", 0.4, 0.3, "lagoon / hot-spring water"),
    "Steam":       ("#E9FBFF", "SmoothPlastic", 0.3, 0.5, "steam puffs (Transparency 0.5; particles in game)"),
    "CoralPink":   ("#FF6FB5", "SmoothPlastic", 0, 0, "bubblegum coral-ice"),
    "CoralOrange": ("#FFA552", "SmoothPlastic", 0, 0, "tangerine coral-ice"),
    "CoralMint":   ("#6FFFD2", "Neon", 2.5, 0, "coral neon core / glowing tips"),
    "Pine":        ("#2F6B4F", "Grass", 0, 0, "frosted pine boughs"),
    "Ink":         ("#222233", "SmoothPlastic", 0, 0, "snowpuff body / sign lettering / gauge face"),
    "Cream":       ("#FFF4E2", "SmoothPlastic", 0, 0, "snowpuff belly, sign boards"),
    "Beak":        ("#FF9A3C", "SmoothPlastic", 0, 0, "snowpuff beak"),
    "FlagRed":     ("#E03C31", "Fabric", 0, 0, "cup-flag banner (holes.json cup.flag.banner_color)"),
    "MoveRed":     ("#D3362A", "SmoothPlastic", 0, 0, "moving-part signal red (bands ONLY on moving parts)"),
    "MoveCream":   ("#FFF2D8", "SmoothPlastic", 0, 0, "moving-part signal cream (bands ONLY on moving parts)"),
    "Moonstone":   ("#E6E2F0", "Marble", 0, 0, "H16 pearl moonstone coping / flags"),
    "Silver":      ("#C8CDD8", "Metal", 0, 0, "silver inlay, crescent spout trim"),
    "Canvas":      ("#7A5CC8", "Fabric", 0, 0, "static hut canvas/paint violet (static props avoid red/cream)"),
    "HullTeal":    ("#2F5D7A", "WoodPlanks", 0, 0, "H12 static icebreaker hull (not red: red/cream reserved for movers)"),
    "Felt":        ("#36997A", "Fabric", 0, 0, "felt top strips on meshes that carry felt (H3 plank); matches pass 2g felt"),
    "SignalGreen": ("#5CFF7A", "Neon", 3.0, 0, "H5 signal lamp lens (script tints green/amber)"),
}

# ----------------------------------------------------------------------------- textures
# material: (png in models/textures/, studs per texture repeat). Materials not listed stay flat colour
# (caps, paper, glow, water, iron, ink). UVs are box-projected in prop space (see box_uv).
import os as _os
TEX_DIR = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "textures")
TEX = {
    "Timber": ("timber", 4.0),
    "Snow": ("snow", 6.0),
    "SnowShadow": ("snow", 6.0),
    "Rock": ("slate_rock", 6.0),
    "Basalt": ("basalt_hex", 3.0),
    "Ice": ("ice", 6.0),
    "IceSheen": ("ice", 8.0),
    "CoralPink": ("coral", 3.0),
    "Moonstone": ("moonstone", 4.0),
    "Felt": ("felt", 8.0),
}
USE_TEX = True
# pass 4: alpha-cut card materials (texture alpha -> Alpha, per-face 0..1 "card" UVs instead of box projection)
# and self-lit textured materials (texture also drives Emission Color)
CARD_MATS = set()
EMIT_TEX = set()


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def srgb_to_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def get_mat(name):
    m = bpy.data.materials.get(name)
    if m:
        return m
    hexv, rbx, emis, transp, _ = MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    rgb = [srgb_to_lin(c) for c in hex_rgb(hexv)]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1)
    bsdf.inputs["Roughness"].default_value = 0.75 if name not in ("Ice", "IceSheen", "Lagoon", "Steam") else 0.12
    if emis:
        bsdf.inputs["Emission Color"].default_value = (*rgb, 1)
        bsdf.inputs["Emission Strength"].default_value = emis
    if transp:
        bsdf.inputs["Alpha"].default_value = 1 - transp
        m.blend_method = "BLEND" if hasattr(m, "blend_method") else None
    m.diffuse_color = (*rgb, 1)
    if USE_TEX and name in TEX:
        path = _os.path.join(TEX_DIR, TEX[name][0] + ".png")
        if _os.path.exists(path):
            nt = m.node_tree
            tex = nt.nodes.new("ShaderNodeTexImage")
            tex.image = bpy.data.images.load(path, check_existing=True)
            tex.location = (-400, 200)
            nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            bsdf.inputs["Roughness"].default_value = 0.85
            if name in CARD_MATS:
                nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
                tex.interpolation = "Closest"
            if name in EMIT_TEX:
                nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
            if name == "Felt":
                # pass 4: soft velvet look + faint nap normal map (felt_normal.png) so slopes read
                bsdf.inputs["Roughness"].default_value = 0.95
                # pass 7: stronger sheen + normal (nap) so slopes / the H9 dip read
                for k, v in (("Sheen Weight", 0.45), ("Sheen Roughness", 0.45), ("Sheen Tint", (0.35, 0.75, 0.3, 1.0)),
                             ("Specular IOR Level", 0.2)):
                    if k in bsdf.inputs:
                        bsdf.inputs[k].default_value = v
                npath = _os.path.join(TEX_DIR, "felt_normal.png")
                if _os.path.exists(npath):
                    nimg = nt.nodes.new("ShaderNodeTexImage")
                    nimg.image = bpy.data.images.load(npath, check_existing=True)
                    nimg.image.colorspace_settings.name = "Non-Color"
                    nm = nt.nodes.new("ShaderNodeNormalMap")
                    nm.inputs["Strength"].default_value = 1.0
                    nt.links.new(nimg.outputs["Color"], nm.inputs["Color"])
                    nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def card_uv_bmesh(b):
    """Each face gets the whole texture: U along the face's horizontal axis, V up (0 = face bottom, 1 = top)."""
    uv = b.loops.layers.uv.get("UVMap") or b.loops.layers.uv.new("UVMap")
    b.normal_update()
    for f in b.faces:
        n = f.normal
        h = Vector((0, 0, 1)).cross(n)
        h = h.normalized() if h.length > 1e-6 else Vector((1, 0, 0))
        us = [l.vert.co.dot(h) for l in f.loops]
        zs = [l.vert.co.z for l in f.loops]
        u0, u1, z0, z1 = min(us), max(us), min(zs), max(zs)
        for l, u, z in zip(f.loops, us, zs):
            l[uv].uv = ((u - u0) / max(u1 - u0, 1e-6), (z - z0) / max(z1 - z0, 1e-6))


def uv_bmesh(b, mat):
    if mat in CARD_MATS:
        card_uv_bmesh(b)
    else:
        box_uv_bmesh(b, TEX.get(mat, (None, 4.0))[1])


def box_uv_bmesh(b, tile):
    """Box (cube) projection in prop space: each face uses the two axes perpendicular to its dominant normal,
    1 texture repeat per `tile` studs. Side faces map V to height, so bark/grain textures run vertically."""
    uv = b.loops.layers.uv.get("UVMap") or b.loops.layers.uv.new("UVMap")
    b.normal_update()
    k = 1.0 / tile
    for f in b.faces:
        n = f.normal
        ax, ay, az = abs(n.x), abs(n.y), abs(n.z)
        for l in f.loops:
            c = l.vert.co
            if az >= ax and az >= ay:
                l[uv].uv = (c.x * k, c.y * k)
            elif ax >= ay:
                l[uv].uv = (c.y * k, c.z * k)
            else:
                l[uv].uv = (c.x * k, c.z * k)


def mat_of(obj_name):
    return obj_name.split("__", 1)[1].split("_")[0]


def box_uv_objects(objs):
    """(Re)apply box UVs to finalized prop meshes (after booleans etc.), in each mesh's own space."""
    for o in objs:
        if o.type != "MESH" or o.get("lg_keep_uv"):      # pass 10: hand-made UVs (WristFace 0-1 quad)
            continue
        b = bmesh.new()
        b.from_mesh(o.data)
        uv_bmesh(b, mat_of(o.name))
        b.to_mesh(o.data)
        b.free()


# ----------------------------------------------------------------------------- coords
def R(x, y, z):
    """Roblox/hole-local (x, y-up, z) -> Blender vector."""
    return Vector((x, -z, y))


def M(loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    """Blender-space matrix: translation * rotation(XYZ euler, degrees) * scale."""
    from mathutils import Euler
    S = Matrix.Diagonal((*scale, 1))
    Rm = Euler([math.radians(a) for a in rot], "XYZ").to_matrix().to_4x4()
    return Matrix.Translation(Vector(loc)) @ Rm @ S


# ----------------------------------------------------------------------------- builder
_scratch = None


def _scratch_mesh():
    global _scratch
    if _scratch is None or _scratch.name not in bpy.data.meshes:
        _scratch = bpy.data.meshes.new("_scratch")
    return _scratch


class PB:
    """Prop builder: accumulate geometry per material, then finalize into objects."""

    def __init__(self, name, frame=None):
        self.name = name
        self.bms = {}
        # frame: matrix applied to every add (e.g. translate hole-local coords so origin = prop origin)
        self.frame = frame or Matrix.Identity(4)

    def set_origin_at(self, blender_point):
        """Subsequent geometry given in absolute coords; origin becomes blender_point."""
        self.frame = Matrix.Translation(-Vector(blender_point))

    def bm(self, mat):
        if mat not in self.bms:
            self.bms[mat] = bmesh.new()
        return self.bms[mat]

    def add(self, mat, tbm, matrix=None, smooth=False, free=True):
        mtx = self.frame @ (matrix or Matrix.Identity(4))
        bmesh.ops.transform(tbm, matrix=mtx, verts=tbm.verts)
        for f in tbm.faces:
            f.smooth = smooth
        me = _scratch_mesh()
        tbm.to_mesh(me)
        self.bm(mat).from_mesh(me)
        if free:
            tbm.free()

    # --- primitives (all take a Blender-space matrix) ---
    def box(self, mat, size, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.0, matrix=None, smooth=False, segs=1):
        t = bmesh.new()
        bmesh.ops.create_cube(t, size=1.0)
        bmesh.ops.scale(t, vec=Vector(size), verts=t.verts)
        if bevel > 0:
            bmesh.ops.bevel(t, geom=list(t.edges), offset=min(bevel, min(size) * 0.45), segments=segs,
                            affect="EDGES", profile=0.5)
        self.add(mat, t, (matrix or Matrix.Identity(4)) @ M(loc, rot), smooth)

    def cyl(self, mat, r1, r2, depth, segs=12, loc=(0, 0, 0), rot=(0, 0, 0), matrix=None, smooth=True,
            caps=True, base_at_zero=False):
        t = bmesh.new()
        bmesh.ops.create_cone(t, cap_ends=caps, cap_tris=False, segments=segs, radius1=r1, radius2=r2, depth=depth)
        if base_at_zero:
            bmesh.ops.translate(t, vec=(0, 0, depth / 2), verts=t.verts)
        self.add(mat, t, (matrix or Matrix.Identity(4)) @ M(loc, rot), smooth)
        return

    def sphere(self, mat, r, loc=(0, 0, 0), scale=(1, 1, 1), rot=(0, 0, 0), segs=12, rings=8, matrix=None,
               smooth=True, ico=0):
        t = bmesh.new()
        if ico:
            bmesh.ops.create_icosphere(t, subdivisions=ico, radius=r)
        else:
            bmesh.ops.create_uvsphere(t, u_segments=segs, v_segments=rings, radius=r)
        self.add(mat, t, (matrix or Matrix.Identity(4)) @ M(loc, rot, scale), smooth)

    def rock(self, mat, size, loc=(0, 0, 0), rot=(0, 0, 0), seed=0, amp=0.18, ico=1, matrix=None, flat_bottom=True,
             smooth=False):
        t = bmesh.new()
        bmesh.ops.create_icosphere(t, subdivisions=ico, radius=0.5)
        off = Vector((seed * 3.17, seed * 1.71, seed * 2.33))
        for v in t.verts:
            n = noise.noise(v.co * 2.2 + off)
            v.co *= 1 + amp * n * 2
        bmesh.ops.scale(t, vec=Vector(size), verts=t.verts)
        if flat_bottom:
            zmin = -size[2] * 0.30
            for v in t.verts:
                if v.co.z < zmin:
                    v.co.z = zmin
            bmesh.ops.translate(t, vec=(0, 0, -zmin), verts=t.verts)
            bmesh.ops.remove_doubles(t, verts=t.verts, dist=0.01)
        self.add(mat, t, (matrix or Matrix.Identity(4)) @ M(loc, rot), smooth)

    def lathe(self, mat, profile, segs=16, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), matrix=None,
              smooth=True, wobble=0.0, seed=0, phase=0.0):
        """profile: list of (radius, z) from bottom to top. radius 0 -> pole."""
        t = bmesh.new()
        rings = []
        for (r, z) in profile:
            if r <= 1e-6:
                rings.append([t.verts.new((0, 0, z))])
            else:
                ring = []
                for i in range(segs):
                    a = TAU * i / segs + phase
                    rr = r * (1 + wobble * noise.noise(Vector((math.cos(a) * 2, math.sin(a) * 2, z + seed))))
                    ring.append(t.verts.new((rr * math.cos(a), rr * math.sin(a), z)))
                rings.append(ring)
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
        # cap open ends
        if len(rings[0]) > 1:
            t.faces.new(list(reversed(rings[0])))
        if len(rings[-1]) > 1:
            t.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(t, faces=t.faces)
        self.add(mat, t, (matrix or Matrix.Identity(4)) @ M(loc, rot, scale), smooth)

    def tube(self, mat, pts, radii, segs=8, matrix=None, smooth=True, caps=True, wobble=0.0, seed=0,
             flatten=1.0):
        """Sweep a circle along pts (Blender vectors); radii: float or list per point."""
        pts = [Vector(p) for p in pts]
        if not isinstance(radii, (list, tuple)):
            radii = [radii] * len(pts)
        t = bmesh.new()
        # parallel transport frames
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
            bnorm = tg.cross(n).normalized()
            ring = []
            for k in range(segs):
                a = TAU * k / segs
                r = radii[i] * (1 + wobble * noise.noise(p * 1.7 + Vector((k, seed, 0)) * 0.9))
                ring.append(t.verts.new(p + (n * math.cos(a) * flatten + bnorm * math.sin(a)) * r))
            rings.append(ring)
        for a, b in zip(rings, rings[1:]):
            for k in range(segs):
                t.faces.new((a[k], a[(k + 1) % segs], b[(k + 1) % segs], b[k]))
        if caps:
            t.faces.new(list(reversed(rings[0])))
            t.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(t, faces=t.faces)
        self.add(mat, t, matrix, smooth)

    def torus(self, mat, R_, r, segs=24, rsegs=8, loc=(0, 0, 0), rot=(0, 0, 0), matrix=None, smooth=True):
        t = bmesh.new()
        rings = []
        for i in range(segs):
            a = TAU * i / segs
            c = Vector((math.cos(a), math.sin(a), 0))
            ring = []
            for k in range(rsegs):
                b = TAU * k / rsegs
                ring.append(t.verts.new(c * (R_ + r * math.cos(b)) + Vector((0, 0, r * math.sin(b)))))
            rings.append(ring)
        for i in range(segs):
            a, b = rings[i], rings[(i + 1) % segs]
            for k in range(rsegs):
                t.faces.new((a[k], b[k], b[(k + 1) % rsegs], a[(k + 1) % rsegs]))
        bmesh.ops.recalc_face_normals(t, faces=t.faces)
        self.add(mat, t, (matrix or Matrix.Identity(4)) @ M(loc, rot), smooth)

    def prism(self, mat, poly, depth, loc=(0, 0, 0), rot=(0, 0, 0), matrix=None, smooth=False):
        """Extrude a 2D polygon (x, y) along +Z by depth (centered on z=0)."""
        t = bmesh.new()
        bot = [t.verts.new((x, y, -depth / 2)) for x, y in poly]
        top = [t.verts.new((x, y, depth / 2)) for x, y in poly]
        n = len(poly)
        t.faces.new(list(reversed(bot)))
        t.faces.new(top)
        for i in range(n):
            t.faces.new((bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i]))
        bmesh.ops.recalc_face_normals(t, faces=t.faces)
        bmesh.ops.triangulate(t, faces=[f for f in t.faces if len(f.verts) > 4])
        self.add(mat, t, (matrix or Matrix.Identity(4)) @ M(loc, rot), smooth)

    def loft(self, mat, sections, matrix=None, smooth=False, caps=True):
        """sections: list of equal-length vertex loops (Blender vectors)."""
        t = bmesh.new()
        rings = [[t.verts.new(Vector(p)) for p in sec] for sec in sections]
        n = len(sections[0])
        for a, b in zip(rings, rings[1:]):
            for k in range(n):
                t.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
        if caps:
            t.faces.new(list(reversed(rings[0])))
            t.faces.new(rings[-1])
        bmesh.ops.recalc_face_normals(t, faces=t.faces)
        bmesh.ops.triangulate(t, faces=[f for f in t.faces if len(f.verts) > 4])
        self.add(mat, t, matrix, smooth)

    def plane(self, mat, sx, sy, loc=(0, 0, 0), rot=(0, 0, 0), nx=1, ny=1, matrix=None, smooth=False, ripple=0.0,
              seed=0):
        t = bmesh.new()
        bmesh.ops.create_grid(t, x_segments=nx, y_segments=ny, size=0.5)
        bmesh.ops.scale(t, vec=(sx, sy, 1), verts=t.verts)
        if ripple:
            for v in t.verts:
                v.co.z += ripple * noise.noise(Vector((v.co.x * 0.6, v.co.y * 0.6, seed)))
        self.add(mat, t, (matrix or Matrix.Identity(4)) @ M(loc, rot), smooth)

    # --- composite helpers ---
    def finalize(self, collection, smooth_angle=40.0):
        root = bpy.data.objects.new(self.name, None)
        root.empty_display_size = 0.5
        collection.objects.link(root)
        objs = []
        for mat, b in sorted(self.bms.items()):
            bmesh.ops.remove_doubles(b, verts=b.verts, dist=0.0005)
            bmesh.ops.triangulate(b, faces=[f for f in b.faces if len(f.verts) > 4])
            base_mat, _, tag = mat.partition("#")
            oname = f"{self.name}__{base_mat}" + (f"_{tag}" if tag else "")
            me = bpy.data.meshes.new(oname)
            uv_bmesh(b, base_mat)
            b.to_mesh(me)
            b.free()
            try:
                me.set_sharp_from_angle(angle=math.radians(smooth_angle))
            except Exception:
                pass
            me.materials.append(get_mat(base_mat))
            ob = bpy.data.objects.new(oname, me)
            collection.objects.link(ob)
            ob.parent = root
            objs.append(ob)
        self.bms = {}
        return root, objs


def tri_count(objs):
    n = 0
    for o in objs:
        if o.type == "MESH":
            n += sum(len(p.vertices) - 2 for p in o.data.polygons)
    return n


def bbox_blender(objs):
    """World-space bbox (min, max) of mesh objects in Blender coords."""
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
    """Blender bbox -> Roblox size [x, y, z] and Roblox-space center offset from origin."""
    size = [mx.x - mn.x, mx.z - mn.z, mx.y - mn.y]
    c = (mn + mx) / 2
    center = [c.x, c.z, -c.y]
    return size, center


def apply_boolean(target, cutter_builder_fn, operation="DIFFERENCE", frame=None):
    """Boolean-cut a finalized mesh object with a temporary cutter mesh built by cutter_builder_fn(PB).
    The cutter puts its geometry in material "Cut"; frame should match the prop builder's frame."""
    pb = PB("_cutter", frame)
    cutter_builder_fn(pb)
    b = pb.bms.pop("Cut")
    me = bpy.data.meshes.new("_cutter")
    b.to_mesh(me)
    b.free()
    cut = bpy.data.objects.new("_cutter", me)
    bpy.context.scene.collection.objects.link(cut)
    mod = target.modifiers.new("cut", "BOOLEAN")
    mod.operation = operation
    mod.object = cut
    mod.solver = "EXACT"
    dg = bpy.context.evaluated_depsgraph_get()
    ev = target.evaluated_get(dg)
    newme = bpy.data.meshes.new_from_object(ev)
    old = target.data
    target.modifiers.clear()
    target.data = newme
    newme.name = old.name
    bpy.data.meshes.remove(old)
    bpy.data.objects.remove(cut)
    bpy.data.meshes.remove(me)
    # triangulate ngons left by boolean
    b = bmesh.new()
    b.from_mesh(target.data)
    bmesh.ops.triangulate(b, faces=[f for f in b.faces if len(f.verts) > 4])
    b.to_mesh(target.data)
    b.free()


def text_bm(text, size=1.0, extrude=0.05, font_path=None):
    """Return a bmesh of extruded, centred text lying in the XZ plane (readable from -Y), base on z=0."""
    cu = bpy.data.curves.new("_txt", "FONT")
    cu.body = text
    cu.size = size
    cu.extrude = extrude
    cu.align_x = "CENTER"
    cu.align_y = "BOTTOM_BASELINE"
    cu.resolution_u = 2
    if font_path:
        try:
            cu.font = bpy.data.fonts.load(font_path, check_existing=True)
        except Exception:
            pass
    ob = bpy.data.objects.new("_txt", cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    b = bmesh.new()
    b.from_mesh(me)
    bmesh.ops.remove_doubles(b, verts=b.verts, dist=0.0005)
    bmesh.ops.triangulate(b, faces=b.faces)
    # stand it up: text XY plane -> XZ plane facing -Y
    bmesh.ops.rotate(b, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, "X"), verts=b.verts)
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    bpy.data.meshes.remove(me)
    return b


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


def shell(pb, mat, outer_rings, inner_rings, matrix=None, smooth=True):
    """Closed hollow solid between outer and inner ring stacks (same vertex counts)."""
    t = bmesh.new()
    O = [[t.verts.new(p) for p in r] for r in outer_rings]
    I = [[t.verts.new(p) for p in r] for r in inner_rings]
    n = len(outer_rings[0])
    def strip(A, B, flip=False):
        for a, b in zip(A, B):
            for k in range(n):
                q = (a[k], a[(k + 1) % n], b[(k + 1) % n], b[k])
                t.faces.new(tuple(reversed(q)) if flip else q)
    strip(O, O[1:])
    strip(I, I[1:], flip=True)
    strip([O[-1]], [I[-1]])
    strip([I[0]], [O[0]])
    bmesh.ops.recalc_face_normals(t, faces=t.faces)
    pb.add(mat, t, matrix, smooth)


# ----------------------------------------------------------------------------- Aurora helpers (Roblox-space input)
def hbox(pb, mat, c, s, yaw=0.0, bevel=0.0, segs=1, pitch=0.0, roll=0.0):
    """Box from Roblox centre c / size s (x, y, z) / yaw (deg about +Y); optional pitch (about local X) / roll (about local Z)."""
    mtx = Matrix.Translation(R(*c)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @         Matrix.Rotation(math.radians(-pitch), 4, "X") @ Matrix.Rotation(math.radians(roll), 4, "Y")
    pb.box(mat, (s[0], s[2], s[1]), bevel=bevel, segs=segs, matrix=mtx)


def prism_y(pb, mat, poly, y0, y1, yaw=0.0, at=(0.0, 0.0), matrix=None):
    """Extrude a Roblox (x, z) polygon (counter-clockwise or not) vertically from y0 to y1."""
    t = bmesh.new()
    a = math.radians(yaw)
    pts = []
    for x, z in poly:
        rx = x * math.cos(a) + z * math.sin(a) + at[0]
        rz = -x * math.sin(a) + z * math.cos(a) + at[1]
        pts.append((rx, -rz))
    bot = [t.verts.new((x, y, y0)) for x, y in pts]
    top = [t.verts.new((x, y, y1)) for x, y in pts]
    n = len(pts)
    t.faces.new(bot)
    t.faces.new(top)
    for i in range(n):
        t.faces.new((bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i]))
    bmesh.ops.recalc_face_normals(t, faces=t.faces)
    bmesh.ops.triangulate(t, faces=[f for f in t.faces if len(f.verts) > 4])
    pb.add(mat, t, matrix)


def surface_quad(pb, mat, pts_roblox):
    """One flat polygon from Roblox points (already at the right heights)."""
    t = bmesh.new()
    vs = [t.verts.new(R(*p)) for p in pts_roblox]
    f = t.faces.new(vs)
    f.normal_update()
    if f.normal.z < 0:
        f.normal_flip()
    bmesh.ops.triangulate(t, faces=[f for f in t.faces if len(f.verts) > 4])
    pb.add(mat, t)


def lantern_head(pb, base, s=1.0, glow="Glow", cap="Snow"):
    """Brass lantern head (ember core) standing on Roblox point `base`, about 0.9*s wide, 1.4*s tall."""
    x, y, z = base
    hbox(pb, "Brass", (x, y + 0.08 * s, z), (0.9 * s, 0.16 * s, 0.9 * s), bevel=0.03 * s)
    hbox(pb, glow, (x, y + 0.6 * s, z), (0.56 * s, 0.88 * s, 0.56 * s))
    for dx in (-1, 1):
        for dz in (-1, 1):
            hbox(pb, "Brass", (x + dx * 0.33 * s, y + 0.6 * s, z + dz * 0.33 * s), (0.1 * s, 0.9 * s, 0.1 * s))
    hbox(pb, "Brass", (x, y + 1.1 * s, z), (0.9 * s, 0.12 * s, 0.9 * s), bevel=0.03 * s)
    pb.cyl("Brass", 0.62 * s, 0.05 * s, 0.32 * s, 4, loc=tuple(R(x, y + 1.32 * s, z)), rot=(0, 0, 45), smooth=False)
    if cap:
        pb.cyl(cap, 0.5 * s, 0.0, 0.2 * s, 6, loc=tuple(R(x, y + 1.42 * s, z)), smooth=False)
