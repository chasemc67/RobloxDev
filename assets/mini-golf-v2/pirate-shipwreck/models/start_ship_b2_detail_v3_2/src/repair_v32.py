# v3_2 repair: fix ONLY the 4 coplanar detections of the v3_1 fitcheck, geometry-local on Prop_BowRaise / Prop_CapRails.
# blender -b --factory-startup --python-exit-code 1 source_v3_1.blend --python repair_v32.py -- <out_blend> <repair_log.json>
# source_v3_1.blend is opened read-only and saved AS a new file (never over the source).
#  D1/D2  Prop_BowRaise dark plank line (both sides) rises into the CapRails underside at a shallow angle near x72:
#         trim the plank-line START (aft end) to the first ring that sits >= GAP below the cap underside; close the new end.
#  D3     Prop_CapRails high-side underside crosses the Hull's WoodDk rail top near x51.5 (inside the BowRaise panel):
#         lower the bottom verts of the crossing cap rings to EMB below the hull rail top (cap grows slightly deeper into hull/panel).
#  D4     Prop_CapRails high-side start face at x-118 is flush with Prop_SternCastle tier end face (both inside the step-end post):
#         shorten the cap start by TRIM4 along the tube (start ring lerped toward ring 2); end face stays inside the post box.
import bpy, bmesh, sys, os, json, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shiplib import B, Binv, tilt, untilt
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A = sys.argv[sys.argv.index('--') + 1:]; OUT_BLEND, LOGP = A[0], A[1]
GAP = 0.10; EMB = 0.10; TRIM4 = 0.5
CHECKED = ['Prop_Barnacles', 'Prop_BowRaise', 'Prop_BulwarkGear', 'Prop_Cannons', 'Prop_CapRails', 'Prop_Figurehead', 'Prop_RoofTrim', 'Prop_Seaweed',
           'Prop_SheerWale', 'Prop_SternCastle', 'Prop_SternWheel', 'Prop_Stovepipe', 'Prop_TreasureChest', 'Rigging']   # = v3_1 fitcheck objects_checked
PERMITTED = ['Prop_BowRaise', 'Prop_CapRails', 'Prop_SternCastle']
LOG = dict(source=bpy.data.filepath, blender=bpy.app.version_string, params=dict(plank_gap=GAP, cap_embed=EMB, cap_start_trim=TRIM4), repairs={})

def H(p):  # blender world -> hull frame (Roblox, untilted)
    return untilt(Binv(p))
def W(h):  # hull frame -> blender world
    return Vector(B(tilt(np.asarray(h, float))))
def world_bm(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bm.faces.ensure_lookup_table(); return bm
def coplanar_scan():
    """identical to fitcheck_v31_check.py coplanarity block (same tolerances), over the same 14 objects"""
    trees = {}
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name.startswith('COL'): continue
        bm = world_bm(o); trees[o.name] = (BVHTree.FromBMesh(bm), bm)
    copl = []; checked = 0
    for n in CHECKED:
        bm = world_bm(bpy.data.objects[n])
        for f in bm.faces:
            c = f.calc_center_median(); n0 = f.normal; checked += 1
            for nme, (T, bm2) in trees.items():
                if nme == n: continue
                loc, nor, idx, dist = T.find_nearest(c, 0.03)
                if loc is not None and abs(nor.dot(n0)) > 0.995 and abs((c - loc).dot(nor)) < 0.02:
                    copl.append(dict(obj=n, face=f.index, other=nme, other_face=idx, at=list(np.round(Binv(c), 2)), dist=round(dist, 4)))
        bm.free()
    for T, bm in trees.values(): bm.free()
    return dict(faces_checked=checked, coplanar_pairs=len(copl), pairs=copl)
def tree_of(name):
    bm = world_bm(bpy.data.objects[name]); T = BVHTree.FromBMesh(bm); bm.free(); return T
def island(bm, f0):
    seen = {f0}; st = [f0]
    while st:
        a = st.pop()
        for e in a.edges:
            for g in e.link_faces:
                if g not in seen: seen.add(g); st.append(g)
    return seen
def mesh_sha(me):
    n = len(me.vertices); co = np.zeros(n * 3, np.float32); me.vertices.foreach_get('co', co); return hashlib.sha256(co.tobytes()).hexdigest()
def ncomp(me):
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); left = set(bm.faces); k = 0
    while left: f = next(iter(left)); left -= island(bm, f); k += 1
    bm.free(); return k

before = coplanar_scan(); LOG['detections_before'] = before
print('BEFORE coplanar', before['coplanar_pairs'], [(p['obj'], p['face'], p['other'], p['at']) for p in before['pairs']])
stats0 = {n: dict(verts=len(bpy.data.objects[n].data.vertices), faces=len(bpy.data.objects[n].data.polygons),
                  tris=sum(len(p.vertices) - 2 for p in bpy.data.objects[n].data.polygons), components=ncomp(bpy.data.objects[n].data)) for n in PERMITTED}
