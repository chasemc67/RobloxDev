# Route QA for Prop_SternWheel / Prop_TreasureChest vs the continuous cabin->door->deck->gangplank route.
# READ-ONLY: opens source_v3_2.blend, never saves/exports. Writes out/route_qa_raw.json + out/route_geom.json.
# blender -b --factory-startup source_v3_2.blend --python-exit-code 1 --python out/scripts/route_qa.py -- <out_dir>
# Coordinates reported in ROBLOX model-local (x, y up, z); Blender = B(x,y,z) = (x,-z,y) (shiplib convention).
import bpy, bmesh, sys, os, json, math
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

A = sys.argv[sys.argv.index('--') + 1:]; OUT = A[0]
def B(p): return Vector((float(p[0]), float(-p[2]), float(p[1])))
def Binv(p): return np.array((p[0], p[2], -p[1]), float)
DG = bpy.context.evaluated_depsgraph_get()
PROPS = ['Prop_SternWheel', 'Prop_TreasureChest']
YAW = math.radians(-30.0)          # RampFlight2 + its colliders yawed about the RampFlight2 origin in Studio (manifest placement_note, fitcheck f2_dist)
PLAYER_R = 2.0                     # chosen capsule radius (studs)

def roblox_tris(o):
    ev = o.evaluated_get(DG); me = ev.to_mesh(); me.calc_loop_triangles(); mw = o.matrix_world
    V = np.array([Binv(mw @ v.co) for v in me.vertices]); T = np.array([t.vertices[:] for t in me.loop_triangles], int)
    ev.to_mesh_clear(); return V, T

F2O = Binv(bpy.data.objects['RampFlight2'].matrix_world.translation)
def yaw_xz(P, about=F2O, th=YAW):
    P = np.array(P, float).copy(); q = P[..., [0, 2]] - about[[0, 2]]; c, s = math.cos(th), math.sin(th)
    P[..., 0] = about[0] + q[..., 0] * c + q[..., 1] * s; P[..., 2] = about[2] - q[..., 0] * s + q[..., 1] * c; return P
def is_f2(n): return n == 'RampFlight2' or n.startswith('COL_Flight2')

# ------------------------------------------------------------------ trees (Blender space), studio (yawed) and as-exported (unyawed)
def tree_of(name, yawed):
    V, T = roblox_tris(bpy.data.objects[name])
    if yawed and is_f2(name): V = yaw_xz(V)
    return BVHTree.FromPolygons([B(v) for v in V], [tuple(t) for t in T]), V, T
meshes = [o.name for o in bpy.data.objects if o.type == 'MESH']
COLN = sorted(n for n in meshes if n.startswith('COL'))
VISN = sorted(n for n in meshes if not n.startswith('COL'))
TREES = {y: {n: tree_of(n, y) for n in meshes} for y in (True, False)}

def first_hit(origin, d, L, names, yawed):
    best = None
    for n in names:
        loc, nor, idx, dist = TREES[yawed][n][0].ray_cast(B(origin), B(d), L)
        if loc is not None and (best is None or dist < best[1]): best = (n, dist)
    return best

# ------------------------------------------------------------------ anchors & walk-surface boxes from the source
E = {n: Binv(bpy.data.objects[n].matrix_world.translation) for n in ('Spawn', 'Tee1', 'RampStart', 'CupRef')}
def bbox(name, yawed=False):
    V = TREES[yawed][name][1]; return V.min(0), V.max(0)
