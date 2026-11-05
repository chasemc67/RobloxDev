"""Pass 9 explicit geometry (3D Model Bot). Blender Z-up, 1 BU = 1 stud, arch-local, Blender -Y = Roblox +Z (front).
Zones (Blender coords): A = |x|<5, z<12, y in [-4,12]; B = |x|<11, z<18, y < -4. Every builder self-checks and shrinks/clips if needed.
All colour layers are BYTE 'Col' with sRGB values written directly.
"""
import bpy, bmesh, math, random
from mathutils import Matrix, Vector

def hexc(h, a=1.0): return (int(h[1:3],16)/255, int(h[3:5],16)/255, int(h[5:7],16)/255, a)
def lin(c): return tuple((x/12.92) if x <= 0.04045 else ((x+0.055)/1.055)**2.4 for x in c[:3]) + (1.0,)

def in_zone(p):
    if abs(p.x) < 5 and p.z < 12 and -4 <= p.y <= 12: return True
    if abs(p.x) < 11 and p.z < 18 and p.y < -4: return True
    return False

def vc_material(name, emission=0.0, rough=0.6):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes.get("Principled BSDF")
    vc = nt.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "Col"
    nt.links.new(vc.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rough
    if emission > 0:
        nt.links.new(vc.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = emission
    return m

def finish(bm, name, mats, flat=False):
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = not flat
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    for m in mats: me.materials.append(m)
    return ob

def zone_hits(ob): return sum(1 for v in ob.data.vertices if in_zone(ob.matrix_world @ v.co))

# ---------------------------------------------------------------- 1. Sugarloaf joint crystals
PINK, YEL = hexc("#F59AC8"), hexc("#FFF1A8")
def _crystal(bm, col, M, L, r, c):
    r0 = [bm.verts.new(M @ Vector((r*math.cos(k*math.pi/3), r*math.sin(k*math.pi/3), -0.4))) for k in range(6)]
    r1 = [bm.verts.new(M @ Vector((0.9*r*math.cos(k*math.pi/3), 0.9*r*math.sin(k*math.pi/3), 0.7*L))) for k in range(6)]
    ap = bm.verts.new(M @ Vector((0, 0, L)))
    fs = [bm.faces.new(list(reversed(r0)))] + [bm.faces.new((r0[k], r0[(k+1)%6], r1[(k+1)%6], r1[k])) for k in range(6)] \
         + [bm.faces.new((r1[k], r1[(k+1)%6], ap)) for k in range(6)]
    for f in fs:
        for lp in f.loops: lp[col] = c

def _cluster(bm, col, base, axis, n, size, seed, max_tilt=35):
    """n points fanned within 35 deg of axis (unit Vector), from base."""
    rnd = random.Random(seed); axis = axis.normalized()
    q = Vector((0, 0, 1)).rotation_difference(axis)
    for i in range(n):
        L = (rnd.uniform(2.6, 4.6) * (1.3 if i == 0 else 1.0)) * size; r = rnd.uniform(0.5, 0.8) * size
        tilt = 0 if i == 0 else rnd.uniform(min(12, max_tilt*0.5), max_tilt); az = 2*math.pi*i/max(1, n-1) + rnd.uniform(-0.3, 0.3)
        local = Matrix.Rotation(az, 4, 'Z') @ Matrix.Rotation(math.radians(tilt), 4, 'X')
        M = Matrix.Translation(base) @ q.to_matrix().to_4x4() @ local
        _crystal(bm, col, M, L, r, PINK if i % 2 == 0 else YEL)

def build_sugarloaf_crystals(side):   # side = -1 west, +1 east
    s = side; name = f"bw_scn_sugarloaf_crystals_{'w' if s < 0 else 'e'}"
    for size in (2.0, 1.8, 1.6, 1.4, 1.2, 1.0):
        bm = bmesh.new(); col = bm.loops.layers.color.new("Col")
        # joint clusters: inner/front face of tower where it meets the arch leg, pointing outward + forward, not up
        _cluster(bm, col, Vector((s*8.8, -0.6, 7.0)), Vector((s*0.85, -0.1, 0.45)), 7, size, 11 if s < 0 else 12)
        _cluster(bm, col, Vector((s*8.2, -0.6, 10.5)), Vector((s*0.85, -0.1, 0.5)), 5, size*0.7, 21 if s < 0 else 22)
        # base clusters
        _cluster(bm, col, Vector((s*10.6, -0.4, 0.3)), Vector((s*0.25, 0.0, 0.95)), 6, size*0.55, 31 if s < 0 else 32, max_tilt=18)
        _cluster(bm, col, Vector((s*9.3, -1.4, 0.3)), Vector((s*0.2, 0.0, 0.95)), 5, size*0.4, 41 if s < 0 else 42, max_tilt=16)
        ob = finish(bm, name, [vc_material("Glow_Crystal", emission=0.2, rough=0.3)], flat=True)
        if zone_hits(ob) == 0: ob["size"] = size; return ob
        print("hits", size, [tuple(round(c,1) for c in (ob.matrix_world @ v.co)) for v in ob.data.vertices if in_zone(v.co)][:4])
        bpy.data.objects.remove(ob)
    raise RuntimeError("sugarloaf crystals cannot clear zones")

# ---------------------------------------------------------------- 2. Aurora crown v3 (flat-shaded faceted gems)
VIOLET, TEAL, GLOW = hexc("#7A4FD0"), hexc("#8FE3EE"), hexc("#9FE6F2")
BASE_Z = 13.0
TALL_L = (27.0 - BASE_Z) / math.cos(math.radians(10.0)); S = TALL_L / 27.0
CRYSTALS = [(27*S, 2.4, 3.0, BASE_Z, 0.6, 10.0, 0.0), (18*S, 1.9, -3.4, BASE_Z, 0.5, -15.0, 15.0),
            (18*S, 1.8, 6.6, BASE_Z-0.5, 0.4, 20.0, 30.0), (10*S, 1.4, -6.9, BASE_Z-0.6, 0.2, -25.0, 8.0),
            (10*S, 1.3, -0.4, BASE_Z+1.6, -0.2, -12.0, 22.0), (10*S, 1.4, 5.0, BASE_Z+1.4, 1.1, 25.0, 40.0)]
def build_crown(name="bw_scn_aurora_crown", sides=12):
    bm = bmesh.new(); col = bm.loops.layers.color.new("Col"); meta = []
    for (L, r, bx, bz, by, splay, tw) in CRYSTALS:
        M = Matrix.Translation((bx, by, bz)) @ Matrix.Rotation(math.radians(splay), 4, 'Y') @ Matrix.Rotation(math.radians(tw), 4, 'Z')
        prof = [(0.0, 1.0), (0.35, 0.93), (0.8, 0.82), (0.86, 0.6), (1.0, 0.0)]   # taper, shoulder bevel, point
        rings = []
        for f, k in prof[:-1]:
            rings.append([bm.verts.new(M @ Vector((r*k*math.cos(2*math.pi*j/sides + (0.15 if f > 0.5 else 0)),
                                                       r*k*math.sin(2*math.pi*j/sides + (0.15 if f > 0.5 else 0)), f*L))) for j in range(sides)])
        ap = bm.verts.new(M @ Vector((0, 0, L)))
        bm.faces.new(list(reversed(rings[0])))
        for a, b in zip(rings, rings[1:]):
            for j in range(sides): bm.faces.new((a[j], a[(j+1)%sides], b[(j+1)%sides], b[j]))
        for j in range(sides): bm.faces.new((rings[-1][j], rings[-1][(j+1)%sides], ap))
        meta.append((M.inverted(), L))
    bm.faces.ensure_lookup_table()
    # facet bevel on every vertical edge of the lower shaft
    ed = [e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).normalized().z) > 0.9]
    bmesh.ops.bevel(bm, geom=ed, offset=0.16, segments=2, affect='EDGES', profile=0.5)
    for fc in bm.faces:
        c = fc.calc_center_median(); h = 0.0; inv = meta[0][0]; L = meta[0][1]
        for i, (iv, LL) in enumerate(meta):
            p = iv @ c
            if -0.05 <= p.z/LL <= 1.01 and Vector((p.x, p.y)).length <= 3.0: inv, L, h = iv, LL, p.z/LL; break
        fc.material_index = 1 if h >= 0.8 else 0
        for lp in fc.loops:
            t = max(0.0, min(1.0, (inv @ lp.vert.co).z / L))
            lp[col] = tuple(VIOLET[i] + (TEAL[i]-VIOLET[i])*t for i in range(4))
    m0 = vc_material("BW_Crown_Crystal", rough=0.35)
    m1 = bpy.data.materials.get("Glow_Tips") or bpy.data.materials.new("Glow_Tips"); m1.use_nodes = True
    b1 = m1.node_tree.nodes.get("Principled BSDF"); g = lin(GLOW)
    b1.inputs["Base Color"].default_value = g; b1.inputs["Emission Color"].default_value = g; b1.inputs["Emission Strength"].default_value = 1.5
    return finish(bm, name, [m0, m1], flat=True)