for o in (bpy.data.objects[n] for n in PERMITTED): assert o.matrix_world == o.matrix_world.Identity(4), o.name   # local == world
seeds = {(p['obj'], p['other']): p for p in before['pairs']}

# ------------------------------------------------------------ D1/D2: trim BowRaise plank-line start (both sides)
o = bpy.data.objects['Prop_BowRaise']; me = o.data; bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
uvl = bm.loops.layers.uv.active
TC = tree_of('Prop_CapRails'); UPW = Vector(B(tilt(np.array((0.0, 1.0, 0.0)))))
d12 = []
seed_faces = [p['face'] for p in before['pairs'] if p['obj'] == 'Prop_BowRaise' and p['other'] == 'Prop_CapRails']
XS_B = list(np.arange(50.0, 150.0, 3.0)) + list(np.arange(150.0, 158.5, 1.5)) + [158.5]; PL_ST = [float(x) for x in XS_B[2:-3]]   # build_v31 plank stations
assert uvl is not None
seed_refs = [(sf, bm.faces[sf]) for sf in seed_faces]
for sf, sref in seed_refs:
    isl = island(bm, sref); vs = list({v for f in isl for v in f.verts})
    hx = {v: H(v.co) for v in vs}
    stations = PL_ST
    rings = {s: [] for s in stations}
    for v in vs: rings[min(stations, key=lambda s: abs(s - hx[v][0]))].append(v)
    assert all(len(r) == 4 for r in rings.values()), {s: len(r) for s, r in rings.items()}
    per_ring = []
    for s in stations:
        r = rings[s]; top = max(hx[v][1] for v in r); zc = float(np.mean([hx[v][2] for v in r]))
        loc, nor, idx, dist = TC.ray_cast(W((s, top - 1.5, zc)), UPW, 5.0)
        cb = None if loc is None else float(H(loc)[1]); per_ring.append(dict(x=s, plank_top=round(top, 4), cap_bottom=None if cb is None else round(cb, 4), gap=None if cb is None else round(cb - top, 4)))
    k = 0
    while per_ring[k]['gap'] is not None and per_ring[k]['gap'] < GAP: k += 1
    drop = stations[:k]; keep0 = stations[k]
    # old start-cap face (normal along -x in hull frame) : remember material + per-corner UV keyed by ring-relative offset
    old_cap = [f for f in isl if all(v in rings[stations[0]] for v in f.verts)]; assert len(old_cap) == 1; old_cap = old_cap[0]
    c0 = np.mean([hx[v] for v in old_cap.verts], 0); uvmap = [(hx[l.vert] - c0, tuple(l[uvl].uv)) for l in old_cap.loops]; mi = old_cap.material_index; sm = old_cap.smooth
    dverts = [v for s in drop for v in rings[s]]; nfaces_isl = len(isl)
    bmesh.ops.delete(bm, geom=dverts, context='VERTS')
    nr = rings[keep0]; be = [e for v in nr for e in v.link_edges if len(e.link_faces) == 1 and all(w in nr for w in e.verts)]
    order = [nr[0]]
    while len(order) < 4:
        nxt = [w for e in be if order[-1] in e.verts for w in e.verts if w is not order[-1] and w not in order]; order.append(nxt[0])
    nf = bm.faces.new(order); nf.material_index = mi; nf.normal_update()
    nxt_c = W(np.mean([H(v.co) for v in rings[stations[k + 1]]], 0)); cen = nf.calc_center_median()
    if nf.normal.dot(nxt_c - cen) > 0: nf.normal_flip()
    c1 = np.mean([H(v.co) for v in nf.verts], 0)
    for l in nf.loops:
        rel = H(l.vert.co) - c1; best = min(uvmap, key=lambda t: np.linalg.norm(t[0][1:] - rel[1:])); l[uvl].uv = best[1]
    nf.smooth = sm
    d12.append(dict(seed_face=sf, side='high(-Z)' if c0[2] < 0 else 'low(+Z)', island_faces_before=nfaces_isl, rings_before=len(stations),
                    rings_removed=len(drop), removed_ring_x=drop, new_start_x=keep0, old_start_x=stations[0], trimmed_length=round(keep0 - stations[0], 3),
                    verts_removed=len(dverts), faces_removed=len(drop) * 4 + 1, faces_added=1, new_end_face_material=me.materials[mi].name,
                    new_start_gap_below_cap=per_ring[k]['gap'], ring_gaps=per_ring[:k + 2]))
    bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
bm.to_mesh(me); me.update(); bm.free()
LOG['repairs']['D1_D2_Prop_BowRaise_plank_line_trim'] = d12