def hull2(P):
    P = sorted(set(map(tuple, np.round(P, 6))))
    if len(P) < 3: return np.array(P)
    def cr(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return np.array(lo[:-1] + up[:-1])
def foot(name, yawed=True):
    V = TREES[yawed][name][1]; return hull2(V[:, [0, 2]])

f1lo, f1hi = bbox('COL_Flight1_Surface'); f2lo_u, f2hi_u = bbox('COL_Flight2_Surface', False); aplo_u, aphi_u = bbox('COL_Flight2_Apron', False)
la = [bbox('COL_Landing_FloorA'), bbox('COL_Landing_FloorB')]
lmin = np.min([l[0] for l in la], 0); lmax = np.max([l[1] for l in la], 0)
DOOR = np.array((-120.0, 24.0, 24.0))   # brief door anchor (= shiplib DOORX, cabin front wall z1=24)
F1_END = np.array((E['RampStart'][0], 0.0, float(f1hi[2])))                    # Flight1 bottom edge on its centreline x
LAND_C = np.array((E['RampStart'][0], 0.0, float((lmin[2] + lmax[2]) / 2)))   # landing centre on the Flight1 axis
F2_MOUTH = np.array((F2O[0], 0.0, F2O[2]))                                    # RampFlight2 origin = top edge centre (yaw pivot)
F2_LEN = float(f2hi_u[2] - F2O[2])                                            # along-length of the Flight2 surface collider (unyawed +Z)
_rw = TREES[False]['COL_Landing_RailW'][1]; _rs = TREES[False]['COL_Landing_RailS'][1]
RW_CORNER = np.array((_rw[:, 0].max(), _rw[:, 2].max())); RS_CORNER = np.array((_rs[:, 0].min(), _rs[:, 2].min()))
_le = (RW_CORNER + RS_CORNER) / 2; LAND_EXIT = np.array((_le[0], 0.0, _le[1]))   # mid of the landing's south exit (RailW end <-> RailS start)
AP_C_u = np.array(((aplo_u[0] + aphi_u[0]) / 2, 0.0, (aplo_u[2] + aphi_u[2]) / 2))
def route_pts(yawed):
    d2 = np.array((math.sin(YAW), 0, math.cos(YAW))) if yawed else np.array((0, 0, 1.0))
    F2_END = F2_MOUTH + F2_LEN * d2
    AP = yaw_xz(AP_C_u) if yawed else AP_C_u
    F2_IN = F2_MOUTH + 6.0 * d2     # first Flight2 station with full 12-stud rail-to-rail clearance (measured), on the Flight2 axis
    P = [('Spawn', E['Spawn']), ('Door', DOOR), ('Tee1', E['Tee1']), ('RampStart', E['RampStart']), ('Flight1_bottom', F1_END),
         ('Landing_centre', LAND_C), ('Landing_exit', LAND_EXIT), ('Flight2_axis6', F2_IN), ('Flight2_bottom', F2_END), ('Apron_centre', AP)]
    return [(n, np.array((p[0], p[2]))) for n, p in P]
# segment -> (route half-width main, conservative half-width, section)
SEGS = [('Spawn->Door', 4.0, 6.0, 'cabin'), ('Door->Tee1', 4.0, 6.0, 'deck'), ('Tee1->RampStart', 4.0, 6.0, 'deck'),
        ('RampStart->Flight1_bottom', 6.0, 6.0, 'flight1'), ('Flight1_bottom->Landing_centre', 6.0, 6.0, 'landing'),
        ('Landing_centre->Landing_exit', 6.0, 6.0, 'landing_turn'), ('Landing_exit->Flight2_axis6', 6.0, 6.0, 'landing_turn'),
        ('Flight2_axis6->Flight2_bottom', 6.0, 6.0, 'flight2'),
        ('Flight2_bottom->Apron_centre', 6.0, 6.0, 'apron')]
AREA_NAMES = ['COL_Landing_FloorA', 'COL_Landing_FloorB', 'COL_Flight2_Surface', 'COL_Flight2_Apron']   # full walkable landing transition + Flight2 + apron
AREA_CONS_EXTRA = ['COL_Outrigger', 'COL_Flight1_Surface']   # conservative variant also takes the whole outrigger platform + Flight1 surface

# ------------------------------------------------------------------ 2D exact geometry (vectorised)
def pt_seg(P, a, b):
    ab = b - a; L2 = (ab * ab).sum(-1); t = np.clip(((P - a) * ab).sum(-1) / np.where(L2 > 0, L2, 1), 0, 1)
    C = a + t[..., None] * ab; return np.linalg.norm(P - C, axis=-1), C
def orient(a, b, c): return (b[..., 0] - a[..., 0]) * (c[..., 1] - a[..., 1]) - (b[..., 1] - a[..., 1]) * (c[..., 0] - a[..., 0])
def seg_seg(A0, A1, C0, C1):
    """A0,A1:(N,2) edges, C0,C1:(M,2) -> (N,M) distance + closest points"""
    A0 = A0[:, None]; A1 = A1[:, None]; C0 = C0[None]; C1 = C1[None]
    o1 = orient(A0, A1, C0); o2 = orient(A0, A1, C1); o3 = orient(C0, C1, A0); o4 = orient(C0, C1, A1)
    X = (o1 * o2 <= 0) & (o3 * o4 <= 0) & ~((o1 == 0) & (o2 == 0) & (o3 == 0) & (o4 == 0))
    A0b, A1b, C0b, C1b = np.broadcast_arrays(A0, A1, C0, C1)
    cands = [(pt_seg(A0b, C0b, C1b), 'a0'), (pt_seg(A1b, C0b, C1b), 'a1'), (pt_seg(C0b, A0b, A1b), 'c0'), (pt_seg(C1b, A0b, A1b), 'c1')]
    D = np.stack([c[0][0] for c in cands]); k = D.argmin(0); d = np.take_along_axis(D, k[None], 0)[0]
    d = np.where(X, 0.0, d)
    def closest(i, j):
        kk = k[i, j]; (dd, Cp), w = cands[kk]
        own = {'a0': A0b, 'a1': A1b, 'c0': C0b, 'c1': C1b}[w][i, j]; other = Cp[i, j]
        return (own, other) if w in ('a0', 'a1') else (other, own)   # (point on A-edge, point on C-edge)
    return d, X, closest
def in_tris(P, T3):
    """P:(M,2) points, T3:(N,3,2) -> (N,M) inside-or-on"""
    a, b, c = T3[:, 0][:, None], T3[:, 1][:, None], T3[:, 2][:, None]; p = P[None]
    d1, d2, d3 = orient(a, b, p), orient(b, c, p), orient(c, a, p)
    return ~(((d1 < 0) | (d2 < 0) | (d3 < 0)) & ((d1 > 0) | (d2 > 0) | (d3 > 0)))
def in_poly(P, poly):   # convex CCW polygon
    ins = np.ones(len(P), bool)
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]; ins &= orient(a[None], b[None], P) >= -1e-9
    return ins
