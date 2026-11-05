"""Explicit Aurora crown geometry (written by 3D Model Bot; do NOT redesign, only wire into the pipeline).
Blender Z-up, 1 BU = 1 stud, arch-local coords (X east, Blender -Y = Roblox +Z front). Pivot = arch base centre (0,0,0).
6 hexagonal pointed crystals: cylinder shaft (bottom 80%) + 6-sided pyramid tip (top 20% = Glow_Tips material).
Vertex colour attribute 'Col': violet #7A4FD0 at base -> teal #8FE3EE at tip (linear along crystal length).
Materials: slot 0 'BW_Crown_Crystal' (uses Col), slot 1 'Glow_Tips' (preview: emission #9FE6F2 strength 4; Roblox: Neon #9FE6F2).
"""
import bpy, bmesh, math
from mathutils import Matrix, Vector

VIOLET = (0x7A/255, 0x4F/255, 0xD0/255, 1.0)
TEAL   = (0x8F/255, 0xE3/255, 0xEE/255, 1.0)
def srgb2lin(c): return tuple(((x/12.92) if x <= 0.04045 else ((x+0.055)/1.055)**2.4) if i < 3 else x for i, x in enumerate(c))

# (length, radius, base x, base z, depth y, outward splay deg (+ = top leans +X), twist deg)
CRYSTALS = [
    (27.0, 2.3,  3.0, 14.5, 0.4,  10.0,  0.0),   # tallest, off-centre east
    (18.0, 1.7, -3.6, 14.5, 0.3, -15.0, 15.0),   # medium west
    (18.0, 1.6,  7.0, 14.0, 0.2,  20.0, 30.0),   # medium east
    (10.0, 1.1, -7.2, 13.8, 0.0, -25.0,  8.0),   # small far west
    (10.0, 1.0, -0.6, 15.0, -0.5, -12.0, 22.0),  # small centre-front (slightly toward front)
    (10.0, 1.1,  5.6, 15.2, 0.9,  25.0, 40.0),   # small east, behind
]
RINGS = (0.0, 0.27, 0.54, 0.8)   # shaft rings as fraction of length; tip apex at 1.0

def lerp(a, b, t): return tuple(a[i] + (b[i]-a[i])*t for i in range(4))

def build_crown(name="bw_scn_aurora_crown"):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    col = bm.loops.layers.color.new("Col")
    for (L, r, bx, bz, by, splay, twist) in CRYSTALS:
        M = (Matrix.Translation((bx, by, bz)) @ Matrix.Rotation(math.radians(splay), 4, 'Y')
             @ Matrix.Rotation(math.radians(twist), 4, 'Z'))
        rings = []
        for f in RINGS:
            rr = r * (1.0 - 0.08 * f)          # slight taper
            ring = [bm.verts.new(M @ Vector((rr*math.cos(k*math.pi/3), rr*math.sin(k*math.pi/3), f*L))) for k in range(6)]
            rings.append((f, ring))
        apex = bm.verts.new(M @ Vector((0, 0, L)))
        faces = []
        bottom = bm.faces.new(list(reversed(rings[0][1]))); bottom.material_index = 0; faces.append((bottom, None))
        for (f0, r0), (f1, r1) in zip(rings, rings[1:]):
            for k in range(6):
                fc = bm.faces.new((r0[k], r0[(k+1)%6], r1[(k+1)%6], r1[k])); fc.material_index = 0
        for k in range(6):
            fc = bm.faces.new((rings[-1][1][k], rings[-1][1][(k+1)%6], apex)); fc.material_index = 1
        # vertex colour by height fraction along this crystal
        inv = M.inverted()
        for v in [x for _, rg in rings for x in rg] + [apex]:
            pass
        for fc in bm.faces:
            for lp in fc.loops:
                h = (inv @ lp.vert.co).z / L
                if -0.01 <= h <= 1.01:
                    lp[col] = srgb2lin(lerp(VIOLET, TEAL, max(0.0, min(1.0, h))))
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    m0 = bpy.data.materials.get("BW_Crown_Crystal") or bpy.data.materials.new("BW_Crown_Crystal")
    m0.use_nodes = True
    nt = m0.node_tree; bsdf = nt.nodes.get("Principled BSDF")
    attr = nt.nodes.new("ShaderNodeVertexColor"); attr.layer_name = "Col"
    nt.links.new(attr.outputs["Color"], bsdf.inputs["Base Color"]); bsdf.inputs["Roughness"].default_value = 0.35
    m1 = bpy.data.materials.get("Glow_Tips") or bpy.data.materials.new("Glow_Tips")
    m1.use_nodes = True
    b1 = m1.node_tree.nodes.get("Principled BSDF")
    c = srgb2lin((0x9F/255, 0xE6/255, 0xF2/255, 1.0))
    b1.inputs["Base Color"].default_value = c
    b1.inputs["Emission Color"].default_value = c
    b1.inputs["Emission Strength"].default_value = 4.0
    ob.data.materials.append(m0); ob.data.materials.append(m1)
    return ob

if __name__ == "__main__":
    o = build_crown(); print("crown tris", len(o.data.polygons))
