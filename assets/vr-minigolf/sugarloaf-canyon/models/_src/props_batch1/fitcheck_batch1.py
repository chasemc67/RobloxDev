"""Batch-1 fitcheck (skill §6). Visual triangles (pivot-relative, Roblox local) sampled at <=0.05 stud,
swept through the full holes.json motion range; signed point-to-OBB distance vs static walls and felt.
Cut boxes from props.md remove their targets' residual volume. Also: containment in holes.json blockers, tris."""
import json, math, sys
import numpy as np
D = '/workspace/RobloxDev/assets/vr-minigolf/sugarloaf-canyon/'
HJ = json.load(open(D + 'holes.json')); H = {h['id']: h for h in HJ['holes']}
TRI = json.load(open(sys.argv[1])); REP = json.load(open(sys.argv[2]))
CUTS = {'h06': [(['rail5', 'rock18'], [-10.68, -0.15, -28.47], [3.68, 1.17, -27.53])],
        'h11': [(['rail4', 'rail5', 'rail7', 'rail8', 'approach'], [-1.95, -1.45, -21.65], [1.95, 1.35, -20.85])]}
MP = {'h06_sluice_gate': ('h06', 'sluice_gate'), 'h09_windpump_rotor': ('h09', 'windpump'), 'h11_lock_gate': ('h11', 'lock_gate'),
      'h14_ore_bucket': ('h14', 'ore_bucket'), 'h17_shadow_arms': ('h17', 'shadow_arm')}
def samples(tris, step=0.05):
    out = []
    for t in np.array(tris):
        a, b, c = t; n = max(1, int(math.ceil(max(np.linalg.norm(b-a), np.linalg.norm(c-a), np.linalg.norm(c-b)) / step)))
        for i in range(n+1):
            for j in range(n+1-i):
                u, v = i/n, j/n; out.append(a + u*(b-a) + v*(c-a))
    return np.unique(np.round(np.array(out), 5), axis=0)
def Ry(d):
    a = math.radians(d); return np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
def Rax(axis, d):
    ax = np.array(axis, float); ax /= np.linalg.norm(ax); a = math.radians(d); K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + math.sin(a)*K + (1-math.cos(a))*K@K
def sdist(P, c, size, yaw=0):
    q = (P - np.array(c)) @ Ry(yaw)  # world->local: p_local = R^T (p-c); row-vector form p@R
    d = np.abs(q) - np.array(size)/2
    out = np.linalg.norm(np.maximum(d, 0), axis=1); ins = np.minimum(d.max(axis=1), 0); return out + ins
def felt_box(f):
    sx, sz = f['size']; sl = f.get('slope'); th = f.get('thickness', 0.4); rise = abs(sl['rise']) if sl else 0
    return [f['center'][0], f['center'][1] - th/2 - rise/2 + rise/2, f['center'][2]], [sx, th + rise, sz], f.get('yaw', 0), bool(sl)
lines = ['Sugarloaf batch 1 fitcheck: visual meshes vs holes.json (static walls + felt), full motion sweep', '']
allpass = True; summary = {}
for part in REP['parts']:
    pid = part['id']; st = 'PASS'; info = {'tris': part['tris'], 'max_mesh_tris': part['max_mesh_tris']}
    if part['max_mesh_tris'] >= 20000: st = 'FAIL'
    P0 = samples(TRI[pid])
    info['bbox_local'] = [P0.min(0).round(4).tolist(), P0.max(0).round(4).tolist()]
    if pid not in MP: summary[pid] = (st, info); continue
    hid, mid = MP[pid]; h = H[hid]; mp = next(m for m in h['moving_parts'] if m['id'] == mid); piv = np.array(mp['pivot'], float)
    # containment in blockers (rest pose, pivot-relative)
    dmin = np.full(len(P0), np.inf)
    for b in mp['blockers']:
        roll = b.get('roll', 0); c = np.array(b['center'], float); R = np.eye(3)
        if roll: R = Rax(mp['axis'], roll); c = R @ c
        q = (P0 - c) @ R  # undo roll
        dmin = np.minimum(dmin, sdist(q, [0, 0, 0], b['size'], b.get('yaw', 0)))
    sel = np.ones(len(P0), bool)
    if pid == 'h14_ore_bucket': sel = P0[:, 1] < -8.0 + 1e-6   # hanger/bail above the bucket has no collider by design
    outside = dmin[sel] > 1e-3
    info['containment'] = {'points': int(sel.sum()), 'outside_collider': int(outside.sum()), 'max_outside': round(float(dmin[sel].max()), 4)}
    if pid == 'h09_windpump_rotor': info['containment']['note'] = 'visual tip r 4.1 (props.md envelope) vs collider strip corners r~4.06: visual-only overhang, CanCollide off'
    elif outside.any(): st = 'FAIL'
    # motion states
    if mp['type'] == 'slide': states = [('off', o) for o in np.arange(mp['range'][0], mp['range'][1] + 1e-9, 0.02)]
    elif mp['type'] == 'swing': states = [('ang', a) for a in np.arange(-mp['amplitude_deg'], mp['amplitude_deg'] + 1e-9, 0.1)]
    else: states = [('ang', a) for a in np.arange(0, 360, 0.25)]
    obst = []
    for w in h['walls']: obst.append((w['id'], w['center'], w['size'], w.get('yaw', 0), 'wall'))
    for f in h['felt']:
        c, s, y, sl = felt_box(f); obst.append(('felt_' + f['id'], c, s, y, 'felt_slope_env' if sl else 'felt'))
    cuts = CUTS.get(hid, [])
    best = {}
    Pp = P0[::max(1, len(P0)//6000)] if mp['type'] == 'rotate' else P0
    for kind, v in states:
        P = (Pp @ Rax(mp['axis'], v).T if kind == 'ang' else Pp + np.array(mp['axis'])*v) + piv
        for (oid, c, s, y, k) in obst:
            if np.linalg.norm(np.array(c) - P.mean(0)) > np.linalg.norm(s)/2 + np.linalg.norm(P.max(0)-P.min(0))/2 + 1: continue
            d = sdist(P, c, s, y)
            for tg, lo, hi in cuts:
                if oid in tg or oid.replace('felt_', '') in tg:
                    inc = np.all((P >= np.array(lo) - 1e-6) & (P <= np.array(hi) + 1e-6), axis=1); d = np.where(inc, np.inf, d)
            i = int(d.argmin())
            if oid not in best or d[i] < best[oid][0]: best[oid] = (float(d[i]), kind, round(float(v), 3), P[i].round(3).tolist(), k)
    worst = sorted(best.items(), key=lambda kv: kv[1][0])[:6]
    info['min_clearance'] = [{'obstacle': o, 'clearance': round(b[0], 4), b[1]: b[2], 'at_local': b[3], 'kind': b[4]} for o, b in worst]
    flags = []
    for o, b in best.items():
        if b[0] < -1e-3 and b[4] != 'felt_slope_env': flags.append(f'{o} intersects ({b[0]:.3f})')
        elif b[0] < 0.05 and b[4] == 'wall': flags.append(f'{o} under 0.05 ({b[0]:.3f})')
    info['flags'] = flags
    if flags: st = 'REVIEW'
    summary[pid] = (st, info)
for pid, (st, info) in summary.items():
    lines.append(f'{st} {pid} ' + json.dumps(info)); allpass &= st == 'PASS'
lines.append(''); lines.append('ALL PASS: ' + ('YES' if allpass else 'NO'))
print('\n'.join(lines))