def tri_edges(T3): return np.concatenate([T3[:, 0], T3[:, 1], T3[:, 2]]), np.concatenate([T3[:, 1], T3[:, 2], T3[:, 0]])

def dist_tris_to_segment(T3, a, b):
    """exact min distance between union of 2D triangles and segment ab; 0 if overlapping"""
    E0, E1 = tri_edges(T3); d, X, cl = seg_seg(E0, E1, a[None], b[None])
    inside = in_tris(np.array([a, b]), T3).any(0)
    if inside.any():
        p = a if inside[0] else b; return 0.0, p, p, True
    i = int(d[:, 0].argmin()); pa, pc = cl(i, 0); return float(d[i, 0]), pa, pc, bool(X.any())
def dist_tris_to_poly(T3, poly):
    E0, E1 = tri_edges(T3); P0 = poly; P1 = np.roll(poly, -1, 0); d, X, cl = seg_seg(E0, E1, P0, P1)
    if X.any() or in_tris(poly, T3).any() or in_poly(T3.reshape(-1, 2), poly).any(): return 0.0, None, None, True
    i, j = np.unravel_index(d.argmin(), d.shape); pa, pc = cl(i, j); return float(d[i, j]), pa, pc, False
def poly_poly(p, q):
    d, X, cl = seg_seg(p, np.roll(p, -1, 0), q, np.roll(q, -1, 0))
    if X.any() or in_poly(p, q).any() or in_poly(q, p).any(): return 0.0
    return float(d.min())

