"""Rock-candy cluster generator (3D Model Bot, explicit). Pointed hex crystals radiating from a base point.
make_cluster(name, n_points=6, size=1.0, seed=0) -> object at origin (pivot = cluster base centre), Z-up.
Crystal lengths ~ (2.4..5.0)*size, radius (0.45..0.8)*size, splay 10-45 deg; colours alternate pink #F59AC8 / pale yellow #FFF1A8
(byte 'Col' layer, sRGB direct). Single material 'Glow_Crystal' (Neon in Roblox; preview emission ~0.6 from Col).
"""
import bpy, bmesh, math, random
from mathutils import Matrix, Vector
PINK = (0xF5/255, 0x9A/255, 0xC8/255, 1.0); YELLOW = (0xFF/255, 0xF1/255, 0xA8/255, 1.0)

def make_cluster(name, n_points=6, size=1.0, seed=0):
    assert 5 <= n_points <= 8
    rnd = random.Random(seed); me = bpy.data.meshes.new(name); bm = bmesh.new(); col = bm.loops.layers.color.new("Col")
    for i in range(n_points):
        L = rnd.uniform(2.4, 5.0)*size*(1.25 if i == 0 else 1.0); r = rnd.uniform(0.45, 0.8)*size
        az = 2*math.pi*i/n_points + rnd.uniform(-0.3, 0.3); tilt = 0.0 if i == 0 else rnd.uniform(10, 45)
        M = Matrix.Rotation(az, 4, 'Z') @ Matrix.Rotation(math.radians(tilt), 4, 'Y') @ Matrix.Rotation(rnd.uniform(0, 1), 4, 'Z')
        ring0 = [bm.verts.new(M @ Vector((r*math.cos(k*math.pi/3), r*math.sin(k*math.pi/3), -0.3*size))) for k in range(6)]
        ring1 = [bm.verts.new(M @ Vector((r*0.9*math.cos(k*math.pi/3), r*0.9*math.sin(k*math.pi/3), 0.72*L))) for k in range(6)]
        apex = bm.verts.new(M @ Vector((0, 0, L)))
        c = PINK if i % 2 == 0 else YELLOW
        fs = [bm.faces.new(list(reversed(ring0)))]
        fs += [bm.faces.new((ring0[k], ring0[(k+1)%6], ring1[(k+1)%6], ring1[k])) for k in range(6)]
        fs += [bm.faces.new((ring1[k], ring1[(k+1)%6], apex)) for k in range(6)]
        for f in fs:
            for lp in f.loops: lp[col] = c
    bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.get("Glow_Crystal") or bpy.data.materials.new("Glow_Crystal"); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes.get("Principled BSDF"); vc = nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "Col"
    nt.links.new(vc.outputs["Color"], b.inputs["Base Color"]); nt.links.new(vc.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.6; b.inputs["Roughness"].default_value = 0.3
    ob.data.materials.append(m); return ob
