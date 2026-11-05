"""Shared render helpers (Cycles GPU / OptiX) for pass-1 previews."""
import bpy, math, os
from mathutils import Vector, Matrix
import bwlib as L
import atlas_def as A


def setup_cycles(sc, samples=64, res=(768, 768)):
    try:
        sc.render.engine = "CYCLES"
    except TypeError as e:
        print("engine err", e)
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for t in ("OPTIX", "CUDA"):
        try:
            prefs.compute_device_type = t
            prefs.get_devices()
            ok = False
            for d in prefs.devices:
                d.use = d.type == t
                ok = ok or d.use
            if ok:
                sc.cycles.device = "GPU"
                break
        except Exception as e:
            print("device err", t, e)
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = "OPTIX"
    except Exception:
        pass
    sc.cycles.max_bounces = 6
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    try:
        sc.view_settings.view_transform = "Standard"
    except TypeError:
        pass
    sc.view_settings.look = "None"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"


def world(sc, hexv="#F2C7A8", strength=0.8, fog_density=0.0, fog_hex=None, zenith_hex=None):
    w = bpy.data.worlds.new("w")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (*L.lin(hexv), 1)
    bg.inputs["Strength"].default_value = strength
    if zenith_hex:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.0
        mr.inputs["From Max"].default_value = 0.45
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.inputs["A"].default_value = (*L.lin(hexv), 1)
        mix.inputs["B"].default_value = (*L.lin(zenith_hex), 1)
        nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
        nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], mix.inputs["Factor"])
        nt.links.new(mix.outputs["Result"], bg.inputs["Color"])
    if fog_density > 0:
        out = next(n for n in nt.nodes if n.type == "OUTPUT_WORLD")
        vol = nt.nodes.new("ShaderNodeVolumePrincipled")
        vol.inputs["Color"].default_value = (*L.lin(fog_hex or hexv), 1)
        vol.inputs["Density"].default_value = fog_density
        vol.inputs["Anisotropy"].default_value = 0.35
        nt.links.new(vol.outputs["Volume"], out.inputs["Volume"])
    return w


def sun(col, direction, hexv="#FFB46A", energy=3.5, angle_deg=3.0):
    s = bpy.data.lights.new("sun", "SUN")
    s.color = L.lin(hexv)
    s.energy = energy
    s.angle = math.radians(angle_deg)
    o = bpy.data.objects.new("sun", s)
    o.rotation_euler = Vector(direction).normalized().to_track_quat("-Z", "Y").to_euler()
    col.objects.link(o)
    return o


def flat_mat(name, hexv, rough=0.9, metal=0.0, emit=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*L.lin(hexv), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*L.lin(hexv), 1)
        b.inputs["Emission Strength"].default_value = emit
    return m


def plane(col, name, size, loc, mat):
    me = bpy.data.meshes.new(name)
    import bmesh
    b = bmesh.new()
    bmesh.ops.create_grid(b, x_segments=1, y_segments=1, size=0.5)
    bmesh.ops.scale(b, vec=(size[0], size[1], 1), verts=b.verts)
    b.to_mesh(me)
    b.free()
    me.materials.append(mat)
    o = bpy.data.objects.new(name, me)
    o.location = loc
    col.objects.link(o)
    return o


def fix_imported_materials(neon_strength=6.0):
    """FBX import loses emission/vertex-colour wiring: restore BW_Neon glow and BW_Backdrop vertex colour."""
    for m in bpy.data.materials:
        if not m.use_nodes:
            m.use_nodes = True
        nt = m.node_tree
        b = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if not b:
            continue
        if m.name.startswith("BW_Neon"):
            c = b.inputs["Base Color"].default_value
            b.inputs["Emission Color"].default_value = c
            b.inputs["Emission Strength"].default_value = neon_strength
        elif m.name.startswith("BW_Backdrop"):
            va = nt.nodes.new("ShaderNodeVertexColor")
            va.layer_name = "Col"
            nt.links.new(va.outputs["Color"], b.inputs["Base Color"])
            b.inputs["Roughness"].default_value = 0.9
        elif m.name.startswith("BW_Atlas"):
            b.inputs["Roughness"].default_value = 0.8
            try:
                b.inputs["Specular IOR Level"].default_value = 0.3
            except Exception:
                pass
            b.inputs["Metallic"].default_value = 0.0
            tex = next((n for n in nt.nodes if n.type == "TEX_IMAGE"), None)
            if tex is None or tex.image is None:
                tex = tex or nt.nodes.new("ShaderNodeTexImage")
                tex.image = bpy.data.images.load(L.ATLAS_PATH, check_existing=True)
                nt.links.new(tex.outputs["Color"], b.inputs["Base Color"])


def import_fbx(path, col):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path, axis_forward="-Z", axis_up="Y", global_scale=1.0)
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)
    return [o for o in new if o.type == "MESH"]


def capsule(col, loc, radius=1.0, height=5.0, hexv="#3F6FD8"):
    import bmesh
    b = bmesh.new()
    segs, rings = 20, 6
    prof = [(0.0, 0.0)]
    for i in range(1, rings + 1):
        a = math.pi / 2 * i / rings
        prof.append((radius * math.sin(a), radius - radius * math.cos(a)))
    for i in range(rings + 1):
        a = math.pi / 2 * i / rings
        prof.append((radius * math.cos(a), height - radius + radius * math.sin(a)))
    prof.append((0.0, height))
    rs = []
    for r, z in prof:
        if r < 1e-6:
            rs.append([b.verts.new((0, 0, z))])
        else:
            rs.append([b.verts.new((r * math.cos(math.tau * k / segs), r * math.sin(math.tau * k / segs), z))
                       for k in range(segs)])
    for a_, b_ in zip(rs, rs[1:]):
        if len(a_) == 1 and len(b_) == 1:
            continue
        if len(a_) == 1:
            for k in range(segs):
                b.faces.new((a_[0], b_[k], b_[(k + 1) % segs]))
        elif len(b_) == 1:
            for k in range(segs):
                b.faces.new((a_[k], b_[0], a_[(k + 1) % segs]))
        else:
            for k in range(segs):
                b.faces.new((a_[k], a_[(k + 1) % segs], b_[(k + 1) % segs], b_[k]))
    bmesh.ops.recalc_face_normals(b, faces=b.faces)
    me = bpy.data.meshes.new("capsule")
    b.to_mesh(me)
    b.free()
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(flat_mat("capsule", hexv, 0.6))
    o = bpy.data.objects.new("capsule_2x5", me)
    o.location = loc
    col.objects.link(o)
    return o


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def camera(col, name="cam", fov_deg=50.0, ortho=None):
    c = bpy.data.cameras.new(name)
    if ortho:
        c.type = "ORTHO"
        c.ortho_scale = ortho
    else:
        c.lens_unit = "FOV"
        c.sensor_fit = "HORIZONTAL"
        c.angle = math.radians(fov_deg)
    c.clip_start = 0.1
    c.clip_end = 3000
    o = bpy.data.objects.new(name, c)
    col.objects.link(o)
    bpy.context.scene.camera = o
    return o