# ------------------------------------------------------------------ props
R = dict(blend=bpy.data.filepath, blender=bpy.app.version_string, player_capsule_radius=PLAYER_R, yaw_deg_flight2=-30.0,
         anchors={k: v.round(4).tolist() for k, v in E.items()}, door_anchor=DOOR.tolist(), flight2_origin=F2O.round(4).tolist(), flight2_len=F2_LEN)
G = dict(props={}, col_feet={}, route={}, areas={})
PT = {}
for pn in PROPS:
    V, T = TREES[False][pn][1], TREES[False][pn][2]; T3full = V[T]
    o = bpy.data.objects[pn]
    PT[pn] = dict(V=V, T=T)
    R.setdefault('props', {})[pn] = dict(tris=len(T), verts=len(V), bbox_min=V.min(0).round(4).tolist(), bbox_max=V.max(0).round(4).tolist(),
        origin=Binv(o.matrix_world.translation).round(4).tolist(), collections=[c.name for c in o.users_collection], parent=o.parent.name if o.parent else None,
        children=[c.name for c in o.children], modifiers=[m.type for m in o.modifiers], custom_props={k: str(o[k]) for k in o.keys()},
        footprint_hull_area=None)
    G['props'][pn] = T3full[:, :, [0, 2]].round(4).tolist()

def corridor_eval(yawed, which):
    """which: 'main' (8 on cabin/deck, 12 flights) or 'conservative' (12 everywhere)"""
    pts = dict(route_pts(yawed)); names = [n for n, _ in route_pts(yawed)]
    out = {}
    for pn in PROPS:
        V, T = PT[pn]['V'], PT[pn]['T']
        sets = {'full_projection': V[T]}
        ylo, yhi = 24.0 - 0.5, 24.0 + 6.0    # player-relevant band on the cabin/deck section (walk 24 + capsule ~5)
        keep = (V[T][:, :, 1].max(1) >= ylo) & (V[T][:, :, 1].min(1) <= yhi); sets['clip_y_23.5_30'] = V[T][keep]
        res = {}
        for sk, T3 in sets.items():
            T2 = T3[:, :, [0, 2]]; segres = []
            for (sn, rm, rc, sec) in SEGS:
                a, b = sn.split('->'); pa, pb = pts[a], pts[b]; r = rm if which == 'main' else rc
                d, cp_prop, cp_route, ov = dist_tris_to_segment(T2, pa, pb)
                segres.append(dict(segment=sn, section=sec, half_width=r, centreline_dist=round(d, 4), clearance=round(d - r, 4), intersects_corridor=d - r <= 0,
                                   closest_prop_xz=np.round(cp_prop, 4).tolist(), closest_centreline_xz=np.round(cp_route, 4).tolist()))
            for an in AREA_NAMES + (AREA_CONS_EXTRA if which != 'main' else []):
                d, cp_prop, cp_area, ov = dist_tris_to_poly(T2, foot(an, yawed))
                segres.append(dict(segment='AREA:' + an, section='full_walkable_area', half_width=0.0, centreline_dist=round(d, 4),
                                   clearance=round(d, 4), intersects_corridor=d <= 0, closest_prop_xz=None if cp_prop is None else np.round(cp_prop, 4).tolist(),
                                   closest_centreline_xz=None if cp_area is None else np.round(cp_area, 4).tolist()))
            m = min(segres, key=lambda s: s['clearance'])
            # source 3D coordinate of the closest prop triangle edge point (nearest prop vertex to the 2D closest point, for reference)
            cp = np.array(m['closest_prop_xz']); vi = np.linalg.norm(V[:, [0, 2]] - cp, axis=1).argmin()
            res[sk] = dict(tris=len(T3), min_clearance=m['clearance'], closest_segment=m['segment'], centreline_dist=m['centreline_dist'], half_width=m['half_width'],
                           closest_prop_xz=m['closest_prop_xz'], closest_route_xz=m['closest_centreline_xz'], nearest_prop_vertex_roblox=V[vi].round(4).tolist(),
                           nearest_prop_vertex_blender=list(np.round(B(V[vi]), 4)), per_segment=segres)
        # bbox-based reference
        bl, bh = V.min(0)[[0, 2]], V.max(0)[[0, 2]]; box = np.array([[bl[0], bl[1]], [bh[0], bl[1]], [bh[0], bh[1]], [bl[0], bh[1]]])
        bt = np.array([[box[0], box[1], box[2]], [box[0], box[2], box[3]]]); bres = []
        for (sn, rm, rc, sec) in SEGS:
            a, b = sn.split('->'); r = rm if which == 'main' else rc; d = dist_tris_to_segment(bt, pts[a], pts[b])[0]; bres.append((d - r, sn, d))
        bm_ = min(bres); res['bbox_reference'] = dict(min_clearance=round(bm_[0], 4), segment=bm_[1], centreline_dist=round(bm_[2], 4))
        out[pn] = res
    return out