# ---------------------------------------------------------------- 3. Lantern Grove twisted trunk (trunk part only; canopy stays)
BARK, BARK_D = hexc("#6B4429"), hexc("#4A2F1A")
def build_twisted_trunk(side, name=None, strands=3, segs=26, ring=8, height=21.0, twist_deg=250.0):
    s = side; name = name or f"lg_trunk_core_{'w' if s < 0 else 'e'}"
    bm = bmesh.new(); col = bm.loops.layers.color.new("Col")
    def axis(t):   # trunk centreline: stands at x=±8.4 hugging the leg, curls inward above the lintel
        x = s*(8.4 - 3.6*max(0.0, (t-0.62)/0.38)**1.5); z = t*height; return Vector((x, 0.0, z))
    for k in range(strands):
        prev = None; phase = 2*math.pi*k/strands
        for i in range(segs+1):
            t = i/segs; c = axis(t)
            a = phase + math.radians(twist_deg)*t
            orbit = 1.15*(1-t) + 0.45*t
            cen = c + Vector((orbit*math.cos(a), orbit*math.sin(a), 0))
            rad = 1.35*(1-t) + 0.55*t + (0.5 if t < 0.08 else 0)*(1-t/0.08)
            cur = [bm.verts.new(cen + Vector((rad*math.cos(2*math.pi*j/ring), rad*math.sin(2*math.pi*j/ring), 0))) for j in range(ring)]
            if prev:
                for j in range(ring):
                    f = bm.faces.new((prev[j], prev[(j+1)%ring], cur[(j+1)%ring], cur[j]))
                    for lp in f.loops: lp[col] = BARK if (j + i//3) % 3 else BARK_D
            prev = cur
        top = bm.faces.new(list(prev))
        for lp in top.loops: lp[col] = BARK_D
    # 5 root flares
    for k in range(5):
        a = 2*math.pi*k/5 + 0.4; d = Vector((math.cos(a), math.sin(a), 0))
        b0 = axis(0) + d*0.6; tip = axis(0) + d*3.2 + Vector((0, 0, 0.15)); up = axis(0) + d*0.4 + Vector((0, 0, 2.2))
        w = Vector((-d.y, d.x, 0))*0.8
        vs = [bm.verts.new(p) for p in (b0 + w, b0 - w, tip, up)]
        for tri in ((0, 1, 3), (1, 2, 3), (2, 0, 3), (0, 2, 1)):
            f = bm.faces.new([vs[i] for i in tri])
            for lp in f.loops: lp[col] = BARK_D
    ob = finish(bm, name, [vc_material("BW_Bark_VC", rough=0.8)])
    hits = [ob.matrix_world @ v.co for v in ob.data.vertices if in_zone(ob.matrix_world @ v.co)]
    if hits: raise RuntimeError(f"trunk {name} zone hits {len(hits)} e.g. {hits[0]}")
    return ob

# ---------------------------------------------------------------- 4. Aurora snowy rock piles
ROCK, ROCK_L, SNOW = hexc("#3A3550"), hexc("#4B4566"), hexc("#EEF3F7")
def build_aurora_rocks(side):
    s = side; name = f"bw_scn_aurora_rocks_{'w' if s < 0 else 'e'}"; rnd = random.Random(7 if s < 0 else 8)
    # (x, y, z, scale): hugging the outside/back of the leg; snowpuff spot west front (x -7.3..-5.7, y -2..-0.55) stays clear
    spots = [(10.3, -0.4, 0.0, 2.3), (10.6, 1.4, 0.0, 2.1), (8.6, 2.4, 0.0, 1.9), (11.9, -1.2, 0.0, 1.5),
             (10.2, -2.4, 0.0, 1.3), (9.4, 1.0, 2.2, 1.8), (10.9, 0.0, 3.4, 1.4), (9.0, 2.6, 2.6, 1.3),
             (10.0, 0.6, 5.0, 1.0), (12.2, 1.6, 0.0, 1.2)]
    bm = bmesh.new(); col = bm.loops.layers.color.new("Col")
    for (x, y, z, sc) in spots:
        res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
        vs = res["verts"]
        for v in vs:
            v.co = Vector((v.co.x*sc*rnd.uniform(0.85, 1.15), v.co.y*sc*rnd.uniform(0.85, 1.15), v.co.z*sc*0.95*rnd.uniform(0.9, 1.15)))
            v.co += Vector((s*x, y, z + sc*0.6))
            v.co.z = max(v.co.z, 0.0)
    bm.normal_update()
    for f in bm.faces:
        c = SNOW if f.normal.z > 0.55 else (ROCK_L if f.normal.z > 0.1 else ROCK)
        for lp in f.loops: lp[col] = c
    ob = finish(bm, name, [vc_material("BW_Rock_VC", rough=0.9)], flat=True)
    hits = zone_hits(ob)
    if s < 0:   # snowpuff footprint
        hits += sum(1 for v in ob.data.vertices if -7.6 <= v.co.x <= -5.4 and -2.3 <= v.co.y <= -0.3 and v.co.z < 3.2)
    if hits: raise RuntimeError(f"{name} clearance hits {hits}")
    return ob

if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for f in (lambda: build_sugarloaf_crystals(-1), lambda: build_sugarloaf_crystals(1), build_crown,
              lambda: build_twisted_trunk(-1), lambda: build_twisted_trunk(1), lambda: build_aurora_rocks(-1), lambda: build_aurora_rocks(1)):
        o = f(); print("OK", o.name, len(o.data.polygons), "tris", "size=" + str(o.get("size", "")))
