"""Aurora crown v2 (3D Model Bot, explicit; wire in unchanged except the allowed nudges).
Blender Z-up, arch-local, pivot arch base centre. Tallest tip at Z=27.0 (1.5 x arch top 18). 6 crystals, 3 sizes, 12 sides,
slight taper, beveled vertical facet edges. Vertex colour 'Col' is a BYTE colour layer -> store sRGB values directly
(pass 7 bug: values were linearised before writing to a byte layer, double-darkening them). Violet #7A4FD0 -> teal #8FE3EE.
Glow_Tips = faces in the top 20% of each crystal (material slot 1). Target 1.5-3k tris.
"""
import bpy, bmesh, math
from mathutils import Matrix, Vector

VIOLET = (0x7A/255, 0x4F/255, 0xD0/255, 1.0)
TEAL   = (0x8F/255, 0xE3/255, 0xEE/255, 1.0)
GLOW_SRGB = (0x9F/255, 0xE6/255, 0xF2/255)
SIDES = 12
def lin(c): return tuple((x/12.92) if x <= 0.04045 else ((x+0.055)/1.055)**2.4 for x in c)
def lerp(a, b, t): return tuple(a[i]+(b[i]-a[i])*t for i in range(4))

BASE_Z = 13.0
TALL_L = (27.0 - BASE_Z) / math.cos(math.radians(10.0))   # ~14.2 so the tallest tip lands at Z=27
S = TALL_L / 27.0                                          # same scale for the others (27/18/10 ratios)
# (length, radius, x, z, y(+ = behind), splay deg (+ top -> +X), twist deg)
CRYSTALS = [
    (27*S, 2.4,  3.0, BASE_Z,      0.6,  10.0,  0.0),
    (18*S, 1.9, -3.4, BASE_Z,      0.5, -15.0, 15.0),
    (18*S, 1.8,  6.6, BASE_Z-0.5,  0.4,  20.0, 30.0),
    (10*S, 1.4, -6.9, BASE_Z-0.6,  0.2, -25.0,  8.0),
    (10*S, 1.3, -0.4, BASE_Z+1.6, -0.2, -12.0, 22.0),
    (10*S, 1.4,  5.0, BASE_Z+1.4,  1.1,  25.0, 40.0),
]
RINGS = (0.0, 0.2, 0.4, 0.6, 0.8)      # shaft; tip = 0.8 -> 0.92 (ring) -> 1.0 apex

def build_crown(name="bw_scn_aurora_crown"):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    meta = []
    for (L, r, bx, bz, by, splay, twist) in CRYSTALS:
        M = (Matrix.Translation((bx, by, bz)) @ Matrix.Rotation(math.radians(splay), 4, 'Y')
             @ Matrix.Rotation(math.radians(twist), 4, 'Z'))
        rings = []
        for f in RINGS + (0.92,):
            rr = r*(1.0-0.15*f) if f <= 0.8 else r*0.85*0.45
            rings.append([bm.verts.new(M @ Vector((rr*math.cos(2*math.pi*k/SIDES), rr*math.sin(2*math.pi*k/SIDES), f*L))) for k in range(SIDES)])
        apex = bm.verts.new(M @ Vector((0, 0, L)))
        new_faces = [bm.faces.new(list(reversed(rings[0])))]
        for a, b in zip(rings, rings[1:]):
            for k in range(SIDES):
                new_faces.append(bm.faces.new((a[k], a[(k+1)%SIDES], b[(k+1)%SIDES], b[k])))
        for k in range(SIDES):
            new_faces.append(bm.faces.new((rings[-1][k], rings[-1][(k+1)%SIDES], apex)))
        # facet bevel on vertical shaft edges (every other edge -> faceted gem look)
        edges = set()
        for i in range(len(RINGS)-1):
            for k in range(0, SIDES, 2):
                e = bm.edges.get((rings[i][k], rings[i+1][k]))
                if e: edges.add(e)
        if edges:
            bmesh.ops.bevel(bm, geom=list(edges), offset=r*0.12, segments=1, affect='EDGES', profile=0.5)
        meta.append((M.inverted(), L))
    col = bm.loops.layers.color.new("Col")
    bm.faces.ensure_lookup_table()
    for fc in bm.faces:
        best = None
        for inv, L in meta:      # assign face to the crystal whose local axis contains it
            p = inv @ fc.calc_center_median()
            if -0.05 <= p.z/L <= 1.01 and Vector((p.x, p.y)).length <= 3.0:
                best = (inv, L, p.z/L); break
        inv, L, h = best if best else (meta[0][0], meta[0][1], 0.0)
        fc.material_index = 1 if h >= 0.8 else 0
        for lp in fc.loops:
            t = max(0.0, min(1.0, (inv @ lp.vert.co).z / L))
            lp[col] = lerp(VIOLET, TEAL, t)          # sRGB straight into byte layer
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    m0 = bpy.data.materials.get("BW_Crown_Crystal") or bpy.data.materials.new("BW_Crown_Crystal"); m0.use_nodes = True
    nt = m0.node_tree; b = nt.nodes.get("Principled BSDF")
    vc = nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "Col"
    nt.links.new(vc.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.4
    m1 = bpy.data.materials.get("Glow_Tips") or bpy.data.materials.new("Glow_Tips"); m1.use_nodes = True
    b1 = m1.node_tree.nodes.get("Principled BSDF"); g = lin(GLOW_SRGB) + (1.0,)
    b1.inputs["Base Color"].default_value = g; b1.inputs["Emission Color"].default_value = g
    b1.inputs["Emission Strength"].default_value = 1.5
    ob.data.materials.append(m0); ob.data.materials.append(m1)
    return ob

if __name__ == "__main__":
    o = build_crown(); print("crown tris", len(o.data.polygons))