R['route'] = {}
for yawed in (True, False):
    key = 'studio_yawed' if yawed else 'as_exported_unyawed'
    pts = route_pts(yawed)
    R['route'][key] = dict(centreline=[dict(name=n, xz=p.round(4).tolist()) for n, p in pts],
                           segments=[dict(segment=s[0], half_width_main=s[1], half_width_conservative=s[2], section=s[3]) for s in SEGS],
                           corridor_main=corridor_eval(yawed, 'main'), corridor_conservative12=corridor_eval(yawed, 'conservative'))
    G['route'][key] = [dict(name=n, xz=p.tolist()) for n, p in pts]
    G['areas'][key] = {an: foot(an, yawed).tolist() for an in AREA_NAMES}
    # joint union test: shared endpoints identical + disc of min(adjacent r) at each joint inside both capsules
    J = []
    P = dict(pts)
    for i in range(len(SEGS) - 1):
        s0, s1 = SEGS[i], SEGS[i + 1]; a0, b0 = [P[x] for x in s0[0].split('->')]; a1, b1 = [P[x] for x in s1[0].split('->')]
        rmin = min(s0[1], s1[1]); ang = np.linspace(0, 2 * np.pi, 72, endpoint=False)
        disc = b0 + rmin * 0.999 * np.c_[np.cos(ang), np.sin(ang)]
        in0 = (pt_seg(disc, a0, b0)[0] <= s0[1]).all(); in1 = (pt_seg(disc, a1, b1)[0] <= s1[1]).all()
        turn = math.degrees(math.atan2(np.cross(b0 - a0, b1 - a1), np.dot(b0 - a0, b1 - a1))) if np.linalg.norm(b1 - a1) > 0 else 0.0
        J.append(dict(joint=s0[0].split('->')[1], endpoint_gap=float(np.linalg.norm(b0 - a1)), disc_r=rmin, disc_in_prev=bool(in0), disc_in_next=bool(in1), turn_deg=round(turn, 2)))
    # landing turn lies on the landing walk area?
    lp = [foot(an, yawed) for an in AREA_NAMES[:2]]
    seg_on = []
    for nm in ('Flight1_bottom', 'Landing_centre', 'Landing_exit'):
        def pdist(q, p): return 0.0 if in_poly(q[None], p)[0] else float(min(pt_seg(q[None], p[i], p[(i + 1) % len(p)])[0][0] for i in range(len(p))))
        seg_on.append(dict(point=nm, on_landing_floor=bool(any(in_poly(P[nm][None], p)[0] for p in lp)), dist_to_landing_floor=round(min(pdist(P[nm], p) for p in lp), 4)))
    R['route'][key]['joints'] = J; R['route'][key]['landing_points'] = seg_on

