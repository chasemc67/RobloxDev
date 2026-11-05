"""Batch-2 fitcheck: H1-H6 landmarks vs holes.json rails/walls and felt (signed point-to-OBB, triangles sampled <= 0.1),
envelope containment (props.md box around the anchor), 8-stud overhead clearance over reachable felt, lane rule (info)."""
import json, math, sys
import numpy as np
D = '/workspace/RobloxDev/assets/vr-minigolf/sugarloaf-canyon/'
H = {h['id']: h for h in json.load(open(D + 'holes.json'))['holes']}
TRI = json.load(open(sys.argv[1])); REP = json.load(open(sys.argv[2]))
def samples(tris, step=0.1):
    out = []
    for t in np.array(tris):
        a, b, c = t; n = max(1, int(math.ceil(max(np.linalg.norm(b-a), np.linalg.norm(c-a), np.linalg.norm(c-b)) / step)))
        i, j = np.meshgrid(np.arange(n+1), np.arange(n+1)); m = i + j <= n; u, v = i[m]/n, j[m]/n
        out.append(a + u[:, None]*(b-a) + v[:, None]*(c-a))
    return np.unique(np.round(np.vstack(out), 4), axis=0)
def Ry(d):
    a = math.radians(d); return np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
def sdist(P, c, size, yaw=0):
    q = (P - np.array(c)) @ Ry(yaw); d = np.abs(q) - np.array(size)/2
    return np.linalg.norm(np.maximum(d, 0), axis=1) + np.minimum(d.max(axis=1), 0)
def in_poly(x, z, poly):
    inside = np.zeros(len(x), bool); n = len(poly)
    for i in range(n):
        (x0, z0), (x1, z1) = poly[i], poly[(i+1) % n]
        c = ((z0 > z) != (z1 > z)) & (x < (x1 - x0)*(z - z0)/(z1 - z0 + 1e-12) + x0); inside ^= c
    return inside
def felt_top(f, P):  # plane height of felt f at P (local), and in-footprint mask
    q = (P - np.array(f['center'])) @ Ry(f.get('yaw', 0)); sx, sz = f['size']
    m = (np.abs(q[:, 0]) <= sx/2) & (np.abs(q[:, 2]) <= sz/2); sl = f.get('slope'); y = np.full(len(P), f['center'][1])
    if sl: y = y + sl['rise'] * (q[:, 0]/sx if sl['axis'] == 'x' else q[:, 2]/sz)
    return y, m
lines = ['Sugarloaf batch 2 fitcheck (H1-H6 landmarks) vs holes.json rails/walls + felt', '']; allpass = True
for part in REP['parts']:
    pid, hid = part['id'], part['hole']; h = H[hid]; st = 'PASS'; info = {'tris': part['tris'], 'max_mesh_tris': part['max_mesh_tris']}
    if part['max_mesh_tris'] >= 20000: st = 'FAIL'
    A = np.array(part['anchor_local'], float); P = samples(TRI[pid]) + A
    env = np.array(part['envelope']); lo = A + [-env[0]/2, 0, -env[2]/2]; hi = A + [env[0]/2, env[1], env[2]/2]
    out = np.maximum(np.maximum(lo - P, P - hi), 0).max(); info['envelope'] = {'box': [lo.tolist(), hi.tolist()], 'max_outside': round(float(out), 4)}
    if out > 1e-3: st = 'FAIL'
    walls = []
    for w in h['walls']:
        d = sdist(P, w['center'], w['size'], w.get('yaw', 0)); i = int(d.argmin()); walls.append((float(d[i]), w['id'], P[i].round(3).tolist()))
    walls.sort(); info['min_wall'] = [{'wall': w, 'clearance': round(c, 4), 'at': p} for c, w, p in walls[:3]]
    if walls and walls[0][0] < 0.05: st = 'FAIL'
    # felt: penetration below a felt top inside its footprint (0.4 slab), and 8-stud overhead over reachable felt
    pen, over = 0.0, 0; vis = h.get('plate_visible')
    for f in h['felt']:
        y, m = felt_top(f, P)
        if f.get('kind') == 'plate' and vis:
            reach = m & in_poly(P[:, 0], P[:, 2], vis[0])
        else: reach = m
        below = m & (P[:, 1] < y - 1e-3) & (P[:, 1] > y - 0.4)
        if below.any(): pen = max(pen, float((y - P[:, 1])[below].max()))
        over += int((reach & (P[:, 1] >= y - 1e-3) & (P[:, 1] < y + 8.0)).sum())
    info['felt_penetration'] = round(pen, 4); info['points_under_8_over_reachable_felt'] = over
    if pen > 1e-3 or over: st = 'FAIL'
    # lane rule (info): points taller than 2 above felt level within 3 of a rail
    tall = 0
    for w in h['walls']:
        d = sdist(P, w['center'], w['size'], w.get('yaw', 0)); tall += int(((d < 3) & (P[:, 1] > 2.0)).sum())
    info['lane_rule_points_tall_within_3_of_rail'] = tall
    info['notes'] = part['notes']
    lines.append(f'{st} {pid} ' + json.dumps(info)); allpass &= st == 'PASS'
lines += ['', 'Lane rule (nothing > 2 within 3 of a rail) is reported, not gated: the H1 arch posts, H2 headframe legs and H5 slot walls stand beside the rails by design (holes.json anchor notes).', 'ALL PASS: ' + ('YES' if allpass else 'NO')]
print('\n'.join(lines))