# ------------------------------------------------------------ D3 + D4 on Prop_CapRails (high side island)
o = bpy.data.objects['Prop_CapRails']; me = o.data; bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
TH = tree_of('Hull'); DN = -UPW
p3 = seeds[('Prop_CapRails', 'Hull')]; p4 = seeds[('Prop_CapRails', 'Prop_SternCastle')]
isl = island(bm, bm.faces[p3['face']]); assert bm.faces[p4['face']] in isl
vs = list({v for f in isl for v in f.verts}); hx = {v: H(v.co) for v in vs}
STN = sorted(set(list(np.arange(-118.0, 150.0, 3.0)) + [150.0, 152.0, 154.0]))
ring = {s: [] for s in STN}
for v in vs: ring[min(STN, key=lambda s: abs(s - hx[v][0]))].append(v)
assert all(len(r) == 4 for r in ring.values()), {s: len(r) for s, r in ring.items() if len(r) != 4}
# D3: crossing rings near the detection
x3 = float(p3['at'][0]); d3 = []
for s in STN:
    if not (x3 - 15 <= s <= x3 + 15): continue
    r = ring[s]; bot = sorted(r, key=lambda v: hx[v][1])[:2]; yb = float(np.mean([hx[v][1] for v in bot])); zc = float(np.mean([hx[v][2] for v in r]))
    loc, nor, idx, dist = TH.ray_cast(W((s, yb + 3.0, zc)), DN, 8.0)
    ht = float(H(loc)[1]); g = yb - ht
    d3.append(dict(x=s, cap_bottom=round(yb, 4), hull_rail_top=round(ht, 4), gap=round(g, 4), hull_face=idx, bot=bot, ht=ht))
# lower rings with -EMB < gap < 2*0.08+EMB (so the transition face to the next untouched ring keeps a >=0.08 mean gap)
moved3 = []
for e in d3:
    if -EMB < e['gap'] < 2 * 0.08 + EMB:
        for v in e['bot']:
            h = H(v.co); dy = (e['ht'] - EMB) - h[1]; h[1] = e['ht'] - EMB; v.co = W(h); moved3.append(dict(x=e['x'], vert=v.index, moved_hull_frame_y=round(float(dy), 4)))
        e['new_gap'] = -EMB
for e in d3: e.pop('bot'); e.pop('ht')
LOG['repairs']['D3_Prop_CapRails_underside_vs_Hull_rail'] = dict(side='high(-Z)', rings_examined=d3, verts_moved=moved3, n_verts_moved=len(moved3),
    max_displacement=round(max(abs(m['moved_hull_frame_y']) for m in moved3), 4) if moved3 else 0.0, faces_added=0, faces_removed=0,
    direction='down along the 15deg-tilted hull-frame vertical (into Hull rail / BowRaise panel); Hull itself untouched')
# D4: shorten cap start along the tube
s0, s1 = STN[0], STN[1]; r0 = ring[s0]; r1 = ring[s1]; t = TRIM4 / (s1 - s0); moved4 = []
for v in r0:
    w = min(r1, key=lambda u: np.linalg.norm(hx[u][1:] - hx[v][1:]))   # matching corner on ring 2
    old = v.co.copy(); v.co = old.lerp(w.co, t); moved4.append(dict(vert=v.index, displacement=round((v.co - old).length, 4)))
LOG['repairs']['D4_Prop_CapRails_start_vs_SternCastle_tier_end'] = dict(side='high(-Z)', old_start_x=s0, new_start_x=round(float(np.mean([H(v.co)[0] for v in r0])), 4),
    trim_along_tube=TRIM4, verts_moved=moved4, faces_added=0, faces_removed=0,
    note='start face moves from the tier end plane x-118 to x-117.5; still enclosed by the SternCastle step-end post box (x-118.6..-117.0)')
bm.to_mesh(me); me.update(); bm.free()

after = coplanar_scan(); LOG['detections_after'] = after
print('AFTER coplanar', after['coplanar_pairs'], [(p['obj'], p['face'], p['other'], p['at']) for p in after['pairs']])
LOG['mesh_stats'] = {n: dict(before=stats0[n], after=dict(verts=len(bpy.data.objects[n].data.vertices), faces=len(bpy.data.objects[n].data.polygons),
                     tris=sum(len(p.vertices) - 2 for p in bpy.data.objects[n].data.polygons), components=ncomp(bpy.data.objects[n].data))) for n in PERMITTED}
LOG['changed_meshes'] = [n for n in PERMITTED if LOG['mesh_stats'][n]['before'] != LOG['mesh_stats'][n]['after'] or n != 'Prop_SternCastle']
LOG['Prop_SternCastle'] = 'not modified (D4 fixed on the CapRails side, which keeps the step post/tier art intact)'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND, compress=False)
json.dump(LOG, open(LOGP, 'w'), indent=1, default=float)
print('REPAIR_OK', OUT_BLEND)