# ------------------------------------------------------------------ walk-surface continuity + lateral clear width along the centreline
WALKCOL = [n for n in COLN if any(k in n for k in ('Deck', 'CabinFloor', 'Outrigger', 'Flight1_Surface', 'Landing_Floor', 'Flight2_Surface', 'Flight2_Apron'))]
def section_of(si): return SEGS[si][3]
def measure(yawed, step=0.5):
    pts = route_pts(yawed); P = dict(pts); rows = []; yprev = 24.0
    for si, (sn, rm, rc, sec) in enumerate(SEGS):
        a, b = [P[x] for x in sn.split('->')]; L = float(np.linalg.norm(b - a)); t = (b - a) / L; n = np.array((t[1], -t[0]))
        for s in np.arange(0.0, L + 1e-9, step):
            q = a + s * t; top = yprev + 6.0
            h = first_hit((q[0], top, q[1]), (0, -1, 0), 30.0, WALKCOL, yawed)
            hv = first_hit((q[0], top, q[1]), (0, -1, 0), 30.0, ['DeckCabin', 'RampFlight1', 'RampLanding', 'RampFlight2', 'Hull', 'Dressing'], yawed)
            wy = None if h is None else top - h[1]
            if wy is not None: yprev = wy
            row = dict(seg=si, s=round(float(s), 3), xz=q.round(3).tolist(), walk_col=None if h is None else [h[0], round(wy, 4)],
                       walk_vis=None if hv is None else [hv[0], round(top - hv[1], 4)])
            base = yprev
            for setn, names in (('col', COLN), ('vis', VISN)):
                wmin = None
                for dh in (0.5, 2.5, 4.5):
                    side = []
                    for sg in (1, -1):
                        d3 = (sg * n[0], 0, sg * n[1]); hh = first_hit((q[0], base + dh, q[1]), d3, 40.0, names, yawed)
                        side.append((40.0, None) if hh is None else (hh[1], hh[0]))
                    w = side[0][0] + side[1][0]; row.setdefault('w_by_h_' + setn, {})[str(dh)] = [round(w, 3), side[0][1], side[1][1]]
                    if wmin is None or w < wmin[0]: wmin = (w, dh, side[0], side[1])
                row['width_' + setn] = dict(width=round(wmin[0], 4), at_dh=wmin[1], left=[round(wmin[2][0], 3), wmin[2][1]], right=[round(wmin[3][0], 3), wmin[3][1]])
            rows.append(row)
    return rows
MEAS = {}
for yawed in (True, False):
    key = 'studio_yawed' if yawed else 'as_exported_unyawed'
    rows = measure(yawed); MEAS[key] = rows
    summ = {}
    for si, (sn, rm, rc, sec) in enumerate(SEGS):
        rr = [r for r in rows if r['seg'] == si]
        nohit = [r['xz'] for r in rr if r['walk_col'] is None]
        ys = [r['walk_col'][1] for r in rr if r['walk_col']]
        steps = [abs(ys[i + 1] - ys[i]) for i in range(len(ys) - 1)]
        wc = min(rr, key=lambda r: r['width_col']['width']); wv = min(rr, key=lambda r: r['width_vis']['width'])
        summ[sn] = dict(section=sec, samples=len(rr), samples_without_walk_collider=len(nohit), no_hit_xz=nohit[:10],
                        walk_y_range=[round(min(ys), 3), round(max(ys), 3)] if ys else None, max_step_between_0p5_samples=round(max(steps), 4) if steps else None,
                        walk_objects=sorted(set(r['walk_col'][0] for r in rr if r['walk_col'])),
                        min_clear_width_colliders=dict(width=wc['width_col']['width'], at_xz=wc['xz'], s=wc['s'], **{k: wc['width_col'][k] for k in ('at_dh', 'left', 'right')}),
                        min_clear_width_visual=dict(width=wv['width_vis']['width'], at_xz=wv['xz'], s=wv['s'], **{k: wv['width_vis'][k] for k in ('at_dh', 'left', 'right')}))
    R['route'][key]['walk_and_width'] = summ
