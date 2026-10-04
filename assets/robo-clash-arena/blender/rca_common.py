"""Shared helpers for Robo Clash Arena Blender generators (headless).

Everything is authored in ROBLOX coordinates (studs): X right, Y up, -Z forward, ground at y=0.
Each piece goes into a named part (one MeshPart in Studio) with per-face vertex colors.
Pieces flagged glow=True go to "<part>Glow" (imported as Neon in Studio).

Verified on the 3D Importer (Oct 2026): Blender (x, y, z) lands in Roblox at (-x, z, y) with the
export settings below, vertex colors render (MeshPart.Color multiplies them, so use white), and
Neon MeshParts glow with their vertex colors.
"""
import bpy, bmesh, math, json, os, sys
from mathutils import Vector, Matrix


def rgb(r, g, b):
    return (r / 255.0, g / 255.0, b / 255.0)


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def to_blender(v):
    return Vector((-v[0], v[2], v[1]))


def rot(rx=0.0, ry=0.0, rz=0.0):
    """Roblox CFrame.Angles(rx, ry, rz) in degrees (applied Z, then Y, then X)."""
    return (Matrix.Rotation(math.radians(rx), 4, 'X') @ Matrix.Rotation(math.radians(ry), 4, 'Y')
            @ Matrix.Rotation(math.radians(rz), 4, 'Z'))


def xf(pos=(0, 0, 0), r=(0, 0, 0)):
    return Matrix.Translation(Vector(pos)) @ rot(*r)