# door opening (8-stud) measured directly: rays +-X at the door plane, z 22..24 (wall thickness 2), heights 0.5..9.5 above deck
door = []
for z in np.arange(22.0, 24.01, 0.5):
    for dh in (0.5, 2.5, 4.5, 6.5, 8.5):
        row = {}
        for setn, names in (('col', COLN), ('vis', ['DeckCabin'])):
            l = first_hit((-120.0, 24.0 + dh, z), (-1, 0, 0), 30, names, True); r_ = first_hit((-120.0, 24.0 + dh, z), (1, 0, 0), 30, names, True)
            row[setn] = [None if l is None else [l[0], round(l[1], 4)], None if r_ is None else [r_[0], round(r_[1], 4)]]
        door.append(dict(z=float(z), dh=dh, **row))
R['door_opening'] = door
def wmin_door(k):
    ws = [(d[k][0][1] + d[k][1][1]) for d in door if d[k][0] and d[k][1]]; return round(min(ws), 4) if ws else None
R['door_opening_min_width'] = dict(colliders=wmin_door('col'), deckcabin_visual=wmin_door('vis'))

# ------------------------------------------------------------------ walk-surface joints between consecutive walk colliders (footprint gaps)
pairs = [('COL_CabinFloor', 'COL_Deck_'), ('COL_Outrigger', 'COL_Deck_'), ('COL_Outrigger', 'COL_Flight1_Surface'), ('COL_Flight1_Surface', 'COL_Landing_FloorA'),
         ('COL_Flight1_Surface', 'COL_Landing_FloorB'), ('COL_Landing_FloorA', 'COL_Landing_FloorB'), ('COL_Landing_FloorA', 'COL_Flight2_Surface'),
         ('COL_Landing_FloorB', 'COL_Flight2_Surface'), ('COL_Flight2_Surface', 'COL_Flight2_Apron')]
WJ = {}
for yawed in (True, False):
    key = 'studio_yawed' if yawed else 'as_exported_unyawed'; L = []
    for a, b in pairs:
        an = [n for n in COLN if n.startswith(a)]; bn = [n for n in COLN if n.startswith(b)]
        best = min(((poly_poly(foot(x, yawed), foot(y, yawed)), x, y) for x in an for y in bn))
        L.append(dict(a=best[1], b=best[2], footprint_gap=round(best[0], 4),
                      top_y=[round(float(TREES[yawed][best[1]][1][:, 1].max()), 3), round(float(TREES[yawed][best[2]][1][:, 1].max()), 3)]))
    WJ[key] = L
R['walk_collider_joints'] = WJ

# ------------------------------------------------------------------ landing -> Flight2 exit opening (2D footprint gaps between rail colliders)
OPEN = {}
for yawed in (True, False):
    key = 'studio_yawed' if yawed else 'as_exported_unyawed'
    W_ = ['COL_Landing_RailW', 'COL_Flight2_RailW']; E_ = ['COL_Landing_RailS', 'COL_Landing_RailE', 'COL_Flight2_RailE']
    L = [dict(west=w, east=e, gap=round(poly_poly(foot(w, yawed), foot(e, yawed)), 4)) for w in W_ for e in E_]
    OPEN[key] = dict(pairs=L, min_gap=min(x['gap'] for x in L), rw_corner=RW_CORNER.tolist(), rs_corner=RS_CORNER.tolist(),
                     flight2_rail_inner_clear=round(poly_poly(foot('COL_Flight2_RailW', yawed), foot('COL_Flight2_RailE', yawed)), 4),
                     flight1_rail_inner_clear=round(poly_poly(foot('COL_Flight1_RailW', yawed), foot('COL_Flight1_RailE', yawed)), 4),
                     landing_north_entry=round(poly_poly(foot('COL_Landing_RailN_W', yawed), foot('COL_Landing_RailN_E', yawed)), 4))
R['landing_exit_opening'] = OPEN
# HullExt colliders near the outrigger route (bump check): top height under the centreline
HX = []
for n in COLN:
    if not n.startswith('COL_HullExt'): continue
    V = TREES[True][n][1]
    if V[:, 0].min() < -112 and V[:, 0].max() > -128 and V[:, 2].max() > 40 and V[:, 2].min() < 64:
        tops = []
        for z in np.arange(40.0, 64.1, 0.5):
            for x in (-124.0, -122.0, -120.0, -118.0, -116.0):
                loc, nor, idx, d = TREES[True][n][0].ray_cast(B((x, 60.0, z)), B((0, -1, 0)), 80.0)
                if loc is not None: tops.append((round(60.0 - d, 4), x, float(z)))
        HX.append(dict(collider=n, y_range=[round(float(V[:, 1].min()), 4), round(float(V[:, 1].max()), 4)], x_range=[round(float(V[:, 0].min()), 3), round(float(V[:, 0].max()), 3)],
                       z_range=[round(float(V[:, 2].min()), 3), round(float(V[:, 2].max()), 3)], max_top_under_corridor=max(tops) if tops else None))
R['hullext_near_outrigger'] = HX

# ------------------------------------------------------------------ collider audit for the two props
CA = {}
for pn in PROPS:
    V = PT[pn]['V']; lo, hi = V.min(0), V.max(0); Tp = TREES[False][pn][0]; fp = hull2(V[:, [0, 2]])
    named = [n for n in COLN if any(k in n.lower() for k in ('wheel', 'chest', 'stern_w', 'treasure', pn.lower()))]
    hits = []
    for n in COLN:
        Vc = TREES[False][n][1]; clo, chi = Vc.min(0), Vc.max(0)
        xz_ov = poly_poly(fp, foot(n, False)) == 0.0
        aabb_ov = bool(np.all(clo <= hi) and np.all(chi >= lo))
        tri_ov = len(Tp.overlap(TREES[False][n][0])) if aabb_ov else 0
        if xz_ov or aabb_ov:
            hits.append(dict(collider=n, xz_footprint_overlap=xz_ov, aabb3d_overlap=aabb_ov, triangle_overlaps=tri_ov,
                             col_y=[round(float(clo[1]), 4), round(float(chi[1]), 4)], prop_y=[round(float(lo[1]), 4), round(float(hi[1]), 4)],
                             vertical_overlap=round(float(min(chi[1], hi[1]) - max(clo[1], lo[1])), 4)))
    CA[pn] = dict(collider_names_matching_prop=named, prop_in_Collision_collection='Collision' in [c.name for c in bpy.data.objects[pn].users_collection],
                  colliders_overlapping_xz_or_3d=hits,
                  colliders_rising_into_prop_volume=[h['collider'] for h in hits if h['aabb3d_overlap'] and h['col_y'][1] > h['prop_y'][0] + 0.05])
R['collider_audit'] = dict(collider_count=len(COLN), per_prop=CA)

# ------------------------------------------------------------------ geometry for the diagram
G['col_feet'] = {k: {n: foot(n, k == 'studio_yawed').tolist() for n in COLN} for k in ('studio_yawed', 'as_exported_unyawed')}
G['segs'] = SEGS; G['meas'] = {k: [dict(xz=r['xz'], seg=r['seg']) for r in v] for k, v in MEAS.items()}
G['anchors'] = {k: v.tolist() for k, v in E.items()}
os.makedirs(OUT, exist_ok=True)
json.dump(R, open(os.path.join(OUT, 'route_qa_raw.json'), 'w'), indent=1, default=lambda x: x.tolist() if hasattr(x, 'tolist') else (bool(x) if isinstance(x, np.bool_) else float(x)))
json.dump(G, open(os.path.join(OUT, 'route_geom.json'), 'w'), default=lambda x: x.tolist() if hasattr(x, 'tolist') else float(x))
json.dump(dict(rows=MEAS), open(os.path.join(OUT, 'route_samples.json'), 'w'), default=float)
print('ROUTE_QA_OK', bpy.data.is_dirty)