class Builder:
    def __init__(self, name):
        self.name = name
        self.parts = {}  # part -> dict(verts, faces, cols, smooth)
        self.meta = {"name": name, "joints": [], "attachments": {}, "parts": {}}

    # ------------------------------------------------------------------ core
    def _target(self, part, glow):
        key = part + ("Glow" if glow else "")
        if key not in self.parts:
            self.parts[key] = {"verts": [], "faces": [], "cols": [], "smooth": []}
            self.meta["parts"][key] = {"limb": part, "glow": glow}
        return self.parts[key]

    def _emit(self, bm, part, color, M, glow=False, smooth=True, mirror_x=False):
        if mirror_x:
            M = Matrix.Scale(-1, 4, Vector((1, 0, 0))) @ M
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
        t = self._target(part, glow)
        base = len(t["verts"])
        bm.verts.index_update()
        for v in bm.verts:
            t["verts"].append(tuple(M @ v.co))
        flip = M.to_3x3().determinant() < 0
        for f in bm.faces:
            idx = [base + v.index for v in f.verts]
            if flip:
                idx.reverse()
            t["faces"].append(idx)
            t["cols"].append(color if not callable(color) else color(f, M))
            t["smooth"].append(smooth)
        bm.free()

    @staticmethod
    def _bevel(bm, amount, segs=2, edges=None):
        if amount <= 0:
            return
        es = edges if edges is not None else list(bm.edges)
        bmesh.ops.bevel(bm, geom=list(es), offset=amount, offset_type='OFFSET', segments=segs,
                        profile=0.5, affect='EDGES', clamp_overlap=True)

    # ------------------------------------------------------------ primitives
    def box(self, part, size, pos=(0, 0, 0), r=(0, 0, 0), color=(1, 1, 1), bevel=0.15, segs=2, glow=False,
            taper=None, mirror=False):
        """Rounded box. taper=(sx, sz) scales the top face (y+) for tapered shapes."""
        b = min(bevel, min(size) * 0.45)

        def make():
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=1.0)
            for v in bm.verts:
                v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
                if taper and v.co.y > 0:
                    v.co.x *= taper[0]
                    v.co.z *= taper[1]
            self._bevel(bm, b, segs)
            return bm
        self._emit(make(), part, color, xf(pos, r), glow, smooth=b > 0)
        if mirror:
            self._emit(make(), part if mirror is True else mirror, color, xf(pos, r), glow, smooth=b > 0,
                       mirror_x=True)

    def cyl(self, part, radius, depth, pos=(0, 0, 0), r=(0, 0, 0), color=(1, 1, 1), segs=16, bevel=0.06,
            radius2=None, glow=False, cap=True, mirror=False):
        """Cylinder along local Y (use r=(90,0,0) to point it along Z)."""
        def make():
            bm = bmesh.new()
            bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=segs, radius1=radius,
                                  radius2=radius if radius2 is None else radius2, depth=depth,
                                  matrix=Matrix.Rotation(math.radians(-90), 4, 'X'))
            if bevel > 0 and cap:
                rim = [e for e in bm.edges if len(e.link_faces) == 2 and
                       abs(e.link_faces[0].normal.dot(e.link_faces[1].normal)) < 0.5]
                self._bevel(bm, min(bevel, depth * 0.3, radius * 0.4), 2, rim)
            return bm
        self._emit(make(), part, color, xf(pos, r), glow)
        if mirror:
            self._emit(make(), part if mirror is True else mirror, color, xf(pos, r), glow, mirror_x=True)

    def sphere(self, part, radius, pos=(0, 0, 0), r=(0, 0, 0), color=(1, 1, 1), scale=(1, 1, 1), segs=(14, 9),
               glow=False, mirror=False, cut=None):
        """UV sphere, optionally scaled into an ellipsoid. cut=y keeps only verts with local y >= cut*radius."""
        def make():
            bm = bmesh.new()
            bmesh.ops.create_uvsphere(bm, u_segments=segs[0], v_segments=segs[1], radius=radius)
            if cut is not None:
                geom = [v for v in bm.verts if v.co.z < cut * radius - 1e-4]
                bmesh.ops.delete(bm, geom=geom, context='VERTS')
                edges = [e for e in bm.edges if e.is_boundary]
                if edges:
                    bmesh.ops.edgeloop_fill(bm, edges=edges)
            for v in bm.verts:  # uvsphere is Z-up; make local Y the pole axis
                v.co = Vector((v.co.x * scale[0], v.co.z * scale[1], -v.co.y * scale[2]))
            return bm
        self._emit(make(), part, color, xf(pos, r), glow)
        if mirror:
            self._emit(make(), part if mirror is True else mirror, color, xf(pos, r), glow, mirror_x=True)

    def torus(self, part, R, rr, pos=(0, 0, 0), r=(0, 0, 0), color=(1, 1, 1), segs=20, rsegs=8, glow=False,
              mirror=False, scale_y=1.0):
        """Torus around local Y."""
        def make():
            bm = bmesh.new()
            rings = []
            for i in range(segs):
                a = 2 * math.pi * i / segs
                ring = []
                for j in range(rsegs):
                    b = 2 * math.pi * j / rsegs
                    rad = R + rr * math.cos(b)
                    ring.append(bm.verts.new((rad * math.cos(a), rr * math.sin(b) * scale_y, rad * math.sin(a))))
                rings.append(ring)
            for i in range(segs):
                for j in range(rsegs):
                    a, b = rings[i], rings[(i + 1) % segs]
                    bm.faces.new((a[j], a[(j + 1) % rsegs], b[(j + 1) % rsegs], b[j]))
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            return bm
        self._emit(make(), part, color, xf(pos, r), glow)
        if mirror:
            self._emit(make(), part if mirror is True else mirror, color, xf(pos, r), glow, mirror_x=True)

    def lathe(self, part, profile, pos=(0, 0, 0), r=(0, 0, 0), color=(1, 1, 1), segs=16, glow=False, mirror=False,
              colors=None, smooth=True):
        """Revolve [(radius, y), ...] around local Y. colors: optional per-band color list."""
        def make():
            bm = bmesh.new()
            rings = []
            for (rad, y) in profile:
                if rad <= 1e-5:
                    rings.append([bm.verts.new((0, y, 0))])
                else:
                    rings.append([bm.verts.new((rad * math.cos(2 * math.pi * i / segs), y,
                                                rad * math.sin(2 * math.pi * i / segs))) for i in range(segs)])
            band_of = {}
            for k in range(len(rings) - 1):
                a, b = rings[k], rings[k + 1]
                for i in range(segs):
                    if len(a) == 1 and len(b) == 1:
                        continue
                    if len(a) == 1:
                        f = bm.faces.new((a[0], b[(i + 1) % segs], b[i]))
                    elif len(b) == 1:
                        f = bm.faces.new((a[i], a[(i + 1) % segs], b[0]))
                    else:
                        f = bm.faces.new((a[i], a[(i + 1) % segs], b[(i + 1) % segs], b[i]))
                    band_of[f] = k
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.faces.index_update()
            return bm, band_of
        def colfn(f, M, band_of):
            if colors is None:
                return color
            return colors[min(band_of.get(f, 0), len(colors) - 1)]
        for mx in ([False, True] if mirror else [False]):
            bm, band_of = make()
            self._emit(bm, (part if not mx or mirror is True else mirror), (lambda f, M, bo=band_of: colfn(f, M, bo)),
                       xf(pos, r), glow, smooth=smooth, mirror_x=mx)

    def hull(self, part, points, pos=(0, 0, 0), r=(0, 0, 0), color=(1, 1, 1), bevel=0.0, glow=False, mirror=False,
             smooth=False):
        """Convex hull of local points (chunky custom shapes: ears, fins, wedges)."""
        def make():
            bm = bmesh.new()
            vs = [bm.verts.new(p) for p in points]
            res = bmesh.ops.convex_hull(bm, input=vs)
            drop = {g for g in res.get("geom_interior", []) + res.get("geom_unused", [])
                    if isinstance(g, bmesh.types.BMVert)}
            bmesh.ops.delete(bm, geom=list(drop), context='VERTS')
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            if bevel > 0:
                self._bevel(bm, bevel, 2)
            return bm
        self._emit(make(), part, color, xf(pos, r), glow, smooth=smooth or bevel > 0)
        if mirror:
            self._emit(make(), part if mirror is True else mirror, color, xf(pos, r), glow,
                       smooth=smooth or bevel > 0, mirror_x=True)

    # ------------------------------------------------------------------- rig
    def joint(self, name, part, parent, pivot, anim=None, r=(0, 0, 0)):
        """Motor6D `name` driving limb `part` from `parent` around world `pivot` (Roblox coords), joint frame
        rotated by Roblox Euler degrees `r`. `anim` is a hint for RobotAnim (e.g. "spin", "wobble", "orbit")."""
        self.meta["joints"].append({"name": name, "part": part, "parent": parent, "pivot": list(pivot),
                                    "rot": list(r), "anim": anim})

    def attach(self, name, part, pos):
        self.meta["attachments"][name] = {"part": part, "pos": list(pos)}

    # --------------------------------------------------------------- output
    def build_objects(self, collection=None):
        objs = []
        coll = collection or bpy.context.scene.collection
        for key, t in self.parts.items():
            me = bpy.data.meshes.new(key)
            me.from_pydata([to_blender(v) for v in t["verts"]], [], t["faces"])
            me.validate(clean_customdata=False)
            me.update()
            attr = me.color_attributes.new(name="Col", type='BYTE_COLOR', domain='CORNER')
            for i, poly in enumerate(me.polygons):
                c = t["cols"][i]
                poly.use_smooth = t["smooth"][i]
                for li in poly.loop_indices:
                    attr.data[li].color_srgb = (c[0], c[1], c[2], 1.0)
            try:
                me.set_sharp_from_angle(angle=math.radians(38))
            except Exception:
                pass
            ob = bpy.data.objects.new(key, me)
            coll.objects.link(ob)
            ob.data.materials.append(vcol_material(glow=self.meta["parts"][key]["glow"]))
            objs.append(ob)
        return objs

    def tri_count(self):
        n = 0
        for t in self.parts.values():
            for f in t["faces"]:
                n += len(f) - 2
        return n

    def part_tris(self):
        return {k: sum(len(f) - 2 for f in t["faces"]) for k, t in self.parts.items()}


_MATS = {}


def vcol_material(glow=False):
    key = "glow" if glow else "solid"
    if key in _MATS:
        return _MATS[key]
    mat = bpy.data.materials.new("RCA_" + key)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    ca = nt.nodes.new("ShaderNodeVertexColor")
    ca.layer_name = "Col"
    nt.links.new(ca.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.45
    if glow:
        nt.links.new(ca.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = 2.0
    _MATS[key] = mat
    return mat


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _MATS.clear()
    sc = bpy.context.scene
    sc.unit_settings.system = 'NONE'
    return sc


def export_fbx(path):
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        if o.type == 'MESH' and not o.name.startswith("_"):
            o.select_set(True)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_scale_options='FBX_SCALE_UNITS',
                             axis_forward='Z', axis_up='Y', path_mode='COPY', embed_textures=True,
                             add_leaf_bones=False, bake_anim=False, mesh_smooth_type='OFF', colors_type='SRGB',
                             use_mesh_modifiers=True)


def render_preview(path, objs, views=((200, 15), (130, 15), (20, 15), (165, 55)), size=(1600, 520), focus_y=4.0,
                   spacing=9.0, cam_dist=None, bg=(0.55, 0.62, 0.72)):
    """Workbench render of the model from several yaw angles (Roblox degrees around Y, 180 = facing camera)
    side by side, by instancing the objects into a collection."""
    sc = bpy.context.scene
    src = bpy.data.collections.new("_src")
    for o in objs:
        for c in o.users_collection:
            c.objects.unlink(o)
        src.objects.link(o)
    n = len(views)
    for i, (yaw, pitch) in enumerate(views):
        e = bpy.data.objects.new("_inst%d" % i, None)
        e.instance_type = 'COLLECTION'
        e.instance_collection = src
        x = -(i - (n - 1) / 2) * spacing
        e.location = to_blender((x, 0, 0))
        e.rotation_mode = 'ZXY'
        e.rotation_euler = (0, 0, math.radians(-yaw + 180))
        if pitch > 40:  # gameplay-like view: tilt the instance towards the camera
            e.location = to_blender((x, 1.5, 0))
            e.rotation_euler = (math.radians(pitch - 15), 0, math.radians(-yaw + 180))
        sc.collection.objects.link(e)
    cam_d = bpy.data.cameras.new("_cam")
    cam_d.type = 'ORTHO'
    cam_d.ortho_scale = spacing * n * 1.02
    cam = bpy.data.objects.new("_cam", cam_d)
    sc.collection.objects.link(cam)
    cam.location = to_blender((0, focus_y + 3.0, -40))
    look = to_blender((0, focus_y, 0)) - cam.location
    cam.rotation_euler = look.to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    sc.render.engine = 'BLENDER_WORKBENCH'
    sh = sc.display.shading
    sh.light = 'STUDIO'
    sh.color_type = 'VERTEX'
    sh.show_shadows = True
    sh.show_cavity = True
    sh.cavity_type = 'BOTH'
    sh.show_object_outline = True
    sc.display.shadow_focus = 0.5
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.film_transparent = False
    world = bpy.data.worlds.new("_w")
    sc.world = world
    sh.background_type = 'VIEWPORT'
    sh.background_color = bg
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = path
    sc.view_settings.view_transform = 'Standard'
    bpy.ops.render.render(write_still=True)
    # restore: move objects back to scene root, drop helpers
    for o in list(src.objects):
        src.objects.unlink(o)
        sc.collection.objects.link(o)
    for o in list(sc.collection.objects):
        if o.name.startswith("_"):
            bpy.data.objects.remove(o)
    bpy.data.collections.remove(src)


def finish(b, outdir, preview=True, focus_y=4.0, spacing=9.0, views=None, size=None):
    """Build objects, write <name>.fbx, <name>_rig.json and <name>_preview.png into outdir."""
    os.makedirs(outdir, exist_ok=True)
    objs = b.build_objects()
    tris = b.tri_count()
    b.meta["tris"] = tris
    b.meta["part_tris"] = b.part_tris()
    fbx = os.path.join(outdir, b.name.lower() + ".fbx")
    export_fbx(fbx)
    with open(os.path.join(outdir, b.name.lower() + "_rig.json"), "w") as f:
        json.dump(b.meta, f, indent=1)
    if preview:
        kw = {}
        if views:
            kw["views"] = views
        if size:
            kw["size"] = size
        render_preview(os.path.join(outdir, b.name.lower() + "_preview.png"), objs, focus_y=focus_y,
                       spacing=spacing, **kw)
    print("RCA_DONE %s tris=%d parts=%d fbx=%s" % (b.name, tris, len(b.parts), fbx))
    return objs
